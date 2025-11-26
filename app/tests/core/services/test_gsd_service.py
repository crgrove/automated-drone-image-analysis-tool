"""
Comprehensive tests for GSDService.

Tests Ground Sampling Distance calculations.
"""

import pytest
import numpy as np
from core.services.GSDService import GSDService


@pytest.fixture
def gsd_service():
    """Fixture providing a GSDService instance."""
    return GSDService(
        focal_length=24.0,  # 24mm
        image_size=(4000, 3000),  # 4K image
        altitude=100.0,  # 100 meters
        tilt_angle=0.0,  # Nadir
        sensor=(23.5, 15.6)  # APS-C sensor in mm
    )


def test_gsd_service_initialization(gsd_service):
    """Test GSDService initialization."""
    assert gsd_service.focal_length == 0.024  # Converted to meters
    assert gsd_service.image == (4000, 3000)
    assert gsd_service.altitude == 100.0
    assert gsd_service.title_angle == 0.0
    assert gsd_service.principalPoint == (2000.0, 1500.0)  # Image center


def test_gsd_service_custom_principal_point():
    """Test GSDService with custom principal point."""
    service = GSDService(
        focal_length=24.0,
        image_size=(4000, 3000),
        altitude=100.0,
        tilt_angle=0.0,
        sensor=(23.5, 15.6),
        principalPoint=(2000.0, 1500.0)
    )

    # principalPoint is converted from mm to pixels
    # pel_size is calculated from sensor[0] / image_size[0] (same for both x and y)
    # pel_size = (23.5 / 4000) * 1e-3 = 5.875e-6 m
    # principalPoint[0] = (2000.0 * 1e-3) / 5.875e-6 ≈ 340.43
    # principalPoint[1] = (1500.0 * 1e-3) / 5.875e-6 ≈ 255.32
    pel_size = (23.5 / 4000) * 1e-3
    expected_x = (2000.0 * 1e-3) / pel_size
    expected_y = (1500.0 * 1e-3) / pel_size
    assert abs(service.principalPoint[0] - expected_x) < 0.1
    assert abs(service.principalPoint[1] - expected_y) < 0.1


def test_compute_gsd_center(gsd_service):
    """Test GSD calculation at image center."""
    gsd = gsd_service.compute_gsd(1500, 2000)  # Center pixel

    assert gsd > 0
    assert isinstance(gsd, (int, float, np.floating))


def test_compute_gsd_corner(gsd_service):
    """Test GSD calculation at image corner."""
    gsd = gsd_service.compute_gsd(0, 0)  # Top-left corner

    assert gsd > 0


def test_compute_gsd_with_tilt():
    """Test GSD calculation with camera tilt."""
    service = GSDService(
        focal_length=24.0,
        image_size=(4000, 3000),
        altitude=100.0,
        tilt_angle=30.0,  # 30 degree tilt
        sensor=(23.5, 15.6)
    )

    gsd = service.compute_gsd(1500, 2000)
    assert gsd > 0


def test_compute_gsd_for_all_pixels(gsd_service):
    """Test computing GSD for all pixels."""
    gsd_array = gsd_service.compute_gsd_for_all_pixels()

    assert gsd_array.shape == (3000, 4000)
    assert np.all(gsd_array > 0)


def test_compute_average_gsd(gsd_service):
    """Test computing average GSD."""
    avg_gsd = gsd_service.compute_average_gsd()

    assert avg_gsd > 0
    assert isinstance(avg_gsd, (int, float, np.floating))


def test_compute_average_gsd_between_points(gsd_service):
    """Test computing average GSD between two points."""
    avg_gsd = gsd_service.compute_average_gsd_between_points(
        1500, 2000,  # Point 1 (center)
        1000, 1500   # Point 2
    )

    assert avg_gsd > 0


def test_compute_ground_distance(gsd_service):
    """Test computing ground distance between two points."""
    dist_x, dist_y = gsd_service.compute_ground_distance(
        1500, 2000,  # Point 1 (center)
        1000, 1500   # Point 2
    )

    assert dist_x is not None
    assert dist_y is not None
    assert isinstance(dist_x, (int, float, np.floating))
    assert isinstance(dist_y, (int, float, np.floating))
