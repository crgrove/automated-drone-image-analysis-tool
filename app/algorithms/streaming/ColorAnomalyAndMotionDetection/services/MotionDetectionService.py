"""
MotionDetectionService.py - Motion detection service

Handles motion detection using frame differencing, MOG2, and KNN algorithms.
"""

from core.services.LoggerService import LoggerService
from PySide6.QtCore import QObject
from threading import Lock
from typing import List, Optional
from collections import deque
import time
import numpy as np
import cv2

# Import shared types
from .shared_types import Detection, MotionAlgorithm, ColorAnomalyAndMotionDetectionConfig


class MotionDetectionService(QObject):
    """
    Motion detection service for detecting moving objects in video streams.

    Supports multiple algorithms:
    - FRAME_DIFF: Simple frame differencing
    - MOG2: Gaussian mixture model (best for static cameras)
    - KNN: K-nearest neighbors (alternative for busy scenes)
    """

    def __init__(self):
        super().__init__()
        self.logger = LoggerService()
        self.config_lock = Lock()

        # Previous frame for frame differencing
        self._prev_gray: Optional[np.ndarray] = None

        # Pre-compute morphology kernels for efficiency
        self._morph_kernel_cache: dict = {}

        # Background subtractors (initialized with default config)
        # Initialize with default config to ensure they're ready for use
        default_config = ColorAnomalyAndMotionDetectionConfig()
        self._bg_subtractor_mog2: Optional[cv2.BackgroundSubtractorMOG2] = None
        self._bg_subtractor_knn: Optional[cv2.BackgroundSubtractorKNN] = None
        self._init_background_subtractors(default_config)

        # Persistence filter state
        self._detection_masks = []
        self._persistence_frames = 3

    def update_config(self, config: ColorAnomalyAndMotionDetectionConfig):
        """Update motion detection configuration."""
        with self.config_lock:
            old_persistence = self._persistence_frames
            self._persistence_frames = config.persistence_frames

            # Update persistence deque size if changed
            if old_persistence != config.persistence_frames:
                self._detection_masks = deque(
                    list(self._detection_masks) if hasattr(self._detection_masks, '__iter__') else [],
                    maxlen=config.persistence_frames
                )

            # Reinitialize background subtractors if parameters changed
            self._init_background_subtractors(config)

    def _init_background_subtractors(self, config: ColorAnomalyAndMotionDetectionConfig):
        """Initialize background subtraction algorithms."""
        # MOG2 - Gaussian Mixture-based Background/Foreground Segmentation
        self._bg_subtractor_mog2 = cv2.createBackgroundSubtractorMOG2(
            history=config.bg_history,
            varThreshold=config.bg_var_threshold,
            detectShadows=config.bg_detect_shadows
        )

        # KNN - K-Nearest Neighbors Background Subtraction
        self._bg_subtractor_knn = cv2.createBackgroundSubtractorKNN(
            history=config.bg_history,
            dist2Threshold=400.0,
            detectShadows=config.bg_detect_shadows
        )

    def _get_morph_kernel(self, size: int) -> np.ndarray:
        """Get cached morphology kernel."""
        if size not in self._morph_kernel_cache:
            self._morph_kernel_cache[size] = cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE, (size, size)
            )
        return self._morph_kernel_cache[size]

    def detect(self, frame_gray: np.ndarray, config: ColorAnomalyAndMotionDetectionConfig,
               max_detections: int = 0) -> List[Detection]:
        """
        Detect motion in a grayscale frame.

        Args:
            frame_gray: Grayscale frame
            config: Detection configuration
            max_detections: Maximum number of detections to return (0 = unlimited)

        Returns:
            List of Detection objects
        """
        with self.config_lock:
            if not config.enable_motion:
                return []

            # Select algorithm
            if config.motion_algorithm == MotionAlgorithm.MOG2:
                return self._mog2_detect(frame_gray, config, max_detections)
            elif config.motion_algorithm == MotionAlgorithm.KNN:
                return self._knn_detect(frame_gray, config, max_detections)
            else:  # FRAME_DIFF
                return self._baseline_detect_720p(frame_gray, config, max_detections)

    def _baseline_detect_720p(self, frame_gray: np.ndarray, config: ColorAnomalyAndMotionDetectionConfig,
                              max_detections: int = 0) -> List[Detection]:
        """Frame differencing detection."""
        detections = []

        # Need previous frame for differencing
        if self._prev_gray is None or self._prev_gray.shape != frame_gray.shape:
            self._prev_gray = frame_gray.copy()
            return detections

        # Vectorized frame differencing
        diff = cv2.absdiff(self._prev_gray, frame_gray)
        _, binary_mask = cv2.threshold(diff, config.motion_threshold, 255, cv2.THRESH_BINARY)

        # Morphology operations
        if config.enable_morphology:
            morph_kernel = self._get_morph_kernel(config.morphology_kernel_size)
            binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, morph_kernel)
            binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, morph_kernel)

        # Find contours
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Process contours
        timestamp = time.time()
        for contour in contours:
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
                detection_type='baseline_motion',
                timestamp=timestamp,
                contour=contour,
                metadata={'threshold': config.motion_threshold}
            )
            detections.append(detection)

        # Update previous frame
        self._prev_gray = frame_gray.copy()
        return detections

    def _mog2_detect(self, frame_gray: np.ndarray, config: ColorAnomalyAndMotionDetectionConfig,
                     max_detections: int = 0) -> List[Detection]:
        """MOG2 background subtraction detection."""
        detections = []

        # Apply background subtraction
        fg_mask = self._bg_subtractor_mog2.apply(frame_gray)

        # Threshold to remove shadow artifacts
        if config.bg_detect_shadows:
            _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

        # Morphology to clean up noise
        if config.enable_morphology:
            morph_kernel = self._get_morph_kernel(config.morphology_kernel_size)
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, morph_kernel)
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, morph_kernel)

        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Process contours
        timestamp = time.time()
        for contour in contours:
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

    def _knn_detect(self, frame_gray: np.ndarray, config: ColorAnomalyAndMotionDetectionConfig,
                    max_detections: int = 0) -> List[Detection]:
        """KNN background subtraction detection."""
        detections = []

        # Apply background subtraction
        fg_mask = self._bg_subtractor_knn.apply(frame_gray)

        # Threshold to remove shadow artifacts
        if config.bg_detect_shadows:
            _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

        # Morphology to clean up noise
        if config.enable_morphology:
            morph_kernel = self._get_morph_kernel(config.morphology_kernel_size)
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, morph_kernel)
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, morph_kernel)

        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Process contours
        timestamp = time.time()
        for contour in contours:
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

    def check_camera_movement(self, frame_gray: np.ndarray, config: ColorAnomalyAndMotionDetectionConfig) -> bool:
        """
        Check if camera is moving by analyzing frame differences.

        Args:
            frame_gray: Grayscale frame
            config: Detection configuration

        Returns:
            True if camera movement detected, False otherwise
        """
        if not config.pause_on_camera_movement or self._prev_gray is None:
            return False

        if self._prev_gray.shape != frame_gray.shape:
            return False

        # Quick frame difference check
        diff = cv2.absdiff(self._prev_gray, frame_gray)
        _, diff_mask = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)

        # Calculate percentage of frame that changed
        changed_pixels = np.count_nonzero(diff_mask)
        total_pixels = diff_mask.size
        change_ratio = changed_pixels / total_pixels

        # If more than threshold of frame changed, assume camera movement
        return change_ratio > config.camera_movement_threshold

    def reset(self):
        """Reset motion detection state."""
        self._prev_gray = None
        self._detection_masks = []
