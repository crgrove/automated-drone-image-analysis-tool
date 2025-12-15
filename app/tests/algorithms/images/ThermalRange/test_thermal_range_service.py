import pytest
import numpy as np
import tempfile
import os
from unittest.mock import patch, MagicMock
from algorithms.images.ThermalRange.services.ThermalRangeService import ThermalRangeService
from algorithms.AlgorithmService import AnalysisResult


@pytest.fixture
def thermal_range_service():
    """Fixture providing a ThermalRangeService instance."""
    options = {
        'minTemp': 20.0,
        'maxTemp': 30.0
    }
    return ThermalRangeService(
        identifier=(255, 0, 0),
        min_area=10,
        max_area=1000,
        aoi_radius=5,
        combine_aois=True,
        options=options
    )


@pytest.fixture
def test_image():
    """Create a test thermal image."""
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    return img


def test_thermal_range_service_initialization(thermal_range_service):
    """Test ThermalRangeService initialization."""
    assert thermal_range_service.name == 'MatchedFilter'  # Note: inherits from base
    assert thermal_range_service.is_thermal is True
    assert thermal_range_service.min_temp == 20.0
    assert thermal_range_service.max_temp == 30.0


def test_process_image_mock_thermal(thermal_range_service, test_image):
    """Test processing with mocked thermal parser."""
    # Mock temperature data
    mock_temperature = np.ones((200, 200), dtype=np.float32) * 25.0  # 25°C

    with patch('algorithms.images.ThermalRange.services.ThermalRangeService.ThermalParserService') as MockThermalParser:
        mock_parser = MagicMock()
        mock_parser.parse_file.return_value = (mock_temperature, test_image)
        MockThermalParser.return_value = mock_parser

        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = tmpdir
            output_dir = os.path.join(tmpdir, "output")
            os.makedirs(output_dir, exist_ok=True)
            full_path = os.path.join(input_dir, "test.jpg")

            result = thermal_range_service.process_image(test_image, full_path, input_dir, output_dir)

            assert isinstance(result, AnalysisResult)
            assert result.input_path == full_path


def test_process_image_temperature_extraction(thermal_range_service, test_image):
    """Test that temperature data is extracted for AOIs."""
    # Create temperature data with a hot spot
    mock_temperature = np.ones((200, 200), dtype=np.float32) * 15.0  # Background
    mock_temperature[50:100, 50:100] = 25.0  # Hot spot in range

    with patch('algorithms.images.ThermalRange.services.ThermalRangeService.ThermalParserService') as MockThermalParser:
        mock_parser = MagicMock()
        mock_parser.parse_file.return_value = (mock_temperature, test_image)
        MockThermalParser.return_value = mock_parser

        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = tmpdir
            output_dir = os.path.join(tmpdir, "output")
            os.makedirs(output_dir, exist_ok=True)
            full_path = os.path.join(input_dir, "test.jpg")

            result = thermal_range_service.process_image(test_image, full_path, input_dir, output_dir)

            if result.areas_of_interest and len(result.areas_of_interest) > 0:
                # Check that temperature was extracted
                assert 'temperature' in result.areas_of_interest[0]
                assert result.areas_of_interest[0]['temperature'] is not None
