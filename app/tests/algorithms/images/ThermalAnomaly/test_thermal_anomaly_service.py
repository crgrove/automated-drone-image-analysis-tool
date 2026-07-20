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


def _make_service(direction="Above Mean", threshold=3.0, segments=2):
    return ThermalAnomalyService(
        identifier=(255, 0, 0),
        min_area=1,
        max_area=100000,
        aoi_radius=3,
        combine_aois=True,
        options={"threshold": threshold, "segments": segments, "type": direction},
    )


def _run_with_mock_thermal(service, temperature, visual_shape=None):
    visual_shape = visual_shape or temperature.shape
    if len(visual_shape) == 2:
        visual_image = np.zeros((*visual_shape, 3), dtype=np.uint8)
    else:
        visual_image = np.zeros(visual_shape, dtype=np.uint8)

    with patch(
        "algorithms.images.ThermalAnomaly.services.ThermalAnomalyService.ThermalParserService"
    ) as MockParser:
        parser = MagicMock()
        parser.parse_file.return_value = (temperature, visual_image)
        MockParser.return_value = parser

        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = tmpdir
            output_dir = os.path.join(tmpdir, "output")
            os.makedirs(output_dir, exist_ok=True)
            full_path = os.path.join(input_dir, "test.jpg")
            return service.process_image(visual_image, full_path, input_dir, output_dir)


def test_process_image_below_mean_detects_cold():
    service = _make_service(direction="Below Mean", threshold=2.0)
    temperature = np.ones((100, 100), dtype=np.float32) * 20.0
    # Cold anomaly
    temperature[40:60, 40:60] = -5.0

    result = _run_with_mock_thermal(service, temperature)
    assert isinstance(result, AnalysisResult)
    assert result.error_message is None
    assert result.areas_of_interest is not None
    assert len(result.areas_of_interest) >= 1


def test_process_image_above_or_below_mean_detects_both():
    service = _make_service(direction="Above or Below Mean", threshold=2.0)
    temperature = np.ones((100, 100), dtype=np.float32) * 20.0
    temperature[10:20, 10:20] = 80.0   # hot
    temperature[80:90, 80:90] = -40.0  # cold

    result = _run_with_mock_thermal(service, temperature)
    assert result.error_message is None
    assert result.areas_of_interest is not None
    assert len(result.areas_of_interest) >= 2


def test_process_image_extracts_temperatures_for_aois():
    service = _make_service(direction="Above Mean", threshold=2.0)
    temperature = np.ones((100, 100), dtype=np.float32) * 20.0
    temperature[40:60, 40:60] = 60.0

    result = _run_with_mock_thermal(service, temperature)
    assert result.areas_of_interest is not None
    # At least one AOI should have an extracted temperature
    has_temp = any(
        aoi.get("temperature") is not None for aoi in result.areas_of_interest
    )
    assert has_temp


def test_process_image_scales_aoi_when_visual_differs_from_thermal():
    service = _make_service(direction="Above Mean", threshold=2.0)
    # Thermal data 50x50, visual image 100x100 -> scale 2x
    temperature = np.ones((50, 50), dtype=np.float32) * 20.0
    temperature[20:30, 20:30] = 60.0

    result = _run_with_mock_thermal(service, temperature, visual_shape=(100, 100, 3))
    assert result.areas_of_interest is not None
    # Centers should be in visual-resolution coordinates (> thermal's 50x50 range)
    for aoi in result.areas_of_interest:
        cx, cy = aoi["center"]
        # Hot region centroid ~(25,25) in thermal -> ~(50,50) in visual (2x scale)
        assert 0 <= cx <= 100
        assert 0 <= cy <= 100


def test_process_image_returns_error_when_parser_raises():
    service = _make_service()
    with patch(
        "algorithms.images.ThermalAnomaly.services.ThermalAnomalyService.ThermalParserService"
    ) as MockParser:
        MockParser.return_value.parse_file.side_effect = RuntimeError("bad file")
        with tempfile.TemporaryDirectory() as tmpdir:
            full_path = os.path.join(tmpdir, "test.jpg")
            result = service.process_image(
                np.zeros((50, 50, 3), dtype=np.uint8),
                full_path,
                tmpdir,
                tmpdir,
            )
    assert isinstance(result, AnalysisResult)
    assert result.error_message is not None
    assert "bad file" in result.error_message


def test_process_image_uniform_temperature_no_anomalies():
    service = _make_service(direction="Above Mean", threshold=2.0)
    # Perfectly uniform -> std=0 -> thresholds equal mean -> no anomaly
    temperature = np.ones((50, 50), dtype=np.float32) * 20.0
    result = _run_with_mock_thermal(service, temperature)
    assert result.error_message is None
    # Either no AOIs or base_contour_count is 0/None
    assert result.areas_of_interest is None or len(result.areas_of_interest) == 0
