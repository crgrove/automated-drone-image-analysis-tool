"""Tests for the POD / look-count RGBA lookup tables."""

import numpy as np

from core.services.coverage.params import PodParams
from core.services.coverage.colormap import (
    _build_pod_lut,
    pod_to_rgba,
    look_count_to_rgba,
    chm_to_rgba,
)


def test_pod_lut_shape_and_alpha_ramp():
    lut = _build_pod_lut(0.05)
    assert lut.shape == (256, 4)
    floor_i = int(round(0.05 * 255))
    # Fully transparent below the floor, opaque-ish above.
    assert np.all(lut[:floor_i, 3] == 0)
    assert lut[floor_i:, 3].max() > 150
    # Alpha is monotonically non-decreasing above the floor.
    assert np.all(np.diff(lut[floor_i:, 3].astype(int)) >= 0)


def test_pod_to_rgba_transparent_where_no_looks():
    params = PodParams()
    pod = np.array([[0.0, 0.5], [0.8, 0.9]], dtype=np.float32)
    look = np.array([[0, 2], [0, 3]], dtype=np.uint16)
    rgba = pod_to_rgba(pod, look, params)
    assert rgba.shape == (2, 2, 4)
    # Cells with zero looks are fully transparent regardless of POD value.
    assert tuple(rgba[0, 0]) == (0, 0, 0, 0)
    assert tuple(rgba[1, 0]) == (0, 0, 0, 0)
    # Looked cells above the floor are opaque.
    assert rgba[0, 1, 3] > 0
    assert rgba[1, 1, 3] > 0


def test_chm_rgba_transparent_at_open_ground_and_nodata():
    chm = np.array([[np.nan, 0.0, 0.3, 5.0]], dtype=np.float32)
    rgba = chm_to_rgba(chm)
    assert rgba.shape == (1, 4, 4)
    # NaN, bare ground, and sub-threshold vegetation are all fully transparent.
    assert tuple(rgba[0, 0]) == (0, 0, 0, 0)
    assert tuple(rgba[0, 1]) == (0, 0, 0, 0)
    assert tuple(rgba[0, 2]) == (0, 0, 0, 0)
    assert rgba[0, 3, 3] > 0


def test_chm_rgba_darker_and_more_opaque_with_height():
    chm = np.array([[2.0, 15.0, 35.0, 80.0]], dtype=np.float32)
    rgba = chm_to_rgba(chm, max_height_m=35.0)
    # Green channel dominates and darkens as canopy gets taller.
    lum = rgba[0, :, :3].astype(int).sum(axis=1)
    assert lum[0] > lum[1] > lum[2]
    # Alpha rises with height, saturating at max_height_m.
    assert rgba[0, 0, 3] < rgba[0, 1, 3] < rgba[0, 2, 3]
    assert tuple(rgba[0, 2]) == tuple(rgba[0, 3])


def test_look_count_rgba_saturates():
    look = np.array([[0, 1, 2, 3, 4, 5, 9]], dtype=np.uint16)
    rgba = look_count_to_rgba(look)
    assert tuple(rgba[0, 0]) == (0, 0, 0, 0)   # 0 looks transparent
    assert rgba[0, 1, 3] > 0                    # 1 look visible
    # 5 and 9 saturate to the same top step.
    assert tuple(rgba[0, 5]) == tuple(rgba[0, 6])


# --- P3 LUT edges: display floor at/above 1.0 and NaN inputs -------------------


def test_pod_lut_fully_transparent_when_floor_at_one():
    """display_floor == 1.0 pushes the alpha floor to index 255, leaving no room
    for the ramp -> the whole LUT alpha channel is 0 (nothing renders)."""
    lut = _build_pod_lut(1.0)
    assert lut.shape == (256, 4)
    assert np.all(lut[:, 3] == 0)


def test_pod_lut_fully_transparent_when_floor_above_one():
    """display_floor > 1.0 is clamped to 1.0 -> still an all-transparent LUT,
    and the RGB (viridis) channels are unchanged vs. a normal floor."""
    lut_high = _build_pod_lut(1.5)
    assert lut_high.shape == (256, 4)
    assert np.all(lut_high[:, 3] == 0)
    # RGB ramp is independent of the alpha floor: identical to a normal LUT.
    lut_ref = _build_pod_lut(0.05)
    assert np.array_equal(lut_high[:, :3], lut_ref[:, :3])


def test_pod_to_rgba_nan_input_no_crash_and_transparent():
    """NaN POD values are squashed to 0.0 via nan_to_num, so they index the
    bottom of the LUT (below the display floor) -> transparent, no crash/warning."""
    params = PodParams()
    pod = np.array([[np.nan, 0.9], [np.nan, 0.0]], dtype=np.float32)
    look = np.array([[2, 2], [3, 3]], dtype=np.uint16)  # all looked -> not zeroed by look mask
    with np.errstate(invalid="raise"):
        rgba = pod_to_rgba(pod, look, params)
    assert rgba.shape == (2, 2, 4)
    assert rgba.dtype == np.uint8
    # NaN cells map to POD 0.0, which is below the default floor -> alpha 0.
    assert rgba[0, 0, 3] == 0
    assert rgba[1, 0, 3] == 0
    # A genuinely looked, high-POD cell still renders.
    assert rgba[0, 1, 3] > 0


def test_pod_to_rgba_all_nan_grid_is_all_transparent():
    """A grid that is entirely NaN produces a valid, fully-transparent output."""
    params = PodParams()
    pod = np.full((3, 3), np.nan, dtype=np.float32)
    look = np.ones((3, 3), dtype=np.uint16)  # looked everywhere -> transparency is from NaN path
    rgba = pod_to_rgba(pod, look, params)
    assert rgba.shape == (3, 3, 4)
    assert np.all(rgba[..., 3] == 0)


def test_chm_to_rgba_nan_input_no_crash_and_transparent():
    """NaN canopy heights are squashed to 0.0 via nan_to_num -> below the
    minimum height -> transparent, while a valid tall cell still renders."""
    chm = np.array([[np.nan, 20.0], [np.nan, np.nan]], dtype=np.float32)
    with np.errstate(invalid="raise"):
        rgba = chm_to_rgba(chm)
    assert rgba.shape == (2, 2, 4)
    assert rgba.dtype == np.uint8
    # NaN cells are fully transparent.
    assert tuple(rgba[0, 0]) == (0, 0, 0, 0)
    assert tuple(rgba[1, 0]) == (0, 0, 0, 0)
    assert tuple(rgba[1, 1]) == (0, 0, 0, 0)
    # The one valid tall-canopy cell renders opaque-ish.
    assert rgba[0, 1, 3] > 0


def test_chm_to_rgba_all_nan_grid_is_all_transparent():
    """An entirely-NaN canopy grid yields a valid, fully-transparent output."""
    chm = np.full((2, 4), np.nan, dtype=np.float32)
    rgba = chm_to_rgba(chm)
    assert rgba.shape == (2, 4, 4)
    assert np.all(rgba == 0)
