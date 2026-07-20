"""Unit tests for :class:`DetectionThumbCropper` (plan §19.4.1).

The cropper replaces the mobile-side JPEG path: it takes a meta
envelope (``bbox_norm`` + ``frame_ts_ns``), pulls the matching source
frame out of the overlay's ``recent_frames`` ring (or falls back to
the latest buffered frame), crops with the cross-platform padding
spec, and emits ``thumbReady(track_key, jpeg_bytes)``.

Tests exercise:

* Crop geometry — padding, clamping at the frame edge, minimum-edge
  enforcement.
* Frame lookup — exact match by ``frame_ts_ns`` vs. latest fallback
  vs. miss (no frame buffered yet).
* JPEG round-trip — emitted bytes decode back to a valid image.
* Signal — ``thumbReady`` fires with the correct ``track_key``.
"""

from __future__ import annotations

import os
import sys

import cv2
import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.controllers.flight.DetectionThumbCropper import (  # noqa: E402
    JPEG_QUALITY,
    MIN_PIXEL_EDGE,
    PADDING_FRACTION,
    DetectionThumbCropper,
)
from core.views.flight.DetectionOverlayWidget import DetectionOverlayWidget  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _frame(w: int = 1920, h: int = 1080) -> np.ndarray:
    """Build a synthetic BGR frame with predictable per-pixel content."""
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    # Each channel gets a horizontal gradient so the crop result
    # carries unambiguous "this pixel came from x,y" information.
    frame[:, :, 0] = np.tile(np.arange(w, dtype=np.uint16) % 255, (h, 1)).astype(np.uint8)
    frame[:, :, 1] = np.tile(np.arange(h, dtype=np.uint16) % 255, (w, 1)).T.astype(np.uint8)
    frame[:, :, 2] = 128
    return frame


def _meta(track_key: str = "t1", bbox=(0.40, 0.45, 0.10, 0.12), frame_ts_ns: int = 5_000_000_000) -> dict:
    return {
        "event": "promote",
        "track_key": track_key,
        "detector_id": "person",
        "class_name": "person",
        "confidence": 0.9,
        "bbox_norm": list(bbox),
        "captured_at_ms": 1_700_000_000_000,
        "frame_ts_ns": frame_ts_ns,
    }


def _make_pair():
    overlay = DetectionOverlayWidget()
    cropper = DetectionThumbCropper(overlay=overlay)
    return overlay, cropper


# ---------------------------------------------------------------------
# crop geometry
# ---------------------------------------------------------------------


def test_crop_with_padding_returns_padded_subrect() -> None:
    frame = _frame(1000, 1000)
    crop = DetectionThumbCropper._crop_with_padding(frame, (0.40, 0.45, 0.20, 0.10))
    # x range 0.40..0.60, pad 0.20 * 20% = 0.04 → 0.36..0.64 → 360..640
    # y range 0.45..0.55, pad 0.10 * 20% = 0.02 → 0.43..0.57 → 430..570
    assert crop.shape == (570 - 430, 640 - 360, 3)


def test_crop_with_padding_clamps_at_frame_edge() -> None:
    frame = _frame(1000, 1000)
    # Bbox at the top-left corner; padding can't go negative.
    crop = DetectionThumbCropper._crop_with_padding(frame, (0.0, 0.0, 0.10, 0.10))
    # x range 0..0.10, pad 0.02 → clamp to 0..0.12 → 0..120
    # y range 0..0.10, pad 0.02 → clamp to 0..0.12 → 0..120
    assert crop.shape == (120, 120, 3)


def test_crop_with_padding_enforces_min_pixel_edge() -> None:
    frame = _frame(1000, 1000)
    # A tiny 1% × 1% bbox would crop to ~12×12 px with padding;
    # MIN_PIXEL_EDGE expands it around the center to at least 96×96.
    crop = DetectionThumbCropper._crop_with_padding(frame, (0.5, 0.5, 0.01, 0.01))
    assert crop.shape[0] >= MIN_PIXEL_EDGE
    assert crop.shape[1] >= MIN_PIXEL_EDGE


def test_crop_with_padding_rejects_degenerate_bbox() -> None:
    frame = _frame(1000, 1000)
    assert DetectionThumbCropper._crop_with_padding(frame, (0.5, 0.5, 0.0, 0.0)) is None
    assert DetectionThumbCropper._crop_with_padding(frame, (0.5, 0.5, -0.1, 0.1)) is None


# ---------------------------------------------------------------------
# frame lookup
# ---------------------------------------------------------------------


def test_lookup_uses_publisher_ts_when_calibrated() -> None:
    """A meta with ``frame_ts_ns`` matches the frame buffered at the same
    publisher time (translated via the overlay's offset)."""
    overlay, cropper = _make_pair()
    overlay.resize(800, 450)
    # Buffer three frames: distinct ndarrays so we can identify which one
    # the lookup returned.
    f1, f2, f3 = _frame(640, 360), _frame(640, 360), _frame(640, 360)
    f1[0, 0] = (1, 1, 1)
    f2[0, 0] = (2, 2, 2)
    f3[0, 0] = (3, 3, 3)
    # Seed the offset with a single (meta, frame) pair: publisher t=5.0s,
    # RTP t=2.0s → offset = 3.0s.
    overlay.on_track_event(_meta(frame_ts_ns=5_000_000_000))
    overlay.on_video_frame(frame_time_s=2.0, src_w=640, src_h=360, frame_bgr=f1)
    assert overlay._publisher_offset_s == pytest.approx(3.0)
    # Buffer two more frames at later RTP times.
    overlay.on_video_frame(frame_time_s=2.1, src_w=640, src_h=360, frame_bgr=f2)
    overlay.on_video_frame(frame_time_s=2.2, src_w=640, src_h=360, frame_bgr=f3)

    # Meta whose source-frame ts maps to RTP t=2.1 (5.1e9 ns - 3.0s = 2.1).
    looked_up = cropper._lookup_frame(_meta(frame_ts_ns=5_100_000_000))
    assert looked_up is not None
    assert looked_up[0, 0, 0] == 2


def test_lookup_falls_back_to_latest_when_uncalibrated() -> None:
    overlay, cropper = _make_pair()
    overlay.resize(800, 450)
    f1 = _frame(320, 180)
    f1[0, 0] = (7, 7, 7)
    overlay.on_video_frame(frame_time_s=0.1, src_w=320, src_h=180, frame_bgr=f1)
    # No calibration yet (no meta), but the cropper still gets a frame.
    looked_up = cropper._lookup_frame(_meta(frame_ts_ns=999_999_999))
    assert looked_up is not None
    assert looked_up[0, 0, 0] == 7


def test_lookup_returns_none_when_no_frames_buffered() -> None:
    overlay, cropper = _make_pair()
    assert cropper._lookup_frame(_meta()) is None


def test_lookup_falls_back_to_latest_when_meta_frame_too_old() -> None:
    """Snapshot replay carries a ``frame_ts_ns`` older than the
    ring's depth — the offset is calibrated but the matching frame
    has aged out. Falls back to the latest buffered frame rather
    than returning ``None``."""
    overlay, cropper = _make_pair()
    overlay.resize(800, 450)
    f1 = _frame(320, 180)
    f1[0, 0] = (11, 11, 11)
    overlay.on_track_event(_meta(frame_ts_ns=10_000_000_000))
    overlay.on_video_frame(frame_time_s=5.0, src_w=320, src_h=180, frame_bgr=f1)
    # Push 30 more frames so the original "matched" frame is evicted.
    for i in range(30):
        f = _frame(320, 180)
        f[0, 0] = (100 + i, 100 + i, 100 + i)
        overlay.on_video_frame(frame_time_s=5.0 + 0.1 * (i + 1), src_w=320, src_h=180, frame_bgr=f)
    # Old meta with ``frame_ts_ns`` pointing at the original frame —
    # offset-based lookup misses, falls back to the newest buffered.
    looked_up = cropper._lookup_frame(_meta(frame_ts_ns=10_000_000_000))
    assert looked_up is not None
    # Should be the latest frame (i=29 → value 129).
    assert looked_up[0, 0, 0] == 129


# ---------------------------------------------------------------------
# end-to-end signal flow
# ---------------------------------------------------------------------


def test_on_track_event_emits_thumb_ready_with_valid_jpeg() -> None:
    overlay, cropper = _make_pair()
    overlay.resize(800, 450)
    frame = _frame(640, 360)
    overlay.on_video_frame(frame_time_s=0.5, src_w=640, src_h=360, frame_bgr=frame)

    received: list = []
    cropper.thumbReady.connect(lambda key, jpeg: received.append((key, jpeg)))

    cropper.on_track_event(_meta(track_key="abc", frame_ts_ns=0))
    assert len(received) == 1
    track_key, jpeg_bytes = received[0]
    assert track_key == "abc"
    assert isinstance(jpeg_bytes, bytes)
    # Round-trip: the emitted bytes must decode as a valid image.
    arr = np.frombuffer(jpeg_bytes, dtype=np.uint8)
    decoded = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    assert decoded is not None
    # And the decoded image's dims should match the padded crop.
    # bbox (0.40, 0.45, 0.10, 0.12) on a 640×360 frame with 20% padding:
    #   x: 0.40..0.50 → pad ±0.02 → 0.38..0.52 → 243..333 = 90 px
    #   y: 0.45..0.57 → pad ±0.024 → 0.426..0.594 → 153..214 = 61 px
    # Min-edge bumps both to ≥ 96 px.
    assert decoded.shape[0] >= MIN_PIXEL_EDGE
    assert decoded.shape[1] >= MIN_PIXEL_EDGE


def test_on_track_event_no_frame_does_not_emit() -> None:
    """Cropper skips silently when no frame is buffered yet."""
    overlay, cropper = _make_pair()
    received: list = []
    cropper.thumbReady.connect(lambda key, jpeg: received.append((key, jpeg)))
    cropper.on_track_event(_meta(track_key="never"))
    assert received == []


def test_on_track_event_malformed_envelopes_ignored() -> None:
    overlay, cropper = _make_pair()
    overlay.on_video_frame(frame_time_s=0.0, src_w=320, src_h=180, frame_bgr=_frame(320, 180))
    received: list = []
    cropper.thumbReady.connect(lambda key, jpeg: received.append((key, jpeg)))

    cropper.on_track_event("not-a-dict")                  # type: ignore[arg-type]
    cropper.on_track_event({"track_key": ""})              # empty
    cropper.on_track_event({"track_key": "x"})             # no bbox
    cropper.on_track_event({"track_key": "x", "bbox_norm": [0.1]})  # wrong shape
    cropper.on_track_event({"track_key": "x", "bbox_norm": [0.1, 0.1, 0, 0]})  # zero bbox
    assert received == []


def test_spec_constants_match_mobile_bbox_cropper() -> None:
    """Sanity-pin the cross-platform crop spec so future tweaks raise
    an alarm — the mobile gallery still produces thumbs locally using
    the same parameters; divergence would mean two visually-different
    thumbnails for the same track."""
    assert PADDING_FRACTION == pytest.approx(0.20)
    assert MIN_PIXEL_EDGE == 96
    assert JPEG_QUALITY == 85
