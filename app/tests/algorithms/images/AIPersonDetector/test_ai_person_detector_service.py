import pytest
import numpy as np
import tempfile
import os
from unittest.mock import patch, MagicMock
from algorithms.images.AIPersonDetector.services.AIPersonDetectorService import AIPersonDetectorService
from algorithms.AlgorithmService import AnalysisResult


@pytest.fixture
def ai_person_detector_service():
    """Fixture providing an AIPersonDetectorService instance."""
    options = {
        'person_detector_confidence': 50,
        'cpu_only': True
    }
    return AIPersonDetectorService(
        identifier=(255, 0, 0),
        min_area=100,
        max_area=10000,
        aoi_radius=10,
        combine_aois=True,
        options=options
    )


@pytest.fixture
def test_image():
    """Create a test image."""
    img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    return img


def test_ai_person_detector_service_initialization(ai_person_detector_service):
    """Test AIPersonDetectorService initialization."""
    assert ai_person_detector_service.name == 'AIPersonDetector'
    assert ai_person_detector_service.confidence == 0.5  # 50/100
    assert ai_person_detector_service.cpu_only is True
    assert ai_person_detector_service.slice_size == 1280
    assert ai_person_detector_service.model_img_size == 640


def test_ai_person_detector_service_gpu_mode():
    """Test AIPersonDetectorService with GPU mode."""
    options = {
        'person_detector_confidence': 50,
        'cpu_only': False
    }
    service = AIPersonDetectorService(
        identifier=(255, 0, 0),
        min_area=100,
        max_area=10000,
        aoi_radius=10,
        combine_aois=True,
        options=options
    )
    assert service.cpu_only is False
    assert service.slice_size == 2048
    assert service.model_img_size == 1024


def test_preprocess_whole_image(ai_person_detector_service, test_image):
    """Test image preprocessing."""
    result = ai_person_detector_service._preprocess_whole_image(test_image)

    assert result.shape == test_image.shape
    assert result.dtype == np.float32
    assert result.max() <= 1.0
    assert result.min() >= 0.0


def test_preprocess_slice(ai_person_detector_service):
    """Test slice preprocessing."""
    slice_img = np.random.rand(100, 100, 3).astype(np.float32)

    result = ai_person_detector_service._preprocess_slice(slice_img, out_size=640)

    assert result.shape == (1, 3, 640, 640)
    assert result.dtype == np.float32


def test_process_image_mock_onnx(ai_person_detector_service, test_image):
    """Test processing with mocked ONNX session."""
    # Mock ONNX session
    mock_session = MagicMock()
    mock_input = MagicMock()
    mock_input.name = 'input'
    mock_session.get_inputs.return_value = [mock_input]

    # Mock outputs (format: [boxes, scores, classes])
    mock_outputs = [
        np.array([[[0.1, 0.1, 0.2, 0.2, 0.9, 0]]], dtype=np.float32)  # Single detection
    ]
    mock_session.run.return_value = mock_outputs

    with patch.object(ai_person_detector_service, '_create_onnx_session', return_value=mock_session):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = tmpdir
            output_dir = os.path.join(tmpdir, "output")
            os.makedirs(output_dir, exist_ok=True)
            full_path = os.path.join(input_dir, "test.jpg")

            result = ai_person_detector_service.process_image(test_image, full_path, input_dir, output_dir)

            assert isinstance(result, AnalysisResult)
            assert result.input_path == full_path
