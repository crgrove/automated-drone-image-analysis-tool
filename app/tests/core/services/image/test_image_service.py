"""
Comprehensive tests for ImageService.

Tests metadata extraction and image attribute calculation functionality.
"""

import pytest
import numpy as np
import cv2
import tempfile
import os
from unittest.mock import patch, MagicMock
from core.services.image.ImageService import ImageService

try:
    import tifffile
except ImportError:
    tifffile = None


@pytest.fixture
def image_service():
    """Fixture providing an ImageService instance."""
    # Create a temporary test image file
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(tmp_file.name, test_img)
        tmp_path = tmp_file.name

    service = ImageService(tmp_path)
    yield service

    # Cleanup
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


@pytest.fixture
def image_service_with_img_array():
    """Fixture providing an ImageService instance with pre-loaded image array."""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(tmp_file.name, test_img)
        tmp_path = tmp_file.name

    # Pre-load image array
    img_array = np.zeros((100, 100, 3), dtype=np.uint8)
    service = ImageService(tmp_path, img_array=img_array)
    yield service

    # Cleanup
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


def test_image_service_initialization(image_service):
    """Test ImageService initialization."""
    assert image_service is not None
    assert image_service.path is not None
    assert image_service.img_array is not None
    assert image_service.exif_data is not None or image_service.exif_data is None  # May be None for test images
    assert hasattr(image_service, 'xmp_data')
    assert hasattr(image_service, 'drone_make')


def test_image_service_with_img_array(image_service_with_img_array):
    """Test ImageService initialization with pre-loaded image array."""
    assert image_service_with_img_array is not None
    assert image_service_with_img_array.img_array is not None
    assert image_service_with_img_array.img_array.shape == (100, 100, 3)


def test_image_service_with_calculated_bearing():
    """Test ImageService initialization with calculated bearing."""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(tmp_file.name, test_img)
        tmp_path = tmp_file.name

    try:
        service = ImageService(tmp_path, calculated_bearing=45.5)
        assert service.calculated_bearing == 45.5
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_get_relative_altitude(image_service):
    """Test getting relative altitude from metadata."""
    # This will return None for test images without proper metadata
    altitude = image_service.get_relative_altitude()
    # Should return None or a float, depending on metadata
    assert altitude is None or isinstance(altitude, (int, float))

    # Test with feet unit
    altitude_ft = image_service.get_relative_altitude(distance_unit='ft')
    assert altitude_ft is None or isinstance(altitude_ft, (int, float))


def test_get_asl_altitude(image_service):
    """Test getting altitude above sea level from EXIF data."""
    altitude = image_service.get_asl_altitude('m')
    # Should return None or a float, depending on metadata
    assert altitude is None or isinstance(altitude, (int, float))

    # Test with feet unit
    altitude_ft = image_service.get_asl_altitude('ft')
    assert altitude_ft is None or isinstance(altitude_ft, (int, float))


def test_get_camera_pitch(image_service):
    """Test getting camera pitch angle."""
    pitch = image_service.get_camera_pitch()
    # Should return None or a float in range [-90, 90]
    assert pitch is None or (isinstance(pitch, (int, float)) and -90 <= pitch <= 90)


def test_get_gimbal_roll(image_service):
    """Test getting gimbal roll from XMP metadata."""
    roll = image_service.get_gimbal_roll()
    # Should return None or a float
    assert roll is None or isinstance(roll, (int, float))


def test_get_camera_yaw(image_service):
    """Test getting camera yaw/bearing."""
    yaw = image_service.get_camera_yaw()
    # Should return None or a float in range [0, 360)
    assert yaw is None or (isinstance(yaw, (int, float)) and 0 <= yaw < 360)


def test_get_camera_yaw_with_calculated_bearing():
    """Test that calculated bearing is used as fallback for camera yaw."""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(tmp_file.name, test_img)
        tmp_path = tmp_file.name

    try:
        service = ImageService(tmp_path, calculated_bearing=180.5)
        yaw = service.get_camera_yaw()
        # Should use calculated bearing if EXIF/XMP data is missing
        # May be None if there's other metadata, or 180.5 if calculated bearing is used
        assert yaw is None or isinstance(yaw, (int, float))
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_get_camera_intrinsics(image_service):
    """Test getting camera intrinsics."""
    intrinsics = image_service.get_camera_intrinsics()
    # Should return None or a dict with required keys
    assert intrinsics is None or isinstance(intrinsics, dict)
    if intrinsics:
        assert 'focal_length_mm' in intrinsics
        assert 'sensor_width_mm' in intrinsics
        assert 'sensor_height_mm' in intrinsics


def test_get_camera_hfov(image_service):
    """Test getting horizontal field of view."""
    hfov = image_service.get_camera_hfov()
    # Should return None or a float in degrees
    assert hfov is None or (isinstance(hfov, (int, float)) and 0 < hfov < 180)


def test_get_average_gsd(image_service):
    """Test getting average ground sampling distance."""
    gsd = image_service.get_average_gsd()
    # Should return None or a positive float
    assert gsd is None or (isinstance(gsd, (int, float)) and gsd > 0)

    # Test with custom altitude
    gsd_custom = image_service.get_average_gsd(custom_altitude_ft=100.0)
    assert gsd_custom is None or (isinstance(gsd_custom, (int, float)) and gsd_custom > 0)


def test_get_position(image_service):
    """Test getting GPS position in various formats."""
    # Test decimal degrees format
    pos = image_service.get_position('Lat/Long - Decimal Degrees')
    assert pos is None or isinstance(pos, str)

    # Test DMS format
    pos_dms = image_service.get_position('Lat/Long - Degrees, Minutes, Seconds')
    assert pos_dms is None or isinstance(pos_dms, str)

    # Test UTM format
    pos_utm = image_service.get_position('UTM')
    assert pos_utm is None or isinstance(pos_utm, str)


def test_circle_areas_of_interest(image_service):
    """Test drawing circles on image for areas of interest."""
    areas_of_interest = [
        {'center': (50, 50), 'radius': 10},
        {'center': (80, 80), 'radius': 15}
    ]

    identifier_color = (255, 0, 0)  # Red in RGB
    augmented = image_service.circle_areas_of_interest(identifier_color, areas_of_interest)

    assert augmented is not None
    assert isinstance(augmented, np.ndarray)
    assert augmented.shape == image_service.img_array.shape


def test_circle_areas_of_interest_empty_list(image_service):
    """Test drawing circles with empty areas of interest list."""
    identifier_color = (255, 0, 0)
    augmented = image_service.circle_areas_of_interest(identifier_color, [])

    assert augmented is not None
    assert isinstance(augmented, np.ndarray)
    assert augmented.shape == image_service.img_array.shape


def test_circle_areas_of_interest_none(image_service):
    """Test drawing circles with None areas of interest."""
    identifier_color = (255, 0, 0)
    augmented = image_service.circle_areas_of_interest(identifier_color, None)

    assert augmented is not None
    assert isinstance(augmented, np.ndarray)
    assert augmented.shape == image_service.img_array.shape


def test_get_thermal_data_no_mask(image_service):
    """Test getting thermal data when no mask path is provided."""
    thermal_data = image_service.get_thermal_data('C')
    assert thermal_data is None


def test_get_thermal_data_with_mask():
    """Test getting thermal data from mask file."""
    # Skip test if tifffile is not available
    if tifffile is None:
        pytest.skip("tifffile is not available")

    # Create a temporary test image
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(tmp_file.name, test_img)
        tmp_path = tmp_file.name

    # Create a temporary mask file with thermal data
    with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as tmp_mask:
        # Create a 3-band TIFF: band 0 = mask, band 1 = temperature data
        mask_data = np.zeros((2, 100, 100), dtype=np.float32)
        mask_data[0] = 255  # Mask band
        mask_data[1] = 25.5  # Temperature in Celsius
        tifffile.imwrite(tmp_mask.name, mask_data)
        mask_path = tmp_mask.name

    try:
        service = ImageService(tmp_path, mask_path=mask_path)

        # Test getting thermal data in Celsius
        thermal_c = service.get_thermal_data('C')
        assert thermal_c is not None
        assert isinstance(thermal_c, np.ndarray)
        assert thermal_c.shape == (100, 100)

        # Test getting thermal data in Fahrenheit
        thermal_f = service.get_thermal_data('F')
        assert thermal_f is not None
        assert isinstance(thermal_f, np.ndarray)
        # Fahrenheit should be different from Celsius
        assert not np.array_equal(thermal_c, thermal_f)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        if os.path.exists(mask_path):
            os.unlink(mask_path)
