"""
ThermalHistogramService - Histogram and mask utilities for thermal imagery.

Computes histogram data for thermal images, including anomaly-only overlays,
and generates boolean masks used to filter or highlight pixels in the viewer.
"""

import numpy as np


class ThermalHistogramService:
    """Business logic for thermal histogram visualization."""

    DEFAULT_BIN_COUNT = 128

    @staticmethod
    def _sanitize_temperature_data(temperature_data):
        """Return the finite temperature values and validity mask."""
        if temperature_data is None:
            return None, None

        values = np.asarray(temperature_data, dtype=np.float32)
        finite_mask = np.isfinite(values)
        if not np.any(finite_mask):
            return values, finite_mask

        return values, finite_mask

    def build_histogram_data(self, temperature_data, areas_of_interest=None, bin_count=None, temperature_unit='C'):
        """
        Build histogram line-series data for the full image and anomaly pixels.

        Args:
            temperature_data (np.ndarray): Temperature matrix aligned to image space.
            areas_of_interest (list | None): AOIs with optional ``detected_pixels``.
            bin_count (int | None): Number of histogram bins to compute.

        Returns:
            dict | None: Histogram metadata suitable for the histogram widget.
        """
        values, finite_mask = self._sanitize_temperature_data(temperature_data)
        if values is None or finite_mask is None or not np.any(finite_mask):
            return None

        finite_values = values[finite_mask]
        min_temp = float(np.min(finite_values))
        max_temp = float(np.max(finite_values))

        if np.isclose(min_temp, max_temp):
            max_temp = min_temp + 1.0

        bins = max(8, int(bin_count or self.DEFAULT_BIN_COUNT))
        counts, edges = np.histogram(finite_values, bins=bins, range=(min_temp, max_temp))

        anomaly_values = self._extract_anomaly_values(
            values,
            finite_mask,
            areas_of_interest,
            temperature_unit=temperature_unit
        )
        anomaly_counts, _ = np.histogram(anomaly_values, bins=edges) if anomaly_values.size > 0 else (np.zeros_like(counts), edges)

        centers = (edges[:-1] + edges[1:]) / 2.0

        return {
            'bin_edges': edges.astype(np.float32),
            'bin_centers': centers.astype(np.float32),
            'counts': counts.astype(np.int32),
            'anomaly_counts': anomaly_counts.astype(np.int32),
            'anomaly_overlay_mode': 'full_bin',
            'min_temperature': float(edges[0]),
            'max_temperature': float(edges[-1]),
            'total_pixels': int(finite_values.size),
            'anomaly_pixels': int(anomaly_values.size),
        }

    def _extract_anomaly_values(self, temperature_data, finite_mask, areas_of_interest=None, temperature_unit='C'):
        """
        Extract temperatures representing AOI/anomaly pixels or AOI temperatures.

        Prefer pixel-accurate temperatures when `detected_pixels` are available.
        Fall back to persisted AOI average temperatures so anomaly bars still render
        for datasets where only summary AOI data is available in the viewer.
        """
        anomaly_mask = self.build_anomaly_mask(temperature_data.shape, areas_of_interest)
        if anomaly_mask is not None and np.any(anomaly_mask):
            return temperature_data[finite_mask & anomaly_mask]

        aoi_temperatures = []
        for aoi in areas_of_interest or []:
            temperature = aoi.get('temperature')
            if temperature is None:
                continue

            try:
                temp_value = float(temperature)
            except (TypeError, ValueError):
                continue

            if np.isfinite(temp_value):
                if temperature_unit == 'F':
                    temp_value = (temp_value * 1.8) + 32.0
                aoi_temperatures.append(temp_value)

        if not aoi_temperatures:
            return np.asarray([], dtype=np.float32)

        return np.asarray(aoi_temperatures, dtype=np.float32)

    @staticmethod
    def build_anomaly_mask(shape, areas_of_interest=None):
        """Create a boolean image mask from AOI detected pixels."""
        if shape is None or len(shape) < 2:
            return None

        mask = np.zeros(shape[:2], dtype=bool)
        if not areas_of_interest:
            return mask

        max_y, max_x = mask.shape
        for aoi in areas_of_interest:
            for pixel in aoi.get('detected_pixels', []) or []:
                if not isinstance(pixel, (list, tuple)) or len(pixel) < 2:
                    continue

                x = int(pixel[0])
                y = int(pixel[1])
                if 0 <= x < max_x and 0 <= y < max_y:
                    mask[y, x] = True

        return mask

    @staticmethod
    def build_temperature_mask(temperature_data, minimum=None, maximum=None):
        """
        Create a visibility mask for pixels inside the selected temperature band.

        Args:
            temperature_data (np.ndarray): Temperature matrix aligned to image space.
            minimum (float | None): Inclusive lower bound.
            maximum (float | None): Inclusive upper bound.

        Returns:
            np.ndarray | None: Boolean visibility mask.
        """
        if temperature_data is None:
            return None

        values = np.asarray(temperature_data, dtype=np.float32)
        finite_mask = np.isfinite(values)
        if not np.any(finite_mask):
            return np.zeros(values.shape[:2], dtype=bool)

        visible = finite_mask.copy()
        if minimum is not None:
            visible &= values >= float(minimum)
        if maximum is not None:
            visible &= values <= float(maximum)
        return visible
