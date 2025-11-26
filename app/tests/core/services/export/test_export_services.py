"""
Comprehensive tests for export services.

Tests KML, PDF, CalTopo, and Zip export functionality.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from core.services.export.KMLGeneratorService import KMLGeneratorService
from core.services.export.ZipBundleService import ZipBundleService


@pytest.fixture
def kml_service():
    """Fixture providing a KMLGeneratorService instance."""
    return KMLGeneratorService()


@pytest.fixture
def sample_images():
    """Sample image data for testing."""
    return [
        {
            'path': 'test1.jpg',
            'name': 'test1.jpg',
            'lat': 37.7749,
            'lon': -122.4194,
            'areas_of_interest': [
                {
                    'center': (100, 100),
                    'radius': 20,
                    'area': 400,
                    'flagged': True
                }
            ],
            'hidden': False
        }
    ]


def test_kml_service_initialization(kml_service):
    """Test KMLGeneratorService initialization."""
    assert kml_service.kml is not None
    assert kml_service.custom_altitude_ft is None


def test_kml_service_custom_altitude():
    """Test KMLGeneratorService with custom altitude."""
    service = KMLGeneratorService(custom_altitude_ft=328.084)
    assert service.custom_altitude_ft == 328.084


def test_add_aoi_placemark(kml_service):
    """Test adding an AOI placemark to KML."""
    kml_service.add_aoi_placemark(
        name="Test AOI",
        lat=37.7749,
        lon=-122.4194,
        description="Test description",
        color_rgb=(255, 0, 0)
    )

    # Verify placemark was added
    assert len(kml_service.kml.features) > 0


def test_add_image_location_placemark(kml_service):
    """Test adding an image location placemark to KML."""
    kml_service.add_image_location_placemark(
        name="Test Image",
        lat=37.7749,
        lon=-122.4194,
        description="Test image location"
    )

    # Verify placemark was added
    assert len(kml_service.kml.features) > 0


def test_save_kml(kml_service):
    """Test saving KML to file."""
    with tempfile.NamedTemporaryFile(suffix='.kml', delete=False) as tmp_file:
        kml_path = tmp_file.name

    try:
        kml_service.add_aoi_placemark("Test", 37.7749, -122.4194, "Test")
        kml_service.save_kml(kml_path)

        assert os.path.exists(kml_path)
    finally:
        if os.path.exists(kml_path):
            os.remove(kml_path)


def test_generate_kml_export_mock(kml_service, sample_images):
    """Test generating KML export with mocked dependencies."""
    with patch('core.services.export.KMLGeneratorService.ImageService') as MockImageService, \
            patch('core.services.export.KMLGeneratorService.LocationInfo') as MockLocationInfo, \
            patch('core.services.export.KMLGeneratorService.AOIService') as MockAOIService:

        # Mock ImageService
        mock_img_service = MagicMock()
        mock_img_service.exif_data = {}
        mock_img_service.img_array = MagicMock()
        mock_img_service.img_array.shape = (200, 200, 3)
        MockImageService.return_value = mock_img_service

        # Mock LocationInfo
        MockLocationInfo.get_gps.return_value = {
            'latitude': 37.7749,
            'longitude': -122.4194
        }

        # Mock AOIService
        mock_aoi_service = MagicMock()
        mock_aoi_service.calculate_gps_with_custom_altitude.return_value = (37.7750, -122.4195)
        mock_aoi_service.get_aoi_representative_color.return_value = {
            'rgb': (100, 150, 200),
            'hex': '#6496C8',
            'hue_degrees': 210.0
        }
        MockAOIService.return_value = mock_aoi_service

        with tempfile.NamedTemporaryFile(suffix='.kml', delete=False) as tmp_file:
            kml_path = tmp_file.name

        try:
            kml_service.generate_kml_export(sample_images, kml_path)
            assert os.path.exists(kml_path)
        finally:
            if os.path.exists(kml_path):
                os.remove(kml_path)


def test_generate_image_locations_kml(kml_service, sample_images):
    """Test generating KML with image locations."""
    with patch('core.services.export.KMLGeneratorService.ImageService') as MockImageService, \
            patch('core.services.export.KMLGeneratorService.LocationInfo') as MockLocationInfo:

        mock_img_service = MagicMock()
        mock_img_service.exif_data = {}
        mock_img_service.get_relative_altitude.return_value = 100.0
        mock_img_service.get_camera_pitch.return_value = -90.0
        mock_img_service.get_camera_yaw.return_value = 0.0
        MockImageService.return_value = mock_img_service

        MockLocationInfo.get_gps.return_value = {
            'latitude': 37.7749,
            'longitude': -122.4194
        }

        kml_service.generate_image_locations_kml(sample_images)

        # Verify placemarks were added
        assert len(kml_service.kml.features) > 0


def test_generate_coverage_extent_kml(kml_service):
    """Test generating coverage extent KML."""
    coverage_data = {
        'polygons': [
            {
                'coordinates': [
                    (37.7749, -122.4194),
                    (37.7750, -122.4194),
                    (37.7750, -122.4195),
                    (37.7749, -122.4195)
                ],
                'area_sqm': 10000.0
            }
        ],
        'image_count': 1,
        'total_area_sqm': 10000.0
    }

    with tempfile.NamedTemporaryFile(suffix='.kml', delete=False) as tmp_file:
        kml_path = tmp_file.name

    try:
        kml_service.generate_coverage_extent_kml(coverage_data, kml_path)
        assert os.path.exists(kml_path)
    finally:
        if os.path.exists(kml_path):
            os.remove(kml_path)


def test_zip_bundle_service_initialization():
    """Test ZipBundleService initialization."""
    service = ZipBundleService()
    assert service is not None


def test_generate_zip_file():
    """Test generating a zip file."""
    service = ZipBundleService()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        test_file1 = os.path.join(tmpdir, 'test1.txt')
        test_file2 = os.path.join(tmpdir, 'test2.txt')
        with open(test_file1, 'w') as f:
            f.write('test1')
        with open(test_file2, 'w') as f:
            f.write('test2')

        zip_path = os.path.join(tmpdir, 'test.zip')
        service.generate_zip_file([test_file1, test_file2], zip_path)

        assert os.path.exists(zip_path)
