"""Vectorized per-cell GSD vs GSDService, and the adequacy piecewise endpoints."""

import numpy as np
import pytest

pytest.importorskip("scipy")

from core.services.GSDService import GSDService
from core.services.coverage.params import PodParams
from core.services.coverage.kernel import compute_target_mask_and_gsd, frame_pod_kernel
from ._kernel_helpers import make_fg, metric_spec

FOCAL = 8.8
SENSOR = (13.2, 8.8)
SIZE = (4000, 3000)
AGL = 120.0


def _grid(fg, params):
    spec = metric_spec(400.0, 320.0, 1.0)
    dem = np.zeros((spec.height, spec.width), dtype=np.float32)
    minx, miny, maxx, maxy = spec.bounds
    cam_xyz = ((minx + maxx) / 2.0, (miny + maxy) / 2.0, fg.agl_m)
    mask, gsd = compute_target_mask_and_gsd(dem, spec, fg, cam_xyz, params, 1.0)
    return spec, dem, cam_xyz, mask, gsd


def test_nadir_gsd_matches_gsdservice():
    fg = make_fg(pitch=-90.0, focal=FOCAL, sensor=SENSOR, size=SIZE, agl=AGL)
    spec, dem, cam_xyz, mask, gsd = _grid(fg, PodParams())
    rows, cols = spec.world_to_index(cam_xyz[0], cam_xyz[1])
    r, c = int(round(float(rows))), int(round(float(cols)))

    svc = GSDService(FOCAL, SIZE, AGL, 0.0, SENSOR)
    center_cm = svc.compute_gsd(SIZE[1] // 2, SIZE[0] // 2)
    assert gsd[r, c] == pytest.approx(center_cm, rel=1e-3)

    analytic = 100.0 * AGL * (SENSOR[0] / SIZE[0]) * 1e-3 / (FOCAL * 1e-3)
    assert gsd[r, c] == pytest.approx(analytic, rel=1e-3)


def test_oblique_on_axis_gsd_matches_gsdservice():
    # 30 deg off nadir (pitch -60).
    fg = make_fg(pitch=-60.0, yaw=0.0, focal=FOCAL, sensor=SENSOR, size=SIZE, agl=AGL)
    spec = metric_spec(600.0, 500.0, 1.0)
    dem = np.zeros((spec.height, spec.width), dtype=np.float32)
    minx, miny, maxx, maxy = spec.bounds
    cam_x = (minx + maxx) / 2.0
    cam_y = miny + 20.0
    cam_xyz = (cam_x, cam_y, AGL)
    mask, gsd = compute_target_mask_and_gsd(dem, spec, fg, cam_xyz, PodParams(), 1.0)
    # On-axis ground point at 60 deg depression: north offset = agl / tan(60).
    import math
    ty = cam_y + AGL / math.tan(math.radians(60.0))
    rows, cols = spec.world_to_index(cam_x, ty)
    r, c = int(round(float(rows))), int(round(float(cols)))
    assert mask[r, c]

    # The kernel uses a geometric-mean closed form while GSDService does a full
    # per-pixel ray/ground projection; they agree exactly at nadir and diverge
    # modestly with obliquity. A ~10% band at 30 deg off-nadir is immaterial to
    # the coarse adequacy ramp.
    svc = GSDService(FOCAL, SIZE, AGL, 30.0, SENSOR)
    center_cm = svc.compute_gsd(SIZE[1] // 2, SIZE[0] // 2)
    assert gsd[r, c] == pytest.approx(center_cm, rel=0.10)


def test_adequacy_endpoints():
    fg = make_fg(pitch=-90.0, focal=FOCAL, sensor=SENSOR, size=SIZE, agl=AGL)
    # Sub-nadir GSD ~4.5 cm. Knobs below it -> adequacy 1; knobs above it -> 0.
    p_full = PodParams(gsd_full_cm=10.0, gsd_max_cm=20.0)
    spec, dem, cam_xyz, mask, gsd = _grid(fg, p_full)
    rows, cols = spec.world_to_index(cam_xyz[0], cam_xyz[1])
    r, c = int(round(float(rows))), int(round(float(cols)))
    pod = frame_pod_kernel(dem, None, None, spec.transform, cam_xyz, mask, gsd, p_full, 1.0)
    assert pod[r, c] == pytest.approx(1.0, rel=1e-3)

    p_zero = PodParams(gsd_full_cm=1.0, gsd_max_cm=3.0)
    pod0 = frame_pod_kernel(dem, None, None, spec.transform, cam_xyz, mask, gsd, p_zero, 1.0)
    assert pod0[r, c] == 0.0
