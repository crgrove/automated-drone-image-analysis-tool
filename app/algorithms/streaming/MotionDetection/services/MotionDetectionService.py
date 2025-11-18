"""
MotionDetectionService.py - Advanced motion detection for static and moving cameras

Provides dual-mode motion detection optimized for drone surveillance with camera
motion compensation for in-flight detection scenarios.

This service is part of the MotionDetection algorithm module.
"""

# Set environment variable to avoid numpy compatibility issues
from core.services.LoggerService import LoggerService
from PySide6.QtCore import QObject, Signal
import collections
from threading import Lock
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
import time
import numpy as np
import cv2
import os
os.environ.setdefault('NUMPY_EXPERIMENTAL_DTYPE_API', '0')
os.environ.setdefault('NUMBA_DISABLE_INTEL_SVML', '1')
os.environ.setdefault('NPY_DISABLE_SVML', '1')


class DetectionMode(Enum):
    """Camera/detection mode selection."""
    STATIC = "static"  # Camera is stationary
    MOVING = "moving"  # Camera is moving (drone in flight)
    AUTO = "auto"      # Auto-detect based on motion patterns


class MotionAlgorithm(Enum):
    """Motion detection algorithms."""
    FRAME_DIFF = "frame_diff"          # Simple frame differencing
    MOG2 = "mog2"                      # Gaussian mixture background subtraction
    KNN = "knn"                        # K-nearest neighbors background subtraction
    OPTICAL_FLOW = "optical_flow"      # Dense optical flow
    FEATURE_MATCH = "feature_match"    # Feature-based motion estimation


@dataclass
class MotionDetection:
    """Container for motion detection result."""
    bbox: Tuple[int, int, int, int]    # x, y, width, height
    centroid: Tuple[int, int]          # center point
    area: float                        # pixel area
    velocity: Tuple[float, float]      # motion velocity (px/frame)
    confidence: float                   # detection confidence 0-1
    timestamp: float                    # detection time
    is_compensated: bool               # True if camera motion was compensated
    contour: np.ndarray = field(repr=False)  # original contour data


@dataclass
class CameraMotion:
    """Camera motion estimation result."""
    global_velocity: Tuple[float, float]  # Average camera motion vector
    rotation_angle: float                  # Camera rotation (degrees)
    confidence: float                      # Estimation confidence
    homography: Optional[np.ndarray]      # Transformation matrix


@dataclass
class MotionConfig:
    """Motion detection configuration."""
    mode: DetectionMode = DetectionMode.AUTO
    algorithm: MotionAlgorithm = MotionAlgorithm.MOG2
    sensitivity: float = 0.5               # 0-1, higher = more sensitive
    min_area: int = 500                   # Minimum detection area in pixels
    max_area: int = 100000                # Maximum detection area
    blur_size: int = 5                    # Gaussian blur kernel size
    morphology_size: int = 3               # Morphology kernel size
    motion_threshold: float = 25.0        # Pixel difference threshold
    compensation_strength: float = 0.8     # Camera motion compensation (0-1)
    auto_mode_threshold: float = 10.0     # Threshold for auto mode switching
    show_vectors: bool = True              # Show motion vectors
    show_camera_motion: bool = True       # Show camera motion overlay
    history_frames: int = 5                # Frames to keep for motion analysis
    processing_resolution: Optional[Tuple[int, int]] = None  # (width, height) to downsample to


class MotionDetectionService(QObject):
    """
    Advanced motion detector with camera motion compensation for drones.

    Features:
    - Dual-mode detection for static and moving cameras
    - Camera motion compensation using optical flow and feature matching
    - Multiple detection algorithms
    - Auto-detection of camera motion state
    - Real-time performance optimization
    """

    # Qt signals for integration
    detectionsReady = Signal(list, object, np.ndarray)  # detections, camera_motion, annotated_frame
    performanceUpdate = Signal(dict)  # processing_time, fps, detections_count
    configurationChanged = Signal(dict)  # current config state
    modeChanged = Signal(str)  # new detection mode

    def __init__(self):
        super().__init__()
        self.logger = LoggerService()

        # Check for GPU support
        self._use_gpu = self._check_gpu_support()
        self._gpu_mats = {}  # Cache for GPU matrices

        # Configuration
        self._config = MotionConfig()
        self._config_lock = Lock()

        # Detection state
        self._prev_frame = None
        self._prev_gray = None
        self._frame_history = collections.deque(maxlen=self._config.history_frames)

        # Background subtractors
        self._bg_subtractor_mog2 = None
        self._bg_subtractor_knn = None
        self._init_background_subtractors()

        # Feature detector for camera motion estimation (reduced features for speed)
        self._feature_detector = cv2.ORB_create(nfeatures=100)  # Reduced from 500
        self._matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)  # Faster without crossCheck

        # Camera motion estimation
        self._camera_motion_history = collections.deque(maxlen=10)
        self._current_mode = DetectionMode.STATIC
        self._mode_confidence = 0.0

        # Performance optimization
        self._frame_skip_counter = 0
        self._motion_check_interval = 10  # Check camera motion every N frames
        self._processing_times = collections.deque(maxlen=30)
        self._frame_count = 0
        self._last_fps_time = time.time()

        gpu_status = "GPU-accelerated" if self._use_gpu else "CPU-only"
        self.logger.info(f"Motion detector initialized with dual-mode support ({gpu_status})")

    def _check_gpu_support(self) -> bool:
        """Check if GPU acceleration is available for OpenCV."""
        try:
            if hasattr(cv2, 'cuda'):
                device_count = cv2.cuda.getCudaEnabledDeviceCount()
                if device_count > 0:
                    # Test if we can actually use GPU
                    test_mat = cv2.cuda_GpuMat()
                    test_mat.upload(np.zeros((100, 100), dtype=np.uint8))
                    self.logger.info(f"GPU acceleration available: {device_count} CUDA device(s) detected")
                    return True
        except Exception as e:
            self.logger.debug(f"GPU check failed: {e}")

        self.logger.info("GPU acceleration not available, using CPU")
        return False

    def _init_background_subtractors(self):
        """Initialize background subtraction algorithms (GPU or CPU based)."""
        if self._use_gpu:
            try:
                # Try to create GPU versions
                self._bg_subtractor_mog2 = cv2.cuda.createBackgroundSubtractorMOG2(
                    detectShadows=False,
                    varThreshold=25,
                    history=100
                )
                # KNN not available in OpenCV CUDA, use CPU version
                self._bg_subtractor_knn = cv2.createBackgroundSubtractorKNN(
                    detectShadows=False,
                    dist2Threshold=400,
                    history=100
                )
                self.logger.info("Using GPU-accelerated MOG2 background subtractor")
                return
            except Exception as e:
                self.logger.warning(f"Failed to create GPU background subtractors: {e}")
                self._use_gpu = False

        # CPU versions (fallback or primary)
        self._bg_subtractor_mog2 = cv2.createBackgroundSubtractorMOG2(
            detectShadows=False,  # Faster without shadow detection
            varThreshold=25,      # Less sensitive
            history=100            # Shorter history for faster adaptation
        )
        self._bg_subtractor_mog2.setComplexityReductionThreshold(0.05)

        # KNN background subtractor (optimized)
        self._bg_subtractor_knn = cv2.createBackgroundSubtractorKNN(
            detectShadows=False,   # Faster without shadow detection
            dist2Threshold=400,
            history=100            # Shorter history
        )

    def process_frame(self, frame: np.ndarray) -> Tuple[List[MotionDetection], Optional[CameraMotion], np.ndarray]:
        """
        Process a frame for motion detection with camera compensation.

        Args:
            frame: Input frame (BGR)

        Returns:
            Tuple of (detections, camera_motion, annotated_frame)
        """
        start_time = time.time()

        # Quick snapshot of config to avoid holding lock during processing
        with self._config_lock:
            mode = self._config.mode
            algorithm = self._config.algorithm
            min_area = self._config.min_area
            max_area = self._config.max_area
            morphology_size = self._config.morphology_size
            motion_threshold = self._config.motion_threshold
            compensation_strength = self._config.compensation_strength
            auto_mode_threshold = self._config.auto_mode_threshold
            processing_resolution = self._config.processing_resolution

        # Downsample for performance if configured
        h, w = frame.shape[:2]
        scale_factor = 1.0

        if processing_resolution is not None:
            target_width, target_height = processing_resolution
            # Calculate scale factor maintaining aspect ratio
            if w > target_width or h > target_height:
                scale_factor = min(target_width / w, target_height / h)
                new_w = int(w * scale_factor)
                new_h = int(h * scale_factor)
                small_frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
                gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            else:
                small_frame = frame
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            # Default behavior: downsample if width > 1280
            if w > 1280:
                scale_factor = 1280 / w
                new_w = int(w * scale_factor)
                new_h = int(h * scale_factor)
                small_frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
                gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
            else:
                small_frame = frame
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Only check camera motion periodically (not every frame)
        self._frame_skip_counter += 1

        # Auto-detect mode if needed (but not every frame)
        if mode == DetectionMode.AUTO and self._frame_skip_counter % self._motion_check_interval == 0:
            self._update_detection_mode(gray, auto_mode_threshold)
        else:
            self._current_mode = mode if mode != DetectionMode.AUTO else self._current_mode

        # Estimate camera motion only periodically and if in moving mode
        camera_motion = None
        compensated_frame = small_frame.copy()

        if self._current_mode == DetectionMode.MOVING and self._prev_gray is not None:
            if self._frame_skip_counter % self._motion_check_interval == 0:
                camera_motion = self._estimate_camera_motion(self._prev_gray, gray)
                if camera_motion and camera_motion.confidence > 0.5:
                    compensated_frame = self._compensate_camera_motion(small_frame, camera_motion, compensation_strength)
            else:
                # Reuse last camera motion if available
                if self._camera_motion_history:
                    camera_motion = self._camera_motion_history[-1]

        # Store camera motion in history if new
        if camera_motion and self._frame_skip_counter % self._motion_check_interval == 0:
            self._camera_motion_history.append(camera_motion)

        # Detect motion based on selected algorithm
        if algorithm == MotionAlgorithm.FRAME_DIFF:
            detections = self._detect_frame_diff(compensated_frame, gray, motion_threshold, morphology_size, min_area, max_area)
        elif algorithm == MotionAlgorithm.MOG2:
            detections = self._detect_mog2(compensated_frame, morphology_size, min_area, max_area)
        elif algorithm == MotionAlgorithm.KNN:
            detections = self._detect_knn(compensated_frame, morphology_size, min_area, max_area)
        elif algorithm == MotionAlgorithm.OPTICAL_FLOW:
            detections = self._detect_optical_flow(gray, motion_threshold, morphology_size, min_area, max_area)
        else:
            detections = self._detect_feature_match(gray, min_area, max_area)

        # Filter detections by area
        detections = [d for d in detections
                      if min_area <= d.area <= max_area]

        # Scale detection coordinates back to original frame size if downsampled
        if scale_factor < 1.0:
            scale_back = 1.0 / scale_factor
            for detection in detections:
                x, y, width, height = detection.bbox
                detection.bbox = (
                    int(x * scale_back),
                    int(y * scale_back),
                    int(width * scale_back),
                    int(height * scale_back)
                )
                detection.centroid = (
                    int(detection.centroid[0] * scale_back),
                    int(detection.centroid[1] * scale_back)
                )
                detection.area *= (scale_back * scale_back)

        # Create annotated frame using original resolution
        annotated_frame = self._annotate_frame(frame, detections, camera_motion)

        # Update state
        self._prev_frame = compensated_frame.copy()
        self._prev_gray = gray.copy()
        self._frame_history.append(gray)

        # Track performance
        processing_time = time.time() - start_time
        self._update_performance_metrics(processing_time, len(detections))

        # Emit signals
        self.detectionsReady.emit(detections, camera_motion, annotated_frame)

        return detections, camera_motion, annotated_frame

    def _update_detection_mode(self, gray: np.ndarray, auto_mode_threshold: float):
        """Auto-detect whether camera is static or moving."""
        if self._prev_gray is None:
            return

        # Downsample further for faster optical flow
        h, w = gray.shape
        scale = 0.25  # Process at 1/4 resolution
        small_prev = cv2.resize(self._prev_gray, (int(w*scale), int(h*scale)))
        small_curr = cv2.resize(gray, (int(w*scale), int(h*scale)))

        # Calculate optical flow on downsampled images
        flow = cv2.calcOpticalFlowFarneback(
            small_prev, small_curr, None,
            pyr_scale=0.5, levels=1, winsize=15,
            iterations=1, poly_n=5, poly_sigma=1.1, flags=0
        )

        # Calculate average flow magnitude
        magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
        avg_magnitude = np.mean(magnitude) * 4  # Scale back up

        # Update mode based on motion threshold
        threshold = auto_mode_threshold
        if avg_magnitude > threshold * 1.5:
            self._current_mode = DetectionMode.MOVING
            self._mode_confidence = min(1.0, avg_magnitude / (threshold * 2))
        elif avg_magnitude < threshold * 0.5:
            self._current_mode = DetectionMode.STATIC
            self._mode_confidence = 1.0 - (avg_magnitude / threshold)

        # Emit mode change signal if mode changed
        if hasattr(self, '_last_mode') and self._last_mode != self._current_mode:
            self.modeChanged.emit(self._current_mode.value)
        self._last_mode = self._current_mode

    def _estimate_camera_motion(self, prev_gray: np.ndarray, curr_gray: np.ndarray) -> Optional[CameraMotion]:
        """Estimate global camera motion using feature matching."""
        try:
            # Check if frame sizes match
            if prev_gray.shape != curr_gray.shape:
                self.logger.warning("Camera motion estimation frame size mismatch. Skipping.")
                return None

            # Downsample for faster feature detection
            h, w = prev_gray.shape
            if w > 640:
                scale = 640 / w
                small_prev = cv2.resize(prev_gray, (int(w*scale), int(h*scale)))
                small_curr = cv2.resize(curr_gray, (int(w*scale), int(h*scale)))
            else:
                small_prev = prev_gray
                small_curr = curr_gray
                scale = 1.0

            # Detect features in both frames
            kp1, des1 = self._feature_detector.detectAndCompute(small_prev, None)
            kp2, des2 = self._feature_detector.detectAndCompute(small_curr, None)

            if des1 is None or des2 is None or len(kp1) < 10 or len(kp2) < 10:
                return None

            # Match features using knnMatch for better performance
            matches = self._matcher.knnMatch(des1, des2, k=2)

            # Apply ratio test to get good matches
            good_matches = []
            for match_pair in matches:
                if len(match_pair) == 2:
                    m, n = match_pair
                    if m.distance < 0.7 * n.distance:
                        good_matches.append(m)

            if len(good_matches) < 8:
                return None

            # Extract matched points and scale back up
            pts1 = np.float32([kp1[m.queryIdx].pt for m in good_matches]) / scale
            pts2 = np.float32([kp2[m.trainIdx].pt for m in good_matches]) / scale

            # Calculate homography for camera motion
            homography, mask = cv2.findHomography(pts1, pts2, cv2.RANSAC, 5.0)

            if homography is None:
                return None

            # Calculate average motion vector
            motion_vectors = pts2 - pts1
            inliers = motion_vectors[mask.ravel() == 1]

            if len(inliers) > 0:
                global_velocity = np.mean(inliers, axis=0)

                # Estimate rotation from homography
                rotation_angle = np.arctan2(homography[1, 0], homography[0, 0]) * 180 / np.pi

                # Calculate confidence based on inlier ratio
                confidence = len(inliers) / len(matches)

                return CameraMotion(
                    global_velocity=tuple(global_velocity),
                    rotation_angle=rotation_angle,
                    confidence=confidence,
                    homography=homography
                )

        except Exception as e:
            self.logger.error(f"Camera motion estimation error: {e}")

        return None

    def _compensate_camera_motion(self, frame: np.ndarray, camera_motion: CameraMotion, compensation_strength: float) -> np.ndarray:
        """Compensate for camera motion by warping frame."""
        if camera_motion.homography is None:
            return frame

        try:
            # Apply inverse homography to compensate for camera motion
            h, w = frame.shape[:2]

            # Apply compensation strength factor
            strength = compensation_strength
            if strength < 1.0:
                # Blend identity matrix with homography based on strength
                identity = np.eye(3, dtype=np.float32)
                compensated_h = identity * (1 - strength) + camera_motion.homography * strength
            else:
                compensated_h = camera_motion.homography

            # Warp frame to compensate for motion
            compensated = cv2.warpPerspective(frame, np.linalg.inv(compensated_h), (w, h))

            return compensated

        except Exception as e:
            self.logger.error(f"Motion compensation error: {e}")
            return frame

    def _detect_frame_diff(self, frame: np.ndarray, gray: np.ndarray, motion_threshold: int,
                           morphology_size: int, min_area: int, max_area: int) -> List[MotionDetection]:
        """Simple frame differencing motion detection."""
        detections = []

        if self._prev_gray is None:
            return detections

        # Check if frame sizes match (in case of resolution change)
        if self._prev_gray.shape != gray.shape:
            self.logger.warning(f"Frame size mismatch: prev={self._prev_gray.shape}, curr={gray.shape}. Skipping frame.")
            self._prev_gray = gray.copy()
            return detections

        # Calculate frame difference
        diff = cv2.absdiff(self._prev_gray, gray)

        # Apply threshold
        _, thresh = cv2.threshold(diff, motion_threshold, 255, cv2.THRESH_BINARY)

        # Apply morphology to remove noise
        kernel = np.ones((morphology_size, morphology_size), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue

            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)

            # Calculate centroid
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = x + w // 2, y + h // 2

            # Estimate velocity (simple frame-to-frame difference)
            velocity = (0.0, 0.0)  # Will be calculated with history if available

            detection = MotionDetection(
                bbox=(x, y, w, h),
                centroid=(cx, cy),
                area=area,
                velocity=velocity,
                confidence=min(1.0, area / max_area),
                timestamp=time.time(),
                is_compensated=(self._current_mode == DetectionMode.MOVING),
                contour=contour
            )
            detections.append(detection)

        return detections

    def _detect_mog2(self, frame: np.ndarray, morphology_size: int, min_area: int, max_area: int) -> List[MotionDetection]:
        """MOG2 background subtraction motion detection with GPU support."""
        if self._use_gpu and hasattr(self._bg_subtractor_mog2, 'apply'):
            try:
                # GPU path
                gpu_frame = cv2.cuda_GpuMat()
                gpu_frame.upload(frame)

                gpu_fg_mask = self._bg_subtractor_mog2.apply(gpu_frame, -1)
                fg_mask = gpu_fg_mask.download()

                # Threshold on GPU if possible
                gpu_fg_mask.upload(fg_mask)
                gpu_thresh = cv2.cuda.threshold(gpu_fg_mask, 200, 255, cv2.THRESH_BINARY)[1]
                fg_mask = gpu_thresh.download()

            except Exception as e:
                self.logger.debug(f"GPU MOG2 failed, falling back to CPU: {e}")
                # Fallback to CPU
                fg_mask = self._bg_subtractor_mog2.apply(frame)
                _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
        else:
            # CPU path
            fg_mask = self._bg_subtractor_mog2.apply(frame)
            _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

        # Minimal morphology only if needed (CPU only for now)
        if morphology_size > 0:
            kernel = np.ones((3, 3), np.uint8)  # Fixed small kernel
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel, iterations=1)

        # Find contours and create detections
        return self._contours_to_detections(fg_mask, min_area, max_area)

    def _detect_knn(self, frame: np.ndarray, morphology_size: int, min_area: int, max_area: int) -> List[MotionDetection]:
        """KNN background subtraction motion detection."""
        # Apply background subtraction
        fg_mask = self._bg_subtractor_knn.apply(frame)

        # Simple threshold instead of morphology for speed
        _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

        # Minimal morphology only if needed
        if morphology_size > 0:
            kernel = np.ones((3, 3), np.uint8)  # Fixed small kernel
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel, iterations=1)

        # Find contours and create detections
        return self._contours_to_detections(fg_mask, min_area, max_area)

    def _detect_optical_flow(self, gray: np.ndarray, motion_threshold: int, morphology_size: int,
                             min_area: int, max_area: int) -> List[MotionDetection]:
        """Dense optical flow motion detection."""
        detections = []

        if self._prev_gray is None:
            return detections

        # Check if frame sizes match (in case of resolution change)
        if self._prev_gray.shape != gray.shape:
            self.logger.warning(f"Optical flow frame size mismatch: prev={self._prev_gray.shape}, "
                                f"curr={gray.shape}. Skipping frame.")
            self._prev_gray = gray.copy()
            return detections

        # Calculate dense optical flow
        flow = cv2.calcOpticalFlowFarneback(
            self._prev_gray, gray, None,
            pyr_scale=0.5, levels=3, winsize=15,
            iterations=3, poly_n=5, poly_sigma=1.2, flags=0
        )

        # Calculate magnitude and angle
        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])

        # Threshold magnitude to find motion
        motion_mask = magnitude > motion_threshold

        # Convert to binary mask
        binary_mask = (motion_mask * 255).astype(np.uint8)

        # Apply morphology
        kernel = np.ones((morphology_size * 2, morphology_size * 2), np.uint8)
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)

        # Find contours
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue

            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)

            # Calculate centroid
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = x + w // 2, y + h // 2

            # Calculate average velocity in region
            roi_flow = flow[y:y+h, x:x+w]
            avg_velocity = np.mean(roi_flow, axis=(0, 1))

            detection = MotionDetection(
                bbox=(x, y, w, h),
                centroid=(cx, cy),
                area=area,
                velocity=tuple(avg_velocity),
                confidence=min(1.0, np.mean(magnitude[y:y+h, x:x+w]) / 50),
                timestamp=time.time(),
                is_compensated=(self._current_mode == DetectionMode.MOVING),
                contour=contour
            )
            detections.append(detection)

        return detections

    def _detect_feature_match(self, gray: np.ndarray, min_area: int, max_area: int) -> List[MotionDetection]:
        """Feature matching based motion detection."""
        # This is primarily used for camera motion, but can detect object motion too
        # For now, return empty list since we need previous frame
        return []

    def _contours_to_detections(self, mask: np.ndarray, min_area: int, max_area: int) -> List[MotionDetection]:
        """Convert contours from a mask to motion detections."""
        detections = []

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue

            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)

            # Calculate centroid
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = x + w // 2, y + h // 2

            detection = MotionDetection(
                bbox=(x, y, w, h),
                centroid=(cx, cy),
                area=area,
                velocity=(0.0, 0.0),
                confidence=min(1.0, area / max_area),
                timestamp=time.time(),
                is_compensated=(self._current_mode == DetectionMode.MOVING),
                contour=contour
            )
            detections.append(detection)

        return detections

    def _annotate_frame(self, frame: np.ndarray, detections: List[MotionDetection],
                        camera_motion: Optional[CameraMotion]) -> np.ndarray:
        """Annotate frame with detection results."""
        # Always annotate frame with detections for visibility
        annotated = frame.copy()

        # Draw camera motion info if available
        if camera_motion:
            # Only draw if motion is significant
            if abs(camera_motion.global_velocity[0]) > 1 or abs(camera_motion.global_velocity[1]) > 1:
                h, w = frame.shape[:2]
                center = (w // 2, h // 2)
                end_point = (
                    int(center[0] + camera_motion.global_velocity[0] * 5),
                    int(center[1] + camera_motion.global_velocity[1] * 5)
                )
                cv2.arrowedLine(annotated, center, end_point, (255, 0, 255), 2)

            # Add camera motion info text (simplified)
            info_text = f"{self._current_mode.value}: ({camera_motion.global_velocity[0]:.0f}, {camera_motion.global_velocity[1]:.0f})"
            cv2.putText(annotated, info_text, (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 1)

        # Draw detections (simplified for performance)
        for detection in detections[:10]:  # Limit to 10 detections for performance
            x, y, w, h = detection.bbox

            # Draw bounding box
            color = (0, 255, 0) if detection.is_compensated else (0, 255, 255)
            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 1)

            # Draw area text on each detection
            area_text = f"{int(detection.area)}"
            cv2.putText(annotated, area_text, (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

            # Only draw centroid for large detections
            if detection.area > 1000:
                cv2.circle(annotated, detection.centroid, 3, (0, 0, 255), -1)

            # Draw velocity vector only if significant
            if abs(detection.velocity[0]) > 2 or abs(detection.velocity[1]) > 2:
                start = detection.centroid
                end = (
                    int(start[0] + detection.velocity[0] * 5),
                    int(start[1] + detection.velocity[1] * 5)
                )
                cv2.arrowedLine(annotated, start, end, (255, 255, 0), 1)

        # Add statistics with total area
        total_area = sum(d.area for d in detections)
        stats_text = f"Detections: {len(detections)} | Total Area: {int(total_area)} | Mode: {self._current_mode.value}"
        cv2.putText(annotated, stats_text, (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        return annotated

    def _update_performance_metrics(self, processing_time: float, detection_count: int):
        """Update and emit performance metrics."""
        self._processing_times.append(processing_time)
        self._frame_count += 1

        current_time = time.time()
        if current_time - self._last_fps_time >= 1.0:
            fps = self._frame_count / (current_time - self._last_fps_time)
            avg_processing_time = np.mean(self._processing_times) if self._processing_times else 0

            metrics = {
                'fps': fps,
                'avg_processing_time_ms': avg_processing_time * 1000,
                'detection_count': detection_count,
                'mode': self._current_mode.value,
                'mode_confidence': self._mode_confidence,
                'gpu_enabled': self._use_gpu
            }

            self.performanceUpdate.emit(metrics)

            self._frame_count = 0
            self._last_fps_time = current_time

    def update_config(self, **kwargs):
        """Update detection configuration."""
        try:
            with self._config_lock:
                # Check if resolution is changing
                resolution_changed = 'processing_resolution' in kwargs and \
                    kwargs['processing_resolution'] != self._config.processing_resolution

                for key, value in kwargs.items():
                    if hasattr(self._config, key):
                        setattr(self._config, key, value)

                # Clear frame buffers if resolution changed to avoid size mismatch errors
                if resolution_changed:
                    self._prev_frame = None
                    self._prev_gray = None
                    self._frame_history.clear()
                    self._camera_motion_history.clear()
                    # Reinitialize background subtractors for new resolution
                    self._init_background_subtractors()
                    self.logger.info("Cleared frame buffers due to resolution change")

                # Update dependent settings
                if 'history_frames' in kwargs:
                    self._frame_history = collections.deque(maxlen=self._config.history_frames)

                # Don't reinit background subtractors for sensitivity - just adjust threshold
                # This prevents the UI freeze when adjusting the slider
                if 'sensitivity' in kwargs and self._bg_subtractor_mog2 and not resolution_changed:
                    # Adjust the variance threshold based on sensitivity (0-1)
                    # Lower sensitivity = higher threshold (less sensitive)
                    # Higher sensitivity = lower threshold (more sensitive)
                    new_threshold = 50 - (self._config.sensitivity * 40)  # Range: 10-50
                    self._bg_subtractor_mog2.setVarThreshold(new_threshold)
        except Exception as e:
            self.logger.error(f"Error updating config: {e}")

        # Don't emit signal - it's not connected and might cause issues
        # self.configurationChanged.emit(self.get_config())

    def get_config(self) -> dict:
        """Get current configuration as dictionary."""
        with self._config_lock:
            return {
                'mode': self._config.mode.value,
                'algorithm': self._config.algorithm.value,
                'sensitivity': self._config.sensitivity,
                'min_area': self._config.min_area,
                'max_area': self._config.max_area,
                'motion_threshold': self._config.motion_threshold,
                'compensation_strength': self._config.compensation_strength,
                'show_vectors': self._config.show_vectors,
                'show_camera_motion': self._config.show_camera_motion,
                'gpu_enabled': self._use_gpu
            }

    def reset(self):
        """Reset detector state."""
        self._prev_frame = None
        self._prev_gray = None
        self._frame_history.clear()
        self._camera_motion_history.clear()
        self._init_background_subtractors()
        self.logger.info("Motion detector reset")


# Alias for backward compatibility with existing code
RealtimeMotionDetector = MotionDetectionService
