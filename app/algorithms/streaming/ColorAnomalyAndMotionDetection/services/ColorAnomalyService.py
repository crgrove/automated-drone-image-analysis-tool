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
from .shared_types import Detection, ColorAnomalyAndMotionDetectionConfig, ContourMethod, ColorSpace


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

    def _extract_blobs_connected_components(self, binary_mask: np.ndarray, config: ColorAnomalyAndMotionDetectionConfig,
                                             timestamp: float, frame_bgr: np.ndarray,
                                             color_indices: np.ndarray, histogram: np.ndarray,
                                             total_pixels: int, max_detections: int = 0,
                                             color_space: str = 'bgr') -> List[Detection]:
        """
        Extract blobs using cv2.connectedComponentsWithStats.

        This is an alternative to findContours that provides direct access to blob statistics
        in a single pass.

        Args:
            binary_mask: Binary mask of rare color pixels
            config: Detection configuration
            timestamp: Frame timestamp
            frame_bgr: Original BGR frame for color extraction
            color_indices: Quantized color indices for confidence calculation
            histogram: Color histogram for rarity calculation
            total_pixels: Total pixels in frame
            max_detections: Maximum detections to return (0 = unlimited)

        Returns:
            List of Detection objects
        """
        detections = []
        h, w = binary_mask.shape[:2]

        # Apply connected components with statistics
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            binary_mask, connectivity=8, ltype=cv2.CV_32S
        )

        # Label 0 is background, skip it
        # Process ALL components (no early stopping - we sort by rarity first)
        for label_idx in range(1, num_labels):
            # Get statistics for this component
            x = stats[label_idx, cv2.CC_STAT_LEFT]
            y = stats[label_idx, cv2.CC_STAT_TOP]
            w_box = stats[label_idx, cv2.CC_STAT_WIDTH]
            h_box = stats[label_idx, cv2.CC_STAT_HEIGHT]
            area = stats[label_idx, cv2.CC_STAT_AREA]

            # Filter by area
            if area < config.color_min_detection_area or area > config.max_detection_area:
                continue

            # Get centroid
            cx, cy = int(centroids[label_idx][0]), int(centroids[label_idx][1])

            # Create component mask for this blob (reused for color and contour)
            component_mask = (labels == label_idx).astype(np.uint8) * 255

            # Get dominant color from ONLY the detected pixels (not entire bbox)
            # This ensures color exclusion and rendering use the actual detected color
            region = frame_bgr[y:y + h_box, x:x + w_box]
            region_mask = component_mask[y:y + h_box, x:x + w_box]
            if region.size > 0 and np.any(region_mask):
                # cv2.mean returns (B, G, R, 0) when using mask
                mean_color = cv2.mean(region, mask=region_mask)[:3]
                dominant_color = tuple(int(c) for c in mean_color)
            else:
                dominant_color = (0, 0, 0)

            # Calculate confidence based on rarity
            if 0 <= cy < h and 0 <= cx < w:
                bin_idx = color_indices[cy, cx]
                bin_count = histogram[bin_idx]
                rarity = 1.0 - (bin_count / total_pixels)
                confidence = min(1.0, rarity * 2.0)
            else:
                confidence = 0.5
                bin_count = 0
                rarity = 0.5

            # Create contour from component mask for compatibility with rendering
            contours, _ = cv2.findContours(component_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contour = contours[0] if contours else None

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
                    'color_space': color_space,
                    'contour_method': 'connected_components',
                    'dominant_color': dominant_color,
                    'bin_count': int(bin_count),
                    'rarity': float(rarity)
                }
            )
            detections.append(detection)

        # Sort by rarity (lowest bin_count = rarest) and apply max_detections limit
        if len(detections) > 0:
            detections.sort(key=lambda d: d.metadata.get('bin_count', float('inf')))
            if max_detections > 0 and len(detections) > max_detections:
                detections = detections[:max_detections]

        return detections

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
        """Color quantization anomaly detection - routes to appropriate color space method."""
        # Route to appropriate color space implementation
        if config.color_space == ColorSpace.HSV:
            return self._hsv_hue_detect(frame_bgr, config, max_detections)
        elif config.color_space == ColorSpace.LAB:
            return self._lab_ab_detect(frame_bgr, config, max_detections)
        else:
            return self._bgr_detect(frame_bgr, config, max_detections)

    def _bgr_detect(self, frame_bgr: np.ndarray, config: ColorAnomalyAndMotionDetectionConfig,
                    max_detections: int = 0) -> List[Detection]:
        """BGR color space anomaly detection (original 3D histogram method)."""
        detections = []
        timestamp = time.time()

        # Use frame at processing resolution (no downsampling - respects user-specified resolution)
        h, w = frame_bgr.shape[:2]

        # Step 1: Quantize colors
        bits = config.color_quantization_bits
        scale = 2 ** (8 - bits)

        # Quantize by dividing and rounding
        quantized = (frame_bgr // scale).astype(np.uint8)

        # Step 2: Build histogram
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

        # Step 4: Create binary mask of rare color pixels at processing resolution
        rare_mask = rare_bins[color_indices].astype(np.uint8) * 255

        # Morphology to clean up noise
        morph_kernel = self._get_morph_kernel(config.morphology_kernel_size)
        rare_mask = cv2.morphologyEx(rare_mask, cv2.MORPH_OPEN, morph_kernel)
        rare_mask = cv2.morphologyEx(rare_mask, cv2.MORPH_CLOSE, morph_kernel)

        # Step 5: Extract blobs using configured method
        if config.contour_method == ContourMethod.CONNECTED_COMPONENTS:
            # Use connected components - returns detections directly
            detections = self._extract_blobs_connected_components(
                rare_mask, config, timestamp, frame_bgr,
                color_indices, histogram, total_pixels, max_detections,
                color_space='bgr'
            )
        else:
            # Default: use findContours
            contours, _ = cv2.findContours(rare_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Process ALL contours (no early stopping - we sort by rarity first)
            for contour in contours:
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

                # Get dominant color from ONLY the detected pixels (not entire bbox)
                # Create mask from contour and use it to extract only detected pixel colors
                region = frame_bgr[y:y + h_box, x:x + w_box]
                if region.size > 0:
                    # Create local mask by drawing contour shifted to bbox origin
                    contour_mask = np.zeros((h_box, w_box), dtype=np.uint8)
                    shifted_contour = contour - np.array([x, y])
                    cv2.drawContours(contour_mask, [shifted_contour], -1, 255, -1)
                    # cv2.mean returns (B, G, R, 0) when using mask
                    mean_color = cv2.mean(region, mask=contour_mask)[:3]
                    dominant_color = tuple(int(c) for c in mean_color)
                else:
                    dominant_color = (0, 0, 0)

                # Confidence based on rarity (use full resolution coordinates)
                if 0 <= cy < h and 0 <= cx < w:
                    bin_idx = color_indices[cy, cx]
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
                        'color_space': 'bgr',
                        'dominant_color': dominant_color,
                        'bin_count': int(bin_count),
                        'rarity': float(rarity)
                    }
                )
                detections.append(detection)

            # Sort by rarity (lowest bin_count = rarest) and apply max_detections limit
            if len(detections) > 0:
                detections.sort(key=lambda d: d.metadata.get('bin_count', float('inf')))
                if max_detections > 0 and len(detections) > max_detections:
                    detections = detections[:max_detections]

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

    def _hsv_hue_detect(self, frame_bgr: np.ndarray, config: ColorAnomalyAndMotionDetectionConfig,
                        max_detections: int = 0) -> List[Detection]:
        """
        HSV Hue-based anomaly detection (1D histogram on Hue channel).

        Lighting-invariant detection that groups colors by hue regardless of brightness.
        Filters out low-saturation pixels (grays/whites/blacks) where hue is meaningless.
        """
        detections = []
        timestamp = time.time()

        h, w = frame_bgr.shape[:2]
        total_pixels = h * w

        # Convert to HSV
        frame_hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

        # Extract channels
        hue = frame_hsv[:, :, 0]  # 0-179 in OpenCV
        saturation = frame_hsv[:, :, 1]  # 0-255

        # Create mask for pixels with sufficient saturation (filter out grays)
        saturation_mask = saturation >= config.hsv_min_saturation

        # Quantize hue values
        # OpenCV Hue is 0-179, so max bins is 180
        bits = min(config.color_quantization_bits, 8)
        if bits >= 8:
            # Full resolution - use raw hue values (0-179)
            hue_indices = hue.astype(np.int32)
            max_bins = 180
        else:
            # Quantize hue
            bins_count = 2 ** bits
            # Scale 0-179 to 0-(bins_count-1)
            hue_indices = (hue.astype(np.int32) * bins_count // 180).clip(0, bins_count - 1)
            max_bins = bins_count

        # Build histogram only from saturated pixels
        valid_hues = hue_indices[saturation_mask]
        if len(valid_hues) == 0:
            return detections

        histogram = np.bincount(valid_hues.ravel(), minlength=max_bins)

        # Find rare hue bins
        nonzero_counts = histogram[histogram > 0]
        if len(nonzero_counts) == 0:
            return detections

        valid_pixel_count = len(valid_hues)
        percentile_threshold = np.percentile(nonzero_counts, config.color_rarity_percentile)
        absolute_max = valid_pixel_count * 0.05
        threshold = min(percentile_threshold, absolute_max)

        # Create mask of rare bins
        rare_bins = (histogram > 0) & (histogram < threshold)

        # Create binary mask: pixel is rare if it has sufficient saturation AND rare hue
        rare_hue_mask = rare_bins[hue_indices]
        rare_mask = (rare_hue_mask & saturation_mask).astype(np.uint8) * 255

        # Morphology to clean up noise
        morph_kernel = self._get_morph_kernel(config.morphology_kernel_size)
        rare_mask = cv2.morphologyEx(rare_mask, cv2.MORPH_OPEN, morph_kernel)
        rare_mask = cv2.morphologyEx(rare_mask, cv2.MORPH_CLOSE, morph_kernel)

        # Extract blobs using configured method
        if config.contour_method == ContourMethod.CONNECTED_COMPONENTS:
            detections = self._extract_blobs_connected_components(
                rare_mask, config, timestamp, frame_bgr,
                hue_indices, histogram, valid_pixel_count, max_detections,
                color_space='hsv'
            )
        else:
            detections = self._extract_blobs_find_contours(
                rare_mask, config, timestamp, frame_bgr,
                hue_indices, histogram, valid_pixel_count, max_detections,
                color_space='hsv'
            )

        return detections

    def _lab_ab_detect(self, frame_bgr: np.ndarray, config: ColorAnomalyAndMotionDetectionConfig,
                       max_detections: int = 0) -> List[Detection]:
        """
        LAB a,b-based anomaly detection (2D histogram on a,b channels).

        Lighting-invariant detection using perceptually uniform color space.
        Filters out low-chroma pixels (near-neutral grays) where a,b are close to 128.
        """
        detections = []
        timestamp = time.time()

        h, w = frame_bgr.shape[:2]
        total_pixels = h * w

        # Convert to LAB
        frame_lab = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2LAB)

        # Extract a and b channels (both 0-255 in OpenCV, centered at 128)
        a_channel = frame_lab[:, :, 1].astype(np.int32)
        b_channel = frame_lab[:, :, 2].astype(np.int32)

        # Calculate chroma (distance from neutral gray at 128,128)
        chroma = np.sqrt((a_channel - 128.0) ** 2 + (b_channel - 128.0) ** 2)

        # Create mask for pixels with sufficient chroma (filter out grays)
        chroma_mask = chroma >= config.lab_min_chroma

        # Quantize a and b values
        bits = config.color_quantization_bits
        scale = 2 ** (8 - bits)
        bins_per_channel = 2 ** bits

        # Quantize a and b
        a_quantized = (a_channel // scale).clip(0, bins_per_channel - 1)
        b_quantized = (b_channel // scale).clip(0, bins_per_channel - 1)

        # Create 2D histogram index (a + b * bins_per_channel)
        color_indices = a_quantized + b_quantized * bins_per_channel
        max_bins = bins_per_channel ** 2

        # Build histogram only from chromatic pixels
        valid_indices = color_indices[chroma_mask]
        if len(valid_indices) == 0:
            return detections

        histogram = np.bincount(valid_indices.ravel(), minlength=max_bins)

        # Find rare color bins
        nonzero_counts = histogram[histogram > 0]
        if len(nonzero_counts) == 0:
            return detections

        valid_pixel_count = len(valid_indices)
        percentile_threshold = np.percentile(nonzero_counts, config.color_rarity_percentile)
        absolute_max = valid_pixel_count * 0.05
        threshold = min(percentile_threshold, absolute_max)

        # Create mask of rare bins
        rare_bins = (histogram > 0) & (histogram < threshold)

        # Create binary mask: pixel is rare if it has sufficient chroma AND rare a,b
        rare_ab_mask = rare_bins[color_indices]
        rare_mask = (rare_ab_mask & chroma_mask).astype(np.uint8) * 255

        # Morphology to clean up noise
        morph_kernel = self._get_morph_kernel(config.morphology_kernel_size)
        rare_mask = cv2.morphologyEx(rare_mask, cv2.MORPH_OPEN, morph_kernel)
        rare_mask = cv2.morphologyEx(rare_mask, cv2.MORPH_CLOSE, morph_kernel)

        # Extract blobs using configured method
        if config.contour_method == ContourMethod.CONNECTED_COMPONENTS:
            detections = self._extract_blobs_connected_components(
                rare_mask, config, timestamp, frame_bgr,
                color_indices, histogram, valid_pixel_count, max_detections,
                color_space='lab'
            )
        else:
            detections = self._extract_blobs_find_contours(
                rare_mask, config, timestamp, frame_bgr,
                color_indices, histogram, valid_pixel_count, max_detections,
                color_space='lab'
            )

        return detections

    def _extract_blobs_find_contours(self, binary_mask: np.ndarray, config: ColorAnomalyAndMotionDetectionConfig,
                                      timestamp: float, frame_bgr: np.ndarray,
                                      color_indices: np.ndarray, histogram: np.ndarray,
                                      total_pixels: int, max_detections: int = 0,
                                      color_space: str = 'bgr') -> List[Detection]:
        """
        Extract blobs using cv2.findContours.

        Shared implementation for all color spaces.
        """
        detections = []
        h, w = binary_mask.shape[:2]

        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Process ALL contours (no early stopping - we sort by rarity first)
        for contour in contours:
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

            # Get dominant color from detected pixels
            region = frame_bgr[y:y + h_box, x:x + w_box]
            if region.size > 0:
                contour_mask = np.zeros((h_box, w_box), dtype=np.uint8)
                shifted_contour = contour - np.array([x, y])
                cv2.drawContours(contour_mask, [shifted_contour], -1, 255, -1)
                mean_color = cv2.mean(region, mask=contour_mask)[:3]
                dominant_color = tuple(int(c) for c in mean_color)
            else:
                dominant_color = (0, 0, 0)

            # Confidence based on rarity
            if 0 <= cy < h and 0 <= cx < w:
                bin_idx = color_indices[cy, cx]
                bin_count = histogram[bin_idx] if bin_idx < len(histogram) else 0
                rarity = 1.0 - (bin_count / total_pixels) if total_pixels > 0 else 0.5
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
                    'color_space': color_space,
                    'dominant_color': dominant_color,
                    'bin_count': int(bin_count),
                    'rarity': float(rarity)
                }
            )
            detections.append(detection)

        # Sort by rarity (lowest bin_count = rarest) and apply max_detections limit
        if len(detections) > 0:
            detections.sort(key=lambda d: d.metadata.get('bin_count', float('inf')))
            if max_detections > 0 and len(detections) > max_detections:
                detections = detections[:max_detections]

        return detections
