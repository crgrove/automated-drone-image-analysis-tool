import pytest
import numpy as np
import tempfile
import os
from algorithms.images.MRMap.services.MRMapService import MRMapService, Histogram, _percent_to_u8
from algorithms.AlgorithmService import AnalysisResult


@pytest.fixture
def mrmap_service():
    """Fixture providing an MRMapService instance."""
    options = {
        'threshold': 95,
        'segments': 2,
        'window': 3,
        'colorspace': 'RGB'
    }
    return MRMapService(
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


def test_mrmap_service_initialization(mrmap_service):
    """Test MRMapService initialization."""
    assert mrmap_service.name == 'MRMap'
    assert mrmap_service.segments == 2
    assert mrmap_service.threshold == 95
    assert mrmap_service.window_size == 3
    assert mrmap_service.colorspace == 'RGB'


def test_mrmap_service_hsv_colorspace():
    """Test MRMapService with HSV colorspace."""
    options = {
        'threshold': 95,
        'segments': 2,
        'window': 3,
        'colorspace': 'HSV'
    }
    service = MRMapService(
        identifier=(255, 0, 0),
        min_area=10,
        max_area=1000,
        aoi_radius=5,
        combine_aois=True,
        options=options
    )
    assert service.colorspace == 'HSV'


def test_mrmap_service_lab_colorspace():
    """Test MRMapService with LAB colorspace."""
    options = {
        'threshold': 95,
        'segments': 2,
        'window': 3,
        'colorspace': 'LAB'
    }
    service = MRMapService(
        identifier=(255, 0, 0),
        min_area=10,
        max_area=1000,
        aoi_radius=5,
        combine_aois=True,
        options=options
    )
    assert service.colorspace == 'LAB'


def test_process_image(mrmap_service, test_image):
    """Test processing an image with MRMap algorithm."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = tmpdir
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(input_dir, "test.jpg")

        result = mrmap_service.process_image(test_image, full_path, input_dir, output_dir)

        assert isinstance(result, AnalysisResult)
        assert result.input_path == full_path
        assert result.error_message is None


def test_mask_contains_only_flagged_pixels():
    """Mask must contain only actually flagged pixels, not filled bounding rectangles."""
    options = {'threshold': 95, 'segments': 1, 'window': 5, 'colorspace': 'RGB'}
    service = MRMapService(
        identifier=(255, 0, 0),
        min_area=3,
        max_area=0,
        aoi_radius=0,
        combine_aois=False,
        options=options,
    )

    pixel_anom = np.zeros((50, 50), dtype=bool)
    sparse_coords = [(10, 10), (12, 10), (14, 12), (10, 14), (14, 14)]
    for x, y in sparse_coords:
        pixel_anom[y, x] = True

    mask, clusters = service._getMRMapsContours(pixel_anom)

    assert len(clusters) == 1
    assert len(clusters[0]['pixels']) == len(sparse_coords)
    assert int(mask.sum() // 255) == len(sparse_coords)
    for x, y in sparse_coords:
        assert mask[y, x] == 255

    bounding_area = (14 - 10 + 1) * (14 - 10 + 1)
    assert int(mask.sum() // 255) < bounding_area


def test_build_aois_from_scattered_cluster():
    """A scattered BFS cluster must produce exactly one AOI with actual pixels."""
    options = {'threshold': 95, 'segments': 1, 'window': 5, 'colorspace': 'RGB'}
    service = MRMapService(
        identifier=(255, 0, 0),
        min_area=3,
        max_area=0,
        aoi_radius=2,
        combine_aois=False,
        options=options,
    )

    sparse_coords = [(10, 10), (12, 10), (14, 12), (10, 14), (14, 14)]
    pixel_anom = np.zeros((50, 50), dtype=bool)
    for x, y in sparse_coords:
        pixel_anom[y, x] = True

    mask, clusters = service._getMRMapsContours(pixel_anom)
    aois, base_count = service._build_aois_from_clusters(clusters, (50, 50, 3))

    assert base_count == 1
    assert len(aois) == 1
    aoi = aois[0]
    assert aoi['area'] == len(sparse_coords)
    assert len(aoi['detected_pixels']) == len(sparse_coords)
    returned = {tuple(p) for p in aoi['detected_pixels']}
    expected = set(sparse_coords)
    assert returned == expected
    assert len(aoi['contour']) == 4  # rectangle corners


def test_add_confidence_scores(mrmap_service):
    """Test adding confidence scores to AOIs."""
    areas_of_interest = [
        {
            'center': (50, 50),
            'radius': 10,
            'detected_pixels': [(45, 45), (46, 46), (47, 47)]
        }
    ]

    bin_counts = np.zeros((100, 100), dtype=np.float32)
    bin_counts[45:48, 45:48] = 5.0  # Low bin count = rare = anomaly

    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[45:48, 45:48] = 1

    result = mrmap_service._add_confidence_scores(
        areas_of_interest, bin_counts, mask
    )

    assert len(result) == 1
    assert 'confidence' in result[0]
    assert 'score_type' in result[0]
    assert result[0]['score_type'] == 'rarity'


# ---------------------------------------------------------------------------
# _percent_to_u8 helper
# ---------------------------------------------------------------------------

def test_percent_to_u8_clamps_in_range():
    assert _percent_to_u8(0) == 0
    assert _percent_to_u8(50) == 128
    assert _percent_to_u8(100) == 255


def test_percent_to_u8_clamps_out_of_range():
    assert _percent_to_u8(-10) == 0
    assert _percent_to_u8(150) == 255


def test_percent_to_u8_handles_invalid_input():
    assert _percent_to_u8(None) == 0
    assert _percent_to_u8("abc") == 0


# ---------------------------------------------------------------------------
# Rectangle helpers
# ---------------------------------------------------------------------------

def test_rectangles_overlap_separated(mrmap_service):
    assert mrmap_service._rectangles_overlap([0, 0, 5, 5], [10, 10, 15, 15]) is False


def test_rectangles_overlap_touching(mrmap_service):
    # Corner touching still counts as overlap (inclusive bounds)
    assert mrmap_service._rectangles_overlap([0, 0, 5, 5], [5, 5, 10, 10]) is True


def test_rectangles_overlap_contained(mrmap_service):
    assert mrmap_service._rectangles_overlap([0, 0, 10, 10], [2, 2, 4, 4]) is True


def test_merge_rectangles_covers_both(mrmap_service):
    merged = mrmap_service._merge_rectangles([0, 0, 5, 5], [3, 3, 10, 10])
    assert merged == [0, 0, 10, 10]


# ---------------------------------------------------------------------------
# Histogram mappings (colorspace-aware quantization)
# ---------------------------------------------------------------------------

def test_histogram_rgb_mapping_monotonic():
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    hist = Histogram(img, colorspace='RGB')
    # Mapping should be non-decreasing (values in 0..NUMBER_OF_QUANTIZED_HISTOGRAM_BINS-1)
    assert hist.mapping_ch0[0] == 0
    assert hist.mapping_ch0[255] == 25
    # All three channels use same mapping for RGB
    assert np.array_equal(hist.mapping_ch0, hist.mapping_ch1)
    assert np.array_equal(hist.mapping_ch1, hist.mapping_ch2)


def test_histogram_hsv_mapping_h_different_from_sv():
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    hist = Histogram(img, colorspace='HSV')
    # S and V share mapping; H has its own
    assert np.array_equal(hist.mapping_ch1, hist.mapping_ch2)
    assert not np.array_equal(hist.mapping_ch0, hist.mapping_ch1)


def test_histogram_lab_mapping_a_and_b_match():
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    hist = Histogram(img, colorspace='LAB')
    # A and B channels share mapping; L is standard
    assert np.array_equal(hist.mapping_ch1, hist.mapping_ch2)


def test_histogram_bin_count_returns_same_shape_as_input():
    img = np.random.randint(0, 255, (20, 20, 3), dtype=np.uint8)
    hist = Histogram(img, colorspace='RGB')
    counts = hist.bin_count(img[:, :, 0], img[:, :, 1], img[:, :, 2])
    assert counts.shape == (20, 20)


# ---------------------------------------------------------------------------
# Colorspace end-to-end paths through process_image
# ---------------------------------------------------------------------------

def test_process_image_hsv_colorspace(test_image):
    options = {'threshold': 95, 'segments': 2, 'window': 3, 'colorspace': 'HSV'}
    service = MRMapService(
        identifier=(255, 0, 0),
        min_area=10,
        max_area=1000,
        aoi_radius=5,
        combine_aois=False,
        options=options,
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        full_path = os.path.join(tmpdir, "test.jpg")
        result = service.process_image(test_image, full_path, tmpdir, tmpdir)
    assert isinstance(result, AnalysisResult)


def test_process_image_lab_colorspace(test_image):
    options = {'threshold': 95, 'segments': 2, 'window': 3, 'colorspace': 'LAB'}
    service = MRMapService(
        identifier=(255, 0, 0),
        min_area=10,
        max_area=1000,
        aoi_radius=5,
        combine_aois=False,
        options=options,
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        full_path = os.path.join(tmpdir, "test.jpg")
        result = service.process_image(test_image, full_path, tmpdir, tmpdir)
    assert isinstance(result, AnalysisResult)


def test_process_image_returns_error_on_exception(mrmap_service):
    # Passing None as img triggers an exception in shape extraction
    result = mrmap_service.process_image(None, "/fake/path.jpg", "/in", "/out")
    assert isinstance(result, AnalysisResult)
    assert result.error_message is not None


# ---------------------------------------------------------------------------
# _getMRMapsContours edge cases
# ---------------------------------------------------------------------------

def test_get_mrmaps_contours_empty_anomaly_mask():
    options = {'threshold': 95, 'segments': 1, 'window': 3, 'colorspace': 'RGB'}
    service = MRMapService(
        identifier=(255, 0, 0),
        min_area=5,
        max_area=0,
        aoi_radius=0,
        combine_aois=False,
        options=options,
    )
    pixel_anom = np.zeros((30, 30), dtype=bool)
    mask, clusters = service._getMRMapsContours(pixel_anom)
    assert clusters == []
    assert mask.sum() == 0


def test_get_mrmaps_contours_filters_below_min_area():
    options = {'threshold': 95, 'segments': 1, 'window': 1, 'colorspace': 'RGB'}
    service = MRMapService(
        identifier=(255, 0, 0),
        min_area=100,  # very high so nothing passes
        max_area=0,
        aoi_radius=0,
        combine_aois=False,
        options=options,
    )
    pixel_anom = np.zeros((30, 30), dtype=bool)
    pixel_anom[10:15, 10:15] = True  # 25 pixels, below min_area
    mask, clusters = service._getMRMapsContours(pixel_anom)
    assert clusters == []


def test_build_aois_filters_max_area():
    options = {'threshold': 95, 'segments': 1, 'window': 5, 'colorspace': 'RGB'}
    service = MRMapService(
        identifier=(255, 0, 0),
        min_area=1,
        max_area=5,  # very low; 25 pixels should filter out
        aoi_radius=0,
        combine_aois=False,
        options=options,
    )
    pixel_anom = np.zeros((30, 30), dtype=bool)
    pixel_anom[10:15, 10:15] = True
    mask, clusters = service._getMRMapsContours(pixel_anom)
    aois, base_count = service._build_aois_from_clusters(clusters, (30, 30, 3))
    assert aois is None
    assert base_count is None


def test_build_aois_empty_cluster_list():
    options = {'threshold': 95, 'segments': 1, 'window': 3, 'colorspace': 'RGB'}
    service = MRMapService(
        identifier=(255, 0, 0),
        min_area=1,
        max_area=0,
        aoi_radius=0,
        combine_aois=False,
        options=options,
    )
    aois, base_count = service._build_aois_from_clusters([], (30, 30, 3))
    assert aois is None
    assert base_count is None


def test_add_confidence_scores_skips_aoi_without_pixels(mrmap_service):
    areas = [{'center': (10, 10), 'radius': 5, 'detected_pixels': []}]
    bin_counts = np.ones((50, 50), dtype=np.float32)
    mask = np.zeros((50, 50), dtype=np.uint8)
    mask[10:12, 10:12] = 1

    result = mrmap_service._add_confidence_scores(areas, bin_counts, mask)
    assert result[0]['confidence'] == 0.0


def test_add_confidence_scores_empty_mask_returns_input(mrmap_service):
    areas = [{'center': (10, 10), 'radius': 5, 'detected_pixels': [(10, 10)]}]
    bin_counts = np.ones((50, 50), dtype=np.float32)
    mask = np.zeros((50, 50), dtype=np.uint8)  # no detected pixels

    result = mrmap_service._add_confidence_scores(areas, bin_counts, mask)
    # Returned unchanged when nothing in mask
    assert result is areas


# ---------------------------------------------------------------------------
# Expansion options
# ---------------------------------------------------------------------------

def test_mrmap_service_reads_expansion_options():
    options = {
        'threshold': 95,
        'segments': 1,
        'window': 3,
        'colorspace': 'RGB',
        'threshold_expansion': 5,
        'hue_expansion': 15,
        'hue_expansion_sat_floor': 20,
        'hue_expansion_val_floor': 30,
    }
    service = MRMapService(
        identifier=(255, 0, 0),
        min_area=1,
        max_area=0,
        aoi_radius=0,
        combine_aois=False,
        options=options,
    )
    assert service.threshold_expansion == 5
    assert service.hue_expansion == 15
    # Percentages converted to 0-255 scale
    assert service.hue_expansion_sat_floor == _percent_to_u8(20)
    assert service.hue_expansion_val_floor == _percent_to_u8(30)


def test_mrmap_service_defaults_for_missing_expansion_options():
    options = {'threshold': 95, 'segments': 1, 'window': 3, 'colorspace': 'RGB'}
    service = MRMapService(
        identifier=(255, 0, 0),
        min_area=1,
        max_area=0,
        aoi_radius=0,
        combine_aois=False,
        options=options,
    )
    assert service.threshold_expansion == 0
    assert service.hue_expansion == 0
    assert service.hue_expansion_sat_floor == 0
    assert service.hue_expansion_val_floor == 0


# ---------------------------------------------------------------------------
# _apply_expansion
# ---------------------------------------------------------------------------

def _service_with_expansion(**opts):
    options = {
        'threshold': 95, 'segments': 1, 'window': 3, 'colorspace': 'RGB',
        **opts,
    }
    return MRMapService(
        identifier=(255, 0, 0),
        min_area=1,
        max_area=0,
        aoi_radius=0,
        combine_aois=False,
        options=options,
    )


def test_apply_expansion_empty_pixels_skipped():
    service = _service_with_expansion(threshold_expansion=10)
    aois = [{'center': (10, 10), 'detected_pixels': [], 'contour': []}]
    result_aois, mask = service._apply_expansion(aois, (50, 50, 3), None, None)
    assert mask.sum() == 0


def test_apply_expansion_derives_rect_from_contour():
    service = _service_with_expansion(threshold_expansion=10)
    aois = [{
        'center': (15, 15),
        'detected_pixels': [(10, 10), (20, 20)],
        'contour': [[5, 5], [25, 5], [25, 25], [5, 25]],
    }]
    expanded_bin_mask = np.zeros((50, 50), dtype=bool)
    expanded_bin_mask[5:25, 5:25] = True
    result_aois, mask = service._apply_expansion(aois, (50, 50, 3), expanded_bin_mask, None)
    assert mask.sum() > 0


def test_apply_expansion_without_contour_uses_pixel_bounds():
    service = _service_with_expansion(threshold_expansion=10)
    aois = [{
        'center': (10, 10),
        'detected_pixels': [(8, 8), (12, 12)],
        # No contour key
    }]
    expanded_bin_mask = np.ones((50, 50), dtype=bool)
    result_aois, mask = service._apply_expansion(aois, (50, 50, 3), expanded_bin_mask, None)
    assert mask.sum() > 0


def test_apply_expansion_hue_path():
    service = _service_with_expansion(hue_expansion=10)
    aois = [{
        'center': (10, 10),
        'detected_pixels': [(8, 8), (12, 12)],
        'contour': [[5, 5], [15, 5], [15, 15], [5, 15]],
    }]
    hsv_img = np.zeros((50, 50, 3), dtype=np.uint8)
    hsv_img[:, :] = [90, 200, 200]  # uniform saturated
    result_aois, mask = service._apply_expansion(aois, (50, 50, 3), None, hsv_img)
    assert mask.sum() > 0


def test_apply_expansion_preserves_area_and_pixels():
    service = _service_with_expansion(threshold_expansion=10)
    aois = [{
        'center': (10, 10),
        'detected_pixels': [(8, 8), (12, 12)],
        'contour': [[5, 5], [15, 5], [15, 15], [5, 15]],
    }]
    expanded_bin_mask = np.zeros((50, 50), dtype=bool)
    expanded_bin_mask[5:16, 5:16] = True
    result_aois, _ = service._apply_expansion(aois, (50, 50, 3), expanded_bin_mask, None)
    aoi = result_aois[0]
    assert 'detected_pixels' in aoi
    assert 'area' in aoi
    assert aoi['area'] > 0


def test_process_image_with_threshold_expansion_and_hue():
    service = _service_with_expansion(
        threshold_expansion=10, hue_expansion=10,
        hue_expansion_sat_floor=10, hue_expansion_val_floor=10,
    )
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    with tempfile.TemporaryDirectory() as tmpdir:
        full_path = os.path.join(tmpdir, "test.jpg")
        result = service.process_image(img, full_path, tmpdir, tmpdir)
    assert isinstance(result, AnalysisResult)
