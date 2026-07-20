import os
import tempfile
from unittest.mock import MagicMock

import numpy as np
import pytest

from algorithms.AlgorithmService import AnalysisResult
from algorithms.images.ThermalResidualAnomaly.services.ThermalResidualAnomalyService import ThermalResidualAnomalyService


@pytest.fixture
def residual_service():
    options = {
        'sensitivity': 5,
        'type': 'Above Mean'
    }
    return ThermalResidualAnomalyService(
        identifier=(255, 0, 0),
        min_area=10,
        max_area=5000,
        aoi_radius=5,
        combine_aois=True,
        options=options
    )


def _build_background(height=220, width=240):
    yy, xx = np.indices((height, width))
    return 22.0 + (xx * 0.015) + (yy * 0.01)


def _run_service_with_temperature(service, temperature, visual_img):
    service.thermal_parser = MagicMock()
    service.thermal_parser.parse_file.return_value = (temperature.astype(np.float32), visual_img)

    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = os.path.join(tmpdir, 'input')
        output_dir = os.path.join(tmpdir, 'output')
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(input_dir, 'sample.jpg')
        return service.process_image(visual_img, full_path, input_dir, output_dir)


def test_initialization_maps_direction_options():
    hot_service = ThermalResidualAnomalyService((255, 0, 0), 10, 5000, 5, True, {'threshold': 4, 'type': 'Above Mean'})
    cold_service = ThermalResidualAnomalyService((255, 0, 0), 10, 5000, 5, True, {'threshold': 4, 'type': 'Cold'})
    both_service = ThermalResidualAnomalyService((255, 0, 0), 10, 5000, 5, True, {'threshold': 4, 'type': 'Both'})

    assert hot_service.direction == 'Hot'
    assert cold_service.direction == 'Cold'
    assert both_service.direction == 'Both'


def test_initialization_clamps_new_options_and_defaults():
    options = {
        'sensitivity': 42,
        'threshold': -1,
        'score_threshold': -2,
        'type': 'unknown',
        'background_method': 'invalid',
        'background_kernel': 2,
        'morph_kernel': 0,
        'rarity_weight': 9.0,
        'min_valid_fraction': 5.0,
        'residual_bins_c': 'not-a-list'
    }
    service = ThermalResidualAnomalyService((255, 0, 0), 10, 5000, 5, True, options)

    assert service.delta_t_threshold == 0.1
    assert service.sensitivity == 10
    assert service.sensitivity_sigma_multiplier == 1.0
    assert service.score_threshold == 0.1
    assert service.direction == 'Both'
    assert service.background_method == 'median'
    assert service.background_kernel >= 3 and service.background_kernel % 2 == 1
    assert service.morph_kernel >= 1 and service.morph_kernel % 2 == 1
    assert service.rarity_weight == 1.0
    assert service.min_valid_fraction == 1.0
    assert np.isinf(service.residual_bins_c[-1])


def test_process_image_detects_hot_local_residual_anomaly_with_median_background(residual_service):
    temperature = _build_background()
    temperature[80:125, 100:150] += 8.0
    visual_img = np.zeros((220, 240, 3), dtype=np.uint8)

    result = _run_service_with_temperature(residual_service, temperature, visual_img)

    assert isinstance(result, AnalysisResult)
    assert result.error_message is None
    assert result.areas_of_interest

    first_aoi = result.areas_of_interest[0]
    assert 'confidence' in first_aoi
    assert 'score_type' in first_aoi
    assert 'raw_score' in first_aoi
    assert first_aoi['score_type'] == 'delta_t_rarity'
    assert first_aoi['score_method'] == 'mean_max_p90_rarity'
    assert 0.0 <= first_aoi['confidence'] <= 100.0
    assert first_aoi.get('temperature') is not None
    assert 'mean_residual_c' in first_aoi
    assert 'max_residual_c' in first_aoi
    assert 'p90_residual_c' in first_aoi
    assert 'mean_robust_score' in first_aoi
    assert 'rarity_score' in first_aoi
    assert 'valid_fraction' in first_aoi
    assert 'anomaly_direction' in first_aoi


def test_process_image_detects_cold_anomaly_in_cold_mode():
    options = {'sensitivity': 6, 'type': 'Below Mean'}
    service = ThermalResidualAnomalyService((255, 0, 0), 10, 5000, 5, True, options)

    temperature = _build_background()
    temperature[60:110, 70:125] -= 7.0
    visual_img = np.zeros((220, 240, 3), dtype=np.uint8)

    result = _run_service_with_temperature(service, temperature, visual_img)

    assert result.error_message is None
    assert result.areas_of_interest
    assert any(aoi.get('raw_score', 0) > 0 for aoi in result.areas_of_interest)
    assert any(aoi.get('anomaly_direction') in ('Cold', 'Both') for aoi in result.areas_of_interest)


def test_segments_is_ignored_for_detection_behavior():
    base_options = {'sensitivity': 6, 'type': 'Both', 'background_kernel': 41, 'score_threshold': 2.5}
    service_a = ThermalResidualAnomalyService((255, 0, 0), 10, 5000, 5, True, {**base_options, 'segments': 1})
    service_b = ThermalResidualAnomalyService((255, 0, 0), 10, 5000, 5, True, {**base_options, 'segments': 36})

    temperature = _build_background()
    temperature[90:130, 90:130] += 7.0
    visual_img = np.zeros((220, 240, 3), dtype=np.uint8)

    result_a = _run_service_with_temperature(service_a, temperature, visual_img)
    result_b = _run_service_with_temperature(service_b, temperature, visual_img)

    assert result_a.error_message is None and result_b.error_message is None
    assert bool(result_a.areas_of_interest) == bool(result_b.areas_of_interest)
    if result_a.areas_of_interest and result_b.areas_of_interest:
        assert len(result_a.areas_of_interest) == len(result_b.areas_of_interest)


def test_robust_threshold_suppresses_false_positives_in_noisy_scene():
    options = {
        'sensitivity': 10,
        'delta_t_threshold': 0.5,
        'score_threshold': 5.0,
        'type': 'Both',
        'background_kernel': 31,
        'morph_kernel': 1
    }
    service = ThermalResidualAnomalyService((255, 0, 0), 10, 5000, 5, True, options)

    rng = np.random.default_rng(123)
    temperature = (22.0 + rng.normal(0.0, 0.8, size=(220, 240))).astype(np.float32)
    visual_img = np.zeros((220, 240, 3), dtype=np.uint8)

    result = _run_service_with_temperature(service, temperature, visual_img)

    assert result.error_message is None
    assert result.areas_of_interest in (None, [])


def test_quantized_rarity_map_favors_rare_residual_buckets():
    service = ThermalResidualAnomalyService((255, 0, 0), 10, 5000, 5, True, {'sensitivity': 7, 'type': 'Hot'})

    anomaly_map = np.array([[1.2, 1.1, 1.0, 1.3, 6.5]], dtype=np.float32)
    mask = np.array([[1, 1, 1, 1, 1]], dtype=np.uint8)

    rarity_map = service._build_rarity_map(anomaly_map, mask)

    assert rarity_map[0, 4] > rarity_map[0, 0]


def test_invalid_heavy_aoi_is_filtered_by_min_valid_fraction():
    service = ThermalResidualAnomalyService(
        (255, 0, 0),
        10,
        5000,
        5,
        True,
        {'sensitivity': 7, 'type': 'Both', 'min_valid_fraction': 0.8}
    )

    areas = [{'detected_pixels': [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)], 'center': (2, 0), 'radius': 2, 'area': 5}]
    anomaly_map = np.ones((1, 5), dtype=np.float32) * 3.0
    score_map = np.ones((1, 5), dtype=np.float32) * 4.0
    rarity_map = np.ones((1, 5), dtype=np.float32)
    binary_mask = np.ones((1, 5), dtype=np.uint8)
    finite_mask = np.array([[True, True, False, False, False]])
    hot_mask = np.ones((1, 5), dtype=bool)
    cold_mask = np.zeros((1, 5), dtype=bool)

    filtered = service._add_confidence_scores(areas, anomaly_map, score_map, rarity_map, binary_mask, finite_mask, hot_mask, cold_mask)

    assert filtered == []


def test_process_image_no_anomaly_returns_no_aois():
    options = {'sensitivity': 1, 'type': 'Both'}
    service = ThermalResidualAnomalyService((255, 0, 0), 10, 5000, 5, True, options)

    temperature = _build_background()
    visual_img = np.zeros((220, 240, 3), dtype=np.uint8)

    result = _run_service_with_temperature(service, temperature, visual_img)

    assert result.error_message is None
    assert result.areas_of_interest in (None, [])


def test_process_image_returns_error_for_missing_radiometric_data():
    service = ThermalResidualAnomalyService((255, 0, 0), 10, 5000, 5, True, {'sensitivity': 5, 'type': 'Both'})
    visual_img = np.zeros((64, 64, 3), dtype=np.uint8)

    service.thermal_parser = MagicMock()
    service.thermal_parser.parse_file.return_value = (None, visual_img)

    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = os.path.join(tmpdir, 'input')
        output_dir = os.path.join(tmpdir, 'output')
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(input_dir, 'missing.jpg')
        result = service.process_image(visual_img, full_path, input_dir, output_dir)

    assert result.error_message is not None
    assert 'radiometric' in result.error_message.lower()


def test_process_image_returns_error_for_non_finite_temperature_matrix():
    service = ThermalResidualAnomalyService((255, 0, 0), 10, 5000, 5, True, {'sensitivity': 5, 'type': 'Both'})
    visual_img = np.zeros((64, 64, 3), dtype=np.uint8)
    invalid_temperature = np.full((64, 64), np.nan, dtype=np.float32)

    service.thermal_parser = MagicMock()
    service.thermal_parser.parse_file.return_value = (invalid_temperature, visual_img)

    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = os.path.join(tmpdir, 'input')
        output_dir = os.path.join(tmpdir, 'output')
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(input_dir, 'invalid.jpg')
        result = service.process_image(visual_img, full_path, input_dir, output_dir)

    assert result.error_message is not None
    assert 'finite' in result.error_message.lower()


def test_sensitivity_maps_to_expected_delta_t_threshold():
    service_low = ThermalResidualAnomalyService((255, 0, 0), 10, 5000, 5, True, {'sensitivity': 1, 'type': 'Both'})
    service_mid = ThermalResidualAnomalyService((255, 0, 0), 10, 5000, 5, True, {'sensitivity': 5, 'type': 'Both'})
    service_high = ThermalResidualAnomalyService((255, 0, 0), 10, 5000, 5, True, {'sensitivity': 10, 'type': 'Both'})

    assert service_low.delta_t_threshold == 8.0
    assert service_mid.delta_t_threshold == 4.0
    assert service_high.delta_t_threshold == 1.0


def test_effective_thresholds_adapt_to_per_image_variability():
    service = ThermalResidualAnomalyService((255, 0, 0), 10, 5000, 5, True, {'sensitivity': 5, 'type': 'Both'})

    low_variability_delta_t = service._compute_effective_delta_t(0.4)
    high_variability_delta_t = service._compute_effective_delta_t(3.0)
    adaptive_score_threshold = service._compute_effective_score_threshold()

    assert low_variability_delta_t == 4.0
    assert high_variability_delta_t == pytest.approx(7.5, rel=1e-6)
    assert adaptive_score_threshold == pytest.approx(2.5, rel=1e-6)


def test_score_threshold_option_overrides_adaptive_multiplier():
    service = ThermalResidualAnomalyService(
        (255, 0, 0),
        10,
        5000,
        5,
        True,
        {'sensitivity': 9, 'score_threshold': 4.2, 'type': 'Both'}
    )

    assert service._compute_effective_score_threshold() == pytest.approx(4.2, rel=1e-6)
