"""
Comprehensive tests for export services.

Tests KML, PDF, CalTopo, and Zip export functionality.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from core.services.export.KMLGeneratorService import KMLGeneratorService
from core.services.image.ImageService import AltitudeReadings
from helpers.FormatHelper import FormatHelper
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
        mock_aoi_service.get_cached_or_representative_color.return_value = {
            'rgb': (100, 150, 200),
            'hex': '#6496C8',
            'hue_degrees': 210
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
        mock_img_service.get_altitude_readings.return_value = AltitudeReadings(
            value=100.0, reference=FormatHelper.ALTITUDE_REFERENCE_TAKEOFF,
            unit='ft')
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


# --- report metadata formatting ---------------------------------------------
#
# Field report: images without camera intrinsics (every frame cut from a video)
# rendered "AGL: Noneft" and "Estimated Average GSD: Nonecm/px", and a missing
# gimbal yaw fell back to 0, printing "Drone Orientation: 0°" - a real-looking
# due-north heading for an image that reports no heading at all.

from core.services.export.PdfGeneratorService import PdfGeneratorService


@pytest.mark.parametrize('value, unit, expected', [
    (123.4, 'ft', '123.4ft'),
    (0, '°', '0°'),           # a real zero is a reading, not an absence
    (1.99, 'cm/px', '1.99cm/px'),
])
def test_report_value_keeps_real_measurements(value, unit, expected):
    assert PdfGeneratorService._report_value(value, unit) == expected


@pytest.mark.parametrize('unit', ['ft', 'm', '°', 'cm/px'])
def test_report_value_says_na_when_there_is_no_measurement(unit):
    assert PdfGeneratorService._report_value(None, unit) == 'N/A'
    assert PdfGeneratorService._report_value('', unit) == 'N/A'


class TestKmlAltitudeReferenceLabels:
    """A KML is read in Google Earth and CalTopo, with no tooltip to help.

    The description therefore has to say which plane each altitude is
    measured from, and carry the DEM-derived height above the ground being
    flown over beside a takeoff-relative figure. Every one of these cases
    used to export the single word "AGL".
    """

    @staticmethod
    def _descriptions(service, images, readings=None):
        with patch('core.services.export.KMLGeneratorService.ImageService') as MockImageService, \
                patch('core.services.export.KMLGeneratorService.LocationInfo') as MockLocationInfo:
            mock_img_service = MagicMock()
            mock_img_service.exif_data = {}
            mock_img_service.get_altitude_readings.return_value = (
                readings if readings is not None else AltitudeReadings(
                    value=100.0, unit='ft',
                    reference=FormatHelper.ALTITUDE_REFERENCE_TAKEOFF))
            mock_img_service.get_camera_pitch.return_value = -90.0
            mock_img_service.get_camera_yaw.return_value = 0.0
            MockImageService.return_value = mock_img_service

            MockLocationInfo.get_gps.return_value = {
                'latitude': 37.7749, 'longitude': -122.4194,
            }
            service.generate_image_locations_kml(images)
            return ([f.description for f in service.kml.features],
                    mock_img_service)

    def test_dji_altitude_is_labelled_above_takeoff(self, kml_service, sample_images):
        descriptions, _ = self._descriptions(kml_service, sample_images)
        assert "Altitude: 100.0 ft ATO (above the takeoff point)" in descriptions[0]

    def test_the_dem_agl_is_exported_beside_it(self, kml_service, sample_images):
        """The number that describes clearance over the ground flown."""
        descriptions, _ = self._descriptions(kml_service, sample_images, AltitudeReadings(
            value=100.0, unit='ft',
            reference=FormatHelper.ALTITUDE_REFERENCE_TAKEOFF, terrain_agl=71.4))
        assert "Altitude: 71.4 ft AGL (above the terrain, from DEM)" in descriptions[0]
        assert "Altitude: 100.0 ft ATO (above the takeoff point)" in descriptions[0]
        # AGL first for a reader who cannot see the launch point.
        assert (descriptions[0].index("AGL (above the terrain")
                < descriptions[0].index("ATO (above the takeoff"))

    def test_a_terrain_referenced_altitude_is_labelled_agl(self, kml_service, sample_images):
        """WALDO-prepassed imagery really is height above the terrain."""
        descriptions, _ = self._descriptions(kml_service, sample_images, AltitudeReadings(
            value=100.0, unit='ft',
            reference=FormatHelper.ALTITUDE_REFERENCE_TERRAIN))
        assert "Altitude: 100.0 ft AGL (above the terrain)" in descriptions[0]

    def test_an_operator_override_is_labelled_as_entered(self, sample_images):
        """The operator typed a height above the ground being flown over."""
        service = KMLGeneratorService(custom_altitude_ft=250.0)
        descriptions, mock_img = self._descriptions(service, sample_images, AltitudeReadings(
            value=250.0, unit='ft',
            reference=FormatHelper.ALTITUDE_REFERENCE_MANUAL))
        assert "Altitude: 250.0 ft AGL (operator-entered)" in descriptions[0]
        # The override is handed to the service, which decides what it means.
        assert mock_img.get_altitude_readings.call_args.kwargs[
            'custom_altitude_ft'] == 250.0

    def test_the_export_waits_for_the_dem(self, kml_service, sample_images):
        """Unlike the status bar: an export may block for a correct number."""
        _descriptions, mock_img = self._descriptions(kml_service, sample_images)
        assert mock_img.get_altitude_readings.call_args.kwargs[
            'offline_only'] is False

    def test_no_altitude_writes_no_altitude_line(self, kml_service, sample_images):
        descriptions, _ = self._descriptions(
            kml_service, sample_images, AltitudeReadings(value=None, unit='ft'))
        assert "Altitude:" not in descriptions[0]

    def test_the_coordinates_are_untouched(self, kml_service, sample_images):
        """This pass moves labels, never numbers."""
        descriptions, _ = self._descriptions(kml_service, sample_images)
        assert "37.774900, -122.419400" in descriptions[0]


class TestKmlWingtraAltitude:
    """Wingtra imagery carries no altitude of its own; the per-image AGL its
    geotags CSV supplied must reach both the label and the AOI position."""

    @staticmethod
    def _wingtra_images(agl_ft=318.0):
        return [{
            'path': 'W.jpg', 'name': 'W.jpg', 'hidden': False,
            'wingtra_agl_ft': agl_ft,
            'areas_of_interest': [{'center': (10, 10), 'radius': 5, 'area': 50,
                                   'flagged': True}],
        }]

    def test_the_wingtra_agl_is_handed_to_the_altitude_label(self, kml_service):
        _descriptions, mock_img = TestKmlAltitudeReferenceLabels._descriptions(
            kml_service, self._wingtra_images())
        assert mock_img.get_altitude_readings.call_args.kwargs[
            'terrain_agl_ft'] == 318.0

    @staticmethod
    def _aoi_altitude(service, images):
        with patch('core.services.export.KMLGeneratorService.ImageService') as MockImageService, \
                patch('core.services.export.KMLGeneratorService.LocationInfo') as MockLocationInfo, \
                patch('core.services.export.KMLGeneratorService.AOIService') as MockAOIService:
            mock_img_service = MagicMock()
            mock_img_service.exif_data = {}
            mock_img_service.img_array.shape = (200, 200, 3)
            MockImageService.return_value = mock_img_service
            MockLocationInfo.get_gps.return_value = {
                'latitude': 37.7749, 'longitude': -122.4194}
            aoi_service = MagicMock()
            aoi_service.calculate_gps_with_custom_altitude.return_value = (37.775, -122.4195)
            aoi_service.get_cached_or_representative_color.return_value = None
            MockAOIService.return_value = aoi_service

            with tempfile.TemporaryDirectory() as folder:
                service.generate_kml_export(images, os.path.join(folder, 'aois.kml'))
            return aoi_service.calculate_gps_with_custom_altitude.call_args.args[2]

    def test_a_wingtra_aoi_is_positioned_with_its_agl(self, kml_service):
        """The same altitude the GPS map uses, so the export agrees with it."""
        assert self._aoi_altitude(kml_service, self._wingtra_images()) == 318.0

    def test_the_operator_override_still_wins(self):
        service = KMLGeneratorService(custom_altitude_ft=250.0)
        assert self._aoi_altitude(service, self._wingtra_images()) == 250.0

    def test_other_imagery_is_positioned_as_before(self, kml_service):
        assert self._aoi_altitude(kml_service, self._wingtra_images(agl_ft=None)) is None
