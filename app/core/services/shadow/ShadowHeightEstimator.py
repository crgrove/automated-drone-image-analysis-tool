"""Shadow-based object height estimation.

Given two user-clicked pixels in a drone image (object base + shadow tip),
project both to ground using AOIService, then apply the simple shadow
geometry:

    H = Delta_h + d_h * tan(alpha)

where d_h is horizontal ground distance between projected points,
Delta_h is their elevation difference (terrain slope), and alpha is the
solar elevation at the capture time.

Reuses the battle-tested pixel-to-ground projection from
:class:`core.services.image.AOIService.AOIService` — same rotations,
same iterative terrain convergence — and layers solar geometry on top.
No new photogrammetry math is introduced here.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple

import utm

from helpers.MetaDataHelper import MetaDataHelper
from core.services.image.AOIService import AOIService
from core.services.LoggerService import LoggerService
from core.services.shadow.SolarPosition import (
    get_solar_position,
    resolve_capture_utc,
    SolarTimeUnresolvable,
)


# Sun-elevation gates per design §5.9. Below the lower bound shadows are
# unstable; above the upper bound they're too short to read.
MIN_SUN_ELEV_DEG = 5.0
MAX_SUN_ELEV_DEG = 85.0

# Azimuth-mismatch confidence bands per design §5.8.
AZ_OK_DEG = 5.0
AZ_WARNING_DEG = 15.0

# Conservative DEM vertical-accuracy estimate: USGS 3DEP 1 m lidar runs
# ~0.3 m RMSE; coarser DEMs scale roughly with horizontal resolution.
# Floored at 0.3 m so we never claim sub-decimetre accuracy.
DEM_VERTICAL_SIGMA_FLOOR_M = 0.3
DEM_VERTICAL_SIGMA_PER_M = 0.3

# Solar-elevation sigma is dominated by ephemeris model error; the
# subsecond timestamp jitter from drone EXIF is ~0.005°/s and negligible.
SUN_ELEV_SIGMA_DEG = 0.1

# Minimum horizontal separation between the two projected ground points
# before we treat the click as degenerate.
MIN_GROUND_SEPARATION_M = 0.05


@dataclass
class ShadowHeightResult:
    """Output of a shadow-based height estimate.

    `confidence` is one of:
        'ok'        — geometry consistent, within tolerance
        'warning'   — proceeded with a soft warning (e.g. azimuth off 5-15°)
        'rejected'  — refused to estimate; `height_m` is None

    All world coordinates are local-ENU meters relative to the base point
    (so the base is (0, 0, 0); tip is offset). This keeps the numbers small
    and easy to read in the UI/debug log; it has no effect on H.
    """

    confidence: str
    warnings: List[str] = field(default_factory=list)
    height_m: Optional[float] = None
    sigma_m: Optional[float] = None
    sun_elev_deg: Optional[float] = None
    sun_az_deg: Optional[float] = None
    measured_shadow_az_deg: Optional[float] = None
    delta_az_deg: Optional[float] = None
    base_world_xyz: Optional[Tuple[float, float, float]] = None
    tip_world_xyz: Optional[Tuple[float, float, float]] = None
    horizontal_dist_m: Optional[float] = None
    elev_delta_m: Optional[float] = None
    base_lat_lon: Optional[Tuple[float, float]] = None
    tip_lat_lon: Optional[Tuple[float, float]] = None
    dem_source: Optional[str] = None
    terrain_resolution_m: Optional[float] = None
    utc_used: Optional[datetime] = None
    time_source: Optional[str] = None
    rejection_reason: Optional[str] = None
    # True when the rejection is specifically an azimuth-band failure; the
    # dialog uses this to surface a "Use anyway" override button.
    azimuth_override_available: bool = False


class ShadowHeightEstimator:
    """Estimate height from a base+tip pixel pair and image metadata."""

    def __init__(self, logger: Optional[LoggerService] = None):
        self.logger = logger or LoggerService()

    def estimate(
        self,
        image: dict,
        base_px: Tuple[float, float],
        tip_px: Tuple[float, float],
        allow_azimuth_override: bool = False,
        use_terrain: bool = True,
    ) -> ShadowHeightResult:
        """Compute height of a vertical object from its shadow.

        Args:
            image: ADIAT image-metadata dict (must contain 'path').
            base_px: (u, v) pixel of the object's ground base.
            tip_px:  (u, v) pixel of the shadow tip.
            allow_azimuth_override: if True, demote an out-of-tolerance
                shadow-azimuth mismatch from rejection to warning. The
                dialog sets this when the user clicks "Use anyway" on a
                previously-rejected measurement.
            use_terrain: honor DEM terrain data when projecting the clicks
                to ground (mirrors the viewer's UseTerrainElevation
                preference). When False the flat-terrain fallback is used
                and the estimate ignores ground slope.

        Returns:
            ShadowHeightResult — always returned, even on rejection.
            Callers should branch on `.confidence`.
        """
        result = ShadowHeightResult(confidence='rejected')

        # --- Capture-time → UTC ---
        try:
            exif_data = MetaDataHelper.get_exif_data_piexif(image['path'])
        except Exception as exc:
            return _reject(result, f"Could not read EXIF: {exc}")

        # XMP carries the capture-time offset that DJI (and most modern
        # cameras) omit from OffsetTimeOriginal. Read it lazily here so the
        # resolver can fall back to it without re-parsing the file.
        try:
            xmp_data = MetaDataHelper.get_xmp_data(image['path'], parse=True)
        except Exception:
            xmp_data = None

        try:
            utc_dt, time_source = resolve_capture_utc(exif_data, xmp_data)
        except SolarTimeUnresolvable as exc:
            return _reject(result, str(exc))
        result.utc_used = utc_dt
        result.time_source = time_source

        # --- Project both pixels to the ground ---
        try:
            aoi_service = AOIService(image)
        except Exception as exc:
            return _reject(result, f"Could not load image for projection: {exc}")

        base_gps = aoi_service.estimate_aoi_gps(
            image, {'center': tuple(base_px)}, use_terrain=use_terrain
        )
        if base_gps is None:
            return _reject(
                result,
                _diagnose_projection_failure(aoi_service, exif_data, "base"),
            )
        tip_gps = aoi_service.estimate_aoi_gps(
            image, {'center': tuple(tip_px)}, use_terrain=use_terrain
        )
        if tip_gps is None:
            return _reject(
                result,
                _diagnose_projection_failure(aoi_service, exif_data, "shadow-tip"),
            )

        result.base_lat_lon = (base_gps.latitude, base_gps.longitude)
        result.tip_lat_lon = (tip_gps.latitude, tip_gps.longitude)
        result.dem_source = base_gps.elevation_source
        result.terrain_resolution_m = base_gps.terrain_resolution_m

        # --- Convert to local meters (UTM, both points forced into the same zone) ---
        base_east, base_north, zone_no, zone_letter = utm.from_latlon(
            base_gps.latitude, base_gps.longitude
        )
        tip_east, tip_north, _, _ = utm.from_latlon(
            tip_gps.latitude, tip_gps.longitude,
            force_zone_number=zone_no,
            force_zone_letter=zone_letter,
        )

        d_east = tip_east - base_east
        d_north = tip_north - base_north
        d_h = math.hypot(d_east, d_north)

        if d_h < MIN_GROUND_SEPARATION_M:
            return _reject(
                result,
                "Base and shadow-tip clicks project to the same ground point. "
                "Pick two clearly different pixels."
            )

        # Elevation difference — only meaningful when both ground points
        # came from a real DEM, not a flat-terrain fallback.
        if base_gps.elevation_source == 'terrain' and tip_gps.elevation_source == 'terrain':
            base_elev = base_gps.terrain_elevation_m or 0.0
            tip_elev = tip_gps.terrain_elevation_m or 0.0
            delta_h = tip_elev - base_elev
        else:
            base_elev = 0.0
            tip_elev = 0.0
            delta_h = 0.0
            result.warnings.append(
                "No DEM available for this location; assuming flat terrain. "
                "Estimate ignores ground slope."
            )

        # Express both points in local-ENU relative to base.
        result.base_world_xyz = (0.0, 0.0, 0.0)
        result.tip_world_xyz = (d_east, d_north, delta_h)
        result.horizontal_dist_m = d_h
        result.elev_delta_m = delta_h

        # Bearing of the drawn shadow line, base→tip, clockwise from north.
        measured_az = math.degrees(math.atan2(d_east, d_north)) % 360.0
        result.measured_shadow_az_deg = measured_az

        # --- Sun position ---
        sun_elev, sun_az = get_solar_position(
            base_gps.latitude, base_gps.longitude, utc_dt
        )
        result.sun_elev_deg = sun_elev
        result.sun_az_deg = sun_az

        if sun_elev < MIN_SUN_ELEV_DEG:
            return _reject(
                result,
                f"Sun is too low ({sun_elev:.1f}°). Shadow geometry is "
                "unreliable below 5°."
            )
        if sun_elev > MAX_SUN_ELEV_DEG:
            return _reject(
                result,
                f"Sun is nearly overhead ({sun_elev:.1f}°). Shadows are "
                "too short to measure reliably above 85°."
            )

        # Expected shadow direction = away from sun.
        expected_az = (sun_az + 180.0) % 360.0
        delta_az = ((measured_az - expected_az + 180.0) % 360.0) - 180.0
        result.delta_az_deg = delta_az

        if abs(delta_az) > AZ_WARNING_DEG:
            if allow_azimuth_override:
                result.warnings.append(
                    f"Shadow direction is {abs(delta_az):.1f}° off the "
                    f"expected direction; override accepted, but the "
                    "estimate is sensitive to this mismatch."
                )
            else:
                rejected = _reject(
                    result,
                    f"Drawn line is {delta_az:+.1f}° off the expected shadow "
                    f"direction (sun azimuth {sun_az:.1f}°). Click the object "
                    "base first, then the shadow tip."
                )
                rejected.azimuth_override_available = True
                return rejected
        elif abs(delta_az) > AZ_OK_DEG:
            result.warnings.append(
                f"Shadow direction differs from expected by "
                f"{abs(delta_az):.1f}°; result may be inaccurate."
            )

        # --- Height ---
        alpha = math.radians(sun_elev)
        height_m = delta_h + d_h * math.tan(alpha)
        if height_m <= 0:
            return _reject(
                result,
                f"Computed negative or zero height ({height_m:.2f} m). "
                "Likely the base/tip click order is reversed."
            )
        result.height_m = height_m

        # --- Uncertainty (design §5.10) ---
        result.sigma_m = _propagate_sigma(
            d_h=d_h,
            alpha=alpha,
            terrain_resolution_m=base_gps.terrain_resolution_m,
            base_effective_agl_m=base_gps.effective_agl_m,
            tip_effective_agl_m=tip_gps.effective_agl_m,
            image_service=aoi_service.image_service,
        )

        result.confidence = 'warning' if result.warnings else 'ok'
        return result


def _reject(result: ShadowHeightResult, reason: str) -> ShadowHeightResult:
    """Stamp the rejection reason and return the result unchanged otherwise."""
    result.confidence = 'rejected'
    result.rejection_reason = reason
    result.warnings.append(reason)
    return result


def _diagnose_projection_failure(aoi_service, exif_data, which: str) -> str:
    """Translate a generic AOIService rejection into a specific user message.

    AOIService logs the precise reason but only returns None to callers, so
    we re-derive the failure mode from the metadata to surface something
    actionable in the dialog.
    """
    image_service = getattr(aoi_service, 'image_service', None)

    # GPS is the cheapest precondition to verify.
    gps = (exif_data or {}).get('GPS') or {}
    if not gps:
        return (
            f"Could not project the {which} click: image has no GPS "
            "coordinates in EXIF."
        )

    # Camera intrinsics — typically missing when the drone/camera isn't in
    # drones.csv.
    intrinsics = None
    if image_service is not None:
        try:
            intrinsics = image_service.get_camera_intrinsics()
        except Exception:
            intrinsics = None
    if not intrinsics:
        make = _decode(exif_data.get('0th', {}).get(_PIEXIF_MAKE_TAG))
        model = _decode(exif_data.get('0th', {}).get(_PIEXIF_MODEL_TAG))
        descriptor = " / ".join(filter(None, [make, model])) or "this camera"
        return (
            f"Could not project the {which} click: no camera profile for "
            f"{descriptor} in drones.csv (need sensor + focal length)."
        )

    # AGL — DJI carries it in XMP RelativeAltitude; airframe/WALDO imagery
    # gets it synthesized by the WALDO pre-pass.
    agl = None
    pitch = None
    if image_service is not None:
        try:
            agl = image_service.get_relative_altitude('m')
        except Exception:
            agl = None
        try:
            pitch = image_service.get_camera_pitch()
        except Exception:
            pitch = None
    if not agl or agl <= 0:
        make = _decode(exif_data.get('0th', {}).get(_PIEXIF_MAKE_TAG)) or ''
        if make.upper().startswith(('CANON', 'SONY', 'NIKON', 'FUJI')):
            return (
                f"Could not project the {which} click: airframe imagery "
                "without AGL. Run Tools > WALDO Pre-Pass on this folder "
                "first so per-image altitude and gimbal angles are written "
                "into the XMP."
            )
        return (
            f"Could not project the {which} click: no RelativeAltitude in "
            "XMP and no terrain-derived AGL fallback. Verify the drone "
            "wrote altitude metadata."
        )

    # Pitch — AOIService assumes nadir (-90°) when missing; pitch >= 0 means
    # the optical axis is at or above the horizon, so the ray never hits ground.
    if pitch is not None and pitch >= 0:
        return (
            f"Could not project the {which} click: camera pitch is "
            f"{pitch:.1f}° (at or above horizon), so the click can't be "
            "projected onto terrain."
        )

    # Last resort — the ray went off into space (clicked above horizon, or
    # terrain coverage doesn't reach that far).
    return (
        f"Could not project the {which} click onto terrain. The ray "
        "either missed terrain coverage or landed above the horizon. "
        "Check that the click is on the ground."
    )


_PIEXIF_MAKE_TAG = 271   # piexif.ImageIFD.Make
_PIEXIF_MODEL_TAG = 272  # piexif.ImageIFD.Model


def _decode(value) -> Optional[str]:
    """Best-effort bytes→str for piexif IFD0 tags."""
    if value is None:
        return None
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8', errors='ignore').strip().rstrip('\x00')
        except Exception:
            return None
    return str(value).strip()


def _propagate_sigma(
    d_h: float,
    alpha: float,
    terrain_resolution_m: Optional[float],
    base_effective_agl_m: Optional[float],
    tip_effective_agl_m: Optional[float],
    image_service,
) -> float:
    """First-order uncertainty propagation for H = Delta_h + d_h * tan(alpha).

    σ_H² ≈ (tan α · σ_dh)²  +  (d_h · sec²α · σ_α)²  +  σ_Δh²
    """
    # σ_α: ephemeris + timestamp jitter (radians).
    sigma_alpha = math.radians(SUN_ELEV_SIGMA_DEG)

    # σ_Δh: terrain DEM vertical accuracy, combined for two endpoints.
    if terrain_resolution_m is not None:
        sigma_dem_vert = max(
            DEM_VERTICAL_SIGMA_FLOOR_M,
            DEM_VERTICAL_SIGMA_PER_M * terrain_resolution_m,
        )
    else:
        sigma_dem_vert = DEM_VERTICAL_SIGMA_FLOOR_M
    sigma_delta_h = sigma_dem_vert * math.sqrt(2.0)

    # σ_dh: pixel-localization noise projected to ground via the per-pixel
    # GSD at each endpoint. Approximate GSD as effective_AGL / focal_px —
    # exact at nadir, conservative-low under oblique viewing.
    sigma_dh = _estimate_horizontal_sigma(
        base_effective_agl_m, tip_effective_agl_m, image_service
    )

    cos_a = math.cos(alpha)
    sec2_a = 1.0 / (cos_a * cos_a) if cos_a != 0 else 0.0
    var = (
        (math.tan(alpha) * sigma_dh) ** 2
        + (d_h * sec2_a * sigma_alpha) ** 2
        + sigma_delta_h ** 2
    )
    return math.sqrt(var)


def _estimate_horizontal_sigma(
    base_agl_m: Optional[float],
    tip_agl_m: Optional[float],
    image_service,
) -> float:
    """Estimate σ_dh from the per-pixel ground sample distance at each endpoint.

    Falls back to a conservative 1 m when intrinsics are unavailable.
    """
    try:
        intrinsics = image_service.get_camera_intrinsics()
    except Exception:
        intrinsics = None
    if not intrinsics:
        return 1.0

    focal_mm = intrinsics.get('focal_length_mm')
    sensor_w_mm = intrinsics.get('sensor_width_mm')
    img_width = image_service.img_array.shape[1] if image_service.img_array is not None else None
    if not (focal_mm and sensor_w_mm and img_width):
        return 1.0

    focal_px = focal_mm * img_width / sensor_w_mm
    base_agl = base_agl_m if (base_agl_m and base_agl_m > 0) else 0.0
    tip_agl = tip_agl_m if (tip_agl_m and tip_agl_m > 0) else 0.0
    if base_agl == 0.0 and tip_agl == 0.0:
        return 1.0

    gsd_base = base_agl / focal_px if base_agl > 0 else 0.0
    gsd_tip = tip_agl / focal_px if tip_agl > 0 else 0.0
    return math.sqrt(2.0) * math.hypot(gsd_base, gsd_tip)
