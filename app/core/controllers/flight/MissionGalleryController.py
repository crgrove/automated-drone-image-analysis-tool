"""Aggregator controller for the Mission Gallery dock.

Holds the per-session detection store, applies the user's filter selection,
and pushes the filtered+sorted list to the dock view for repaint. Listens
to :class:`FlightTileController` instances via the Flight Viewer
controller and tracks per-tile mute state per plan §7.
"""

from __future__ import annotations

import os
import time
from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QFileDialog, QMessageBox

from core.services.LoggerService import LoggerService
from core.views.flight.MissionGalleryDock import MissionGalleryDock


class MissionGalleryController(QObject):
    """Owns the aggregate detection list and drives the dock's repaint."""

    def __init__(self, dock: MissionGalleryDock, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.logger = LoggerService()
        self._dock = dock
        self._detections: List[Tuple[float, dict]] = []
        self._muted_feeds: set[str] = set()
        # Track-key → JPEG bytes cache that survives tile close/reopen
        # within a single viewer session. Snapshot replays (which fire on
        # reconnect to catch the desktop up with tracks the publisher
        # already promoted) carry meta only — the mobile-side
        # ``snapshotJson()`` strips thumb bytes because they're too bulky
        # to ship in a single JSON blob (publish plan §6). Without this
        # cache, every reconnected row would render "no thumb" even
        # though the desktop already received the thumbnail earlier.
        self._thumb_cache: Dict[str, bytes] = {}
        self._dock.filtersChanged.connect(self._render)
        self._dock.exportRequested.connect(self._on_export_clicked)

    # ------------------------------------------------------------------
    # feed registration (called by FlightViewerController)
    # ------------------------------------------------------------------

    def register_feed(self, feed_id: str, label: str) -> None:
        self._dock.register_feed(feed_id, label)

    def set_feed_display_name(self, feed_id: str, display_name: str) -> None:
        """Rename an active feed across the gallery — dropdown + every row.

        Wired to :class:`FlightTileController.feedDisplayNameChanged` so
        an operator-typed nickname (or a telemetry-derived aircraft
        name) propagates to:

        * The Feed filter dropdown entry (label only; ``itemData`` stays
          the pairing code so the filter logic doesn't move).
        * Every existing detection row's ``feed_display_name`` field,
          so already-rendered rows pick up the new label on re-paint.
        """
        if not isinstance(feed_id, str) or not feed_id:
            return
        if not isinstance(display_name, str) or not display_name.strip():
            return
        cleaned = display_name.strip()
        self._dock.update_feed_label(feed_id, cleaned)
        patched = False
        for _, detection in self._detections:
            if detection.get("feed_id") == feed_id:
                detection["feed_display_name"] = cleaned
                patched = True
        if patched:
            self._render()

    def deregister_feed(self, feed_id: str) -> None:
        self._dock.deregister_feed(feed_id)
        before = len(self._detections)
        self._detections = [
            (ts, d) for (ts, d) in self._detections if d.get("feed_id") != feed_id
        ]
        if len(self._detections) != before:
            self._render()

    def set_feed_muted(self, feed_id: str, muted: bool) -> None:
        if muted:
            self._muted_feeds.add(feed_id)
        else:
            self._muted_feeds.discard(feed_id)
        self._render()

    # ------------------------------------------------------------------
    # detection ingest
    # ------------------------------------------------------------------

    def add_detection(self, _feed_id: str, detection: dict) -> None:
        track_key = detection.get("track_key")
        thumb_bytes = detection.get("thumb_bytes")

        # Thumbnail cache: remember thumbs as they arrive on live
        # promotions; restore them on snapshot replays that carry meta
        # only. Keyed by ``track_key`` so the cache survives tile
        # close/reopen and snapshot dedup boundaries.
        if isinstance(thumb_bytes, (bytes, bytearray)) and thumb_bytes:
            if isinstance(track_key, str) and track_key:
                self._thumb_cache[track_key] = bytes(thumb_bytes)
        elif isinstance(track_key, str) and track_key in self._thumb_cache:
            detection = dict(detection)
            detection["thumb_bytes"] = self._thumb_cache[track_key]

        ts = self._timestamp(detection)

        # Register the detector id (universal across publishers) rather
        # than the per-detector class_name — operators pick from
        # ``person`` / ``color-range`` / ``motion`` / ``dji-native``
        # instead of a flat list of incompatible per-detector labels.
        detector_id = detection.get("detector_id") or ""
        if detector_id:
            self._dock.register_detector(str(detector_id))

        # Plan §7 per-track lifecycle: PROMOTE creates the row, UPDATE
        # refreshes it in place. Dedup is keyed on ``track_key`` — the
        # wire ``event`` field is informational. Without this, every
        # UPDATE for a long-lived (moving) target spawns a duplicate
        # gallery row.
        if isinstance(track_key, str) and track_key:
            for i, (_existing_ts, existing) in enumerate(self._detections):
                if existing.get("track_key") == track_key:
                    # Right-hand-side wins where present; preserve any
                    # promote-time fields (``context_frame_jpeg``, etc.)
                    # that the UPDATE envelope doesn't carry.
                    merged = {
                        **existing,
                        **{k: v for k, v in detection.items() if v is not None},
                    }
                    self._detections[i] = (ts, merged)
                    self._render()
                    return

        # New track — append.
        self._detections.append((ts, dict(detection)))
        self._render()

    def replace_snapshot(self, feed_id: str, detections: list) -> None:
        self._detections = [
            (ts, d) for (ts, d) in self._detections if d.get("feed_id") != feed_id
        ]
        for d in detections:
            if not isinstance(d, dict):
                continue
            d = dict(d)
            d.setdefault("feed_id", feed_id)
            self._detections.append((self._timestamp(d), d))
        self._render()

    def clear(self) -> None:
        self._detections.clear()
        self._thumb_cache.clear()
        self._dock.clear()

    # ------------------------------------------------------------------
    # desktop-side thumb cropping (plan §19.4.1)
    # ------------------------------------------------------------------

    def upsert_thumb(self, track_key: str, jpeg_bytes: bytes) -> None:
        """Attach a freshly-cropped JPEG to an existing track's row.

        Mobile no longer ships thumbnails over the DataChannel (plan
        §19.4.1); the desktop now crops them locally from the live
        video frame and emits ``DetectionThumbCropper.thumbReady`` per
        track. This slot stores the bytes in the per-key thumb cache
        AND patches every in-flight gallery row that matches the same
        ``track_key`` so the operator sees the new thumbnail without
        waiting for the next live promotion to re-render.
        """
        if not isinstance(track_key, str) or not track_key:
            return
        if not isinstance(jpeg_bytes, (bytes, bytearray)) or not jpeg_bytes:
            return
        self._thumb_cache[track_key] = bytes(jpeg_bytes)
        changed = False
        for _, detection in self._detections:
            if detection.get("track_key") == track_key:
                detection["thumb_bytes"] = bytes(jpeg_bytes)
                changed = True
        if changed:
            self._render()

    @property
    def detections(self) -> List[dict]:
        return [d for _, d in self._detections]

    # ------------------------------------------------------------------
    # internal
    # ------------------------------------------------------------------

    @staticmethod
    def _timestamp(detection: dict) -> float:
        ts = detection.get("captured_at_ms")
        if isinstance(ts, (int, float)):
            return float(ts)
        return 0.0

    def _passes_filters(self, detection: dict) -> bool:
        feed_id = detection.get("feed_id")
        if feed_id in self._muted_feeds:
            return False
        feed_filter = self._dock.selected_feed()
        if feed_filter and feed_filter != feed_id:
            return False
        detector_filter = self._dock.selected_detector()
        if detector_filter and detector_filter != detection.get("detector_id"):
            return False
        min_score = self._dock.min_score()
        if min_score > 0:
            score = detection.get("confidence")
            if not isinstance(score, (int, float)) or score < min_score:
                return False
        return True

    def _render(self) -> None:
        # Newest first — the operator's eyes naturally land on the top
        # of the list, so put the most recent detection there. Combined
        # with ``MissionGalleryDock.render_rows`` preserving scroll, a
        # user reviewing older rows isn't bumped by new arrivals.
        rows = [d for (_, d) in sorted(self._detections, key=lambda t: t[0], reverse=True)]
        filtered = [d for d in rows if self._passes_filters(d)]
        self._dock.render_rows(filtered)

    def _on_export_clicked(self) -> None:
        """Write the filtered gallery to an ADIAT image-mode results folder.

        Per plan §15 M3 — "Optional export of mission gallery into standard
        ADIAT image-mode gallery format." The output is a directory the
        operator can re-open via the main window's *Load Results File*
        action, containing:

        * One JPEG per detection (thumbnail bytes, or a placeholder when
          the detection arrived without one).
        * ``ADIAT_Data.xml`` shaped like an ordinary image-mode results
          file: each detection becomes one ``image`` entry with a single
          ``areas_of_interest`` capturing the bbox + GPS location.

        The export uses ``XmlService`` (the same one MainWindow's
        ResultsScanner consumes), so loading the output requires no
        new code on the receiving side.
        """
        # Bounce out to a directory picker. The Mission Gallery dock is
        # the natural parent so the dialog inherits the right window.
        parent_widget = self._dock
        out_dir = QFileDialog.getExistingDirectory(
            parent_widget,
            "Choose export directory",
        )
        if not out_dir:
            return

        rows = [d for d in self.detections if self._passes_filters(d)]
        if not rows:
            QMessageBox.information(
                parent_widget,
                "Export",
                "No detections match the current filters.",
            )
            return

        try:
            xml_path = self._write_export(out_dir, rows)
        except Exception as exc:  # noqa: BLE001 - surface to user
            self.logger.error(
                f"Mission Gallery export failed: {exc}"
            )
            QMessageBox.critical(
                parent_widget,
                "Export failed",
                f"Could not write the export:\n{exc}",
            )
            return

        self.logger.info(
            f"Mission Gallery exported {len(rows)} detections to {xml_path}"
        )
        QMessageBox.information(
            parent_widget,
            "Export complete",
            (
                f"Wrote {len(rows)} detections to:\n{xml_path}\n\n"
                "Open this file from the Image Analysis window via "
                "Menu → Load Results File."
            ),
        )

    def _write_export(self, out_dir: str, rows: list[dict]) -> str:
        """Write thumbnails + ``ADIAT_Data.xml`` into ``out_dir``.

        Returns the path of the XML file that was written.
        """
        # Import lazily so the gallery module doesn't pull in XmlService
        # (and its dependencies) at import time.
        from core.services.XmlService import XmlService

        os.makedirs(out_dir, exist_ok=True)
        xml = XmlService()
        xml.xml_path = os.path.join(out_dir, "ADIAT_Data.xml")

        # Settings block — fields are required by the image-mode loader
        # even though they're meaningless for a Flight Viewer export.
        settings = {
            "output_dir": out_dir,
            "input_dir": out_dir,
            "num_processes": 1,
            "identifier_color": (0, 255, 0),
            "aoi_radius": 20,
            "min_area": 1,
            "max_area": 0,
            "hist_ref_path": "",
            "kmeans_clusters": 0,
            "algorithm": "FlightViewer",
            "thermal": "False",
            "options": {
                "exported_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "source": "ADIAT Flight Viewer",
            },
        }
        # XmlService.add_settings_to_xml is the dedicated path for writing
        # settings into the new tree.
        xml.add_settings_to_xml(**settings)

        # One ``image`` per detection. The image's areas_of_interest
        # captures the bbox (in fractional coords) and the GPS location
        # so the standard viewer can re-render the pin + AOI overlay.
        for idx, detection in enumerate(rows):
            thumb_path = self._write_thumb(out_dir, idx, detection)
            img_record = {
                "path": thumb_path,
                "width": 0,
                "height": 0,
                "aois": [self._build_aoi(detection)],
            }
            xml.add_image_to_xml(img_record)

        xml.save_xml_file(xml.xml_path)
        return xml.xml_path

    @staticmethod
    def _write_thumb(out_dir: str, idx: int, detection: dict) -> str:
        """Write the detection's thumbnail (or a placeholder) and return its path."""
        thumb_bytes = detection.get("thumb_bytes")
        filename = f"detection_{idx:04d}.jpg"
        thumb_path = os.path.join(out_dir, filename)
        if isinstance(thumb_bytes, (bytes, bytearray)) and thumb_bytes:
            with open(thumb_path, "wb") as fp:
                fp.write(thumb_bytes)
        else:
            # No thumbnail in the snapshot — encode a tiny 1x1 black JPEG
            # so the XML loader doesn't choke on a missing file. cv2 is
            # already a hard dependency of the streaming stack.
            import cv2
            import numpy as np
            placeholder = np.zeros((1, 1, 3), dtype=np.uint8)
            ok, buf = cv2.imencode(".jpg", placeholder)
            if ok:
                with open(thumb_path, "wb") as fp:
                    fp.write(buf.tobytes())
            else:
                # Last-resort: write the minimal SOI+EOI marker pair. Not a
                # valid renderable JPEG but enough to satisfy "file exists".
                with open(thumb_path, "wb") as fp:
                    fp.write(b"\xff\xd8\xff\xd9")
        return thumb_path

    @staticmethod
    def _build_aoi(detection: dict) -> dict:
        """Compose a single areas_of_interest entry for ``detection``."""
        bbox = detection.get("bbox_norm") or []
        # Default to a small AOI in the center of a synthetic 256x256 frame
        # so the image-mode viewer can render a pin even when bbox is missing.
        if isinstance(bbox, (list, tuple)) and len(bbox) >= 4:
            try:
                # Translate normalized bbox into a center+radius pair.
                # `bbox_norm` is [x_min, y_min, w, h] in 0..1 coords; we
                # synthesize against a 256x256 reference so the AOI lands
                # somewhere recognisable in the exported placeholder JPEG.
                w_ref, h_ref = 256, 256
                cx = int((float(bbox[0]) + float(bbox[2]) / 2.0) * w_ref)
                cy = int((float(bbox[1]) + float(bbox[3]) / 2.0) * h_ref)
                radius = max(8, int(min(bbox[2], bbox[3]) * min(w_ref, h_ref) / 2.0))
                area = int(float(bbox[2]) * float(bbox[3]) * w_ref * h_ref)
            except (TypeError, ValueError):
                cx, cy, radius, area = 128, 128, 20, 100
        else:
            cx, cy, radius, area = 128, 128, 20, 100

        aoi = {
            "center": (cx, cy),
            "radius": radius,
            "area": area,
        }
        confidence = detection.get("confidence")
        if isinstance(confidence, (int, float)):
            aoi["confidence"] = float(confidence)
            aoi["score_type"] = "confidence"
            aoi["raw_score"] = float(confidence)
            aoi["score_method"] = "FlightViewer"

        loc = detection.get("location")
        if isinstance(loc, dict):
            lat = loc.get("lat")
            lon = loc.get("lon")
            if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                comment = f"GPS: {lat:.6f}, {lon:.6f}"
                cls = detection.get("class_name") or detection.get("detector_id") or ""
                if cls:
                    comment = f"{cls} @ {comment}"
                aoi["user_comment"] = comment

        return aoi
