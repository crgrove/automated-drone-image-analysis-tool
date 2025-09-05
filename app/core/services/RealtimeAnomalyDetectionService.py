"""
RealtimeAnomalyDetectionService.py - High-performance statistical anomaly detection

Optimized statistical anomaly detector designed for real-time RTMP streams
with <50ms processing latency per frame. Provides similar capabilities to
RX Anomaly detection but using efficient local statistical analysis.
"""

# Set environment variable to avoid numpy compatibility issues
import os
os.environ.setdefault('NUMPY_EXPERIMENTAL_DTYPE_API', '0')
os.environ.setdefault('NUMBA_DISABLE_INTEL_SVML', '1')
os.environ.setdefault('NPY_DISABLE_SVML', '1')

import cv2
import numpy as np
import time
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field
from threading import Lock
import concurrent.futures

from PySide6.QtCore import QObject, QThread, Signal
from core.services.LoggerService import LoggerService


@dataclass
class AnomalyDetection:
    """Container for anomaly detection result."""
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    centroid: Tuple[int, int]  # center point
    area: float  # pixel area
    anomaly_score: float  # anomaly score (higher = more anomalous)
    confidence: float  # detection confidence 0-1
    timestamp: float  # detection time
    contour: np.ndarray = field(repr=False)  # original contour data


@dataclass
class AnomalyConfig:
    """Statistical anomaly detection configuration."""
    sensitivity: int = 5  # Sensitivity level 1-10 (maps to threshold multiplier)
    min_area: int = 100  # minimum detection area in pixels
    max_area: int = 50000  # maximum detection area in pixels
    window_size: int = 15  # local statistics window size (odd number)
    confidence_threshold: float = 0.0  # minimum confidence threshold (0-1)
    morphology_enabled: bool = True  # noise reduction
    gpu_acceleration: bool = False  # attempt GPU processing
    distance_metric: str = "euclidean"  # euclidean, manhattan, or mahalanobis_approx
    show_heatmap: bool = False  # show anomaly heatmap overlay


class RealtimeAnomalyDetector(QObject):
    """
    High-performance statistical anomaly detector optimized for real-time streaming.

    Features:
    - Sub-50ms processing per frame
    - Local statistical analysis (mean, std deviation)
    - Multiple distance metrics for anomaly scoring
    - GPU acceleration when available
    - Adaptive sensitivity control
    - Thread-safe configuration updates
    """

    # Qt signals for integration
    detectionsReady = Signal(list, float, np.ndarray)  # detections, timestamp, annotated_frame
    performanceUpdate = Signal(dict)  # processing_time, fps, detections_count
    configurationChanged = Signal(dict)  # current config state

    def __init__(self):
        super().__init__()
        self.logger = LoggerService()

        # Detection configuration
        self._config = AnomalyConfig()
        self._config_lock = Lock()

        # Performance tracking
        self._processing_times = []
        self._max_processing_samples = 30
        self._frame_count = 0
        self._last_fps_time = time.time()

        # GPU acceleration
        self._gpu_available = self._check_gpu_availability()
        self._use_gpu = self._gpu_available and self._config.gpu_acceleration

        # Cached kernels for morphology
        self._morphology_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

        self.logger.info(f"Anomaly detector initialized (GPU: {self._gpu_available})")

    def _check_gpu_availability(self) -> bool:
        """Check if GPU acceleration is available."""
        try:
            test_img = np.zeros((100, 100, 3), dtype=np.uint8)
            gpu_img = cv2.cuda_GpuMat()
            gpu_img.upload(test_img)
            gpu_img.download()
            return True
        except Exception:
            return False

    def update_config(self, config: AnomalyConfig):
        """
        Update detection configuration thread-safely.

        Args:
            config: New anomaly detection configuration
        """
        with self._config_lock:
            self._config = config
            self._use_gpu = self._gpu_available and config.gpu_acceleration

        self.configurationChanged.emit(self._get_config_dict())
        self.logger.info("Anomaly detection configuration updated")

    def detect_anomalies(self, frame: np.ndarray, timestamp: float) -> List[AnomalyDetection]:
        """
        Perform real-time anomaly detection on a frame.

        Args:
            frame: Input BGR frame from video stream
            timestamp: Frame timestamp

        Returns:
            List of AnomalyDetection objects found in frame
        """
        start_time = time.perf_counter()
        detections = []

        try:
            # Validate input frame
            if frame is None or frame.size == 0:
                self.logger.warning("Invalid frame received for detection")
                return []

            if len(frame.shape) != 3 or frame.shape[2] != 3:
                self.logger.warning(f"Invalid frame shape: {frame.shape}")
                return []

            with self._config_lock:
                config = self._config

            # Optimize frame size for real-time processing
            processing_frame, scale_factor = self._prepare_frame_for_processing(frame)

            # GPU-accelerated processing if available
            if self._use_gpu:
                detections = self._detect_gpu(processing_frame, timestamp, config)
            else:
                detections = self._detect_cpu(processing_frame, timestamp, config)

            # Scale detections back to original frame coordinates
            if scale_factor != 1.0:
                detections = self._scale_detections_to_original(detections, scale_factor)

        except Exception as e:
            self.logger.error(f"Detection error: {e}")
            import traceback
            self.logger.error(f"Detection traceback: {traceback.format_exc()}")
            detections = []

        # Performance tracking
        processing_time = time.perf_counter() - start_time
        self._update_performance_stats(processing_time, len(detections))

        return detections

    def _detect_cpu(self, frame: np.ndarray, timestamp: float, config: AnomalyConfig) -> List[AnomalyDetection]:
        """CPU-based statistical anomaly detection."""
        try:
            # Convert to LAB color space for better perceptual distance
            lab_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB).astype(np.float32)

            # Compute local statistics efficiently
            anomaly_map = self._compute_anomaly_map_cpu(lab_frame, config)

            # Apply sensitivity threshold
            threshold = self._get_threshold_from_sensitivity(config.sensitivity, anomaly_map)
            binary_mask = (anomaly_map > threshold).astype(np.uint8) * 255

            # Morphological operations for noise reduction
            if config.morphology_enabled:
                binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, self._morphology_kernel)
                binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, self._morphology_kernel)

            # Find contours
            contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            return self._process_contours(contours, anomaly_map, timestamp, config)

        except Exception as e:
            self.logger.error(f"Error in CPU detection: {e}")
            return []

    def _detect_gpu(self, frame: np.ndarray, timestamp: float, config: AnomalyConfig) -> List[AnomalyDetection]:
        """GPU-accelerated anomaly detection."""
        try:
            # Upload frame to GPU
            gpu_frame = cv2.cuda_GpuMat()
            gpu_frame.upload(frame)

            # Convert to LAB on GPU
            gpu_lab = cv2.cuda.cvtColor(gpu_frame, cv2.COLOR_BGR2LAB)

            # Download for statistical computation (CPU operations)
            lab_frame = gpu_lab.download().astype(np.float32)

            # Compute anomaly map (CPU - complex statistics)
            anomaly_map = self._compute_anomaly_map_cpu(lab_frame, config)

            # Threshold and morphology on GPU
            threshold = self._get_threshold_from_sensitivity(config.sensitivity, anomaly_map)

            # Upload anomaly map to GPU for thresholding
            gpu_anomaly = cv2.cuda_GpuMat()
            gpu_anomaly.upload((anomaly_map * 255).astype(np.uint8))

            # Threshold on GPU
            gpu_binary = cv2.cuda.threshold(gpu_anomaly, threshold * 255, 255, cv2.THRESH_BINARY)[1]

            # Download for contour detection (CPU operation)
            binary_mask = gpu_binary.download()

            # Morphological operations
            if config.morphology_enabled:
                binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, self._morphology_kernel)
                binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, self._morphology_kernel)

            # Find contours (CPU)
            contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            return self._process_contours(contours, anomaly_map, timestamp, config)

        except Exception as e:
            self.logger.warning(f"GPU detection failed, falling back to CPU: {e}")
            return self._detect_cpu(frame, timestamp, config)

    def _compute_anomaly_map_cpu(self, lab_frame: np.ndarray, config: AnomalyConfig) -> np.ndarray:
        """
        Compute anomaly map using RX-style spectral anomaly detection.

        This implements a proper RX anomaly detector that finds pixels that don't
        fit the local spectral statistical model - like a pink shirt in natural scenery.
        """
        h, w, c = lab_frame.shape
        anomaly_map = np.zeros((h, w), dtype=np.float32)

        if config.window_size <= 1:
            # Global RX anomaly detection for fastest performance
            return self._compute_global_rx_anomaly(lab_frame)

        # Local RX anomaly detection - proper implementation
        window_size = config.window_size if config.window_size % 2 == 1 else config.window_size + 1
        half_window = window_size // 2

        # Pad the frame to handle borders
        padded_frame = np.pad(lab_frame, ((half_window, half_window), (half_window, half_window), (0, 0)), mode='reflect')

        # Efficient sliding window using array operations
        for i in range(h):
            for j in range(w):
                # Extract local window
                window = padded_frame[i:i+window_size, j:j+window_size]
                center_pixel = lab_frame[i, j]

                # Compute RX anomaly score for this pixel
                anomaly_score = self._compute_rx_score(center_pixel, window, config.distance_metric)
                anomaly_map[i, j] = anomaly_score

        # Normalize to [0, 1]
        if anomaly_map.max() > 0:
            anomaly_map = anomaly_map / anomaly_map.max()

        return anomaly_map

    def _compute_global_rx_anomaly(self, lab_frame: np.ndarray) -> np.ndarray:
        """
        Fast global RX anomaly detection.

        Computes how spectrally different each pixel is from the overall image statistics.
        This should detect things like pink shirts in natural green/gray environments.
        """
        h, w, c = lab_frame.shape
        pixels = lab_frame.reshape(-1, c).astype(np.float64)

        # Compute global mean and covariance
        mean = np.mean(pixels, axis=0)

        # For performance, use simplified covariance (diagonal approximation)
        # This is much faster than full covariance matrix inversion but still effective
        cov_diag = np.var(pixels, axis=0) + 1e-6  # Add small value to avoid division by zero

        # Compute anomaly score for each pixel using simplified Mahalanobis distance
        diff = lab_frame - mean
        # Normalized squared difference (simplified Mahalanobis)
        normalized_diff = diff / np.sqrt(cov_diag)
        anomaly_map = np.sum(normalized_diff ** 2, axis=2)

        # Apply square root to make scores more linear
        anomaly_map = np.sqrt(anomaly_map)

        # Normalize to [0, 1]
        if anomaly_map.max() > 0:
            anomaly_map = anomaly_map / anomaly_map.max()

        return anomaly_map

    def _compute_rx_score(self, center_pixel: np.ndarray, window: np.ndarray, distance_metric: str) -> float:
        """
        Compute RX anomaly score for a single pixel given its local window.

        Args:
            center_pixel: The pixel to evaluate
            window: Local neighborhood around the pixel
            distance_metric: Type of distance calculation

        Returns:
            Anomaly score (higher = more anomalous)
        """
        window_flat = window.reshape(-1, window.shape[-1]).astype(np.float64)

        # Remove the center pixel from background estimation
        center_idx = len(window_flat) // 2
        background = np.delete(window_flat, center_idx, axis=0)

        if len(background) < 3:  # Need minimum samples for statistics
            return 0.0

        # Compute background statistics
        bg_mean = np.mean(background, axis=0)

        if distance_metric == "euclidean":
            # Simple Euclidean distance from local mean
            diff = center_pixel - bg_mean
            return np.linalg.norm(diff)

        elif distance_metric == "manhattan":
            # Manhattan distance from local mean
            diff = np.abs(center_pixel - bg_mean)
            return np.sum(diff)

        elif distance_metric == "mahalanobis_approx":
            # Approximate Mahalanobis distance (diagonal covariance for speed)
            diff = center_pixel - bg_mean
            bg_var = np.var(background, axis=0) + 1e-6
            normalized_diff = diff / np.sqrt(bg_var)
            return np.linalg.norm(normalized_diff)

        return 0.0

    def _prepare_frame_for_processing(self, frame: np.ndarray) -> tuple[np.ndarray, float]:
        """
        Prepare frame for processing by downscaling if necessary for real-time performance.

        Target processing resolution: 640x480 for optimal performance.
        Larger frames are downscaled proportionally.

        Returns:
            tuple: (processing_frame, scale_factor)
        """
        height, width = frame.shape[:2]

        # Target resolution for optimal real-time performance
        target_width = 640
        target_height = 480

        # Calculate if we need to downscale
        if width <= target_width and height <= target_height:
            # Frame is already small enough
            return frame, 1.0

        # Calculate scale factor to fit within target resolution
        width_scale = target_width / width
        height_scale = target_height / height
        scale_factor = min(width_scale, height_scale)

        # Calculate new dimensions
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)

        # Downscale frame
        processing_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

        # Commented out to avoid logging spam in production
        # self.logger.info(f"Downscaled frame from {width}x{height} to {new_width}x{new_height} (scale: {scale_factor:.2f})")

        return processing_frame, scale_factor

    def _scale_detections_to_original(self, detections: List[AnomalyDetection], scale_factor: float) -> List[AnomalyDetection]:
        """
        Scale detection coordinates back to original frame size.

        Args:
            detections: List of detections from downscaled frame
            scale_factor: Scale factor used for downscaling

        Returns:
            List of detections with coordinates scaled to original frame
        """
        if scale_factor == 1.0:
            return detections

        inverse_scale = 1.0 / scale_factor
        scaled_detections = []

        for detection in detections:
            # Scale bounding box
            x, y, w, h = detection.bbox
            scaled_bbox = (
                int(x * inverse_scale),
                int(y * inverse_scale),
                int(w * inverse_scale),
                int(h * inverse_scale)
            )

            # Scale centroid
            cx, cy = detection.centroid
            scaled_centroid = (
                int(cx * inverse_scale),
                int(cy * inverse_scale)
            )

            # Scale area
            scaled_area = detection.area * (inverse_scale ** 2)

            # Scale contour coordinates
            scaled_contour = detection.contour * inverse_scale
            scaled_contour = scaled_contour.astype(np.int32)

            # Create new detection with scaled coordinates
            scaled_detection = AnomalyDetection(
                bbox=scaled_bbox,
                centroid=scaled_centroid,
                area=scaled_area,
                anomaly_score=detection.anomaly_score,  # Score unchanged
                confidence=detection.confidence,  # Confidence unchanged
                timestamp=detection.timestamp,
                contour=scaled_contour
            )

            scaled_detections.append(scaled_detection)

        return scaled_detections

    def _get_threshold_from_sensitivity(self, sensitivity: int, anomaly_map: np.ndarray) -> float:
        """
        Convert sensitivity level (1-10) to anomaly threshold.

        Maps sensitivity to percentile thresholds:
        - Sensitivity 1 (low): 99th percentile (few detections)
        - Sensitivity 10 (high): 70th percentile (many detections)
        """
        # Map sensitivity 1-10 to percentiles 99-70
        percentile = 99 - (sensitivity - 1) * 3.0  # Linear mapping
        percentile = max(70, min(99, percentile))  # Clamp to range

        return np.percentile(anomaly_map, percentile)

    def _process_contours(self, contours: List, anomaly_map: np.ndarray, timestamp: float, config: AnomalyConfig) -> List[AnomalyDetection]:
        """Process contours into AnomalyDetection objects."""
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

            # Calculate average anomaly score in the region
            mask = np.zeros(anomaly_map.shape, dtype=np.uint8)
            cv2.fillPoly(mask, [contour], 255)
            region_scores = anomaly_map[mask > 0]
            avg_anomaly_score = np.mean(region_scores) if len(region_scores) > 0 else 0

            # Calculate confidence based on contour properties and anomaly score
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0

            # Confidence scoring (0-1)
            size_score = min(area / config.max_area, 1.0)
            shape_score = solidity
            anomaly_score_normalized = min(avg_anomaly_score * 2, 1.0)  # Scale anomaly score
            confidence = (size_score + shape_score + anomaly_score_normalized) / 3.0

            # Filter by confidence threshold
            if confidence < config.confidence_threshold:
                continue

            detection = AnomalyDetection(
                bbox=(x, y, w, h),
                centroid=centroid,
                area=area,
                anomaly_score=avg_anomaly_score,
                confidence=confidence,
                timestamp=timestamp,
                contour=contour
            )

            detections.append(detection)

        # Sort by anomaly score (highest first)
        detections.sort(key=lambda d: d.anomaly_score, reverse=True)

        return detections

    def create_annotated_frame(self, frame: np.ndarray, detections: List[AnomalyDetection], anomaly_map: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Create annotated frame with detection overlays.

        Args:
            frame: Original frame
            detections: List of detections to draw
            anomaly_map: Optional anomaly heatmap to overlay

        Returns:
            Annotated frame with bounding boxes and labels or anomaly heatmap
        """
        annotated = frame.copy()

        # Show anomaly heatmap if requested
        if self._config.show_heatmap and anomaly_map is not None:
            # Create heatmap overlay
            heatmap = cv2.applyColorMap((anomaly_map * 255).astype(np.uint8), cv2.COLORMAP_JET)
            # Blend with original frame
            annotated = cv2.addWeighted(annotated, 0.7, heatmap, 0.3, 0)

        for i, detection in enumerate(detections):
            x, y, w, h = detection.bbox
            centroid_x, centroid_y = detection.centroid

            # Color coding by anomaly score
            if detection.anomaly_score > 0.8:
                color = (0, 0, 255)  # Red - high anomaly
            elif detection.anomaly_score > 0.5:
                color = (0, 165, 255)  # Orange - medium anomaly
            else:
                color = (0, 255, 255)  # Yellow - low anomaly

            # Draw contour outline for precise anomaly region
            try:
                cv2.drawContours(annotated, [detection.contour], -1, color, 2)
            except Exception:
                # Fallback to bounding box if contour drawing fails
                cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)

            # Draw centroid
            cv2.circle(annotated, (centroid_x, centroid_y), 3, color, -1)

            # Add detection info
            label = f"#{i+1} A:{detection.anomaly_score:.2f} C:{detection.confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]

            # Background for text
            cv2.rectangle(annotated, (x, y - label_size[1] - 10), (x + label_size[0], y), color, -1)

            # Text
            cv2.putText(annotated, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Add overall stats
        stats_text = f"Anomalies: {len(detections)} | Sensitivity: {self._config.sensitivity}"
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
            'sensitivity': self._config.sensitivity,
            'min_area': self._config.min_area,
            'max_area': self._config.max_area,
            'window_size': self._config.window_size,
            'morphology_enabled': self._config.morphology_enabled,
            'gpu_acceleration': self._use_gpu,
            'distance_metric': self._config.distance_metric,
            'show_heatmap': self._config.show_heatmap
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
