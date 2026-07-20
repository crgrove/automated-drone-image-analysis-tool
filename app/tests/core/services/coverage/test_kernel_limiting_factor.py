"""Per-cell limiting-factor classification (``frame_pod_kernel(return_factors=True)``)
and ``compute_frame_spec`` bbox sizing.

Closes the audit gap that no test exercised the ``return_factors`` branch of
``frame_pod_kernel`` (the LIMIT_* classification block) nor the oblique-frame
sizing path of ``compute_frame_spec``. Scenes/geometry reuse the same builders as
the ridge/canopy kernel tests.
"""

import math

import numpy as np
import pytest

pytest.importorskip("scipy")

from affine import Affine

from core.services.coverage.params import PodParams
from core.services.coverage.kernel import (
    compute_target_mask_and_gsd,
    frame_pod_kernel,
    compute_frame_spec,
    project_footprint_corners,
)
from core.services.coverage.contracts import (
    LIMIT_NO_LOOKS,
    LIMIT_TERRAIN,
    LIMIT_CANOPY,
    LIMIT_GSD,
    LIMIT_NONE,
)
from core.services.terrain.grid import (
    lonlat_to_mercator,
    mercator_units_per_meter,
    WEB_MERCATOR_CRS,
)
from ._kernel_helpers import make_fg, metric_spec

# Ridge scene knobs (match test_kernel_ridge): dense rays + generous GSD so POD is
# pure terrain visibility and the only limiter behind the wall is occlusion.
RIDGE_PARAMS = PodParams(ray_samples=96, gsd_full_cm=1.0, gsd_max_cm=500.0)
# Canopy scene knobs (match test_kernel_canopy): GSD so generous adequacy == 1
# everywhere and POD isolates canopy transmittance.
CANOPY_PARAMS = PodParams(gsd_full_cm=50.0, gsd_max_cm=1000.0, extinction_k=0.06)


def _cell(spec, x, y):
    rows, cols = spec.world_to_index(x, y)
    return int(round(float(rows))), int(round(float(cols)))


def _ridge_scene():
    """South-edge camera at pitch -35 looking north over a 60 m E-W wall."""
    spec = metric_spec(300.0, 260.0, 1.0)
    dem = np.zeros((spec.height, spec.width), dtype=np.float32)
    ys = spec.cell_centers()[1]
    wall_rows = np.where((ys >= 100.0) & (ys <= 110.0))[0]
    dem[wall_rows, :] = 60.0
    fg = make_fg(pitch=-35.0, yaw=0.0)
    minx, _, maxx, _ = spec.bounds
    cam_xyz = ((minx + maxx) / 2.0, 20.0, fg.agl_m)
    mask, gsd = compute_target_mask_and_gsd(dem, spec, fg, cam_xyz, RIDGE_PARAMS, 1.0)
    pod, factor = frame_pod_kernel(dem, None, None, spec.transform, cam_xyz,
                                   mask, gsd, RIDGE_PARAMS, 1.0, return_factors=True)
    return spec, dem, fg, cam_xyz, mask, gsd, pod, factor


def _nadir_scene(chm_val=None, cover_val=None, params=None,
                 width_m=240.0, height_m=200.0, cell=1.0):
    """Flat-DEM nadir frame; optional uniform canopy height/cover."""
    params = params or PodParams()
    fg = make_fg(pitch=-90.0)
    spec = metric_spec(width_m, height_m, cell)
    dem = np.zeros((spec.height, spec.width), dtype=np.float32)
    chm = (None if chm_val is None
           else np.full((spec.height, spec.width), chm_val, dtype=np.float32))
    cover = (None if cover_val is None
             else np.full((spec.height, spec.width), cover_val, dtype=np.float32))
    minx, miny, maxx, maxy = spec.bounds
    cam_xyz = ((minx + maxx) / 2.0, (miny + maxy) / 2.0, fg.agl_m)
    mask, gsd = compute_target_mask_and_gsd(dem, spec, fg, cam_xyz, params, 1.0)
    pod, factor = frame_pod_kernel(dem, chm, cover, spec.transform, cam_xyz,
                                   mask, gsd, params, 1.0, return_factors=True)
    return spec, cam_xyz, mask, pod, factor


# --- return_factors contract -------------------------------------------------

def test_return_factors_returns_tuple_and_uint8_grid():
    spec, cam_xyz, mask, pod, factor = _nadir_scene(
        params=PodParams(gsd_full_cm=1.0, gsd_max_cm=500.0))
    assert factor.shape == pod.shape
    assert factor.dtype == np.uint8
    # Factor is only meaningful inside the mask; outside cells stay LIMIT_NO_LOOKS.
    assert np.all(factor[~mask] == LIMIT_NO_LOOKS)


def test_return_factors_false_returns_bare_array():
    """Default return shape is unchanged (single ndarray, not a tuple)."""
    spec, cam_xyz, _, _, _ = _nadir_scene(
        params=PodParams(gsd_full_cm=1.0, gsd_max_cm=500.0))
    fg = make_fg(pitch=-90.0)
    dem = np.zeros((spec.height, spec.width), dtype=np.float32)
    params = PodParams(gsd_full_cm=1.0, gsd_max_cm=500.0)
    mask, gsd = compute_target_mask_and_gsd(dem, spec, fg, cam_xyz, params, 1.0)
    out = frame_pod_kernel(dem, None, None, spec.transform, cam_xyz,
                           mask, gsd, params, 1.0)
    assert isinstance(out, np.ndarray)
    assert out.shape == (spec.height, spec.width)


def test_return_factors_empty_mask_all_no_looks():
    """The early-return (no target cells) path still yields a factor grid."""
    dem = np.zeros((5, 5), dtype=np.float32)
    transform = Affine(1.0, 0.0, 0.0, 0.0, -1.0, 5.0)
    mask = np.zeros((5, 5), dtype=bool)
    gsd = np.zeros((5, 5), dtype=np.float32)
    pod, factor = frame_pod_kernel(dem, None, None, transform, (2.5, 2.5, 120.0),
                                   mask, gsd, PodParams(), 1.0, return_factors=True)
    assert factor.shape == (5, 5)
    assert factor.dtype == np.uint8
    assert np.all(factor == LIMIT_NO_LOOKS)
    assert np.all(pod == 0.0)


# --- (a) terrain-occluded cell -> LIMIT_TERRAIN ------------------------------

def test_shadowed_ridge_cell_is_limit_terrain():
    spec, dem, fg, cam_xyz, mask, gsd, pod, factor = _ridge_scene()
    cx = cam_xyz[0]
    # Immediately behind the 60 m wall: masked (in-frustum) but LOS is blocked.
    r, c = _cell(spec, cx, 135.0)
    assert mask[r, c]
    assert pod[r, c] == 0.0
    assert factor[r, c] == LIMIT_TERRAIN
    # In front of the wall the LOS is clear, so it is never terrain-limited.
    r2, c2 = _cell(spec, cx, 95.0)
    assert mask[r2, c2] and pod[r2, c2] > 0
    assert factor[r2, c2] != LIMIT_TERRAIN


def test_terrain_factor_only_where_pod_zeroed_by_occlusion():
    spec, dem, fg, cam_xyz, mask, gsd, pod, factor = _ridge_scene()
    # Every LIMIT_TERRAIN cell must be a masked cell whose POD was driven to 0.
    terrain = mask & (factor == LIMIT_TERRAIN)
    assert terrain.any()
    assert np.all(pod[terrain] == 0.0)


# --- (b) tall low-transmittance canopy -> LIMIT_CANOPY -----------------------

def test_tall_canopy_nadir_cell_is_limit_canopy():
    spec, cam_xyz, mask, pod, factor = _nadir_scene(
        chm_val=20.0, cover_val=1.0, params=CANOPY_PARAMS)
    r, c = _cell(spec, cam_xyz[0], cam_xyz[1])
    assert mask[r, c]
    # trans ~ exp(-0.06 * 20) ~ 0.30 (< adequacy == 1) -> canopy dominates.
    assert 0.0 < pod[r, c] < 0.999
    assert factor[r, c] == LIMIT_CANOPY


# --- (c) coarse GSD (no canopy, clear LOS) -> LIMIT_GSD ----------------------

def test_coarse_gsd_nadir_cell_is_limit_gsd():
    # Nadir GSD is ~4.5 cm; putting gsd_max just above it makes adequacy the sole
    # sub-unity factor (trans == 1, LOS clear).
    params = PodParams(gsd_full_cm=1.0, gsd_max_cm=6.0)
    spec, cam_xyz, mask, pod, factor = _nadir_scene(params=params)
    r, c = _cell(spec, cam_xyz[0], cam_xyz[1])
    assert mask[r, c]
    assert 0.0 < pod[r, c] < 0.999
    assert factor[r, c] == LIMIT_GSD


# --- (d) generous GSD + no canopy + clear LOS -> LIMIT_NONE ------------------

def test_clear_generous_nadir_cell_is_limit_none():
    # gsd_full above the nadir GSD -> adequacy clips to 1; no canopy -> trans == 1.
    params = PodParams(gsd_full_cm=10.0, gsd_max_cm=1000.0)
    spec, cam_xyz, mask, pod, factor = _nadir_scene(params=params)
    r, c = _cell(spec, cam_xyz[0], cam_xyz[1])
    assert mask[r, c]
    assert pod[r, c] == pytest.approx(1.0, rel=1e-3)
    assert factor[r, c] == LIMIT_NONE


# --- compute_frame_spec sizing (oblique frame) -------------------------------

def _frame_spec_for(fg, params=None):
    params = params or PodParams()
    units_per_m = mercator_units_per_meter(fg.lat)
    cell = params.grid_res_m * units_per_m
    spec = compute_frame_spec(fg, params, cell)
    return spec, params, units_per_m


def test_compute_frame_spec_contains_nadir_and_footprint_corners():
    fg = make_fg(pitch=-35.0, yaw=0.0)
    spec, params, units_per_m = _frame_spec_for(fg)
    assert spec.crs == WEB_MERCATOR_CRS
    assert spec.width >= 1 and spec.height >= 1

    nadir_x, nadir_y = lonlat_to_mercator(fg.lon, fg.lat)
    minx, miny, maxx, maxy = spec.bounds

    # Nadir is always included (spec samples the LOS corridor to the footprint).
    assert minx <= nadir_x <= maxx
    assert miny <= nadir_y <= maxy

    corners = project_footprint_corners(fg, params)
    assert corners  # oblique frame projects real ground corners
    for east_m, north_m in corners:
        cx = nadir_x + east_m * units_per_m
        cy = nadir_y + north_m * units_per_m
        assert minx <= cx <= maxx
        assert miny <= cy <= maxy

    # The far (largest ground-range) corner is contained too.
    east_far, north_far = max(corners, key=lambda c: math.hypot(c[0], c[1]))
    fx = nadir_x + east_far * units_per_m
    fy = nadir_y + north_far * units_per_m
    assert minx <= fx <= maxx and miny <= fy <= maxy


def test_compute_frame_spec_padding_at_least_footprint_buffer():
    fg = make_fg(pitch=-35.0, yaw=0.0)
    spec, params, units_per_m = _frame_spec_for(fg)

    nadir_x, nadir_y = lonlat_to_mercator(fg.lon, fg.lat)
    xs = [nadir_x]
    ys = [nadir_y]
    for east_m, north_m in project_footprint_corners(fg, params):
        xs.append(nadir_x + east_m * units_per_m)
        ys.append(nadir_y + north_m * units_per_m)

    minx, miny, maxx, maxy = spec.bounds
    buf_m = params.footprint_buffer_m  # 50.0 default
    tol = 1e-6

    # make_lattice_spec snaps OUTWARD, so each side has at least the buffer margin
    # (in true ground meters) beyond the footprint hull.
    assert (min(xs) - minx) / units_per_m >= buf_m - tol
    assert (maxx - max(xs)) / units_per_m >= buf_m - tol
    assert (min(ys) - miny) / units_per_m >= buf_m - tol
    assert (maxy - max(ys)) / units_per_m >= buf_m - tol


def test_compute_frame_spec_includes_nadir_for_steep_oblique():
    # A shallow, far-reaching frame: the footprint sits well forward of the
    # camera, yet the nadir ground point must remain inside the grid.
    fg = make_fg(pitch=-12.0, yaw=90.0)
    spec, params, _ = _frame_spec_for(fg)
    nadir_x, nadir_y = lonlat_to_mercator(fg.lon, fg.lat)
    minx, miny, maxx, maxy = spec.bounds
    assert minx <= nadir_x <= maxx
    assert miny <= nadir_y <= maxy
