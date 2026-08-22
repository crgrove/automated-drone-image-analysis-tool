"""
Comprehensive tests for AOINeighborService.

Tests for tracking AOIs across neighboring images including:
- GPS coordinate coverage calculation
- GPS to pixel coordinate conversion
- Point-in-image detection
- Thumbnail extraction
- Neighbor image finding
"""

import pytest
import numpy as np
import cv2
import math
from unittest.mock import patch, MagicMock, PropertyMock

from core.services.image.AOINeighborService import AOINeighborService


@pytest.fixture
def aoi_neighbor_service():
    """Create an AOINeighborService instance."""
    return AOINeighborService()


@pytest.fixture
def sample_image():
    """Sample image metadata."""
    return {
        'path': 'test_image.jpg',
        'mask_path': 'test_mask.tif',
        'bearing': 90.0
    }


@pytest.fixture
def sample_images():
    """Sample list of image metadata for neighbor search."""
    return [
        {'path': f'image_{i}.jpg', 'mask_path': '', 'bearing': 90.0}
        for i in range(5)
    ]


@pytest.fixture
def mock_coverage_info():
    """Sample coverage info returned by get_image_coverage_info."""
    mock_service = MagicMock()
    mock_service.img_array = np.zeros((1000, 1500, 3), dtype=np.uint8)

    return {
        'center_lat': 37.7749,
        'center_lon': -122.4194,
        'yaw': 90.0,
        'pitch': -90.0,
        'tilt_angle': 0,
        'altitude': 100.0,
        'width': 1500,
        'height': 1000,
        'focal_mm': 24.0,
        'sensor_w_mm': 23.5,
        'sensor_h_mm': 15.6,
        'image_service': mock_service
    }


# ============================================================================
# Test AOINeighborService Initialization
# ============================================================================

def test_aoi_neighbor_service_initialization():
    """Test AOINeighborService initializes correctly."""
    service = AOINeighborService()
    assert service is not None
    assert service.logger is not None


# ============================================================================
# Test get_image_coverage_info
# ============================================================================

def test_get_image_coverage_info_success(aoi_neighbor_service, sample_image):
    """Test successful coverage info extraction."""
    with patch('core.services.image.AOINeighborService.ImageService') as MockImageService, \
            patch('core.services.image.AOINeighborService.MetaDataHelper') as MockMetaData, \
            patch('core.services.image.AOINeighborService.LocationInfo') as MockLocation:

        # Setup mocks
        MockMetaData.get_exif_data_piexif.return_value = {}
        MockLocation.get_gps.return_value = {'latitude': 37.7749, 'longitude': -122.4194}

        mock_service = MagicMock()
        mock_service.get_camera_yaw.return_value = 90.0
        mock_service.get_camera_pitch.return_value = -90.0
        mock_service.get_gimbal_roll.return_value = None
        mock_service.get_roll_axis_azimuth.return_value = None
        mock_service.get_relative_altitude.return_value = 100.0
        mock_service.get_camera_intrinsics.return_value = {
            'focal_length_mm': 24.0,
            'sensor_width_mm': 23.5,
            'sensor_height_mm': 15.6
        }
        mock_service.img_array = np.zeros((1000, 1500, 3), dtype=np.uint8)
        MockImageService.return_value = mock_service

        result = aoi_neighbor_service.get_image_coverage_info(sample_image)

        assert result is not None
        assert result['center_lat'] == 37.7749
        assert result['center_lon'] == -122.4194
        assert result['yaw'] == 90.0
        assert result['altitude'] == 100.0
        assert result['width'] == 1500
        assert result['height'] == 1000
        assert result['image_service'] is not None


def test_get_image_coverage_info_with_agl_override(aoi_neighbor_service, sample_image):
    """Test coverage info with altitude override."""
    with patch('core.services.image.AOINeighborService.ImageService') as MockImageService, \
            patch('core.services.image.AOINeighborService.MetaDataHelper') as MockMetaData, \
            patch('core.services.image.AOINeighborService.LocationInfo') as MockLocation:

        MockMetaData.get_exif_data_piexif.return_value = {}
        MockLocation.get_gps.return_value = {'latitude': 37.7749, 'longitude': -122.4194}

        mock_service = MagicMock()
        mock_service.get_camera_yaw.return_value = 90.0
        mock_service.get_camera_pitch.return_value = -90.0
        mock_service.get_gimbal_roll.return_value = None
        mock_service.get_roll_axis_azimuth.return_value = None
        mock_service.get_relative_altitude.return_value = 100.0  # Original altitude
        mock_service.get_camera_intrinsics.return_value = {
            'focal_length_mm': 24.0,
            'sensor_width_mm': 23.5,
            'sensor_height_mm': 15.6
        }
        mock_service.img_array = np.zeros((1000, 1500, 3), dtype=np.uint8)
        MockImageService.return_value = mock_service

        result = aoi_neighbor_service.get_image_coverage_info(sample_image, agl_override_m=200.0)

        assert result is not None
        assert result['altitude'] == 200.0  # Should use override


def test_get_image_coverage_info_no_gps(aoi_neighbor_service, sample_image):
    """Test coverage info returns None when GPS is not available."""
    with patch('core.services.image.AOINeighborService.ImageService'), \
            patch('core.services.image.AOINeighborService.MetaDataHelper') as MockMetaData, \
            patch('core.services.image.AOINeighborService.LocationInfo') as MockLocation:

        MockMetaData.get_exif_data_piexif.return_value = {}
        MockLocation.get_gps.return_value = None

        result = aoi_neighbor_service.get_image_coverage_info(sample_image)
        assert result is None


def test_get_image_coverage_info_zero_altitude(aoi_neighbor_service, sample_image):
    """Test coverage info returns None when altitude is zero."""
    with patch('core.services.image.AOINeighborService.ImageService') as MockImageService, \
            patch('core.services.image.AOINeighborService.MetaDataHelper') as MockMetaData, \
            patch('core.services.image.AOINeighborService.LocationInfo') as MockLocation:

        MockMetaData.get_exif_data_piexif.return_value = {}
        MockLocation.get_gps.return_value = {'latitude': 37.7749, 'longitude': -122.4194}

        mock_service = MagicMock()
        mock_service.get_camera_yaw.return_value = 90.0
        mock_service.get_camera_pitch.return_value = -90.0
        mock_service.get_gimbal_roll.return_value = None
        mock_service.get_roll_axis_azimuth.return_value = None
        mock_service.get_relative_altitude.return_value = 0  # Zero altitude
        mock_service.get_camera_intrinsics.return_value = {
            'focal_length_mm': 24.0,
            'sensor_width_mm': 23.5,
            'sensor_height_mm': 15.6
        }
        mock_service.img_array = np.zeros((1000, 1500, 3), dtype=np.uint8)
        MockImageService.return_value = mock_service

        result = aoi_neighbor_service.get_image_coverage_info(sample_image)
        assert result is None


def test_get_image_coverage_info_no_intrinsics(aoi_neighbor_service, sample_image):
    """Test coverage info returns None when camera intrinsics are not available."""
    with patch('core.services.image.AOINeighborService.ImageService') as MockImageService, \
            patch('core.services.image.AOINeighborService.MetaDataHelper') as MockMetaData, \
            patch('core.services.image.AOINeighborService.LocationInfo') as MockLocation:

        MockMetaData.get_exif_data_piexif.return_value = {}
        MockLocation.get_gps.return_value = {'latitude': 37.7749, 'longitude': -122.4194}

        mock_service = MagicMock()
        mock_service.get_camera_yaw.return_value = 90.0
        mock_service.get_camera_pitch.return_value = -90.0
        mock_service.get_gimbal_roll.return_value = None
        mock_service.get_roll_axis_azimuth.return_value = None
        mock_service.get_relative_altitude.return_value = 100.0
        mock_service.get_camera_intrinsics.return_value = None
        mock_service.img_array = np.zeros((1000, 1500, 3), dtype=np.uint8)
        MockImageService.return_value = mock_service

        result = aoi_neighbor_service.get_image_coverage_info(sample_image)
        assert result is None


def test_get_image_coverage_info_default_pitch(aoi_neighbor_service, sample_image):
    """Test coverage info uses default pitch when not available."""
    with patch('core.services.image.AOINeighborService.ImageService') as MockImageService, \
            patch('core.services.image.AOINeighborService.MetaDataHelper') as MockMetaData, \
            patch('core.services.image.AOINeighborService.LocationInfo') as MockLocation:

        MockMetaData.get_exif_data_piexif.return_value = {}
        MockLocation.get_gps.return_value = {'latitude': 37.7749, 'longitude': -122.4194}

        mock_service = MagicMock()
        mock_service.get_camera_yaw.return_value = None  # No yaw
        mock_service.get_camera_pitch.return_value = None  # No pitch
        mock_service.get_gimbal_roll.return_value = None
        mock_service.get_roll_axis_azimuth.return_value = None
        mock_service.get_relative_altitude.return_value = 100.0
        mock_service.get_camera_intrinsics.return_value = {
            'focal_length_mm': 24.0,
            'sensor_width_mm': 23.5,
            'sensor_height_mm': 15.6
        }
        mock_service.img_array = np.zeros((1000, 1500, 3), dtype=np.uint8)
        MockImageService.return_value = mock_service

        result = aoi_neighbor_service.get_image_coverage_info(sample_image)

        assert result is not None
        assert result['yaw'] == 0.0  # Default yaw
        assert result['pitch'] == -90  # Default nadir pitch


# ============================================================================
# Test gps_to_pixel
# ============================================================================

def test_gps_to_pixel_at_center(aoi_neighbor_service, mock_coverage_info):
    """Test GPS to pixel conversion at image center."""
    # The center GPS should project to the center pixel
    result = aoi_neighbor_service.gps_to_pixel(
        mock_coverage_info['center_lat'],
        mock_coverage_info['center_lon'],
        mock_coverage_info
    )

    assert result is not None
    u, v = result
    # Should be close to center
    assert abs(u - mock_coverage_info['width'] / 2) < 1
    assert abs(v - mock_coverage_info['height'] / 2) < 1


def test_gps_to_pixel_offset_point(aoi_neighbor_service, mock_coverage_info):
    """Test GPS to pixel conversion for offset point."""
    # Offset target point slightly
    target_lat = mock_coverage_info['center_lat'] + 0.0001
    target_lon = mock_coverage_info['center_lon'] + 0.0001

    result = aoi_neighbor_service.gps_to_pixel(
        target_lat,
        target_lon,
        mock_coverage_info
    )

    assert result is not None
    u, v = result
    # Should be offset from center
    assert u != mock_coverage_info['width'] / 2 or v != mock_coverage_info['height'] / 2


def test_gps_to_pixel_horizontal_camera_returns_none(aoi_neighbor_service, mock_coverage_info):
    """Test GPS to pixel returns None when camera is horizontal and point is behind it."""
    # Set camera to horizontal pitch pointing North
    coverage = dict(mock_coverage_info)
    coverage['pitch'] = 0  # horizontal
    coverage['yaw'] = 0  # pointing North

    # Target point directly below the drone — a horizontal camera can't see it
    result = aoi_neighbor_service.gps_to_pixel(
        coverage['center_lat'],
        coverage['center_lon'],
        coverage
    )

    assert result is None


# ============================================================================
# Test is_point_in_image
# ============================================================================

def test_is_point_in_image_inside(aoi_neighbor_service):
    """Test point inside image bounds."""
    result = aoi_neighbor_service.is_point_in_image(500, 500, 1000, 800)
    assert result is True


def test_is_point_in_image_at_edge(aoi_neighbor_service):
    """Test point at image edge."""
    # At exact edge (0, 0)
    result = aoi_neighbor_service.is_point_in_image(0, 0, 1000, 800)
    assert result is True

    # Just before max boundary
    result = aoi_neighbor_service.is_point_in_image(999, 799, 1000, 800)
    assert result is True


def test_is_point_in_image_outside(aoi_neighbor_service):
    """Test point outside image bounds."""
    # Negative coordinates
    result = aoi_neighbor_service.is_point_in_image(-1, 500, 1000, 800)
    assert result is False

    # Beyond width
    result = aoi_neighbor_service.is_point_in_image(1000, 500, 1000, 800)
    assert result is False

    # Beyond height
    result = aoi_neighbor_service.is_point_in_image(500, 800, 1000, 800)
    assert result is False


def test_is_point_in_image_with_margin(aoi_neighbor_service):
    """Test point in image with margin."""
    # Point at (50, 50) with margin of 50 - should be at boundary
    result = aoi_neighbor_service.is_point_in_image(50, 50, 1000, 800, margin=50)
    assert result is True

    # Point at (49, 50) with margin of 50 - should be outside
    result = aoi_neighbor_service.is_point_in_image(49, 50, 1000, 800, margin=50)
    assert result is False

    # Point at (950, 750) with margin of 50 - should be at boundary
    result = aoi_neighbor_service.is_point_in_image(949, 749, 1000, 800, margin=50)
    assert result is True


# ============================================================================
# Test _get_image_center_gps
# ============================================================================

def test_get_image_center_gps_success(aoi_neighbor_service, sample_image):
    """Test getting image center GPS coordinates."""
    with patch('core.services.image.AOINeighborService.MetaDataHelper') as MockMetaData, \
            patch('core.services.image.AOINeighborService.LocationInfo') as MockLocation:

        MockMetaData.get_exif_data_piexif.return_value = {}
        MockLocation.get_gps.return_value = {'latitude': 37.7749, 'longitude': -122.4194}

        result = aoi_neighbor_service._get_image_center_gps(sample_image)

        assert result is not None
        assert result == (37.7749, -122.4194)


def test_get_image_center_gps_no_gps(aoi_neighbor_service, sample_image):
    """Test getting image center GPS returns None when not available."""
    with patch('core.services.image.AOINeighborService.MetaDataHelper') as MockMetaData, \
            patch('core.services.image.AOINeighborService.LocationInfo') as MockLocation:

        MockMetaData.get_exif_data_piexif.return_value = {}
        MockLocation.get_gps.return_value = None

        result = aoi_neighbor_service._get_image_center_gps(sample_image)
        assert result is None


def test_get_image_center_gps_exception(aoi_neighbor_service, sample_image):
    """Test getting image center GPS returns None on exception."""
    with patch('core.services.image.AOINeighborService.MetaDataHelper') as MockMetaData:
        MockMetaData.get_exif_data_piexif.side_effect = Exception("Test error")

        result = aoi_neighbor_service._get_image_center_gps(sample_image)
        assert result is None


# ============================================================================
# Test _estimate_max_coverage_radius
# ============================================================================

def test_estimate_max_coverage_radius_success(aoi_neighbor_service, sample_images):
    """Test estimating max coverage radius."""
    with patch.object(aoi_neighbor_service, 'get_image_coverage_info') as mock_coverage, \
            patch('core.services.image.AOINeighborService.GSDService') as MockGSD:

        # Mock coverage info for sampled images
        mock_coverage.return_value = {
            'focal_mm': 24.0,
            'width': 1500,
            'height': 1000,
            'altitude': 100.0,
            'tilt_angle': 0,
            'sensor_w_mm': 23.5,
            'sensor_h_mm': 15.6
        }

        mock_gsd = MagicMock()
        mock_gsd.compute_average_gsd.return_value = 5.0  # 5 cm = 0.05 m per pixel
        MockGSD.return_value = mock_gsd

        result = aoi_neighbor_service._estimate_max_coverage_radius(sample_images)

        # Should return positive value with 20% buffer
        assert result > 0


def test_estimate_max_coverage_radius_no_coverage_info(aoi_neighbor_service, sample_images):
    """Test estimating max coverage radius when coverage info fails."""
    with patch.object(aoi_neighbor_service, 'get_image_coverage_info') as mock_coverage:
        mock_coverage.return_value = None

        result = aoi_neighbor_service._estimate_max_coverage_radius(sample_images)

        # Should return default 500m
        assert result == 500


def test_estimate_max_coverage_radius_empty_images(aoi_neighbor_service):
    """Test estimating max coverage radius with empty image list."""
    result = aoi_neighbor_service._estimate_max_coverage_radius([])

    # Should return default 500m
    assert result == 500


# ============================================================================
# Test extract_thumbnail
# ============================================================================

def test_extract_thumbnail_success(aoi_neighbor_service):
    """Test successful thumbnail extraction."""
    # Create a mock image with a colored region
    mock_service = MagicMock()
    test_img = np.zeros((1000, 1500, 3), dtype=np.uint8)
    test_img[400:600, 700:800] = [255, 128, 64]  # Colored region
    mock_service.img_array = test_img

    thumbnail = aoi_neighbor_service.extract_thumbnail(mock_service, 750, 500, radius=100)

    assert thumbnail is not None
    assert thumbnail.shape[0] > 0
    assert thumbnail.shape[1] > 0


def test_extract_thumbnail_at_edge(aoi_neighbor_service):
    """Test thumbnail extraction near image edge."""
    mock_service = MagicMock()
    test_img = np.zeros((1000, 1500, 3), dtype=np.uint8)
    mock_service.img_array = test_img

    # Extract near corner
    thumbnail = aoi_neighbor_service.extract_thumbnail(mock_service, 50, 50, radius=100)

    assert thumbnail is not None
    # Should be cropped to fit within bounds
    assert thumbnail.shape[0] <= 200
    assert thumbnail.shape[1] <= 200


def test_extract_thumbnail_has_circle_marker(aoi_neighbor_service):
    """Test that extracted thumbnail has center circle marker."""
    mock_service = MagicMock()
    test_img = np.zeros((500, 500, 3), dtype=np.uint8)
    mock_service.img_array = test_img

    thumbnail = aoi_neighbor_service.extract_thumbnail(mock_service, 250, 250, radius=100)

    assert thumbnail is not None
    # Check that some pixels are modified (circle drawn)
    # The circle is drawn in red (255, 0, 0)
    red_pixels = np.sum(thumbnail[:, :, 0] > 200)
    assert red_pixels > 0


def test_uncertainty_ring_is_drawn_at_the_real_error_radius(aoi_neighbor_service):
    """Regression: a 10 px circle asserted precision the projection never had.

    Neighbouring captures disagree about where the same ground object is by
    metres -- mostly a gimbal yaw stamped ~4.5 degrees off the actual heading.
    A tight circle pointed the reviewer confidently at bare ground; a ring at
    the real uncertainty tells them where to search.
    """
    mock_service = MagicMock()
    mock_service.img_array = np.zeros((2000, 2000, 3), dtype=np.uint8)

    thumbnail = aoi_neighbor_service.extract_thumbnail(
        mock_service, 1000, 1000, radius=400, uncertainty_px=224)

    red = np.where((thumbnail[:, :, 0] == 255) & (thumbnail[:, :, 1] == 0))
    assert len(red[0]) > 0, "the marker must be drawn"
    # The ring reaches out to its radius, far beyond the old 10 px circle.
    reach = max(abs(red[0].max() - 400), abs(red[1].max() - 400))
    assert reach > 200, f"ring should reach ~224 px from centre, reached {reach}"


def test_plain_marker_when_the_scale_is_unknown(aoi_neighbor_service):
    """No intrinsics -> no honest radius, so do not invent one."""
    mock_service = MagicMock()
    mock_service.img_array = np.zeros((2000, 2000, 3), dtype=np.uint8)

    thumbnail = aoi_neighbor_service.extract_thumbnail(
        mock_service, 1000, 1000, radius=400, uncertainty_px=None)

    red = np.where((thumbnail[:, :, 0] == 255) & (thumbnail[:, :, 1] == 0))
    reach = max(abs(red[0].max() - 400), abs(red[1].max() - 400))
    assert reach < 20, "expected the small fallback marker"


def test_uncertainty_radius_scales_with_ground_sample_distance(aoi_neighbor_service):
    """The ring means a fixed GROUND distance, so it must scale with altitude."""
    def coverage(altitude):
        return {'focal_mm': 8.8, 'sensor_w_mm': 13.2, 'sensor_h_mm': 8.8,
                'width': 5472, 'height': 3648, 'altitude': altitude,
                'tilt_angle': 0}

    low = aoi_neighbor_service._uncertainty_radius_px(coverage(50.0))
    high = aoi_neighbor_service._uncertainty_radius_px(coverage(100.0))

    assert low is not None and high is not None
    # Twice the altitude -> twice the ground per pixel -> half the pixel radius.
    assert low / high == pytest.approx(2.0, rel=0.02)


def test_uncertainty_radius_is_none_without_intrinsics(aoi_neighbor_service):
    """A manually aligned image can reach here with focal/sensor unset."""
    assert aoi_neighbor_service._uncertainty_radius_px(
        {'focal_mm': None, 'sensor_w_mm': None, 'width': 100, 'height': 100,
         'altitude': 50.0, 'tilt_angle': 0}) is None


def test_extract_thumbnail_invalid_region(aoi_neighbor_service):
    """Test thumbnail extraction with invalid region."""
    mock_service = MagicMock()
    test_img = np.zeros((100, 100, 3), dtype=np.uint8)
    mock_service.img_array = test_img

    # Point outside image
    thumbnail = aoi_neighbor_service.extract_thumbnail(mock_service, 200, 200, radius=10)

    # Should return None for out-of-bounds extraction
    assert thumbnail is None


# ============================================================================
# Test find_aoi_in_neighbors
# ============================================================================

def test_find_aoi_in_neighbors_success(aoi_neighbor_service, sample_images):
    """Test finding AOI in neighboring images."""
    with patch.object(aoi_neighbor_service, '_estimate_max_coverage_radius') as mock_radius, \
            patch.object(aoi_neighbor_service, '_get_image_center_gps') as mock_center, \
            patch.object(aoi_neighbor_service, '_check_image_for_aoi') as mock_check, \
            patch('core.services.image.AOINeighborService.GeodesicHelper') as MockGeodesic:

        mock_radius.return_value = 500  # 500m radius
        mock_center.return_value = (37.7749, -122.4194)

        # All images are within range
        MockGeodesic.haversine_distance.return_value = 50  # 50m away

        # Mock check to return results for some images
        mock_check.side_effect = [
            {'image_idx': 0, 'image_name': 'image_0.jpg', 'thumbnail': np.zeros((100, 100, 3))},
            None,  # Image 1 doesn't contain AOI
            {'image_idx': 2, 'image_name': 'image_2.jpg', 'thumbnail': np.zeros((100, 100, 3))},
            None,
            {'image_idx': 4, 'image_name': 'image_4.jpg', 'thumbnail': np.zeros((100, 100, 3))},
        ]

        results, _truncated = aoi_neighbor_service.find_aoi_in_neighbors(
            images=sample_images,
            current_image_idx=2,
            aoi_gps=(37.7749, -122.4194)
        )

        assert len(results) == 3
        # Results should be sorted by image index
        assert results[0]['image_idx'] == 0
        assert results[1]['image_idx'] == 2
        assert results[2]['image_idx'] == 4


def test_find_aoi_in_neighbors_marks_current(aoi_neighbor_service, sample_images):
    """Test that current image is marked in results."""
    with patch.object(aoi_neighbor_service, '_estimate_max_coverage_radius') as mock_radius, \
            patch.object(aoi_neighbor_service, '_get_image_center_gps') as mock_center, \
            patch.object(aoi_neighbor_service, '_check_image_for_aoi') as mock_check, \
            patch('core.services.image.AOINeighborService.GeodesicHelper') as MockGeodesic:

        mock_radius.return_value = 500
        mock_center.return_value = (37.7749, -122.4194)
        MockGeodesic.haversine_distance.return_value = 50

        mock_check.side_effect = [
            {'image_idx': 0, 'image_name': 'image_0.jpg', 'thumbnail': np.zeros((100, 100, 3)), 'is_current': False},
            {'image_idx': 1, 'image_name': 'image_1.jpg', 'thumbnail': np.zeros((100, 100, 3)), 'is_current': False},
            {'image_idx': 2, 'image_name': 'image_2.jpg', 'thumbnail': np.zeros((100, 100, 3)), 'is_current': False},
            None,
            None,
        ]

        results, _truncated = aoi_neighbor_service.find_aoi_in_neighbors(
            images=sample_images,
            current_image_idx=2,
            aoi_gps=(37.7749, -122.4194)
        )

        # Find the result for current image
        current_result = next((r for r in results if r['image_idx'] == 2), None)
        assert current_result is not None
        assert current_result['is_current'] is True


def test_find_aoi_in_neighbors_with_progress_callback(aoi_neighbor_service, sample_images):
    """Test neighbor search with progress callback."""
    progress_messages = []

    def progress_callback(msg):
        progress_messages.append(msg)

    with patch.object(aoi_neighbor_service, '_estimate_max_coverage_radius') as mock_radius, \
            patch.object(aoi_neighbor_service, '_get_image_center_gps') as mock_center, \
            patch.object(aoi_neighbor_service, '_check_image_for_aoi') as mock_check, \
            patch('core.services.image.AOINeighborService.GeodesicHelper') as MockGeodesic:

        mock_radius.return_value = 500
        mock_center.return_value = (37.7749, -122.4194)
        MockGeodesic.haversine_distance.return_value = 50
        mock_check.return_value = None

        aoi_neighbor_service.find_aoi_in_neighbors(
            images=sample_images,
            current_image_idx=0,
            aoi_gps=(37.7749, -122.4194),
            progress_callback=progress_callback
        )

        assert len(progress_messages) > 0
        assert any("Calculating search area" in msg for msg in progress_messages)


def test_find_aoi_in_neighbors_max_results(aoi_neighbor_service, sample_images):
    """Test that max_results limits the number of results."""
    with patch.object(aoi_neighbor_service, '_estimate_max_coverage_radius') as mock_radius, \
            patch.object(aoi_neighbor_service, '_get_image_center_gps') as mock_center, \
            patch.object(aoi_neighbor_service, '_check_image_for_aoi') as mock_check, \
            patch('core.services.image.AOINeighborService.GeodesicHelper') as MockGeodesic:

        mock_radius.return_value = 500
        mock_center.return_value = (37.7749, -122.4194)
        MockGeodesic.haversine_distance.return_value = 50

        # All images return results
        mock_check.return_value = {
            'image_idx': 0, 'image_name': 'image.jpg',
            'thumbnail': np.zeros((100, 100, 3)), 'is_current': False
        }

        results, _truncated = aoi_neighbor_service.find_aoi_in_neighbors(
            images=sample_images,
            current_image_idx=0,
            aoi_gps=(37.7749, -122.4194),
            max_results=2
        )

        assert len(results) <= 2


def test_find_aoi_in_neighbors_filters_distant_images(aoi_neighbor_service, sample_images):
    """Test that images outside coverage radius are filtered."""
    with patch.object(aoi_neighbor_service, '_estimate_max_coverage_radius') as mock_radius, \
            patch.object(aoi_neighbor_service, '_get_image_center_gps') as mock_center, \
            patch.object(aoi_neighbor_service, '_check_image_for_aoi') as mock_check, \
            patch('core.services.image.AOINeighborService.GeodesicHelper') as MockGeodesic:

        mock_radius.return_value = 100  # 100m radius
        mock_center.return_value = (37.7749, -122.4194)

        # Some images are far away
        MockGeodesic.haversine_distance.side_effect = [50, 200, 50, 300, 50]

        mock_check.return_value = {
            'image_idx': 0, 'image_name': 'image.jpg',
            'thumbnail': np.zeros((100, 100, 3)), 'is_current': False
        }

        aoi_neighbor_service.find_aoi_in_neighbors(
            images=sample_images,
            current_image_idx=0,
            aoi_gps=(37.7749, -122.4194)
        )

        # Only 3 images should be checked (those within 100m)
        assert mock_check.call_count == 3


# ============================================================================
# Test _check_image_for_aoi
# ============================================================================

def test_check_image_for_aoi_success(aoi_neighbor_service, sample_image):
    """Test checking if AOI is in image - success case."""
    with patch.object(aoi_neighbor_service, 'get_image_coverage_info') as mock_coverage, \
            patch.object(aoi_neighbor_service, 'gps_to_pixel') as mock_gps2pixel, \
            patch.object(aoi_neighbor_service, 'is_point_in_image') as mock_in_image, \
            patch.object(aoi_neighbor_service, 'extract_thumbnail') as mock_thumbnail, \
            patch('core.services.image.AOINeighborService.ImageService') as MockImageService:

        # The shape get_image_coverage_info actually returns: altitude and the
        # camera centre are read on the way to a terrain-consistent AGL.
        mock_coverage.return_value = {
            'width': 1500, 'height': 1000, 'altitude': 100.0,
            'center_lat': 37.7749, 'center_lon': -122.4194,
        }
        mock_gps2pixel.return_value = (750, 500)
        mock_in_image.return_value = True
        mock_thumbnail.return_value = np.zeros((200, 200, 3), dtype=np.uint8)

        result = aoi_neighbor_service._check_image_for_aoi(
            sample_image, 0, 37.7749, -122.4194, thumbnail_radius=100
        )

        assert result is not None
        assert result['image_idx'] == 0
        assert result['pixel_x'] == 750
        assert result['pixel_y'] == 500
        assert result['is_current'] is False
        # Coverage was tested metadata-only; the decode happened for the
        # confirmed hit, at thumbnail time
        mock_coverage.assert_called_once_with(sample_image, None, include_service=False)
        MockImageService.assert_called_once()


def test_check_image_rejected_candidate_never_decodes(aoi_neighbor_service, sample_image):
    """A candidate that fails the bounds check must not have its pixels decoded."""
    with patch.object(aoi_neighbor_service, 'get_image_coverage_info') as mock_coverage, \
            patch.object(aoi_neighbor_service, 'gps_to_pixel') as mock_gps2pixel, \
            patch.object(aoi_neighbor_service, 'is_point_in_image') as mock_in_image, \
            patch('core.services.image.AOINeighborService.ImageService') as MockImageService:

        # The shape get_image_coverage_info actually returns: altitude and the
        # camera centre are read on the way to a terrain-consistent AGL.
        mock_coverage.return_value = {
            'width': 1500, 'height': 1000, 'altitude': 100.0,
            'center_lat': 37.7749, 'center_lon': -122.4194,
        }
        mock_gps2pixel.return_value = (5000, 5000)
        mock_in_image.return_value = False

        result = aoi_neighbor_service._check_image_for_aoi(
            sample_image, 0, 37.7749, -122.4194, thumbnail_radius=100
        )

        assert result is None
        MockImageService.assert_not_called()


def test_check_image_for_aoi_no_coverage(aoi_neighbor_service, sample_image):
    """Test checking image when coverage info is not available."""
    with patch.object(aoi_neighbor_service, 'get_image_coverage_info') as mock_coverage:
        mock_coverage.return_value = None

        result = aoi_neighbor_service._check_image_for_aoi(
            sample_image, 0, 37.7749, -122.4194
        )

        assert result is None


def test_check_image_for_aoi_gps_conversion_fails(aoi_neighbor_service, sample_image):
    """Test checking image when GPS to pixel conversion fails."""
    with patch.object(aoi_neighbor_service, 'get_image_coverage_info') as mock_coverage, \
            patch.object(aoi_neighbor_service, 'gps_to_pixel') as mock_gps2pixel:

        # The shape get_image_coverage_info actually returns: altitude and the
        # camera centre are read on the way to a terrain-consistent AGL.
        mock_coverage.return_value = {
            'width': 1500, 'height': 1000, 'altitude': 100.0,
            'center_lat': 37.7749, 'center_lon': -122.4194,
        }
        mock_gps2pixel.return_value = None

        result = aoi_neighbor_service._check_image_for_aoi(
            sample_image, 0, 37.7749, -122.4194
        )

        assert result is None


def test_check_image_for_aoi_point_outside(aoi_neighbor_service, sample_image):
    """Test checking image when point is outside bounds."""
    with patch.object(aoi_neighbor_service, 'get_image_coverage_info') as mock_coverage, \
            patch.object(aoi_neighbor_service, 'gps_to_pixel') as mock_gps2pixel, \
            patch.object(aoi_neighbor_service, 'is_point_in_image') as mock_in_image:

        # The shape get_image_coverage_info actually returns: altitude and the
        # camera centre are read on the way to a terrain-consistent AGL.
        mock_coverage.return_value = {
            'width': 1500, 'height': 1000, 'altitude': 100.0,
            'center_lat': 37.7749, 'center_lon': -122.4194,
        }
        mock_gps2pixel.return_value = (2000, 500)  # Outside image
        mock_in_image.return_value = False

        result = aoi_neighbor_service._check_image_for_aoi(
            sample_image, 0, 37.7749, -122.4194
        )

        assert result is None


def test_check_image_for_aoi_thumbnail_extraction_fails(aoi_neighbor_service, sample_image):
    """Test checking image when thumbnail extraction fails."""
    with patch.object(aoi_neighbor_service, 'get_image_coverage_info') as mock_coverage, \
            patch.object(aoi_neighbor_service, 'gps_to_pixel') as mock_gps2pixel, \
            patch.object(aoi_neighbor_service, 'is_point_in_image') as mock_in_image, \
            patch.object(aoi_neighbor_service, 'extract_thumbnail') as mock_thumbnail:

        mock_service = MagicMock()
        mock_coverage.return_value = {
            'width': 1500, 'height': 1000,
            'image_service': mock_service
        }
        mock_gps2pixel.return_value = (750, 500)
        mock_in_image.return_value = True
        mock_thumbnail.return_value = None

        result = aoi_neighbor_service._check_image_for_aoi(
            sample_image, 0, 37.7749, -122.4194
        )

        assert result is None


# ============================================================================
# Test metadata caching (repeated searches must not re-read metadata per image)
# ============================================================================

def _patch_coverage_metadata(exif_calls):
    """Patch the metadata stack behind get_image_coverage_info."""
    module = 'core.services.image.AOINeighborService'

    def counted_exif(path):
        exif_calls.append(path)
        return {}

    mock_service = MagicMock()
    mock_service.get_camera_yaw.return_value = 90.0
    mock_service.get_camera_pitch.return_value = -90.0
    mock_service.get_gimbal_roll.return_value = None
    mock_service.get_roll_axis_azimuth.return_value = None
    mock_service.get_relative_altitude.return_value = 100.0
    mock_service.get_camera_intrinsics.return_value = {
        'focal_length_mm': 24.0,
        'sensor_width_mm': 23.5,
        'sensor_height_mm': 15.6
    }
    mock_service.img_array = np.zeros((1000, 1500, 3), dtype=np.uint8)

    meta = patch(f'{module}.MetaDataHelper')
    loc = patch(f'{module}.LocationInfo')
    svc = patch(f'{module}.ImageService', return_value=mock_service)
    return meta, loc, svc, counted_exif


def test_coverage_info_is_cached_across_calls(aoi_neighbor_service, sample_image):
    """The second lookup for the same image must not re-read its metadata."""
    exif_calls = []
    meta, loc, svc, counted_exif = _patch_coverage_metadata(exif_calls)
    with meta as MockMeta, loc as MockLoc, svc:
        MockMeta.get_exif_data_piexif.side_effect = counted_exif
        MockLoc.get_gps.return_value = {'latitude': 37.7749, 'longitude': -122.4194}

        first = aoi_neighbor_service.get_image_coverage_info(sample_image, include_service=False)
        second = aoi_neighbor_service.get_image_coverage_info(sample_image, include_service=False)

        assert first is not None
        assert second is not None
        assert len(exif_calls) == 1


def test_cached_coverage_returns_a_mutation_safe_copy(aoi_neighbor_service, sample_image):
    """Callers mutate coverage (terrain altitude adjustment); the cache must not see it."""
    exif_calls = []
    meta, loc, svc, counted_exif = _patch_coverage_metadata(exif_calls)
    with meta as MockMeta, loc as MockLoc, svc:
        MockMeta.get_exif_data_piexif.side_effect = counted_exif
        MockLoc.get_gps.return_value = {'latitude': 37.7749, 'longitude': -122.4194}

        first = aoi_neighbor_service.get_image_coverage_info(sample_image, include_service=False)
        first['altitude'] = -1.0

        second = aoi_neighbor_service.get_image_coverage_info(sample_image, include_service=False)
        assert second['altitude'] == 100.0


def test_coverage_cache_invalidated_by_alignment_change(aoi_neighbor_service, sample_image):
    """A new FOV alignment (Align Image tool) must invalidate the cached coverage."""
    exif_calls = []
    meta, loc, svc, counted_exif = _patch_coverage_metadata(exif_calls)
    with meta as MockMeta, loc as MockLoc, svc:
        MockMeta.get_exif_data_piexif.side_effect = counted_exif
        MockLoc.get_gps.return_value = {'latitude': 37.7749, 'longitude': -122.4194}

        aoi_neighbor_service.get_image_coverage_info(sample_image, include_service=False)
        sample_image['fov_alignment'] = {'corners': None}  # alignment changed
        aoi_neighbor_service.get_image_coverage_info(sample_image, include_service=False)

        assert len(exif_calls) == 2


def test_negative_coverage_result_is_cached(aoi_neighbor_service, sample_image):
    """GPS-less images are also remembered, not re-read every search."""
    exif_calls = []
    meta, loc, svc, counted_exif = _patch_coverage_metadata(exif_calls)
    with meta as MockMeta, loc as MockLoc, svc:
        MockMeta.get_exif_data_piexif.side_effect = counted_exif
        MockLoc.get_gps.return_value = None

        assert aoi_neighbor_service.get_image_coverage_info(sample_image, include_service=False) is None
        assert aoi_neighbor_service.get_image_coverage_info(sample_image, include_service=False) is None
        assert len(exif_calls) == 1


def test_center_gps_is_cached(aoi_neighbor_service, sample_image):
    """Center-GPS lookups are one EXIF read per image per session, not per search."""
    module = 'core.services.image.AOINeighborService'
    with patch(f'{module}.MetaDataHelper') as MockMeta,             patch(f'{module}.LocationInfo') as MockLoc:
        MockMeta.get_exif_data_piexif.return_value = {}
        MockLoc.get_gps.return_value = {'latitude': 1.0, 'longitude': 2.0}

        first = aoi_neighbor_service._get_image_center_gps(sample_image)
        second = aoi_neighbor_service._get_image_center_gps(sample_image)

        assert first == (1.0, 2.0)
        assert second == (1.0, 2.0)
        MockMeta.get_exif_data_piexif.assert_called_once()


def test_get_image_dimensions_reads_header_only(aoi_neighbor_service, tmp_path):
    """Dimensions come from the file header, matching the stored (unrotated) size."""
    from PIL import Image as PILImage
    path = tmp_path / 'header_test.jpg'
    PILImage.new('RGB', (640, 480), (10, 10, 10)).save(path)

    assert aoi_neighbor_service._get_image_dimensions(str(path)) == (640, 480)
    assert aoi_neighbor_service._get_image_dimensions(str(tmp_path / 'missing.jpg')) is None
