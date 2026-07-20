"""Unit tests for :class:`DetectionOverlayWidget` (plan §19.4).

The overlay has two sync responsibilities:

1. **Time sync** — calibrate the publisher↔RTP clock offset from the
   first meta + next-frame pair, then refine via EWMA. Boxes only draw
   on the frame they were computed from (±``FRAME_WINDOW_S``).
2. **Space sync** — bbox-normalized coords must map to the letterboxed
   pixmap subrect inside the widget, NOT the full widget rect.

These tests exercise both without rendering pixels: the overlay's
internal state (`_publisher_offset_s`, `_current_frame_pub_s`,
`_tracks`, `_legacy_mode`) and the public `displayed_pixmap_rect()`
geometry helper are both observable and deterministic.
"""

from __future__ import annotations

import os
import sys
import time

import pytest
from PySide6.QtCore import QRect
from PySide6.QtWidgets import QApplication, QWidget

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from core.views.flight.DetectionOverlayWidget import (  # noqa: E402
    EWMA_ALPHA,
    FRAME_WINDOW_S,
    FRESHNESS_S,
    LEGACY_THRESHOLD_METAS,
    DetectionOverlayWidget,
)


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _meta(
    track_key: str,
    *,
    bbox=(0.1, 0.2, 0.3, 0.4),
    frame_ts_ns: int = 5_000_000_000,
    detector_id: str = "person",
    class_name: str = "person",
    confidence: float = 0.87,
    extra: dict | None = None,
) -> dict:
    env = {
        "event": "promote",
        "track_key": track_key,
        "detector_id": detector_id,
        "class_name": class_name,
        "confidence": confidence,
        "bbox_norm": list(bbox),
        "captured_at_ms": 1_700_000_000_000,
        "frame_ts_ns": frame_ts_ns,
    }
    if extra:
        env.update(extra)
    return env


# ---------------------------------------------------------------------
# calibration (plan §19.4 — "learning the publisher↔RTP offset")
# ---------------------------------------------------------------------


def test_first_meta_then_first_frame_seeds_offset() -> None:
    w = DetectionOverlayWidget()
    w.resize(800, 450)
    # Frame ts of 2.5s (RTP-derived); meta carries 5s on publisher clock.
    w.on_track_event(_meta("p|s|1", frame_ts_ns=5_000_000_000))
    assert w._publisher_offset_s is None
    assert w._pending_first_meta is not None

    w.on_video_frame(frame_time_s=2.5, src_w=1920, src_h=1080)
    # offset_s = (5_000_000_000 / 1e9) - 2.5 == 2.5
    assert w._publisher_offset_s == pytest.approx(2.5)
    assert w._pending_first_meta is None


def test_active_track_always_drawn_after_calibration() -> None:
    """The draw policy now renders every active (non-stale) track on
    every frame; strict frame-window gating was dropped because tiny
    calibration drifts were hiding boxes entirely (plan §19.4 trade-off
    note in ``DetectionOverlayWidget._should_draw``).
    """
    w = DetectionOverlayWidget()
    w.resize(800, 450)
    w.on_track_event(_meta("p|s|1", frame_ts_ns=5_000_000_000))
    w.on_video_frame(frame_time_s=2.5, src_w=1920, src_h=1080)
    assert w._publisher_offset_s == pytest.approx(2.5)

    only_track = next(iter(w._tracks.values()))
    # Far away from "the current frame" by publisher timeline math.
    w.on_video_frame(frame_time_s=10.0, src_w=1920, src_h=1080)
    assert w._should_draw(only_track)
    # Right on the matching frame.
    w.on_video_frame(frame_time_s=2.5, src_w=1920, src_h=1080)
    assert w._should_draw(only_track)


def test_ewma_refines_offset_toward_drift() -> None:
    w = DetectionOverlayWidget()
    w.resize(800, 450)
    # Seed offset = 0.5s
    w.on_track_event(_meta("p|s|1", frame_ts_ns=1_500_000_000))
    w.on_video_frame(frame_time_s=1.0, src_w=1920, src_h=1080)
    seeded = w._publisher_offset_s
    assert seeded == pytest.approx(0.5)

    # Simulate publisher clock drifting by 30ms forward — a new track at
    # the same RTP frame time would now correspond to a slightly later
    # publisher time. Each (meta, frame) pair refines the offset by
    # EWMA_ALPHA × drift; repeated pairs drag the offset toward the new
    # steady-state value (0.53s).
    drifted = 1_530_000_000   # publisher t for the drifted track
    for _ in range(40):
        w.on_track_event(_meta("p|s|2", frame_ts_ns=drifted))
        w.on_video_frame(frame_time_s=1.0, src_w=1920, src_h=1080)
    # EWMA at alpha=0.05 converges towards (drifted - 1.0e9) / 1e9 = 0.53
    # after enough iterations.
    assert w._publisher_offset_s == pytest.approx(0.53, abs=0.01)
    # And it definitely moved from the original 0.5 seed.
    assert w._publisher_offset_s > seeded


def test_active_track_drawn_even_before_calibration() -> None:
    """Always-draw policy renders any track as soon as it lands —
    pre-calibration boxes are slightly time-mismatched but still
    actionable for the operator."""
    w = DetectionOverlayWidget()
    w.resize(800, 450)
    w.on_track_event(_meta("p|s|1"))
    only_track = next(iter(w._tracks.values()))
    assert w._publisher_offset_s is None
    assert w._should_draw(only_track)


# ---------------------------------------------------------------------
# legacy fallback (`frame_ts_ns == 0` from pre-this-PR publishers)
# ---------------------------------------------------------------------


def test_legacy_mode_engages_after_threshold_zero_metas() -> None:
    w = DetectionOverlayWidget()
    w.resize(800, 450)
    for i in range(LEGACY_THRESHOLD_METAS):
        w.on_track_event(_meta(f"p|s|{i}", frame_ts_ns=0))
    assert w._legacy_mode is True

    # Legacy mode draws every active track on every frame even before
    # any video frame has come through (no calibration needed).
    only_track = next(iter(w._tracks.values()))
    assert w._should_draw(only_track)


def test_real_meta_after_zero_metas_still_calibrates() -> None:
    """If a non-zero meta arrives even after some zero-metas, calibrate."""
    w = DetectionOverlayWidget()
    w.resize(800, 450)
    for i in range(LEGACY_THRESHOLD_METAS - 1):
        w.on_track_event(_meta(f"p|s|{i}", frame_ts_ns=0))
    assert w._legacy_mode is False  # still below threshold
    w.on_track_event(_meta("p|s|new", frame_ts_ns=4_000_000_000))
    w.on_video_frame(frame_time_s=2.0, src_w=1920, src_h=1080)
    assert w._publisher_offset_s == pytest.approx(2.0)
    assert w._legacy_mode is False  # calibration succeeded, no fallback


# ---------------------------------------------------------------------
# space sync — letterbox math (the critical "boxes-over-actual-pixels"
# fix; otherwise pillarbox offsets every box by the black-bar width)
# ---------------------------------------------------------------------


def test_pixmap_rect_pillarbox_for_4_3_source_in_16_9_widget() -> None:
    """4:3 source in 16:9 widget → height-bound, pillarbox left/right."""
    w = DetectionOverlayWidget()
    w.resize(1600, 900)  # 16:9
    # Mimic on_video_frame side-effect: store source dims.
    w._video_w = 640
    w._video_h = 480  # 4:3
    rect = w.displayed_pixmap_rect()
    # Height-bound: pixmap_h = 900, pixmap_w = 900 * (640/480) = 1200.
    # Centered horizontally: offset_x = (1600 - 1200) / 2 = 200.
    assert rect == QRect(200, 0, 1200, 900)


def test_pixmap_rect_letterbox_for_16_9_source_in_4_3_widget() -> None:
    w = DetectionOverlayWidget()
    w.resize(800, 600)  # 4:3
    w._video_w = 1920
    w._video_h = 1080  # 16:9
    rect = w.displayed_pixmap_rect()
    # Width-bound: pixmap_w = 800, pixmap_h = 800 * (1080/1920) = 450.
    # Centered vertically: offset_y = (600 - 450) / 2 = 75.
    assert rect == QRect(0, 75, 800, 450)


def test_pixmap_rect_exact_match_no_letterbox() -> None:
    w = DetectionOverlayWidget()
    w.resize(1600, 900)
    w._video_w = 1920
    w._video_h = 1080  # both 16:9
    rect = w.displayed_pixmap_rect()
    assert rect == QRect(0, 0, 1600, 900)


def test_pixmap_rect_falls_back_to_widget_rect_without_video_dims() -> None:
    w = DetectionOverlayWidget()
    w.resize(640, 360)
    # No on_video_frame() has set _video_w / _video_h.
    rect = w.displayed_pixmap_rect()
    assert rect == QRect(0, 0, 640, 360)


# ---------------------------------------------------------------------
# track lifecycle: upsert, snapshot dedupe, freshness prune
# ---------------------------------------------------------------------


def test_promote_then_update_keeps_one_track_per_key() -> None:
    w = DetectionOverlayWidget()
    w.on_track_event(_meta("p|s|1", bbox=(0.1, 0.1, 0.1, 0.1)))
    w.on_track_event(_meta("p|s|1", bbox=(0.4, 0.4, 0.2, 0.2)))
    assert len(w._tracks) == 1
    assert w._tracks["p|s|1"].bbox_norm == (0.4, 0.4, 0.2, 0.2)


def test_snapshot_skips_already_known_track_keys() -> None:
    """Plan §19.4: live promote wins over a replayed snapshot."""
    w = DetectionOverlayWidget()
    w.on_track_event(_meta("p|s|1", bbox=(0.1, 0.1, 0.1, 0.1)))
    w.on_snapshot([
        _meta("p|s|1", bbox=(0.99, 0.99, 0.01, 0.01)),  # should be ignored
        _meta("p|s|2", bbox=(0.5, 0.5, 0.1, 0.1)),       # should be added
    ])
    assert w._tracks["p|s|1"].bbox_norm == (0.1, 0.1, 0.1, 0.1)  # untouched
    assert "p|s|2" in w._tracks


def test_stale_tracks_are_pruned_on_next_frame() -> None:
    w = DetectionOverlayWidget()
    w.resize(800, 450)
    w.on_track_event(_meta("p|s|1"))
    # Backdate the track to look stale.
    w._tracks["p|s|1"].received_at = time.monotonic() - (FRESHNESS_S + 1)
    w.on_video_frame(frame_time_s=1.0, src_w=1920, src_h=1080)
    assert "p|s|1" not in w._tracks


def test_clear_resets_all_state() -> None:
    w = DetectionOverlayWidget()
    w.resize(800, 450)
    w.on_track_event(_meta("p|s|1"))
    w.on_video_frame(frame_time_s=1.0, src_w=1920, src_h=1080)
    assert w._tracks and w._publisher_offset_s is not None
    w.clear()
    assert w._tracks == {}
    assert w._publisher_offset_s is None
    assert w._pending_first_meta is None
    assert w._current_frame_pub_s is None
    assert w._metas_seen == 0
    assert w._legacy_mode is False


# ---------------------------------------------------------------------
# input validation
# ---------------------------------------------------------------------


def test_malformed_envelopes_ignored() -> None:
    w = DetectionOverlayWidget()
    w.on_track_event("not-a-dict")               # type: ignore[arg-type]
    w.on_track_event({"track_key": ""})           # empty key
    w.on_track_event({"track_key": "x"})          # no bbox
    w.on_track_event({"track_key": "x", "bbox_norm": [1, 2, 3]})    # wrong length
    w.on_track_event({"track_key": "x", "bbox_norm": ["a", "b", "c", "d"]})
    w.on_snapshot("not-a-list")                   # type: ignore[arg-type]
    assert w._tracks == {}


def test_ewma_alpha_is_small_and_within_range() -> None:
    # Sanity guardrails on the tuned constants; a surprise here would
    # mean someone tweaked the convergence rate / window without
    # noting it in the corresponding doc comment.
    assert 0 < EWMA_ALPHA <= 0.2
    assert 0 < FRAME_WINDOW_S <= 0.2
    # ``FRESHNESS_S`` is tuned tight so boxes drop quickly after the
    # publisher stops updating (i.e., the target leaves the frame).
    # Sanity-pin the range so it doesn't drift back to multi-second
    # lingering.
    assert 0.2 <= FRESHNESS_S <= 2.0
