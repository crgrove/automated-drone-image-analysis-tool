"""``QFrame`` widget representing one paired drone feed.

Each tile owns a video pane (``QLabel`` with ``setPixmap`` of the latest
frame), a transparent detection overlay, a telemetry HUD, and a status
strip. Plan §4 *FlightTile* describes the layout — this class is just
the view; the lifecycle of the underlying :class:`WebRTCStreamService`
lives in :class:`~core.controllers.flight.FlightTileController.\
FlightTileController`.

A ``FlightTile`` is **embedded** inside the
:class:`~core.views.flight.FlightViewerWindow.FlightViewerWindow`'s
``QMdiArea`` via a ``QMdiSubWindow`` wrapper. That makes it a true
child widget of the viewer: it cannot escape the parent frame, follows
the parent on resize, and inherits min/max/close window chrome from
Qt's MDI machinery — no floating-window hacks required.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QMdiSubWindow,
    QMenu,
    QVBoxLayout,
    QWidget,
)

from core.views.flight.DetectionOverlayWidget import DetectionOverlayWidget
from core.views.flight.flight_tile_ui import Ui_FlightTileContents
from core.views.flight.TelemetryHud import TelemetryHud
from helpers.TranslationMixin import TranslationMixin


class FlightTile(TranslationMixin, QFrame):
    """Single feed tile embedded as a sub-window in the Flight Viewer.

    The video pane is a ``QLabel`` updated from a Qt slot — frames arrive
    via ``WebRTCStreamService.frameReady(np.ndarray, ts, n)`` on the Qt
    thread. The detection overlay + telemetry HUD layer on top of that
    label; the status strip pinned to the bottom shows stream stats.
    """

    closeRequested = Signal(object)
    reconnectRequested = Signal(object)
    fullscreenRequested = Signal(object)
    muteGalleryToggled = Signal(object, bool)
    # Fires whenever the tile's operator-facing display name changes —
    # nickname rename, ``aircraft_name`` arriving from telemetry, or
    # the operator clearing a nickname. Carries the pairing code and
    # the resolved label so the gallery / map / filter dropdowns can
    # update in lock-step without reaching into the tile state.
    displayNameChanged = Signal(str, str)

    def __init__(
        self,
        *,
        pairing_code: str,
        title: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.pairing_code = pairing_code
        # Latest aircraft identity from the publisher's telemetry stream
        # (plan §19.3 ``aircraft_name`` + ``aircraft_serial``). Updated
        # in ``apply_telemetry`` on every envelope; drives the tile
        # title via :meth:`_resolve_title`. Both are ``None`` until the
        # publisher's DJI ``ProductState`` populates — typical first
        # second of any session.
        self._aircraft_name: Optional[str] = None
        self._aircraft_serial: Optional[str] = None
        # Display title — surfaces on the QMdiSubWindow wrapper's title bar
        # (the viewer's ``dock_tile`` reads ``windowTitle()`` from us).
        # Title precedence (highest first):
        #   1. Operator nickname (persisted by ``aircraft_serial`` in
        #      QSettings — survives new pairing codes since the desktop
        #      gets a fresh code every session).
        #   2. ``aircraft_name`` from telemetry, with code as suffix.
        #   3. Pairing-code-keyed nickname (rename happened before
        #      serial was known; migrated to serial-keyed once it
        #      arrives).
        #   4. ``Feed <code>``.
        display_title = title or self._resolve_title()
        self.setWindowTitle(display_title)
        # Unique objectName lets QMdiArea's own state save / restore round-trip.
        self.setObjectName(f"flightTile-{pairing_code}")

        # Embed the generated tile contents (video pane + status strip) as
        # the single child of this frame; tight margins so the embedded
        # widget visually IS the tile.
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        contents = QWidget(self)
        self.ui = Ui_FlightTileContents()
        self.ui.setupUi(contents)
        layout.addWidget(contents)

        self._frame_count = 0
        self._gallery_muted = False
        # Per-tile recording state (created on demand from the context menu).
        self._recorder = None
        self._recording_path: Optional[str] = None
        # Most-recent decoded source frame (BGR ndarray). Held by
        # reference, not copied — ``WebRTCStreamService`` produces one
        # ndarray per frame and the prior reference goes out of scope
        # on the next emit. Snapshotting at promotion time gives the
        # detection popout a full-resolution context image (not just
        # the small cropped thumb that ships over the data channel).
        self._latest_frame_bgr: Optional[np.ndarray] = None

        # Detection bbox overlay (plan §19.4) — transparent full-pane
        # child that draws per-track rectangles aligned to the exact
        # frame each box was computed from. Created BEFORE the HUD so
        # the HUD's bottom strip ends up on top (the strip is opaque;
        # boxes that would land under it are hidden by the HUD anyway).
        self.detection_overlay = DetectionOverlayWidget(self.ui.videoLabel)
        self.detection_overlay.move(0, 0)
        self.detection_overlay.resize(self.ui.videoLabel.size())

        # Telemetry HUD (plan §19.3) — overlay anchored to the bottom of
        # the video pane. ``TelemetryHud`` reads ``DistanceUnit`` from
        # Settings on each envelope so unit-toggle in Preferences applies
        # without a restart.
        self.telemetry_hud = TelemetryHud(self.ui.videoLabel)
        self.telemetry_hud.move(0, 0)
        self.telemetry_hud.setVisible(False)  # show on first envelope
        self.ui.videoLabel.installEventFilter(self)

        self._build_context_menu()

    # ------------------------------------------------------------------
    # telemetry HUD
    # ------------------------------------------------------------------

    def apply_telemetry(self, envelope: dict) -> None:
        """Push a parsed telemetry envelope into the bottom-of-video HUD.

        Also absorbs ``aircraft_name`` / ``aircraft_serial`` for the
        tile title and the status-strip tooltip (plan §19.3). Title
        and tooltip refresh whenever either field's value changes,
        which typically happens once per session (the first envelope
        after DJI's ``ProductState`` populates).
        """
        self.telemetry_hud.apply_envelope(envelope)
        if not self.telemetry_hud.isVisible():
            self.telemetry_hud.setVisible(True)
        self._reposition_hud()
        if isinstance(envelope, dict):
            name = envelope.get("aircraft_name")
            serial = envelope.get("aircraft_serial")
            name_str = name.strip() if isinstance(name, str) and name.strip() else None
            serial_str = serial.strip() if isinstance(serial, str) and serial.strip() else None
            changed = False
            if name_str != self._aircraft_name:
                self._aircraft_name = name_str
                changed = True
            if serial_str != self._aircraft_serial:
                self._aircraft_serial = serial_str
                # First-time arrival of a serial: migrate any pairing-code-keyed
                # nickname (set before telemetry arrived) into the serial slot
                # so the rename sticks across future sessions.
                if serial_str is not None:
                    self._migrate_pairing_code_nickname_to_serial(serial_str)
                changed = True
            if changed:
                self._refresh_title_and_tooltip()

    def _reposition_hud(self) -> None:
        """Anchor the HUD to the bottom of the video pane."""
        if not self.telemetry_hud.isVisible():
            return
        video_rect = self.ui.videoLabel.rect()
        hud_height = self.telemetry_hud.sizeHint().height()
        # Compress to fit narrow tiles; expand to full width otherwise.
        self.telemetry_hud.setGeometry(
            0,
            max(0, video_rect.height() - hud_height),
            max(120, video_rect.width()),
            hud_height,
        )

    def eventFilter(self, watched, event):  # noqa: N802 - Qt name
        from PySide6.QtCore import QEvent

        if watched is self.ui.videoLabel and event.type() == QEvent.Resize:
            self._reposition_hud()
            # Detection overlay tracks the full video pane so bbox coords
            # always map against the same rect that ``on_frame`` scales
            # the pixmap into.
            self.detection_overlay.resize(self.ui.videoLabel.size())
        return super().eventFilter(watched, event)

    # ------------------------------------------------------------------
    # sub-window helpers (the wrapping ``QMdiSubWindow`` owns close /
    # maximize / minimize natively; we just expose convenience helpers
    # for the context menu)
    # ------------------------------------------------------------------

    def _subwindow(self) -> Optional[QMdiSubWindow]:
        """Return the ``QMdiSubWindow`` wrapping this tile, if any.

        ``FlightViewerWindow.dock_tile`` stashes the wrapper as a
        Qt dynamic property on the tile so we can find it later without
        a viewer back-reference. Returns ``None`` for un-embedded tiles
        (e.g. raw tile instances in tests).
        """
        sw = self.property("_mdi_subwindow")
        return sw if isinstance(sw, QMdiSubWindow) else None

    def maximize_within_viewer(self) -> None:
        """Maximize the wrapping sub-window to fill the MDI area."""
        sw = self._subwindow()
        if sw is not None:
            sw.showMaximized()

    def restore_subwindow(self) -> None:
        """Restore the wrapping sub-window to its normal size."""
        sw = self._subwindow()
        if sw is not None:
            sw.showNormal()

    # ------------------------------------------------------------------
    # video
    # ------------------------------------------------------------------

    def on_frame(self, frame_bgr: np.ndarray, ts: float, _frame_n: int) -> None:
        """Render an incoming BGR frame on the video pane.

        Scales the source frame to fit ``videoLabel.size()`` with
        ``KeepAspectRatio`` — the displayed video follows the tile size,
        with letterbox/pillarbox black bars on the unfilled axis.

        ``videoLabel`` has ``sizePolicy = Ignored/Ignored`` so the pixmap
        size cannot feed back into the layout's ``sizeHint`` (that loop
        was responsible for the tile slowly growing each frame when the
        dock honored the contents widget's hint).
        """
        if frame_bgr is None or frame_bgr.size == 0:
            return
        # Stash the latest source-resolution frame for the detection
        # popout's context image. Keep a *reference* — the publisher
        # produces one ndarray per frame and the prior one releases
        # naturally; no per-frame copy cost.
        self._latest_frame_bgr = frame_bgr
        try:
            h, w = frame_bgr.shape[:2]
            # `bgr24` ndarray -> QImage via Format_BGR888 (no copy).
            qimg = QImage(frame_bgr.data, w, h, frame_bgr.strides[0], QImage.Format_BGR888)
            pixmap = QPixmap.fromImage(qimg)
            scaled = pixmap.scaled(
                self.ui.videoLabel.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.ui.videoLabel.setPixmap(scaled)
            self._frame_count += 1
            # Drive the detection overlay AFTER the pixmap update so its
            # ``paintEvent`` repaints on the same frame the operator sees.
            # ``ts`` is aiortc's RTP-derived seconds (the same value the
            # plan §19.4 calibration expects). Also hand over the raw
            # BGR ndarray so the overlay's ``recent_frames`` ring fills
            # for the desktop-side thumb cropper (plan §19.4.1).
            self.detection_overlay.on_video_frame(ts, w, h, frame_bgr)
        except Exception:  # noqa: BLE001 - never crash the UI thread
            pass

        # Feed the frame to the recorder if one is active. Done AFTER
        # rendering so a slow disk doesn't stall the display path.
        recorder = self._recorder
        if recorder is not None:
            try:
                recorder.add_frame(frame_bgr, ts)
            except Exception:  # noqa: BLE001 - recording is best-effort
                pass

    # ------------------------------------------------------------------
    # per-tile recording (plan §15 M3)
    # ------------------------------------------------------------------

    @property
    def is_recording(self) -> bool:
        return self._recorder is not None

    def _start_recording_from_menu(self) -> None:
        from PySide6.QtWidgets import QFileDialog
        # Default to ~/Videos/ADIAT to keep recordings out of the user's
        # home directory root. The directory is created on demand by the
        # VideoRecorder service if it doesn't exist yet.
        import os as _os
        default_dir = _os.path.join(_os.path.expanduser("~"), "Videos", "ADIAT")
        chosen = QFileDialog.getExistingDirectory(
            self, self.tr("Choose recording directory"), default_dir
        )
        if not chosen:
            return
        self._start_recording(chosen)

    def _start_recording(self, output_dir: str) -> None:
        # Determine the source resolution from the current video pane
        # pixmap. Falls back to a sane default if no frame has arrived yet.
        from core.services.streaming.VideoRecordingService import (
            RecordingConfig,
            VideoRecorder,
        )
        pixmap = self.ui.videoLabel.pixmap()
        if pixmap is not None and not pixmap.isNull():
            resolution = (max(640, pixmap.width()), max(360, pixmap.height()))
        else:
            resolution = (1280, 720)

        config = RecordingConfig(
            output_dir=output_dir,
            filename_prefix=f"flight_{self.pairing_code}",
            fps=30,
        )
        recorder = VideoRecorder(config)

        # Surface the recorder's output path on the status strip while
        # recording is active.
        def _on_recording_started(path: str) -> None:
            self._recording_path = path
            self.ui.statusBadgeLabel.setText(self.tr("REC ● {filename}").format(
                filename=__import__("os").path.basename(path)
            ))

        def _on_recording_error(msg: str) -> None:
            self.ui.statusBadgeLabel.setText(self.tr("REC error: {msg}").format(msg=msg))

        recorder.recordingStarted.connect(_on_recording_started)
        recorder.errorOccurred.connect(_on_recording_error)

        if not recorder.start_recording(resolution):
            # Service already logged the failure; surface to the user via
            # the status strip so they're not left guessing.
            self.ui.statusBadgeLabel.setText(self.tr("REC failed to start"))
            return
        self._recorder = recorder

    def _stop_recording(self) -> None:
        recorder = self._recorder
        self._recorder = None
        if recorder is None:
            return
        try:
            recorder.stop_recording()
        except Exception:  # noqa: BLE001 - cleanup must not crash UI
            pass
        if self._recording_path:
            self.ui.statusBadgeLabel.setText(self.tr("Recording saved"))
            self._recording_path = None

    # ------------------------------------------------------------------
    # status strip
    # ------------------------------------------------------------------

    def update_stats(self, stats: dict) -> None:
        self.ui.iceStateLabel.setText(
            self.tr("Network: {state}").format(
                state=self._friendly_ice_state(stats.get("ice_state"))
            )
        )
        width = stats.get("width") or 0
        height = stats.get("height") or 0
        self.ui.resolutionLabel.setText(f"{width}x{height}")
        fps = stats.get("fps")
        self.ui.fpsLabel.setText(f"{fps:.1f} fps" if isinstance(fps, (int, float)) else "0 fps")
        kbps = stats.get("bitrate_kbps")
        self.ui.bitrateLabel.setText(f"{kbps:.0f} kbps" if isinstance(kbps, (int, float)) else "0 kbps")
        latency = stats.get("one_way_latency_ms")
        if isinstance(latency, (int, float)):
            self.ui.latencyLabel.setText(self.tr("latency: {ms:.0f}ms").format(ms=latency))
        else:
            self.ui.latencyLabel.setText(self.tr("latency: --"))

    def set_ice_state(self, state: str) -> None:
        self.ui.iceStateLabel.setText(
            self.tr("Network: {state}").format(state=self._friendly_ice_state(state))
        )

    # ------------------------------------------------------------------
    # rename — operator nicknames persisted by aircraft serial (preferred)
    # or pairing code (transitional, before telemetry arrives)
    # ------------------------------------------------------------------

    _RENAME_GROUP = "FlightTileNicknamesBySerial"
    _LEGACY_RENAME_GROUP = "FlightTileNames"  # pre-serial-keyed; pairing_code

    @classmethod
    def _read_setting(cls, group: str, key: str) -> Optional[str]:
        if not key:
            return None
        from PySide6.QtCore import QSettings
        settings = QSettings("ADIAT", "FlightViewer")
        settings.beginGroup(group)
        try:
            value = settings.value(key)
        finally:
            settings.endGroup()
        return value if isinstance(value, str) and value.strip() else None

    @classmethod
    def _write_setting(cls, group: str, key: str, value: Optional[str]) -> None:
        if not key:
            return
        from PySide6.QtCore import QSettings
        settings = QSettings("ADIAT", "FlightViewer")
        settings.beginGroup(group)
        try:
            if value and value.strip():
                settings.setValue(key, value.strip())
            else:
                settings.remove(key)
        finally:
            settings.endGroup()
        settings.sync()

    def _persisted_nickname(self) -> Optional[str]:
        """Look up the operator's nickname using the best key we have.

        Preference: serial > pairing code. The serial entry takes
        priority because it follows the drone across new pairing
        sessions (each session gets a fresh code).
        """
        if self._aircraft_serial:
            value = self._read_setting(self._RENAME_GROUP, self._aircraft_serial)
            if value:
                return value
        return self._read_setting(self._LEGACY_RENAME_GROUP, self.pairing_code)

    def _migrate_pairing_code_nickname_to_serial(self, serial: str) -> None:
        """Move a pre-telemetry rename from pairing-code-keyed to serial-keyed.

        Handles the case where the operator renamed the feed before
        the publisher's ``aircraft_serial`` arrived; the nickname
        wouldn't otherwise survive a new pairing session.
        """
        legacy = self._read_setting(self._LEGACY_RENAME_GROUP, self.pairing_code)
        if not legacy:
            return
        existing = self._read_setting(self._RENAME_GROUP, serial)
        if not existing:
            self._write_setting(self._RENAME_GROUP, serial, legacy)
        self._write_setting(self._LEGACY_RENAME_GROUP, self.pairing_code, None)

    def _resolve_title(self) -> str:
        """Compute the title using the precedence chain (see ``__init__``)."""
        nickname = self._persisted_nickname()
        if nickname:
            return nickname
        if self._aircraft_name:
            return self.tr("{name} · {code}").format(
                name=self._aircraft_name, code=self.pairing_code
            )
        return self.tr("Feed {code}").format(code=self.pairing_code)

    def _refresh_title_and_tooltip(self) -> None:
        """Re-resolve the title + tooltip after identity/nickname changes.

        Emits ``displayNameChanged`` when the resolved title actually
        changed so downstream consumers (gallery row labels, feed
        filter dropdown, map dock if it ever shows names) update in
        lock-step without polling.
        """
        title = self._resolve_title()
        prev_title = self.windowTitle()
        if prev_title != title:
            self.setWindowTitle(title)
            self.displayNameChanged.emit(self.pairing_code, title)
        sw = self._subwindow()
        if sw is not None and sw.windowTitle() != title:
            sw.setWindowTitle(title)
        # Status-strip tooltip surfaces the serial so the operator can
        # disambiguate two identically-nicknamed drones (plan §19.3).
        if self._aircraft_serial:
            self.ui.statusStrip.setToolTip(
                self.tr("Aircraft serial: {sn}").format(sn=self._aircraft_serial)
            )
        else:
            self.ui.statusStrip.setToolTip("")

    def display_name(self) -> str:
        """Return the current operator-facing label (nickname/aircraft/code)."""
        return self.windowTitle()

    def nickname(self) -> Optional[str]:
        """Return the operator-set nickname, if any."""
        return self._persisted_nickname()

    def rename(self, new_name: str) -> None:
        """Persist a new nickname and refresh the title.

        Keys by ``aircraft_serial`` when telemetry has populated it,
        otherwise by ``pairing_code`` (the value migrates to a
        serial-keyed entry once telemetry arrives — see
        :meth:`_migrate_pairing_code_nickname_to_serial`).
        """
        cleaned = (new_name or "").strip()
        if not cleaned:
            return
        if self._aircraft_serial:
            self._write_setting(self._RENAME_GROUP, self._aircraft_serial, cleaned)
        else:
            self._write_setting(self._LEGACY_RENAME_GROUP, self.pairing_code, cleaned)
        self._refresh_title_and_tooltip()

    def _prompt_rename(self) -> None:
        """Pop a QInputDialog asking the operator for a new feed name."""
        from PySide6.QtWidgets import QInputDialog
        # Pre-fill with the operator's existing nickname (if any), not the
        # auto-derived title — so renames feel like edits, not retyping.
        current_nickname = self._persisted_nickname() or ""
        new_name, ok = QInputDialog.getText(
            self,
            self.tr("Rename Feed"),
            self.tr(
                "Nickname for this drone (persists across new pairing codes "
                "via the aircraft serial number). Leave blank to clear."
            ),
            text=current_nickname,
        )
        if not ok:
            return
        cleaned = (new_name or "").strip()
        if cleaned:
            self.rename(cleaned)
            return
        # Clear: drop both keys so the title falls through to the
        # telemetry-derived label.
        if self._aircraft_serial:
            self._write_setting(self._RENAME_GROUP, self._aircraft_serial, None)
        self._write_setting(self._LEGACY_RENAME_GROUP, self.pairing_code, None)
        self._refresh_title_and_tooltip()

    def _friendly_ice_state(self, raw: Optional[str]) -> str:
        """Map raw WebRTC ICE state names to operator-friendly labels.

        ``completed`` is the ideal WebRTC state — ICE finished all its
        checks and locked onto the best candidate pair — but reads as
        "the session ended" to a non-WebRTC operator. Conflating it
        with ``connected`` is fine for the status strip; both mean
        "media is flowing." Same logic for the rest of the raw names
        (``checking`` reads as "connecting"; ``new`` reads as
        "initializing").
        """
        if not raw:
            return "--"
        return {
            "new": self.tr("Initializing"),
            "checking": self.tr("Connecting"),
            "connected": self.tr("Connected"),
            "completed": self.tr("Connected"),
            "disconnected": self.tr("Disconnected"),
            "failed": self.tr("Failed"),
            "closed": self.tr("Closed"),
        }.get(str(raw).lower(), str(raw))

    # ------------------------------------------------------------------
    # context menu (right-click on dock title; plan §4)
    # ------------------------------------------------------------------

    def _build_context_menu(self) -> None:
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

    def _on_context_menu(self, pos) -> None:
        menu = QMenu(self)

        rename = QAction(self.tr("Rename Feed..."), menu)
        rename.triggered.connect(self._prompt_rename)
        menu.addAction(rename)

        menu.addSeparator()

        full_screen = QAction(self.tr("Full Screen"), menu)
        full_screen.triggered.connect(lambda: self.fullscreenRequested.emit(self))
        menu.addAction(full_screen)

        # "Maximize" defers to the wrapping QMdiSubWindow's native
        # maximize, which fills the MDI area (i.e. stays inside the
        # viewer). The OS-native maximize button on the subwindow's
        # title bar does the same thing.
        sw = self._subwindow()
        if sw is not None:
            if sw.isMaximized():
                restore = QAction(self.tr("Restore"), menu)
                restore.triggered.connect(self.restore_subwindow)
                menu.addAction(restore)
            else:
                maximize = QAction(self.tr("Maximize"), menu)
                maximize.triggered.connect(self.maximize_within_viewer)
                menu.addAction(maximize)

        menu.addSeparator()

        mute = QAction(self.tr("Mute Detections in Gallery"), menu)
        mute.setCheckable(True)
        mute.setChecked(self._gallery_muted)

        def _toggle_mute():
            self._gallery_muted = not self._gallery_muted
            self.muteGalleryToggled.emit(self, self._gallery_muted)

        mute.triggered.connect(_toggle_mute)
        menu.addAction(mute)

        # Recording toggle. Reuses the existing :class:`VideoRecorder`
        # service so the output format matches RTMP/HDMI recordings the
        # rest of the app produces (plan §15 M3 — Recording via existing
        # VideoRecordingService).
        if self.is_recording:
            stop_rec = QAction(self.tr("Stop Recording"), menu)
            stop_rec.triggered.connect(self._stop_recording)
            menu.addAction(stop_rec)
        else:
            start_rec = QAction(self.tr("Start Recording…"), menu)
            start_rec.triggered.connect(self._start_recording_from_menu)
            menu.addAction(start_rec)

        reconnect = QAction(self.tr("Reconnect"), menu)
        reconnect.triggered.connect(lambda: self.reconnectRequested.emit(self))
        menu.addAction(reconnect)

        menu.addSeparator()

        close_act = QAction(self.tr("Close"), menu)
        close_act.triggered.connect(lambda: self.closeRequested.emit(self))
        menu.addAction(close_act)

        menu.exec(self.mapToGlobal(pos))

    # ------------------------------------------------------------------
    # full-screen toggle (delegates to the wrapping QMdiSubWindow)
    # ------------------------------------------------------------------

    def toggle_fullscreen(self) -> None:
        """Toggle the wrapping sub-window between maximized and normal.

        We delegate "full-screen" to the MDI sub-window's maximize state
        — true OS full-screen would yank the tile out of the viewer's
        widget hierarchy, breaking the contain-to-parent contract. The
        operator can resize the *viewer* to fill the desktop for an
        effectively-fullscreen feed.
        """
        sw = self._subwindow()
        if sw is None:
            return
        if sw.isMaximized():
            sw.showNormal()
        else:
            sw.showMaximized()

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt name
        # F11 / Esc both behave like a maximize-toggle now that there's
        # no separate full-screen window state to escape.
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
            return
        if event.key() == Qt.Key_Escape:
            sw = self._subwindow()
            if sw is not None and sw.isMaximized():
                sw.showNormal()
                return
        super().keyPressEvent(event)

    # ------------------------------------------------------------------
    # gallery muting accessor
    # ------------------------------------------------------------------

    @property
    def is_gallery_muted(self) -> bool:
        return self._gallery_muted
