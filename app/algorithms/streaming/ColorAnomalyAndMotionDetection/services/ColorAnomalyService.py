"""
ColorAnomalyService.py - Color anomaly detection service

Handles color quantization-based anomaly detection for detecting rare colors.
"""

from core.services.LoggerService import LoggerService
from PySide6.QtCore import QObject
from threading import Lock
from typing import List
import time
import numpy as np
import cv2

# Import shared types
from .shared_types import Detection, ColorAnomalyAndMotionDetectionConfig


class ColorAnomalyService(QObject):
    """
    Color anomaly detection service for detecting rare/unusual colors in video streams.

    Uses histogram-based color quantization to identify colors that appear infrequently.
    """

    def __init__(self):
        super().__init__()
        self.logger = LoggerService()
        self.config_lock = Lock()

        # Pre-compute morphology kernels for efficiency
        self._morph_kernel_cache: dict = {}

    def update_config(self, config: ColorAnomalyAndMotionDetectionConfig):
        """Update color anomaly detection configuration."""
        with self.config_lock:
            pass  # Configuration is read-only for this service

    def _get_morph_kernel(self, size: int) -> np.ndarray:
        """Get cached morphology kernel."""
        if size not in self._morph_kernel_cache:
            self._morph_kernel_cache[size] = cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE, (size, size)
            )
        return self._morph_kernel_cache[size]

    def detect(self, frame_bgr: np.ndarray, config: ColorAnomalyAndMotionDetectionConfig,
               max_detections: int = 0) -> List[Detection]:
        """
        Detect color anomalies in a BGR frame.

        Args:
            frame_bgr: BGR color frame (already scaled to processing resolution)
            config: Detection configuration
            max_detections: Maximum number of detections to return (0 = unlimited)

        Returns:
            List of Detection objects for rare color regions
        """
        with self.config_lock:
            if not config.enable_color_quantization:
                return []

            return self._color_quantization_detect(frame_bgr, config, max_detections)

    def _color_quantization_detect(self, frame_bgr: np.ndarray, config: ColorAnomalyAndMotionDetectionConfig,
                                   max_detections: int = 0) -> List[Detection]:
        """Color quantization anomaly detection."""
        detections = []
        timestamp = time.time()

        # OPTIMIZATION: Downsample 2x for color analysis (4x fewer pixels = 4x faster)
        h_orig, w_orig = frame_bgr.shape[:2]
        downsampled = cv2.resize(frame_bgr, (w_orig // 2, h_orig // 2), interpolation=cv2.INTER_LINEAR)

        # Step 1: Quantize colors
        bits = config.color_quantization_bits
        scale = 2 ** (8 - bits)

        # Quantize by dividing and rounding
        quantized = (downsampled // scale).astype(np.uint8)

        # Step 2: Build histogram
        h, w = quantized.shape[:2]
        bins_per_channel = 2 ** bits

        # Vectorized index computation
        color_indices = (
            quantized[:, :, 0].astype(np.int32) +
            quantized[:, :, 1].astype(np.int32) * bins_per_channel +
            quantized[:, :, 2].astype(np.int32) * bins_per_channel ** 2
        )

        # Build histogram
        max_bins = bins_per_channel ** 3
        histogram = np.bincount(color_indices.ravel(), minlength=max_bins)

        # Step 3: Find rare color bins
        nonzero_counts = histogram[histogram > 0]
        if len(nonzero_counts) == 0:
            return detections

        total_pixels = h * w
        percentile_threshold = np.percentile(nonzero_counts, config.color_rarity_percentile)
        absolute_max = total_pixels * 0.05
        threshold = min(percentile_threshold, absolute_max)

        # Create mask of rare bins
        rare_bins = (histogram > 0) & (histogram < threshold)
        rare_bins[0] = False  # Don't mark bin 0 as rare

        # Step 4: Create binary mask of rare color pixels
        rare_mask_small = rare_bins[color_indices].astype(np.uint8) * 255

        # Upscale mask back to original processing resolution
        rare_mask = cv2.resize(rare_mask_small, (w_orig, h_orig), interpolation=cv2.INTER_NEAREST)

        # Morphology to clean up noise
        morph_kernel = self._get_morph_kernel(config.morphology_kernel_size)
        rare_mask = cv2.morphologyEx(rare_mask, cv2.MORPH_OPEN, morph_kernel)
        rare_mask = cv2.morphologyEx(rare_mask, cv2.MORPH_CLOSE, morph_kernel)

        # Step 5: Extract contours
        contours, _ = cv2.findContours(rare_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Process contours
        for contour in contours:
            if max_detections > 0 and len(detections) >= max_detections:
                break

            area = cv2.contourArea(contour)
            if area < config.color_min_detection_area or area > config.max_detection_area:
                continue

            x, y, w_box, h_box = cv2.boundingRect(contour)

            # Calculate centroid
            M = cv2.moments(contour)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = x + w_box // 2, y + h_box // 2

            # Get dominant color in this region
            region = frame_bgr[y:y + h_box, x:x + w_box]
            if region.size > 0:
                mean_color = region.mean(axis=(0, 1)).astype(int)
                dominant_color = tuple(mean_color.tolist())
            else:
                dominant_color = (0, 0, 0)

            # Confidence based on rarity
            cy_down = cy // 2
            cx_down = cx // 2
            if 0 <= cy_down < h and 0 <= cx_down < w:
                bin_idx = color_indices[cy_down, cx_down]
                bin_count = histogram[bin_idx]
                rarity = 1.0 - (bin_count / total_pixels)
                confidence = min(1.0, rarity * 2.0)
            else:
                confidence = 0.5
                bin_count = 0
                rarity = 0.5

            detection = Detection(
                bbox=(x, y, w_box, h_box),
                centroid=(cx, cy),
                area=area,
                confidence=confidence,
                detection_type='color_anomaly',
                timestamp=timestamp,
                contour=contour,
                metadata={
                    'algorithm': 'quantization',
                    'dominant_color': dominant_color,
                    'bin_count': int(bin_count),
                    'rarity': float(rarity)
                }
            )
            detections.append(detection)

        # Hue expansion: Expand detections to include neighboring similar-hue pixels
        if config.enable_hue_expansion and len(detections) > 0 and config.hue_expansion_range > 0:
            frame_hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
            expanded_detections = []
            for detection in detections:
                expanded = self._expand_detection_by_hue(frame_hsv, detection, config.hue_expansion_range)
                if expanded.area >= config.color_min_detection_area and expanded.area <= config.max_detection_area:
                    expanded_detections.append(expanded)
            detections = expanded_detections

        return detections

    def _expand_detection_by_hue(self, frame_hsv: np.ndarray, detection: Detection, hue_range: int) -> Detection:
        """Expand a color detection to include neighboring pixels with similar hue."""
        x, y, w, h = detection.bbox
        h_frame, w_frame = frame_hsv.shape[:2]

        # Bounds check
        x = max(0, min(x, w_frame - 1))
        y = max(0, min(y, h_frame - 1))
        w = min(w, w_frame - x)
        h = min(h, h_frame - y)

        if w <= 0 or h <= 0:
            return detection

        # Extract hue from detection region
        region_hsv = frame_hsv[y:y + h, x:x + w]
        mean_hue = float(region_hsv[:, :, 0].mean())

        # Create mask of pixels with similar hue in entire frame
        hue_channel = frame_hsv[:, :, 0].astype(np.float32)
        hue_min = mean_hue - hue_range
        hue_max = mean_hue + hue_range

        if hue_min < 0 or hue_max > 179:
            # Wraparound case
            if hue_min < 0:
                mask = ((hue_channel >= (180 + hue_min)) | (hue_channel <= hue_max)).astype(np.uint8) * 255
            else:
                mask = ((hue_channel >= hue_min) | (hue_channel <= (hue_max - 180))).astype(np.uint8) * 255
        else:
            mask = ((hue_channel >= hue_min) & (hue_channel <= hue_max)).astype(np.uint8) * 255

        # Morphology cleanup
        morph_kernel = self._get_morph_kernel(3)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, morph_kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, morph_kernel)

        # Find contours in expanded mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find the contour that contains the original detection centroid
        cx, cy = detection.centroid
        expanded_contour = None
        max_area = 0

        for contour in contours:
            if cv2.pointPolygonTest(contour, (float(cx), float(cy)), False) >= 0:
                area = cv2.contourArea(contour)
                if area > max_area:
                    expanded_contour = contour
                    max_area = area

        # If we found an expanded contour, create new detection
        if expanded_contour is not None and max_area > detection.area:
            x_new, y_new, w_new, h_new = cv2.boundingRect(expanded_contour)
            M = cv2.moments(expanded_contour)
            if M["m00"] > 0:
                cx_new = int(M["m10"] / M["m00"])
                cy_new = int(M["m01"] / M["m00"])
            else:
                cx_new, cy_new = x_new + w_new // 2, y_new + h_new // 2

            expanded_detection = Detection(
                bbox=(x_new, y_new, w_new, h_new),
                centroid=(cx_new, cy_new),
                area=max_area,
                confidence=detection.confidence,
                detection_type=detection.detection_type,
                timestamp=detection.timestamp,
                contour=expanded_contour,
                metadata={
                    **detection.metadata,
                    'hue_expanded': True,
                    'original_area': detection.area,
                    'expansion_ratio': max_area / detection.area if detection.area > 0 else 1.0
                }
            )
            return expanded_detection

        return detection
