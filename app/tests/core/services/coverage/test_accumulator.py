"""Spec section 8-4: multi-look combination (max within a bin, product across
bins, common-mode ceiling, per-frame cap, confidence haircut, lazy growth)."""

import numpy as np
import pytest

from core.services.coverage.params import PodParams
from core.services.coverage.accumulator import MissionAccumulator
from core.services.terrain.grid import make_lattice_spec

CELL = 3.0
C = 0.90  # common_mode_ceiling default


def _spec(x0=0.0, y0=0.0, n=30.0):
    return make_lattice_spec((x0, y0, x0 + n, y0 + n), CELL)


def _const_pod(spec, value):
    return np.full((spec.height, spec.width), value, dtype=np.float32)


def _fresh(params=None):
    params = params or PodParams()
    return MissionAccumulator(CELL, params), params


# Each of these tests fills a single constant-valued frame region on an otherwise
# zero mission grid, so the grid max equals the accumulated value at that region
# (independent of where the coarse-snapped mission grid places the frame).


def test_two_frames_same_bin_do_not_compound():
    acc, _ = _fresh()
    spec = _spec()
    for _ in range(2):
        assert acc.add_frame(0, _const_pod(spec, 0.5), spec, yaw_deg=0.0,
                             pitch_deg=-90.0, bearing_confidence=1.0)
    pod, look, _, _, _ = acc.finalize()
    assert float(pod.max()) == pytest.approx(C * 0.5, abs=1e-4)


def test_two_frames_different_bins_combine():
    acc, _ = _fresh()
    spec = _spec()
    acc.add_frame(0, _const_pod(spec, 0.5), spec, 0.0, -90.0, 1.0)     # bin 0
    acc.add_frame(1, _const_pod(spec, 0.5), spec, 180.0, -90.0, 1.0)   # bin 2
    pod, _, _, _, _ = acc.finalize()
    assert float(pod.max()) == pytest.approx(C * 0.75, abs=1e-4)


def test_eight_bins_at_cap_asymptote_to_ceiling():
    acc, _ = _fresh()
    spec = _spec()
    for i, (yaw, pitch) in enumerate([(y, p) for p in (-90.0, -50.0)
                                      for y in (0.0, 90.0, 180.0, 270.0)]):
        acc.add_frame(i, _const_pod(spec, 1.0), spec, yaw, pitch, 1.0)
    pod, _, _, _, _ = acc.finalize()
    v = float(pod.max())
    assert v == pytest.approx(C, abs=1e-3)
    assert v < 1.0


def test_per_frame_cap_applied():
    acc, _ = _fresh()
    spec = _spec()
    acc.add_frame(0, _const_pod(spec, 1.0), spec, 0.0, -90.0, 1.0)
    pod, _, _, _, _ = acc.finalize()
    assert float(pod.max()) == pytest.approx(C * 0.85, abs=1e-4)


def test_low_confidence_haircut():
    acc, params = _fresh()
    spec = _spec()
    acc.add_frame(0, _const_pod(spec, 0.8), spec, 0.0, -90.0, bearing_confidence=0.4)
    pod, _, _, _, _ = acc.finalize()
    expected = C * (0.8 * params.low_confidence_haircut)
    assert float(pod.max()) == pytest.approx(expected, abs=1e-4)


def test_look_count_counts_positive_frames():
    acc, _ = _fresh()
    spec = _spec()
    acc.add_frame(0, _const_pod(spec, 0.5), spec, 0.0, -90.0, 1.0)
    acc.add_frame(1, _const_pod(spec, 0.5), spec, 90.0, -90.0, 1.0)
    _, look, _, _, _ = acc.finalize()
    assert int(look.max()) == 2


def test_lazy_growth_preserves_both_frames():
    acc, _ = _fresh()
    a = _spec(0.0, 0.0)
    b = _spec(3000.0, 3000.0)  # far away -> triggers growth
    assert acc.add_frame(0, _const_pod(a, 0.6), a, 0.0, -90.0, 1.0)
    assert acc.add_frame(1, _const_pod(b, 0.4), b, 0.0, -90.0, 1.0)
    pod, look, _, fidx, transform = acc.finalize()
    from core.services.coverage.contracts import CoverageResult
    res = CoverageResult(pod=pod, look_count=look, transform=transform,
                         image_count=2, skipped=[], stats={}, gap_polygons=[],
                         cancelled=False, frame_index=fidx)
    # Both frame regions carry their values in the grown grid.
    from core.services.terrain.grid import mercator_to_lonlat
    for spec, val, fid in ((a, C * 0.6, 0), (b, C * 0.4, 1)):
        xs, ys = spec.cell_centers()
        cx, cy = float(xs[spec.width // 2]), float(ys[spec.height // 2])
        lon, lat = mercator_to_lonlat(cx, cy)
        s = res.sample(lat, lon)
        assert s is not None
        assert s['pod'] == pytest.approx(val, abs=1e-3)
        assert fid in s['frames']


def test_budget_refusal_returns_false():
    params = PodParams(mem_budget_mb=1)  # tiny budget
    acc = MissionAccumulator(CELL, params)
    a = _spec(0.0, 0.0)
    b = _spec(3000.0, 3000.0)  # union ~1e6 cells -> exceeds 1 MB
    assert acc.add_frame(0, _const_pod(a, 0.6), a, 0.0, -90.0, 1.0)
    assert acc.add_frame(1, _const_pod(b, 0.6), b, 0.0, -90.0, 1.0) is False


@pytest.mark.parametrize("yaw,pitch,expected", [
    (0.0, -90.0, 0), (89.0, -90.0, 1), (91.0, -90.0, 1),
    (181.0, -90.0, 2), (271.0, -90.0, 3),
    (0.0, -50.0, 4), (0.0, -10.0, 4), (271.0, -50.0, 7),
])
def test_bin_for_frame_table(yaw, pitch, expected):
    assert MissionAccumulator.bin_for_frame(yaw, pitch, PodParams()) == expected


# --- limiting-factor tracking (best_factor follows the highest-POD look) -------
#
# add_frame records a per-cell limiting-factor code (frame_factor) but only where
# the frame's capped POD exceeds the running best POD, so the mission-wide
# limiting-factor grid always reflects the *best look* at each cell. finalize()
# then stamps LIMIT_NO_LOOKS wherever no positive look ever landed.

from core.services.coverage.contracts import (  # noqa: E402
    LIMIT_NO_LOOKS, LIMIT_TERRAIN, LIMIT_CANOPY,
)


def _const_factor(spec, code):
    return np.full((spec.height, spec.width), code, dtype=np.uint8)


def _region(spec, transform, shape):
    """(r0, c0) of ``spec``'s top-left cell within the finalized mission grid.

    Rebuilds the mission GridSpec from finalize()'s returned transform + array
    shape (public data only) so tests can index the exact frame footprint inside
    the coarse-snapped mission grid.
    """
    from core.services.terrain.grid import (
        GridSpec, WEB_MERCATOR_CRS, integer_offset,
    )
    mission = GridSpec(crs=WEB_MERCATOR_CRS, transform=transform,
                       width=int(shape[1]), height=int(shape[0]))
    return integer_offset(spec, mission)


def test_best_factor_follows_higher_pod_added_second():
    # Same region, same bin. The second (higher-POD) frame's factor must win.
    acc, _ = _fresh()
    spec = _spec()
    acc.add_frame(0, _const_pod(spec, 0.4), spec, 0.0, -90.0, 1.0,
                  frame_factor=_const_factor(spec, LIMIT_TERRAIN))
    acc.add_frame(1, _const_pod(spec, 0.6), spec, 0.0, -90.0, 1.0,
                  frame_factor=_const_factor(spec, LIMIT_CANOPY))
    _, look, limiting, _, transform = acc.finalize()

    r0, c0 = _region(spec, transform, limiting.shape)
    region = limiting[r0:r0 + spec.height, c0:c0 + spec.width]
    assert np.all(region == LIMIT_CANOPY)
    # And the whole footprint was actually looked at.
    assert np.all(look[r0:r0 + spec.height, c0:c0 + spec.width] > 0)


def test_best_factor_not_overwritten_by_lower_pod():
    # Higher-POD frame first; a later lower-POD look must NOT replace its factor.
    acc, _ = _fresh()
    spec = _spec()
    acc.add_frame(0, _const_pod(spec, 0.6), spec, 0.0, -90.0, 1.0,
                  frame_factor=_const_factor(spec, LIMIT_CANOPY))
    acc.add_frame(1, _const_pod(spec, 0.4), spec, 0.0, -90.0, 1.0,
                  frame_factor=_const_factor(spec, LIMIT_TERRAIN))
    _, _, limiting, _, transform = acc.finalize()

    r0, c0 = _region(spec, transform, limiting.shape)
    region = limiting[r0:r0 + spec.height, c0:c0 + spec.width]
    assert np.all(region == LIMIT_CANOPY)


def test_best_factor_equal_pod_does_not_overwrite():
    # best_factor updates only where capped POD *exceeds* (strict >) the running
    # best; an equal-POD later look must not flip the factor.
    acc, _ = _fresh()
    spec = _spec()
    acc.add_frame(0, _const_pod(spec, 0.5), spec, 0.0, -90.0, 1.0,
                  frame_factor=_const_factor(spec, LIMIT_TERRAIN))
    acc.add_frame(1, _const_pod(spec, 0.5), spec, 0.0, -90.0, 1.0,
                  frame_factor=_const_factor(spec, LIMIT_CANOPY))
    _, _, limiting, _, transform = acc.finalize()

    r0, c0 = _region(spec, transform, limiting.shape)
    region = limiting[r0:r0 + spec.height, c0:c0 + spec.width]
    assert np.all(region == LIMIT_TERRAIN)


def test_best_factor_tracks_higher_pod_per_cell():
    # Two overlapping frames whose POD dominance splits left/right. best_factor
    # must be chosen per cell from whichever frame had the higher capped POD.
    acc, _ = _fresh()
    spec = _spec()
    h, w = spec.height, spec.width
    half = w // 2

    pod1 = np.full((h, w), 0.3, dtype=np.float32)
    pod1[:, :half] = 0.7                       # frame 1 wins the left half
    pod2 = np.full((h, w), 0.3, dtype=np.float32)
    pod2[:, half:] = 0.7                       # frame 2 wins the right half

    acc.add_frame(0, pod1, spec, 0.0, -90.0, 1.0,
                  frame_factor=_const_factor(spec, LIMIT_TERRAIN))
    acc.add_frame(1, pod2, spec, 0.0, -90.0, 1.0,
                  frame_factor=_const_factor(spec, LIMIT_CANOPY))
    _, _, limiting, _, transform = acc.finalize()

    r0, c0 = _region(spec, transform, limiting.shape)
    region = limiting[r0:r0 + h, c0:c0 + w]
    assert np.all(region[:, :half] == LIMIT_TERRAIN)
    assert np.all(region[:, half:] == LIMIT_CANOPY)


def test_finalize_stamps_no_looks_on_never_looked_cells():
    # The coarse-snapped mission grid is larger than a single frame, so cells
    # outside the frame are never looked and finalize must stamp LIMIT_NO_LOOKS
    # there, while looked cells retain their tracked limiting factor.
    acc, _ = _fresh()
    spec = _spec()
    acc.add_frame(0, _const_pod(spec, 0.5), spec, 0.0, -90.0, 1.0,
                  frame_factor=_const_factor(spec, LIMIT_CANOPY))
    _, look, limiting, _, _ = acc.finalize()

    assert np.any(look == 0)                    # there really are unseen cells
    assert np.all(limiting[look == 0] == LIMIT_NO_LOOKS)
    assert np.all(limiting[look > 0] == LIMIT_CANOPY)
