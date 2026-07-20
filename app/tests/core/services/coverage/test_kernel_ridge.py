"""Spec section 8-2: a ridge/wall occludes exactly the cells a brute-force
line-of-sight check says it should."""

import math

import numpy as np
import pytest

pytest.importorskip("scipy")

from core.services.coverage.params import PodParams
from core.services.coverage.kernel import compute_target_mask_and_gsd, frame_pod_kernel
from ._kernel_helpers import make_fg, metric_spec

# Dense sampling + generous GSD so POD == terrain visibility (0/adequacy).
PARAMS = PodParams(ray_samples=96, gsd_full_cm=1.0, gsd_max_cm=500.0)


def _brute_blocked(dem, spec, cam, tx, ty, tz, cell_m, n=800, eps=0.5):
    cam_x, cam_y, cam_z = cam
    ground_range = math.hypot(tx - cam_x, ty - cam_y)
    ts = (np.arange(n) + 0.5) / n
    sxs = cam_x + (tx - cam_x) * ts
    sys = cam_y + (ty - cam_y) * ts
    szs = cam_z + (tz - cam_z) * ts
    for i in range(n):
        if (1.0 - ts[i]) * ground_range <= cell_m:
            continue
        rows, cols = spec.world_to_index(sxs[i], sys[i])
        ri = int(round(float(rows)))
        ci = int(round(float(cols)))
        if 0 <= ri < dem.shape[0] and 0 <= ci < dem.shape[1]:
            if dem[ri, ci] > szs[i] + eps:
                return True
    return False


@pytest.fixture
def ridge_scene():
    spec = metric_spec(300.0, 260.0, 1.0)
    dem = np.zeros((spec.height, spec.width), dtype=np.float32)
    # A full-width E-W wall, 60 m tall, spanning y in [100, 110].
    ys = spec.cell_centers()[1]
    wall_rows = np.where((ys >= 100.0) & (ys <= 110.0))[0]
    dem[wall_rows, :] = 60.0
    fg = make_fg(pitch=-35.0, yaw=0.0)
    minx, _, maxx, _ = spec.bounds
    cam_xyz = ((minx + maxx) / 2.0, 20.0, fg.agl_m)  # south edge, looking north
    mask, gsd = compute_target_mask_and_gsd(dem, spec, fg, cam_xyz, PARAMS, 1.0)
    pod = frame_pod_kernel(dem, None, None, spec.transform, cam_xyz, mask, gsd, PARAMS, 1.0)
    return spec, dem, fg, cam_xyz, mask, gsd, pod


def _cell(spec, x, y):
    rows, cols = spec.world_to_index(x, y)
    return int(round(float(rows))), int(round(float(cols)))


def test_spot_checks_front_shadow_and_clear(ridge_scene):
    spec, dem, fg, cam_xyz, mask, gsd, pod = ridge_scene
    cx = cam_xyz[0]
    # In front of the wall -> visible.
    r, c = _cell(spec, cx, 95.0)
    assert mask[r, c] and pod[r, c] > 0
    # Immediately behind the wall -> shadowed (LOS still below the 60 m top).
    r, c = _cell(spec, cx, 135.0)
    assert mask[r, c] and pod[r, c] == 0.0
    # Far enough north that the LOS clears the wall top -> visible again.
    r, c = _cell(spec, cx, 205.0)
    assert mask[r, c] and pod[r, c] > 0


def test_matches_brute_force_along_centerline(ridge_scene):
    spec, dem, fg, cam_xyz, mask, gsd, pod = ridge_scene
    cx = cam_xyz[0]
    ys = spec.cell_centers()[1]
    cell_m = spec.transform.a
    mismatches = 0
    checked = 0
    for y in ys:
        # Skip the wall itself and a small band around the shadow boundary (~y=190)
        # where bilinear (kernel) vs nearest (brute) sampling can disagree by a cell.
        if 98.0 <= y <= 112.0 or 182.0 <= y <= 198.0:
            continue
        r, c = _cell(spec, cx, float(y))
        if not mask[r, c]:
            continue
        checked += 1
        tz = float(dem[r, c])
        brute = _brute_blocked(dem, spec, cam_xyz, cx, float(y), tz, cell_m)
        kernel_blocked = (pod[r, c] == 0.0)
        if brute != kernel_blocked:
            mismatches += 1
    assert checked > 30
    assert mismatches == 0
