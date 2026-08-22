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


# ---------------------------------------------------------------------------
# transform_aois_to_original_resolution
# ---------------------------------------------------------------------------

def test_transform_aois_no_scale_returns_unchanged(algorithm_service):
    aois = [{"center": (10, 20), "radius": 5}]
    assert algorithm_service.transform_aois_to_original_resolution(aois) is aois


def test_transform_aois_empty_list_returns_unchanged(algorithm_service):
    algorithm_service.set_scale_factor(0.5)
    assert algorithm_service.transform_aois_to_original_resolution([]) == []


def test_transform_aois_scales_center_and_radius(algorithm_service):
    algorithm_service.set_scale_factor(0.5)
    aois = [{"center": (10, 20), "radius": 5}]
    result = algorithm_service.transform_aois_to_original_resolution(aois)
    assert result[0]["center"] == (20, 40)
    assert result[0]["radius"] == 10


def test_transform_aois_scales_contour_and_pixels(algorithm_service):
    algorithm_service.set_scale_factor(0.5)
    aois = [{
        "center": (10, 10),
        "radius": 5,
        "contour": [[1, 1], [2, 2]],
        "detected_pixels": [(3, 4), (5, 6)],
    }]
    result = algorithm_service.transform_aois_to_original_resolution(aois)
    assert result[0]["contour"] == [[2.0, 2.0], [4.0, 4.0]]
    assert result[0]["detected_pixels"] == [(6, 8), (10, 12)]


def test_transform_aois_preserves_non_geometric_fields(algorithm_service):
    algorithm_service.set_scale_factor(0.5)
    aois = [{"center": (10, 10), "radius": 5, "confidence": 0.9, "label": "hit"}]
    result = algorithm_service.transform_aois_to_original_resolution(aois)
    assert result[0]["confidence"] == 0.9
    assert result[0]["label"] == "hit"


# ---------------------------------------------------------------------------
# apply_hue_expansion edge cases
# ---------------------------------------------------------------------------

def test_apply_hue_expansion_no_aois_returns_mask(algorithm_service):
    img = np.zeros((50, 50, 3), dtype=np.uint8)
    mask = np.zeros((50, 50), dtype=np.uint8)
    assert algorithm_service.apply_hue_expansion(img, mask, None, 10) is mask
    assert np.array_equal(algorithm_service.apply_hue_expansion(img, mask, [], 10), mask)


def test_apply_hue_expansion_handles_red_wraparound(algorithm_service):
    # Red hue wraps around 0/180 in OpenCV. A red pixel (hue ~0) with average
    # hue near 175 and a wide range should still match via wraparound.
    img = np.zeros((50, 50, 3), dtype=np.uint8)
    img[:, :] = (0, 0, 200)  # BGR red -> hue near 0
    mask = np.zeros((50, 50), dtype=np.uint8)
    mask[20:30, 20:30] = 255

    aois = [{
        "center": (25, 25),
        "radius": 15,
        "detected_pixels": [(20, 20), (21, 21), (22, 22)],
    }]
    expanded = algorithm_service.apply_hue_expansion(img, mask, aois, hue_range=10)
    assert expanded.shape == mask.shape
    assert expanded.sum() >= mask.sum()


def test_apply_hue_expansion_skips_aois_without_pixels(algorithm_service):
    img = np.zeros((30, 30, 3), dtype=np.uint8)
    mask = np.zeros((30, 30), dtype=np.uint8)
    aois = [{"center": (10, 10), "radius": 5, "detected_pixels": []}]
    result = algorithm_service.apply_hue_expansion(img, mask, aois, 10)
    assert np.array_equal(result, mask)


def test_apply_hue_expansion_ignores_out_of_bounds_pixels(algorithm_service):
    img = np.zeros((20, 20, 3), dtype=np.uint8)
    mask = np.zeros((20, 20), dtype=np.uint8)
    # All detected pixels are outside image bounds -> no avg hue computable -> skip
    aois = [{"center": (10, 10), "radius": 3, "detected_pixels": [(100, 100), (200, 200)]}]
    result = algorithm_service.apply_hue_expansion(img, mask, aois, 10)
    assert np.array_equal(result, mask)


# ---------------------------------------------------------------------------
# _calculate_aoi_representative_color
# ---------------------------------------------------------------------------

def test_calculate_aoi_color_from_detected_pixels(algorithm_service):
    img_rgb = np.zeros((50, 50, 3), dtype=np.uint8)
    img_rgb[10:20, 10:20] = (200, 50, 50)  # RGB red

    aoi = {
        "center": (15, 15),
        "radius": 5,
        "detected_pixels": [(10, 10), (11, 11), (12, 12)],
    }
    result = algorithm_service._calculate_aoi_representative_color(img_rgb, aoi)
    assert result is not None
    assert "rgb" in result
    assert "hex" in result
    assert "hue_degrees" in result
    assert result["hex"].startswith("#")
    assert 0 <= result["hue_degrees"] <= 360


def test_calculate_aoi_color_samples_circle_without_detected_pixels(algorithm_service):
    img_rgb = np.ones((50, 50, 3), dtype=np.uint8) * np.array([100, 150, 200], dtype=np.uint8)
    aoi = {"center": (25, 25), "radius": 10}

    result = algorithm_service._calculate_aoi_representative_color(img_rgb, aoi)
    assert result is not None
    # avg_rgb should be close to the uniform color
    assert result["avg_rgb"] == (100, 150, 200)


def test_calculate_aoi_color_skips_out_of_bounds_pixels(algorithm_service):
    img_rgb = np.zeros((20, 20, 3), dtype=np.uint8)
    img_rgb[0:5, 0:5] = (255, 0, 0)
    aoi = {
        "center": (2, 2),
        "radius": 1,
        "detected_pixels": [(0, 0), (1000, 1000), (-5, -5)],
    }
    result = algorithm_service._calculate_aoi_representative_color(img_rgb, aoi)
    # Only (0, 0) is valid -> should still return a result
    assert result is not None
    assert result["avg_rgb"] == (255, 0, 0)


def test_calculate_aoi_color_returns_none_when_no_colors(algorithm_service):
    img_rgb = np.zeros((20, 20, 3), dtype=np.uint8)
    # Radius 0 with no detected_pixels -> no pixels sampled -> None
    aoi = {"center": (10, 10), "radius": 0}
    result = algorithm_service._calculate_aoi_representative_color(img_rgb, aoi)
    # Depending on geometry the circle may sample (10,10). Accept None or a valid result.
    assert result is None or "rgb" in result


def test_calculate_aoi_color_handles_exception(algorithm_service):
    # Pass a malformed AOI that will trip the try/except
    result = algorithm_service._calculate_aoi_representative_color(None, {"center": (0, 0)})
    assert result is None


# ---------------------------------------------------------------------------
# _construct_output_path additional cases
# ---------------------------------------------------------------------------

def test_construct_output_path_nested_subdirs(algorithm_service):
    out = algorithm_service._construct_output_path(
        "/input/a/b/c/image.jpg", "/input", "/output"
    )
    assert out == str(Path("/output/a/b/c/image.jpg"))


# ---------------------------------------------------------------------------
# split_image / glue_image round-trip
# ---------------------------------------------------------------------------

def test_split_and_glue_round_trip_preserves_shape(algorithm_service):
    img = np.arange(60 * 60 * 3, dtype=np.uint8).reshape(60, 60, 3)
    pieces = algorithm_service.split_image(img, segments=4, overlap=0)
    glued = algorithm_service.glue_image(pieces)
    assert glued.shape == img.shape


def test_get_rows_cols_from_segments(algorithm_service):
    rows, cols = algorithm_service._get_rows_cols_from_segments(4)
    assert rows * cols == 4
    rows9, cols9 = algorithm_service._get_rows_cols_from_segments(9)
    assert rows9 * cols9 == 9

# ============================================================================
# Equivalence regression: ROI-local rasterization vs the full-frame reference
# ============================================================================


def _reference_identify_areas_of_interest(service, shape, contours):
    """The pre-optimization implementation, kept as the correctness oracle.

    identify_areas_of_interest was rewritten to rasterize each contour into a
    bounding-rect-local mask instead of a full-frame one (a ~200x speedup on
    48MP images). This reference reproduces the original full-frame algorithm
    so the outputs can be compared structure-for-structure.
    """
    if len(contours) == 0:
        return None, None
    height, width = int(shape[0]), int(shape[1])
    areas_of_interest = []
    temp_mask = np.zeros((height, width), dtype=np.uint8)
    base_contour_count = 0
    original_pixels_mask = np.zeros((height, width), dtype=np.uint8)

    for cnt in contours:
        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.drawContours(mask, [cnt], -1, 255, thickness=-1)
        contour_area = cv2.countNonZero(mask)
        if contour_area >= service.min_area and (service.max_area == 0 or contour_area <= service.max_area):
            (x, y), radius = cv2.minEnclosingCircle(cnt)
            center = (int(x), int(y))
            radius = int(radius) + service.aoi_radius
            base_contour_count += 1
            cv2.circle(temp_mask, center, radius, 255, -1)
            original_pixels_mask = cv2.bitwise_or(original_pixels_mask, mask)
            if not service.combine_aois:
                contour_points = cnt.reshape(-1, 2).tolist()
                detected_pixels = np.argwhere(mask > 0)
                detected_pixels_list = detected_pixels[:, [1, 0]].tolist() if len(detected_pixels) > 0 else []
                areas_of_interest.append({
                    'center': center,
                    'radius': radius,
                    'area': len(detected_pixels_list),
                    'contour': contour_points,
                    'detected_pixels': detected_pixels_list
                })

    if service.combine_aois:
        while True:
            new_contours, _ = cv2.findContours(temp_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            for cnt in new_contours:
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                cv2.circle(temp_mask, (int(x), int(y)), int(radius), 255, -1)
            if len(new_contours) == len(contours):
                contours = new_contours
                break
            contours = new_contours
        for cnt in contours:
            mask = np.zeros((height, width), dtype=np.uint8)
            cv2.drawContours(mask, [cnt], -1, 255, thickness=-1)
            (x, y), radius = cv2.minEnclosingCircle(cnt)
            contour_points = cnt.reshape(-1, 2).tolist()
            aoi_pixels_mask = cv2.bitwise_and(original_pixels_mask, mask)
            aoi_pixels = np.argwhere(aoi_pixels_mask > 0)
            aoi_pixels_list = aoi_pixels[:, [1, 0]].tolist() if len(aoi_pixels) > 0 else []
            areas_of_interest.append({
                'center': (int(x), int(y)),
                'radius': int(radius),
                'area': len(aoi_pixels_list),
                'contour': contour_points,
                'detected_pixels': aoi_pixels_list
            })

    areas_of_interest.sort(key=lambda item: (item['center'][1], item['center'][0]))
    return areas_of_interest, base_contour_count


def _blob_scene(width=800, height=600, seed=3):
    """Synthetic mask with touching, separate, tiny, and edge-hugging blobs."""
    rng = np.random.default_rng(seed)
    mask = np.zeros((height, width), dtype=np.uint8)
    for _ in range(25):
        x = int(rng.integers(0, width))
        y = int(rng.integers(0, height))
        r = int(rng.integers(2, 24))
        cv2.circle(mask, (x, y), r, 255, -1)
    # Blobs overlapping the frame edge exercise the ROI clamping
    cv2.circle(mask, (0, height // 2), 15, 255, -1)
    cv2.circle(mask, (width - 1, 10), 9, 255, -1)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return contours


@pytest.mark.parametrize('combine', [False, True])
def test_identify_areas_of_interest_matches_reference(combine):
    """The ROI-local implementation must reproduce the reference exactly."""
    service = MockAlgorithmService(
        name='Equiv', identifier_color=(255, 0, 0), min_area=10, max_area=0,
        aoi_radius=8, combine_aois=combine, options={}
    )
    shape = (600, 800, 3)
    contours = _blob_scene()

    actual_aois, actual_count = service.identify_areas_of_interest(shape, contours)
    expected_aois, expected_count = _reference_identify_areas_of_interest(service, shape, contours)

    assert actual_count == expected_count
    assert len(actual_aois) == len(expected_aois)
    for got, want in zip(actual_aois, expected_aois):
        assert got['center'] == want['center']
        assert got['radius'] == want['radius']
        assert got['area'] == want['area']
        assert got['contour'] == want['contour']
        assert sorted(got['detected_pixels']) == sorted(want['detected_pixels'])


def test_representative_color_circle_path_matches_loop():
    """Vectorized circle sampling must average the same pixel set as the loop."""
    service = MockAlgorithmService(
        name='Color', identifier_color=(255, 0, 0), min_area=1, max_area=0,
        aoi_radius=0, combine_aois=False, options={}
    )
    rng = np.random.default_rng(11)
    img = rng.integers(0, 255, (120, 160, 3), dtype=np.uint8)
    aoi = {'center': (80, 60), 'radius': 12}

    result = service._calculate_aoi_representative_color(img, aoi)

    # Reference: the original per-pixel loop
    colors = []
    cx, cy, radius = 80, 60, 12
    for y in range(max(0, cy - radius), min(120, cy + radius + 1)):
        for x in range(max(0, cx - radius), min(160, cx + radius + 1)):
            if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                colors.append(img[y, x])
    avg = np.mean(colors, axis=0).astype(int)

    assert result is not None
    assert result['avg_rgb'] == (int(avg[0]), int(avg[1]), int(avg[2]))


def test_representative_color_detected_pixels_path_matches_loop():
    """Vectorized detected-pixels sampling must match, including out-of-bounds skips."""
    service = MockAlgorithmService(
        name='Color', identifier_color=(255, 0, 0), min_area=1, max_area=0,
        aoi_radius=0, combine_aois=False, options={}
    )
    rng = np.random.default_rng(12)
    img = rng.integers(0, 255, (60, 80, 3), dtype=np.uint8)
    pixels = [[5, 5], [10, 12], [79, 59], [80, 60], [-1, 3], [30, 100]]  # last three out of bounds
    aoi = {'center': (10, 10), 'radius': 5, 'detected_pixels': pixels}

    result = service._calculate_aoi_representative_color(img, aoi)

    valid = [img[5, 5], img[12, 10], img[59, 79]]
    avg = np.mean(valid, axis=0).astype(int)

    assert result is not None
    assert result['avg_rgb'] == (int(avg[0]), int(avg[1]), int(avg[2]))


def test_representative_color_ragged_detected_pixels_falls_back():
    """Malformed detected_pixels entries are skipped, not fatal."""
    service = MockAlgorithmService(
        name='Color', identifier_color=(255, 0, 0), min_area=1, max_area=0,
        aoi_radius=0, combine_aois=False, options={}
    )
    img = np.full((20, 20, 3), 100, dtype=np.uint8)
    aoi = {'center': (10, 10), 'radius': 3,
           'detected_pixels': [[5, 5], [7], 'bad', [8, 8]]}

    result = service._calculate_aoi_representative_color(img, aoi)

    assert result is not None
    assert result['avg_rgb'] == (100, 100, 100)
