"""Tests for ImageService camera-yaw source selection + roll>90 yaw flip.

Covers ImageService.get_camera_yaw_with_source() precedence
(gimbal -> flight -> calculated -> None) and the gimbal-roll inversion
(|roll| > 90 flips the yaw by 180 degrees), plus parity between
get_camera_yaw() and get_camera_yaw_with_source()[0].
"""

import numpy as np
import pytest
from unittest.mock import patch

from core.services.image.ImageService import ImageService

# Patch target: ImageService imports MetaDataHelper into its own module namespace.
_XMP_ATTR = "core.services.image.ImageService.MetaDataHelper.get_drone_xmp_attribute"


def _xmp_side_effect(mapping):
    """Build a get_drone_xmp_attribute(attribute, make, xmp_data) stub.

    Returns mapping[attribute] (or None) so each yaw-source rung can be forced
    independently: 'Gimbal Yaw', 'Flight Yaw', 'Gimbal Roll'.
    """
    def se(attribute, make, xmp_data):
        return mapping.get(attribute)
    return se


@pytest.fixture
def pose_service():
    """An ImageService with no disk/EXIF/XMP reads (all injected)."""
    svc = ImageService(
        "dummy.jpg",
        img_array=np.zeros((60, 80, 3), dtype=np.uint8),
        exif_data={"0th": {}},
        xmp_data={},
    )
    # Force the rungs' guards (xmp_data is not None and drone_make is not None).
    svc.drone_make = "DJI"
    svc.xmp_data = {"present": True}
    svc.calculated_bearing = None
    return svc


# --- source precedence ---------------------------------------------------

def test_gimbal_yaw_wins(pose_service):
    mapping = {"Gimbal Yaw": "137.0", "Flight Yaw": "95.0", "Gimbal Roll": "0.0"}
    with patch(_XMP_ATTR, side_effect=_xmp_side_effect(mapping)):
        yaw, source = pose_service.get_camera_yaw_with_source()
    assert yaw == pytest.approx(137.0)
    assert source == "gimbal"


def test_flight_yaw_when_no_gimbal(pose_service):
    mapping = {"Gimbal Yaw": None, "Flight Yaw": "95.0", "Gimbal Roll": "0.0"}
    with patch(_XMP_ATTR, side_effect=_xmp_side_effect(mapping)):
        yaw, source = pose_service.get_camera_yaw_with_source()
    assert yaw == pytest.approx(95.0)
    assert source == "flight"


def test_calculated_when_no_gimbal_or_flight(pose_service):
    pose_service.calculated_bearing = 210.0
    mapping = {"Gimbal Yaw": None, "Flight Yaw": None, "Gimbal Roll": None}
    with patch(_XMP_ATTR, side_effect=_xmp_side_effect(mapping)):
        yaw, source = pose_service.get_camera_yaw_with_source()
    assert yaw == pytest.approx(210.0)
    assert source == "calculated"


def test_calculated_when_xmp_data_missing(pose_service):
    # xmp_data None / drone_make None short-circuits gimbal + flight rungs.
    pose_service.xmp_data = None
    pose_service.drone_make = None
    pose_service.calculated_bearing = 42.0
    with patch(_XMP_ATTR, side_effect=_xmp_side_effect({})):
        yaw, source = pose_service.get_camera_yaw_with_source()
    assert yaw == pytest.approx(42.0)
    assert source == "calculated"


def test_no_yaw_returns_none_none(pose_service):
    pose_service.calculated_bearing = None
    mapping = {"Gimbal Yaw": None, "Flight Yaw": None, "Gimbal Roll": None}
    with patch(_XMP_ATTR, side_effect=_xmp_side_effect(mapping)):
        result = pose_service.get_camera_yaw_with_source()
    assert result == (None, None)


def test_invalid_gimbal_yaw_falls_through_to_flight(pose_service):
    # A non-floatable gimbal value is swallowed and the flight rung fires.
    mapping = {"Gimbal Yaw": "not-a-number", "Flight Yaw": "60.0", "Gimbal Roll": "0.0"}
    with patch(_XMP_ATTR, side_effect=_xmp_side_effect(mapping)):
        yaw, source = pose_service.get_camera_yaw_with_source()
    assert yaw == pytest.approx(60.0)
    assert source == "flight"


# --- normalization + roll flip ------------------------------------------

def test_negative_yaw_normalized_to_0_360(pose_service):
    mapping = {"Gimbal Yaw": "-30.0", "Gimbal Roll": "0.0"}
    with patch(_XMP_ATTR, side_effect=_xmp_side_effect(mapping)):
        yaw, source = pose_service.get_camera_yaw_with_source()
    assert yaw == pytest.approx(330.0)
    assert source == "gimbal"


def test_roll_over_90_flips_gimbal_yaw(pose_service):
    mapping = {"Gimbal Yaw": "100.0", "Gimbal Roll": "178.0"}
    with patch(_XMP_ATTR, side_effect=_xmp_side_effect(mapping)):
        yaw, source = pose_service.get_camera_yaw_with_source()
    # (100 + 180) % 360 == 280
    assert yaw == pytest.approx(280.0)
    assert source == "gimbal"


def test_roll_over_90_flips_flight_yaw(pose_service):
    mapping = {"Gimbal Yaw": None, "Flight Yaw": "50.0", "Gimbal Roll": "-120.0"}
    with patch(_XMP_ATTR, side_effect=_xmp_side_effect(mapping)):
        yaw, source = pose_service.get_camera_yaw_with_source()
    # |−120| > 90 -> (50 + 180) % 360 == 230; source is still 'flight'.
    assert yaw == pytest.approx(230.0)
    assert source == "flight"


def test_roll_flip_wraps_past_360(pose_service):
    mapping = {"Gimbal Yaw": "300.0", "Gimbal Roll": "180.0"}
    with patch(_XMP_ATTR, side_effect=_xmp_side_effect(mapping)):
        yaw, _ = pose_service.get_camera_yaw_with_source()
    # (300 + 180) % 360 == 120
    assert yaw == pytest.approx(120.0)


def test_roll_at_90_boundary_does_not_flip(pose_service):
    mapping = {"Gimbal Yaw": "100.0", "Gimbal Roll": "90.0"}
    with patch(_XMP_ATTR, side_effect=_xmp_side_effect(mapping)):
        yaw, _ = pose_service.get_camera_yaw_with_source()
    # abs(90) is not > 90 -> no flip.
    assert yaw == pytest.approx(100.0)


def test_roll_just_over_90_flips(pose_service):
    mapping = {"Gimbal Yaw": "100.0", "Gimbal Roll": "90.1"}
    with patch(_XMP_ATTR, side_effect=_xmp_side_effect(mapping)):
        yaw, _ = pose_service.get_camera_yaw_with_source()
    assert yaw == pytest.approx(280.0)


def test_missing_roll_does_not_flip(pose_service):
    # Gimbal Roll absent -> get_gimbal_roll() returns None -> no flip.
    mapping = {"Gimbal Yaw": "100.0", "Gimbal Roll": None}
    with patch(_XMP_ATTR, side_effect=_xmp_side_effect(mapping)):
        yaw, source = pose_service.get_camera_yaw_with_source()
    assert yaw == pytest.approx(100.0)
    assert source == "gimbal"


# --- parity --------------------------------------------------------------

def test_get_camera_yaw_matches_with_source(pose_service):
    mapping = {"Gimbal Yaw": "137.0", "Gimbal Roll": "0.0"}
    with patch(_XMP_ATTR, side_effect=_xmp_side_effect(mapping)):
        assert pose_service.get_camera_yaw() == pose_service.get_camera_yaw_with_source()[0]


def test_get_camera_yaw_none_when_no_source(pose_service):
    pose_service.calculated_bearing = None
    mapping = {"Gimbal Yaw": None, "Flight Yaw": None, "Gimbal Roll": None}
    with patch(_XMP_ATTR, side_effect=_xmp_side_effect(mapping)):
        assert pose_service.get_camera_yaw() is None
