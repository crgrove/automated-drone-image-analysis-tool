"""Spec section 8-5: a constant vertical datum offset must not change POD.

The datum rule sets cam_elev = DEM(nadir) + AGL, so shifting the whole DEM (and
therefore the camera) by a constant leaves every relative height identical.
"""

import numpy as np
import pytest

pytest.importorskip("scipy")

from core.services.coverage.params import PodParams
from core.services.coverage.kernel import compute_target_mask_and_gsd, frame_pod_kernel
from ._kernel_helpers import make_fg, metric_spec

PARAMS = PodParams(ray_samples=96, gsd_full_cm=1.0, gsd_max_cm=500.0)


def _pod_for_dem(dem, spec, fg, cam_xy, agl):
    # Datum rule: camera elevation tracks the DEM under the nadir point.
    rows, cols = spec.world_to_index(cam_xy[0], cam_xy[1])
    r, c = int(round(float(rows))), int(round(float(cols)))
    cam_z = float(dem[r, c]) + agl
    cam_xyz = (cam_xy[0], cam_xy[1], cam_z)
    mask, gsd = compute_target_mask_and_gsd(dem, spec, fg, cam_xyz, PARAMS, 1.0)
    return frame_pod_kernel(dem, None, None, spec.transform, cam_xyz, mask, gsd, PARAMS, 1.0)


def test_constant_datum_offset_invariant_with_ridge():
    spec = metric_spec(300.0, 260.0, 1.0)
    dem = np.zeros((spec.height, spec.width), dtype=np.float32)
    ys = spec.cell_centers()[1]
    wall_rows = np.where((ys >= 100.0) & (ys <= 110.0))[0]
    dem[wall_rows, :] = 60.0
    fg = make_fg(pitch=-35.0, yaw=0.0)
    minx, _, maxx, _ = spec.bounds
    cam_xy = ((minx + maxx) / 2.0, 20.0)
    agl = 120.0

    pod1 = _pod_for_dem(dem, spec, fg, cam_xy, agl)
    pod2 = _pod_for_dem(dem - 30.0, spec, fg, cam_xy, agl)
    assert np.array_equal(pod1, pod2)
