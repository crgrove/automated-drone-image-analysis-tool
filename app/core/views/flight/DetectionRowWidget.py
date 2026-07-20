"""Single-detection row used by both per-tile and aggregate gallery panels.

Per plan §7 the same widget is reused — scoped to one tile in the tile's
``QListWidget`` and aggregated across tiles in the Mission Gallery dock.
The widget itself is dumb: it accepts a fully-formed detection dict (the
shape produced by :class:`~core.services.streaming.DetectionFeedService.\
DetectionFeedService` — the channel envelope merged with ``thumb_bytes``)
and renders it.
"""

from __future__ import annotations

import time
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QWidget

from core.services.SettingsService import SettingsService
from core.views.flight.detection_row_ui import Ui_DetectionRowWidget
from helpers.TranslationMixin import TranslationMixin


class DetectionRowWidget(TranslationMixin, QWidget, Ui_DetectionRowWidget):
    """Render a single detection envelope + thumbnail.

    Args:
        detection: Envelope produced by :class:`DetectionFeedService`. Keys
            consulted: ``class_name``, ``confidence``, ``location``,
            ``captured_at_ms``, ``thumb_bytes``, ``feed_label``.
        parent: Qt parent.
    """

    viewRequested = Signal(dict)
    coordinatesCopied = Signal(str)

    def __init__(self, detection: dict, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setupUi(self)
        self._detection = dict(detection)
        self._settings = SettingsService()

        self.viewButton.clicked.connect(self._on_view_clicked)
        self.copyCoordsButton.clicked.connect(self._on_copy_clicked)
        # Clicking the thumbnail opens the same popup as the View button
        # — most operators reach for the image first, so wire it up.
        self.thumbnailLabel.setCursor(Qt.PointingHandCursor)
        self.thumbnailLabel.installEventFilter(self)
        self.update_detection(detection)

    def eventFilter(self, watched, event):  # noqa: N802 - Qt name
        from PySide6.QtCore import QEvent
        if (
            watched is self.thumbnailLabel
            and event.type() == QEvent.MouseButtonRelease
            and event.button() == Qt.LeftButton
        ):
            self._on_view_clicked()
            return True
        return super().eventFilter(watched, event)

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def update_detection(self, detection: dict) -> None:
        """Repaint with a (possibly updated) detection envelope."""
        self._detection = dict(detection)
        cls = str(detection.get("class_name") or detection.get("detector_id") or "OBJECT")
        self.classLabel.setText(cls.upper())

        confidence = detection.get("confidence")
        if isinstance(confidence, (int, float)):
            self.confidenceLabel.setText(f"{float(confidence) * 100:.0f}%")
        else:
            self.confidenceLabel.setText("--%")

        loc = detection.get("location") or {}
        lat = loc.get("lat") if isinstance(loc, dict) else None
        lon = loc.get("lon") if isinstance(loc, dict) else None
        if lat is not None and lon is not None:
            self.locationLabel.setText(self._format_coords(lat, lon))
        else:
            self.locationLabel.setText("--, --")

        ts_ms = detection.get("captured_at_ms")
        if ts_ms is not None:
            try:
                ts = float(ts_ms) / 1000.0
                lt = time.localtime(ts)
                self.timestampLabel.setText(time.strftime("%H:%M:%S", lt))
            except (TypeError, ValueError):
                self.timestampLabel.setText("--:--:--")
        else:
            self.timestampLabel.setText("--:--:--")

        # Source-aircraft line. Precedence:
        #   1. ``feed_display_name`` — the tile's current operator-facing
        #      label (nickname if set, otherwise the aircraft formula
        #      already resolved by the tile). Always takes priority so
        #      a rename propagates here without us re-resolving.
        #   2. ``aircraft_name`` from telemetry, with pairing code in
        #      parens as a disambiguator (plan §19.3).
        #   3. ``feed_label`` ("Tile-<code>") — first-second fallback
        #      before telemetry populates.
        display_name = detection.get("feed_display_name")
        aircraft_name = detection.get("aircraft_name")
        code = detection.get("feed_id")
        if isinstance(display_name, str) and display_name.strip():
            self.feedLabel.setText(display_name.strip())
        elif isinstance(aircraft_name, str) and aircraft_name.strip():
            if isinstance(code, str) and code:
                self.feedLabel.setText(
                    self.tr("{name} ({code})").format(
                        name=aircraft_name.strip(), code=code
                    )
                )
            else:
                self.feedLabel.setText(aircraft_name.strip())
        else:
            feed_label = detection.get("feed_label")
            if feed_label:
                self.feedLabel.setText(self.tr("Feed: {feed}").format(feed=feed_label))
            else:
                self.feedLabel.setText("")
        # Serial in the row tooltip — disambiguates identically-named
        # drones if the same operator nicknames two of them the same.
        serial = detection.get("aircraft_serial")
        if isinstance(serial, str) and serial.strip():
            self.feedLabel.setToolTip(
                self.tr("Aircraft serial: {sn}").format(sn=serial.strip())
            )
        else:
            self.feedLabel.setToolTip("")

        self._apply_thumbnail(detection.get("thumb_bytes"))

    @property
    def detection(self) -> dict:
        return dict(self._detection)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _apply_thumbnail(self, blob: Optional[bytes]) -> None:
        if not blob:
            self.thumbnailLabel.setPixmap(QPixmap())
            self.thumbnailLabel.setText(self.tr("no\nthumb"))
            self.thumbnailLabel.setAlignment(Qt.AlignCenter)
            return
        image = QImage()
        if not image.loadFromData(blob):
            self.thumbnailLabel.setPixmap(QPixmap())
            self.thumbnailLabel.setText(self.tr("bad\nthumb"))
            return
        pixmap = QPixmap.fromImage(image).scaled(
            self.thumbnailLabel.maximumWidth(),
            self.thumbnailLabel.maximumHeight(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.thumbnailLabel.setPixmap(pixmap)
        self.thumbnailLabel.setText("")

    def _format_coords(self, lat: float, lon: float) -> str:
        """Format coordinates per operator preference (DD/DM/MGRS).

        DD is the M1 default; DM is implemented inline; MGRS is delegated
        to ``pygeodesy`` if it is available (best-effort).
        """
        fmt = (self._settings.get_setting("PositionFormat", "Lat/Long - Decimal Degrees") or "")
        fmt_lower = str(fmt).lower()
        try:
            if "decimal" in fmt_lower or "dd" in fmt_lower:
                return f"{lat:.6f}, {lon:.6f}"
            if "minute" in fmt_lower or "dm" in fmt_lower:
                return f"{self._dd_to_dm(lat, is_lat=True)}, {self._dd_to_dm(lon, is_lat=False)}"
            if "mgrs" in fmt_lower:
                mgrs = self._dd_to_mgrs(lat, lon)
                if mgrs:
                    return mgrs
        except Exception:  # noqa: BLE001 - formatter must not crash UI
            pass
        return f"{lat:.6f}, {lon:.6f}"

    @staticmethod
    def _dd_to_dm(value: float, *, is_lat: bool) -> str:
        hemi_pos, hemi_neg = ("N", "S") if is_lat else ("E", "W")
        hemi = hemi_pos if value >= 0 else hemi_neg
        value = abs(value)
        deg = int(value)
        minutes = (value - deg) * 60.0
        return f"{deg}° {minutes:.4f}' {hemi}"

    @staticmethod
    def _dd_to_mgrs(lat: float, lon: float) -> str:
        try:
            from pygeodesy.mgrs import toMgrs  # type: ignore
        except Exception:
            return ""
        try:
            return str(toMgrs(lat, lon))
        except Exception:
            return ""

    # ------------------------------------------------------------------
    # signals
    # ------------------------------------------------------------------

    def _on_view_clicked(self) -> None:
        self.viewRequested.emit(self._detection)
        self._show_full_view()

    def _show_full_view(self) -> None:
        """Open a modal popout with the full-frame context (or the
        cropped thumb if no context frame is available), the bbox
        drawn on top, and the detection metadata.
        """
        from PySide6.QtGui import QPainter, QPen, QColor

        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr("Detection"))
        dialog.resize(1100, 800)
        layout = QVBoxLayout(dialog)

        # Pick the best available image source. The full-frame snapshot
        # the tile attaches on promotion is preferred (operator sees the
        # entire scene); fall back to the small cropped thumb if it's
        # missing (e.g., snapshot replay after reconnect).
        context_bytes = self._detection.get("context_frame_jpeg")
        bbox = self._detection.get("bbox_norm") or []
        has_context = isinstance(context_bytes, (bytes, bytearray)) and context_bytes
        thumb_bytes = self._detection.get("thumb_bytes")

        image_label = QLabel(dialog)
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setMinimumHeight(500)
        image_label.setStyleSheet("QLabel { background-color: black; }")

        image = QImage()
        if has_context and image.loadFromData(bytes(context_bytes)):
            # Paint the bbox on top before display so the operator can
            # see exactly which target in the scene corresponds to this
            # gallery row.
            if isinstance(bbox, (list, tuple)) and len(bbox) == 4:
                try:
                    x, y, w, h = (float(v) for v in bbox)
                    pixmap = QPixmap.fromImage(image)
                    painter = QPainter(pixmap)
                    pen = QPen(QColor(251, 94, 28))  # AdiatColors.Accent orange
                    pen.setWidth(max(3, pixmap.width() // 300))
                    painter.setPen(pen)
                    painter.drawRect(
                        int(round(x * pixmap.width())),
                        int(round(y * pixmap.height())),
                        int(round(w * pixmap.width())),
                        int(round(h * pixmap.height())),
                    )
                    painter.end()
                    image_label.setPixmap(
                        pixmap.scaled(
                            1080, 720,
                            Qt.KeepAspectRatio, Qt.SmoothTransformation,
                        )
                    )
                except (TypeError, ValueError):
                    image_label.setPixmap(QPixmap.fromImage(image))
            else:
                image_label.setPixmap(QPixmap.fromImage(image))
        elif thumb_bytes and image.loadFromData(bytes(thumb_bytes)):
            # Scale the cropped thumb up for visibility — the raw JPEG
            # is only ~96 px wide, which renders as a postage stamp in
            # an 1100×800 dialog.
            image_label.setPixmap(
                QPixmap.fromImage(image).scaled(
                    800, 600,
                    Qt.KeepAspectRatio, Qt.SmoothTransformation,
                )
            )
        else:
            image_label.setText(self.tr("No image available."))
        layout.addWidget(image_label, stretch=1)

        meta_lines = []
        # ``aircraft_name`` + ``aircraft_serial`` lead the popout meta so the
        # operator can unambiguously identify the source drone without
        # hunting through the wire-level fields below them.
        for key in (
            "aircraft_name", "aircraft_serial",
            "class_name", "confidence", "captured_at_ms",
            "track_key", "feed_label",
        ):
            if key in self._detection and self._detection.get(key) is not None:
                meta_lines.append(f"{key}: {self._detection[key]}")
        loc = self._detection.get("location") or {}
        if isinstance(loc, dict) and loc:
            meta_lines.append(f"location: {loc}")
        meta_label = QLabel("\n".join(meta_lines), dialog)
        meta_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(meta_label)

        dialog.exec()

    def _on_copy_clicked(self) -> None:
        loc = self._detection.get("location") or {}
        lat = loc.get("lat") if isinstance(loc, dict) else None
        lon = loc.get("lon") if isinstance(loc, dict) else None
        if lat is None or lon is None:
            return
        formatted = self._format_coords(lat, lon)
        QApplication.clipboard().setText(formatted)
        self.coordinatesCopied.emit(formatted)
