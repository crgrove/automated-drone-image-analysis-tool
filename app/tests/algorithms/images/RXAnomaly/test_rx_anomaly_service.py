import pytest
import numpy as np
import tempfile
import os
from algorithms.images.RXAnomaly.services.RXAnomalyService import RXAnomalyService
from algorithms.AlgorithmService import AnalysisResult


@pytest.fixture
def rx_anomaly_service():
    """Fixture providing an RXAnomalyService instance."""
    options = {
        'sensitivity': 7,
        'segments': 2
    }
    return RXAnomalyService(
        identifier=(255, 0, 0),
        min_area=10,
        max_area=1000,
        aoi_radius=5,
        combine_aois=True,
        options=options
    )


@pytest.fixture
def test_image():
    """Create a test image."""
    img = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    return img


def test_rx_anomaly_service_initialization(rx_anomaly_service):
    """Test RXAnomalyService initialization."""
    assert rx_anomaly_service.name == 'RXAnomaly'
    assert rx_anomaly_service.chi_threshold is not None
    assert rx_anomaly_service.segments == 2


def test_get_threshold(rx_anomaly_service):
    """Test threshold calculation from sensitivity."""
    # Test different sensitivity values
    thresholds = []
    for sensitivity in range(1, 11):
        threshold = rx_anomaly_service.get_threshold(sensitivity)
        thresholds.append(threshold)

    # Thresholds should increase with sensitivity
    assert all(thresholds[i] <= thresholds[i + 1] for i in range(len(thresholds) - 1))


def test_process_image(rx_anomaly_service, test_image):
    """Test processing an image with RX Anomaly algorithm."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = tmpdir
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(input_dir, "test.jpg")

        result = rx_anomaly_service.process_image(test_image, full_path, input_dir, output_dir)

        assert isinstance(result, AnalysisResult)
        assert result.input_path == full_path
        assert result.error_message is None


def test_process_image_hue_expansion(rx_anomaly_service, test_image):
    """Test processing with hue expansion enabled."""
    rx_anomaly_service.options['hue_expansion_enabled'] = True
    rx_anomaly_service.options['hue_expansion_range'] = 10

    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = tmpdir
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(input_dir, "test.jpg")

        result = rx_anomaly_service.process_image(test_image, full_path, input_dir, output_dir)

        assert isinstance(result, AnalysisResult)
        assert result.error_message is None


def test_add_confidence_scores(rx_anomaly_service):
    """Test adding confidence scores to AOIs."""
    areas_of_interest = [
        {
            'center': (50, 50),
            'radius': 10,
            'detected_pixels': [(45, 45), (46, 46), (47, 47)]
        }
    ]

    rx_values = np.zeros((100, 100), dtype=np.float32)
    rx_values[45:48, 45:48] = 100.0  # High RX value = anomaly

    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[45:48, 45:48] = 1

    result = rx_anomaly_service._add_confidence_scores(
        areas_of_interest, rx_values, mask
    )

    assert len(result) == 1
    assert 'confidence' in result[0]
    assert 'score_type' in result[0]
    assert result[0]['score_type'] == 'anomaly'  # Service uses 'anomaly', not 'rx_anomaly'
