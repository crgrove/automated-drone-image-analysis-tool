"""PersonShadow - cast a standing person's shadow onto the ground.

The forward complement of ShadowHeightEstimator: given a known person
height and the sun position (from SolarPosition at the image's capture
time), project the person's 3D form along the sun ray onto the ground to
produce the shadow outline.

Geometry is computed in the same local North/East/Down (NED) frame used by
CameraModel, so the resulting ground points can be projected straight to
image pixels.

The `slope` parameter is a hook for a terrain-slope correction (the shadow
is shorter uphill, longer downhill). Callers that have DEM data can sample
the grade along the shadow direction and pass it in; with slope = 0 the
shadow is computed on flat ground at the (already DEM-placed) foot level.
"""

import math
from typing import List, Sequence, Tuple

Point3D = Tuple[float, float, float]


def shadow_length(height_m: float, sun_elevation_deg: float, slope: float = 0.0) -> float:
    """Horizontal length of the shadow cast by a vertical object.

    Args:
        height_m: object height above the ground, metres.
        sun_elevation_deg: sun elevation above the horizon, degrees.
        slope: terrain gradient along the shadow direction (rise/run);
            positive means the ground rises away from the sun, shortening
            the shadow. Default 0 (flat ground).

    Returns:
        Horizontal shadow length in metres, or 0.0 when the sun is at or
        below the horizon (no usable shadow).
    """
    if sun_elevation_deg <= 0.0:
        return 0.0
    denom = math.tan(math.radians(sun_elevation_deg)) + slope
    if denom <= 1e-6:
        return 0.0
    return max(0.0, height_m) / denom


def compute_shadow_ground_points(
    person_points: Sequence[Point3D],
    foot_ned: Point3D,
    sun_elevation_deg: float,
    sun_azimuth_deg: float,
    slope: float = 0.0,
) -> List[Point3D]:
    """Cast a 3D person point cloud along the sun ray onto the ground.

    Each point is dropped along the sun ray to the ground: a point at
    height z lands a horizontal distance z / (tan(elevation) + slope) away,
    in the direction opposite the sun.

    Args:
        person_points: person-local surface points (x = right, y = forward,
            z = up), origin at the feet.
        foot_ned: (north, east, down) of the person's feet in the camera
            NED frame.
        sun_elevation_deg: sun elevation above the horizon, degrees.
        sun_azimuth_deg: sun azimuth, degrees (0 = north, clockwise).
        slope: terrain gradient along the shadow direction; default 0 (flat).

    Returns:
        Ground points (north, east, down) for every cast point. Empty when
        the sun is at or below the horizon.
    """
    if sun_elevation_deg <= 0.0:
        return []
    denom = math.tan(math.radians(sun_elevation_deg)) + slope
    if denom <= 1e-6:
        return []

    foot_n, foot_e, foot_d = foot_ned
    # Shadows fall away from the sun.
    anti_sun = math.radians(sun_azimuth_deg + 180.0)
    dir_north = math.cos(anti_sun)
    dir_east = math.sin(anti_sun)

    ground: List[Point3D] = []
    for px, py, pz in person_points:
        # Person-local -> camera NED: x = right = east, y = forward = north.
        base_n = foot_n + py
        base_e = foot_e + px
        length = max(0.0, pz) / denom
        ground.append((
            base_n + length * dir_north,
            base_e + length * dir_east,
            foot_d,
        ))
    return ground
