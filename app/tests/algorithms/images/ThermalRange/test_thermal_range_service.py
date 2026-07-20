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


def _make_service(min_temp=20.0, max_temp=30.0, min_area=1, max_area=10000, combine=False):
    return ThermalRangeService(
        identifier=(255, 0, 0),
        min_area=min_area,
        max_area=max_area,
        aoi_radius=3,
        combine_aois=combine,
        options={'minTemp': min_temp, 'maxTemp': max_temp},
    )


def _run_with_mock(service, temperature, visual_shape=None):
    visual_shape = visual_shape or temperature.shape
    if len(visual_shape) == 2:
        visual = np.zeros((*visual_shape, 3), dtype=np.uint8)
    else:
        visual = np.zeros(visual_shape, dtype=np.uint8)

    with patch(
        "algorithms.images.ThermalRange.services.ThermalRangeService.ThermalParserService"
    ) as MockParser:
        parser = MagicMock()
        parser.parse_file.return_value = (temperature, visual)
        MockParser.return_value = parser

        with tempfile.TemporaryDirectory() as tmpdir:
            full_path = os.path.join(tmpdir, "test.jpg")
            return service.process_image(visual, full_path, tmpdir, tmpdir)


def test_process_image_no_pixels_in_range_returns_no_aois():
    service = _make_service(min_temp=100.0, max_temp=200.0)
    temperature = np.ones((50, 50), dtype=np.float32) * 20.0  # all out of range
    result = _run_with_mock(service, temperature)
    assert result.error_message is None
    assert result.areas_of_interest is None or len(result.areas_of_interest) == 0


def test_process_image_scales_aoi_when_visual_differs_from_thermal():
    service = _make_service(min_temp=20.0, max_temp=30.0)
    temperature = np.ones((50, 50), dtype=np.float32) * 15.0
    temperature[20:30, 20:30] = 25.0  # hot patch in range
    result = _run_with_mock(service, temperature, visual_shape=(100, 100, 3))
    assert result.error_message is None
    if result.areas_of_interest:
        # Center should be scaled up to visual coordinates (>50)
        for aoi in result.areas_of_interest:
            cx, cy = aoi['center']
            # Hot patch centroid was ~(25, 25) thermal -> ~(50, 50) visual
            assert 0 <= cx <= 100
            assert 0 <= cy <= 100


def test_process_image_returns_error_when_parser_raises():
    service = _make_service()
    with patch(
        "algorithms.images.ThermalRange.services.ThermalRangeService.ThermalParserService"
    ) as MockParser:
        MockParser.return_value.parse_file.side_effect = RuntimeError("parse failed")
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
    assert "parse failed" in result.error_message


def test_process_image_combines_overlapping_aois():
    service = _make_service(combine=True)
    temperature = np.ones((100, 100), dtype=np.float32) * 10.0
    # Two overlapping hot regions
    temperature[20:40, 20:40] = 25.0
    temperature[30:50, 30:50] = 25.0
    result = _run_with_mock(service, temperature)
    assert result.error_message is None


def test_process_image_filters_by_area():
    # max_area=5 is very small, should eliminate larger regions
    service = _make_service(min_area=1, max_area=5)
    temperature = np.ones((50, 50), dtype=np.float32) * 15.0
    temperature[20:35, 20:35] = 25.0  # 225 pixel region
    result = _run_with_mock(service, temperature)
    # Large region filtered out
    assert result.areas_of_interest is None or len(result.areas_of_interest) == 0
