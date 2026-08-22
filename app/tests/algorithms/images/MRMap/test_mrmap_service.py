import pytest
import numpy as np
import tempfile
import os
from algorithms.images.MRMap.services.MRMapService import MRMapService, Histogram, _percent_to_u8
from algorithms import DetectionExpansion
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


# ---------------------------------------------------------------------------
# Histogram equivalence: bincount fast path must reproduce np.histogramdd
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('colorspace', ['RGB', 'HSV', 'LAB'])
def test_histogram_matches_histogramdd(colorspace):
    """The fused-index bincount must equal the histogramdd it replaced."""
    rng = np.random.default_rng(42)
    img = rng.integers(0, 256, (120, 160, 3), dtype=np.uint8)
    if colorspace == 'HSV':
        img[:, :, 0] = rng.integers(0, 180, (120, 160), dtype=np.uint8)

    hist = Histogram(img, colorspace=colorspace)

    ch0_mapped = hist.mapping_ch0[img[:, :, 0]]
    ch1_mapped = hist.mapping_ch1[img[:, :, 1]]
    ch2_mapped = hist.mapping_ch2[img[:, :, 2]]
    from algorithms.images.MRMap.services.MRMapService import NUMBER_OF_QUANTIZED_HISTOGRAM_BINS as B
    reference, _ = np.histogramdd(
        (ch0_mapped.ravel(), ch1_mapped.ravel(), ch2_mapped.ravel()),
        bins=(B,) * 3, range=((0, B),) * 3
    )

    assert hist.q_histogram.dtype == reference.dtype
    assert np.array_equal(hist.q_histogram, reference)


def test_bin_count_matches_direct_indexing():
    """The flat-gather lookup must equal 3D fancy indexing of the histogram."""
    rng = np.random.default_rng(7)
    img = rng.integers(0, 256, (80, 100, 3), dtype=np.uint8)
    hist = Histogram(img, colorspace='LAB')

    ch0, ch1, ch2 = img[:, :, 0], img[:, :, 1], img[:, :, 2]
    counts = hist.bin_count(ch0, ch1, ch2)

    q0 = hist.mapping_ch0[ch0]
    q1 = hist.mapping_ch1[ch1]
    q2 = hist.mapping_ch2[ch2]
    reference = hist.q_histogram[q0, q1, q2]

    assert counts.shape == reference.shape
    assert np.array_equal(counts, reference)
    # Every pixel's own bin contains at least itself
    assert (hist.bin_count(ch0, ch1, ch2) >= 1).all()


def test_bin_count_for_image_matches_bin_count():
    """The cached-index fast path must equal the general lookup."""
    rng = np.random.default_rng(9)
    img = rng.integers(0, 256, (60, 90, 3), dtype=np.uint8)
    hist = Histogram(img, colorspace='LAB')

    fast = hist.bin_count_for_image()
    general = hist.bin_count(img[:, :, 0], img[:, :, 1], img[:, :, 2])

    assert fast.shape == (60, 90)
    assert np.array_equal(fast, general)

# ---------------------------------------------------------------------------
# Windowed expansion equivalence: _apply_expansion must reproduce the old
# full-frame implementation exactly, including window-regrowth and cap cases.
# ---------------------------------------------------------------------------


def _reference_apply_expansion(service, areas_of_interest, img_shape, expanded_bin_mask, hsv_img):
    """The pre-windowing full-frame implementation, kept as the oracle."""
    h, w = int(img_shape[0]), int(img_shape[1])
    combined_mask = np.zeros((h, w), dtype=np.uint8)

    for aoi in areas_of_interest:
        original_pixels = aoi.get('detected_pixels') or []
        if not original_pixels:
            continue
        coords = np.asarray(original_pixels, dtype=np.int32)
        seed_mask = np.zeros((h, w), dtype=bool)
        seed_mask[coords[:, 1], coords[:, 0]] = True

        contour = aoi.get('contour') or []
        if contour:
            xs = [int(p[0]) for p in contour]
            ys = [int(p[1]) for p in contour]
            cluster_rect = [min(xs), min(ys), max(xs), max(ys)]
        else:
            cluster_rect = [int(coords[:, 0].min()), int(coords[:, 1].min()),
                            int(coords[:, 0].max()), int(coords[:, 1].max())]

        safety_cap = DetectionExpansion.compute_safety_cap(cluster_rect)

        selected = seed_mask
        if expanded_bin_mask is not None:
            threshold_selected = DetectionExpansion.expand_threshold_mrmap(
                expanded_bin_mask, cluster_rect, (h, w))
            selected = seed_mask | threshold_selected

        if hsv_img is not None and service.hue_expansion > 0:
            seed_hues = hsv_img[coords[:, 1], coords[:, 0], 0]
            mean_hue = DetectionExpansion.circular_mean_hue(seed_hues)
            if mean_hue is not None:
                hue_ok = DetectionExpansion.hue_distance_mask(
                    hsv_img, mean_hue, service.hue_expansion,
                    sat_floor=service.hue_expansion_sat_floor,
                    val_floor=service.hue_expansion_val_floor)
                flooded, cap_hit = DetectionExpansion.expand_hue_flood(selected, hue_ok, safety_cap)
                if not cap_hit:
                    selected = flooded

        ys2, xs2 = np.where(selected)
        if len(xs2) == 0:
            continue
        aoi['detected_pixels'] = np.stack([xs2, ys2], axis=1).tolist()
        aoi['area'] = int(round(DetectionExpansion.convex_hull_area_from_mask(selected)))
        combined_mask[selected] = 255

    return areas_of_interest, combined_mask


def _expansion_service(**overrides):
    options = {'threshold': 4, 'segments': 1, 'window': 5, 'colorspace': 'HSV',
               'threshold_expansion': 400, 'hue_expansion': 5,
               'hue_expansion_sat_floor': 35, 'hue_expansion_val_floor': 20}
    options.update(overrides)
    return MRMapService((255, 255, 0), 1, 0, 15, True, options)


def _aoi_from_pixels(pixels):
    coords = np.asarray(pixels, dtype=np.int32)
    xmin, ymin = int(coords[:, 0].min()), int(coords[:, 1].min())
    xmax, ymax = int(coords[:, 0].max()), int(coords[:, 1].max())
    return {
        'center': (int(coords[:, 0].mean()), int(coords[:, 1].mean())),
        'radius': 10,
        'area': len(pixels),
        'contour': [[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]],
        'detected_pixels': [list(p) for p in pixels],
    }


def _assert_expansion_equivalent(service, aois, shape, expanded_bin_mask, hsv_img):
    import copy
    actual_aois = copy.deepcopy(aois)
    expected_aois = copy.deepcopy(aois)

    actual, actual_mask = service._apply_expansion(actual_aois, shape, expanded_bin_mask, hsv_img)
    expected, expected_mask = _reference_apply_expansion(
        service, expected_aois, shape, expanded_bin_mask, hsv_img)

    assert np.array_equal(actual_mask, expected_mask)
    for got, want in zip(actual, expected):
        assert sorted(map(tuple, got['detected_pixels'])) == sorted(map(tuple, want['detected_pixels']))
        assert got['area'] == want['area']


def test_windowed_expansion_matches_full_frame_locally():
    """A flood contained near the AOI must match the old full-frame result."""
    rng = np.random.default_rng(21)
    hsv = np.zeros((500, 700, 3), dtype=np.uint8)
    hsv[:, :, 0] = rng.integers(90, 140, (500, 700))  # background hues far from red
    hsv[:, :, 1] = 200
    hsv[:, :, 2] = 200
    # A red-ish patch around the seed for the hue flood to grab
    hsv[240:260, 340:365, 0] = 2
    seeds = [(350, 250), (351, 250), (350, 251)]
    aois = [_aoi_from_pixels(seeds)]

    bin_mask = np.zeros((500, 700), dtype=bool)
    bin_mask[245:255, 345:360] = True  # threshold expansion inside the rect area

    service = _expansion_service()
    _assert_expansion_equivalent(service, aois, hsv.shape, bin_mask, hsv)


def test_windowed_expansion_follows_long_ribbon_across_windows():
    """A hue-matching ribbon far longer than the initial window must be fully
    followed - the window regrows until the flood is contained."""
    hsv = np.zeros((400, 3000, 3), dtype=np.uint8)
    hsv[:, :, 0] = 120
    hsv[:, :, 1] = 200
    hsv[:, :, 2] = 200
    # Ribbon of seed-matching hue from x=100 to x=2900 at y=200
    hsv[199:202, 100:2900, 0] = 3
    seeds = [(150, 200), (151, 200)]
    aois = [_aoi_from_pixels(seeds)]

    service = _expansion_service()
    _assert_expansion_equivalent(service, aois, hsv.shape, None, hsv)

    # And the ribbon really was followed beyond the first window
    xs = [p[0] for p in aois and service._apply_expansion(
        [_aoi_from_pixels(seeds)], hsv.shape, None, hsv)[0][0]['detected_pixels']]
    assert max(xs) >= 2890


def test_windowed_expansion_cap_hit_matches_full_frame():
    """A hue region larger than the safety cap must trigger the cap in both
    implementations and keep the pre-hue selection."""
    hsv = np.zeros((600, 900, 3), dtype=np.uint8)
    hsv[:, :, 0] = 3       # the WHOLE image matches the seed hue
    hsv[:, :, 1] = 200
    hsv[:, :, 2] = 200
    seeds = [(450, 300), (451, 300)]
    aois = [_aoi_from_pixels(seeds)]

    service = _expansion_service()
    _assert_expansion_equivalent(service, aois, hsv.shape, None, hsv)


def test_windowed_expansion_at_image_corner():
    """Seeds at the frame corner: clamped windows must not distort results."""
    hsv = np.zeros((300, 300, 3), dtype=np.uint8)
    hsv[:, :, 0] = 120
    hsv[:, :, 1] = 200
    hsv[:, :, 2] = 200
    hsv[0:8, 0:8, 0] = 3
    seeds = [(1, 1), (2, 1)]
    aois = [_aoi_from_pixels(seeds)]

    service = _expansion_service()
    _assert_expansion_equivalent(service, aois, hsv.shape, None, hsv)


def test_windowed_threshold_expansion_connectivity_across_window_border():
    """Phase-B threshold connectivity that extends past the initial window
    must be followed via window regrowth."""
    shape = (400, 2600)
    bin_mask = np.zeros(shape, dtype=bool)
    # Rect area with expanded-threshold pixels, connected to a long tail
    bin_mask[195:206, 95:110] = True
    bin_mask[199:202, 110:2500] = True
    seeds = [(100, 200), (101, 200)]
    aois = [_aoi_from_pixels(seeds)]

    service = _expansion_service(hue_expansion=0)
    _assert_expansion_equivalent(service, aois, shape, bin_mask, None)
