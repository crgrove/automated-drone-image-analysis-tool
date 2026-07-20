"""Spec section 8-3: canopy transmittance matches closed-form Beer-Lambert."""

import math

import numpy as np
import pytest

pytest.importorskip("scipy")

from core.services.coverage.params import PodParams
from core.services.coverage.kernel import compute_target_mask_and_gsd, frame_pod_kernel
from ._kernel_helpers import make_fg, metric_spec

# Generous GSD knobs (gsd_full above every in-frame GSD) so adequacy == 1
# everywhere and POD isolates transmittance.
PARAMS = PodParams(gsd_full_cm=50.0, gsd_max_cm=1000.0, extinction_k=0.06)

# The midpoint ray-march carries an O(1/K) integration bias at the sharp canopy
# boundary (~5% in L at K=48); it is a constant that extinction_k absorbs during
# field calibration (spec section 8-6), so the closed-form checks use a matching
# tolerance rather than asserting exactness.
BEER_TOL = 0.07


def _pod_grid(fg, chm_val, cover_val, cell=1.0, width_m=240.0, height_m=200.0,
              params=PARAMS):
    spec = metric_spec(width_m, height_m, cell)
    dem = np.zeros((spec.height, spec.width), dtype=np.float32)
    chm = (None if chm_val is None
           else np.full((spec.height, spec.width), chm_val, dtype=np.float32))
    cover = (None if cover_val is None
             else np.full((spec.height, spec.width), cover_val, dtype=np.float32))
    minx, miny, maxx, maxy = spec.bounds
    cam_xyz = ((minx + maxx) / 2.0, (miny + maxy) / 2.0, fg.agl_m)
    mask, gsd = compute_target_mask_and_gsd(dem, spec, fg, cam_xyz, params, 1.0)
    pod = frame_pod_kernel(dem, chm, cover, spec.transform, cam_xyz, mask, gsd, params, 1.0)
    return spec, mask, pod, cam_xyz


def _center_pod(spec, pod, cam_xyz):
    rows, cols = spec.world_to_index(cam_xyz[0], cam_xyz[1])
    return float(pod[int(round(float(rows))), int(round(float(cols)))])


def test_nadir_uniform_canopy_beer_lambert():
    fg = make_fg(pitch=-90.0)
    spec, mask, pod, cam = _pod_grid(fg, chm_val=20.0, cover_val=1.0)
    expected = math.exp(-PARAMS.extinction_k * 20.0)   # vertical path == chm
    center = _center_pod(spec, pod, cam)
    assert center == pytest.approx(expected, rel=BEER_TOL)
    # The sub-nadir cell is the most vertical LOS, so it has the shortest canopy
    # path and the highest transmittance of the frame.
    assert center == pytest.approx(float(pod[mask].max()), rel=1e-3)


def test_cover_half_halves_optical_path():
    fg = make_fg(pitch=-90.0)
    spec, mask, pod, cam = _pod_grid(fg, chm_val=20.0, cover_val=0.5)
    expected = math.exp(-PARAMS.extinction_k * 20.0 * 0.5)
    assert _center_pod(spec, pod, cam) == pytest.approx(expected, rel=BEER_TOL)


def test_no_canopy_transmittance_one():
    fg = make_fg(pitch=-90.0)
    spec, mask, pod, cam = _pod_grid(fg, chm_val=None, cover_val=None)
    # adequacy == 1 (generous knobs), no canopy -> POD == 1.
    assert _center_pod(spec, pod, cam) == pytest.approx(1.0, rel=1e-3)
    assert np.allclose(pod[mask], 1.0, atol=1e-3)


def test_oblique_45_path_is_root2_longer():
    # Optical axis at 45 deg depression; the cell on the axis sees the 20 m layer
    # over a slant path of ~20 * sqrt(2).
    fg = make_fg(pitch=-45.0, yaw=0.0)
    spec = metric_spec(600.0, 400.0, 1.0)
    dem = np.zeros((spec.height, spec.width), dtype=np.float32)
    chm = np.full((spec.height, spec.width), 20.0, dtype=np.float32)
    cover = np.ones((spec.height, spec.width), dtype=np.float32)
    # Camera near the south edge so the -45 deg axis lands inside the grid.
    minx, miny, maxx, maxy = spec.bounds
    cam_x = (minx + maxx) / 2.0
    cam_y = miny + 20.0
    cam_z = fg.agl_m
    cam_xyz = (cam_x, cam_y, cam_z)
    mask, gsd = compute_target_mask_and_gsd(dem, spec, fg, cam_xyz, PARAMS, 1.0)
    pod = frame_pod_kernel(dem, chm, cover, spec.transform, cam_xyz, mask, gsd, PARAMS, 1.0)
    # On-axis ground point at 45 deg: north offset == agl (since tan(45)=1).
    tgt_x, tgt_y = cam_x, cam_y + fg.agl_m
    rows, cols = spec.world_to_index(tgt_x, tgt_y)
    r, c = int(round(float(rows))), int(round(float(cols)))
    assert mask[r, c]
    l_eff = -math.log(pod[r, c]) / PARAMS.extinction_k
    assert l_eff == pytest.approx(20.0 * math.sqrt(2), rel=0.10)
