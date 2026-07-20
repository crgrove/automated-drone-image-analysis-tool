"""Top-level controller for the Flight Viewer window.

Owns the shared :class:`SignalingChannel`, the list of active
:class:`FlightTileController` instances, the
:class:`MissionGalleryController`, and the layout save/restore wiring
described in plan §15 / M3.
"""

from __future__ import annotations

import json
import threading
import time
from typing import Dict, List, Optional

from PySide6.QtCore import QObject, QSettings, Qt, QByteArray, Slot

from core.services.LoggerService import LoggerService
from core.services.streaming.FingerprintStore import FingerprintStore, PeerRecord
from core.services.streaming.FlightSessionStore import FlightSessionStore
from core.services.streaming.signaling import (
    DEFAULT_WORKER_URL,
    HttpSignalingChannel,
    InMemorySignalingChannel,
    SignalingChannel,
)
from core.controllers.flight.FlightTileController import FlightTileController
from core.controllers.flight.MissionGalleryController import MissionGalleryController
from core.views.flight.FlightViewerWindow import FlightViewerWindow


def _prewarm_webrtc_imports() -> None:
    """Force the heavy WebRTC native libraries to load on a worker thread.

    First-time import of ``aiortc`` pulls in PyAV (FFmpeg native bindings),
    ``cryptography`` (a Rust extension), ``aioice``, and ``pyee``. Each
    module's init runs with the GIL held, so loading them on demand inside
    :meth:`WebRTCStreamService.run` competes with the Qt main thread the
    moment the operator clicks Connect — visible as a ~1s UI freeze.
    Doing it ahead of time on a background thread amortises the cost
    while the operator is reading the pairing dialog.
    """
    try:
        import aiortc  # noqa: F401
        from aiortc.sdp import candidate_from_sdp  # noqa: F401
    except ImportError:
        # aiortc isn't installed in this environment — first Connect
        # will surface the same ImportError via the service's normal
        # ``_require_aiortc`` path. Don't crash the viewer window over
        # missing deps; just skip the warmup.
        return


# Plan §19.4.1: ``state`` / ``geometry`` under a versioned key. The ``v1``
# suffix lets future structural changes (additional docks, renamed
# objectNames) invalidate stored state cleanly instead of restoring a
# half-broken layout.
# Bumped to v2 when the right-dock vertical split was retuned (Map dock
# default height shrunk to a sliver under earlier code). Old saved
# state values are intentionally ignored so first-launch operators see
# the new defaults rather than the legacy 30 px Map dock.
SETTINGS_LAYOUT_KEY = "state/v2"
SETTINGS_GEOMETRY_KEY = "geometry/v2"
# Plan §20: last-active pairing(s) — JSON-encoded list of entries
# ``{code, session_id, worker_url, connected_at}`` so an accidental
# close can auto-resume on the next launch.
SETTINGS_LAST_SESSIONS_KEY = "lastSessions/v1"


class FlightViewerController(QObject):
    """Wires the window, services, and per-tile controllers together."""

    def __init__(
        self,
        *,
        signaling: Optional[SignalingChannel] = None,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.logger = LoggerService()
        self._signaling = signaling or self._default_signaling_channel()

        self.window = FlightViewerWindow()
        self.window.addFeedRequested.connect(self.open_pairing_dialog)
        self.window.toggleGalleryRequested.connect(self._toggle_gallery)
        self.window.toggleMapRequested.connect(self._toggle_map)
        self.window.saveLayoutRequested.connect(self.save_layout)
        self.window.restoreLayoutRequested.connect(self.restore_layout)
        self.window.openImageAnalysisRequested.connect(self._open_image_analysis)
        self.window.openStreamingDetectorRequested.connect(self._open_streaming_detector)
        self.window.helpRequested.connect(self._open_help)
        self.window.closeViewerRequested.connect(self.shutdown)

        self.gallery = MissionGalleryController(self.window.mission_gallery, parent=self)

        # feed_id -> controller mapping; feed_id is the pairing code in v1
        self._tile_controllers: Dict[str, FlightTileController] = {}
        # Keep dialogs alive while they're in flight
        self._dialogs: List[object] = []

        # Plan §15 M3 — Map dock auto-reveals on first geo-tagged detection;
        # clicking a row in the gallery centers the map on that detection.
        self.window.mission_gallery.detectionActivated.connect(
            self._on_gallery_row_activated
        )
        # Reverse direction: clicking a pin on the map highlights the
        # corresponding row in the Mission Gallery (plan §19.4.4).
        self.window.map_dock.pinClicked.connect(self._on_map_pin_clicked)

        self._settings = QSettings("ADIAT", "FlightViewer")
        # SQLite-backed TOFU store (plan §19.4.3). Lazy-instantiated so
        # tests that don't touch TOFU don't have to mock the filesystem.
        self._fingerprint_store: Optional[FingerprintStore] = None
        # SQLite-backed per-session detection store (plan §20). Same
        # lazy pattern — tests that don't touch session continuity
        # don't need the file on disk.
        self._session_store: Optional[FlightSessionStore] = None
        # Set during ``shutdown()`` so the ``_on_tile_closed`` slot can
        # distinguish "operator clicked X on the tile" (clear the
        # persisted entry — they don't want this feed back) from
        # "viewer / app is closing" (keep the entry so next launch
        # auto-resumes). Plan §20 spec: "Clear the entry on
        # operator-initiated disconnect."
        self._shutting_down: bool = False

        # Apply any persisted layout on construction (plan §15 M3).
        self.restore_layout()

        # Kick off the WebRTC import warmup on a daemon thread so the
        # first Connect click doesn't pay ~1s of native-library load
        # time. Daemon = won't keep the process alive on shutdown.
        threading.Thread(
            target=_prewarm_webrtc_imports,
            name="adiat-webrtc-prewarm",
            daemon=True,
        ).start()

    # ------------------------------------------------------------------
    # window lifecycle
    # ------------------------------------------------------------------

    def show(self) -> None:
        # Open maximized — the dock-based layout (feed tiles + Mission
        # Gallery + Map) is most useful with plenty of screen real estate,
        # and the operator can always restore down via the title bar.
        # ``showMaximized`` is preferred over ``showFullScreen`` so the
        # menu bar, toolbar, and OS chrome stay visible.
        self.window.showMaximized()
        self.window.raise_()
        self.window.activateWindow()
        # Auto-resume any pairings that were active when the operator
        # last closed the viewer (plan §20). Deferred via QTimer so the
        # window is fully shown / Qt event loop is pumping before we
        # block on GET /state.
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, self._try_auto_resume)

    def _try_auto_resume(self) -> None:
        """Kick off resume flow for every persisted session (plan §20).

        For each entry in ``LastSessions/v1``:

        1. Restore the session's stored detections into the live gallery
           so the operator immediately sees their prior history.
        2. ``GET /v1/sessions/:code/state`` on the Worker (async).
        3. If the Worker reports ``awaiting_viewer`` with the same
           ``session_id`` → kick off a pairing dialog pre-filled with
           the code and armed for resume backfill.
        4. If ``active`` (someone else attached) → leave the persisted
           entry for now; operator can resolve manually.
        5. If ``ended`` / 404 → clear the entry; gallery still shows
           the restored history.
        """
        entries = self._read_persisted_sessions()
        if not entries:
            self.logger.info(
                "Flight Viewer: no persisted sessions to auto-resume"
            )
            return
        self.logger.info(
            f"Flight Viewer: auto-resume found {len(entries)} persisted session(s): "
            f"{[e.get('code') for e in entries]}"
        )
        # Synchronously restore stored detections so the gallery isn't
        # empty during the (async) Worker probe.
        for entry in entries:
            session_id = entry.get("session_id")
            code = entry.get("code")
            if isinstance(session_id, str) and session_id and isinstance(code, str) and code:
                self._restore_session_detections(session_id=session_id, feed_id=code)
        # Probe the Worker for each persisted code asynchronously so a
        # slow / unreachable Worker doesn't block the UI thread.
        threading.Thread(
            target=self._auto_resume_worker,
            args=(entries,),
            name="adiat-flight-resume",
            daemon=True,
        ).start()

    def _restore_session_detections(self, *, session_id: str, feed_id: str) -> None:
        """Replay persisted detections into the live gallery + map.

        Skips entries that never received a thumbnail crop (typically
        snapshot replays from a prior session that arrived after the
        live frame had aged out of the cropper's ring). Those rows
        carry no image and minimal operator value — they'd just
        accumulate as "no thumb" placeholders.

        Collapses to one envelope per ``track_key`` (latest ``seq``
        wins) before replay. SQLite stores every promote/update event
        keyed by ``(session_id, seq)`` — for a long-lived target
        that's typically hundreds of UPDATEs. The live ``add_detection``
        path now dedups by ``track_key`` so feeding all 5000 events
        would still yield the right final state, but at the cost of
        5000 insert-then-refresh roundtrips on launch. Collapsing
        client-side keeps relaunch cheap.
        """
        try:
            envelopes = self.session_store.load_session_detections(session_id)
        except Exception as exc:  # noqa: BLE001
            self.logger.warning(
                f"Flight Viewer: load session {session_id} failed: {exc}"
            )
            return
        if not envelopes:
            return
        with_thumbs = [
            env for env in envelopes
            if isinstance(env.get("thumb_bytes"), (bytes, bytearray))
            and env.get("thumb_bytes")
        ]
        if not with_thumbs:
            return
        # Envelopes are returned from the store in ``seq`` order, so the
        # later iteration overwrites earlier — latest event per track
        # wins. Envelopes without a ``track_key`` (pre-§20 publishers)
        # fall through as one row each.
        latest_per_track: dict = {}
        for env in with_thumbs:
            tk = env.get("track_key")
            if isinstance(tk, str) and tk:
                latest_per_track[tk] = env
            else:
                latest_per_track[id(env)] = env
        collapsed = list(latest_per_track.values())
        # Register the feed before flushing rows so the Feed filter
        # dropdown has the entry.
        first = collapsed[0]
        label = (
            first.get("feed_display_name")
            or (first.get("aircraft_name") and f"{first['aircraft_name']} ({feed_id})")
            or f"Tile-{feed_id}"
        )
        self.gallery.register_feed(feed_id, label)
        for envelope in collapsed:
            envelope.setdefault("feed_id", feed_id)
            self.gallery.add_detection(feed_id, envelope)
            # Mirror detections-with-GPS into the map too.
            self._on_detection_for_map(feed_id, envelope)

    def _auto_resume_worker(self, entries: List[dict]) -> None:
        """Async Worker-state probe + auto-pair kickoff. Runs off the UI thread."""
        import asyncio
        for entry in entries:
            code = entry.get("code")
            session_id = entry.get("session_id")
            if not isinstance(code, str) or not code:
                continue
            if not isinstance(session_id, str) or not session_id:
                continue
            try:
                loop = asyncio.new_event_loop()
                state = loop.run_until_complete(self._signaling.get_session_state(code))
                loop.close()
            except Exception as exc:  # noqa: BLE001
                self.logger.warning(
                    f"Flight Viewer: get_session_state({code}) failed: {exc}"
                )
                continue
            self.logger.info(
                f"Flight Viewer: Worker reports state={state.state} for {code} "
                f"(local session_id={session_id}, remote session_id={state.session_id})"
            )
            # Marshal back to the Qt main thread to spawn the dialog.
            from PySide6.QtCore import QMetaObject, Q_ARG, Qt as _Qt
            QMetaObject.invokeMethod(
                self,
                "_handle_resume_state",
                _Qt.QueuedConnection,
                Q_ARG(str, code),
                Q_ARG(str, session_id),
                Q_ARG(str, state.state),
                Q_ARG(str, state.session_id or ""),
            )

    @Slot(str, str, str, str)
    def _handle_resume_state(
        self,
        code: str,
        local_session_id: str,
        state: str,
        remote_session_id: str,
    ) -> None:
        """Apply the Worker's session-state response on the Qt main thread."""
        if state == "awaiting_viewer":
            # Same session_id → silent resume. Different → operator
            # archive/discard prompt fires once envelopes arrive (via
            # ``_on_tile_session_changed``).
            self.open_pairing_dialog(
                prefilled_code=code, resume_session_id=local_session_id
            )
        elif state == "active":
            # Someone else is already attached. Leave the entry; the
            # operator can re-pair via the Add Feed dialog if they want
            # to take over (which will return 409 until that viewer
            # disconnects, per plan §20 race resolution).
            self.logger.info(
                f"Flight Viewer: skipping auto-resume of {code} — Worker reports active"
            )
        else:
            # ``ended`` / 404 / anything else → cleanup. Gallery rows
            # already restored stay visible until the operator clears
            # them via the Mission Gallery's existing controls.
            self._clear_persisted_session(code)

    def shutdown(self) -> None:
        """Tear down all active tiles + signaling, persist layout.

        Sets ``_shutting_down`` so the per-tile teardown signal chain
        knows to PRESERVE the persisted ``lastSessions`` entries
        instead of treating each tile close as an "operator-initiated
        disconnect" (which clears the entry). Without this guard,
        every clean app close wipes the resume state and the next
        launch can't find anything to auto-resume.
        """
        self._shutting_down = True
        try:
            self.save_layout()
        except Exception:  # pragma: no cover - persistence shouldn't crash exit
            pass
        for code, controller in list(self._tile_controllers.items()):
            controller.tear_down()
        self._tile_controllers.clear()
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self._signaling.close())
            loop.close()
        except Exception:  # pragma: no cover - best effort
            pass

    # ------------------------------------------------------------------
    # pairing flow
    # ------------------------------------------------------------------

    def open_pairing_dialog(
        self,
        *,
        prefilled_code: Optional[str] = None,
        resume_session_id: Optional[str] = None,
    ) -> None:
        """Spawn a non-modal pairing dialog.

        Defaults to a blank dialog the operator fills in. The auto-resume
        path on launch (plan §20) calls this with ``prefilled_code`` +
        ``resume_session_id`` set so the tile controller arms the
        resume handshake and the dialog dismisses itself the moment
        the network connection establishes.
        """
        controller = FlightTileController(
            signaling=self._signaling,
            session_store=self.session_store,
            resume_session_id=resume_session_id,
            parent=self,
        )
        controller.tileReady.connect(self._on_tile_ready)
        controller.tileClosed.connect(self._on_tile_closed)
        controller.detectionPromoted.connect(self.gallery.add_detection)
        controller.detectionPromoted.connect(self._on_detection_for_map)
        controller.detectionUpdated.connect(self.gallery.add_detection)
        controller.detectionUpdated.connect(self._on_detection_for_map)
        # Desktop-side thumbnail crops (plan §19.4.1) — mobile no longer
        # ships JPEGs over the data channel; the per-tile cropper crops
        # them locally from the live frame buffer and emits ``thumbReady``
        # per track. Bridge straight to the Mission Gallery's
        # ``upsert_thumb`` so the row's image refreshes in place.
        controller.thumbReady.connect(self._on_thumb_ready)
        # Tile renames + telemetry-derived names → propagate to the
        # gallery's Feed filter dropdown AND every row that already
        # carries this feed's pairing code.
        controller.feedDisplayNameChanged.connect(self.gallery.set_feed_display_name)
        # Plan §20 session-continuity wiring. ``sessionEstablished``
        # fires once per pairing as soon as the publisher's
        # ``session_id`` lands on any envelope; we persist the
        # ``(code, session_id)`` pair so an accidental close can
        # auto-resume on the next launch.
        controller.sessionEstablished.connect(self._on_session_established)
        controller.sessionChanged.connect(self._on_tile_session_changed)
        controller.resumeComplete.connect(self._on_tile_resume_complete)
        controller.resumeFailed.connect(self._on_tile_resume_failed)
        # Snapshot replay is fanned out per-detection through the existing
        # detectionPromoted path (plan §18 → *Desktop residual work* item 2),
        # so the gallery picks it up automatically. The bulk
        # ``detectionSnapshot`` signal is still emitted by the tile
        # controller for forward-compat but is intentionally not wired to
        # ``MissionGalleryController.replace_snapshot`` — that path would
        # wipe pre-snapshot detections rather than merging idempotently.

        dialog = controller.run_pairing_dialog(self.window)
        if dialog is None:
            return
        dialog.setAttribute(Qt.WA_DeleteOnClose, True)
        dialog.setModal(False)  # plan §4: multiple pairings in parallel
        self._dialogs.append((controller, dialog))
        # Auto-resume: pre-fill the code and submit immediately so the
        # operator doesn't have to type anything. The dialog still
        # renders (carries the "Pairing…" / "Failed" UI) but skips
        # the code-entry step.
        if prefilled_code:
            try:
                dialog.codeEdit.setText(prefilled_code)
                dialog._on_connect_clicked()
            except Exception as exc:  # noqa: BLE001
                self.logger.warning(
                    f"Flight Viewer: auto-resume prefill failed for {prefilled_code}: {exc}"
                )
        dialog.show()

    # ------------------------------------------------------------------
    # tile callbacks
    # ------------------------------------------------------------------

    def _on_tile_ready(self, tile) -> None:
        controller = self._find_controller_for_tile(tile)
        if controller is None or controller.pairing_code is None:
            return
        code = controller.pairing_code
        self._tile_controllers[code] = controller
        self.gallery.register_feed(code, f"Tile-{code}")
        self.window.dock_tile(tile)
        tile.muteGalleryToggled.connect(self._on_mute_toggled)

    def _find_controller_for_tile(self, tile) -> Optional[FlightTileController]:
        for ctrl, _dlg in self._dialogs:
            if isinstance(ctrl, FlightTileController) and ctrl.tile is tile:
                return ctrl
        return None

    def _on_tile_closed(self, code: str) -> None:
        controller = self._tile_controllers.pop(code, None)
        if controller is not None and controller.tile is not None:
            self.window.remove_tile(controller.tile)
        self.gallery.deregister_feed(code)
        # Drop the dialog/controller pair reference once the tile is gone.
        self._dialogs = [
            (ctrl, dlg) for (ctrl, dlg) in self._dialogs if ctrl is not controller
        ]
        # Only clear the persisted entry when this is an operator-driven
        # close (X on the tile / Disconnect). App / viewer shutdown also
        # routes through this slot via the per-tile tear_down chain;
        # the ``_shutting_down`` guard preserves the entry so the next
        # launch can auto-resume per plan §20.
        if not self._shutting_down:
            self._clear_persisted_session(code)

    # ------------------------------------------------------------------
    # session continuity (plan §20)
    # ------------------------------------------------------------------

    def _on_session_established(self, code: str, session_id: str) -> None:
        """Persist ``(code, session_id)`` so the next launch can auto-resume."""
        worker_url = getattr(self._signaling, "base_url", "") or ""
        self._upsert_persisted_session(
            code=code, session_id=session_id, worker_url=worker_url
        )
        self.logger.info(
            f"Flight Viewer: persisted session for {code} "
            f"(session_id={session_id}); next launch will auto-resume"
        )

    def _on_tile_session_changed(
        self, code: str, old_session_id: str, new_session_id: str
    ) -> None:
        """Mobile started a fresh session since our stored history.

        Prompt the operator: archive the old session's detections
        under their session_id, or discard. Default is archive — the
        UI shows the new session's detections going forward either way.
        """
        from PySide6.QtWidgets import QMessageBox
        # Update the persisted ``LastSession`` to the new id so a
        # subsequent restart auto-resumes against the right session.
        worker_url = getattr(self._signaling, "base_url", "") or ""
        self._upsert_persisted_session(
            code=code, session_id=new_session_id, worker_url=worker_url
        )
        reply = QMessageBox.question(
            self.window,
            self.tr("New flight session"),
            self.tr(
                "Mobile started a new flight under code {code}. The previous "
                "session's detections are still saved on this computer. "
                "Discard them, or keep them archived?"
            ).format(code=code),
            QMessageBox.Discard | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Discard:
            try:
                self.session_store.prune_session(old_session_id)
            except Exception as exc:  # noqa: BLE001
                self.logger.warning(
                    f"Flight Viewer: discard of session {old_session_id} failed: {exc}"
                )
        # Clear any rows already painted in the gallery for the old
        # session — the new session_id will repopulate from live promotions.
        self.gallery.clear()

    def _on_tile_resume_complete(self, code: str, session_id: str, last_seq: int) -> None:
        """Mobile finished streaming backfill for our resume request."""
        self.logger.info(
            f"Flight Viewer: resume complete for {code} ({session_id}, seq≤{last_seq})"
        )

    def _on_tile_resume_failed(self, code: str) -> None:
        """Auto-resume aborted — clear the persisted entry.

        Triggered when the operator cancels the auto-resume dialog or
        the connection times out before ICE pairs. Without clearing,
        every subsequent launch would repeat the same broken
        auto-resume against a stale persisted code.
        """
        self.logger.info(
            f"Flight Viewer: auto-resume failed for {code} — clearing "
            "persisted entry"
        )
        self._clear_persisted_session(code)

    # -- persistence helpers ------------------------------------------------

    def _read_persisted_sessions(self) -> List[dict]:
        raw = self._settings.value(SETTINGS_LAST_SESSIONS_KEY)
        if isinstance(raw, str) and raw:
            try:
                payload = json.loads(raw)
            except (TypeError, ValueError):
                return []
            if isinstance(payload, list):
                return [entry for entry in payload if isinstance(entry, dict)]
        return []

    def _write_persisted_sessions(self, entries: List[dict]) -> None:
        self._settings.setValue(SETTINGS_LAST_SESSIONS_KEY, json.dumps(entries))
        self._settings.sync()

    def _upsert_persisted_session(
        self, *, code: str, session_id: str, worker_url: str
    ) -> None:
        if not code or not session_id:
            return
        existing = [e for e in self._read_persisted_sessions() if e.get("code") != code]
        existing.append({
            "code": code,
            "session_id": session_id,
            "worker_url": worker_url,
            "connected_at_epoch_s": time.time(),
        })
        self._write_persisted_sessions(existing)

    def _clear_persisted_session(self, code: str) -> None:
        if not code:
            return
        remaining = [e for e in self._read_persisted_sessions() if e.get("code") != code]
        self._write_persisted_sessions(remaining)

    def _on_thumb_ready(self, _feed_id: str, track_key: str, jpeg_bytes: bytes) -> None:
        """Bridge a desktop-cropped thumbnail to the Mission Gallery.

        Plan §19.4.1: the per-tile :class:`DetectionThumbCropper` emits
        ``thumbReady(track_key, jpeg_bytes)`` after every successful
        crop. The gallery's ``upsert_thumb`` patches the existing row's
        image in place and caches the bytes for future snapshot replays
        of the same track.
        """
        self.gallery.upsert_thumb(track_key, jpeg_bytes)

    def _on_mute_toggled(self, tile, muted: bool) -> None:
        code = getattr(tile, "pairing_code", None)
        if code is not None:
            self.gallery.set_feed_muted(code, muted)

    # ------------------------------------------------------------------
    # gallery dock visibility
    # ------------------------------------------------------------------

    def _toggle_gallery(self, visible: bool) -> None:
        self.window.mission_gallery.setVisible(visible)

    def _toggle_map(self, visible: bool) -> None:
        """Show/hide the map dock via the menu toggle."""
        if visible:
            self.window.show_map_dock()
        else:
            self.window.map_dock.setVisible(False)

    # ------------------------------------------------------------------
    # navigation to other ADIAT windows
    # ------------------------------------------------------------------

    def _open_image_analysis(self) -> None:
        """Open the Image Analysis main window; keep the Flight Viewer up."""
        try:
            from core.controllers.images.MainWindow import MainWindow
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            existing = getattr(app, "_main_window", None) if app else None
            if existing is not None and existing.isVisible():
                existing.raise_()
                existing.activateWindow()
                return
            main_window = MainWindow()
            if app is not None:
                app._main_window = main_window
            main_window.show()
        except Exception as exc:  # noqa: BLE001 - surface to user, never crash
            self.logger.error(f"Flight Viewer: open Image Analysis failed: {exc}")
            self._show_navigation_error(self.tr("Image Analysis"), exc)

    def _open_streaming_detector(self) -> None:
        """Open the Streaming Detector window; keep the Flight Viewer up."""
        try:
            from core.controllers.streaming.StreamViewerWindow import StreamViewerWindow
            from PySide6.QtWidgets import QApplication
            from core.services.SettingsService import SettingsService
            app = QApplication.instance()
            existing = getattr(app, "_stream_viewer", None) if app else None
            if existing is not None and existing.isVisible():
                existing.raise_()
                existing.activateWindow()
                return
            theme = SettingsService().get_setting("Theme", "Dark").lower()
            stream_viewer = StreamViewerWindow(
                algorithm_name="ColorAnomalyAndMotionDetection", theme=theme
            )
            if app is not None:
                app._stream_viewer = stream_viewer
            stream_viewer.show()
        except Exception as exc:  # noqa: BLE001
            self.logger.error(f"Flight Viewer: open Streaming Detector failed: {exc}")
            self._show_navigation_error(self.tr("Streaming Detector"), exc)

    def _open_help(self) -> None:
        """Open the ADIAT documentation URL in the operator's browser."""
        try:
            from PySide6.QtCore import QUrl
            from PySide6.QtGui import QDesktopServices
            QDesktopServices.openUrl(
                QUrl("https://www.texsar.org/automated-drone-image-analysis-tool/")
            )
        except Exception as exc:  # noqa: BLE001
            self.logger.error(f"Flight Viewer: open help URL failed: {exc}")

    def _show_navigation_error(self, target_name: str, exc: Exception) -> None:
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(
            self.window,
            self.tr("Error"),
            self.tr("Failed to open {target}:\n{error}").format(
                target=target_name, error=str(exc)
            ),
        )

    # ------------------------------------------------------------------
    # map dock plumbing
    # ------------------------------------------------------------------

    def _on_detection_for_map(self, _feed_id: str, detection: dict) -> None:
        """Push every detection with GPS into :class:`MapDock`.

        Reveals the dock the first time we see a geo-tagged detection so
        the operator isn't faced with an empty map at session start.
        """
        loc = detection.get("location") if isinstance(detection, dict) else None
        if not isinstance(loc, dict):
            return
        lat = loc.get("lat")
        lon = loc.get("lon")
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            return
        self.window.map_dock.add_detection(detection)
        if not self.window.map_dock.isVisible():
            self.window.show_map_dock()

    def _on_gallery_row_activated(self, detection: dict) -> None:
        """Center the map dock on a detection when the operator clicks its row."""
        self.window.map_dock.focus_detection(detection)
        if not self.window.map_dock.isVisible():
            self.window.show_map_dock()

    def _on_map_pin_clicked(self, track_key: str) -> None:
        """Highlight the matching Mission Gallery row when a pin is clicked.

        Implements the reverse direction of plan §19.4.4 — Leaflet pin
        clicks bubble up through :class:`MapDock`'s ``pinClicked`` signal
        and we ask the gallery to scroll/select the matching row.
        """
        if not track_key:
            return
        try:
            self.window.mission_gallery.highlight_track(track_key)
        except Exception:  # noqa: BLE001 - never let UI plumbing crash signals
            pass

    # ------------------------------------------------------------------
    # TOFU fingerprint persistence (plan §15 M3)
    # ------------------------------------------------------------------

    @property
    def fingerprint_store(self) -> FingerprintStore:
        """SQLite-backed TOFU store; created on first access (plan §19.4.3)."""
        if self._fingerprint_store is None:
            self._fingerprint_store = FingerprintStore()
        return self._fingerprint_store

    @property
    def session_store(self) -> FlightSessionStore:
        """SQLite-backed per-session detection store (plan §20).

        Lazy-instantiated so test fixtures that never touch session
        continuity don't have to mock the filesystem.
        """
        if self._session_store is None:
            self._session_store = FlightSessionStore()
        return self._session_store

    def remember_fingerprint(
        self,
        fingerprint: str,
        *,
        device_label: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> None:
        """Persist a peer fingerprint after a successful SAS confirm.

        ``device_label`` is the operator-assigned name (M4E #3, Bravo's
        tablet, …). When omitted we mint a placeholder label from the
        fingerprint so the desktop still has a record, but the operator
        UI in :class:`FlightPairingDialog` is expected to surface a real
        label dialog before this path is taken.

        ``notes`` is the optional free-text annotation written into the
        store. Set this when the operator accepts a fingerprint *change*
        for an existing device (plan §19.4.3 mismatch warning), so a
        future audit can tell the swap apart from a clean first pair.
        """
        if not fingerprint:
            return
        label = device_label or f"unlabeled-{self._fingerprint_id(fingerprint)}"
        try:
            self.fingerprint_store.record_pairing(label, fingerprint, notes=notes)
        except Exception as exc:  # noqa: BLE001 - TOFU storage must not crash
            self.logger.warning(
                f"FlightViewerController: failed to persist fingerprint for "
                f"{label}: {exc}"
            )

    def known_fingerprint(self, device_label: str) -> Optional[str]:
        """Return the previously-trusted fingerprint for ``device_label``."""
        if not device_label:
            return None
        record = self.fingerprint_store.get(device_label)
        return record.sha256 if record else None

    def is_fingerprint_trusted(self, fingerprint: str) -> bool:
        """``True`` if any stored device's fingerprint matches ``fingerprint``."""
        if not fingerprint:
            return False
        match = self.fingerprint_store.find_by_fingerprint(fingerprint)
        return match is not None

    def lookup_device_by_fingerprint(self, fingerprint: str) -> Optional[PeerRecord]:
        """Return the matching :class:`PeerRecord` for ``fingerprint`` or ``None``."""
        if not fingerprint:
            return None
        return self.fingerprint_store.find_by_fingerprint(fingerprint)

    @staticmethod
    def _fingerprint_id(fingerprint: str) -> str:
        """Stable short key derived from a fingerprint (for placeholder labels)."""
        import hashlib

        normalized = (fingerprint or "").replace(":", "").replace(" ", "").lower()
        return hashlib.sha256(normalized.encode("ascii")).hexdigest()[:16]

    # ------------------------------------------------------------------
    # layout save/restore
    # ------------------------------------------------------------------

    def save_layout(self) -> None:
        self._settings.setValue(SETTINGS_LAYOUT_KEY, self.window.saveState())
        self._settings.setValue(SETTINGS_GEOMETRY_KEY, self.window.saveGeometry())
        self._settings.sync()

    def restore_layout(self) -> None:
        state = self._settings.value(SETTINGS_LAYOUT_KEY)
        geometry = self._settings.value(SETTINGS_GEOMETRY_KEY)
        if isinstance(state, QByteArray):
            self.window.restoreState(state)
        if isinstance(geometry, QByteArray):
            self.window.restoreGeometry(geometry)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _default_signaling_channel() -> SignalingChannel:
        """Pick the signaling backend based on operator configuration.

        Production default is :class:`HttpSignalingChannel` pointed at the
        canonical ``signal.adiat.app`` Cloudflare Worker. Operators can
        override via ``config.toml``:

        .. code-block:: toml

            [signaling]
            base_url = "https://my-self-hosted-worker.example/"

        See plan §17 for the file location. If ``httpx`` is not installed
        (development environment without WebRTC deps), falls back to the
        :class:`InMemorySignalingChannel` so the UI still loads.
        """
        url = DEFAULT_WORKER_URL
        try:
            from helpers.AppConfig import get_section

            signaling_cfg = get_section("signaling")
            override = signaling_cfg.get("base_url")
            if isinstance(override, str) and override.strip():
                url = override.strip()
        except Exception:  # pragma: no cover - defensive
            pass

        try:
            return HttpSignalingChannel(base_url=url)
        except ImportError:
            # httpx not installed yet — fall back to the in-process channel
            # so the rest of the Flight Viewer still works in a dev environment.
            return InMemorySignalingChannel()
