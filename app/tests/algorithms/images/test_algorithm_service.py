"""
Tests for the base AlgorithmService class.

This test file should be in algorithms/images/ to match the code structure.
The AlgorithmService base class is located at algorithms/AlgorithmService.py
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
from algorithms.AlgorithmService import AlgorithmService, AnalysisResult
import cv2
import numpy as np
from pathlib import Path
import tempfile
import os


class MockAlgorithmService(AlgorithmService):
    """Test implementation of AlgorithmService for testing base class functionality."""

    def process_image(self, img, full_path, input_dir, output_dir):
        """Simple test implementation that returns a basic result."""
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        # Create a simple test contour
        cv2.rectangle(mask, (10, 10), (50, 50), 255, -1)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        areas_of_interest, base_contour_count = self.identify_areas_of_interest(img.shape, contours)
        output_path = self._construct_output_path(full_path, input_dir, output_dir)
        return AnalysisResult(full_path, output_path, output_dir, areas_of_interest, base_contour_count)


@pytest.fixture
def algorithm_service():
    """Fixture providing a test AlgorithmService instance."""
    return MockAlgorithmService(
        name='TestAlgorithm',
        identifier_color=(255, 0, 0),
        min_area=10,
        max_area=1000,
        aoi_radius=5,
        combine_aois=True,
        options={'option1': 'value1'},
        is_thermal=False
    )


def test_algorithm_service_initialization(algorithm_service):
    """Test that AlgorithmService initializes correctly."""
    assert algorithm_service.name == 'TestAlgorithm'
    assert algorithm_service.identifier_color == (255, 0, 0)
    assert algorithm_service.min_area == 10
    assert algorithm_service.max_area == 1000
    assert algorithm_service.aoi_radius == 5
    assert algorithm_service.combine_aois is True
    assert algorithm_service.options == {'option1': 'value1'}
    assert algorithm_service.is_thermal is False
    assert algorithm_service.scale_factor == 1.0


def test_set_scale_factor(algorithm_service):
    """Test setting the scale factor."""
    algorithm_service.set_scale_factor(0.5)
    assert algorithm_service.scale_factor == 0.5


def test_transform_to_original_coords(algorithm_service):
    """Test coordinate transformation."""
    # No scaling
    x, y = algorithm_service.transform_to_original_coords(100, 200)
    assert x == 100
    assert y == 200

    # With scaling
    algorithm_service.set_scale_factor(0.5)
    x, y = algorithm_service.transform_to_original_coords(100, 200)
    assert x == 200
    assert y == 400


def test_transform_contour_to_original(algorithm_service):
    """Test contour transformation."""
    contour = np.array([[10, 20], [30, 40]], dtype=np.int32)

    # No scaling
    result = algorithm_service.transform_contour_to_original(contour)
    np.testing.assert_array_equal(result, contour)

    # With scaling
    algorithm_service.set_scale_factor(0.5)
    result = algorithm_service.transform_contour_to_original(contour)
    expected = np.array([[20, 40], [60, 80]], dtype=np.int32)
    np.testing.assert_array_equal(result, expected)


def test_collect_pixels_of_interest(algorithm_service):
    """Test collecting pixels of interest from a mask."""
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[10:20, 10:20] = 255

    pixels = algorithm_service.collect_pixels_of_interest(mask)
    assert len(pixels) > 0
    assert pixels.shape[1] == 2  # x, y coordinates


def test_identify_areas_of_interest_with_contours(algorithm_service):
    """Test identifying areas of interest from contours."""
    img_shape = (100, 100, 3)
    # Create a contour for a rectangle
    contour = np.array([[10, 10], [10, 30], [30, 30], [30, 10]], dtype=np.int32)
    contours = [contour]

    areas_of_interest, base_contour_count = algorithm_service.identify_areas_of_interest(img_shape, contours)

    assert areas_of_interest is not None
    assert len(areas_of_interest) > 0
    assert base_contour_count == 1
    assert 'center' in areas_of_interest[0]
    assert 'radius' in areas_of_interest[0]
    assert 'area' in areas_of_interest[0]
    assert 'contour' in areas_of_interest[0]
    assert 'detected_pixels' in areas_of_interest[0]


def test_identify_areas_of_interest_no_contours(algorithm_service):
    """Test identifying areas of interest with no contours."""
    img_shape = (100, 100, 3)
    contours = []

    areas_of_interest, base_contour_count = algorithm_service.identify_areas_of_interest(img_shape, contours)

    assert areas_of_interest is None
    assert base_contour_count is None


def test_identify_areas_of_interest_area_filtering(algorithm_service):
    """Test that areas are filtered by min_area and max_area."""
    img_shape = (100, 100, 3)

    # Small contour (should be filtered out by min_area)
    small_contour = np.array([[10, 10], [10, 12], [12, 12], [12, 10]], dtype=np.int32)

    # Large contour (should be filtered out by max_area)
    algorithm_service.max_area = 100
    large_contour = np.array([[10, 10], [10, 50], [50, 50], [50, 10]], dtype=np.int32)

    areas_of_interest, base_contour_count = algorithm_service.identify_areas_of_interest(
        img_shape, [small_contour, large_contour]
    )

    # Both contours should be filtered out: small by min_area, large by max_area
    assert base_contour_count == 0


def test_identify_areas_of_interest_combine_aois(algorithm_service):
    """Test combining overlapping AOIs."""
    img_shape = (100, 100, 3)
    algorithm_service.combine_aois = True

    # Create two overlapping contours
    contour1 = np.array([[10, 10], [10, 30], [30, 30], [30, 10]], dtype=np.int32)
    contour2 = np.array([[20, 20], [20, 40], [40, 40], [40, 20]], dtype=np.int32)
    contours = [contour1, contour2]

    areas_of_interest, base_contour_count = algorithm_service.identify_areas_of_interest(img_shape, contours)

    assert areas_of_interest is not None
    assert base_contour_count == 2
    # When combining, we might get fewer AOIs if they overlap
    assert len(areas_of_interest) <= 2


def test_construct_output_path(algorithm_service):
    """Test constructing output paths from input paths."""
    input_dir = "/input"
    output_dir = "/output"
    full_path = "/input/subdir/image.jpg"

    output_path = algorithm_service._construct_output_path(full_path, input_dir, output_dir)

    assert output_path == str(Path("/output/subdir/image.jpg"))


def test_construct_output_path_no_subdir(algorithm_service):
    """Test constructing output path when file is directly in input dir."""
    input_dir = "/input"
    output_dir = "/output"
    full_path = "/input/image.jpg"

    output_path = algorithm_service._construct_output_path(full_path, input_dir, output_dir)

    assert output_path == str(Path("/output/image.jpg"))


def test_store_mask(algorithm_service):
    """Test storing a mask as a TIFF file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = os.path.join(tmpdir, "input.jpg")
        output_file = os.path.join(tmpdir, "output.jpg")

        # Create a test mask
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[10:50, 10:50] = 255

        mask_path = algorithm_service.store_mask(input_file, output_file, mask)

        assert mask_path.endswith('.tif')
        assert os.path.exists(mask_path)


def test_store_mask_with_temperature(algorithm_service):
    """Test storing a mask with temperature data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = os.path.join(tmpdir, "input.jpg")
        output_file = os.path.join(tmpdir, "output.jpg")

        # Create a test mask
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[10:50, 10:50] = 255

        # Create temperature data
        temperature_data = np.ones((100, 100), dtype=np.float32) * 25.5

        mask_path = algorithm_service.store_mask(input_file, output_file, mask, temperature_data)

        assert mask_path.endswith('.tif')
        assert os.path.exists(mask_path)


def test_split_image(algorithm_service):
    """Test splitting an image into segments."""
    img = np.zeros((100, 100, 3), dtype=np.uint8)

    pieces = algorithm_service.split_image(img, segments=4, overlap=0)

    assert len(pieces) == 2  # 2 rows
    assert len(pieces[0]) == 2  # 2 columns
    assert pieces[0][0].shape[0] <= 50
    assert pieces[0][0].shape[1] <= 50


def test_split_image_with_overlap(algorithm_service):
    """Test splitting an image with overlap."""
    img = np.zeros((100, 100, 3), dtype=np.uint8)

    pieces = algorithm_service.split_image(img, segments=4, overlap=10)

    assert len(pieces) == 2
    assert len(pieces[0]) == 2


def test_glue_image(algorithm_service):
    """Test gluing image pieces back together."""
    # Create test pieces
    piece1 = np.ones((50, 50, 3), dtype=np.uint8) * 100
    piece2 = np.ones((50, 50, 3), dtype=np.uint8) * 200
    piece3 = np.ones((50, 50, 3), dtype=np.uint8) * 150
    piece4 = np.ones((50, 50, 3), dtype=np.uint8) * 250

    pieces = [[piece1, piece2], [piece3, piece4]]

    result = algorithm_service.glue_image(pieces)

    assert result.shape == (100, 100, 3)


def test_apply_hue_expansion(algorithm_service):
    """Test hue expansion functionality."""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    # Create a colored region
    img[10:50, 10:50] = [100, 150, 200]  # BGR

    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[20:30, 20:30] = 255

    areas_of_interest = [{
        'center': (30, 30),
        'radius': 20,
        'detected_pixels': [(25, 25), (26, 26), (27, 27)]
    }]

    expanded_mask = algorithm_service.apply_hue_expansion(img, mask, areas_of_interest, hue_range=10)

    assert expanded_mask.shape == mask.shape
    assert np.sum(expanded_mask) >= np.sum(mask)  # Should have at least as many pixels


def test_process_image(algorithm_service):
    """Test the process_image method returns an AnalysisResult."""
    img = np.zeros((100, 100, 3), dtype=np.uint8)

    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = tmpdir
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(input_dir, "test.jpg")

        result = algorithm_service.process_image(img, full_path, input_dir, output_dir)

        assert isinstance(result, AnalysisResult)
        assert result.input_path == full_path
        assert result.areas_of_interest is not None or result.error_message is not None


def test_analysis_result_initialization():
    """Test AnalysisResult initialization."""
    result = AnalysisResult(
        input_path="/input/image.jpg",
        output_path="output/image.jpg",
        output_dir="/output",
        areas_of_interest=[{'center': (50, 50), 'radius': 10}],
        base_contour_count=1
    )

    assert result.input_path == "/input/image.jpg"
    assert result.output_path == "output/image.jpg"
    assert result.areas_of_interest is not None
    assert result.base_contour_count == 1
    assert result.error_message is None


def test_analysis_result_with_error():
    """Test AnalysisResult with an error message."""
    result = AnalysisResult(
        input_path="/input/image.jpg",
        error_message="Test error"
    )

    assert result.input_path == "/input/image.jpg"
    assert result.error_message == "Test error"
    assert result.areas_of_interest is None
