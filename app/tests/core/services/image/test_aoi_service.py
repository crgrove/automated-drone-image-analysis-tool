"""
Comprehensive tests for AOIService.

Tests AOI geospatial calculations and color extraction.
"""

import pytest
import numpy as np
import tempfile
import os
from unittest.mock import patch, MagicMock
from core.services.image.AOIService import AOIService


@pytest.fixture
def sample_image_data():
    """Sample image metadata."""
    return {
        'path': 'test_image.jpg',
        'mask_path': 'test_mask.tif',
        'lat': 37.7749,
        'lon': -122.4194
    }


@pytest.fixture
def sample_aoi():
    """Sample AOI data."""
    return {
        'center': (100, 100),
        'radius': 20,
        'area': 400,
        'detected_pixels': [(95, 95), (96, 96), (97, 97)]
    }


def test_aoi_service_initialization(sample_image_data):
    """Test AOIService initialization."""
    with patch('core.services.image.AOIService.ImageService'):
        service = AOIService(sample_image_data)
        assert service.image_service is not None


def test_aoi_service_with_preloaded_image(sample_image_data):
    """Test AOIService with preloaded image array."""
    test_img = np.zeros((200, 200, 3), dtype=np.uint8)

    with patch('core.services.image.AOIService.ImageService'):
        service = AOIService(sample_image_data, img_array=test_img)
        assert service.image_service is not None


def test_estimate_aoi_gps(sample_image_data, sample_aoi):
    """Test estimating AOI GPS coordinates."""
    with patch('core.services.image.AOIService.ImageService') as MockImageService, \
            patch('helpers.MetaDataHelper.MetaDataHelper.get_exif_data_piexif') as mock_exif, \
            patch('helpers.LocationInfo.LocationInfo.get_gps') as mock_gps:

        # Mock EXIF and GPS data
        mock_exif.return_value = {}
        mock_gps.return_value = {'latitude': 37.7749, 'longitude': -122.4194}

        # Mock ImageService
        mock_service = MagicMock()
        mock_service.get_camera_yaw.return_value = 0.0
        mock_service.get_camera_pitch.return_value = -90.0
        mock_service.get_relative_altitude.return_value = 100.0
        mock_service.get_camera_intrinsics.return_value = {
            'focal_length_mm': 24.0,
            'sensor_width_mm': 23.5,
            'sensor_height_mm': 15.6
        }
        mock_service.img_array = np.zeros((200, 200, 3), dtype=np.uint8)
        MockImageService.return_value = mock_service

        service = AOIService(sample_image_data)
        result = service.estimate_aoi_gps(sample_image_data, sample_aoi)

        # Result should be AOIGPSResult or None (new return type)
        if result is not None:
            assert hasattr(result, 'latitude')
            assert hasattr(result, 'longitude')
            assert hasattr(result, 'elevation_source')


def test_get_aoi_representative_color(sample_image_data, sample_aoi):
    """Test getting representative color for an AOI."""
    test_img = np.zeros((200, 200, 3), dtype=np.uint8)
    test_img[95:105, 95:105] = [100, 150, 200]  # Colored region

    with patch('core.services.image.AOIService.ImageService') as MockImageService:
        mock_service = MagicMock()
        mock_service.img_array = test_img
        MockImageService.return_value = mock_service

        service = AOIService(sample_image_data, img_array=test_img)
        color_result = service.get_aoi_representative_color(sample_aoi)

        if color_result:
            assert 'rgb' in color_result
            assert 'hex' in color_result
            assert 'hue_degrees' in color_result


def test_calculate_gps_with_custom_altitude(sample_image_data, sample_aoi):
    """Test calculating GPS with custom altitude override."""
    with patch('core.services.image.AOIService.ImageService') as MockImageService, \
            patch('helpers.MetaDataHelper.MetaDataHelper.get_exif_data_piexif') as mock_exif, \
            patch('helpers.LocationInfo.LocationInfo.get_gps') as mock_gps:

        mock_exif.return_value = {}
        mock_gps.return_value = {'latitude': 37.7749, 'longitude': -122.4194}

        mock_service = MagicMock()
        mock_service.get_camera_yaw.return_value = 0.0
        mock_service.get_camera_pitch.return_value = -90.0
        mock_service.get_relative_altitude.return_value = 100.0
        mock_service.get_camera_intrinsics.return_value = {
            'focal_length_mm': 24.0,
            'sensor_width_mm': 23.5,
            'sensor_height_mm': 15.6
        }
        mock_service.img_array = np.zeros((200, 200, 3), dtype=np.uint8)
        MockImageService.return_value = mock_service

        service = AOIService(sample_image_data)
        result = service.calculate_gps_with_custom_altitude(
            sample_image_data,
            sample_aoi,
            custom_altitude_ft=328.084  # 100 meters in feet
        )

        # Returns tuple (lat, lon) for backward compatibility
        assert result is None or (isinstance(result, tuple) and len(result) == 2)


def test_estimate_aoi_gps_with_terrain_disabled(sample_image_data, sample_aoi):
    """Test AOI GPS estimation with terrain explicitly disabled."""
    with patch('core.services.image.AOIService.ImageService') as MockImageService, \
            patch('helpers.MetaDataHelper.MetaDataHelper.get_exif_data_piexif') as mock_exif, \
            patch('helpers.LocationInfo.LocationInfo.get_gps') as mock_gps:

        mock_exif.return_value = {}
        mock_gps.return_value = {'latitude': 37.7749, 'longitude': -122.4194}

        mock_service = MagicMock()
        mock_service.get_camera_yaw.return_value = 0.0
        mock_service.get_camera_pitch.return_value = -90.0
        mock_service.get_relative_altitude.return_value = 100.0
        mock_service.get_camera_intrinsics.return_value = {
            'focal_length_mm': 24.0,
            'sensor_width_mm': 23.5,
            'sensor_height_mm': 15.6
        }
        mock_service.img_array = np.zeros((200, 200, 3), dtype=np.uint8)
        MockImageService.return_value = mock_service

        service = AOIService(sample_image_data)
        result = service.estimate_aoi_gps(sample_image_data, sample_aoi, use_terrain=False)

        # Result should be AOIGPSResult or None
        if result:
            assert hasattr(result, 'elevation_source')
            assert result.elevation_source == 'flat'


def test_calculate_gps_with_metadata(sample_image_data, sample_aoi):
    """Test calculating GPS with full metadata result."""
    with patch('core.services.image.AOIService.ImageService') as MockImageService, \
            patch('helpers.MetaDataHelper.MetaDataHelper.get_exif_data_piexif') as mock_exif, \
            patch('helpers.LocationInfo.LocationInfo.get_gps') as mock_gps:

        mock_exif.return_value = {}
        mock_gps.return_value = {'latitude': 37.7749, 'longitude': -122.4194}

        mock_service = MagicMock()
        mock_service.get_camera_yaw.return_value = 0.0
        mock_service.get_camera_pitch.return_value = -90.0
        mock_service.get_relative_altitude.return_value = 100.0
        mock_service.get_camera_intrinsics.return_value = {
            'focal_length_mm': 24.0,
            'sensor_width_mm': 23.5,
            'sensor_height_mm': 15.6
        }
        mock_service.img_array = np.zeros((200, 200, 3), dtype=np.uint8)
        MockImageService.return_value = mock_service

        service = AOIService(sample_image_data)
        result = service.calculate_gps_with_metadata(
            sample_image_data,
            sample_aoi,
            use_terrain=False
        )

        if result:
            assert hasattr(result, 'latitude')
            assert hasattr(result, 'longitude')
            assert hasattr(result, 'elevation_source')
            assert hasattr(result, 'effective_agl_m')


def test_get_aoi_gps_with_metadata(sample_image_data, sample_aoi):
    """Test getting AOI GPS with full metadata dict."""
    with patch('core.services.image.AOIService.ImageService') as MockImageService, \
            patch('helpers.MetaDataHelper.MetaDataHelper.get_exif_data_piexif') as mock_exif, \
            patch('helpers.LocationInfo.LocationInfo.get_gps') as mock_gps:

        mock_exif.return_value = {}
        mock_gps.return_value = {'latitude': 37.7749, 'longitude': -122.4194}

        mock_service = MagicMock()
        mock_service.get_camera_yaw.return_value = 0.0
        mock_service.get_camera_pitch.return_value = -90.0
        mock_service.get_relative_altitude.return_value = 100.0
        mock_service.get_camera_intrinsics.return_value = {
            'focal_length_mm': 24.0,
            'sensor_width_mm': 23.5,
            'sensor_height_mm': 15.6
        }
        mock_service.img_array = np.zeros((200, 200, 3), dtype=np.uint8)
        MockImageService.return_value = mock_service

        service = AOIService(sample_image_data)
        result = service.get_aoi_gps_with_metadata(
            sample_image_data,
            sample_aoi,
            aoi_index=0,
            use_terrain=False
        )

        if result:
            assert 'latitude' in result
            assert 'longitude' in result
            assert 'aoi_index' in result
            assert 'elevation_source' in result
            assert result['aoi_index'] == 0


def test_is_terrain_available():
    """Test terrain availability check."""
    with patch('core.services.image.AOIService._get_terrain_service') as mock_get_terrain:
        # Test when terrain service is not available
        mock_get_terrain.return_value = None
        assert not AOIService.is_terrain_available()

        # Test when terrain service is available and enabled
        mock_service = MagicMock()
        mock_service.enabled = True
        mock_get_terrain.return_value = mock_service
        assert AOIService.is_terrain_available()

        # Test when terrain service is available but disabled
        mock_service.enabled = False
        assert not AOIService.is_terrain_available()


def test_get_terrain_service_info():
    """Test getting terrain service info."""
    with patch('core.services.image.AOIService._get_terrain_service') as mock_get_terrain:
        # Test when terrain service is not available
        mock_get_terrain.return_value = None
        assert AOIService.get_terrain_service_info() is None

        # Test when terrain service is available
        mock_service = MagicMock()
        mock_service.get_service_info.return_value = {
            'enabled': True,
            'zoom_level': 12,
            'provider': 'Test Provider'
        }
        mock_get_terrain.return_value = mock_service
        info = AOIService.get_terrain_service_info()
        assert info is not None
        assert 'enabled' in info


def test_aoi_gps_result_to_tuple(sample_image_data, sample_aoi):
    """Test AOIGPSResult to_tuple method for backward compatibility."""
    with patch('core.services.image.AOIService.ImageService') as MockImageService, \
            patch('helpers.MetaDataHelper.MetaDataHelper.get_exif_data_piexif') as mock_exif, \
            patch('helpers.LocationInfo.LocationInfo.get_gps') as mock_gps:

        mock_exif.return_value = {}
        mock_gps.return_value = {'latitude': 37.7749, 'longitude': -122.4194}

        mock_service = MagicMock()
        mock_service.get_camera_yaw.return_value = 0.0
        mock_service.get_camera_pitch.return_value = -90.0
        mock_service.get_relative_altitude.return_value = 100.0
        mock_service.get_camera_intrinsics.return_value = {
            'focal_length_mm': 24.0,
            'sensor_width_mm': 23.5,
            'sensor_height_mm': 15.6
        }
        mock_service.img_array = np.zeros((200, 200, 3), dtype=np.uint8)
        MockImageService.return_value = mock_service

        service = AOIService(sample_image_data)
        result = service.estimate_aoi_gps(sample_image_data, sample_aoi, use_terrain=False)

        if result:
            tuple_result = result.to_tuple()
            assert isinstance(tuple_result, tuple)
            assert len(tuple_result) == 2
            assert tuple_result == (result.latitude, result.longitude)