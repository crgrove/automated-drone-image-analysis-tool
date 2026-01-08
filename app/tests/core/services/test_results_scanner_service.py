"""
Comprehensive tests for ResultsScannerService.

Tests for scanning folders for ADIAT result files including:
- Directory counting
- Recursive folder scanning
- XML file parsing
- GPS extraction
- Data class handling
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, PropertyMock
from dataclasses import asdict

from core.services.ResultsScannerService import ResultsScannerService, ResultsScanResult


@pytest.fixture
def scanner_service():
    """Create a ResultsScannerService instance."""
    return ResultsScannerService()


@pytest.fixture
def temp_folder():
    """Create a temporary folder for testing."""
    folder = tempfile.mkdtemp()
    yield folder
    shutil.rmtree(folder, ignore_errors=True)


@pytest.fixture
def sample_xml_content():
    """Sample ADIAT_DATA.XML content."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<settings>
    <algorithm>Color Range</algorithm>
    <image_count>3</image_count>
</settings>
<images>
    <image>
        <path>test_image1.jpg</path>
        <areas_of_interest>
            <aoi><id>1</id></aoi>
            <aoi><id>2</id></aoi>
        </areas_of_interest>
    </image>
    <image>
        <path>test_image2.jpg</path>
        <areas_of_interest>
            <aoi><id>3</id></aoi>
        </areas_of_interest>
    </image>
</images>'''


# ============================================================================
# Test ResultsScanResult data class
# ============================================================================

class TestResultsScanResult:
    """Tests for ResultsScanResult dataclass."""

    def test_initialization_with_all_fields(self):
        """Test ResultsScanResult with all fields."""
        result = ResultsScanResult(
            xml_path='/path/to/ADIAT_DATA.XML',
            folder_name='Test Folder',
            algorithm='Color Range',
            image_count=10,
            aoi_count=25,
            missing_images=2,
            first_image_path='/path/to/image.jpg',
            gps_coordinates=(37.7749, -122.4194)
        )

        assert result.xml_path == '/path/to/ADIAT_DATA.XML'
        assert result.folder_name == 'Test Folder'
        assert result.algorithm == 'Color Range'
        assert result.image_count == 10
        assert result.aoi_count == 25
        assert result.missing_images == 2
        assert result.first_image_path == '/path/to/image.jpg'
        assert result.gps_coordinates == (37.7749, -122.4194)

    def test_initialization_with_none_optionals(self):
        """Test ResultsScanResult with None optional fields."""
        result = ResultsScanResult(
            xml_path='/path/to/ADIAT_DATA.XML',
            folder_name='Test Folder',
            algorithm='Unknown',
            image_count=0,
            aoi_count=0,
            missing_images=0,
            first_image_path=None,
            gps_coordinates=None
        )

        assert result.first_image_path is None
        assert result.gps_coordinates is None

    def test_dataclass_conversion(self):
        """Test ResultsScanResult can be converted to dict."""
        result = ResultsScanResult(
            xml_path='/path/to/file.xml',
            folder_name='Test',
            algorithm='Test Algo',
            image_count=5,
            aoi_count=10,
            missing_images=1,
            first_image_path='/path/image.jpg',
            gps_coordinates=(0.0, 0.0)
        )

        result_dict = asdict(result)
        assert isinstance(result_dict, dict)
        assert result_dict['folder_name'] == 'Test'


# ============================================================================
# Test ResultsScannerService initialization
# ============================================================================

class TestResultsScannerServiceInit:
    """Tests for ResultsScannerService initialization."""

    def test_initialization(self):
        """Test service initializes correctly."""
        service = ResultsScannerService()
        assert service is not None
        assert service.logger is not None

    def test_xml_filename_constant(self):
        """Test XML filename constant is set."""
        assert ResultsScannerService.XML_FILENAME == "ADIAT_DATA.XML"


# ============================================================================
# Test count_directories
# ============================================================================

class TestCountDirectories:
    """Tests for count_directories method."""

    def test_count_empty_folder(self, scanner_service, temp_folder):
        """Test counting directories in empty folder."""
        count = scanner_service.count_directories(temp_folder)
        assert count >= 1  # At least the root folder

    def test_count_with_subdirectories(self, scanner_service, temp_folder):
        """Test counting directories with subdirectories."""
        # Create subdirectories
        os.makedirs(os.path.join(temp_folder, 'sub1'))
        os.makedirs(os.path.join(temp_folder, 'sub2'))
        os.makedirs(os.path.join(temp_folder, 'sub1', 'nested'))

        count = scanner_service.count_directories(temp_folder)
        assert count >= 4  # root + sub1 + sub2 + nested

    def test_count_with_files_only(self, scanner_service, temp_folder):
        """Test counting directories when only files exist."""
        # Create files but no subdirectories
        with open(os.path.join(temp_folder, 'file1.txt'), 'w') as f:
            f.write('test')
        with open(os.path.join(temp_folder, 'file2.txt'), 'w') as f:
            f.write('test')

        count = scanner_service.count_directories(temp_folder)
        assert count >= 1  # At least the root folder


# ============================================================================
# Test scan_folder
# ============================================================================

class TestScanFolder:
    """Tests for scan_folder method."""

    def test_scan_empty_folder(self, scanner_service, temp_folder):
        """Test scanning empty folder returns empty list."""
        results = scanner_service.scan_folder(temp_folder)
        assert results == []

    def test_scan_with_progress_callback(self, scanner_service, temp_folder):
        """Test scan_folder calls progress callback."""
        progress_calls = []

        def progress_callback(current, total, current_dir):
            progress_calls.append((current, total, current_dir))

        scanner_service.scan_folder(temp_folder, progress_callback=progress_callback)

        assert len(progress_calls) > 0
        # First call should have current >= 1
        assert progress_calls[0][0] >= 1

    def test_scan_finds_xml_file(self, scanner_service, temp_folder):
        """Test scan_folder finds ADIAT_DATA.XML files."""
        # Create ADIAT_Results folder with XML
        results_folder = os.path.join(temp_folder, 'ADIAT_Results')
        os.makedirs(results_folder)

        with patch.object(scanner_service, '_parse_result_file') as mock_parse:
            mock_parse.return_value = ResultsScanResult(
                xml_path=os.path.join(results_folder, 'ADIAT_DATA.XML'),
                folder_name='Test',
                algorithm='Color Range',
                image_count=1,
                aoi_count=1,
                missing_images=0,
                first_image_path=None,
                gps_coordinates=None
            )

            # Create the XML file
            xml_path = os.path.join(results_folder, 'ADIAT_DATA.XML')
            with open(xml_path, 'w') as f:
                f.write('<root></root>')

            results = scanner_service.scan_folder(temp_folder)

            assert len(results) == 1
            mock_parse.assert_called_once()

    def test_scan_finds_case_insensitive(self, scanner_service, temp_folder):
        """Test scan_folder finds XML files regardless of case."""
        results_folder = os.path.join(temp_folder, 'results')
        os.makedirs(results_folder)

        with patch.object(scanner_service, '_parse_result_file') as mock_parse:
            mock_parse.return_value = ResultsScanResult(
                xml_path=os.path.join(results_folder, 'adiat_data.xml'),
                folder_name='Test',
                algorithm='Test',
                image_count=0,
                aoi_count=0,
                missing_images=0,
                first_image_path=None,
                gps_coordinates=None
            )

            # Create lowercase XML file
            xml_path = os.path.join(results_folder, 'adiat_data.xml')
            with open(xml_path, 'w') as f:
                f.write('<root></root>')

            results = scanner_service.scan_folder(temp_folder)

            assert len(results) == 1

    def test_scan_handles_parse_error(self, scanner_service, temp_folder):
        """Test scan_folder handles parsing errors gracefully."""
        results_folder = os.path.join(temp_folder, 'results')
        os.makedirs(results_folder)

        with patch.object(scanner_service, '_parse_result_file') as mock_parse:
            mock_parse.side_effect = Exception("Parse error")

            xml_path = os.path.join(results_folder, 'ADIAT_DATA.XML')
            with open(xml_path, 'w') as f:
                f.write('<root></root>')

            # Should not raise, just return empty results
            results = scanner_service.scan_folder(temp_folder)
            assert results == []

    def test_scan_multiple_results(self, scanner_service, temp_folder):
        """Test scan_folder finds multiple result files."""
        # Create multiple result folders
        for i in range(3):
            folder = os.path.join(temp_folder, f'folder{i}', 'ADIAT_Results')
            os.makedirs(folder)
            xml_path = os.path.join(folder, 'ADIAT_DATA.XML')
            with open(xml_path, 'w') as f:
                f.write('<root></root>')

        with patch.object(scanner_service, '_parse_result_file') as mock_parse:
            mock_parse.return_value = ResultsScanResult(
                xml_path='test.xml',
                folder_name='Test',
                algorithm='Test',
                image_count=0,
                aoi_count=0,
                missing_images=0,
                first_image_path=None,
                gps_coordinates=None
            )

            results = scanner_service.scan_folder(temp_folder)

            assert len(results) == 3


# ============================================================================
# Test _parse_result_file
# ============================================================================

class TestParseResultFile:
    """Tests for _parse_result_file method."""

    def test_parse_success(self, scanner_service, temp_folder):
        """Test successful parsing of result file."""
        results_folder = os.path.join(temp_folder, 'ADIAT_Results')
        os.makedirs(results_folder)
        xml_path = os.path.join(results_folder, 'ADIAT_DATA.XML')

        with patch('core.services.ResultsScannerService.XmlService') as MockXmlService:
            mock_xml = MagicMock()
            mock_xml.get_settings.return_value = ({'algorithm': 'Color Range'}, 5)
            mock_xml.get_images.return_value = [
                {'path': 'image1.jpg', 'areas_of_interest': [{'id': 1}, {'id': 2}]},
                {'path': 'image2.jpg', 'areas_of_interest': [{'id': 3}]}
            ]
            MockXmlService.return_value = mock_xml

            result = scanner_service._parse_result_file(xml_path)

            assert result is not None
            assert result.algorithm == 'Color Range'
            assert result.image_count == 5
            assert result.aoi_count == 3

    def test_parse_with_missing_images(self, scanner_service, temp_folder):
        """Test parsing when some images are missing."""
        results_folder = os.path.join(temp_folder, 'ADIAT_Results')
        os.makedirs(results_folder)
        xml_path = os.path.join(results_folder, 'ADIAT_DATA.XML')

        # Create only one of the image files
        existing_image = os.path.join(temp_folder, 'exists.jpg')
        with open(existing_image, 'w') as f:
            f.write('image data')

        with patch('core.services.ResultsScannerService.XmlService') as MockXmlService, \
                patch.object(scanner_service, '_get_image_gps') as mock_gps:

            mock_xml = MagicMock()
            mock_xml.get_settings.return_value = ({'algorithm': 'Test'}, 2)
            mock_xml.get_images.return_value = [
                {'path': existing_image, 'areas_of_interest': []},
                {'path': '/nonexistent/path.jpg', 'areas_of_interest': []}
            ]
            MockXmlService.return_value = mock_xml
            mock_gps.return_value = None

            result = scanner_service._parse_result_file(xml_path)

            assert result is not None
            assert result.missing_images == 1
            assert result.first_image_path == existing_image

    def test_parse_extracts_gps_from_available_images(self, scanner_service, temp_folder):
        """Test that GPS is extracted from available images."""
        results_folder = os.path.join(temp_folder, 'ADIAT_Results')
        os.makedirs(results_folder)
        xml_path = os.path.join(results_folder, 'ADIAT_DATA.XML')

        existing_image = os.path.join(temp_folder, 'exists.jpg')
        with open(existing_image, 'w') as f:
            f.write('image data')

        with patch('core.services.ResultsScannerService.XmlService') as MockXmlService, \
                patch.object(scanner_service, '_get_image_gps') as mock_gps:

            mock_xml = MagicMock()
            mock_xml.get_settings.return_value = ({'algorithm': 'Test'}, 1)
            mock_xml.get_images.return_value = [
                {'path': existing_image, 'areas_of_interest': []}
            ]
            MockXmlService.return_value = mock_xml
            mock_gps.return_value = (37.7749, -122.4194)

            result = scanner_service._parse_result_file(xml_path)

            assert result is not None
            assert result.gps_coordinates == (37.7749, -122.4194)

    def test_parse_gps_fallback_to_second_image(self, scanner_service, temp_folder):
        """Test GPS extraction falls back to second image if first fails."""
        results_folder = os.path.join(temp_folder, 'ADIAT_Results')
        os.makedirs(results_folder)
        xml_path = os.path.join(results_folder, 'ADIAT_DATA.XML')

        image1 = os.path.join(temp_folder, 'image1.jpg')
        image2 = os.path.join(temp_folder, 'image2.jpg')
        with open(image1, 'w') as f:
            f.write('image data')
        with open(image2, 'w') as f:
            f.write('image data')

        with patch('core.services.ResultsScannerService.XmlService') as MockXmlService, \
                patch.object(scanner_service, '_get_image_gps') as mock_gps:

            mock_xml = MagicMock()
            mock_xml.get_settings.return_value = ({'algorithm': 'Test'}, 2)
            mock_xml.get_images.return_value = [
                {'path': image1, 'areas_of_interest': []},
                {'path': image2, 'areas_of_interest': []}
            ]
            MockXmlService.return_value = mock_xml

            # First image has no GPS, second image has GPS
            mock_gps.side_effect = [None, (40.7128, -74.0060)]

            result = scanner_service._parse_result_file(xml_path)

            assert result is not None
            assert result.gps_coordinates == (40.7128, -74.0060)
            assert mock_gps.call_count == 2

    def test_parse_uses_parent_folder_name(self, scanner_service, temp_folder):
        """Test folder name uses parent when in ADIAT_Results."""
        parent_folder = os.path.join(temp_folder, 'MyDroneFlightData')
        results_folder = os.path.join(parent_folder, 'ADIAT_Results')
        os.makedirs(results_folder)
        xml_path = os.path.join(results_folder, 'ADIAT_DATA.XML')

        with patch('core.services.ResultsScannerService.XmlService') as MockXmlService:
            mock_xml = MagicMock()
            mock_xml.get_settings.return_value = ({'algorithm': 'Test'}, 0)
            mock_xml.get_images.return_value = []
            MockXmlService.return_value = mock_xml

            result = scanner_service._parse_result_file(xml_path)

            assert result is not None
            assert result.folder_name == 'MyDroneFlightData'

    def test_parse_unknown_algorithm(self, scanner_service, temp_folder):
        """Test parsing when algorithm is not specified."""
        results_folder = os.path.join(temp_folder, 'results')
        os.makedirs(results_folder)
        xml_path = os.path.join(results_folder, 'ADIAT_DATA.XML')

        with patch('core.services.ResultsScannerService.XmlService') as MockXmlService:
            mock_xml = MagicMock()
            mock_xml.get_settings.return_value = ({}, 0)  # No algorithm key
            mock_xml.get_images.return_value = []
            MockXmlService.return_value = mock_xml

            result = scanner_service._parse_result_file(xml_path)

            assert result is not None
            assert result.algorithm == 'Unknown'

    def test_parse_handles_exception(self, scanner_service, temp_folder):
        """Test parsing handles exceptions gracefully."""
        xml_path = os.path.join(temp_folder, 'ADIAT_DATA.XML')

        with patch('core.services.ResultsScannerService.XmlService') as MockXmlService:
            MockXmlService.side_effect = Exception("XML parse error")

            result = scanner_service._parse_result_file(xml_path)

            assert result is None


# ============================================================================
# Test _get_image_gps
# ============================================================================

class TestGetImageGps:
    """Tests for _get_image_gps method."""

    def test_get_gps_from_exif(self, scanner_service, temp_folder):
        """Test getting GPS from EXIF data."""
        image_path = os.path.join(temp_folder, 'test.jpg')

        with patch('core.services.ResultsScannerService.MetaDataHelper') as MockMeta, \
                patch('core.services.ResultsScannerService.LocationInfo') as MockLocation:

            MockMeta.get_exif_data_piexif.return_value = {'GPS': 'data'}
            MockLocation.get_gps.return_value = {
                'latitude': 37.7749,
                'longitude': -122.4194
            }

            result = scanner_service._get_image_gps(image_path)

            assert result == (37.7749, -122.4194)

    def test_get_gps_fallback_to_path_method(self, scanner_service, temp_folder):
        """Test GPS extraction falls back to path method."""
        image_path = os.path.join(temp_folder, 'test.jpg')

        with patch('core.services.ResultsScannerService.MetaDataHelper') as MockMeta, \
                patch('core.services.ResultsScannerService.LocationInfo') as MockLocation:

            # EXIF method returns empty
            MockMeta.get_exif_data_piexif.return_value = None

            # First call (from exif_data) returns None, second call (from full_path) returns GPS
            def get_gps_side_effect(**kwargs):
                if 'full_path' in kwargs:
                    return {'latitude': 40.7128, 'longitude': -74.0060}
                return None

            MockLocation.get_gps.side_effect = get_gps_side_effect

            result = scanner_service._get_image_gps(image_path)

            assert result == (40.7128, -74.0060)

    def test_get_gps_no_coordinates(self, scanner_service, temp_folder):
        """Test getting GPS when no coordinates available."""
        image_path = os.path.join(temp_folder, 'test.jpg')

        with patch('core.services.ResultsScannerService.MetaDataHelper') as MockMeta, \
                patch('core.services.ResultsScannerService.LocationInfo') as MockLocation:

            MockMeta.get_exif_data_piexif.return_value = {}
            MockLocation.get_gps.return_value = None

            result = scanner_service._get_image_gps(image_path)

            assert result is None

    def test_get_gps_partial_coordinates(self, scanner_service, temp_folder):
        """Test getting GPS when only partial coordinates available."""
        image_path = os.path.join(temp_folder, 'test.jpg')

        with patch('core.services.ResultsScannerService.MetaDataHelper') as MockMeta, \
                patch('core.services.ResultsScannerService.LocationInfo') as MockLocation:

            MockMeta.get_exif_data_piexif.return_value = {}
            # Only latitude, no longitude
            MockLocation.get_gps.return_value = {'latitude': 37.7749}

            result = scanner_service._get_image_gps(image_path)

            assert result is None

    def test_get_gps_handles_exception(self, scanner_service, temp_folder):
        """Test GPS extraction handles exceptions gracefully."""
        image_path = os.path.join(temp_folder, 'test.jpg')

        with patch('core.services.ResultsScannerService.MetaDataHelper') as MockMeta:
            MockMeta.get_exif_data_piexif.side_effect = Exception("EXIF read error")

            result = scanner_service._get_image_gps(image_path)

            assert result is None


# ============================================================================
# Integration tests
# ============================================================================

class TestIntegration:
    """Integration tests for ResultsScannerService."""

    def test_full_scan_workflow(self, scanner_service, temp_folder):
        """Test complete scan workflow with mocked XML service."""
        # Create folder structure
        flight1 = os.path.join(temp_folder, 'Flight1', 'ADIAT_Results')
        flight2 = os.path.join(temp_folder, 'Flight2', 'ADIAT_Results')
        os.makedirs(flight1)
        os.makedirs(flight2)

        # Create dummy image
        image_path = os.path.join(temp_folder, 'Flight1', 'image.jpg')
        with open(image_path, 'w') as f:
            f.write('dummy')

        # Create XML files
        for folder in [flight1, flight2]:
            xml_path = os.path.join(folder, 'ADIAT_DATA.XML')
            with open(xml_path, 'w') as f:
                f.write('<root></root>')

        with patch('core.services.ResultsScannerService.XmlService') as MockXmlService, \
                patch.object(scanner_service, '_get_image_gps') as mock_gps:

            mock_xml = MagicMock()
            mock_xml.get_settings.return_value = ({'algorithm': 'RX Anomaly'}, 3)
            mock_xml.get_images.return_value = [
                {'path': image_path, 'areas_of_interest': [{'id': 1}]}
            ]
            MockXmlService.return_value = mock_xml
            mock_gps.return_value = (37.0, -122.0)

            progress_updates = []
            results = scanner_service.scan_folder(
                temp_folder,
                progress_callback=lambda c, t, d: progress_updates.append((c, t, d))
            )

            assert len(results) == 2
            assert len(progress_updates) > 0

            # Check result content
            for result in results:
                assert result.algorithm == 'RX Anomaly'
                assert result.image_count == 3
                assert result.aoi_count == 1

    def test_scan_deeply_nested_structure(self, scanner_service, temp_folder):
        """Test scanning deeply nested folder structure."""
        # Create deeply nested structure
        deep_path = os.path.join(temp_folder, 'a', 'b', 'c', 'd', 'ADIAT_Results')
        os.makedirs(deep_path)

        xml_path = os.path.join(deep_path, 'ADIAT_DATA.XML')
        with open(xml_path, 'w') as f:
            f.write('<root></root>')

        with patch('core.services.ResultsScannerService.XmlService') as MockXmlService:
            mock_xml = MagicMock()
            mock_xml.get_settings.return_value = ({'algorithm': 'Test'}, 0)
            mock_xml.get_images.return_value = []
            MockXmlService.return_value = mock_xml

            results = scanner_service.scan_folder(temp_folder)

            assert len(results) == 1
            assert results[0].folder_name == 'd'
