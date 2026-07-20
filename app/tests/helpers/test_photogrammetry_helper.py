"""Unit tests for helpers.PhotogrammetryHelper."""

import math

import cv2
import numpy as np
import pytest

from helpers.PhotogrammetryHelper import (
    FovHomography,
    build_camera_matrix,
    camera_center_world,
    corners_are_mirrored,
    local_enu_to_gps,
    project_pixel_to_plane,
    recover_camera_pose,
    validate_alignment,
)

# A footprint in US 3DEP territory; ~200 m east-west, ~150 m north-south.
ORIGIN_LAT = 39.5
ORIGIN_LON = -105.5
IMG_WIDTH = 4000
IMG_HEIGHT = 3000


def _enu_corner(east, north):
    """Build a (lat, lon) corner from local East/North metres about the origin."""
    return local_enu_to_gps(east, north, ORIGIN_LAT, ORIGIN_LON)


def _rectangular_corners():
    """Four corners (TL, TR, BR, BL) of a north-up rectangular footprint."""
    return [
        _enu_corner(-100.0, 75.0),   # TL  -> pixel (0, 0)
        _enu_corner(100.0, 75.0),    # TR  -> pixel (W, 0)
        _enu_corner(100.0, -75.0),   # BR  -> pixel (W, H)
        _enu_corner(-100.0, -75.0),  # BL  -> pixel (0, H)
    ]


def test_corners_map_to_pixel_corners():
    corners = _rectangular_corners()
    homography = FovHomography(corners, IMG_WIDTH, IMG_HEIGHT)

    pixel_corners = [(0, 0), (IMG_WIDTH, 0), (IMG_WIDTH, IMG_HEIGHT), (0, IMG_HEIGHT)]
    for (u, v), (exp_lat, exp_lon) in zip(pixel_corners, corners):
        lat, lon = homography.pixel_to_gps(u, v)
        assert lat == pytest.approx(exp_lat, abs=1e-7)
        assert lon == pytest.approx(exp_lon, abs=1e-7)


def test_center_pixel_maps_to_centroid():
    homography = FovHomography(_rectangular_corners(), IMG_WIDTH, IMG_HEIGHT)
    lat, lon = homography.pixel_to_gps(IMG_WIDTH / 2.0, IMG_HEIGHT / 2.0)
    assert lat == pytest.approx(ORIGIN_LAT, abs=1e-7)
    assert lon == pytest.approx(ORIGIN_LON, abs=1e-7)


def test_pixel_gps_roundtrip():
    homography = FovHomography(_rectangular_corners(), IMG_WIDTH, IMG_HEIGHT)
    for u, v in [(1234, 2345), (10, 10), (3990, 5), (2000, 1500)]:
        lat, lon = homography.pixel_to_gps(u, v)
        back_u, back_v = homography.gps_to_pixel(lat, lon)
        assert back_u == pytest.approx(u, abs=1e-3)
        assert back_v == pytest.approx(v, abs=1e-3)


def test_tie_points_least_squares_fit():
    """A tie point consistent with the 4-corner fit must not break the solve."""
    corners = _rectangular_corners()
    base = FovHomography(corners, IMG_WIDTH, IMG_HEIGHT)

    # Place a tie point exactly on the base homography (perfectly consistent).
    tie_lat, tie_lon = base.pixel_to_gps(1000, 750)
    tie_points = [(1000.0, 750.0, tie_lat, tie_lon)]

    refined = FovHomography(corners, IMG_WIDTH, IMG_HEIGHT, tie_points=tie_points)

    # With a consistent extra point the corners still map the same.
    for (u, v), (exp_lat, exp_lon) in zip(
        [(0, 0), (IMG_WIDTH, IMG_HEIGHT)], [corners[0], corners[2]]
    ):
        lat, lon = refined.pixel_to_gps(u, v)
        assert lat == pytest.approx(exp_lat, abs=1e-6)
        assert lon == pytest.approx(exp_lon, abs=1e-6)

    # And the tie-point pixel still maps back to its GPS.
    lat, lon = refined.pixel_to_gps(1000, 750)
    assert lat == pytest.approx(tie_lat, abs=1e-6)
    assert lon == pytest.approx(tie_lon, abs=1e-6)


def test_consistent_tie_point_is_kept():
    """A tie point consistent with the four corners is retained for the fit."""
    corners = _rectangular_corners()
    base = FovHomography(corners, IMG_WIDTH, IMG_HEIGHT)
    tie_lat, tie_lon = base.pixel_to_gps(1500, 1200)
    tie = (1500.0, 1200.0, tie_lat, tie_lon)

    refined = FovHomography(corners, IMG_WIDTH, IMG_HEIGHT, tie_points=[tie])
    assert refined.rejected_tie_points == []
    assert len(refined.tie_points) == 1


def test_backwards_tie_point_is_rejected():
    """A tie point inconsistent with the four corners must not move them.

    This is the 'handles swapped' mistake: the pixel and the GPS refer to
    different places. The bad tie point must be dropped so the carefully
    placed corners still map exactly.
    """
    corners = _rectangular_corners()
    base = FovHomography(corners, IMG_WIDTH, IMG_HEIGHT)

    # Pixel near the top-left corner, GPS near the bottom-right corner.
    bad_lat, bad_lon = base.pixel_to_gps(IMG_WIDTH - 200, IMG_HEIGHT - 200)
    bad_tie = (200.0, 200.0, bad_lat, bad_lon)

    refined = FovHomography(corners, IMG_WIDTH, IMG_HEIGHT, tie_points=[bad_tie])

    assert refined.tie_points == []
    assert bad_tie in refined.rejected_tie_points
    # The corners are still mapped exactly - the bad tie point was ignored.
    pixel_corners = [(0, 0), (IMG_WIDTH, 0), (IMG_WIDTH, IMG_HEIGHT), (0, IMG_HEIGHT)]
    for (u, v), (exp_lat, exp_lon) in zip(pixel_corners, corners):
        lat, lon = refined.pixel_to_gps(u, v)
        assert lat == pytest.approx(exp_lat, abs=1e-6)
        assert lon == pytest.approx(exp_lon, abs=1e-6)


def test_invalid_construction_raises():
    corners = _rectangular_corners()
    with pytest.raises(ValueError):
        FovHomography(corners[:3], IMG_WIDTH, IMG_HEIGHT)
    with pytest.raises(ValueError):
        FovHomography(corners, 0, IMG_HEIGHT)


def test_validate_alignment_accepts_good_quad():
    assert validate_alignment(_rectangular_corners()) is True


def test_validate_alignment_rejects_wrong_count():
    assert validate_alignment(_rectangular_corners()[:3]) is False
    assert validate_alignment(None) is False


def test_validate_alignment_rejects_coincident_corners():
    corners = _rectangular_corners()
    corners[1] = corners[0]  # duplicate TL into the TR slot
    assert validate_alignment(corners) is False


def test_validate_alignment_rejects_bowtie():
    # Swapping BR and BL produces a self-intersecting (bow-tie) quad.
    corners = [
        _enu_corner(-100.0, 75.0),
        _enu_corner(100.0, 75.0),
        _enu_corner(-100.0, -75.0),
        _enu_corner(100.0, -75.0),
    ]
    assert validate_alignment(corners) is False


def test_validate_alignment_rejects_nonfinite():
    corners = _rectangular_corners()
    corners[2] = (float("nan"), corners[2][1])
    assert validate_alignment(corners) is False


def test_corners_are_mirrored_accepts_correct_order():
    assert corners_are_mirrored(_rectangular_corners()) is False


def test_corners_are_mirrored_detects_vertical_flip():
    # Swap the top and bottom corners: TL<->BL and TR<->BR.
    tl, tr, br, bl = _rectangular_corners()
    assert corners_are_mirrored([bl, br, tr, tl]) is True


def test_corners_are_mirrored_detects_horizontal_flip():
    # Swap the left and right corners: TL<->TR and BL<->BR.
    tl, tr, br, bl = _rectangular_corners()
    assert corners_are_mirrored([tr, tl, bl, br]) is True


# --- DEM resection (camera pose recovery) ---

def _synthetic_pose():
    """A nadir camera ~400 m above the origin (rvec, tvec, world centre)."""
    # Camera axes in world: X=East, Y=South (image-down), Z=Down (forward).
    rotation = np.array([
        [1.0, 0.0, 0.0],
        [0.0, -1.0, 0.0],
        [0.0, 0.0, -1.0],
    ], dtype=np.float64)
    center = np.array([[5.0], [-8.0], [400.0]], dtype=np.float64)
    rvec, _ = cv2.Rodrigues(rotation)
    tvec = -rotation @ center
    return rvec, tvec, center


def test_recover_camera_pose_recovers_known_pose():
    camera_matrix = build_camera_matrix(24.0, 23.5, 15.6, 6000, 4000)
    rvec_true, tvec_true, center_true = _synthetic_pose()
    object_points = [
        (-100.0, -80.0, 5.0), (110.0, -75.0, -3.0),
        (105.0, 90.0, 8.0), (-95.0, 85.0, 0.0),
        (10.0, 5.0, 2.0), (-40.0, 30.0, -6.0),
    ]
    obj = np.array(object_points, dtype=np.float64).reshape(-1, 1, 3)
    dist = np.zeros((5, 1), dtype=np.float64)
    projected, _ = cv2.projectPoints(obj, rvec_true, tvec_true, camera_matrix, dist)
    image_points = [tuple(p) for p in projected.reshape(-1, 2)]

    pose = recover_camera_pose(object_points, image_points, camera_matrix)
    assert pose is not None
    rvec, tvec, error = pose
    assert error < 1.0
    recovered = camera_center_world(rvec, tvec)
    assert recovered[0] == pytest.approx(center_true[0][0], abs=1.0)
    assert recovered[1] == pytest.approx(center_true[1][0], abs=1.0)
    assert recovered[2] == pytest.approx(center_true[2][0], abs=1.0)


def test_recover_camera_pose_rejects_too_few_points():
    camera_matrix = build_camera_matrix(24.0, 23.5, 15.6, 6000, 4000)
    assert recover_camera_pose([(0.0, 0.0, 0.0)], [(0.0, 0.0)], camera_matrix) is None


def test_project_pixel_to_plane_roundtrip():
    camera_matrix = build_camera_matrix(24.0, 23.5, 15.6, 6000, 4000)
    rvec, tvec, _ = _synthetic_pose()
    world_point = np.array([[[40.0, -20.0, 7.0]]], dtype=np.float64)
    dist = np.zeros((5, 1), dtype=np.float64)
    pixel, _ = cv2.projectPoints(world_point, rvec, tvec, camera_matrix, dist)
    u, v = pixel.reshape(2)

    hit = project_pixel_to_plane(rvec, tvec, camera_matrix, u, v, plane_z=7.0)
    assert hit is not None
    assert hit[0] == pytest.approx(40.0, abs=1e-3)
    assert hit[1] == pytest.approx(-20.0, abs=1e-3)
