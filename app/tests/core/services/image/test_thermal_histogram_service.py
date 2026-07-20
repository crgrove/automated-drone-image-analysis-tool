"""Tests for ThermalHistogramService."""

import numpy as np

from core.services.image.ThermalHistogramService import ThermalHistogramService


def test_build_histogram_data_includes_anomaly_counts():
    """Histogram data should include both total and anomaly-only line series."""
    service = ThermalHistogramService()
    temperature_data = np.array(
        [
            [10.0, 11.0, 12.0],
            [13.0, 14.0, 15.0],
        ],
        dtype=np.float32
    )
    areas_of_interest = [
        {'detected_pixels': [(1, 0), (2, 1)]},
    ]

    histogram = service.build_histogram_data(temperature_data, areas_of_interest=areas_of_interest, bin_count=5)

    assert histogram is not None
    assert histogram['total_pixels'] == 6
    assert histogram['anomaly_pixels'] == 2
    assert int(histogram['counts'].sum()) == 6
    assert int(histogram['anomaly_counts'].sum()) == 2
    assert histogram['min_temperature'] == 10.0
    assert histogram['max_temperature'] == 15.0


def test_build_histogram_data_falls_back_to_aoi_temperatures():
    """Anomaly bins should still render when only AOI temperatures are available."""
    service = ThermalHistogramService()
    temperature_data = np.array(
        [
            [10.0, 11.0, 12.0],
            [13.0, 14.0, 15.0],
        ],
        dtype=np.float32
    )
    areas_of_interest = [
        {'temperature': 11.2},
        {'temperature': 14.4},
    ]

    histogram = service.build_histogram_data(temperature_data, areas_of_interest=areas_of_interest, bin_count=5)

    assert histogram is not None
    assert histogram['anomaly_pixels'] == 2
    assert int(histogram['anomaly_counts'].sum()) == 2


def test_build_histogram_data_converts_aoi_temperatures_to_fahrenheit():
    """Fallback AOI temperatures should be converted to the active histogram unit."""
    service = ThermalHistogramService()
    temperature_data = np.array(
        [
            [50.0, 60.0, 70.0],
            [80.0, 90.0, 100.0],
        ],
        dtype=np.float32
    )
    areas_of_interest = [
        {'temperature': 26.6667},  # 80 F
        {'temperature': 32.2222},  # 90 F
    ]

    histogram = service.build_histogram_data(
        temperature_data,
        areas_of_interest=areas_of_interest,
        bin_count=5,
        temperature_unit='F'
    )

    assert histogram is not None
    assert histogram['anomaly_pixels'] == 2
    assert int(histogram['anomaly_counts'].sum()) == 2
    assert np.count_nonzero(histogram['anomaly_counts']) >= 1


def test_build_temperature_mask_filters_to_requested_range():
    """Temperature masks should only keep pixels inside the requested band."""
    service = ThermalHistogramService()
    temperature_data = np.array(
        [
            [10.0, 12.0, 14.0],
            [16.0, np.nan, 18.0],
        ],
        dtype=np.float32
    )

    mask = service.build_temperature_mask(temperature_data, minimum=12.0, maximum=16.0)

    expected = np.array(
        [
            [False, True, True],
            [True, False, False],
        ]
    )
    assert np.array_equal(mask, expected)


def test_build_anomaly_mask_ignores_out_of_bounds_pixels():
    """Anomaly masks should safely ignore invalid detected pixel coordinates."""
    service = ThermalHistogramService()
    areas_of_interest = [
        {'detected_pixels': [(0, 0), (1, 1), (99, 99), (-1, 2)]},
    ]

    mask = service.build_anomaly_mask((3, 3), areas_of_interest)

    expected = np.zeros((3, 3), dtype=bool)
    expected[0, 0] = True
    expected[1, 1] = True
    assert np.array_equal(mask, expected)
