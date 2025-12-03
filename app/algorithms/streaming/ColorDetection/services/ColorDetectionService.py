"""
ColorDetectionService.py - High-performance color detection for live streams

Optimized HSV-based color detection service designed for real-time RTMP streams
with <100ms processing latency per frame. Integrates with existing ADIAT HSV algorithms.

This service is part of the ColorDetection algorithm module.
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
import traceback

from PySide6.QtCore import QObject, QThread, Signal
from helpers.ColorUtils import ColorUtils
from core.services.LoggerService import LoggerService
from core.services.streaming.StreamingUtils import (
    FrameQueue, PerformanceMetrics, StageTimings
)
from enum import Enum
from collections import deque
import threading


# ═══════════════════════════════════════════════════════════════════════════
# ENUMS AND CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

class MotionAlgorithm(Enum):
    """Motion detection algorithms."""
    FRAME_DIFF = "frame_diff"  # Simple frame differencing
    MOG2 = "mog2"  # Gaussian mixture model background subtraction
    KNN = "knn"  # K-nearest neighbors background subtraction


class FusionMode(Enum):
    """Detection fusion modes."""
    UNION = "union"  # All detections, merge overlapping
    INTERSECTION = "intersection"  # Only detections in both sources
    COLOR_PRIORITY = "color_priority"  # Start with color, add non-overlapping motion
    MOTION_PRIORITY = "motion_priority"  # Start with motion, add non-overlapping color


# ═══════════════════════════════════════════════════════════════════════════
# THREADED CAPTURE INFRASTRUCTURE
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class Detection:
    """Container for color detection result."""
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    centroid: Tuple[int, int]  # center point
    area: float  # pixel area
    confidence: float  # detection confidence 0-1
    timestamp: float  # detection time
    contour: np.ndarray = field(repr=False)  # original contour data
    detection_type: str = "color"  # Type: "color", "motion", "fused"
    color: Optional[Tuple[int, int, int]] = None  # BGR color for rendering
    color_id: Optional[int] = None  # Index of the color range that matched (0-based)
    mean_color: Optional[Tuple[int, int, int]] = None  # Mean BGR color of detected region
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata


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
    hsv_ranges: Optional[Dict[str, Any]] = None  # Precise HSV range data from new picker (single range for backward compatibility)
    hsv_ranges_list: Optional[List[Dict[str, Any]]] = None  # Multiple HSV ranges for multi-color detection
    processing_resolution: Optional[Tuple[int, int]] = None  # (width, height) to downsample for color detection
    motion_processing_resolution: Optional[Tuple[int, int]] = None  # Separate (width, height) for motion detection (None = use processing_resolution)

    target_capture_fps: Optional[float] = None  # Optional FPS limit for capture

    # Hue Expansion Options
    enable_hue_expansion: bool = False  # Expand detected colors to similar hues
    hue_expansion_range: int = 5  # Hue expansion range in OpenCV units (0-30)

    # Motion Detection Options
    enable_motion_detection: bool = False  # Enable motion detection
    motion_algorithm: MotionAlgorithm = MotionAlgorithm.KNN  # Algorithm to use
    min_detection_area: int = 100  # Minimum motion detection area (pixels)
    max_detection_area: int = 1000  # Maximum motion detection area (pixels)
    motion_threshold: int = 1  # Threshold for frame differencing
    blur_kernel_size: int = 5  # Gaussian blur kernel size
    morphology_kernel_size: int = 3  # Morphology kernel size
    persistence_frames: int = 15  # Persistence filter window (M)
    persistence_threshold: int = 7  # Persistence filter threshold (N of M)
    bg_history: int = 20  # Number of frames for background learning
    bg_var_threshold: float = 20.0  # Variance threshold for MOG2
    bg_detect_shadows: bool = False  # Detect shadows in background subtraction
    pause_on_camera_movement: bool = True  # Pause motion detection when camera moves
    camera_movement_threshold: float = 0.01  # Pause motion detection when camera moves (1% change)
    motion_confidence_threshold: float = 0.0  # Minimum confidence threshold for motion detections (0-1)

    # Temporal Voting Options
    enable_temporal_voting: bool = False  # Enable temporal voting across frames
    temporal_window_frames: int = 3  # M: Number of frames to track
    temporal_threshold_frames: int = 2  # N: Must appear in N frames to be valid

    # Detection Clustering Options
    enable_detection_clustering: bool = False  # Cluster nearby detections
    clustering_distance: float = 50.0  # Pixel distance threshold for clustering

    # Detection Fusion Options
    enable_detection_fusion: bool = False  # Fuse color and motion detections
    fusion_mode: FusionMode = FusionMode.UNION  # How to combine detections

    # False Positive Reduction Options
    enable_aspect_ratio_filter: bool = False  # Filter detections by aspect ratio
    min_aspect_ratio: float = 0.2  # Minimum aspect ratio (width/height)
    max_aspect_ratio: float = 5.0  # Maximum aspect ratio (width/height)

    # Rendering Shape Options
    render_shape: int = 0  # 0=box+centroid, 1=circle, 2=dot, 3=off
    render_text: bool = True  # Show labels (can be slow)
    render_contours: bool = False  # Show contour outlines (slowest)
    render_at_processing_res: bool = False  # Render at processing resolution (faster)
    use_detection_color_for_rendering: bool = False  # Color shapes by detected hue

    # Performance Limits
    max_detections_to_render: int = 0  # Limit rendering (0 = unlimited)
    max_motion_detections: int = 5  # Limit motion detection processing (0 = unlimited, recommended: 5-100 for performance)

    # Overlay Options
    show_detections: bool = True  # Toggle detection rendering


class ColorDetectionService(QObject):
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

    def __init__(self, parent=None):
        super().__init__(parent)
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

        # Motion detection state
        self._prev_frame = None  # Previous frame for frame differencing
        self._mog2_subtractor = None  # MOG2 background subtractor
        self._knn_subtractor = None  # KNN background subtractor
        self._camera_is_moving = False  # Camera movement detection flag

        # Persistence filter state (for motion detections)
        self._motion_detection_history = deque(maxlen=30)  # History of recent motion detections

        # Temporal voting state (for all detections)
        self._detection_history = deque(maxlen=10)  # History of recent detections

        # Rendering state (for render_at_processing_res)
        self._processing_frame = None  # Lower resolution frame used for detection
        self._original_frame = None  # Original high resolution frame
        self._current_scale_factor = 1.0  # Scale factor between processing and original

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

            # Check if we have multiple HSV ranges for multi-color detection
            if self._config.hsv_ranges_list and len(self._config.hsv_ranges_list) > 0:
                # Process all color ranges
                all_ranges = []
                for hsv_data in self._config.hsv_ranges_list:
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
                        all_ranges.append(
                            (np.array([h_low, s_low, v_low], dtype=np.uint8),
                             np.array([179, s_high, v_high], dtype=np.uint8))
                        )
                        all_ranges.append(
                            (np.array([0, s_low, v_low], dtype=np.uint8),
                             np.array([h_high, s_high, v_high], dtype=np.uint8))
                        )
                    else:
                        # Normal range - single range
                        all_ranges.append(
                            (np.array([h_low, s_low, v_low], dtype=np.uint8),
                             np.array([h_high, s_high, v_high], dtype=np.uint8))
                        )

                self._hsv_ranges = all_ranges
                self.logger.info(f"Loaded {len(self._config.hsv_ranges_list)} color ranges ({len(all_ranges)} HSV ranges after hue wrapping)")

            # Check if we have a single precise HSV range from the new picker (backward compatibility)
            elif self._config.hsv_ranges:
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
        Perform real-time detection on a frame with integrated color + motion detection.

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

            # Store original dimensions
            original_height, original_width = frame.shape[:2]
            color_scale_factor = 1.0
            motion_scale_factor = 1.0

            # Store original frame for render_at_processing_res feature
            self._original_frame = frame
            self._current_scale_factor = 1.0

            # Create separate frames for color and motion detection
            color_processing_frame = frame.copy()
            motion_processing_frame = frame.copy()

            # ═══════════════════════════════════════════════════════════════
            # DOWNSAMPLE COLOR FRAME
            # ═══════════════════════════════════════════════════════════════
            color_scaled_config = config
            if config.processing_resolution is not None:
                target_width, target_height = config.processing_resolution

                if original_width > target_width or original_height > target_height:
                    color_scale_factor = min(
                        target_width / original_width,
                        target_height / original_height
                    )
                    new_width = int(original_width * color_scale_factor)
                    new_height = int(original_height * color_scale_factor)

                    color_processing_frame = cv2.resize(frame, (new_width, new_height),
                                                        interpolation=cv2.INTER_LINEAR)

                    # Store for render_at_processing_res feature (use color frame)
                    self._processing_frame = color_processing_frame
                    self._current_scale_factor = color_scale_factor

                    # Create scaled config for color detection
                    color_scaled_config = HSVConfig(
                        target_color_rgb=config.target_color_rgb,
                        hue_threshold=config.hue_threshold,
                        saturation_threshold=config.saturation_threshold,
                        value_threshold=config.value_threshold,
                        min_area=int(config.min_area * color_scale_factor * color_scale_factor),
                        max_area=int(config.max_area * color_scale_factor * color_scale_factor),
                        confidence_threshold=config.confidence_threshold,
                        morphology_enabled=config.morphology_enabled,
                        gpu_acceleration=config.gpu_acceleration,
                        show_labels=config.show_labels,
                        hsv_ranges=config.hsv_ranges,
                        hsv_ranges_list=config.hsv_ranges_list,
                        processing_resolution=None,  # Already at target resolution
                        target_capture_fps=config.target_capture_fps,
                        # Hue expansion
                        enable_hue_expansion=config.enable_hue_expansion,
                        hue_expansion_range=config.hue_expansion_range,
                        # Motion detection
                        enable_motion_detection=config.enable_motion_detection,
                        motion_algorithm=config.motion_algorithm,
                        min_detection_area=int(config.min_detection_area * color_scale_factor * color_scale_factor),
                        max_detection_area=int(config.max_detection_area * color_scale_factor * color_scale_factor),
                        max_motion_detections=config.max_motion_detections,
                        motion_threshold=config.motion_threshold,
                        blur_kernel_size=config.blur_kernel_size,
                        morphology_kernel_size=config.morphology_kernel_size,
                        persistence_frames=config.persistence_frames,
                        persistence_threshold=config.persistence_threshold,
                        bg_history=config.bg_history,
                        bg_var_threshold=config.bg_var_threshold,
                        bg_detect_shadows=config.bg_detect_shadows,
                        pause_on_camera_movement=config.pause_on_camera_movement,
                        camera_movement_threshold=config.camera_movement_threshold,
                        motion_confidence_threshold=config.motion_confidence_threshold,
                        # Temporal voting
                        enable_temporal_voting=config.enable_temporal_voting,
                        temporal_window_frames=config.temporal_window_frames,
                        temporal_threshold_frames=config.temporal_threshold_frames,
                        # Detection clustering
                        enable_detection_clustering=config.enable_detection_clustering,
                        clustering_distance=config.clustering_distance * color_scale_factor,  # Scale pixel distance
                        # Detection fusion
                        enable_detection_fusion=config.enable_detection_fusion,
                        fusion_mode=config.fusion_mode,
                        # False positive reduction
                        enable_aspect_ratio_filter=config.enable_aspect_ratio_filter,
                        min_aspect_ratio=config.min_aspect_ratio,
                        max_aspect_ratio=config.max_aspect_ratio,
                        # Rendering options
                        render_shape=config.render_shape,
                        render_text=config.render_text,
                        render_contours=config.render_contours,
                        render_at_processing_res=config.render_at_processing_res,
                        use_detection_color_for_rendering=config.use_detection_color_for_rendering,
                        max_detections_to_render=config.max_detections_to_render,
                        show_detections=config.show_detections
                    )
                else:
                    # No downsampling needed - store processing frame anyway
                    self._processing_frame = color_processing_frame
            else:
                # No processing resolution set - store processing frame anyway
                self._processing_frame = color_processing_frame

            # ═══════════════════════════════════════════════════════════════
            # DOWNSAMPLE MOTION FRAME (if separate resolution specified)
            # ═══════════════════════════════════════════════════════════════
            motion_scaled_config = color_scaled_config  # Default to same as color

            # If motion has a separate processing resolution, downsample independently
            if config.motion_processing_resolution is not None:
                motion_target_width, motion_target_height = config.motion_processing_resolution

                # Only downsample if motion target is smaller than original
                if original_width > motion_target_width or original_height > motion_target_height:
                    motion_scale_factor = min(
                        motion_target_width / original_width,
                        motion_target_height / original_height
                    )
                    motion_new_width = int(original_width * motion_scale_factor)
                    motion_new_height = int(original_height * motion_scale_factor)

                    motion_processing_frame = cv2.resize(frame, (motion_new_width, motion_new_height),
                                                         interpolation=cv2.INTER_LINEAR)

                    # Create scaled config for motion detection (separate from color)
                    motion_scaled_config = HSVConfig(
                        target_color_rgb=config.target_color_rgb,
                        hue_threshold=config.hue_threshold,
                        saturation_threshold=config.saturation_threshold,
                        value_threshold=config.value_threshold,
                        min_area=int(config.min_area * motion_scale_factor * motion_scale_factor),
                        max_area=int(config.max_area * motion_scale_factor * motion_scale_factor),
                        confidence_threshold=config.confidence_threshold,
                        morphology_enabled=config.morphology_enabled,
                        gpu_acceleration=config.gpu_acceleration,
                        show_labels=config.show_labels,
                        hsv_ranges=config.hsv_ranges,
                        hsv_ranges_list=config.hsv_ranges_list,
                        processing_resolution=None,  # Already at target resolution
                        motion_processing_resolution=None,  # Already at target resolution
                        target_capture_fps=config.target_capture_fps,
                        # Hue expansion
                        enable_hue_expansion=config.enable_hue_expansion,
                        hue_expansion_range=config.hue_expansion_range,
                        # Motion detection
                        enable_motion_detection=config.enable_motion_detection,
                        motion_algorithm=config.motion_algorithm,
                        min_detection_area=int(config.min_detection_area * motion_scale_factor * motion_scale_factor),
                        max_detection_area=int(config.max_detection_area * motion_scale_factor * motion_scale_factor),
                        max_motion_detections=config.max_motion_detections,
                        motion_threshold=config.motion_threshold,
                        blur_kernel_size=config.blur_kernel_size,
                        morphology_kernel_size=config.morphology_kernel_size,
                        persistence_frames=config.persistence_frames,
                        persistence_threshold=config.persistence_threshold,
                        bg_history=config.bg_history,
                        bg_var_threshold=config.bg_var_threshold,
                        bg_detect_shadows=config.bg_detect_shadows,
                        pause_on_camera_movement=config.pause_on_camera_movement,
                        camera_movement_threshold=config.camera_movement_threshold,
                        motion_confidence_threshold=config.motion_confidence_threshold,
                        # Temporal voting
                        enable_temporal_voting=config.enable_temporal_voting,
                        temporal_window_frames=config.temporal_window_frames,
                        temporal_threshold_frames=config.temporal_threshold_frames,
                        # Detection clustering
                        enable_detection_clustering=config.enable_detection_clustering,
                        clustering_distance=config.clustering_distance * motion_scale_factor,  # Scale pixel distance
                        # Detection fusion
                        enable_detection_fusion=config.enable_detection_fusion,
                        fusion_mode=config.fusion_mode,
                        # False positive reduction
                        enable_aspect_ratio_filter=config.enable_aspect_ratio_filter,
                        min_aspect_ratio=config.min_aspect_ratio,
                        max_aspect_ratio=config.max_aspect_ratio,
                        # Rendering options
                        render_shape=config.render_shape,
                        render_text=config.render_text,
                        render_contours=config.render_contours,
                        render_at_processing_res=config.render_at_processing_res,
                        use_detection_color_for_rendering=config.use_detection_color_for_rendering,
                        max_detections_to_render=config.max_detections_to_render,
                        show_detections=config.show_detections
                    )

            # ═══════════════════════════════════════════════════════════════
            # STEP 1: COLOR DETECTION
            # ═══════════════════════════════════════════════════════════════
            # Apply hue expansion if enabled
            if config.enable_hue_expansion and config.hue_expansion_range > 0:
                hsv_ranges = self._apply_hue_expansion(hsv_ranges, config.hue_expansion_range)

            color_detections = []
            if self._use_gpu:
                color_detections = self._detect_gpu(color_processing_frame, timestamp, color_scaled_config, hsv_ranges)
            else:
                color_detections = self._detect_cpu(color_processing_frame, timestamp, color_scaled_config, hsv_ranges)

            # Scale color detections back to original resolution (if downsampled)
            if color_scale_factor < 1.0:
                color_detections = self._scale_detections_to_original(color_detections, color_scale_factor)

            # ═══════════════════════════════════════════════════════════════
            # STEP 2: MOTION DETECTION (if enabled)
            # ═══════════════════════════════════════════════════════════════
            motion_detections = []
            if config.enable_motion_detection:
                # Check for camera movement first (if pause_on_camera_movement is enabled)
                should_pause = False
                if config.pause_on_camera_movement:
                    self._camera_is_moving = self._detect_camera_movement(motion_processing_frame, motion_scaled_config)
                    should_pause = self._camera_is_moving
                else:
                    self._camera_is_moving = False

                if not should_pause:
                    # Run motion detection based on selected algorithm
                    if config.motion_algorithm == MotionAlgorithm.FRAME_DIFF:
                        motion_detections = self._baseline_detect_motion(motion_processing_frame, timestamp, motion_scaled_config)
                    elif config.motion_algorithm == MotionAlgorithm.MOG2:
                        motion_detections = self._mog2_detect_motion(motion_processing_frame, timestamp, motion_scaled_config)
                    elif config.motion_algorithm == MotionAlgorithm.KNN:
                        motion_detections = self._knn_detect_motion(motion_processing_frame, timestamp, motion_scaled_config)
                else:
                    # Camera is moving - still need to update background models to prevent them from getting stale
                    # Apply the background subtractor but don't extract detections
                    if config.motion_algorithm == MotionAlgorithm.MOG2:
                        if self._mog2_subtractor is not None:
                            _ = self._mog2_subtractor.apply(motion_processing_frame, learningRate=-1)
                    elif config.motion_algorithm == MotionAlgorithm.KNN:
                        if self._knn_subtractor is not None:
                            _ = self._knn_subtractor.apply(motion_processing_frame, learningRate=-1)

                # Apply persistence filter to motion detections
                if motion_detections and config.persistence_threshold > 1:
                    motion_detections = self._apply_persistence_filter(motion_detections, motion_scaled_config)

                # Scale motion detections back to original resolution (if downsampled)
                if motion_scale_factor < 1.0:
                    motion_detections = self._scale_detections_to_original(motion_detections, motion_scale_factor)

            # ═══════════════════════════════════════════════════════════════
            # STEP 3: DETECTION FUSION (if enabled)
            # ═══════════════════════════════════════════════════════════════
            if config.enable_detection_fusion and config.enable_motion_detection:
                detections = self._fuse_detections(color_detections, motion_detections, config)
            else:
                # No fusion - use color detections (or both if fusion disabled but motion enabled)
                detections = color_detections
                if config.enable_motion_detection and not config.enable_detection_fusion:
                    detections.extend(motion_detections)

            # ═══════════════════════════════════════════════════════════════
            # STEP 4: TEMPORAL VOTING (if enabled)
            # ═══════════════════════════════════════════════════════════════
            if config.enable_temporal_voting:
                detections = self._apply_temporal_voting(detections, config)

            # ═══════════════════════════════════════════════════════════════
            # STEP 5: DETECTION CLUSTERING (if enabled)
            # ═══════════════════════════════════════════════════════════════
            if config.enable_detection_clustering:
                detections = self._apply_detection_clustering(detections, config)

            # ═══════════════════════════════════════════════════════════════
            # STEP 6: ASPECT RATIO FILTER (if enabled)
            # ═══════════════════════════════════════════════════════════════
            if config.enable_aspect_ratio_filter:
                detections = self._apply_aspect_ratio_filter(detections, config)

            # NOTE: Scaling is now done immediately after each detection type
            # (color and motion) instead of here, to support dual resolutions

        except Exception as e:
            self.logger.error(f"Detection error: {e}")
            self.logger.error(f"Detection traceback: {traceback.format_exc()}")
            detections = []

        # Performance tracking
        processing_time = time.perf_counter() - start_time
        self._update_performance_stats(processing_time, len(detections))

        return detections

    def _apply_hue_expansion(self, hsv_ranges: List, expansion: int) -> List:
        """
        Expand HSV ranges by adding ±expansion to hue values.

        This groups similar colors together (e.g., red+orange, blue+cyan).

        Args:
            hsv_ranges: List of (lower_bound, upper_bound) tuples
            expansion: Hue expansion in OpenCV units (0-30, ~0-60 degrees)

        Returns:
            Expanded HSV ranges
        """
        try:
            expanded_ranges = []
            for lower, upper in hsv_ranges:
                # Expand hue channel (index 0) only, keep S and V unchanged
                lower_expanded = lower.copy()
                upper_expanded = upper.copy()

                # Expand hue with wrapping (hue is circular 0-179)
                lower_hue = int(lower[0]) - expansion
                upper_hue = int(upper[0]) + expansion

                # Handle hue wrapping
                if lower_hue < 0:
                    # Hue wraps below 0 - create two ranges
                    expanded_ranges.append((
                        np.array([lower_hue + 180, lower[1], lower[2]], dtype=np.uint8),
                        np.array([179, upper[1], upper[2]], dtype=np.uint8)
                    ))
                    lower_hue = 0

                if upper_hue > 179:
                    # Hue wraps above 179 - create two ranges
                    expanded_ranges.append((
                        np.array([0, lower[1], lower[2]], dtype=np.uint8),
                        np.array([upper_hue - 180, upper[1], upper[2]], dtype=np.uint8)
                    ))
                    upper_hue = 179

                # Add the main expanded range
                lower_expanded[0] = np.clip(lower_hue, 0, 179)
                upper_expanded[0] = np.clip(upper_hue, 0, 179)
                expanded_ranges.append((lower_expanded, upper_expanded))

            return expanded_ranges

        except Exception as e:
            self.logger.error(f"Error in hue expansion: {e}")
            return hsv_ranges  # Return original on error

    def _scale_detections_to_original(self, detections: List[Detection], scale_factor: float) -> List[Detection]:
        """
        Scale detections from processing resolution back to original resolution.

        Args:
            detections: List of detections at processing resolution
            scale_factor: The scale factor used for downsampling (e.g., 0.375 for 1920->720)

        Returns:
            List of detections scaled to original resolution
        """
        if scale_factor >= 1.0:
            return detections  # No scaling needed

        inv_scale = 1.0 / scale_factor
        scaled_detections = []

        for detection in detections:
            # Scale bounding box
            x, y, w, h = detection.bbox
            scaled_bbox = (
                int(x * inv_scale),
                int(y * inv_scale),
                int(w * inv_scale),
                int(h * inv_scale)
            )

            # Scale centroid
            cx, cy = detection.centroid
            scaled_centroid = (
                int(cx * inv_scale),
                int(cy * inv_scale)
            )

            # Scale area
            scaled_area = detection.area * inv_scale * inv_scale

            # Scale contour points
            scaled_contour = (detection.contour * inv_scale).astype(np.int32)

            scaled_detection = Detection(
                bbox=scaled_bbox,
                centroid=scaled_centroid,
                area=scaled_area,
                confidence=detection.confidence,
                timestamp=detection.timestamp,
                contour=scaled_contour,
                detection_type=detection.detection_type,
                color=detection.color,
                color_id=detection.color_id,
                mean_color=detection.mean_color,
                metadata=detection.metadata
            )
            scaled_detections.append(scaled_detection)

        return scaled_detections

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
                return self._process_contours(contours, timestamp, config, frame, hsv_ranges)
            except Exception as e:
                self.logger.error(f"Error finding contours: {e}")
                return []

        except Exception as e:
            self.logger.error(f"Error in CPU detection: {e}")
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

            return self._process_contours(contours, timestamp, config, frame, hsv_ranges)

        except Exception as e:
            self.logger.warning(f"GPU detection failed, falling back to CPU: {e}")
            return self._detect_cpu(frame, timestamp, config, hsv_ranges)

    def _process_contours(self, contours: List, timestamp: float, config: HSVConfig,
                          frame: np.ndarray = None, hsv_ranges: List = None) -> List[Detection]:
        """Process contours into Detection objects."""
        detections = []

        # Build color range mapping if we have multiple colors
        color_range_map = {}  # Maps range index to color_id
        if config.hsv_ranges_list and hsv_ranges:
            # Map each HSV range to its color_id
            range_idx = 0
            for color_id, hsv_data in enumerate(config.hsv_ranges_list):
                # Each color can have 1 or 2 ranges (if hue wraps)
                h = hsv_data['h']
                h_center = int(h * 179)
                h_minus, h_plus = hsv_data['h_minus'], hsv_data['h_plus']
                h_low = max(0, h_center - int(h_minus * 179))
                h_high = min(179, h_center + int(h_plus * 179))

                if h_low > h_high:
                    # Hue wraps - two ranges for this color
                    color_range_map[range_idx] = color_id
                    range_idx += 1
                    color_range_map[range_idx] = color_id
                    range_idx += 1
                else:
                    # Single range
                    color_range_map[range_idx] = color_id
                    range_idx += 1

        for contour in contours:
            # Calculate area
            area = cv2.contourArea(contour)

            # Filter by area constraints
            if area < config.min_area or area > config.max_area:
                continue

            # Calculate bounding box and centroid
            x, y, w, h = cv2.boundingRect(contour)
            centroid = (int(x + w / 2), int(y + h / 2))

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

            # Calculate mean color and determine color_id
            mean_color = None
            color_id = None

            if frame is not None:
                # Create mask for this contour
                contour_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
                cv2.drawContours(contour_mask, [contour], -1, 255, -1)

                # Calculate mean BGR color in the contour region
                mean_bgr = cv2.mean(frame, mask=contour_mask)[:3]
                mean_color = (int(mean_bgr[0]), int(mean_bgr[1]), int(mean_bgr[2]))

                # Determine which color range this detection matches
                if hsv_ranges and color_range_map:
                    # Convert mean color to HSV
                    mean_bgr_array = np.uint8([[mean_color]])
                    mean_hsv = cv2.cvtColor(mean_bgr_array, cv2.COLOR_BGR2HSV)[0][0]

                    # Find which range matches
                    for range_idx, (lower_bound, upper_bound) in enumerate(hsv_ranges):
                        if (lower_bound[0] <= mean_hsv[0] <= upper_bound[0] and
                            lower_bound[1] <= mean_hsv[1] <= upper_bound[1] and
                                lower_bound[2] <= mean_hsv[2] <= upper_bound[2]):
                            color_id = color_range_map.get(range_idx, 0)
                            break

                    # If no exact match, find closest color by center distance
                    if color_id is None and config.hsv_ranges_list:
                        min_dist = float('inf')
                        best_color_id = 0
                        for cid, hsv_data in enumerate(config.hsv_ranges_list):
                            h_center = int(hsv_data['h'] * 179)
                            s_center = int(hsv_data['s'] * 255)
                            v_center = int(hsv_data['v'] * 255)

                            # Calculate distance in HSV space
                            h_dist = min(abs(mean_hsv[0] - h_center), 179 - abs(mean_hsv[0] - h_center))
                            s_dist = abs(mean_hsv[1] - s_center)
                            v_dist = abs(mean_hsv[2] - v_center)
                            dist = h_dist + s_dist + v_dist

                            if dist < min_dist:
                                min_dist = dist
                                best_color_id = cid
                        color_id = best_color_id

            detection = Detection(
                bbox=(x, y, w, h),
                centroid=centroid,
                area=area,
                confidence=confidence,
                timestamp=timestamp,
                contour=contour,
                color_id=color_id,
                mean_color=mean_color
            )

            detections.append(detection)

        # Sort by confidence (highest first)
        detections.sort(key=lambda d: d.confidence, reverse=True)

        return detections

    # ═══════════════════════════════════════════════════════════════════════════
    # MOTION DETECTION METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    def _baseline_detect_motion(self, frame: np.ndarray, timestamp: float, config: HSVConfig) -> List[Detection]:
        """
        Baseline motion detection using frame differencing.

        Args:
            frame: Current frame (BGR)
            timestamp: Frame timestamp
            config: Detection configuration

        Returns:
            List of motion detections
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Apply Gaussian blur to reduce noise
            blur_size = config.blur_kernel_size if config.blur_kernel_size % 2 == 1 else config.blur_kernel_size + 1
            blurred = cv2.GaussianBlur(gray, (blur_size, blur_size), 0)

            # Initialize previous frame if needed
            if self._prev_frame is None:
                self._prev_frame = blurred
                return []

            # Compute frame difference
            frame_diff = cv2.absdiff(self._prev_frame, blurred)

            # Threshold
            _, thresh = cv2.threshold(frame_diff, config.motion_threshold, 255, cv2.THRESH_BINARY)

            # Morphological operations to reduce noise
            morph_size = config.morphology_kernel_size
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morph_size, morph_size))
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Early exit if too many contours (performance optimization)
            if config.max_motion_detections > 0 and len(contours) > config.max_motion_detections * 3:
                self.logger.debug(f"Too many contours ({len(contours)}) - limiting to first {config.max_motion_detections * 3} for performance")
                contours = contours[:config.max_motion_detections * 3]

            # Process contours into detections
            detections = []
            for contour in contours:
                # Early exit if we've hit detection limit
                if config.max_motion_detections > 0 and len(detections) >= config.max_motion_detections:
                    break

                area = cv2.contourArea(contour)

                # Filter by area
                if area < config.min_detection_area or area > config.max_detection_area:
                    continue

                # Calculate bounding box and centroid
                x, y, w, h = cv2.boundingRect(contour)
                centroid = (int(x + w / 2), int(y + h / 2))

                # Confidence based on area
                confidence = min(area / config.max_detection_area, 1.0)

                # Filter by motion confidence threshold
                if confidence < config.motion_confidence_threshold:
                    continue

                detection = Detection(
                    bbox=(x, y, w, h),
                    centroid=centroid,
                    area=area,
                    confidence=confidence,
                    timestamp=timestamp,
                    contour=contour,
                    detection_type="motion",
                    color=(0, 255, 0)  # Green for motion
                )
                detections.append(detection)

            # Update previous frame
            self._prev_frame = blurred

            return detections

        except Exception as e:
            self.logger.error(f"Error in baseline motion detection: {e}")
            return []

    def _mog2_detect_motion(self, frame: np.ndarray, timestamp: float, config: HSVConfig) -> List[Detection]:
        """
        Motion detection using MOG2 background subtraction.

        Args:
            frame: Current frame (BGR)
            timestamp: Frame timestamp
            config: Detection configuration

        Returns:
            List of motion detections
        """
        try:
            # Initialize MOG2 subtractor if needed
            if self._mog2_subtractor is None:
                self._mog2_subtractor = cv2.createBackgroundSubtractorMOG2(
                    history=config.bg_history,
                    varThreshold=config.bg_var_threshold,
                    detectShadows=config.bg_detect_shadows
                )

            # Apply background subtraction
            fg_mask = self._mog2_subtractor.apply(frame)

            # Remove shadows if detected (shadow pixels are 127)
            if config.bg_detect_shadows:
                _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

            # Morphological operations
            morph_size = config.morphology_kernel_size
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morph_size, morph_size))
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

            # Find contours
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Early exit if too many contours (performance optimization)
            if config.max_motion_detections > 0 and len(contours) > config.max_motion_detections * 3:
                self.logger.debug(f"Too many contours ({len(contours)}) - limiting to first {config.max_motion_detections * 3} for performance")
                contours = contours[:config.max_motion_detections * 3]

            # Process contours
            detections = []
            for contour in contours:
                # Early exit if we've hit detection limit
                if config.max_motion_detections > 0 and len(detections) >= config.max_motion_detections:
                    break

                area = cv2.contourArea(contour)

                if area < config.min_detection_area or area > config.max_detection_area:
                    continue

                x, y, w, h = cv2.boundingRect(contour)
                centroid = (int(x + w / 2), int(y + h / 2))
                confidence = min(area / config.max_detection_area, 1.0)

                # Filter by motion confidence threshold
                if confidence < config.motion_confidence_threshold:
                    continue

                detection = Detection(
                    bbox=(x, y, w, h),
                    centroid=centroid,
                    area=area,
                    confidence=confidence,
                    timestamp=timestamp,
                    contour=contour,
                    detection_type="motion",
                    color=(0, 255, 0)  # Green for motion
                )
                detections.append(detection)

            return detections

        except Exception as e:
            self.logger.error(f"Error in MOG2 motion detection: {e}")
            return []

    def _knn_detect_motion(self, frame: np.ndarray, timestamp: float, config: HSVConfig) -> List[Detection]:
        """
        Motion detection using KNN background subtraction.

        Args:
            frame: Current frame (BGR)
            timestamp: Frame timestamp
            config: Detection configuration

        Returns:
            List of motion detections
        """
        try:
            # Initialize KNN subtractor if needed
            if self._knn_subtractor is None:
                self._knn_subtractor = cv2.createBackgroundSubtractorKNN(
                    history=config.bg_history,
                    dist2Threshold=400.0,
                    detectShadows=config.bg_detect_shadows
                )

            # Apply background subtraction
            fg_mask = self._knn_subtractor.apply(frame)

            # Remove shadows if detected
            if config.bg_detect_shadows:
                _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

            # Morphological operations
            morph_size = config.morphology_kernel_size
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morph_size, morph_size))
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

            # Find contours
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Early exit if too many contours (performance optimization)
            if config.max_motion_detections > 0 and len(contours) > config.max_motion_detections * 3:
                self.logger.debug(f"Too many contours ({len(contours)}) - limiting to first {config.max_motion_detections * 3} for performance")
                contours = contours[:config.max_motion_detections * 3]

            # Process contours
            detections = []
            for contour in contours:
                # Early exit if we've hit detection limit
                if config.max_motion_detections > 0 and len(detections) >= config.max_motion_detections:
                    break

                area = cv2.contourArea(contour)

                if area < config.min_detection_area or area > config.max_detection_area:
                    continue

                x, y, w, h = cv2.boundingRect(contour)
                centroid = (int(x + w / 2), int(y + h / 2))
                confidence = min(area / config.max_detection_area, 1.0)

                # Filter by motion confidence threshold
                if confidence < config.motion_confidence_threshold:
                    continue

                detection = Detection(
                    bbox=(x, y, w, h),
                    centroid=centroid,
                    area=area,
                    confidence=confidence,
                    timestamp=timestamp,
                    contour=contour,
                    detection_type="motion",
                    color=(0, 255, 0)  # Green for motion
                )
                detections.append(detection)

            return detections

        except Exception as e:
            self.logger.error(f"Error in KNN motion detection: {e}")
            return []

    def _detect_camera_movement(self, frame: np.ndarray, config: HSVConfig) -> bool:
        """
        Detect if the camera is moving significantly (panning, tilting, rotating).

        Uses two complementary metrics:
        1. Mean Absolute Difference (MAD) - Average pixel change across entire frame
        2. Pixel Change Ratio - Percentage of pixels that changed significantly

        Camera panning causes low pixel change ratio but high MAD, so we check both.

        Args:
            frame: Current frame (BGR)
            config: Detection configuration

        Returns:
            True if camera is moving, False otherwise
        """
        try:
            # Convert to grayscale with minimal blur (preserve details for panning detection)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)  # Reduced from (21,21) for better sensitivity

            if self._prev_frame is None:
                self._prev_frame = blurred
                return False

            # Check if frame size has changed (e.g., resolution change)
            if self._prev_frame.shape != blurred.shape:
                self.logger.debug(f"Frame size changed from {self._prev_frame.shape} to {blurred.shape}, resetting camera movement detection")
                self._prev_frame = blurred
                return False

            # Compute frame difference
            frame_diff = cv2.absdiff(self._prev_frame, blurred)

            # METRIC 1: Mean Absolute Difference (good for detecting camera pan/tilt)
            # When camera pans, most pixels change slightly, causing high MAD
            mad = np.mean(frame_diff)
            mad_normalized = mad / 255.0  # Normalize to 0-1 range

            # METRIC 2: Pixel Change Ratio (good for detecting large object motion)
            # When objects move locally, significant pixel changes in specific areas
            _, thresh = cv2.threshold(frame_diff, 15, 255, cv2.THRESH_BINARY)  # Lower threshold from 25 to 15
            changed_pixels = np.count_nonzero(thresh)
            total_pixels = thresh.shape[0] * thresh.shape[1]
            change_ratio = changed_pixels / total_pixels

            # Update previous frame
            self._prev_frame = blurred

            # Camera is moving if EITHER metric exceeds threshold
            # MAD threshold is typically much lower (e.g., 10% MAD = significant camera motion)
            # We use config.camera_movement_threshold for both, but MAD is inherently more sensitive
            mad_threshold = config.camera_movement_threshold * 0.5  # MAD threshold is 50% of user setting
            is_moving_mad = mad_normalized >= mad_threshold
            is_moving_ratio = change_ratio >= config.camera_movement_threshold

            is_moving = is_moving_mad or is_moving_ratio

            # Log camera movement detection for debugging
            if is_moving:
                self.logger.debug(
                    f"Camera movement detected: "
                    f"MAD={mad_normalized * 100:.1f}% (threshold: {mad_threshold * 100:.1f}%), "
                    f"Pixel change={change_ratio * 100:.1f}% (threshold: {config.camera_movement_threshold * 100:.1f}%)"
                )

            return is_moving

        except Exception as e:
            self.logger.error(f"Error detecting camera movement: {e}")
            return False

    # ═══════════════════════════════════════════════════════════════════════════
    # DETECTION POST-PROCESSING METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    def _apply_persistence_filter(self, motion_detections: List[Detection], config: HSVConfig) -> List[Detection]:
        """
        Apply persistence filtering to motion detections.

        Motion must appear in N out of M consecutive frames to be confirmed.
        This reduces flickering false positives in motion detection.

        Args:
            motion_detections: Current frame motion detections
            config: Detection configuration

        Returns:
            Filtered motion detections that meet persistence threshold
        """
        try:
            # Skip if persistence filtering is disabled (threshold = 1 means "appear in 1 frame")
            if config.persistence_threshold <= 1:
                return motion_detections

            # Add current detections to history
            self._motion_detection_history.append(motion_detections)

            # Ensure we have enough history
            if len(self._motion_detection_history) < config.persistence_frames:
                # Not enough history yet - return all detections
                return motion_detections

            # Get the relevant window of frames
            window = list(self._motion_detection_history)[-config.persistence_frames:]

            # Count votes for each current detection
            persistent_detections = []
            for detection in motion_detections:
                votes = 1  # Current frame counts as 1 vote

                # Check overlap with historical detections in the window
                for historical_detections in window[:-1]:  # Exclude current frame
                    for hist_det in historical_detections:
                        iou = self._calculate_iou(detection, hist_det)
                        if iou > 0.3:  # 30% IoU threshold for "same detection"
                            votes += 1
                            break  # Only count once per historical frame

                # Keep detection if it has enough votes (appeared in N of M frames)
                if votes >= config.persistence_threshold:
                    detection.metadata['persistence_votes'] = votes
                    persistent_detections.append(detection)

            return persistent_detections

        except Exception as e:
            self.logger.error(f"Error in persistence filter: {e}")
            return motion_detections

    def _apply_temporal_voting(self, detections: List[Detection], config: HSVConfig) -> List[Detection]:
        """
        Apply temporal voting to filter out transient detections.

        Args:
            detections: Current frame detections
            config: Detection configuration

        Returns:
            Filtered detections that appear in N+ frames
        """
        try:
            # Add current detections to history
            self._detection_history.append(detections)

            # Ensure we have enough history
            if len(self._detection_history) < config.temporal_threshold_frames:
                return detections  # Not enough history yet

            # Count votes for each current detection
            voted_detections = []
            for detection in detections:
                votes = 1  # Current frame counts as 1 vote

                # Check overlap with historical detections
                for historical_detections in list(self._detection_history)[:-1]:  # Exclude current
                    for hist_det in historical_detections:
                        iou = self._calculate_iou(detection, hist_det)
                        if iou > 0.3:  # 30% IoU threshold
                            votes += 1
                            break  # Only count once per historical frame

                # Keep detection if it has enough votes
                if votes >= config.temporal_threshold_frames:
                    detection.metadata['temporal_votes'] = votes
                    voted_detections.append(detection)

            return voted_detections

        except Exception as e:
            self.logger.error(f"Error in temporal voting: {e}")
            return detections

    def _apply_detection_clustering(self, detections: List[Detection], config: HSVConfig) -> List[Detection]:
        """
        Cluster nearby detections into single detections.

        Args:
            detections: List of detections
            config: Detection configuration

        Returns:
            Clustered detections
        """
        try:
            if not detections:
                return detections

            # Group detections by proximity
            clustered = []
            used = set()

            for i, det1 in enumerate(detections):
                if i in used:
                    continue

                # Start a new cluster
                cluster = [det1]
                used.add(i)

                # Find nearby detections
                for j, det2 in enumerate(detections):
                    if j in used:
                        continue

                    # Calculate centroid distance
                    dist = np.sqrt(
                        (det1.centroid[0] - det2.centroid[0])**2 +
                        (det1.centroid[1] - det2.centroid[1])**2
                    )

                    if dist <= config.clustering_distance:
                        cluster.append(det2)
                        used.add(j)

                # Merge cluster into single detection
                if len(cluster) == 1:
                    clustered.append(det1)
                else:
                    # Calculate merged bounding box
                    all_x = [d.bbox[0] for d in cluster]
                    all_y = [d.bbox[1] for d in cluster]
                    all_x2 = [d.bbox[0] + d.bbox[2] for d in cluster]
                    all_y2 = [d.bbox[1] + d.bbox[3] for d in cluster]

                    x = min(all_x)
                    y = min(all_y)
                    x2 = max(all_x2)
                    y2 = max(all_y2)
                    w = x2 - x
                    h = y2 - y

                    # Merged properties
                    centroid = (int(x + w / 2), int(y + h / 2))
                    area = sum(d.area for d in cluster)
                    confidence = max(d.confidence for d in cluster)

                    merged = Detection(
                        bbox=(x, y, w, h),
                        centroid=centroid,
                        area=area,
                        confidence=confidence,
                        timestamp=cluster[0].timestamp,
                        contour=cluster[0].contour,  # Use first contour
                        detection_type=cluster[0].detection_type,
                        color=cluster[0].color,
                        color_id=cluster[0].color_id,
                        mean_color=cluster[0].mean_color
                    )
                    merged.metadata['cluster_size'] = len(cluster)
                    clustered.append(merged)

            return clustered

        except Exception as e:
            self.logger.error(f"Error in detection clustering: {e}")
            return detections

    def _apply_aspect_ratio_filter(self, detections: List[Detection], config: HSVConfig) -> List[Detection]:
        """
        Filter detections by aspect ratio (width/height).

        Useful for removing false positives with unusual shapes (e.g., very thin vertical/horizontal streaks).

        Args:
            detections: Input detections
            config: Detection configuration

        Returns:
            Filtered detections within aspect ratio range
        """
        try:
            filtered = []
            for detection in detections:
                x, y, w, h = detection.bbox

                # Calculate aspect ratio (width / height)
                aspect_ratio = w / h if h > 0 else 0

                # Filter by aspect ratio range
                if config.min_aspect_ratio <= aspect_ratio <= config.max_aspect_ratio:
                    filtered.append(detection)

            if len(detections) != len(filtered):
                self.logger.debug(f"Aspect ratio filter: {len(detections)} -> {len(filtered)} detections")

            return filtered

        except Exception as e:
            self.logger.error(f"Error in aspect ratio filter: {e}")
            return detections

    def _fuse_detections(self, color_detections: List[Detection], motion_detections: List[Detection],
                         config: HSVConfig) -> List[Detection]:
        """
        Fuse color and motion detections based on fusion mode.

        Args:
            color_detections: Color-based detections
            motion_detections: Motion-based detections
            config: Detection configuration

        Returns:
            Fused detections
        """
        try:
            if config.fusion_mode == FusionMode.UNION:
                # Return all detections, merging overlapping ones
                fused = list(color_detections)

                for motion_det in motion_detections:
                    overlaps = False
                    for i, color_det in enumerate(fused):
                        iou = self._calculate_iou(motion_det, color_det)
                        if iou > 0.3:  # 30% IoU threshold
                            # Merge into single detection
                            merged = self._merge_detections(color_det, motion_det)
                            fused[i] = merged
                            overlaps = True
                            break

                    if not overlaps:
                        fused.append(motion_det)

                return fused

            elif config.fusion_mode == FusionMode.INTERSECTION:
                # Only keep detections in BOTH color and motion
                fused = []

                for color_det in color_detections:
                    for motion_det in motion_detections:
                        iou = self._calculate_iou(color_det, motion_det)
                        if iou > 0.3:
                            # Merge with boosted confidence
                            merged = self._merge_detections(color_det, motion_det)
                            merged.confidence = min(merged.confidence * 1.2, 1.0)
                            fused.append(merged)
                            break

                return fused

            elif config.fusion_mode == FusionMode.COLOR_PRIORITY:
                # Start with color, add non-overlapping motion
                fused = list(color_detections)

                for motion_det in motion_detections:
                    overlaps = False
                    for color_det in fused:
                        iou = self._calculate_iou(motion_det, color_det)
                        if iou > 0.3:
                            overlaps = True
                            break

                    if not overlaps:
                        fused.append(motion_det)

                return fused

            elif config.fusion_mode == FusionMode.MOTION_PRIORITY:
                # Start with motion, add non-overlapping color
                fused = list(motion_detections)

                for color_det in color_detections:
                    overlaps = False
                    for motion_det in fused:
                        iou = self._calculate_iou(color_det, motion_det)
                        if iou > 0.3:
                            overlaps = True
                            break

                    if not overlaps:
                        fused.append(color_det)

                return fused

            else:
                return color_detections

        except Exception as e:
            self.logger.error(f"Error in detection fusion: {e}")
            return color_detections

    def _calculate_iou(self, det1: Detection, det2: Detection) -> float:
        """
        Calculate Intersection over Union between two detections.

        Args:
            det1: First detection
            det2: Second detection

        Returns:
            IoU value (0-1)
        """
        try:
            x1, y1, w1, h1 = det1.bbox
            x2, y2, w2, h2 = det2.bbox

            # Calculate intersection
            x_left = max(x1, x2)
            y_top = max(y1, y2)
            x_right = min(x1 + w1, x2 + w2)
            y_bottom = min(y1 + h1, y2 + h2)

            if x_right < x_left or y_bottom < y_top:
                return 0.0

            intersection = (x_right - x_left) * (y_bottom - y_top)
            area1 = w1 * h1
            area2 = w2 * h2
            union = area1 + area2 - intersection

            return intersection / union if union > 0 else 0.0

        except Exception:
            return 0.0

    def _merge_detections(self, det1: Detection, det2: Detection) -> Detection:
        """
        Merge two overlapping detections into one.

        Args:
            det1: First detection
            det2: Second detection

        Returns:
            Merged detection
        """
        try:
            x1, y1, w1, h1 = det1.bbox
            x2, y2, w2, h2 = det2.bbox

            # Calculate merged bounding box
            x = min(x1, x2)
            y = min(y1, y2)
            x2_max = max(x1 + w1, x2 + w2)
            y2_max = max(y1 + h1, y2 + h2)
            w = x2_max - x
            h = y2_max - y

            # Merged properties
            centroid = (int(x + w / 2), int(y + h / 2))
            area = det1.area + det2.area
            confidence = (det1.confidence + det2.confidence) / 2

            merged = Detection(
                bbox=(x, y, w, h),
                centroid=centroid,
                area=area,
                confidence=confidence,
                timestamp=det1.timestamp,
                contour=det1.contour,  # Use first contour
                detection_type="fused",
                color=(255, 128, 0),  # Cyan for fused
                color_id=det1.color_id if det1.color_id is not None else det2.color_id,
                mean_color=det1.mean_color if det1.mean_color is not None else det2.mean_color
            )

            return merged

        except Exception as e:
            self.logger.error(f"Error merging detections: {e}")
            return det1

    def create_annotated_frame(self, frame: np.ndarray, detections: List[Detection]) -> np.ndarray:
        """
        Create annotated frame with detection overlays using enhanced rendering options.

        Args:
            frame: Original frame (high resolution)
            detections: List of detections to draw

        Returns:
            Annotated frame with detection visualizations
        """
        # Early return if detections are disabled
        if not self._config.show_detections:
            return frame.copy()

        # Determine which frame to render on and if we need to scale detections
        if self._config.render_at_processing_res and self._processing_frame is not None:
            # Render at processing resolution (lower res, faster)
            render_base = self._processing_frame.copy()
            # Detections are at original resolution, need to scale down to processing resolution
            render_scale = self._current_scale_factor  # Scale factor to convert original -> processing
            needs_upscale = True
        else:
            # Render at original resolution (higher res, slower)
            render_base = frame.copy()
            render_scale = 1.0  # No scaling needed
            needs_upscale = False

        annotated = render_base

        # Apply detection limit if specified
        render_detections = detections
        if self._config.max_detections_to_render > 0 and len(detections) > self._config.max_detections_to_render:
            # Sort by confidence * area and keep top N
            sorted_detections = sorted(detections, key=lambda d: d.confidence * d.area, reverse=True)
            render_detections = sorted_detections[:self._config.max_detections_to_render]

        # Render each detection
        for i, detection in enumerate(render_detections):
            x, y, w, h = detection.bbox
            centroid_x, centroid_y = detection.centroid

            # Scale coordinates if rendering at processing resolution
            if render_scale != 1.0:
                x = int(x * render_scale)
                y = int(y * render_scale)
                w = int(w * render_scale)
                h = int(h * render_scale)
                centroid_x = int(centroid_x * render_scale)
                centroid_y = int(centroid_y * render_scale)

            # Determine color for this detection
            if self._config.use_detection_color_for_rendering and detection.color is not None:
                color = detection.color
            else:
                # Color by detection type
                if detection.detection_type == "fused":
                    # Cyan for fused detections
                    color = (255, 128, 0)
                elif detection.detection_type == "motion":
                    # Green for motion
                    color = (0, 255, 0)
                else:
                    # Color by confidence for color detections
                    if detection.confidence > 0.8:
                        color = (0, 255, 0)  # Green - high confidence
                    elif detection.confidence > 0.5:
                        color = (0, 255, 255)  # Yellow - medium confidence
                    else:
                        color = (0, 0, 255)  # Red - low confidence

            # Render shape based on render_shape setting
            if self._config.render_shape == 0:
                # Box with centroid marker
                cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
                cv2.circle(annotated, (centroid_x, centroid_y), 3, color, -1)

            elif self._config.render_shape == 1:
                # Circle exceeding contour by 50%
                radius = int(max(w, h) * 0.75)
                cv2.circle(annotated, (centroid_x, centroid_y), radius, color, 2)

            elif self._config.render_shape == 2:
                # Dot at centroid
                cv2.circle(annotated, (centroid_x, centroid_y), 8, color, -1)

            elif self._config.render_shape == 3:
                # Off - no shape rendering
                pass

            # Render contours if enabled
            if self._config.render_contours and self._config.render_shape != 3:
                try:
                    # Scale contour if rendering at processing resolution
                    if render_scale != 1.0 and detection.contour is not None:
                        scaled_contour = (detection.contour * render_scale).astype(np.int32)
                        cv2.drawContours(annotated, [scaled_contour], -1, color, 1)
                    else:
                        cv2.drawContours(annotated, [detection.contour], -1, color, 1)
                except Exception:
                    pass  # Silently skip if contour drawing fails

            # Render text labels if enabled
            if self._config.render_text and self._config.render_shape != 3:
                label = f"#{i + 1}"
                if detection.detection_type != "color":
                    label += f" [{detection.detection_type}]"
                label += f" {detection.confidence:.2f}"
                if 'persistence_votes' in detection.metadata:
                    label += f" P{detection.metadata['persistence_votes']}"
                if 'temporal_votes' in detection.metadata:
                    label += f" V{detection.metadata['temporal_votes']}"
                if 'cluster_size' in detection.metadata:
                    label += f" C{detection.metadata['cluster_size']}"

                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]

                # Background for text
                cv2.rectangle(annotated, (x, y - label_size[1] - 8),
                              (x + label_size[0] + 4, y), color, -1)

                # Text
                cv2.putText(annotated, label, (x + 2, y - 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        # Add detection count and config info
        info_text = f"Detections: {len(detections)}"
        if len(detections) != len(render_detections):
            info_text += f" (showing {len(render_detections)})"

        if self._config.hsv_ranges:
            h_minus = int(self._config.hsv_ranges['h_minus'] * 179)
            h_plus = int(self._config.hsv_ranges['h_plus'] * 179)
            info_text += f" | H-{h_minus}/+{h_plus}"
        else:
            info_text += f" | H±{self._config.hue_threshold}"

        if self._config.processing_resolution:
            info_text += f" | {self._config.processing_resolution[0]}x{self._config.processing_resolution[1]}"

        cv2.putText(annotated, info_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

        # Upscale back to original resolution if we rendered at processing resolution
        if needs_upscale and self._original_frame is not None:
            original_height, original_width = self._original_frame.shape[:2]
            annotated = cv2.resize(annotated, (original_width, original_height),
                                   interpolation=cv2.INTER_LINEAR)

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


# Alias for backward compatibility with existing code
RealtimeColorDetector = ColorDetectionService
