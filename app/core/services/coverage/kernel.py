"""
kernel - pure-numpy geometry for the per-frame POD grid.

Contains, for one frame:
* ``build_camera_rotation`` - the camera->NED rotation, matching
  ``AOIService._calculate_ground_position`` exactly so footprints agree with the
  FOV the viewer already draws.
* ``project_footprint_corners`` / ``compute_frame_spec`` - size the frame-local
  EPSG:3857 grid (flat-plane corners + the nadir point + a buffer).
* ``compute_target_mask_and_gsd`` - which co-registered cells the frustum sees,
  and the per-cell ground sample distance.
* ``frame_pod_kernel`` - the ray-march: terrain visibility x canopy
  transmittance x GSD adequacy (spec section 3.5).

All horizontal math is in EPSG:3857 units; ``meters_per_unit = cos(lat_ref)``
converts horizontal deltas to true ground meters (vertical is already meters).
No Qt, no I/O, no logging side effects.
"""

import math
from typing import List, Optional, Tuple

import numpy as np

from core.services.terrain.grid import (
    GridSpec,
    make_lattice_spec,
    lonlat_to_mercator,
    mercator_units_per_meter,
    WEB_MERCATOR_CRS,
)
from core.services.coverage.contracts import (
    LIMIT_TERRAIN,
    LIMIT_CANOPY,
    LIMIT_GSD,
    LIMIT_NONE,
)


def build_camera_rotation(pitch_deg: float, yaw_deg: float, roll_deg: float,
                          roll_axis_deg: Optional[float] = None) -> np.ndarray:
    """3x3 rotation from camera frame (X=right, Y=down, Z=optical) to NED.

    Mirrors ``AOIService._calculate_ground_position`` step 2 (+ Rodrigues
    roll) so this kernel and the viewer FOV stay consistent. The roll
    rotates about the camera-yaw azimuth by default; ``roll_axis_deg``
    overrides the axis azimuth for stamps that express roll about the
    FLIGHT axis (WALDO processor version >= 6) - using the wrong axis
    mirrors the footprint to the opposite side of the track.
    """
    opt_elevation = math.radians(pitch_deg)
    opt_azimuth = math.radians(yaw_deg)

    opt_axis_ned = np.array([
        math.cos(opt_elevation) * math.cos(opt_azimuth),
        math.cos(opt_elevation) * math.sin(opt_azimuth),
        -math.sin(opt_elevation),
    ])
    up_ned = np.array([
        -math.sin(opt_elevation) * math.cos(opt_azimuth),
        -math.sin(opt_elevation) * math.sin(opt_azimuth),
        -math.cos(opt_elevation),
    ])
    cam_y_ned = -up_ned
    cam_x_ned = np.cross(opt_axis_ned, up_ned)
    cam_x_ned = cam_x_ned / np.linalg.norm(cam_x_ned)

    R = np.column_stack([cam_x_ned, cam_y_ned, opt_axis_ned])

    if roll_deg != 0.0:
        roll_rad = math.radians(roll_deg)
        axis_azimuth = (math.radians(roll_axis_deg)
                        if roll_axis_deg is not None else opt_azimuth)
        heading_axis = np.array([math.cos(axis_azimuth), math.sin(axis_azimuth), 0.0])
        kx, ky, kz = heading_axis
        K = np.array([
            [0.0, -kz, ky],
            [kz, 0.0, -kx],
            [-ky, kx, 0.0],
        ])
        R_roll = np.eye(3) + math.sin(roll_rad) * K + (1.0 - math.cos(roll_rad)) * (K @ K)
        R = R_roll @ R
    return R


def _frustum_half_extents(fg) -> Tuple[float, float]:
    """(hw, hh): image half-width/half-height as tan(half-FOV) = (sensor/2)/focal."""
    sw, sh = fg.sensor_mm
    hw = (sw / 2.0) / fg.focal_mm
    hh = (sh / 2.0) / fg.focal_mm
    return hw, hh


def project_footprint_corners(fg, params) -> List[Tuple[float, float]]:
    """Flat-plane ground offsets (east_m, north_m) of the 4 image corners.

    Rays that miss the ground (pointing up/at the horizon) or land beyond
    ``max_range_m`` are clamped to ``max_range_m`` along their ground azimuth.
    Used only to size the frame bbox.
    """
    hw, hh = _frustum_half_extents(fg)
    R = build_camera_rotation(fg.pitch_deg, fg.yaw_deg, fg.roll_deg,
                              roll_axis_deg=getattr(fg, 'roll_axis_deg', None))
    corners = []
    for sx in (-hw, hw):
        for sy in (-hh, hh):
            ray_cam = np.array([sx, sy, 1.0])
            ray_cam = ray_cam / np.linalg.norm(ray_cam)
            ray_ned = R @ ray_cam
            down = ray_ned[2]
            if down <= 1e-6:
                # Points up/horizon: clamp along the ground azimuth of the ray.
                az = math.atan2(ray_ned[1], ray_ned[0])
                corners.append((math.sin(az) * params.max_range_m,
                                math.cos(az) * params.max_range_m))
                continue
            t = fg.agl_m / down
            north = ray_ned[0] * t
            east = ray_ned[1] * t
            ground_range = math.hypot(north, east)
            if ground_range > params.max_range_m:
                scale = params.max_range_m / ground_range
                north *= scale
                east *= scale
            corners.append((east, north))
    return corners


def compute_frame_spec(fg, params, cell_size_3857: float) -> GridSpec:
    """Lattice-snapped EPSG:3857 GridSpec covering the frame footprint.

    The bbox is the hull of the nadir point and the (clamped) flat-plane
    corners, buffered by ``footprint_buffer_m``. The nadir point is always
    included so oblique frames' line-of-sight corridor (between camera and
    footprint) is sampled for occlusion.
    """
    nadir_x, nadir_y = lonlat_to_mercator(fg.lon, fg.lat)
    units_per_m = mercator_units_per_meter(fg.lat)

    xs = [nadir_x]
    ys = [nadir_y]
    for east_m, north_m in project_footprint_corners(fg, params):
        xs.append(nadir_x + east_m * units_per_m)
        ys.append(nadir_y + north_m * units_per_m)

    buf = params.footprint_buffer_m * units_per_m
    bounds = (min(xs) - buf, min(ys) - buf, max(xs) + buf, max(ys) + buf)
    return make_lattice_spec(bounds, cell_size_3857, crs=WEB_MERCATOR_CRS)


def compute_target_mask_and_gsd(dem: np.ndarray, spec: GridSpec, fg,
                                cam_xyz: Tuple[float, float, float], params,
                                meters_per_unit: float
                                ) -> Tuple[np.ndarray, np.ndarray]:
    """Back-project every cell into the camera; return (mask, gsd_cm).

    ``mask`` is True where the cell (at its DEM elevation) falls inside the
    sensor frustum, within ``max_range_m``, and has finite DEM. ``gsd_cm`` is the
    per-cell ground sample distance in centimeters (meaningful only where masked).
    """
    cam_x, cam_y, cam_z = cam_xyz
    xs, ys = spec.cell_centers()  # (W,), (H,)
    de = (xs[np.newaxis, :] - cam_x) * meters_per_unit      # (1, W) east meters
    dn = (ys[:, np.newaxis] - cam_y) * meters_per_unit      # (H, 1) north meters
    dd = cam_z - dem                                        # (H, W) down meters

    R = build_camera_rotation(fg.pitch_deg, fg.yaw_deg, fg.roll_deg,
                              roll_axis_deg=getattr(fg, 'roll_axis_deg', None))
    Rt = R.T  # camera <- NED
    # p_cam = R^T @ [north, east, down]
    px = Rt[0, 0] * dn + Rt[0, 1] * de + Rt[0, 2] * dd
    py = Rt[1, 0] * dn + Rt[1, 1] * de + Rt[1, 2] * dd
    pz = Rt[2, 0] * dn + Rt[2, 1] * de + Rt[2, 2] * dd

    hw, hh = _frustum_half_extents(fg)
    r = np.sqrt(dn * dn + de * de + dd * dd)               # slant range (H, W)

    with np.errstate(invalid='ignore'):
        in_frustum = (pz > 1e-9) & (np.abs(px) <= pz * hw) & (np.abs(py) <= pz * hh)
        mask = in_frustum & np.isfinite(dem) & (r <= params.max_range_m)

    sw = fg.sensor_mm[0]
    img_w = fg.image_size[0]
    pel_m = (sw / img_w) * 1e-3
    f_m = fg.focal_mm * 1e-3
    with np.errstate(invalid='ignore', divide='ignore'):
        sin_g = np.clip(dd / r, 0.05, 1.0)
        gsd_cm = (100.0 * r * (pel_m / f_m) / np.sqrt(sin_g)).astype(np.float32)

    return mask, gsd_cm


def frame_pod_kernel(dem: np.ndarray, chm: Optional[np.ndarray], cover: Optional[np.ndarray],
                     transform, cam_xyz: Tuple[float, float, float],
                     target_mask: np.ndarray, gsd_cm: np.ndarray, params,
                     meters_per_unit: float = 1.0, return_factors: bool = False):
    """Per-frame POD = terrain_visible x canopy_transmittance x gsd_adequacy.

    ``dem``/``chm``/``cover`` are co-registered (H, W) grids on ``transform``
    (EPSG:3857); ``chm``/``cover`` may be None (transmittance = 1). Returns a
    float32 (H, W) POD array, nonzero only in ``target_mask`` cells.

    When ``return_factors`` is True, returns ``(pod, factor)`` where ``factor``
    is a uint8 (H, W) grid of the dominant limiting factor per target cell
    (LIMIT_TERRAIN / LIMIT_CANOPY / LIMIT_GSD / LIMIT_NONE), for cell inspection.
    """
    H, W = dem.shape
    out = np.zeros((H, W), dtype=np.float32)
    factor = np.zeros((H, W), dtype=np.uint8) if return_factors else None
    rows, cols = np.nonzero(target_mask)
    if rows.size == 0:
        return (out, factor) if return_factors else out

    spec = GridSpec(crs=WEB_MERCATOR_CRS, transform=transform, width=W, height=H)
    xs, ys = spec.cell_centers()
    cam_x, cam_y, cam_z = cam_xyz
    cell_m = transform.a * meters_per_unit
    k_ext = params.extinction_k
    gsd_full = params.gsd_full_cm
    gsd_max = params.gsd_max_cm

    K = params.ray_samples
    u = (np.arange(K, dtype=np.float64) + 0.5) / K
    t = 1.0 - (1.0 - u) ** 2                                     # (K,) camera(0) -> target(1)
    t_edges = 1.0 - (1.0 - np.arange(K + 1, dtype=np.float64) / K) ** 2
    dt = np.diff(t_edges)                                         # (K,)

    from scipy.ndimage import map_coordinates

    chunk = max(1, int(params.kernel_chunk_cells))
    for start in range(0, rows.size, chunk):
        rsel = rows[start:start + chunk]
        csel = cols[start:start + chunk]
        tx = xs[csel]                                            # (n,)
        ty = ys[rsel]
        tz = dem[rsel, csel]
        n = rsel.size

        # Ray points (n, K) from camera to each target cell.
        sx = cam_x + (tx - cam_x)[:, None] * t[None, :]
        sy = cam_y + (ty - cam_y)[:, None] * t[None, :]
        sz = cam_z + (tz - cam_z)[:, None] * t[None, :]

        rr, cc = spec.world_to_index(sx, sy)                    # (n, K) each
        ground = map_coordinates(dem, [rr.ravel(), cc.ravel()], order=1,
                                 mode='constant', cval=np.nan).reshape(n, K)

        ground_range = np.hypot((tx - cam_x) * meters_per_unit,
                                (ty - cam_y) * meters_per_unit)  # (n,)
        ray_len = np.hypot(ground_range, cam_z - tz)             # (n,)

        # Terrain visibility: any DEM sample rises above the ray (excluding the
        # last cell near the target, which is the target's own ground).
        near_ok = (1.0 - t)[None, :] * ground_range[:, None] > cell_m
        with np.errstate(invalid='ignore'):
            blocked = ((ground > sz + params.los_epsilon_m) & near_ok).any(axis=1)

        # Canopy transmittance (Beer-Lambert over foliage path length).
        if chm is not None:
            chm_s = map_coordinates(chm, [rr.ravel(), cc.ravel()], order=1,
                                    mode='constant', cval=np.nan).reshape(n, K)
            chm_s = np.nan_to_num(chm_s, nan=0.0)
            if cover is not None:
                cover_s = map_coordinates(cover, [rr.ravel(), cc.ravel()], order=1,
                                          mode='constant', cval=np.nan).reshape(n, K)
                cover_s = np.clip(np.nan_to_num(cover_s, nan=0.0), 0.0, 1.0)
            else:
                cover_s = np.ones((n, K), dtype=np.float64)
            with np.errstate(invalid='ignore'):
                in_layer = (sz >= ground - 0.01) & (sz <= ground + chm_s)
            # Midpoint Riemann sum of the foliage indicator along the ray. This
            # carries an O(1/K) bias at the sharp canopy boundary; it is a near-
            # constant factor that extinction_k absorbs during field calibration.
            contrib = np.where(in_layer, cover_s, 0.0) * dt[None, :]
            l_eff = contrib.sum(axis=1) * ray_len
            trans = np.exp(-k_ext * l_eff)
        else:
            trans = np.ones(n, dtype=np.float64)

        gsd_vals = gsd_cm[rsel, csel].astype(np.float64)
        denom = (gsd_max - gsd_full) if (gsd_max > gsd_full) else 1e-9
        adequacy = np.clip((gsd_max - gsd_vals) / denom, 0.0, 1.0)

        pod_vals = np.where(blocked, 0.0, trans * adequacy)
        out[rsel, csel] = pod_vals.astype(np.float32)

        if return_factors:
            fac = np.full(rsel.size, LIMIT_NONE, dtype=np.uint8)
            canopy_worse = trans <= adequacy
            fac[(~blocked) & canopy_worse & (trans < 0.999)] = LIMIT_CANOPY
            fac[(~blocked) & (~canopy_worse) & (adequacy < 0.999)] = LIMIT_GSD
            fac[blocked] = LIMIT_TERRAIN
            factor[rsel, csel] = fac

    return (out, factor) if return_factors else out
