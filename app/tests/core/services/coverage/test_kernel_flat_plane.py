"""Spec section 8-1: flat-plane nadir POD footprint matches the analytic FOV."""

import numpy as np
import pytest

pytest.importorskip("scipy")

from core.services.coverage.params import PodParams
from core.services.coverage.kernel import compute_target_mask_and_gsd, frame_pod_kernel
from ._kernel_helpers import make_fg, metric_spec


def _run(fg, cell=0.5, width_m=240.0, height_m=200.0, params=None):
    params = params or PodParams(gsd_full_cm=1.0, gsd_max_cm=50.0)
    spec = metric_spec(width_m, height_m, cell)
    dem = np.zeros((spec.height, spec.width), dtype=np.float32)
    minx, miny, maxx, maxy = spec.bounds
    cam_xyz = ((minx + maxx) / 2.0, (miny + maxy) / 2.0, fg.agl_m)
    mask, gsd = compute_target_mask_and_gsd(dem, spec, fg, cam_xyz, params, 1.0)
    pod = frame_pod_kernel(dem, None, None, spec.transform, cam_xyz, mask, gsd, params, 1.0)
    return spec, mask, gsd, pod, cam_xyz


def test_nadir_footprint_area_within_1_percent():
    fg = make_fg(pitch=-90.0, yaw=0.0)
    cell = 0.5
    spec, mask, gsd, pod, _ = _run(fg, cell=cell)
    # Analytic nadir ground rectangle: (agl * sensor_w / focal) x (agl * sensor_h / focal).
    exp_w = fg.agl_m * fg.sensor_mm[0] / fg.focal_mm    # 180 m
    exp_h = fg.agl_m * fg.sensor_mm[1] / fg.focal_mm    # 120 m
    expected_area = exp_w * exp_h
    area = int(mask.sum()) * cell * cell
    assert area == pytest.approx(expected_area, rel=0.01)
    # POD is nonzero exactly where visible-in-frustum.
    assert np.count_nonzero(pod) == int(mask.sum())


def test_interior_pod_equals_adequacy_at_nadir():
    params = PodParams()  # default gsd knobs 2..10
    fg = make_fg(pitch=-90.0)
    spec, mask, gsd, pod, cam_xyz = _run(fg, params=params)
    # Cell directly under the camera: r == agl, sin_gamma == 1.
    cam_x, cam_y, _ = cam_xyz
    rows, cols = spec.world_to_index(cam_x, cam_y)
    r, c = int(round(float(rows))), int(round(float(cols)))
    pel_m = (fg.sensor_mm[0] / fg.image_size[0]) * 1e-3
    f_m = fg.focal_mm * 1e-3
    gsd_center_cm = 100.0 * fg.agl_m * pel_m / f_m
    adequacy = (params.gsd_max_cm - gsd_center_cm) / (params.gsd_max_cm - params.gsd_full_cm)
    assert pod[r, c] == pytest.approx(adequacy, rel=0.02)
    assert gsd[r, c] == pytest.approx(gsd_center_cm, rel=1e-3)


def test_rotated_yaw_preserves_area():
    cell = 0.5
    _, mask0, _, _, _ = _run(make_fg(pitch=-90.0, yaw=0.0), cell=cell)
    _, mask37, _, _, _ = _run(make_fg(pitch=-90.0, yaw=37.0), cell=cell)
    a0 = int(mask0.sum()) * cell * cell
    a37 = int(mask37.sum()) * cell * cell
    assert a37 == pytest.approx(a0, rel=0.01)
