"""Tests for ColorHistogramService."""

import numpy as np

from core.services.image.ColorHistogramService import ColorHistogramService


def test_build_component_matrix_for_hsv_hue():
    """HSV hue matrices should be converted into degree values."""
    service = ColorHistogramService()
    image_array = np.array(
        [
            [[255, 0, 0], [0, 255, 0]],
        ],
        dtype=np.uint8
    )

    component_matrix = service.build_component_matrix(image_array, 'HSV', 'H')

    assert component_matrix.shape == (1, 2)
    assert np.isclose(component_matrix[0, 0], 0.0)
    assert np.isclose(component_matrix[0, 1], 120.0, atol=2.0)


def test_build_histogram_context_uses_5_degree_bins_for_hsv_hue():
    """HSV hue histograms should use 5-degree bins and integer display precision."""
    service = ColorHistogramService()
    image_array = np.array(
        [
            [[255, 0, 0], [0, 255, 0], [0, 0, 255]],
        ],
        dtype=np.uint8
    )

    context = service.build_histogram_context(image_array, 'HSV', 'H')

    assert context is not None
    edges = context['histogram_data']['bin_edges']
    assert np.isclose(edges[1] - edges[0], 5.0)
    assert len(edges) == 73
    assert context['histogram_data']['value_precision'] == 0


def test_build_component_matrix_for_lab_a_component():
    """LAB a* matrices should include negative/positive perceptual values."""
    service = ColorHistogramService()
    image_array = np.array(
        [
            [[255, 0, 0], [0, 255, 0]],
        ],
        dtype=np.uint8
    )

    component_matrix = service.build_component_matrix(image_array, 'LAB', 'a*')

    assert component_matrix.shape == (1, 2)
    assert np.all(np.isfinite(component_matrix))
    assert component_matrix[0, 0] != component_matrix[0, 1]


def test_build_histogram_context_includes_aoi_overlay_counts():
    """AOI pixels should contribute to the overlay histogram counts."""
    service = ColorHistogramService()
    image_array = np.array(
        [
            [[255, 0, 0], [255, 0, 0], [0, 255, 0]],
            [[0, 255, 0], [0, 0, 255], [0, 0, 255]],
        ],
        dtype=np.uint8
    )
    areas_of_interest = [
        {'detected_pixels': [(0, 0), (1, 0)]},
    ]

    context = service.build_histogram_context(image_array, 'RGB', 'R', areas_of_interest=areas_of_interest, bin_count=8)

    assert context is not None
    assert context['histogram_data']['total_pixels'] == 6
    assert context['histogram_data']['anomaly_pixels'] == 2
    assert int(context['histogram_data']['anomaly_counts'].sum()) == 2
    assert context['histogram_data']['anomaly_overlay_mode'] == 'anomaly_count'


def test_build_histogram_context_deduplicates_overlapping_aoi_pixels():
    """Overlapping AOIs should not count the same pixel more than once."""
    service = ColorHistogramService()
    image_array = np.array(
        [
            [[255, 0, 0], [0, 255, 0]],
            [[0, 0, 255], [255, 255, 0]],
        ],
        dtype=np.uint8
    )
    areas_of_interest = [
        {'detected_pixels': [(0, 0), (1, 0)]},
        {'detected_pixels': [(0, 0)]},
    ]

    context = service.build_histogram_context(
        image_array,
        'RGB',
        'R',
        areas_of_interest=areas_of_interest,
        bin_count=8
    )

    assert context is not None
    assert context['histogram_data']['anomaly_pixels'] == 2
    assert int(context['histogram_data']['anomaly_counts'].sum()) == 2


def test_build_component_mask_filters_values_inside_range():
    """Component masks should only keep values inside the selected band."""
    service = ColorHistogramService()
    component_matrix = np.array(
        [
            [10.0, 20.0, 30.0],
            [40.0, 50.0, 60.0],
        ],
        dtype=np.float32
    )

    mask = service.build_component_mask(component_matrix, minimum=20.0, maximum=50.0)

    expected = np.array(
        [
            [False, True, True],
            [True, True, False],
        ]
    )
    assert np.array_equal(mask, expected)


def test_build_component_mask_supports_wrapped_hue_ranges():
    """Wrapped masks should keep hue values near both ends of the cycle."""
    service = ColorHistogramService()
    component_matrix = np.array(
        [
            [5.0, 25.0, 180.0],
            [340.0, 355.0, 120.0],
        ],
        dtype=np.float32
    )

    mask = service.build_component_mask(component_matrix, minimum=20.0, maximum=350.0, wrap=True)

    expected = np.array(
        [
            [True, False, False],
            [False, True, False],
        ]
    )
    assert np.array_equal(mask, expected)
