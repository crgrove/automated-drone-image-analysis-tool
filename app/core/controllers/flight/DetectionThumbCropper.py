"""Desktop-side per-detection thumbnail cropper (plan §19.4.1).

Replaces the mobile-side ``BboxCropper`` → JPEG → ``detections.thumb``
DataChannel send path. The mobile-side encode + ship was costing
300–750 KB/s of uplink at a typical 5 Hz detector cadence with 2–3
active tracks — meaningful interference with the video bitrate on
cellular SAR flights. The desktop already has the source frame in
memory (it's literally rendering it), has spare CPU, and with the
publisher↔RTP offset calibration ``DetectionOverlayWidget`` already
maintains for the box overlay, it can pixel-lock the crop to the
exact frame the detector saw.

This module is a sibling of ``DetectionOverlayWidget`` — both
subscribe to the same ``DetectionFeedService`` meta events, both
reuse the overlay's frame ring + offset. The cropper emits
``thumbReady(track_key, jpeg_bytes)`` so multiple consumers (the
per-tile detection list, the Mission Gallery, future exporters)
can upsert their row image without coupling to each other.

See ``ADIAT_Mobile/core/.../BboxCropper.kt`` for the parameters
that match: 20% bbox padding, 96 px minimum edge, JPEG quality
85 (slightly higher than mobile's 80 — the desktop has the cycles).
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from PySide6.QtCore import QObject, Signal

from core.services.LoggerService import LoggerService
from core.views.flight.DetectionOverlayWidget import DetectionOverlayWidget


# Match ``BboxCropper`` on the mobile side so per-track thumbnails
# look the same regardless of whether they came from mobile or
# desktop. Numbers were chosen by the publisher team; treat them as
# the cross-platform spec rather than tunables.
PADDING_FRACTION = 0.20
MIN_PIXEL_EDGE = 96
JPEG_QUALITY = 85


class DetectionThumbCropper(QObject):
    """Crop per-detection thumbnails from the live video frame buffer."""

    thumbReady = Signal(str, bytes)  # (track_key, jpeg_bytes)

    def __init__(
        self,
        overlay: DetectionOverlayWidget,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.logger = LoggerService()
        # The overlay owns the frame ring + the publisher↔RTP offset
        # learned from §19.4 calibration. Sharing those keeps the
        # crop pixel-locked to the same source frame the box renders
        # on; an independent buffer would diverge on long sessions.
        self._overlay = overlay

    # ------------------------------------------------------------------
    # signal-slot entrypoint
    # ------------------------------------------------------------------

    def on_track_event(self, envelope: dict) -> None:
        """Crop a thumbnail for one promote/update event.

        Best-effort: if no matching frame is buffered (calibration
        hasn't seeded, or the meta references a frame older than the
        ring's depth), the crop is skipped silently. The next live
        Update on the same ``track_key`` will catch up.
        """
        if not isinstance(envelope, dict):
            return
        track_key = envelope.get("track_key")
        if not isinstance(track_key, str) or not track_key:
            return
        bbox = envelope.get("bbox_norm")
        if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
            return

        frame = self._lookup_frame(envelope)
        if frame is None:
            return

        try:
            cropped = self._crop_with_padding(frame, bbox)
        except Exception as exc:  # noqa: BLE001 - cropping must not crash UI
            self.logger.debug(
                f"DetectionThumbCropper: crop failed for {track_key}: {exc}"
            )
            return
        if cropped is None or cropped.size == 0:
            return

        jpeg = self._encode_jpeg(cropped)
        if jpeg is None:
            return
        self.thumbReady.emit(track_key, jpeg)

    # ------------------------------------------------------------------
    # frame lookup
    # ------------------------------------------------------------------

    def _lookup_frame(self, envelope: dict) -> Optional[np.ndarray]:
        """Pick the source frame for ``envelope``.

        Prefers the exact frame matched by ``frame_ts_ns`` via the
        overlay's publisher↔RTP offset; falls back to the most-recent
        buffered frame when the meta is legacy (``frame_ts_ns == 0``),
        the offset isn't seeded yet, or the matching frame has aged
        out of the ring (e.g., snapshot replay after reconnect).
        """
        try:
            frame_ts_ns = int(envelope.get("frame_ts_ns") or 0)
        except (TypeError, ValueError):
            frame_ts_ns = 0
        if frame_ts_ns > 0:
            matched = self._overlay.frame_at_publisher_ts(frame_ts_ns)
            if matched is not None:
                return matched
        return self._overlay.latest_frame()

    # ------------------------------------------------------------------
    # geometry + encode
    # ------------------------------------------------------------------

    @staticmethod
    def _crop_with_padding(
        frame: np.ndarray,
        bbox_norm,
    ) -> Optional[np.ndarray]:
        """Pad ``bbox_norm`` by ``PADDING_FRACTION``, clamp to frame, crop.

        Mirrors the mobile-side ``BboxCropper`` so per-track thumbnails
        match regardless of source side.
        """
        h, w = frame.shape[:2]
        try:
            x_norm, y_norm, bw_norm, bh_norm = (float(v) for v in bbox_norm)
        except (TypeError, ValueError):
            return None
        if bw_norm <= 0.0 or bh_norm <= 0.0:
            return None

        # Pad in *normalized* space; clamp to the frame after.
        pad_x = bw_norm * PADDING_FRACTION
        pad_y = bh_norm * PADDING_FRACTION
        x0_norm = max(0.0, x_norm - pad_x)
        y0_norm = max(0.0, y_norm - pad_y)
        x1_norm = min(1.0, x_norm + bw_norm + pad_x)
        y1_norm = min(1.0, y_norm + bh_norm + pad_y)

        x0 = int(round(x0_norm * w))
        y0 = int(round(y0_norm * h))
        x1 = int(round(x1_norm * w))
        y1 = int(round(y1_norm * h))

        # Enforce the cross-platform minimum edge length — boxes
        # smaller than this expand around their center so a tiny
        # bbox doesn't produce a 3 px thumbnail.
        if x1 - x0 < MIN_PIXEL_EDGE:
            cx = (x0 + x1) // 2
            x0 = max(0, cx - MIN_PIXEL_EDGE // 2)
            x1 = min(w, x0 + MIN_PIXEL_EDGE)
            x0 = max(0, x1 - MIN_PIXEL_EDGE)
        if y1 - y0 < MIN_PIXEL_EDGE:
            cy = (y0 + y1) // 2
            y0 = max(0, cy - MIN_PIXEL_EDGE // 2)
            y1 = min(h, y0 + MIN_PIXEL_EDGE)
            y0 = max(0, y1 - MIN_PIXEL_EDGE)

        if x1 <= x0 or y1 <= y0:
            return None
        return frame[y0:y1, x0:x1]

    @staticmethod
    def _encode_jpeg(frame: np.ndarray) -> Optional[bytes]:
        try:
            import cv2
        except ImportError:  # pragma: no cover - cv2 is a hard dep
            return None
        try:
            ok, buf = cv2.imencode(
                ".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
            )
        except Exception:  # noqa: BLE001
            return None
        if not ok:
            return None
        return bytes(buf)
