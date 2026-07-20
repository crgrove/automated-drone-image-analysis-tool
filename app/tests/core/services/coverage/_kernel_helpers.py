"""Shared helpers for coverage-kernel tests (metric grids, FrameGeometry literals)."""

from core.services.image.FrameGeometry import FrameGeometry
from core.services.terrain.grid import make_lattice_spec


def make_fg(pitch, yaw=0.0, roll=0.0, agl=120.0, focal=8.8,
            sensor=(13.2, 8.8), size=(4000, 3000)):
    """A FrameGeometry with typical DJI intrinsics; lat/lon are unused by the
    kernel (footprint/mask/ray-march work in the supplied metric grid)."""
    return FrameGeometry(
        lat=38.7, lon=-120.5, agl_m=agl, yaw_deg=yaw, pitch_deg=pitch, roll_deg=roll,
        focal_mm=focal, sensor_mm=sensor, image_size=size, principal_point_mm=None,
        yaw_source='gimbal', bearing_confidence=1.0, asl_alt_m=None, cam_elev_m=None,
    )


def metric_spec(width_m, height_m, cell):
    """A north-up EPSG:3857 GridSpec whose units equal true meters (use
    meters_per_unit=1.0), snapped so the origin sits at (0, 0)."""
    return make_lattice_spec((0.0, 0.0, float(width_m), float(height_m)), float(cell))
