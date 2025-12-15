import pytest
import numpy as np
import tempfile
import os
from algorithms.images.MatchedFilter.services.MatchedFilterService import MatchedFilterService
from algorithms.AlgorithmService import AnalysisResult


@pytest.fixture
def matched_filter_service():
    """Fixture providing a MatchedFilterService instance."""
    options = {
        'color_configs': [
            {
                'selected_color': (100, 150, 200),
                'match_filter_threshold': 0.3
            }
        ]
    }
    return MatchedFilterService(
        identifier=(100, 150, 200),
        min_area=10,
        max_area=1000,
        aoi_radius=5,
        combine_aois=True,
        options=options
    )


@pytest.fixture
def test_image():
    """Create a test image with colored regions and varied background.

    The background must have variance to avoid singular matrix errors in MatchedFilter.
    """
    img = np.zeros((200, 200, 3), dtype=np.uint8)

    # Add varied background (gradient pattern) to ensure non-singular covariance matrix
    # This simulates a real image with natural variation
    y_coords, x_coords = np.meshgrid(np.arange(200), np.arange(200), indexing='ij')

    # Create gradient background with variation
    img[:, :, 0] = ((x_coords + y_coords) % 50 + 20).astype(np.uint8)  # B channel: 20-69
    img[:, :, 1] = ((x_coords * 2 + y_coords) % 60 + 30).astype(np.uint8)  # G channel: 30-89
    img[:, :, 2] = ((x_coords + y_coords * 2) % 70 + 40).astype(np.uint8)  # R channel: 40-109

    # Add a region matching the target color RGB(100, 150, 200) = BGR(200, 150, 100)
    img[50:100, 50:100] = [200, 150, 100]
    return img


def test_matched_filter_service_initialization(matched_filter_service):
    """Test MatchedFilterService initialization."""
    assert matched_filter_service.name == 'MatchedFilter'
    assert len(matched_filter_service.color_configs) == 1


def test_matched_filter_service_legacy_format():
    """Test MatchedFilterService with legacy format."""
    options = {
        'selected_color': (100, 150, 200),
        'match_filter_threshold': 0.3
    }
    service = MatchedFilterService(
        identifier=(100, 150, 200),
        min_area=10,
        max_area=1000,
        aoi_radius=5,
        combine_aois=True,
        options=options
    )
    assert len(service.color_configs) == 1
    assert service.color_configs[0]['selected_color'] == (100, 150, 200)


def test_matched_filter_service_fallback():
    """Test MatchedFilterService fallback to identifier."""
    options = {}
    service = MatchedFilterService(
        identifier=(100, 150, 200),
        min_area=10,
        max_area=1000,
        aoi_radius=5,
        combine_aois=True,
        options=options
    )
    assert len(service.color_configs) == 1
    assert service.color_configs[0]['selected_color'] == (100, 150, 200)


def test_process_image_single_color(matched_filter_service, test_image):
    """Test processing with single color configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = tmpdir
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(input_dir, "test.jpg")

        result = matched_filter_service.process_image(test_image, full_path, input_dir, output_dir)

        assert isinstance(result, AnalysisResult)
        assert result.input_path == full_path
        assert result.error_message is None


def test_process_image_multiple_colors(test_image):
    """Test processing with multiple color configurations."""
    options = {
        'color_configs': [
            {
                'selected_color': (100, 150, 200),
                'match_filter_threshold': 0.3
            },
            {
                'selected_color': (200, 100, 50),
                'match_filter_threshold': 0.3
            }
        ]
    }
    service = MatchedFilterService(
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


def test_process_image_hue_expansion(matched_filter_service, test_image):
    """Test processing with hue expansion enabled."""
    matched_filter_service.options['hue_expansion_enabled'] = True
    matched_filter_service.options['hue_expansion_range'] = 10

    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = tmpdir
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(input_dir, "test.jpg")

        result = matched_filter_service.process_image(test_image, full_path, input_dir, output_dir)

        assert isinstance(result, AnalysisResult)
        assert result.error_message is None


def test_add_confidence_scores(matched_filter_service):
    """Test adding confidence scores to AOIs."""
    areas_of_interest = [
        {
            'center': (50, 50),
            'radius': 10,
            'detected_pixels': [(45, 45), (46, 46), (47, 47)]
        }
    ]

    filter_scores = np.zeros((100, 100), dtype=np.float32)
    filter_scores[45:48, 45:48] = 0.8  # High score = good match

    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[45:48, 45:48] = 1

    result = matched_filter_service._add_confidence_scores(
        areas_of_interest, filter_scores, mask
    )

    assert len(result) == 1
    assert 'confidence' in result[0]
    assert 'score_type' in result[0]
    assert result[0]['score_type'] == 'match'
