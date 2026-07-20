"""Unit tests for core.services.CameraModel."""

import math
from unittest.mock import MagicMock

import numpy as np
import pytest

from core.services.CameraModel import CameraModel

WIDTH = 4000
HEIGHT = 3000
FOCAL_MM = 24.0
SENSOR_W = 23.5
SENSOR_H = 15.6
AGL = 100.0


def _nadir():
    return CameraModel(AGL, -90.0, 0.0, FOCAL_MM, SENSOR_W, SENSOR_H, WIDTH, HEIGHT)


def _oblique(pitch_deg=-45.0, yaw_deg=0.0):
    return CameraModel(AGL, pitch_deg, yaw_deg, FOCAL_MM, SENSOR_W, SENSOR_H, WIDTH, HEIGHT)


def test_nadir_projects_ground_point_to_centre():
    cam = _nadir()
    u, v = cam.project(0.0, 0.0, AGL)
    assert u == pytest.approx(WIDTH / 2.0, abs=1e-6)
    assert v == pytest.approx(HEIGHT / 2.0, abs=1e-6)


def test_nadir_east_is_right_north_is_up():
    cam = _nadir()
    u_east, v_east = cam.project(0.0, 10.0, AGL)
    u_north, v_north = cam.project(10.0, 0.0, AGL)
    # East of nadir -> right of centre; North of nadir -> above centre.
    assert u_east > WIDTH / 2.0
    assert v_east == pytest.approx(HEIGHT / 2.0, abs=1e-6)
    assert v_north < HEIGHT / 2.0
    assert u_north == pytest.approx(WIDTH / 2.0, abs=1e-6)


def test_pixel_to_ground_centre():
    cam = _nadir()
    north, east, down = cam.pixel_to_ground(WIDTH / 2.0, HEIGHT / 2.0)
    assert north == pytest.approx(0.0, abs=1e-6)
    assert east == pytest.approx(0.0, abs=1e-6)
    assert down == pytest.approx(AGL, abs=1e-6)


def test_pixel_to_ground_project_roundtrip():
    for cam in (_nadir(), _oblique(-50.0, 30.0)):
        for u, v in [(2500, 1200), (1000, 2000), (2000, 1500)]:
            ground = cam.pixel_to_ground(u, v)
            assert ground is not None
            back = cam.project(*ground)
            assert back is not None
            assert back[0] == pytest.approx(u, abs=1e-3)
            assert back[1] == pytest.approx(v, abs=1e-3)


def test_standing_person_at_nadir_head_over_feet():
    """Straight down on a person: head and feet land on the same pixel."""
    cam = _nadir()
    feet = cam.project(0.0, 0.0, AGL)
    head = cam.project(0.0, 0.0, AGL - 1.8)  # 1.8 m tall
    assert head[0] == pytest.approx(feet[0], abs=1e-6)
    assert head[1] == pytest.approx(feet[1], abs=1e-6)


def test_oblique_view_foreshortens_standing_person():
    """At an oblique angle a standing person's head projects above the feet."""
    cam = _oblique(-45.0, 0.0)
    # Foot point seen through the centre pixel of a 45-degree oblique frame.
    foot = cam.pixel_to_ground(WIDTH / 2.0, HEIGHT / 2.0)
    assert foot is not None
    feet_px = cam.project(*foot)
    head_px = cam.project(foot[0], foot[1], foot[2] - 1.8)
    # Head appears clearly above the feet, with no sideways shift.
    assert head_px[1] < feet_px[1] - 5.0
    assert head_px[0] == pytest.approx(feet_px[0], abs=1.0)


def test_point_behind_camera_returns_none():
    cam = _nadir()
    # A point above the camera (negative down) is behind the optical axis.
    assert cam.project(0.0, 0.0, -10.0) is None


def test_invalid_construction_raises():
    with pytest.raises(ValueError):
        CameraModel(0.0, -90.0, 0.0, FOCAL_MM, SENSOR_W, SENSOR_H, WIDTH, HEIGHT)
    with pytest.raises(ValueError):
        CameraModel(AGL, -90.0, 0.0, FOCAL_MM, SENSOR_W, SENSOR_H, 0, HEIGHT)


def test_from_image_service():
    service = MagicMock()
    service.get_camera_intrinsics.return_value = {
        'focal_length_mm': FOCAL_MM,
        'sensor_width_mm': SENSOR_W,
        'sensor_height_mm': SENSOR_H,
    }
    service.get_relative_altitude.return_value = AGL
    service.get_camera_pitch.return_value = -90.0
    service.get_camera_yaw.return_value = 0.0
    service.img_array = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

    cam = CameraModel.from_image_service(service)
    assert cam is not None
    u, v = cam.project(0.0, 0.0, AGL)
    assert u == pytest.approx(WIDTH / 2.0, abs=1e-6)
    assert v == pytest.approx(HEIGHT / 2.0, abs=1e-6)


def test_square_pixels_on_cropped_aspect():
    """A 16:9 frame on a 3:2 sensor must still yield square pixels (fx == fy).

    DJI Air 2S 1" sensor is 13.2 x 8.8 mm (3:2); a 16:9 still is 5472 x 3078,
    which crops the sensor height. Using the datasheet height directly would
    make fy ~18% smaller than fx and skew the vertical projection.
    """
    cam = CameraModel(46.0, -90.0, 0.0, 8.38, 13.2, 8.8, 5472, 3078)
    assert cam.fx == pytest.approx(cam.fy)
    # True pitch comes from the uncropped (width) axis: 13.2 / 5472.
    assert cam.fx == pytest.approx(8.38 / (13.2 / 5472))


def test_square_pixels_when_width_is_cropped():
    """When the width is the cropped axis, the height pitch is the true one."""
    # 4:3 image on a 3:2 (APS-C) sensor crops the width.
    cam = CameraModel(100.0, -90.0, 0.0, 24.0, 23.5, 15.6, 4000, 3000)
    assert cam.fx == pytest.approx(cam.fy)
    assert cam.fx == pytest.approx(24.0 / (15.6 / 3000))


def test_from_image_service_missing_intrinsics_returns_none():
    service = MagicMock()
    service.get_camera_intrinsics.return_value = None
    assert CameraModel.from_image_service(service) is None


def test_pitch_deg_is_stored():
    assert _nadir().pitch_deg == pytest.approx(-90.0)
    assert _oblique(-45.0).pitch_deg == pytest.approx(-45.0)


def test_footprint_stays_compact_off_nadir():
    """The flat overhead footprint must not 'lay over' as it moves off-nadir.

    A standing person's 3D hull smears radially (H*R/(agl-H)); the footprint
    is flat (z=0) so it stays person-sized anywhere in the frame.
    """
    from core.services.PersonModel import build_footprint_points

    cam = CameraModel(46.0, -90.0, 0.0, 8.38, 13.2, 8.8, 5472, 3078)
    gsd_m = cam.agl_m / cam.fx  # metres per pixel at nadir
    footprint = build_footprint_points(1.70, "standing")

    def width_m(east_m):
        us = []
        for px, py, pz in footprint:
            uv = cam.project(0.0 + py, east_m + px, 46.0 - pz)
            if uv:
                us.append(uv[0])
        return (max(us) - min(us)) * gsd_m

    for east in (0.0, 20.0, 40.0):
        assert width_m(east) < 0.6  # ~0.44 m shoulders, never a 1.8 m smear
