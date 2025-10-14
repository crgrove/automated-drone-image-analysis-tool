"""
RealtimeIntegratedDetectionService.py - Integrated real-time anomaly detection

Combines motion, color quantization, and RX anomaly detection with progressive
optimizations for 720p-1080p real-time performance (30+ FPS target).

Implements the development roadmap:
Step 0: Groundwork & Tooling ✓
Step 1: Clean 720p Baseline ✓
Step 2: Threaded Capture ✓
Step 3: Fast Motion Mask ✓
Step 4: Color Anomaly v1 - Quantization ✓
Step 5: Mask Fusion & Temporal Smoothing ✓
Step 6: ROI-First Pipeline (pending)
Step 7: Optimize for 1080p (pending)
Step 8: Optional GPU Acceleration (pending)
Step 9: End-to-End Optimization (pending)
"""

# Set environment variables before imports
import os
os.environ.setdefault('NUMPY_EXPERIMENTAL_DTYPE_API', '0')
os.environ.setdefault('NUMBA_DISABLE_INTEL_SVML', '1')
os.environ.setdefault('NPY_DISABLE_SVML', '1')

import cv2
import numpy as np
import time
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field
from collections import deque
from threading import Lock, Thread
from enum import Enum

from PySide6.QtCore import QObject, Signal
from core.services.LoggerService import LoggerService


# ============================================================================
# STEP 0: GROUNDWORK & TOOLING
# ============================================================================

@dataclass
class StageTimings:
    """Per-stage timing measurements for performance analysis."""
    capture_ms: float = 0.0
    preprocessing_ms: float = 0.0
    motion_detection_ms: float = 0.0  # Step 3: Motion detection time
    color_detection_ms: float = 0.0   # Step 4: Color detection time
    detection_ms: float = 0.0          # Total detection time (motion + color)
    fusion_ms: float = 0.0
    render_ms: float = 0.0
    total_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for logging."""
        return {
            'capture_ms': self.capture_ms,
            'preprocessing_ms': self.preprocessing_ms,
            'motion_detection_ms': self.motion_detection_ms,
            'color_detection_ms': self.color_detection_ms,
            'detection_ms': self.detection_ms,
            'fusion_ms': self.fusion_ms,
            'render_ms': self.render_ms,
            'total_ms': self.total_ms
        }


@dataclass
class PerformanceMetrics:
    """Comprehensive performance tracking."""
    fps: float = 0.0
    frame_count: int = 0
    dropped_frames: int = 0
    detection_count: int = 0
    average_timings: Optional[StageTimings] = None
    recent_timings: List[StageTimings] = field(default_factory=list)
    max_recent_samples: int = 30

    def update(self, timings: StageTimings, detection_count: int):
        """Update metrics with new timing data."""
        self.frame_count += 1
        self.detection_count = detection_count
        self.recent_timings.append(timings)

        # Keep only recent samples
        if len(self.recent_timings) > self.max_recent_samples:
            self.recent_timings.pop(0)

        # Calculate averages
        if self.recent_timings:
            avg = StageTimings()
            avg.capture_ms = np.mean([t.capture_ms for t in self.recent_timings])
            avg.preprocessing_ms = np.mean([t.preprocessing_ms for t in self.recent_timings])
            avg.motion_detection_ms = np.mean([t.motion_detection_ms for t in self.recent_timings])
            avg.color_detection_ms = np.mean([t.color_detection_ms for t in self.recent_timings])
            avg.detection_ms = np.mean([t.detection_ms for t in self.recent_timings])
            avg.fusion_ms = np.mean([t.fusion_ms for t in self.recent_timings])
            avg.render_ms = np.mean([t.render_ms for t in self.recent_timings])
            avg.total_ms = np.mean([t.total_ms for t in self.recent_timings])
            self.average_timings = avg

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for display/logging."""
        result = {
            'fps': self.fps,
            'frame_count': self.frame_count,
            'dropped_frames': self.dropped_frames,
            'detection_count': self.detection_count
        }
        if self.average_timings:
            result['average_timings'] = self.average_timings.to_dict()
        return result


class FrameQueue:
    """Single-slot frame queue that drops old frames for low latency.

    When a new frame arrives and the queue is full, the old frame is dropped
    to ensure we always process the most recent frame.
    """

    def __init__(self):
        self.frame: Optional[np.ndarray] = None
        self.timestamp: float = 0.0
        self.lock = Lock()
        self.dropped_count: int = 0

    def put(self, frame: np.ndarray, timestamp: float) -> bool:
        """
        Add frame to queue, dropping old frame if present.

        Returns:
            True if a frame was dropped, False otherwise
        """
        dropped = False
        with self.lock:
            if self.frame is not None:
                # Drop old frame
                dropped = True
                self.dropped_count += 1
            self.frame = frame.copy()
            self.timestamp = timestamp
        return dropped

    def get(self) -> Tuple[Optional[np.ndarray], float]:
        """
        Get and remove frame from queue.

        Returns:
            Tuple of (frame, timestamp) or (None, 0.0) if empty
        """
        with self.lock:
            frame = self.frame
            timestamp = self.timestamp
            self.frame = None
            self.timestamp = 0.0
        return frame, timestamp

    def is_empty(self) -> bool:
        """Check if queue is empty."""
        with self.lock:
            return self.frame is None

    def get_dropped_count(self) -> int:
        """Get number of dropped frames."""
        with self.lock:
            return self.dropped_count

    def reset_dropped_count(self) -> int:
        """Reset and return dropped frame count."""
        with self.lock:
            count = self.dropped_count
            self.dropped_count = 0
            return count


# ============================================================================
# STEP 2: THREADED CAPTURE
# ============================================================================

class ThreadedCaptureWorker:
    """
    Step 2: Background thread that continuously captures frames.

    Runs in a separate thread to avoid blocking the processing pipeline.
    Always captures the latest frame, dropping old ones in the queue.

    Expected improvement: 30-200% FPS increase, lower jitter.
    """

    def __init__(self, video_source, frame_queue: FrameQueue, logger, target_fps: Optional[float] = None):
        """
        Initialize threaded capture worker.

        Args:
            video_source: Video source object with read() method
            frame_queue: FrameQueue to put captured frames into
            logger: Logger instance
            target_fps: Optional target FPS for rate limiting (e.g., for video files)
        """
        self.video_source = video_source
        self.frame_queue = frame_queue
        self.logger = logger
        self.target_fps = target_fps
        self.frame_delay = (1.0 / target_fps) if target_fps and target_fps > 0 else 0.0

        self._running = False
        self._thread: Optional[Thread] = None
        self._lock = Lock()
        self._frames_captured = 0
        self._capture_errors = 0

    def start(self):
        """Start the capture thread."""
        with self._lock:
            if self._running:
                self.logger.warning("Threaded capture already running")
                return

            self._running = True
            self._thread = Thread(target=self._capture_loop, daemon=True, name="CaptureThread")
            self._thread.start()
            self.logger.info("Threaded capture started")

    def stop(self):
        """Stop the capture thread."""
        with self._lock:
            if not self._running:
                return

            self._running = False

        # Wait for thread to finish
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
            self.logger.info(f"Threaded capture stopped (captured {self._frames_captured} frames, {self._capture_errors} errors)")

    def is_running(self) -> bool:
        """Check if capture thread is running."""
        with self._lock:
            return self._running

    def get_stats(self) -> Dict[str, int]:
        """Get capture statistics."""
        return {
            'frames_captured': self._frames_captured,
            'capture_errors': self._capture_errors
        }

    def _capture_loop(self):
        """Main capture loop that runs in background thread."""
        self.logger.info(f"Capture loop starting (FPS limit: {self.target_fps if self.target_fps else 'None'})...")

        last_capture_time = time.time()

        while True:
            # Check if we should stop
            with self._lock:
                if not self._running:
                    break

            try:
                # FPS limiting: wait if needed before next capture
                if self.frame_delay > 0:
                    current_time = time.time()
                    elapsed = current_time - last_capture_time

                    if elapsed < self.frame_delay:
                        sleep_time = self.frame_delay - elapsed
                        time.sleep(sleep_time)

                    last_capture_time = time.time()

                # Capture frame
                ret, frame = self.video_source.read()

                if not ret or frame is None:
                    self._capture_errors += 1
                    # Don't spam errors, just count them
                    if self._capture_errors <= 3:
                        self.logger.warning(f"Failed to capture frame (error #{self._capture_errors})")
                    # Small delay before retry
                    time.sleep(0.001)
                    continue

                # Put frame in queue (will drop old frame if present)
                timestamp = time.time()
                self.frame_queue.put(frame, timestamp)
                self._frames_captured += 1

                # For live sources (no FPS limit), capture as fast as possible
                # The single-slot queue handles backpressure automatically

            except Exception as e:
                self._capture_errors += 1
                self.logger.error(f"Capture loop error: {e}")
                time.sleep(0.01)  # Brief pause on exception

        self.logger.info("Capture loop exiting")


class TimingOverlayRenderer:
    """Renders FPS and timing information on frames."""

    @staticmethod
    def render(frame: np.ndarray, metrics: PerformanceMetrics,
               latest_timings: Optional[StageTimings] = None) -> np.ndarray:
        """
        Render performance overlay on frame.

        Args:
            frame: Input frame to annotate
            metrics: Current performance metrics
            latest_timings: Latest timing measurements (optional)

        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        h, w = frame.shape[:2]

        # Prepare text lines
        lines = []

        # FPS and frame info
        lines.append(f"FPS: {metrics.fps:.1f} | Frames: {metrics.frame_count}")

        if metrics.dropped_frames > 0:
            lines.append(f"Dropped: {metrics.dropped_frames} frames")

        # Latest timings (real-time)
        if latest_timings:
            lines.append(f"Latest: motion={latest_timings.motion_detection_ms:.1f}ms "
                        f"color={latest_timings.color_detection_ms:.1f}ms "
                        f"render={latest_timings.render_ms:.1f}ms")

        # Average timings
        if metrics.average_timings:
            avg = metrics.average_timings
            lines.append(f"Average: motion={avg.motion_detection_ms:.1f}ms "
                        f"color={avg.color_detection_ms:.1f}ms "
                        f"render={avg.render_ms:.1f}ms")
            lines.append(f"Total: {avg.total_ms:.1f}ms/frame "
                        f"(target: 33ms for 30fps)")

        # Detections
        lines.append(f"Detections: {metrics.detection_count}")

        # Render text with background
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        thickness = 1
        padding = 5
        line_height = 20

        # Calculate background size
        max_width = 0
        for line in lines:
            (text_width, text_height), _ = cv2.getTextSize(line, font, font_scale, thickness)
            max_width = max(max_width, text_width)

        bg_height = len(lines) * line_height + padding * 2
        bg_width = max_width + padding * 2

        # Draw semi-transparent background
        overlay = annotated.copy()
        cv2.rectangle(overlay, (5, 5), (5 + bg_width, 5 + bg_height),
                     (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, annotated, 0.4, 0, annotated)

        # Draw text
        y_offset = 5 + padding + 15
        for line in lines:
            cv2.putText(annotated, line, (10, y_offset), font, font_scale,
                       (0, 255, 0), thickness, cv2.LINE_AA)
            y_offset += line_height

        return annotated


# ============================================================================
# DETECTION SERVICE
# ============================================================================

@dataclass
class Detection:
    """Generic detection result."""
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    centroid: Tuple[int, int]
    area: float
    confidence: float
    detection_type: str  # 'motion', 'color', 'rx_anomaly', 'fused'
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    contour: Optional[np.ndarray] = None


class MotionAlgorithm(Enum):
    """Motion detection algorithms (Step 3)."""
    FRAME_DIFF = "frame_diff"      # Simple frame differencing (Step 1)
    MOG2 = "mog2"                  # Gaussian mixture model (Step 3 - best for static camera)
    KNN = "knn"                    # K-nearest neighbors (Step 3 - alternative)


class FusionMode(Enum):
    """Fusion modes for combining motion and color detections (Step 5)."""
    UNION = "union"                      # Detect if EITHER motion OR color (most detections)
    INTERSECTION = "intersection"        # Detect only if BOTH motion AND color agree (high confidence)
    COLOR_PRIORITY = "color_priority"    # Use color, add motion if color misses it
    MOTION_PRIORITY = "motion_priority"  # Use motion, add color if motion misses it


@dataclass
class IntegratedDetectionConfig:
    """Configuration for integrated detection."""
    # Processing resolution (Step 1: Locked to 720p)
    processing_width: int = 1280
    processing_height: int = 720

    # Detection toggles
    enable_motion: bool = True
    enable_color_quantization: bool = False  # Step 4
    enable_rx_anomaly: bool = False  # Later steps

    # Performance settings
    max_fps: Optional[int] = None  # Limit FPS if desired
    use_threaded_capture: bool = False  # Step 2

    # Step 3: Motion algorithm selection
    motion_algorithm: MotionAlgorithm = MotionAlgorithm.MOG2

    # Detection parameters (Step 1)
    min_detection_area: int = 100
    max_detection_area: int = 50000
    motion_threshold: int = 25  # Threshold for frame diff
    blur_kernel_size: int = 5  # Gaussian blur kernel (odd number)
    morphology_kernel_size: int = 3  # Morphology kernel (odd number)

    # Step 3: Persistence filter parameters
    persistence_frames: int = 3  # Total frames in window (M)
    persistence_threshold: int = 2  # Must appear in N frames

    # Step 3: Background subtraction parameters
    bg_history: int = 100  # Number of frames for background learning
    bg_var_threshold: float = 25.0  # Variance threshold for MOG2
    bg_detect_shadows: bool = False  # Shadow detection (slower if True)

    # Display options
    show_timing_overlay: bool = True
    show_detections: bool = True
    max_detections_to_render: int = 20  # Limit rendering for performance (0 = unlimited)

    # Rendering options (individual toggles for performance tuning)
    render_shape: int = 1  # 0=box, 1=circle, 2=dot, 3=off (default: circle for performance)
    render_text: bool = False  # Show labels (slow, default OFF)
    render_contours: bool = False  # Show contour outlines (slowest, default OFF)
    render_at_processing_res: bool = False  # Render at processing resolution (much faster for high-res)
    use_detection_color_for_rendering: bool = False  # Color shapes based on detected hue (100% sat, 100% val)

    # Step 3: Camera movement detection (pause detection during camera panning)
    pause_on_camera_movement: bool = True  # Automatically pause when camera moves
    camera_movement_threshold: float = 0.15  # If >15% of pixels change, assume camera movement (lower = more sensitive)

    # Step 4: Color quantization anomaly detection
    color_quantization_bits: int = 5  # Bits per channel (5 = 32^3 = 32,768 bins, faster than 6-bit)
    color_rarity_percentile: float = 20.0  # Mark colors below this percentile as rare
    color_min_detection_area: int = 50  # Minimum area for color anomalies
    use_tile_analysis: bool = False  # Analyze per-tile (4x4 grid) for local rarity

    # Hue expansion for color detections
    enable_hue_expansion: bool = True  # Expand detections to neighboring pixels with similar hue
    hue_expansion_range: int = 5  # +/- hue range in OpenCV units (0-179, so 5 = ~10 degrees)

    # Step 5: Mask fusion and temporal smoothing
    enable_fusion: bool = True  # Enable fusion (only applies when both motion and color enabled)
    fusion_mode: FusionMode = FusionMode.UNION  # How to combine motion + color detections
    enable_temporal_voting: bool = True  # Enable temporal majority voting to reduce flicker
    temporal_window_frames: int = 3  # Number of frames to track (M)
    temporal_threshold_frames: int = 2  # Must appear in N frames to be valid

    # Task A: False Positive Reduction
    # Aspect ratio filtering
    enable_aspect_ratio_filter: bool = True  # Filter detections by aspect ratio
    min_aspect_ratio: float = 0.2  # Minimum width/height ratio (exclude tall/thin objects)
    max_aspect_ratio: float = 5.0  # Maximum width/height ratio (exclude wide/flat objects)

    # Color exclusion (background learning)
    enable_color_exclusion: bool = False  # Enable color exclusion filtering
    excluded_hue_ranges: List[Tuple[float, float]] = field(default_factory=list)  # List of (hue_min, hue_max) ranges to exclude


class RealtimeIntegratedDetector(QObject):
    """
    Integrated real-time anomaly detector combining multiple algorithms.

    Progressive implementation following development roadmap:
    - Step 0: Timing, FPS overlay, frame queue ✓
    - Step 1: Clean 720p baseline with vectorized operations ✓
    - Step 3: Fast motion mask with background subtraction & persistence ✓
    - Step 2, 4-9: To be implemented progressively

    Current Performance Target:
    - 720p: ≥10-15 FPS stable
    - MOG2/KNN background subtraction for static camera detection
    - Persistence filter to reduce false positives
    - All operations vectorized (no Python loops)
    - Low buffer size for minimal latency

    Signals:
        frameProcessed: Emitted when frame is processed (annotated_frame, detections, metrics)
        performanceUpdate: Emitted with performance metrics
    """

    # Qt signals
    frameProcessed = Signal(np.ndarray, list, object)  # frame, detections, metrics
    performanceUpdate = Signal(dict)

    def __init__(self):
        super().__init__()
        self.logger = LoggerService()

        # Configuration
        self.config = IntegratedDetectionConfig()
        self.config_lock = Lock()

        # Step 0: Performance tracking
        self.metrics = PerformanceMetrics()
        self.frame_queue = FrameQueue()
        self.timing_renderer = TimingOverlayRenderer()

        # FPS calculation
        self._fps_counter = 0
        self._fps_start_time = time.time()
        self._last_fps_update = time.time()

        # Step 1: Detection state for 720p baseline
        self._prev_frame: Optional[np.ndarray] = None
        self._prev_gray: Optional[np.ndarray] = None

        # Step 1: Pre-compute morphology kernels for efficiency (no Python loops)
        self._morph_kernel_cache: Dict[int, np.ndarray] = {}

        # Step 3: Background subtractors
        self._bg_subtractor_mog2: Optional[cv2.BackgroundSubtractorMOG2] = None
        self._bg_subtractor_knn: Optional[cv2.BackgroundSubtractorKNN] = None
        self._init_background_subtractors()

        # Step 3: Persistence filter (temporal smoothing)
        self._detection_masks: deque = deque(maxlen=self.config.persistence_frames)

        # Step 5: Temporal voting (tracks detections across frames)
        self._temporal_detection_history: deque = deque(maxlen=self.config.temporal_window_frames)

        self.logger.info("Integrated detector initialized (Steps 0-1, 3-4 complete)")

    def update_config(self, config: IntegratedDetectionConfig):
        """Update detection configuration thread-safely."""
        with self.config_lock:
            old_persistence = self.config.persistence_frames
            old_temporal_window = self.config.temporal_window_frames
            self.config = config

            # Update persistence deque size if changed
            if old_persistence != config.persistence_frames:
                self._detection_masks = deque(
                    list(self._detection_masks),
                    maxlen=config.persistence_frames
                )

            # Update temporal voting deque size if changed
            if old_temporal_window != config.temporal_window_frames:
                self._temporal_detection_history = deque(
                    list(self._temporal_detection_history),
                    maxlen=config.temporal_window_frames
                )

            # Reinitialize background subtractors if parameters changed
            self._init_background_subtractors()

        self.logger.info("Configuration updated")

    def _init_background_subtractors(self):
        """Step 3: Initialize background subtraction algorithms.

        NOTE: This method should be called while holding config_lock!
        """
        config = self.config

        # MOG2 - Gaussian Mixture-based Background/Foreground Segmentation
        # Best for static cameras with changing lighting
        self._bg_subtractor_mog2 = cv2.createBackgroundSubtractorMOG2(
            history=config.bg_history,
            varThreshold=config.bg_var_threshold,
            detectShadows=config.bg_detect_shadows
        )

        # KNN - K-Nearest Neighbors Background Subtraction
        # Alternative, sometimes better for busy scenes
        self._bg_subtractor_knn = cv2.createBackgroundSubtractorKNN(
            history=config.bg_history,
            dist2Threshold=400.0,
            detectShadows=config.bg_detect_shadows
        )

        self.logger.info(f"Background subtractors initialized (history={config.bg_history})")

    def _get_morph_kernel(self, size: int) -> np.ndarray:
        """Get cached morphology kernel (vectorized, no loops)."""
        if size not in self._morph_kernel_cache:
            self._morph_kernel_cache[size] = cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE, (size, size)
            )
        return self._morph_kernel_cache[size]

    def _baseline_detect_720p(self, frame_gray: np.ndarray, config: IntegratedDetectionConfig, max_detections: int = 0) -> List[Detection]:
        """
        Step 1: Clean 720p baseline detector using vectorized operations only.

        Uses frame differencing with optimized numpy/OpenCV operations.
        NO Python loops - all operations are vectorized for performance.

        Args:
            frame_gray: Grayscale frame at 720p (or scaled)
            config: Detection configuration

        Returns:
            List of Detection objects
        """
        detections = []

        # Need previous frame for differencing
        if self._prev_gray is None or self._prev_gray.shape != frame_gray.shape:
            self._prev_gray = frame_gray.copy()
            return detections

        # Vectorized frame differencing (no loops)
        diff = cv2.absdiff(self._prev_gray, frame_gray)

        # Vectorized threshold
        _, binary_mask = cv2.threshold(diff, config.motion_threshold, 255, cv2.THRESH_BINARY)

        # Vectorized morphology operations (remove noise)
        morph_kernel = self._get_morph_kernel(config.morphology_kernel_size)
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, morph_kernel)
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, morph_kernel)

        # Find contours (optimized OpenCV operation, no Python loops)
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Process contours (minimal iteration, vectorized operations inside)
        timestamp = time.time()
        for contour in contours:
            # Early stopping: if we have enough detections, stop processing
            if max_detections > 0 and len(detections) >= max_detections:
                break

            # Vectorized area calculation
            area = cv2.contourArea(contour)

            # Filter by area
            if area < config.min_detection_area or area > config.max_detection_area:
                continue

            # Vectorized bounding box calculation
            x, y, w, h = cv2.boundingRect(contour)

            # Vectorized moment calculation for centroid
            M = cv2.moments(contour)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = x + w // 2, y + h // 2

            # Confidence based on area (vectorized)
            confidence = min(1.0, area / config.max_detection_area)

            detection = Detection(
                bbox=(x, y, w, h),
                centroid=(cx, cy),
                area=area,
                confidence=confidence,
                detection_type='baseline_motion',
                timestamp=timestamp,
                contour=contour,
                metadata={'threshold': config.motion_threshold}
            )
            detections.append(detection)

        # Update previous frame for next iteration
        self._prev_gray = frame_gray.copy()

        return detections

    def _mog2_detect(self, frame_gray: np.ndarray, config: IntegratedDetectionConfig, max_detections: int = 0) -> List[Detection]:
        """
        Step 3: MOG2 background subtraction detection.

        Best for static cameras - learns what is "background" and detects "foreground" objects.
        Works well for detecting people walking in static scenes.

        Args:
            frame_gray: Grayscale frame
            config: Detection configuration

        Returns:
            List of Detection objects
        """
        detections = []

        # Apply background subtraction
        fg_mask = self._bg_subtractor_mog2.apply(frame_gray)

        # Threshold to remove shadow artifacts (if shadows detected)
        if config.bg_detect_shadows:
            _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

        # Morphology to clean up noise
        morph_kernel = self._get_morph_kernel(config.morphology_kernel_size)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, morph_kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, morph_kernel)

        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Process contours
        timestamp = time.time()
        for contour in contours:
            # Early stopping: if we have enough detections, stop processing
            if max_detections > 0 and len(detections) >= max_detections:
                break

            area = cv2.contourArea(contour)

            if area < config.min_detection_area or area > config.max_detection_area:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            M = cv2.moments(contour)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = x + w // 2, y + h // 2

            confidence = min(1.0, area / config.max_detection_area)

            detection = Detection(
                bbox=(x, y, w, h),
                centroid=(cx, cy),
                area=area,
                confidence=confidence,
                detection_type='mog2_motion',
                timestamp=timestamp,
                contour=contour,
                metadata={'algorithm': 'MOG2'}
            )
            detections.append(detection)

        return detections

    def _knn_detect(self, frame_gray: np.ndarray, config: IntegratedDetectionConfig, max_detections: int = 0) -> List[Detection]:
        """
        Step 3: KNN background subtraction detection.

        Alternative to MOG2, sometimes better for busy/complex scenes.

        Args:
            frame_gray: Grayscale frame
            config: Detection configuration

        Returns:
            List of Detection objects
        """
        detections = []

        # Apply background subtraction
        fg_mask = self._bg_subtractor_knn.apply(frame_gray)

        # Threshold to remove shadow artifacts
        if config.bg_detect_shadows:
            _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

        # Morphology to clean up noise
        morph_kernel = self._get_morph_kernel(config.morphology_kernel_size)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, morph_kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, morph_kernel)

        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Process contours
        timestamp = time.time()
        for contour in contours:
            # Early stopping: if we have enough detections, stop processing
            if max_detections > 0 and len(detections) >= max_detections:
                break

            area = cv2.contourArea(contour)

            if area < config.min_detection_area or area > config.max_detection_area:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            M = cv2.moments(contour)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = x + w // 2, y + h // 2

            confidence = min(1.0, area / config.max_detection_area)

            detection = Detection(
                bbox=(x, y, w, h),
                centroid=(cx, cy),
                area=area,
                confidence=confidence,
                detection_type='knn_motion',
                timestamp=timestamp,
                contour=contour,
                metadata={'algorithm': 'KNN'}
            )
            detections.append(detection)

        return detections

    def _expand_detection_by_hue(self, frame_hsv: np.ndarray, detection: Detection, hue_range: int) -> Detection:
        """
        Expand a color detection to include neighboring pixels with similar hue.

        Only considers hue similarity (not saturation or value), which helps capture
        the full extent of similarly-colored objects.

        Args:
            frame_hsv: Full frame in HSV color space
            detection: Original detection to expand
            hue_range: +/- hue range in OpenCV units (0-179)

        Returns:
            Expanded detection with updated bbox, area, and contour
        """
        # Get mean hue from detection region
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
        region_hsv = frame_hsv[y:y+h, x:x+w]
        mean_hue = float(region_hsv[:, :, 0].mean())

        # Create mask of pixels with similar hue in entire frame
        hue_channel = frame_hsv[:, :, 0].astype(np.float32)

        # Handle hue wraparound (0 and 179 are both red)
        hue_min = mean_hue - hue_range
        hue_max = mean_hue + hue_range

        if hue_min < 0 or hue_max > 179:
            # Wraparound case (e.g., red hues near 0/179)
            if hue_min < 0:
                mask = ((hue_channel >= (180 + hue_min)) | (hue_channel <= hue_max)).astype(np.uint8) * 255
            else:  # hue_max > 179
                mask = ((hue_channel >= hue_min) | (hue_channel <= (hue_max - 180))).astype(np.uint8) * 255
        else:
            # Normal case: simple range check
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
            # Check if this contour contains the original centroid
            if cv2.pointPolygonTest(contour, (float(cx), float(cy)), False) >= 0:
                area = cv2.contourArea(contour)
                if area > max_area:
                    expanded_contour = contour
                    max_area = area

        # If we found an expanded contour, create new detection
        if expanded_contour is not None and max_area > detection.area:
            x_new, y_new, w_new, h_new = cv2.boundingRect(expanded_contour)

            # Calculate new centroid
            M = cv2.moments(expanded_contour)
            if M["m00"] > 0:
                cx_new = int(M["m10"] / M["m00"])
                cy_new = int(M["m01"] / M["m00"])
            else:
                cx_new, cy_new = x_new + w_new // 2, y_new + h_new // 2

            # Create expanded detection
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

        # No expansion possible, return original
        return detection

    def _color_quantization_detect(self, frame_bgr: np.ndarray, config: IntegratedDetectionConfig, max_detections: int = 0) -> List[Detection]:
        """
        Step 4: Color quantization anomaly detection.

        Detects rare colors using histogram-based quantization:
        1. Downsample frame 2x for faster processing
        2. Quantize RGB to 5-6 bits/channel
        3. Build histogram of color frequency
        4. Mark rare colors (below percentile threshold)
        5. Create mask of rare color pixels
        6. Upscale mask back to original resolution
        7. Extract contours as detections

        Performance optimization: Process at half resolution (4x fewer pixels)
        This speeds up from 20-25ms to <10ms at 720p

        Args:
            frame_bgr: BGR color frame (already scaled to processing resolution)
            config: Detection configuration
            max_detections: Stop early after this many detections (0 = no limit)

        Returns:
            List of Detection objects for rare color regions
        """
        detections = []
        timestamp = time.time()

        # OPTIMIZATION: Downsample 2x for color analysis (4x fewer pixels = 4x faster)
        h, w = frame_bgr.shape[:2]
        downsampled = cv2.resize(frame_bgr, (w // 2, h // 2), interpolation=cv2.INTER_LINEAR)

        # Step 1: Quantize colors (vectorized - no Python loops)
        # Reduce from 8 bits (0-255) to N bits (e.g., 5-6 bits)
        bits = config.color_quantization_bits
        scale = 2 ** (8 - bits)  # e.g., 2^2 = 4 for 6-bit

        # Quantize by dividing and rounding (vectorized)
        quantized = (downsampled // scale).astype(np.uint8)

        # Step 2: Build histogram
        # Convert to single-channel index: idx = B + G*64 + R*64^2
        h, w = quantized.shape[:2]
        bins_per_channel = 2 ** bits  # e.g., 64 for 6-bit

        # Vectorized index computation
        color_indices = (
            quantized[:, :, 0].astype(np.int32) +  # B
            quantized[:, :, 1].astype(np.int32) * bins_per_channel +  # G
            quantized[:, :, 2].astype(np.int32) * bins_per_channel ** 2  # R
        )

        # Build histogram (vectorized)
        max_bins = bins_per_channel ** 3
        histogram = np.bincount(color_indices.ravel(), minlength=max_bins)

        # Step 3: Find rare color bins
        nonzero_counts = histogram[histogram > 0]
        if len(nonzero_counts) == 0:
            return detections

        total_pixels = h * w

        # Percentile threshold: colors in bottom N% by frequency
        percentile_threshold = np.percentile(nonzero_counts, config.color_rarity_percentile)

        # Absolute cap: prevent marking common colors as rare
        # If a color appears in >5% of frame, it's not rare even if in bottom percentile
        absolute_max = total_pixels * 0.05

        # Use percentile, but cap it at absolute max (prevents everything being rare)
        threshold = min(percentile_threshold, absolute_max)

        # Create mask of rare bins
        rare_bins = (histogram > 0) & (histogram < threshold)
        rare_bins[0] = False  # Don't mark bin 0 as rare (often black/background)

        # Step 4: Create binary mask of rare color pixels (vectorized)
        rare_mask_small = rare_bins[color_indices].astype(np.uint8) * 255

        # Upscale mask back to original processing resolution
        h_orig, w_orig = frame_bgr.shape[:2]
        rare_mask = cv2.resize(rare_mask_small, (w_orig, h_orig), interpolation=cv2.INTER_NEAREST)

        # Morphology to clean up noise (on full-size mask for better accuracy)
        morph_kernel = self._get_morph_kernel(config.morphology_kernel_size)
        rare_mask = cv2.morphologyEx(rare_mask, cv2.MORPH_OPEN, morph_kernel)
        rare_mask = cv2.morphologyEx(rare_mask, cv2.MORPH_CLOSE, morph_kernel)

        # Step 5: Extract contours (at full processing resolution)
        contours, _ = cv2.findContours(rare_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Process contours
        for contour in contours:
            # Early stopping
            if max_detections > 0 and len(detections) >= max_detections:
                break

            area = cv2.contourArea(contour)

            # Filter by area
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

            # Get dominant color in this region (for visualization)
            region = frame_bgr[y:y+h_box, x:x+w_box]
            if region.size > 0:
                mean_color = region.mean(axis=(0, 1)).astype(int)
                dominant_color = tuple(mean_color.tolist())
            else:
                dominant_color = (0, 0, 0)

            # Confidence based on rarity
            # Scale centroid to downsampled coordinates
            cy_down = cy // 2
            cx_down = cx // 2
            # Bounds check
            if 0 <= cy_down < h and 0 <= cx_down < w:
                bin_idx = color_indices[cy_down, cx_down]
                bin_count = histogram[bin_idx]
                total_pixels = h * w
                rarity = 1.0 - (bin_count / total_pixels)  # Rare = high value
                confidence = min(1.0, rarity * 2.0)  # Scale to 0-1
            else:
                # Fallback if out of bounds
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
            # Convert frame to HSV once for all expansions
            frame_hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

            # Expand each detection
            expanded_detections = []
            for detection in detections:
                expanded = self._expand_detection_by_hue(frame_hsv, detection, config.hue_expansion_range)

                # Re-check area filter after expansion
                if expanded.area >= config.color_min_detection_area and expanded.area <= config.max_detection_area:
                    expanded_detections.append(expanded)

            detections = expanded_detections

        return detections

    def _apply_persistence_filter(self, current_mask: np.ndarray, config: IntegratedDetectionConfig) -> np.ndarray:
        """
        Step 3: Apply temporal persistence filter.

        Objects must appear in N of M frames to be considered valid.
        Reduces flicker and false positives from noise.

        Args:
            current_mask: Binary mask for current frame
            config: Detection configuration

        Returns:
            Filtered binary mask where objects have persisted
        """
        # Add current mask to history
        self._detection_masks.append(current_mask.copy())

        # Need minimum number of frames
        if len(self._detection_masks) < config.persistence_threshold:
            return current_mask

        # Stack masks and count occurrences per pixel (vectorized)
        mask_stack = np.stack(list(self._detection_masks), axis=0).astype(np.uint8)

        # Count how many frames each pixel was detected in
        persistence_count = np.sum(mask_stack > 0, axis=0)

        # Keep pixels that appeared in at least N frames
        persistent_mask = (persistence_count >= config.persistence_threshold).astype(np.uint8) * 255

        return persistent_mask

    def _fuse_detections(self, motion_detections: List[Detection], color_detections: List[Detection],
                        config: IntegratedDetectionConfig) -> List[Detection]:
        """
        Step 5: Fuse motion and color detections using configured mode.

        Smart skip: Returns immediately if only one detection type is available
        (zero overhead when fusion is not needed).

        Args:
            motion_detections: List of motion detections
            color_detections: List of color detections
            config: Detection configuration

        Returns:
            Fused list of detections
        """
        # SMART SKIP: If only one source, return it directly (zero overhead)
        if not motion_detections:
            return color_detections
        if not color_detections:
            return motion_detections

        # If fusion disabled, just concatenate
        if not config.enable_fusion:
            return motion_detections + color_detections

        # Fusion logic based on mode
        fused_detections = []

        if config.fusion_mode == FusionMode.UNION:
            # UNION: Return all detections from both sources
            # Mark overlapping detections as 'fused' with boosted confidence
            all_detections = motion_detections + color_detections

            # Simple approach: merge detections that overlap significantly
            processed = [False] * len(all_detections)

            for i, det1 in enumerate(all_detections):
                if processed[i]:
                    continue

                # Check for overlaps with remaining detections
                overlapping = [det1]
                processed[i] = True

                for j in range(i + 1, len(all_detections)):
                    if processed[j]:
                        continue
                    det2 = all_detections[j]

                    # Calculate IoU (Intersection over Union)
                    iou = self._calculate_iou(det1.bbox, det2.bbox)
                    if iou > 0.3:  # 30% overlap threshold
                        overlapping.append(det2)
                        processed[j] = True

                # Merge overlapping detections
                if len(overlapping) > 1:
                    merged = self._merge_detections(overlapping)
                    merged.detection_type = 'fused'
                    fused_detections.append(merged)
                else:
                    fused_detections.append(det1)

        elif config.fusion_mode == FusionMode.INTERSECTION:
            # INTERSECTION: Only keep detections that appear in BOTH sources
            for motion_det in motion_detections:
                for color_det in color_detections:
                    iou = self._calculate_iou(motion_det.bbox, color_det.bbox)
                    if iou > 0.3:  # Overlap threshold
                        merged = self._merge_detections([motion_det, color_det])
                        merged.detection_type = 'fused'
                        merged.confidence = min(1.0, (motion_det.confidence + color_det.confidence) / 2 * 1.5)  # Boost confidence
                        fused_detections.append(merged)

        elif config.fusion_mode == FusionMode.COLOR_PRIORITY:
            # COLOR_PRIORITY: Start with color, add non-overlapping motion
            fused_detections = color_detections.copy()
            for motion_det in motion_detections:
                # Check if this motion detection overlaps with any color detection
                overlaps = False
                for color_det in color_detections:
                    if self._calculate_iou(motion_det.bbox, color_det.bbox) > 0.3:
                        overlaps = True
                        break
                if not overlaps:
                    fused_detections.append(motion_det)

        elif config.fusion_mode == FusionMode.MOTION_PRIORITY:
            # MOTION_PRIORITY: Start with motion, add non-overlapping color
            fused_detections = motion_detections.copy()
            for color_det in color_detections:
                # Check if this color detection overlaps with any motion detection
                overlaps = False
                for motion_det in motion_detections:
                    if self._calculate_iou(color_det.bbox, motion_det.bbox) > 0.3:
                        overlaps = True
                        break
                if not overlaps:
                    fused_detections.append(color_det)

        return fused_detections

    def _calculate_iou(self, bbox1: Tuple[int, int, int, int], bbox2: Tuple[int, int, int, int]) -> float:
        """
        Calculate Intersection over Union (IoU) between two bounding boxes.

        Args:
            bbox1: (x, y, w, h) for first box
            bbox2: (x, y, w, h) for second box

        Returns:
            IoU score (0.0 to 1.0)
        """
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2

        # Calculate intersection rectangle
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)

        if x_right < x_left or y_bottom < y_top:
            return 0.0  # No overlap

        # Calculate areas
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        box1_area = w1 * h1
        box2_area = w2 * h2
        union_area = box1_area + box2_area - intersection_area

        if union_area == 0:
            return 0.0

        return intersection_area / union_area

    def _merge_detections(self, detections: List[Detection]) -> Detection:
        """
        Merge multiple overlapping detections into one.

        Args:
            detections: List of detections to merge

        Returns:
            Single merged detection
        """
        if len(detections) == 1:
            return detections[0]

        # Find bounding box that encompasses all detections
        min_x = min(d.bbox[0] for d in detections)
        min_y = min(d.bbox[1] for d in detections)
        max_x = max(d.bbox[0] + d.bbox[2] for d in detections)
        max_y = max(d.bbox[1] + d.bbox[3] for d in detections)

        merged_bbox = (min_x, min_y, max_x - min_x, max_y - min_y)

        # Average centroid
        avg_cx = int(np.mean([d.centroid[0] for d in detections]))
        avg_cy = int(np.mean([d.centroid[1] for d in detections]))

        # Sum area
        total_area = sum(d.area for d in detections)

        # Average confidence
        avg_confidence = np.mean([d.confidence for d in detections])

        # Use timestamp from first detection
        timestamp = detections[0].timestamp

        # Determine detection type
        types = [d.detection_type for d in detections]
        if 'color_anomaly' in types and any('motion' in t for t in types):
            detection_type = 'fused'
        else:
            detection_type = detections[0].detection_type

        return Detection(
            bbox=merged_bbox,
            centroid=(avg_cx, avg_cy),
            area=total_area,
            confidence=avg_confidence,
            detection_type=detection_type,
            timestamp=timestamp,
            metadata={'merged_from': len(detections)}
        )

    def _apply_temporal_voting(self, current_detections: List[Detection],
                              config: IntegratedDetectionConfig) -> List[Detection]:
        """
        Step 5: Apply temporal majority voting to reduce flicker.

        Detections must appear in N of M frames to be considered valid.
        Works with any detection source (motion-only, color-only, or fused).

        Args:
            current_detections: Detections from current frame
            config: Detection configuration

        Returns:
            Filtered detections that have persisted across frames
        """
        if not config.enable_temporal_voting:
            return current_detections

        # Add current detections to history
        self._temporal_detection_history.append(current_detections)

        # Need full window before we start filtering
        # (Otherwise we're not using the full M frames for voting)
        if len(self._temporal_detection_history) < config.temporal_window_frames:
            return current_detections

        # Vote: Keep detections that appear in N of M frames
        voted_detections = []

        for current_det in current_detections:
            # Count how many recent frames had a similar detection
            vote_count = 0

            for past_detections in self._temporal_detection_history:
                # Check if any detection in this past frame overlaps with current
                for past_det in past_detections:
                    iou = self._calculate_iou(current_det.bbox, past_det.bbox)
                    if iou > 0.3:  # Overlapping detection found
                        vote_count += 1
                        break

            # Keep detection if it appeared in enough frames
            if vote_count >= config.temporal_threshold_frames:
                voted_detections.append(current_det)

        return voted_detections

    def _apply_aspect_ratio_filter(self, detections: List[Detection], config: IntegratedDetectionConfig) -> List[Detection]:
        """
        Task A3: Filter detections by aspect ratio.

        Removes detections with unrealistic shapes (too tall/thin or too wide/flat).
        Useful for filtering out scan lines, compression artifacts, and noise.

        Args:
            detections: List of detections to filter
            config: Detection configuration

        Returns:
            Filtered list of detections
        """
        if not config.enable_aspect_ratio_filter:
            return detections

        filtered = []
        for detection in detections:
            x, y, w, h = detection.bbox

            # Avoid division by zero
            if h == 0:
                continue

            aspect_ratio = w / h

            # Keep detection if aspect ratio is within acceptable range
            if config.min_aspect_ratio <= aspect_ratio <= config.max_aspect_ratio:
                filtered.append(detection)

        return filtered

    def _apply_color_exclusion_filter(self, detections: List[Detection], frame_bgr: np.ndarray,
                                     config: IntegratedDetectionConfig) -> List[Detection]:
        """
        Task A2: Filter detections by excluded hue ranges (background learning).

        Removes detections whose dominant color matches excluded hue ranges.
        Useful for filtering out sky, water, grass, and other background colors.

        Args:
            detections: List of detections to filter
            frame_bgr: Original BGR frame
            config: Detection configuration

        Returns:
            Filtered list of detections
        """
        if not config.enable_color_exclusion or not config.excluded_hue_ranges:
            return detections

        # Convert frame to HSV for hue analysis
        frame_hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

        filtered = []
        for detection in detections:
            x, y, w, h = detection.bbox

            # Bounds check
            h_frame, w_frame = frame_hsv.shape[:2]
            if x < 0 or y < 0 or x + w > w_frame or y + h > h_frame:
                # Out of bounds, skip
                continue

            # Extract dominant hue from detection region
            region_hsv = frame_hsv[y:y+h, x:x+w]
            if region_hsv.size == 0:
                continue

            mean_hue = float(region_hsv[:, :, 0].mean())

            # Check if this hue falls within any excluded range
            is_excluded = False
            for hue_min, hue_max in config.excluded_hue_ranges:
                # Handle hue wraparound (red color wraps at 0/179)
                if hue_min > hue_max:
                    # Wraparound case (e.g., red: 170-10 means 170-179 OR 0-10)
                    if mean_hue >= hue_min or mean_hue <= hue_max:
                        is_excluded = True
                        break
                else:
                    # Normal case
                    if hue_min <= mean_hue <= hue_max:
                        is_excluded = True
                        break

            # Keep detection if it's not excluded
            if not is_excluded:
                filtered.append(detection)

        return filtered

    def sample_region_colors(self, frame_bgr: np.ndarray, x1: int, y1: int, x2: int, y2: int,
                           hue_tolerance: float = 15.0) -> List[Tuple[float, float]]:
        """
        Task A2: Sample dominant colors from a region and return hue ranges to exclude.

        Analyzes a rectangular region and finds the top dominant hues (colors).
        Returns hue ranges that can be added to excluded_hue_ranges.

        Args:
            frame_bgr: BGR frame to sample from
            x1, y1, x2, y2: Rectangle coordinates
            hue_tolerance: +/- tolerance for each dominant hue (degrees on 0-360 scale, converted to 0-179)

        Returns:
            List of (hue_min, hue_max) tuples to add to exclusion list
        """
        # Ensure coordinates are in order
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        # Bounds check
        h, w = frame_bgr.shape[:2]
        x1 = max(0, min(x1, w - 1))
        y1 = max(0, min(y1, h - 1))
        x2 = max(0, min(x2, w - 1))
        y2 = max(0, min(y2, h - 1))

        if x2 <= x1 or y2 <= y1:
            return []

        # Extract region and convert to HSV
        region_bgr = frame_bgr[y1:y2, x1:x2]
        if region_bgr.size == 0:
            return []

        region_hsv = cv2.cvtColor(region_bgr, cv2.COLOR_BGR2HSV)

        # Build histogram of hues in the region
        hue_channel = region_hsv[:, :, 0]
        hist = cv2.calcHist([region_hsv], [0], None, [180], [0, 180])

        # Find top 5 dominant hues
        top_hues = []
        hist_flat = hist.flatten()

        # Get indices of top 5 peaks
        top_indices = np.argsort(hist_flat)[-5:][::-1]

        # Convert hue_tolerance from degrees (0-360) to OpenCV scale (0-179)
        tolerance_cv = hue_tolerance * 179.0 / 360.0

        hue_ranges = []
        for hue_peak in top_indices:
            if hist_flat[hue_peak] > 0:  # Only include hues that actually appear
                hue_min = max(0, hue_peak - tolerance_cv)
                hue_max = min(179, hue_peak + tolerance_cv)

                # Handle wraparound for red
                if hue_peak < tolerance_cv:
                    # Near 0 (red), wraparound to 179
                    hue_ranges.append((179 - (tolerance_cv - hue_peak), 179.0))
                    hue_ranges.append((0.0, hue_max))
                elif hue_peak > (179 - tolerance_cv):
                    # Near 179 (red), wraparound to 0
                    hue_ranges.append((hue_min, 179.0))
                    hue_ranges.append((0.0, tolerance_cv - (179 - hue_peak)))
                else:
                    hue_ranges.append((hue_min, hue_max))

        return hue_ranges

    def process_frame(self, frame: np.ndarray, timestamp: float) -> Tuple[np.ndarray, List[Detection], StageTimings]:
        """
        Process a frame through the integrated detection pipeline.

        Args:
            frame: Input BGR frame
            timestamp: Frame timestamp

        Returns:
            Tuple of (annotated_frame, detections, timings)
        """
        # Create timing tracker
        timings = StageTimings()
        overall_start = time.perf_counter()

        # Step 0: Frame queue management (simulated capture timing)
        capture_start = time.perf_counter()
        self.frame_queue.put(frame, timestamp)
        working_frame, _ = self.frame_queue.get()
        if working_frame is None:
            working_frame = frame
        timings.capture_ms = (time.perf_counter() - capture_start) * 1000

        # Preprocessing stage
        preprocess_start = time.perf_counter()
        with self.config_lock:
            config = self.config

        # Step 1: Scale to processing resolution (works for ANY input resolution)
        # Examples: 4K→720p, 1080p→720p, 480p→480p (no scaling)
        h, w = working_frame.shape[:2]
        scale_factor = 1.0  # Track scale for coordinate transformation back to original size

        if w > config.processing_width or h > config.processing_height:
            # Input is larger than processing resolution - scale DOWN
            scale_factor = min(config.processing_width / w, config.processing_height / h)
            new_w, new_h = int(w * scale_factor), int(h * scale_factor)
            # Ensure non-zero dimensions
            new_w = max(1, new_w)
            new_h = max(1, new_h)
            processing_frame = cv2.resize(working_frame, (new_w, new_h),
                                         interpolation=cv2.INTER_LINEAR)
        else:
            # Input is smaller or equal - process at original resolution
            processing_frame = working_frame
            scale_factor = 1.0

        # Convert to grayscale for baseline detection (vectorized operation)
        processing_gray = cv2.cvtColor(processing_frame, cv2.COLOR_BGR2GRAY)

        # Optional: Apply Gaussian blur to reduce noise (vectorized)
        if config.blur_kernel_size > 1:
            processing_gray = cv2.GaussianBlur(processing_gray,
                                               (config.blur_kernel_size, config.blur_kernel_size),
                                               0)

        timings.preprocessing_ms = (time.perf_counter() - preprocess_start) * 1000

        # Step 3: Pre-check for camera movement (BEFORE expensive detection)
        # Use lightweight frame differencing to detect if whole screen is moving
        detection_start = time.perf_counter()
        is_camera_moving = False
        detections = []

        if config.pause_on_camera_movement and self._prev_gray is not None:
            # Quick frame difference check
            if self._prev_gray.shape == processing_gray.shape:
                diff = cv2.absdiff(self._prev_gray, processing_gray)
                _, diff_mask = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)

                # Calculate percentage of frame that changed
                changed_pixels = np.count_nonzero(diff_mask)
                total_pixels = diff_mask.size
                change_ratio = changed_pixels / total_pixels

                # If more than threshold of frame changed, assume camera movement
                if change_ratio > config.camera_movement_threshold:
                    is_camera_moving = True
                    # Skip expensive detection entirely!
                    detections = []

        # Calculate early stopping limit (2x the render limit to allow for filtering/sorting)
        max_to_detect = config.max_detections_to_render * 2 if config.max_detections_to_render > 0 else 0

        # Step 3: Motion detection (if enabled)
        # Skip motion detection when camera is moving (too many false positives)
        motion_detections = []
        motion_start = time.perf_counter()
        if config.enable_motion and not is_camera_moving:
            if config.motion_algorithm == MotionAlgorithm.MOG2:
                motion_detections = self._mog2_detect(processing_gray, config, max_to_detect)
            elif config.motion_algorithm == MotionAlgorithm.KNN:
                motion_detections = self._knn_detect(processing_gray, config, max_to_detect)
            else:  # FRAME_DIFF
                motion_detections = self._baseline_detect_720p(processing_gray, config, max_to_detect)
        timings.motion_detection_ms = (time.perf_counter() - motion_start) * 1000

        # Step 4: Color quantization detection (if enabled)
        # Color detection runs even when camera is moving (anomalies are still valid)
        color_detections = []
        color_start = time.perf_counter()
        if config.enable_color_quantization:
            color_detections = self._color_quantization_detect(processing_frame, config, max_to_detect)
        timings.color_detection_ms = (time.perf_counter() - color_start) * 1000

        timings.detection_ms = (time.perf_counter() - detection_start) * 1000

        # Store current frame for next camera movement check
        self._prev_gray = processing_gray.copy()

        # Step 5: Fusion & Temporal Smoothing
        fusion_start = time.perf_counter()

        # Fuse motion and color detections (smart skip if only one source)
        detections = self._fuse_detections(motion_detections, color_detections, config)

        # Apply temporal voting to reduce flicker (works with any detection source)
        detections = self._apply_temporal_voting(detections, config)

        # Task A: Apply false positive reduction filters
        detections = self._apply_aspect_ratio_filter(detections, config)
        detections = self._apply_color_exclusion_filter(detections, processing_frame, config)

        timings.fusion_ms = (time.perf_counter() - fusion_start) * 1000

        # Rendering stage
        render_start = time.perf_counter()

        # Choose rendering resolution based on config
        if config.render_at_processing_res:
            # Render at processing resolution (much faster for high-res videos)
            render_frame = processing_frame.copy()
            render_inverse_scale = 1.0  # No scaling needed - coords are already at processing res
        else:
            # Render at original resolution (default, higher quality)
            render_frame = working_frame.copy()
            # Calculate inverse scale to transform detection coordinates back to original resolution
            # This works for ANY video size: 480p, 720p, 1080p, 4K, etc.
            # - 1920x1080 → 1280x720: scale=0.667, inverse=1.5 → coords × 1.5
            # - 3840x2160 → 1280x720: scale=0.333, inverse=3.0 → coords × 3.0
            # - 640x480 (no scale): scale=1.0, inverse=1.0 → coords × 1.0 (unchanged)
            render_inverse_scale = 1.0 / scale_factor if scale_factor > 0.0 else 1.0

        annotated_frame = render_frame

        # Step 3: Limit detections for performance (prevents render slowdown)
        detections_to_render = detections
        total_detections = len(detections)
        detections_dropped = 0

        if config.show_detections and detections:
            # Limit rendering if too many detections (camera movement scenario)
            if config.max_detections_to_render > 0 and len(detections) > config.max_detections_to_render:
                # Sort by confidence * area (prioritize high-confidence, larger detections)
                detections_sorted = sorted(detections,
                                          key=lambda d: d.confidence * d.area,
                                          reverse=True)
                detections_to_render = detections_sorted[:config.max_detections_to_render]
                detections_dropped = len(detections) - config.max_detections_to_render

            # Draw the selected detections using configured render style
            for i, detection in enumerate(detections_to_render):
                # Scale coordinates from processing resolution to render resolution
                x, y, w, h = detection.bbox
                x_scaled = int(x * render_inverse_scale)
                y_scaled = int(y * render_inverse_scale)
                w_scaled = int(w * render_inverse_scale)
                h_scaled = int(h * render_inverse_scale)

                # Scale centroid
                cx_scaled = int(detection.centroid[0] * render_inverse_scale)
                cy_scaled = int(detection.centroid[1] * render_inverse_scale)

                # Color based on detection type OR detected hue
                if config.use_detection_color_for_rendering and 'dominant_color' in detection.metadata:
                    # Use the detected color with 100% saturation and 100% value
                    try:
                        bgr_color = detection.metadata['dominant_color']
                        # Convert BGR to HSV to get hue
                        bgr_pixel = np.uint8([[[bgr_color[0], bgr_color[1], bgr_color[2]]]])
                        hsv_pixel = cv2.cvtColor(bgr_pixel, cv2.COLOR_BGR2HSV)
                        hue = hsv_pixel[0][0][0]

                        # Create new color with same hue but 100% saturation and 100% value
                        hsv_vibrant = np.uint8([[[hue, 255, 255]]])
                        bgr_vibrant = cv2.cvtColor(hsv_vibrant, cv2.COLOR_HSV2BGR)
                        color = tuple(int(x) for x in bgr_vibrant[0][0])
                    except Exception:
                        # Fallback to default color if conversion fails
                        color = (255, 0, 255)  # Magenta
                elif detection.detection_type == 'fused':
                    # Fused detections (motion + color): Cyan/Blue tones (highest confidence)
                    if detection.confidence > 0.7:
                        color = (255, 255, 0)  # Cyan - very high confidence
                    elif detection.confidence > 0.4:
                        color = (255, 128, 0)  # Light blue - high
                    else:
                        color = (200, 100, 0)  # Dark blue - medium
                elif detection.detection_type == 'color_anomaly':
                    # Color anomalies: Magenta/Purple tones
                    if detection.confidence > 0.7:
                        color = (255, 0, 255)  # Magenta - high confidence
                    elif detection.confidence > 0.4:
                        color = (255, 0, 128)  # Purple - medium
                    else:
                        color = (200, 0, 100)  # Dark purple - low
                else:
                    # Motion detections: Green tones (existing)
                    if detection.confidence > 0.7:
                        color = (0, 255, 0)  # Green - high confidence
                    elif detection.confidence > 0.4:
                        color = (0, 255, 255)  # Yellow - medium
                    else:
                        color = (0, 165, 255)  # Orange - low

                # Render based on individual toggles for performance tuning
                # Draw contours if enabled (slowest)
                if config.render_contours and detection.contour is not None:
                    scaled_contour = (detection.contour * render_inverse_scale).astype(np.int32)
                    cv2.drawContours(annotated_frame, [scaled_contour], -1, color, 2)

                # Draw shape based on render_shape
                if config.render_shape == 0:  # Box
                    cv2.rectangle(annotated_frame, (x_scaled, y_scaled),
                                (x_scaled + w_scaled, y_scaled + h_scaled), color, 2)
                    # Add small centroid marker
                    cv2.circle(annotated_frame, (cx_scaled, cy_scaled), 3, color, -1)
                elif config.render_shape == 1:  # Circle
                    radius = max(5, int(np.sqrt(detection.area) * render_inverse_scale / 2))
                    cv2.circle(annotated_frame, (cx_scaled, cy_scaled), radius, color, 2)
                elif config.render_shape == 2:  # Dot (small filled circle at centroid)
                    cv2.circle(annotated_frame, (cx_scaled, cy_scaled), 5, color, -1)
                # elif config.render_shape == 3: pass  # Off - don't render any shape

                # Draw text if enabled (slow)
                if config.render_text:
                    if detection.detection_type == 'fused':
                        label = f"#{i+1} FUSED {int(detection.area)}px"
                    elif detection.detection_type == 'color_anomaly':
                        label = f"#{i+1} COLOR {int(detection.area)}px"
                    else:
                        label = f"#{i+1} MOTION {int(detection.area)}px"
                    cv2.putText(annotated_frame, label, (x_scaled, max(15, y_scaled - 5)),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)

            # Show warning if we dropped detections for performance
            if detections_dropped > 0:
                warning_text = f"⚠ {total_detections} detections ({detections_dropped} not shown for performance)"
                cv2.putText(annotated_frame, warning_text, (10, annotated_frame.shape[0] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1, cv2.LINE_AA)

        # Show camera movement indicator at top of screen
        if is_camera_moving:
            # Draw semi-transparent overlay at top
            overlay = annotated_frame.copy()
            h, w = annotated_frame.shape[:2]

            # Background bar at top
            cv2.rectangle(overlay, (0, 0), (w, 80), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, annotated_frame, 0.3, 0, annotated_frame)

            # Text centered at top
            cv2.putText(annotated_frame, "CAMERA MOVEMENT DETECTED",
                       (w//2 - 190, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2, cv2.LINE_AA)
            cv2.putText(annotated_frame, "Motion detection paused (color still active)",
                       (w//2 - 210, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        # Add timing overlay
        if config.show_timing_overlay:
            annotated_frame = self.timing_renderer.render(
                annotated_frame, self.metrics, timings
            )

        # Upscale annotated frame to original resolution if we rendered at processing res
        if config.render_at_processing_res and scale_factor < 1.0:
            h_orig, w_orig = working_frame.shape[:2]
            annotated_frame = cv2.resize(annotated_frame, (w_orig, h_orig),
                                        interpolation=cv2.INTER_LINEAR)

        timings.render_ms = (time.perf_counter() - render_start) * 1000

        # Total timing
        timings.total_ms = (time.perf_counter() - overall_start) * 1000

        # Update metrics
        self.metrics.update(timings, len(detections))

        # Update FPS
        self._update_fps()

        # Check for dropped frames
        dropped = self.frame_queue.reset_dropped_count()
        if dropped > 0:
            self.metrics.dropped_frames += dropped

        # Emit signals
        self.frameProcessed.emit(annotated_frame, detections, self.metrics)

        # Emit performance update every second
        current_time = time.time()
        if current_time - self._last_fps_update >= 1.0:
            self.performanceUpdate.emit(self.metrics.to_dict())
            self._last_fps_update = current_time

        return annotated_frame, detections, timings

    def _update_fps(self):
        """Update FPS calculation."""
        self._fps_counter += 1
        current_time = time.time()
        elapsed = current_time - self._fps_start_time

        if elapsed >= 1.0:
            self.metrics.fps = self._fps_counter / elapsed
            self._fps_counter = 0
            self._fps_start_time = current_time

    def get_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics."""
        return self.metrics

    def reset_metrics(self):
        """Reset performance metrics."""
        self.metrics = PerformanceMetrics()
        self._fps_counter = 0
        self._fps_start_time = time.time()
        self.logger.info("Performance metrics reset")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_timing_summary(timings: StageTimings) -> str:
    """Format timing information as readable string."""
    return (f"motion={timings.motion_detection_ms:.1f}ms, "
            f"color={timings.color_detection_ms:.1f}ms, "
            f"render={timings.render_ms:.1f}ms, "
            f"total={timings.total_ms:.1f}ms, "
            f"FPS={1000.0/timings.total_ms if timings.total_ms > 0 else 0:.1f}")
