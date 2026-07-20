import traceback
from ast import literal_eval

import cv2
import numpy as np

from algorithms.AlgorithmService import AlgorithmService, AnalysisResult
from core.services.LoggerService import LoggerService
from core.services.thermal.ThermalParserService import ThermalParserService

try:
    from scipy.ndimage import median_filter, percentile_filter
except ImportError:  # pragma: no cover - scipy is a declared dependency, but keep a safe fallback
    median_filter = None
    percentile_filter = None


class ThermalResidualAnomalyService(AlgorithmService):
    """Local radiometric residual anomaly detector for thermal imagery."""

    DEFAULT_RESIDUAL_BINS = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0, np.inf], dtype=np.float32)
    SENSITIVITY_TO_SIGMA_MULTIPLIER = {
        1: 4.5,
        2: 4.0,
        3: 3.5,
        4: 3.0,
        5: 2.5,
        6: 2.1,
        7: 1.8,
        8: 1.5,
        9: 1.25,
        10: 1.0,
    }
    SENSITIVITY_TO_DELTA_T = {
        1: 8.0,
        2: 7.0,
        3: 6.0,
        4: 5.0,
        5: 4.0,
        6: 3.0,
        7: 2.0,
        8: 1.7,
        9: 1.3,
        10: 1.0,
    }

    def __init__(self, identifier, min_area, max_area, aoi_radius, combine_aois, options):
        self.logger = LoggerService()
        super().__init__('ThermalResidualAnomaly', identifier, min_area, max_area, aoi_radius, combine_aois, options, True)

        self.thermal_parser = ThermalParserService(dtype=np.float32)

        threshold_option = options.get('delta_t_threshold', options.get('threshold'))
        if threshold_option is not None:
            self.delta_t_threshold = self._coerce_float(threshold_option, 4.0, minimum=0.1)
            sensitivity_default = self._threshold_to_sensitivity(self.delta_t_threshold)
            self.sensitivity = self._coerce_int(options.get('sensitivity', sensitivity_default), sensitivity_default, minimum=1, maximum=10)
        else:
            self.sensitivity = self._coerce_int(options.get('sensitivity', 5), 5, minimum=1, maximum=10)
            self.delta_t_threshold = self._sensitivity_to_delta_t(self.sensitivity)

        self.sensitivity_sigma_multiplier = self._sensitivity_to_sigma_multiplier(self.sensitivity)
        score_option = options.get('score_threshold')
        self.score_threshold = self._coerce_float(score_option, 3.0, minimum=0.1) if score_option is not None else None
        self.direction = self._normalize_direction(options.get('type', 'Both'))

        self.background_method = self._normalize_background_method(options.get('background_method', 'median'))
        self.background_kernel = self._coerce_int(options.get('background_kernel', 51), 51, minimum=3)
        if self.background_kernel % 2 == 0:
            self.background_kernel += 1

        self.morph_kernel = self._coerce_int(options.get('morph_kernel', 3), 3, minimum=1)
        if self.morph_kernel % 2 == 0:
            self.morph_kernel += 1

        self.rarity_weight = self._coerce_float(options.get('rarity_weight', 0.35), 0.35, minimum=0.0, maximum=1.0)
        self.min_valid_fraction = self._coerce_float(options.get('min_valid_fraction', 0.7), 0.7, minimum=0.0, maximum=1.0)
        self.residual_bins_c = self._parse_residual_bins(options.get('residual_bins_c'))

        # Legacy option retained as no-op to preserve compatibility with persisted settings.
        self.legacy_segments = self._coerce_int(options.get('segments', 1), 1, minimum=1)

    def _sensitivity_to_delta_t(self, sensitivity):
        sensitivity = self._coerce_int(sensitivity, 5, minimum=1, maximum=10)
        return float(self.SENSITIVITY_TO_DELTA_T.get(sensitivity, 4.0))

    def _sensitivity_to_sigma_multiplier(self, sensitivity):
        sensitivity = self._coerce_int(sensitivity, 5, minimum=1, maximum=10)
        return float(self.SENSITIVITY_TO_SIGMA_MULTIPLIER.get(sensitivity, 2.5))

    def _threshold_to_sensitivity(self, threshold):
        threshold = self._coerce_float(threshold, 4.0, minimum=0.1)
        nearest = min(self.SENSITIVITY_TO_DELTA_T, key=lambda value: abs(self.SENSITIVITY_TO_DELTA_T[value] - threshold))
        return int(nearest)

    def _compute_effective_delta_t(self, robust_sigma):
        return max(self.delta_t_threshold, self.sensitivity_sigma_multiplier * float(robust_sigma))

    def _compute_effective_score_threshold(self):
        if self.score_threshold is not None:
            return self.score_threshold
        return self.sensitivity_sigma_multiplier

    def _coerce_float(self, value, default, minimum=None, maximum=None):
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            parsed = float(default)

        if minimum is not None:
            parsed = max(minimum, parsed)
        if maximum is not None:
            parsed = min(maximum, parsed)
        return parsed

    def _coerce_int(self, value, default, minimum=None, maximum=None):
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            parsed = int(default)

        if minimum is not None:
            parsed = max(minimum, parsed)
        if maximum is not None:
            parsed = min(maximum, parsed)
        return parsed

    def _normalize_direction(self, direction):
        normalized = str(direction or 'Both').strip().lower()

        if normalized in ('hot', 'above mean', 'above', 'warmer', 'warmer than surroundings'):
            return 'Hot'
        if normalized in ('cold', 'below mean', 'below', 'cooler', 'cooler than surroundings'):
            return 'Cold'
        return 'Both'

    def _normalize_background_method(self, method):
        normalized = str(method or 'median').strip().lower()

        if normalized in ('median', 'median_filter'):
            return 'median'
        if normalized in ('gaussian', 'gaussian_blur'):
            return 'gaussian'
        if normalized in ('morph_open', 'morphological_opening', 'opening'):
            return 'morph_open'
        if normalized in ('percentile', 'percentile_filter'):
            return 'percentile'
        return 'median'

    def _parse_residual_bins(self, bins_option):
        if bins_option is None:
            return self.DEFAULT_RESIDUAL_BINS.copy()

        bins_value = bins_option
        if isinstance(bins_option, str):
            try:
                bins_value = literal_eval(bins_option)
            except (ValueError, SyntaxError):
                return self.DEFAULT_RESIDUAL_BINS.copy()

        try:
            bins = np.asarray(list(bins_value), dtype=np.float32).flatten()
        except (TypeError, ValueError):
            return self.DEFAULT_RESIDUAL_BINS.copy()

        if bins.size == 0:
            return self.DEFAULT_RESIDUAL_BINS.copy()

        finite = bins[np.isfinite(bins)]
        finite = finite[finite >= 0.0]
        finite = np.unique(np.sort(finite))

        if finite.size == 0:
            return self.DEFAULT_RESIDUAL_BINS.copy()

        if finite[0] > 0.0:
            finite = np.insert(finite, 0, 0.0)

        parsed = np.concatenate((finite.astype(np.float32), np.array([np.inf], dtype=np.float32)))
        return parsed

    def _get_kernel_for_shape(self, shape):
        height, width = shape[:2]
        kernel = int(self.background_kernel)
        max_kernel = max(1, min(height, width))
        kernel = min(kernel, max_kernel)
        if kernel % 2 == 0 and kernel > 1:
            kernel -= 1
        return max(1, kernel)

    def _estimate_local_background(self, working_temp):
        kernel = self._get_kernel_for_shape(working_temp.shape)

        if kernel <= 1:
            return working_temp.copy()

        if self.background_method == 'gaussian':
            return cv2.GaussianBlur(
                working_temp,
                (kernel, kernel),
                sigmaX=0,
                sigmaY=0,
                borderType=cv2.BORDER_REPLICATE
            )

        if self.background_method == 'morph_open':
            struct = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel, kernel))
            return cv2.morphologyEx(working_temp, cv2.MORPH_OPEN, struct, borderType=cv2.BORDER_REPLICATE)

        if self.background_method == 'percentile' and percentile_filter is not None:
            return percentile_filter(working_temp, percentile=50.0, size=(kernel, kernel), mode='nearest').astype(np.float32)

        if median_filter is not None:
            return median_filter(working_temp, size=(kernel, kernel), mode='nearest').astype(np.float32)

        # Fallback path when scipy is unavailable.
        return cv2.GaussianBlur(
            working_temp,
            (kernel, kernel),
            sigmaX=0,
            sigmaY=0,
            borderType=cv2.BORDER_REPLICATE
        )

    def _build_candidate_masks(self, residual, score_map, finite_mask, effective_delta_t, effective_score_threshold):
        hot_residual = np.maximum(residual, 0.0)
        cold_residual = np.maximum(-residual, 0.0)

        hot_candidate = (hot_residual >= effective_delta_t) & (score_map >= effective_score_threshold) & finite_mask
        cold_candidate = (cold_residual >= effective_delta_t) & (-score_map >= effective_score_threshold) & finite_mask

        if self.direction == 'Hot':
            candidate_mask = hot_candidate
            anomaly_magnitude_map = hot_residual
        elif self.direction == 'Cold':
            candidate_mask = cold_candidate
            anomaly_magnitude_map = cold_residual
        else:
            candidate_mask = hot_candidate | cold_candidate
            anomaly_magnitude_map = np.abs(residual)

        return candidate_mask.astype(np.uint8), anomaly_magnitude_map.astype(np.float32), hot_candidate, cold_candidate

    def _cleanup_mask(self, binary_mask):
        if self.morph_kernel <= 1:
            return binary_mask

        kernel = np.ones((self.morph_kernel, self.morph_kernel), dtype=np.uint8)
        cleaned = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel, iterations=1)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=1)
        return cleaned

    def _build_rarity_map(self, anomaly_magnitude_map, binary_mask):
        rarity_map = np.zeros_like(anomaly_magnitude_map, dtype=np.float32)
        candidate_pixels = binary_mask > 0

        if not np.any(candidate_pixels):
            return rarity_map

        bucket_idx = np.digitize(anomaly_magnitude_map, self.residual_bins_c, right=False)
        valid_idx = bucket_idx[candidate_pixels]
        if valid_idx.size == 0:
            return rarity_map

        max_bucket = int(max(np.max(valid_idx), np.max(bucket_idx)))
        counts = np.bincount(valid_idx, minlength=max_bucket + 1).astype(np.float32)
        total = max(1.0, float(valid_idx.size))
        frequencies = counts / total

        inverse_frequency = np.zeros_like(frequencies, dtype=np.float32)
        present = frequencies > 0
        inverse_frequency[present] = 1.0 / frequencies[present]

        if np.any(present):
            max_inverse = float(np.max(inverse_frequency[present]))
            if max_inverse > 0.0:
                inverse_frequency /= max_inverse

        clipped_idx = np.clip(bucket_idx, 0, len(inverse_frequency) - 1)
        rarity_map = inverse_frequency[clipped_idx]
        return rarity_map.astype(np.float32)

    def _extract_valid_coordinates(self, detected_pixels, shape):
        if detected_pixels is None or len(detected_pixels) == 0:
            return None, None

        coords = np.asarray(detected_pixels, dtype=np.int32)
        if coords.ndim != 2 or coords.shape[1] < 2:
            return None, None

        xs = coords[:, 0]
        ys = coords[:, 1]

        max_h, max_w = shape[:2]
        in_bounds = (xs >= 0) & (xs < max_w) & (ys >= 0) & (ys < max_h)
        if not np.any(in_bounds):
            return None, None

        return xs[in_bounds], ys[in_bounds]

    def _extract_aoi_temperatures(self, areas_of_interest, temperature_c):
        if not areas_of_interest:
            return

        for aoi in areas_of_interest:
            xs, ys = self._extract_valid_coordinates(aoi.get('detected_pixels', []), temperature_c.shape)
            if xs is None:
                aoi['temperature'] = None
                continue

            values = temperature_c[ys, xs]
            finite_values = values[np.isfinite(values)]
            aoi['temperature'] = float(np.mean(finite_values)) if finite_values.size > 0 else None

    def _scale_aois_to_visual_space(self, areas_of_interest, temperature_shape, visual_shape):
        if not areas_of_interest:
            return

        thermal_h, thermal_w = temperature_shape[:2]
        visual_h, visual_w = visual_shape[:2]
        scale_x = visual_w / thermal_w
        scale_y = visual_h / thermal_h

        if scale_x == 1.0 and scale_y == 1.0:
            return

        for aoi in areas_of_interest:
            if 'center' in aoi:
                aoi['center'] = (int(aoi['center'][0] * scale_x), int(aoi['center'][1] * scale_y))
            if 'radius' in aoi:
                aoi['radius'] = int(aoi['radius'] * max(scale_x, scale_y))
            if 'detected_pixels' in aoi:
                aoi['detected_pixels'] = [(int(x * scale_x), int(y * scale_y)) for x, y in aoi['detected_pixels']]

    def _add_confidence_scores(self, areas_of_interest, anomaly_magnitude_map, score_map, rarity_map, binary_mask, finite_mask, hot_mask, cold_mask):
        if not areas_of_interest:
            return []

        enriched = []
        final_scores = []

        for aoi in areas_of_interest:
            xs, ys = self._extract_valid_coordinates(aoi.get('detected_pixels', []), anomaly_magnitude_map.shape)
            if xs is None:
                continue

            in_candidate = binary_mask[ys, xs] > 0
            finite_points = finite_mask[ys, xs]
            valid_fraction = float(np.mean(finite_points)) if finite_points.size > 0 else 0.0
            if valid_fraction < self.min_valid_fraction:
                continue

            usable = in_candidate & finite_points
            if not np.any(usable):
                continue

            sample_x = xs[usable]
            sample_y = ys[usable]

            residual_values = anomaly_magnitude_map[sample_y, sample_x]
            robust_values = np.abs(score_map[sample_y, sample_x])
            rarity_values = rarity_map[sample_y, sample_x]

            if residual_values.size == 0:
                continue

            mean_residual = float(np.mean(residual_values))
            max_residual = float(np.max(residual_values))
            p90_residual = float(np.percentile(residual_values, 90.0))
            mean_robust_score = float(np.mean(robust_values)) if robust_values.size > 0 else 0.0
            rarity_norm = float(np.mean(rarity_values)) if rarity_values.size > 0 else 0.0

            base_score = (0.5 * mean_residual) + (0.3 * max_residual) + (0.2 * p90_residual)
            final_score = base_score * (1.0 + (self.rarity_weight * rarity_norm))

            hot_count = int(np.count_nonzero(hot_mask[sample_y, sample_x]))
            cold_count = int(np.count_nonzero(cold_mask[sample_y, sample_x]))
            if hot_count > 0 and cold_count > 0:
                anomaly_direction = 'Both'
            elif hot_count > 0:
                anomaly_direction = 'Hot'
            elif cold_count > 0:
                anomaly_direction = 'Cold'
            else:
                anomaly_direction = self.direction if self.direction in ('Hot', 'Cold') else 'Both'

            aoi['raw_score'] = round(mean_residual, 3)
            aoi['score_type'] = 'delta_t_rarity'
            aoi['score_method'] = 'mean_max_p90_rarity'
            aoi['mean_residual_c'] = round(mean_residual, 3)
            aoi['max_residual_c'] = round(max_residual, 3)
            aoi['p90_residual_c'] = round(p90_residual, 3)
            aoi['mean_robust_score'] = round(mean_robust_score, 3)
            aoi['rarity_score'] = round(rarity_norm, 3)
            aoi['valid_fraction'] = round(valid_fraction, 3)
            aoi['anomaly_direction'] = anomaly_direction
            aoi['blob_score'] = round(float(final_score), 3)

            enriched.append(aoi)
            final_scores.append(float(final_score))

        if not enriched:
            return []

        scores = np.asarray(final_scores, dtype=np.float32)
        score_min = float(np.min(scores))
        score_max = float(np.max(scores))

        for idx, aoi in enumerate(enriched):
            if score_max > score_min:
                confidence = ((scores[idx] - score_min) / (score_max - score_min)) * 100.0
            else:
                confidence = 100.0 if scores[idx] > 0 else 0.0
            aoi['confidence'] = round(float(max(0.0, min(100.0, confidence))), 1)

        return enriched

    def process_image(self, img, full_path, input_dir, output_dir):
        try:
            temperature_c, _ = self.thermal_parser.parse_file(full_path)
            if temperature_c is None:
                raise ValueError('No radiometric temperature data found')

            temperature_c = np.asarray(temperature_c, dtype=np.float32)
            finite_mask = np.isfinite(temperature_c)
            if not np.any(finite_mask):
                raise ValueError('Radiometric temperature matrix contains no finite values')

            fill_value = float(np.nanmedian(temperature_c[finite_mask]))
            working_temp = np.where(finite_mask, temperature_c, fill_value)

            local_background = self._estimate_local_background(working_temp)

            residual = working_temp - local_background
            residual[~finite_mask] = 0.0

            residual_values = residual[finite_mask]
            residual_median = float(np.median(residual_values))
            mad = float(np.median(np.abs(residual_values - residual_median)))
            robust_sigma = max(1e-6, 1.4826 * mad)

            score_map = (residual - residual_median) / robust_sigma
            score_map[~finite_mask] = 0.0

            effective_delta_t = self._compute_effective_delta_t(robust_sigma)
            effective_score_threshold = self._compute_effective_score_threshold()
            binary_mask, anomaly_magnitude_map, hot_candidate, cold_candidate = self._build_candidate_masks(
                residual,
                score_map,
                finite_mask,
                effective_delta_t,
                effective_score_threshold
            )
            binary_mask = self._cleanup_mask(binary_mask)

            hot_mask = hot_candidate & (binary_mask > 0)
            cold_mask = cold_candidate & (binary_mask > 0)

            contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            areas_of_interest, base_contour_count = self.identify_areas_of_interest(temperature_c.shape, contours)

            if areas_of_interest:
                rarity_map = self._build_rarity_map(anomaly_magnitude_map, binary_mask)
                areas_of_interest = self._add_confidence_scores(
                    areas_of_interest,
                    anomaly_magnitude_map,
                    score_map,
                    rarity_map,
                    binary_mask,
                    finite_mask,
                    hot_mask,
                    cold_mask
                )

                if areas_of_interest:
                    self._extract_aoi_temperatures(areas_of_interest, temperature_c)
                    self._scale_aois_to_visual_space(areas_of_interest, temperature_c.shape, img.shape)

            output_path = self._construct_output_path(full_path, input_dir, output_dir)
            mask_path = None
            if areas_of_interest:
                mask_255 = binary_mask * 255
                mask_path = self.store_mask(full_path, output_path, mask_255, temperature_c, target_shape=img.shape)

            return AnalysisResult(full_path, mask_path, output_dir, areas_of_interest, base_contour_count)

        except Exception as e:
            self.logger.error(traceback.format_exc())
            self.logger.error(f'ThermalResidualAnomaly failed for {full_path}: {e}')
            return AnalysisResult(full_path, error_message=str(e))
