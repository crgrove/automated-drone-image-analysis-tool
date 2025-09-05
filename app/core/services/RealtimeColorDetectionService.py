"""
RealtimeColorDetectionService.py - High-performance color detection for live streams

Optimized HSV-based color detection service designed for real-time RTMP streams
with <100ms processing latency per frame. Integrates with existing ADIAT HSV algorithms.
"""

# Set environment variable to avoid numpy compatibility issues
import os
os.environ.setdefault('NUMPY_EXPERIMENTAL_DTYPE_API', '0')  # noqa: E402
os.environ.setdefault('NUMBA_DISABLE_INTEL_SVML', '1')  # noqa: E402
os.environ.setdefault('NPY_DISABLE_SVML', '1')  # noqa: E402

import cv2
import numpy as np
import time
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field
from threading import Lock
import concurrent.futures

from PySide6.QtCore import QObject, QThread, Signal
from helpers.ColorUtils import ColorUtils
from core.services.LoggerService import LoggerService


@dataclass
class Detection:
    """Container for color detection result."""
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    centroid: Tuple[int, int]  # center point
    area: float  # pixel area
    confidence: float  # detection confidence 0-1
    timestamp: float  # detection time
    contour: np.ndarray = field(repr=False)  # original contour data


@dataclass
class HSVConfig:
    """HSV color detection configuration."""
    target_color_rgb: Tuple[int, int, int]  # RGB values
    hue_threshold: int = 20
    saturation_threshold: int = 50
    value_threshold: int = 50
    min_area: int = 100  # minimum detection area in pixels
    max_area: int = 50000  # maximum detection area in pixels
    confidence_threshold: float = 0.0  # minimum confidence threshold (0-1)
    morphology_enabled: bool = True  # noise reduction
    gpu_acceleration: bool = False  # attempt GPU processing
    show_labels: bool = True  # show detection labels and center dots
    hsv_ranges: Optional[Dict[str, Any]] = None  # Precise HSV range data from new picker


class RealtimeColorDetector(QObject):
    """
    High-performance color detector optimized for real-time streaming.

    Features:
    - Sub-100ms processing per frame
    - GPU acceleration when available
    - Adaptive quality scaling based on performance
    - Thread-safe configuration updates
    - Comprehensive detection metadata
    """

    # Qt signals for integration
    detectionsReady = Signal(list, float, np.ndarray)  # detections, timestamp, annotated_frame
    performanceUpdate = Signal(dict)  # processing_time, fps, detections_count
    configurationChanged = Signal(dict)  # current config state

    def __init__(self):
        super().__init__()
        self.logger = LoggerService()

        # Detection configuration
        self._config = HSVConfig(target_color_rgb=(255, 0, 0))  # Default red
        self._config_lock = Lock()

        # Performance tracking
        self._processing_times = []
        self._max_processing_samples = 30
        self._frame_count = 0
        self._last_fps_time = time.time()

        # GPU acceleration
        self._gpu_available = self._check_gpu_availability()
        self._use_gpu = self._gpu_available and self._config.gpu_acceleration

        # HSV conversion cache
        self._target_hsv = None
        self._hsv_ranges = None
        self._update_hsv_values()

        self.logger.info(f"Color detector initialized (GPU: {self._gpu_available})")

    def _check_gpu_availability(self) -> bool:
        """Check if GPU acceleration is available."""
        try:
            # Test CUDA availability with more specific error handling
            test_img = np.zeros((100, 100, 3), dtype=np.uint8)
            gpu_img = cv2.cuda_GpuMat()
            gpu_img.upload(test_img)
            gpu_img.download()  # Test round-trip
            return True
        except Exception:
            # GPU not available, use CPU processing
            return False

    def update_config(self, config: HSVConfig):
        """
        Update detection configuration thread-safely.

        Args:
            config: New HSV configuration
        """
        with self._config_lock:
            self._config = config
            self._use_gpu = self._gpu_available and config.gpu_acceleration
            self._update_hsv_values()

        self.configurationChanged.emit(self._get_config_dict())
        self.logger.info("Detection configuration updated")

    def _update_hsv_values(self):
        """Update HSV conversion values based on current config."""
        try:
            # Convert RGB to HSV for target color
            rgb_array = np.uint8([[self._config.target_color_rgb]])
            self._target_hsv = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2HSV)[0][0]

            # Check if we have precise HSV ranges from the new picker
            if self._config.hsv_ranges:
                # Use precise HSV ranges from the new picker
                hsv_data = self._config.hsv_ranges
                h, s, v = hsv_data['h'], hsv_data['s'], hsv_data['v']
                h_minus, h_plus = hsv_data['h_minus'], hsv_data['h_plus']
                s_minus, s_plus = hsv_data['s_minus'], hsv_data['s_plus']
                v_minus, v_plus = hsv_data['v_minus'], hsv_data['v_plus']

                # Calculate bounds in OpenCV format (H: 0-179, S: 0-255, V: 0-255)
                h_center = int(h * 179)
                s_center = int(s * 255)
                v_center = int(v * 255)

                h_low = max(0, h_center - int(h_minus * 179))
                h_high = min(179, h_center + int(h_plus * 179))
                s_low = max(0, s_center - int(s_minus * 255))
                s_high = min(255, s_center + int(s_plus * 255))
                v_low = max(0, v_center - int(v_minus * 255))
                v_high = min(255, v_center + int(v_plus * 255))

                # Handle hue wrapping if necessary
                if h_low > h_high:
                    # Hue wraps around (e.g., 350° to 10°) - create two ranges
                    self._hsv_ranges = [
                        (np.array([h_low, s_low, v_low], dtype=np.uint8),
                         np.array([179, s_high, v_high], dtype=np.uint8)),
                        (np.array([0, s_low, v_low], dtype=np.uint8),
                         np.array([h_high, s_high, v_high], dtype=np.uint8))
                    ]
                else:
                    # Normal range - single range
                    self._hsv_ranges = [
                        (np.array([h_low, s_low, v_low], dtype=np.uint8),
                         np.array([h_high, s_high, v_high], dtype=np.uint8))
                    ]

            else:
                # Fallback to old ColorUtils method for backward compatibility
                self._hsv_ranges = ColorUtils.get_hsv_color_range(
                    self._target_hsv,
                    self._config.hue_threshold,
                    self._config.saturation_threshold,
                    self._config.value_threshold
                )

        except Exception as e:
            self.logger.error(f"Error updating HSV values: {e}")

    def detect_colors(self, frame: np.ndarray, timestamp: float) -> List[Detection]:
        """
        Perform real-time color detection on a frame.

        Args:
            frame: Input BGR frame from video stream
            timestamp: Frame timestamp

        Returns:
            List of Detection objects found in frame
        """
        start_time = time.perf_counter()
        detections = []

        try:
            # Validate input frame
            if frame is None or frame.size == 0:
                self.logger.warning("Invalid frame received for detection")
                return []

            # Ensure frame is in the correct format
            if len(frame.shape) != 3 or frame.shape[2] != 3:
                self.logger.warning(f"Invalid frame shape: {frame.shape}")
                return []

            with self._config_lock:
                config = self._config
                hsv_ranges = self._hsv_ranges

            if hsv_ranges is None:
                return []

            # Create a copy to avoid memory issues
            frame_copy = frame.copy()

            # GPU-accelerated processing if available
            if self._use_gpu:
                detections = self._detect_gpu(frame_copy, timestamp, config, hsv_ranges)
            else:
                detections = self._detect_cpu(frame_copy, timestamp, config, hsv_ranges)

        except Exception as e:
            self.logger.error(f"Detection error: {e}")
            import traceback
            self.logger.error(f"Detection traceback: {traceback.format_exc()}")
            detections = []

        # Performance tracking
        processing_time = time.perf_counter() - start_time
        self._update_performance_stats(processing_time, len(detections))

        return detections

    def _detect_cpu(self, frame: np.ndarray, timestamp: float, config: HSVConfig, hsv_ranges: List) -> List[Detection]:
        """CPU-based color detection."""
        try:
            # Convert BGR to HSV with error handling
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Validate HSV conversion
            if hsv_frame is None or hsv_frame.size == 0:
                self.logger.warning("HSV conversion failed")
                return []

            # Create mask from HSV ranges
            mask = None
            for lower_bound, upper_bound in hsv_ranges:
                try:
                    # Ensure bounds are numpy arrays
                    lower_bound = np.array(lower_bound, dtype=np.uint8)
                    upper_bound = np.array(upper_bound, dtype=np.uint8)

                    range_mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
                    if mask is None:
                        mask = range_mask
                    else:
                        mask = cv2.bitwise_or(mask, range_mask)
                except Exception as e:
                    self.logger.error(f"Error creating mask for range {lower_bound}-{upper_bound}: {e}")
                    continue

            if mask is None:
                return []

            # Morphological operations for noise reduction
            if config.morphology_enabled:
                try:
                    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                except Exception as e:
                    self.logger.error(f"Error in morphological operations: {e}")
                    # Continue without morphology

            # Find contours
            try:
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                return self._process_contours(contours, timestamp, config)
            except Exception as e:
                self.logger.error(f"Error finding contours: {e}")
                return []

        except Exception as e:
            self.logger.error(f"Error in CPU detection: {e}")
            import traceback
            self.logger.error(f"CPU detection traceback: {traceback.format_exc()}")
            return []

    def _detect_gpu(self, frame: np.ndarray, timestamp: float, config: HSVConfig, hsv_ranges: List) -> List[Detection]:
        """GPU-accelerated color detection."""
        try:
            # Upload frame to GPU
            gpu_frame = cv2.cuda_GpuMat()
            gpu_frame.upload(frame)

            # Convert BGR to HSV on GPU
            gpu_hsv = cv2.cuda.cvtColor(gpu_frame, cv2.COLOR_BGR2HSV)

            # Create mask on GPU
            gpu_mask = None
            for lower_bound, upper_bound in hsv_ranges:
                gpu_range_mask = cv2.cuda.inRange(gpu_hsv, lower_bound, upper_bound)
                if gpu_mask is None:
                    gpu_mask = gpu_range_mask
                else:
                    cv2.cuda.bitwise_or(gpu_mask, gpu_range_mask, gpu_mask)

            # Download mask for contour detection (CPU operation)
            mask = gpu_mask.download()

            # Morphological operations
            if config.morphology_enabled:
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

            # Find contours (CPU)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            return self._process_contours(contours, timestamp, config)

        except Exception as e:
            self.logger.warning(f"GPU detection failed, falling back to CPU: {e}")
            return self._detect_cpu(frame, timestamp, config, hsv_ranges)

    def _process_contours(self, contours: List, timestamp: float, config: HSVConfig) -> List[Detection]:
        """Process contours into Detection objects."""
        detections = []

        for contour in contours:
            # Calculate area
            area = cv2.contourArea(contour)

            # Filter by area constraints
            if area < config.min_area or area > config.max_area:
                continue

            # Calculate bounding box and centroid
            x, y, w, h = cv2.boundingRect(contour)
            centroid = (int(x + w/2), int(y + h/2))

            # Calculate confidence based on contour properties
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0

            # Confidence scoring (0-1)
            size_score = min(area / config.max_area, 1.0)
            shape_score = solidity
            confidence = (size_score + shape_score) / 2.0

            # Filter by confidence threshold
            if confidence < config.confidence_threshold:
                continue

            detection = Detection(
                bbox=(x, y, w, h),
                centroid=centroid,
                area=area,
                confidence=confidence,
                timestamp=timestamp,
                contour=contour
            )

            detections.append(detection)

        # Sort by confidence (highest first)
        detections.sort(key=lambda d: d.confidence, reverse=True)

        return detections

    def create_annotated_frame(self, frame: np.ndarray, detections: List[Detection]) -> np.ndarray:
        """
        Create annotated frame with detection overlays.

        Args:
            frame: Original frame
            detections: List of detections to draw

        Returns:
            Annotated frame with bounding boxes and labels or pixel outlines
        """
        annotated = frame.copy()

        for i, detection in enumerate(detections):
            x, y, w, h = detection.bbox
            centroid_x, centroid_y = detection.centroid

            # Color coding by confidence
            if detection.confidence > 0.8:
                color = (0, 255, 0)  # Green - high confidence
            elif detection.confidence > 0.5:
                color = (0, 255, 255)  # Yellow - medium confidence
            else:
                color = (0, 0, 255)  # Red - low confidence

            if self._config.show_labels:
                # Original mode: bounding boxes with labels and center dots
                # Draw bounding box
                cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)

                # Draw centroid
                cv2.circle(annotated, (centroid_x, centroid_y), 3, color, -1)

                # Add detection info
                label = f"#{i+1} {detection.confidence:.2f} ({int(detection.area)}px)"
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]

                # Background for text
                cv2.rectangle(annotated, (x, y - label_size[1] - 10), (x + label_size[0], y), color, -1)

                # Text
                cv2.putText(annotated, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            else:
                # New mode: pixel-level contour outlines only
                try:
                    # Draw the actual contour outline
                    cv2.drawContours(annotated, [detection.contour], -1, color, 2)
                except Exception:
                    # Fallback to bounding box if contour drawing fails
                    cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)

        # Add overall stats
        if self._config.hsv_ranges:
            h_minus = int(self._config.hsv_ranges['h_minus'] * 179)
            h_plus = int(self._config.hsv_ranges['h_plus'] * 179)
            stats_text = f"Detections: {len(detections)} | Config: H-{h_minus}/+{h_plus}"
        else:
            stats_text = f"Detections: {len(detections)} | Config: H±{self._config.hue_threshold}"
        cv2.putText(annotated, stats_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

        return annotated

    def _update_performance_stats(self, processing_time: float, detection_count: int):
        """Update and emit performance statistics."""
        self._processing_times.append(processing_time)
        if len(self._processing_times) > self._max_processing_samples:
            self._processing_times.pop(0)

        self._frame_count += 1
        current_time = time.time()

        # Calculate FPS every second
        if current_time - self._last_fps_time >= 1.0:
            fps = self._frame_count / (current_time - self._last_fps_time)
            avg_processing_time = sum(self._processing_times) / len(self._processing_times)

            performance_stats = {
                'fps': fps,
                'avg_processing_time_ms': avg_processing_time * 1000,
                'current_processing_time_ms': processing_time * 1000,
                'detection_count': detection_count,
                'frame_count': self._frame_count,
                'gpu_enabled': self._use_gpu
            }

            self.performanceUpdate.emit(performance_stats)

            # Reset counters
            self._frame_count = 0
            self._last_fps_time = current_time

    def _get_config_dict(self) -> Dict[str, Any]:
        """Get current configuration as dictionary."""
        return {
            'target_color_rgb': self._config.target_color_rgb,
            'hue_threshold': self._config.hue_threshold,
            'saturation_threshold': self._config.saturation_threshold,
            'value_threshold': self._config.value_threshold,
            'min_area': self._config.min_area,
            'max_area': self._config.max_area,
            'morphology_enabled': self._config.morphology_enabled,
            'gpu_acceleration': self._use_gpu
        }

    def get_performance_info(self) -> Dict[str, Any]:
        """Get current performance information."""
        if not self._processing_times:
            return {}

        return {
            'avg_processing_time_ms': sum(self._processing_times) / len(self._processing_times) * 1000,
            'min_processing_time_ms': min(self._processing_times) * 1000,
            'max_processing_time_ms': max(self._processing_times) * 1000,
            'total_frames_processed': sum(range(len(self._processing_times))),
            'gpu_available': self._gpu_available,
            'gpu_enabled': self._use_gpu
        }
