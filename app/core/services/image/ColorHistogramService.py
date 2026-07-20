"""
ColorHistogramService - Histogram and mask utilities for color imagery.
"""

import cv2
import numpy as np


class ColorHistogramService:
    """Business logic for color histogram visualization across multiple color spaces."""

    DEFAULT_BIN_COUNT = 128

    COLOR_SPACE_COMPONENTS = {
        'RGB': ('R', 'G', 'B'),
        'HSV': ('H', 'S', 'V'),
        'LAB': ('L*', 'a*', 'b*'),
    }

    COMPONENT_RANGES = {
        ('RGB', 'R'): (0.0, 255.0),
        ('RGB', 'G'): (0.0, 255.0),
        ('RGB', 'B'): (0.0, 255.0),
        ('HSV', 'H'): (0.0, 360.0),
        ('HSV', 'S'): (0.0, 100.0),
        ('HSV', 'V'): (0.0, 100.0),
        ('LAB', 'L*'): (0.0, 100.0),
        ('LAB', 'a*'): (-128.0, 127.0),
        ('LAB', 'b*'): (-128.0, 127.0),
    }

    DEFAULT_SELECTIONS = {
        'ColorRange': ('RGB', 'R'),
        'MatchedFilter': ('RGB', 'R'),
        'HSVColorRange': ('HSV', 'H'),
        'RXAnomaly': ('HSV', 'H'),
        'MRMap': ('LAB', 'a*'),
    }

    def get_default_selection(self, algorithm_name):
        """Return the preferred default color-space selection for an algorithm."""
        return self.DEFAULT_SELECTIONS.get(str(algorithm_name or ''), ('RGB', 'R'))

    def build_histogram_context(self, image_array, color_space, component, areas_of_interest=None, bin_count=None):
        """
        Build histogram data and component matrix for a color-space component.

        Returns:
            dict | None: Histogram context for the selected component.
        """
        component_matrix = self.build_component_matrix(image_array, color_space, component)
        if component_matrix is None:
            return None

        finite_mask = np.isfinite(component_matrix)
        if not np.any(finite_mask):
            return None

        minimum, maximum = self.COMPONENT_RANGES[(color_space, component)]
        histogram_bins, histogram_range = self._histogram_bins_and_range(color_space, component, bin_count)
        histogram_kwargs = {'bins': histogram_bins}
        if histogram_range is not None:
            histogram_kwargs['range'] = histogram_range
        counts, edges = np.histogram(component_matrix[finite_mask], **histogram_kwargs)

        anomaly_values = self._extract_aoi_component_values(component_matrix, areas_of_interest)
        if anomaly_values.size > 0:
            anomaly_counts = np.histogram(anomaly_values, bins=edges)[0]
        else:
            anomaly_counts = np.zeros_like(counts)
        centers = (edges[:-1] + edges[1:]) / 2.0

        return {
            'color_space': color_space,
            'component': component,
            'component_matrix': component_matrix.astype(np.float32),
            'display_suffix': self._display_suffix(color_space, component),
            'histogram_data': {
                'color_space': color_space,
                'component': component,
                'bin_edges': edges.astype(np.float32),
                'bin_centers': centers.astype(np.float32),
                'counts': counts.astype(np.int32),
                'anomaly_counts': anomaly_counts.astype(np.int32),
                'anomaly_overlay_mode': 'anomaly_count',
                'value_precision': self._value_precision(color_space, component),
                'min_temperature': float(minimum),
                'max_temperature': float(maximum),
                'total_pixels': int(np.count_nonzero(finite_mask)),
                'anomaly_pixels': int(anomaly_values.size),
            }
        }

    def build_component_matrix(self, image_array, color_space, component):
        """Convert an RGB image array into a selected component matrix."""
        if image_array is None:
            return None

        rgb = np.asarray(image_array, dtype=np.uint8)
        if rgb.ndim != 3 or rgb.shape[2] < 3:
            return None

        if color_space == 'RGB':
            component_index = {'R': 0, 'G': 1, 'B': 2}[component]
            return rgb[:, :, component_index].astype(np.float32)

        if color_space == 'HSV':
            hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
            if component == 'H':
                return hsv[:, :, 0] * 2.0
            if component == 'S':
                return (hsv[:, :, 1] / 255.0) * 100.0
            return (hsv[:, :, 2] / 255.0) * 100.0

        if color_space == 'LAB':
            lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
            if component == 'L*':
                return (lab[:, :, 0] / 255.0) * 100.0
            if component == 'a*':
                return lab[:, :, 1] - 128.0
            return lab[:, :, 2] - 128.0

        return None

    @staticmethod
    def build_component_mask(component_matrix, minimum=None, maximum=None, wrap=False):
        """Create a visibility mask for pixels inside the selected component band."""
        if component_matrix is None:
            return None

        values = np.asarray(component_matrix, dtype=np.float32)
        finite_mask = np.isfinite(values)
        visible = finite_mask.copy()
        if minimum is not None and maximum is not None and wrap:
            minimum = float(minimum)
            maximum = float(maximum)
            visible &= (values <= minimum) | (values >= maximum)
            return visible

        if minimum is not None:
            visible &= values >= float(minimum)
        if maximum is not None:
            visible &= values <= float(maximum)
        return visible

    def _extract_aoi_component_values(self, component_matrix, areas_of_interest=None):
        """Extract component values inside AOIs."""
        if component_matrix is None:
            return np.asarray([], dtype=np.float32)

        height, width = component_matrix.shape[:2]
        aoi_mask = np.zeros((height, width), dtype=bool)

        for aoi in areas_of_interest or []:
            pixels = aoi.get('detected_pixels') or []
            if pixels:
                for pixel in pixels:
                    if not isinstance(pixel, (list, tuple)) or len(pixel) < 2:
                        continue
                    x, y = int(pixel[0]), int(pixel[1])
                    if 0 <= x < width and 0 <= y < height:
                        aoi_mask[y, x] = True
                continue

            center = aoi.get('center')
            radius = int(aoi.get('radius', 0) or 0)
            if not center or radius <= 0:
                continue

            cx, cy = int(center[0]), int(center[1])
            for y in range(max(0, cy - radius), min(height, cy + radius + 1)):
                for x in range(max(0, cx - radius), min(width, cx + radius + 1)):
                    if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                        aoi_mask[y, x] = True

        if not np.any(aoi_mask):
            return np.asarray([], dtype=np.float32)

        finite_mask = np.isfinite(component_matrix)
        return component_matrix[aoi_mask & finite_mask].astype(np.float32)

    @staticmethod
    def _display_suffix(color_space, component):
        """Return a display suffix for a component."""
        if color_space == 'HSV' and component == 'H':
            return '°'
        if color_space in ('HSV', 'LAB') and component == 'L*':
            return '%'
        if color_space == 'HSV' and component in ('S', 'V'):
            return '%'
        return ''

    @staticmethod
    def _value_precision(color_space, component):
        """Return the preferred display precision for a component."""
        if color_space == 'HSV' and component == 'H':
            return 0
        return 1

    @classmethod
    def _histogram_bins_and_range(cls, color_space, component, bin_count):
        """Return histogram bin settings for a selected component."""
        if color_space == 'HSV' and component == 'H':
            return 72, (0.0, 360.0)
        minimum, maximum = cls.COMPONENT_RANGES[(color_space, component)]
        return max(8, int(bin_count or cls.DEFAULT_BIN_COUNT)), (minimum, maximum)
