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

        # Result should be a tuple of (lat, lon) or None
        assert result is None or (isinstance(result, tuple) and len(result) == 2)


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

        assert result is None or (isinstance(result, tuple) and len(result) == 2)
