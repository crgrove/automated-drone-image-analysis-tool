import pytest
import numpy as np
import cv2
import tempfile
import os
from algorithms.images.HSVColorRange.services.HSVColorRangeService import HSVColorRangeService
from algorithms.AlgorithmService import AnalysisResult


@pytest.fixture
def hsv_color_range_service():
    """Fixture providing an HSVColorRangeService instance."""
    options = {
        'hsv_configs': [
            {
                'selected_color': (100, 150, 200),
                'hsv_ranges': {
                    'h': 0.5,
                    's': 0.6,
                    'v': 0.8,
                    'h_minus': 0.05,
                    'h_plus': 0.05,
                    's_minus': 0.1,
                    's_plus': 0.1,
                    'v_minus': 0.1,
                    'v_plus': 0.1
                }
            }
        ]
    }
    return HSVColorRangeService(
        identifier=(100, 150, 200),
        min_area=10,
        max_area=1000,
        aoi_radius=5,
        combine_aois=True,
        options=options
    )


@pytest.fixture
def test_image():
    """Create a test image with colored regions."""
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    # Add a colored region (BGR format)
    img[50:100, 50:100] = [200, 150, 100]  # RGB(100, 150, 200) in BGR
    return img


def test_hsv_color_range_service_initialization(hsv_color_range_service):
    """Test HSVColorRangeService initialization."""
    assert hsv_color_range_service.name == 'HSVColorRange'
    assert hsv_color_range_service.target_color_hsv is not None


def test_hsv_color_range_service_legacy_format():
    """Test HSVColorRangeService with legacy hsv_ranges format."""
    # Convert RGB to HSV
    rgb_color = np.uint8([[[100, 150, 200]]])
    hsv_color = cv2.cvtColor(rgb_color, cv2.COLOR_RGB2HSV)[0][0]

    options = {
        'hsv_ranges': {
            'h': hsv_color[0] / 179.0,
            's': hsv_color[1] / 255.0,
            'v': hsv_color[2] / 255.0,
            'h_minus': 0.05,
            'h_plus': 0.05,
            's_minus': 0.1,
            's_plus': 0.1,
            'v_minus': 0.1,
            'v_plus': 0.1
        }
    }
    service = HSVColorRangeService(
        identifier=(100, 150, 200),
        min_area=10,
        max_area=1000,
        aoi_radius=5,
        combine_aois=True,
        options=options
    )
    assert service.name == 'HSVColorRange'


def test_hsv_color_range_service_old_window_format():
    """Test HSVColorRangeService with old hsv_window format."""
    options = {
        'hsv_window': {
            'h_min': 170,
            'h_max': 10,
            's_min': 50,
            's_max': 100,
            'v_min': 50,
            'v_max': 100
        }
    }
    service = HSVColorRangeService(
        identifier=(100, 150, 200),
        min_area=10,
        max_area=1000,
        aoi_radius=5,
        combine_aois=True,
        options=options
    )
    assert service.name == 'HSVColorRange'


def test_create_mask_from_hsv_ranges(hsv_color_range_service):
    """Test _create_mask_from_hsv_ranges method."""
    hsv_image = np.zeros((100, 100, 3), dtype=np.uint8)
    hsv_image[50:70, 50:70] = [90, 150, 200]  # HSV values

    hsv_ranges = {
        'h': 90 / 179.0,
        's': 150 / 255.0,
        'v': 200 / 255.0,
        'h_minus': 0.05,
        'h_plus': 0.05,
        's_minus': 0.1,
        's_plus': 0.1,
        'v_minus': 0.1,
        'v_plus': 0.1
    }

    mask = hsv_color_range_service._create_mask_from_hsv_ranges(hsv_image, hsv_ranges)

    assert mask.shape == (100, 100)
    assert mask.dtype == np.uint8


def test_create_mask_from_hsv_ranges_wraparound(hsv_color_range_service):
    """Test _create_mask_from_hsv_ranges with hue wraparound."""
    hsv_image = np.zeros((100, 100, 3), dtype=np.uint8)

    # Test lower wraparound (h_low < 0)
    hsv_ranges = {
        'h': 5 / 179.0,  # Very low hue
        's': 128 / 255.0,
        'v': 200 / 255.0,
        'h_minus': 0.1,  # Will cause wraparound
        'h_plus': 0.05,
        's_minus': 0.1,
        's_plus': 0.1,
        'v_minus': 0.1,
        'v_plus': 0.1
    }

    mask = hsv_color_range_service._create_mask_from_hsv_ranges(hsv_image, hsv_ranges)
    assert mask.shape == (100, 100)


def test_process_image_single_config(hsv_color_range_service, test_image):
    """Test processing an image with single HSV config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = tmpdir
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(input_dir, "test.jpg")

        result = hsv_color_range_service.process_image(test_image, full_path, input_dir, output_dir)

        assert isinstance(result, AnalysisResult)
        assert result.input_path == full_path
        assert result.error_message is None


def test_process_image_multiple_configs(test_image):
    """Test processing with multiple HSV configs."""
    options = {
        'hsv_configs': [
            {
                'selected_color': (100, 150, 200),
                'hsv_ranges': {
                    'h': 0.5,
                    's': 0.6,
                    'v': 0.8,
                    'h_minus': 0.05,
                    'h_plus': 0.05,
                    's_minus': 0.1,
                    's_plus': 0.1,
                    'v_minus': 0.1,
                    'v_plus': 0.1
                }
            },
            {
                'selected_color': (200, 100, 50),
                'hsv_ranges': {
                    'h': 0.1,
                    's': 0.4,
                    'v': 0.8,
                    'h_minus': 0.05,
                    'h_plus': 0.05,
                    's_minus': 0.1,
                    's_plus': 0.1,
                    'v_minus': 0.1,
                    'v_plus': 0.1
                }
            }
        ]
    }
    service = HSVColorRangeService(
        identifier=(100, 150, 200),
        min_area=10,
        max_area=1000,
        aoi_radius=5,
        combine_aois=True,
        options=options
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = tmpdir
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(input_dir, "test.jpg")

        result = service.process_image(test_image, full_path, input_dir, output_dir)

        assert isinstance(result, AnalysisResult)
        assert result.error_message is None


def test_calculate_hsv_distances(hsv_color_range_service):
    """Test HSV distance calculation."""
    hsv_image = np.zeros((100, 100, 3), dtype=np.uint8)
    hsv_image[50:70, 50:70] = [90, 150, 200]

    target_hsv = np.array([90, 150, 200])
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[50:70, 50:70] = 255

    distances = hsv_color_range_service._calculate_hsv_distances(hsv_image, target_hsv, mask)

    assert distances.shape == (100, 100)
    assert distances.dtype == np.float32
    # Distances in the masked region should be low (good match)
    assert np.mean(distances[50:70, 50:70]) < 0.1


def test_add_confidence_scores(hsv_color_range_service):
    """Test adding confidence scores to AOIs."""
    areas_of_interest = [
        {
            'center': (50, 50),
            'radius': 10,
            'detected_pixels': [(45, 45), (46, 46), (47, 47)]
        }
    ]

    hsv_distances = np.zeros((100, 100), dtype=np.float32)
    hsv_distances[45:48, 45:48] = 0.1  # Low distance = good match

    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[45:48, 45:48] = 255

    result = hsv_color_range_service._add_confidence_scores(
        areas_of_interest, hsv_distances, mask
    )

    assert len(result) == 1
    assert 'confidence' in result[0]
    assert 'score_type' in result[0]
    assert result[0]['score_type'] == 'color_distance'


def test_process_image_no_color_selected():
    """Test processing with no color selected (should return error)."""
    options = {}
    service = HSVColorRangeService(
        identifier=(100, 150, 200),
        min_area=10,
        max_area=1000,
        aoi_radius=5,
        combine_aois=True,
        options=options
    )

    test_image = np.zeros((100, 100, 3), dtype=np.uint8)

    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = tmpdir
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(input_dir, "test.jpg")

        result = service.process_image(test_image, full_path, input_dir, output_dir)

        assert isinstance(result, AnalysisResult)
        assert result.error_message is not None
