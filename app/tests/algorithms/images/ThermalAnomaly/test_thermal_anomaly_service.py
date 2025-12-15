import pytest
import numpy as np
import tempfile
import os
from unittest.mock import patch, MagicMock
from algorithms.images.ThermalAnomaly.services.ThermalAnomalyService import ThermalAnomalyService
from algorithms.AlgorithmService import AnalysisResult


@pytest.fixture
def thermal_anomaly_service():
    """Fixture providing a ThermalAnomalyService instance."""
    options = {
        'threshold': 6.0,
        'segments': 2,
        'type': 'Above Mean'
    }
    return ThermalAnomalyService(
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


def test_thermal_anomaly_service_initialization(thermal_anomaly_service):
    """Test ThermalAnomalyService initialization."""
    assert thermal_anomaly_service.is_thermal is True
    assert thermal_anomaly_service.threshold == 6.0
    assert thermal_anomaly_service.segments == 2
    assert thermal_anomaly_service.direction == 'Above Mean'


def test_thermal_anomaly_service_below_mean():
    """Test ThermalAnomalyService with 'Below Mean' direction."""
    options = {
        'threshold': 6.0,
        'segments': 2,
        'type': 'Below Mean'
    }
    service = ThermalAnomalyService(
        identifier=(255, 0, 0),
        min_area=10,
        max_area=1000,
        aoi_radius=5,
        combine_aois=True,
        options=options
    )
    assert service.direction == 'Below Mean'


def test_thermal_anomaly_service_both_directions():
    """Test ThermalAnomalyService with 'Above or Below Mean' direction."""
    options = {
        'threshold': 6.0,
        'segments': 2,
        'type': 'Above or Below Mean'
    }
    service = ThermalAnomalyService(
        identifier=(255, 0, 0),
        min_area=10,
        max_area=1000,
        aoi_radius=5,
        combine_aois=True,
        options=options
    )
    assert service.direction == 'Above or Below Mean'


def test_process_image_mock_thermal(thermal_anomaly_service, test_image):
    """Test processing with mocked thermal parser."""
    # Create temperature data with anomaly
    mock_temperature = np.ones((200, 200), dtype=np.float32) * 20.0  # Background
    mock_temperature[50:100, 50:100] = 40.0  # Hot anomaly

    with patch('algorithms.images.ThermalAnomaly.services.ThermalAnomalyService.ThermalParserService') as MockThermalParser:
        mock_parser = MagicMock()
        mock_parser.parse_file.return_value = (mock_temperature, test_image)
        MockThermalParser.return_value = mock_parser

        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = tmpdir
            output_dir = os.path.join(tmpdir, "output")
            os.makedirs(output_dir, exist_ok=True)
            full_path = os.path.join(input_dir, "test.jpg")

            result = thermal_anomaly_service.process_image(test_image, full_path, input_dir, output_dir)

            assert isinstance(result, AnalysisResult)
            assert result.input_path == full_path
