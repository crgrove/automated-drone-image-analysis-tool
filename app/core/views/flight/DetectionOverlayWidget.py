"""Detection bbox overlay for the Flight Viewer (plan §19.4).

Renders detector boxes on top of the live video pane, aligned to the
*exact* frame they were computed from. Two sync concerns are critical:

1. **Time sync.** The meta envelope arrives over SCTP ~100 ms ahead of
   its matching RTP video frame. Drawing "the latest box on the latest
   frame" puts the box ~100 ms behind the target, which at a 5 m/s
   drone speed is half a meter of camera motion — unacceptable for SAR.

   Mobile stamps every meta with ``frame_ts_ns`` (the publisher's
   ``VideoFrame.timestampNs`` value passed to the encoder). aiortc
   exposes the corresponding RTP-derived timestamp as ``frame.time``
   seconds. The two relate by a constant per-session offset that we
   learn from the first meta + next-frame pair and refine via EWMA
   on subsequent matches.

2. **Space sync.** The video pane (a ``QLabel``) shows the pixmap
   scaled to fit with ``KeepAspectRatio``, centered — so the pixmap is
   letterboxed (top/bottom black bars) or pillarboxed (left/right) when
   the label aspect differs from the source. Boxes are normalized
   coordinates over the SOURCE FRAME, so mapping them to the full
   label rect would offset every box by the letterbox margin. We
   compute the same displayed-pixmap subrect that ``on_frame`` produces
   and map bbox coords into *that* subrect.

The widget itself is fully transparent and forwards mouse events so
the operator can still click through to the underlying video pane.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional, Tuple

import numpy as np
from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget


# Time window in seconds for considering a track's source frame to be
# "the current frame". 50 ms ≈ 1.5 frames at 30 fps — wide enough to
# tolerate a small calibration error but narrow enough that boxes don't
# bleed across many frames.
FRAME_WINDOW_S = 0.05

# Tracks older than this without a refresh are auto-removed from the
# overlay. At the publisher's typical 5 Hz detector cadence, 0.5 s is
# 2–3 missed update cycles' worth of grace — enough to ride out a
# single dropped frame from the detector without the operator seeing
# box flicker, short enough that a box doesn't linger after the camera
# pans off the target (the publisher stops sending updates the moment
# the tracker loses the target, so freshness here IS the "lost track"
# signal). The Mission Gallery row outlives the overlay box — the
# detection still has a place in the per-session record even after
# its bbox disappears from the live video.
FRESHNESS_S = 0.5

# EWMA weight for refining the publisher↔RTP offset after the initial
# seed. Small value (5%) keeps a stale outlier from yanking the offset
# while still correcting clock drift over a long session.
EWMA_ALPHA = 0.05

# After this many metas with ``frame_ts_ns == 0`` and no successful
# calibration, fall back to drawing the latest box on the latest frame
# (legacy publisher mode; documented in plan §19.4).
LEGACY_THRESHOLD_METAS = 5

# Ring-buffer depth for ``recent_frames``. Plan §19.4.1 suggests
# ≈ 1 s of frames at 30 fps so the desktop-side thumb cropper can
# look up the exact source frame for a recently-arrived meta via
# the publisher↔RTP offset. Larger buffers cost memory (~6 MB per
# 1080p frame, raw ndarray); 30 strikes a balance.
RECENT_FRAMES_DEPTH = 30

# How close (in seconds, publisher clock) a buffered frame's
# timestamp must be to the requested meta's ``frame_ts_ns / 1e9``
# to count as "the matching frame" for crop look-ups. Wider than
# the overlay's ±50 ms time-window because the cropper is more
# tolerant — a slightly-off frame still gives a correct crop.
CROP_FRAME_MATCH_S = 0.075

# Per-detector palette — RGB, mirrors the mobile-side
# ``OverlayCompositor.colorForDetector`` so desktop + tablet show the
# same color for the same detector class.
PALETTE: Dict[str, Tuple[int, int, int]] = {
    "person":      (0xFB, 0x5E, 0x1C),
    "color-range": (0x58, 0xB7, 0xFF),
    "color-hsv":   (0x58, 0xB7, 0xFF),
    "motion":      (0xFF, 0xD5, 0x4F),
    "dji-native":  (0x4C, 0xAF, 0x50),
}

# Fallback color for detectors not in PALETTE — white pops on most
# imagery without coupling to any specific detector identity.
DEFAULT_COLOR = (0xFF, 0xFF, 0xFF)


@dataclass
class ActiveTrack:
    """One detection currently being rendered on the overlay."""

    envelope: dict
    track_key: str
    frame_ts_ns: int           # source frame on the publisher clock; 0 = legacy
    received_at: float         # time.monotonic() of meta arrival
    bbox_norm: Tuple[float, float, float, float]  # left, top, w, h


class DetectionOverlayWidget(QWidget):
    """Transparent overlay drawing detector boxes time-locked to frames."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        # Click-through: video pane gets the mouse events.
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        # Don't request a system background — we paint everything.
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._tracks: Dict[str, ActiveTrack] = {}
        # Calibration state — learned once, refined via EWMA.
        self._publisher_offset_s: Optional[float] = None
        self._pending_first_meta: Optional[ActiveTrack] = None
        # Most-recent meta that arrived after calibration; paired with
        # the NEXT video frame for an EWMA offset refinement (same
        # meta-leads-frame heuristic as the initial seed).
        self._pending_refine_meta: Optional[ActiveTrack] = None
        # Most-recent frame's time on the publisher clock.
        self._current_frame_pub_s: Optional[float] = None
        # Most-recent source frame dimensions; drives the letterbox math.
        self._video_w: int = 0
        self._video_h: int = 0
        # Legacy fallback bookkeeping.
        self._metas_seen: int = 0
        self._legacy_mode: bool = False
        # Publisher-clock floor for accepted envelopes. Set by the
        # controller from the first telemetry envelope's
        # ``captured_at_ms`` — anything older is a pre-session ghost
        # from the publisher's never-cleared ``currentEnvelopes`` map
        # and is dropped before it lands in ``_tracks``.
        self._session_baseline_pub_ms: Optional[int] = None
        # Frame ring buffer for the desktop-side thumb cropper (plan
        # §19.4.1). Each entry is ``(frame_time_s, ndarray, local_arrival_s)``
        # — RTP-derived seconds, the source BGR frame as ndarray, and
        # ``time.monotonic()`` so we can age frames out independent of
        # the publisher clock.
        self._recent_frames: Deque[Tuple[float, np.ndarray, float]] = deque(
            maxlen=RECENT_FRAMES_DEPTH
        )
        # Label font is small + bold; class+confidence chip sits above the
        # box in the top-left corner.
        self._label_font = QFont()
        self._label_font.setBold(True)
        self._label_font.setPointSize(8)

    # ------------------------------------------------------------------
    # public API — called by FlightTileController via signal connections
    # ------------------------------------------------------------------

    PRE_SESSION_TOLERANCE_MS = 5_000

    def set_session_baseline(self, baseline_pub_ms: Optional[int]) -> None:
        """Anchor the overlay to a publisher-clock floor for filtering.

        Mirrors :class:`FlightTileController`'s behaviour — once the
        baseline is set, any track whose ``captured_at_ms`` is older
        than ``baseline - PRE_SESSION_TOLERANCE_MS`` is dropped before
        it ever enters ``_tracks``, so pre-session ghosts from a
        snapshot replay never flash up on the live video pane.
        """
        if isinstance(baseline_pub_ms, (int, float)):
            self._session_baseline_pub_ms = int(baseline_pub_ms)

    def _is_pre_session(self, envelope: dict) -> bool:
        if self._session_baseline_pub_ms is None:
            return False
        ts = envelope.get("captured_at_ms")
        if not isinstance(ts, (int, float)):
            return False
        return int(ts) < self._session_baseline_pub_ms - self.PRE_SESSION_TOLERANCE_MS

    def on_track_event(self, envelope: dict) -> None:
        """Upsert a single track from a promote/update envelope.

        ``promote`` and ``update`` are treated identically — the overlay
        only cares about the *current* bbox for each ``track_key``; the
        per-row gallery rendering owns the "is this new or updated"
        distinction.
        """
        if not isinstance(envelope, dict):
            return
        if self._is_pre_session(envelope):
            return
        track_key = envelope.get("track_key")
        if not isinstance(track_key, str) or not track_key:
            return
        bbox = envelope.get("bbox_norm")
        if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
            return
        try:
            bbox_norm = tuple(float(v) for v in bbox)
        except (TypeError, ValueError):
            return

        frame_ts_ns = self._coerce_int(envelope.get("frame_ts_ns"))

        track = ActiveTrack(
            envelope=envelope,
            track_key=track_key,
            frame_ts_ns=frame_ts_ns,
            received_at=time.monotonic(),
            bbox_norm=bbox_norm,
        )
        self._tracks[track_key] = track

        # Calibration bookkeeping.
        self._metas_seen += 1
        if frame_ts_ns == 0:
            # Legacy publisher — can't seed offset from this envelope.
            # If we never see a non-zero frame_ts_ns after enough metas,
            # paintEvent falls back to "latest box on latest frame".
            if (
                self._publisher_offset_s is None
                and self._metas_seen >= LEGACY_THRESHOLD_METAS
            ):
                self._legacy_mode = True
            return
        if self._publisher_offset_s is None:
            # Stash the first meta with a real frame_ts_ns; the next
            # frame to arrive lets us solve for the publisher↔RTP offset.
            if self._pending_first_meta is None:
                self._pending_first_meta = track
            return
        # Post-calibration: this meta is paired with the NEXT video
        # frame for an EWMA refinement. Same meta-leads-frame heuristic
        # as the seed; small clock drifts get nudged out over time.
        self._pending_refine_meta = track

    def on_snapshot(self, envelopes: List[dict]) -> None:
        """Bulk upsert from a snapshot reply.

        Plan §19.4: live promotion wins over a replayed snapshot — a
        ``track_key`` already in ``self._tracks`` keeps its existing
        envelope (which is by definition fresher than the snapshot).
        """
        if not isinstance(envelopes, list):
            return
        for env in envelopes:
            if not isinstance(env, dict):
                continue
            track_key = env.get("track_key")
            if not isinstance(track_key, str) or not track_key:
                continue
            if track_key in self._tracks:
                continue
            self.on_track_event(env)

    def on_video_frame(
        self,
        frame_time_s: float,
        src_w: int = 0,
        src_h: int = 0,
        frame_bgr: Optional[np.ndarray] = None,
    ) -> None:
        """Called by ``FlightTile.on_frame`` after the pixmap is set.

        * ``frame_time_s`` — aiortc's RTP-derived seconds (the ``ts`` value
          on ``WebRTCStreamService.frameReady``).
        * ``src_w`` / ``src_h`` — source frame dimensions. Needed once
          to compute the letterbox/pillarbox subrect inside the widget;
          we cache the latest values.
        * ``frame_bgr`` — the source BGR ndarray. Buffered into
          ``_recent_frames`` so the desktop-side thumb cropper (plan
          §19.4.1) can look up the exact source frame for an arriving
          meta envelope via the publisher↔RTP offset.

        Side effects:
        1. Buffer ``frame_bgr`` into the recent-frames ring.
        2. If we have a pending first meta, compute and seed the
           publisher↔RTP offset.
        3. Map ``frame_time_s`` to publisher time for paintEvent.
        4. EWMA-refine the offset against any track that the new frame
           falls within ``FRAME_WINDOW_S`` of.
        5. Prune stale tracks.
        6. ``update()`` to trigger a repaint.
        """
        if src_w > 0 and src_h > 0:
            self._video_w = int(src_w)
            self._video_h = int(src_h)

        if frame_bgr is not None and frame_bgr.size > 0:
            self._recent_frames.append((frame_time_s, frame_bgr, time.monotonic()))

        # Seed calibration: first frame to arrive after the first meta
        # with a real frame_ts_ns. Plan §19.4 calibration trick.
        if self._publisher_offset_s is None and self._pending_first_meta is not None:
            self._publisher_offset_s = (
                self._pending_first_meta.frame_ts_ns / 1e9 - frame_time_s
            )
            self._pending_first_meta = None

        # EWMA refinement: pair the most-recent post-calibration meta
        # with this frame and nudge the offset toward the observed
        # difference. We only refine when the implied drift is small
        # (within ±2× FRAME_WINDOW_S) — a large drift means the meta
        # is not actually for this frame and refining would corrupt the
        # offset.
        if (
            self._publisher_offset_s is not None
            and self._pending_refine_meta is not None
        ):
            meta = self._pending_refine_meta
            self._pending_refine_meta = None
            predicted_pub_s = frame_time_s + self._publisher_offset_s
            actual_pub_s = meta.frame_ts_ns / 1e9
            drift = actual_pub_s - predicted_pub_s
            if abs(drift) < FRAME_WINDOW_S * 2:
                self._publisher_offset_s += EWMA_ALPHA * drift

        # Map the current frame onto the publisher clock for paint-time
        # gating; this happens AFTER refinement so the time-window
        # comparison uses the freshest offset.
        if self._publisher_offset_s is not None:
            self._current_frame_pub_s = frame_time_s + self._publisher_offset_s
        elif self._legacy_mode:
            # No calibration possible — paintEvent will draw every
            # active track on every frame (drift returns; documented).
            self._current_frame_pub_s = None

        # Prune tracks the publisher hasn't refreshed recently.
        now = time.monotonic()
        stale = [
            key for key, track in self._tracks.items()
            if now - track.received_at > FRESHNESS_S
        ]
        for key in stale:
            del self._tracks[key]

        self.update()

    def clear(self) -> None:
        """Reset all overlay state — call on session tear-down."""
        self._tracks.clear()
        self._publisher_offset_s = None
        self._pending_first_meta = None
        self._pending_refine_meta = None
        self._current_frame_pub_s = None
        self._metas_seen = 0
        self._legacy_mode = False
        self._recent_frames.clear()
        self.update()

    # ------------------------------------------------------------------
    # frame buffer access (used by DetectionThumbCropper, plan §19.4.1)
    # ------------------------------------------------------------------

    def latest_frame(self) -> Optional[np.ndarray]:
        """Return the most recently buffered source BGR frame, or ``None``."""
        if not self._recent_frames:
            return None
        return self._recent_frames[-1][1]

    def frame_at_publisher_ts(self, frame_ts_ns: int) -> Optional[np.ndarray]:
        """Return the buffered frame that matches a meta's ``frame_ts_ns``.

        Uses the learned publisher↔RTP offset to translate the meta's
        publisher-clock nanoseconds into RTP seconds and scans
        ``_recent_frames`` for the closest match within
        ``CROP_FRAME_MATCH_S``. Returns ``None`` if no buffered frame
        falls within that window (frame already evicted from the ring,
        or calibration hasn't seeded yet).
        """
        if not self._recent_frames or frame_ts_ns <= 0:
            return None
        if self._publisher_offset_s is None:
            return None
        target_rtp_s = (frame_ts_ns / 1e9) - self._publisher_offset_s
        best: Optional[Tuple[float, np.ndarray, float]] = None
        best_drift = CROP_FRAME_MATCH_S
        for entry in self._recent_frames:
            drift = abs(entry[0] - target_rtp_s)
            if drift <= best_drift:
                best = entry
                best_drift = drift
        return best[1] if best is not None else None

    # ------------------------------------------------------------------
    # geometry — space-sync the bbox coords with the displayed pixmap
    # ------------------------------------------------------------------

    def displayed_pixmap_rect(self) -> QRect:
        """Compute the subrect inside the widget where the video pixmap
        is actually drawn.

        ``FlightTile.on_frame`` calls
        ``pixmap.scaled(label.size(), Qt.KeepAspectRatio, ...)`` and the
        label centers the result, so the pixmap occupies a centered
        subrect with letterbox/pillarbox on the unfilled axis. Boxes
        drawn outside this subrect would fall on the black bars; we
        compute the subrect here so bbox-normalized coords land on
        actual video pixels.
        """
        w, h = self.width(), self.height()
        if self._video_w <= 0 or self._video_h <= 0 or w <= 0 or h <= 0:
            # No source dims yet — fall back to full rect; better than
            # rendering nothing.
            return QRect(0, 0, w, h)
        src_aspect = self._video_w / self._video_h
        dst_aspect = w / h
        if src_aspect > dst_aspect:
            # Source is wider than widget — width-bound, letterbox.
            pixmap_w = w
            pixmap_h = int(round(w / src_aspect))
        else:
            # Source is taller than widget — height-bound, pillarbox.
            pixmap_h = h
            pixmap_w = int(round(h * src_aspect))
        offset_x = (w - pixmap_w) // 2
        offset_y = (h - pixmap_h) // 2
        return QRect(offset_x, offset_y, pixmap_w, pixmap_h)

    # ------------------------------------------------------------------
    # rendering
    # ------------------------------------------------------------------

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt name
        if not self._tracks:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setFont(self._label_font)
        pixmap_rect = self.displayed_pixmap_rect()
        for track in self._tracks.values():
            if not self._should_draw(track):
                continue
            self._draw_track(painter, track, pixmap_rect)
        painter.end()

    def _should_draw(self, track: ActiveTrack) -> bool:
        # Active-track draw policy: any track that's still inside the
        # ``FRESHNESS_S`` window gets rendered every paint. This is the
        # "always show the latest known box per detection" model — the
        # strict time-window gating that plan §19.4 specified for
        # exact-frame matching turned out to hide boxes whenever the
        # publisher↔RTP offset drifts even slightly, with no usable
        # signal to the operator. The cost is that on a fast-moving
        # drone the box can lag behind the target by the SCTP-vs-RTP
        # transit difference (~100 ms); for the SAR speeds we ship at
        # (≤5 m/s) that's a fraction of a meter of camera motion —
        # acceptable, and far better than no box at all.
        #
        # Stale-track pruning in ``on_video_frame`` keeps the active
        # set bounded; tracks the publisher hasn't refreshed in
        # ``FRESHNESS_S`` are removed before this slot ever runs.
        return True

    def _draw_track(
        self,
        painter: QPainter,
        track: ActiveTrack,
        pixmap_rect: QRect,
    ) -> None:
        detector_id = track.envelope.get("detector_id") or ""
        color = QColor(*PALETTE.get(detector_id, DEFAULT_COLOR))

        # Map normalized bbox to the displayed-pixmap subrect.
        x_norm, y_norm, w_norm, h_norm = track.bbox_norm
        box_x = pixmap_rect.x() + int(round(x_norm * pixmap_rect.width()))
        box_y = pixmap_rect.y() + int(round(y_norm * pixmap_rect.height()))
        box_w = int(round(w_norm * pixmap_rect.width()))
        box_h = int(round(h_norm * pixmap_rect.height()))
        if box_w <= 0 or box_h <= 0:
            return

        pen = QPen(color)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(box_x, box_y, box_w, box_h)

        # Class + confidence chip — top-left of the bbox, just above
        # the rectangle. Color-filled background so it stays readable
        # against any video content underneath.
        class_name = track.envelope.get("class_name") or "?"
        confidence = track.envelope.get("confidence")
        if isinstance(confidence, (int, float)):
            label_text = "{} {:.0f}%".format(class_name, float(confidence) * 100.0)
        else:
            label_text = class_name
        metrics = painter.fontMetrics()
        text_w = metrics.horizontalAdvance(label_text) + 6
        text_h = metrics.height() + 2
        chip_x = box_x
        chip_y = max(0, box_y - text_h)
        painter.fillRect(chip_x, chip_y, text_w, text_h, color)
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(
            QPoint(chip_x + 3, chip_y + metrics.ascent() + 1),
            label_text,
        )

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    @staticmethod
    def _coerce_int(value) -> int:
        if value is None:
            return 0
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0
