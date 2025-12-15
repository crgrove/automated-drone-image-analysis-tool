"""
ColorAnomalyAndMotionDetectionOrchestrator.py - Orchestrator for color anomaly and motion detection

Coordinates MotionDetectionService and ColorAnomalyService to provide unified
color anomaly and motion detection with fusion, temporal smoothing, and filtering.
"""

from core.services.LoggerService import LoggerService
from core.services.SettingsService import SettingsService
from core.services.streaming.StreamingUtils import (
    FrameQueue, PerformanceMetrics, StageTimings
)
from PySide6.QtCore import QObject, Signal
from threading import Lock
from collections import deque
from typing import List, Tuple, Optional, Dict, Any
import time
import numpy as np
import cv2

# Import shared types
from .shared_types import Detection, FusionMode, ColorAnomalyAndMotionDetectionConfig
from .MotionDetectionService import MotionDetectionService
from .ColorAnomalyService import ColorAnomalyService


class ColorAnomalyAndMotionDetectionOrchestrator(QObject):
    """
    Orchestrator that coordinates motion and color anomaly detection services.

    Provides:
    - Unified interface for combined detection
    - Fusion of motion and color detections
    - Temporal smoothing and voting
    - False positive reduction filters
    - Frame rendering and annotation

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
        self.settings_service = SettingsService()

        # Configuration
        self.config = ColorAnomalyAndMotionDetectionConfig()
        self.config_lock = Lock()

        # Sub-services
        self.motion_service = MotionDetectionService()
        self.color_service = ColorAnomalyService()

        # Initialize services with default config
        self.motion_service.update_config(self.config)
        self.color_service.update_config(self.config)

        # Performance tracking
        self.metrics = PerformanceMetrics()
        self.frame_queue = FrameQueue()

        # FPS calculation
        self._fps_counter = 0
        self._fps_start_time = time.time()
        self._last_fps_update = time.time()

        # Temporal voting state
        self._temporal_detection_history: deque = deque(maxlen=self.config.temporal_window_frames)

        # Processing mask manager
        from core.services.streaming.MaskManager import MaskManager
        self._mask_manager = MaskManager()

        # Rendering state (for render_at_processing_res)
        self._processing_frame = None
        self._original_frame = None
        self._current_scale_factor = 1.0

        # Frame rate limiting state
        self._last_processed_time = 0.0
        self._last_detections: List[Detection] = []  # Persist detections when skipping frames

        # self.logger.info("Color anomaly and motion detection orchestrator initialized")

    def update_config(self, config: ColorAnomalyAndMotionDetectionConfig):
        """Update detection configuration thread-safely."""
        with self.config_lock:
            old_temporal_window = self.config.temporal_window_frames
            self.config = config

            # Update temporal voting deque size if changed
            if old_temporal_window != config.temporal_window_frames:
                self._temporal_detection_history = deque(
                    list(self._temporal_detection_history),
                    maxlen=config.temporal_window_frames
                )

            # Update sub-services
            self.motion_service.update_config(config)
            self.color_service.update_config(config)

        # self.logger.info("Orchestrator configuration updated")

    def _scale_detections_to_original(self, detections: List[Detection], scale_factor: float) -> List[Detection]:
        """
        Scale detections from processing resolution back to original resolution.

        Args:
            detections: List of detections at processing resolution
            scale_factor: The scale factor used for downsampling (e.g., 0.5 for 1920->960)

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

            # Scale area (proportional to inv_scale squared)
            scaled_area = detection.area * inv_scale * inv_scale

            # Scale contour points if present
            scaled_contour = None
            if detection.contour is not None:
                scaled_contour = (detection.contour * inv_scale).astype(np.int32)

            scaled_detection = Detection(
                bbox=scaled_bbox,
                centroid=scaled_centroid,
                area=scaled_area,
                confidence=detection.confidence,
                detection_type=detection.detection_type,
                timestamp=detection.timestamp,
                contour=scaled_contour,
                metadata={**detection.metadata, 'scale_factor_applied': inv_scale}
            )
            scaled_detections.append(scaled_detection)

        return scaled_detections

    def _fuse_detections(self, motion_detections: List[Detection], color_detections: List[Detection]) -> List[Detection]:
        """Fuse motion and color detections using configured mode."""
        config = self.config

        # Smart skip: If only one source, return it directly
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
            all_detections = motion_detections + color_detections
            processed = [False] * len(all_detections)

            for i, det1 in enumerate(all_detections):
                if processed[i]:
                    continue

                overlapping = [det1]
                processed[i] = True

                for j in range(i + 1, len(all_detections)):
                    if processed[j]:
                        continue
                    det2 = all_detections[j]
                    iou = self._calculate_iou(det1.bbox, det2.bbox)
                    if iou > 0.3:
                        overlapping.append(det2)
                        processed[j] = True

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
                    if iou > 0.3:
                        merged = self._merge_detections([motion_det, color_det])
                        merged.detection_type = 'fused'
                        merged.confidence = min(1.0, (motion_det.confidence + color_det.confidence) / 2 * 1.5)
                        fused_detections.append(merged)

        elif config.fusion_mode == FusionMode.COLOR_PRIORITY:
            # COLOR_PRIORITY: Start with color, add non-overlapping motion
            fused_detections = color_detections.copy()
            for motion_det in motion_detections:
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
                overlaps = False
                for motion_det in motion_detections:
                    if self._calculate_iou(color_det.bbox, motion_det.bbox) > 0.3:
                        overlaps = True
                        break
                if not overlaps:
                    fused_detections.append(color_det)

        return fused_detections

    def _calculate_iou(self, bbox1: Tuple[int, int, int, int], bbox2: Tuple[int, int, int, int]) -> float:
        """Calculate Intersection over Union (IoU) between two bounding boxes."""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2

        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)

        if x_right < x_left or y_bottom < y_top:
            return 0.0

        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        box1_area = w1 * h1
        box2_area = w2 * h2
        union_area = box1_area + box2_area - intersection_area

        if union_area == 0:
            return 0.0

        return intersection_area / union_area

    def _merge_detections(self, detections: List[Detection]) -> Detection:
        """Merge multiple overlapping detections into one."""
        if len(detections) == 1:
            return detections[0]

        contours_to_merge = [d.contour for d in detections if d.contour is not None]

        if contours_to_merge:
            merged_contour = np.vstack(contours_to_merge)
            x, y, w, h = cv2.boundingRect(merged_contour)
            merged_bbox = (x, y, w, h)

            M = cv2.moments(merged_contour)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = x + w // 2, y + h // 2

            total_area = cv2.contourArea(merged_contour)
        else:
            min_x = min(d.bbox[0] for d in detections)
            min_y = min(d.bbox[1] for d in detections)
            max_x = max(d.bbox[0] + d.bbox[2] for d in detections)
            max_y = max(d.bbox[1] + d.bbox[3] for d in detections)

            merged_bbox = (min_x, min_y, max_x - min_x, max_y - min_y)
            cx = int(np.mean([d.centroid[0] for d in detections]))
            cy = int(np.mean([d.centroid[1] for d in detections]))
            total_area = sum(d.area for d in detections)
            merged_contour = None

        max_confidence = max(d.confidence for d in detections)
        timestamp = detections[0].timestamp

        types = [d.detection_type for d in detections]
        if 'color_anomaly' in types and any('motion' in t for t in types):
            detection_type = 'fused'
        else:
            detection_type = detections[0].detection_type

        return Detection(
            bbox=merged_bbox,
            centroid=(cx, cy),
            area=total_area,
            confidence=max_confidence,
            detection_type=detection_type,
            timestamp=timestamp,
            contour=merged_contour,
            metadata={'merged_from': len(detections), 'clustered': True}
        )

    def _apply_temporal_voting(self, current_detections: List[Detection]) -> List[Detection]:
        """Apply temporal majority voting to reduce flicker."""
        config = self.config
        if not config.enable_temporal_voting:
            return current_detections

        # Add current detections to history
        self._temporal_detection_history.append(current_detections)

        # Need full window before we start filtering
        if len(self._temporal_detection_history) < config.temporal_window_frames:
            return current_detections

        # Vote: Keep detections that appear in N of M frames
        voted_detections = []

        for current_det in current_detections:
            vote_count = 0

            for past_detections in self._temporal_detection_history:
                for past_det in past_detections:
                    iou = self._calculate_iou(current_det.bbox, past_det.bbox)
                    if iou > 0.3:
                        vote_count += 1
                        break

            if vote_count >= config.temporal_threshold_frames:
                voted_detections.append(current_det)

        return voted_detections

    def _apply_detection_clustering(self, detections: List[Detection]) -> List[Detection]:
        """Cluster nearby detections based on centroid distance."""
        config = self.config
        if not config.enable_detection_clustering or len(detections) == 0:
            return detections

        processed = [False] * len(detections)
        clustered_detections = []

        for i, det1 in enumerate(detections):
            if processed[i]:
                continue

            cluster = [det1]
            processed[i] = True
            cx1, cy1 = det1.centroid

            for j in range(i + 1, len(detections)):
                if processed[j]:
                    continue

                det2 = detections[j]
                cx2, cy2 = det2.centroid
                distance = np.sqrt((cx2 - cx1) ** 2 + (cy2 - cy1) ** 2)

                if distance <= config.clustering_distance:
                    cluster.append(det2)
                    processed[j] = True

            if len(cluster) > 1:
                merged = self._merge_detections(cluster)
                merged.metadata['clustered'] = True
                merged.metadata['cluster_size'] = len(cluster)
                clustered_detections.append(merged)
            else:
                clustered_detections.append(det1)

        return clustered_detections

    def _apply_aspect_ratio_filter(self, detections: List[Detection]) -> List[Detection]:
        """Filter detections by aspect ratio."""
        config = self.config
        if not config.enable_aspect_ratio_filter:
            return detections

        filtered = []
        for detection in detections:
            x, y, w, h = detection.bbox
            if h == 0:
                continue
            aspect_ratio = w / h
            if config.min_aspect_ratio <= aspect_ratio <= config.max_aspect_ratio:
                filtered.append(detection)

        return filtered

    def _apply_color_exclusion_filter(self, detections: List[Detection], frame_bgr: np.ndarray) -> List[Detection]:
        """Filter detections by excluded hue ranges."""
        config = self.config
        if not config.enable_color_exclusion or not config.excluded_hue_ranges:
            return detections

        frame_hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        filtered = []
        h_frame, w_frame = frame_hsv.shape[:2]

        for detection in detections:
            hue_value: Optional[float] = None
            metadata = detection.metadata or {}

            if 'dominant_color' in metadata:
                try:
                    bgr_color = metadata['dominant_color']
                    bgr_pixel = np.uint8([[[bgr_color[0], bgr_color[1], bgr_color[2]]]])
                    hsv_pixel = cv2.cvtColor(bgr_pixel, cv2.COLOR_BGR2HSV)
                    hue_value = float(hsv_pixel[0][0][0])
                except Exception:
                    hue_value = None

            if hue_value is None:
                x, y, w, h = detection.bbox
                x = max(0, min(x, w_frame - 1))
                y = max(0, min(y, h_frame - 1))
                w = max(1, min(w, w_frame - x))
                h = max(1, min(h, h_frame - y))

                region_hsv = frame_hsv[y:y + h, x:x + w]
                if region_hsv.size > 0:
                    hue_value = float(region_hsv[:, :, 0].mean())

            if hue_value is None:
                filtered.append(detection)
                continue

            is_excluded = False
            for hue_min, hue_max in config.excluded_hue_ranges:
                if hue_min > hue_max:
                    if hue_value >= hue_min or hue_value <= hue_max:
                        is_excluded = True
                        break
                else:
                    if hue_min <= hue_value <= hue_max:
                        is_excluded = True
                        break

            if not is_excluded:
                filtered.append(detection)

        return filtered

    def _apply_mask_filter(self, detections: List[Detection]) -> List[Detection]:
        """
        Filter detections to exclude those whose centroids fall outside the processing mask.

        Note: Detections are now at original resolution after immediate scaling.

        Args:
            detections: List of detections to filter (at original resolution)

        Returns:
            Filtered list of detections
        """
        config = self.config
        if not config.mask_enabled:
            return detections

        if not hasattr(self, '_mask_manager'):
            return detections

        if self._original_frame is None:
            return detections

        # Get original resolution (where detections now are)
        original_h, original_w = self._original_frame.shape[:2]

        # Get mask at original resolution (detections are now at original res)
        original_mask = self._mask_manager.get_mask(
            {
                'mask_enabled': config.mask_enabled,
                'frame_mask_enabled': config.frame_mask_enabled,
                'image_mask_enabled': config.image_mask_enabled,
                'frame_buffer_pixels': config.frame_buffer_pixels,
                'mask_image_path': config.mask_image_path,
            },
            (original_w, original_h),
            None  # No processing resolution - use original directly
        )

        if original_mask is None:
            return detections

        # Filter detections whose centroids fall in excluded regions (black in mask)
        filtered = []
        for detection in detections:
            cx, cy = detection.centroid
            # Ensure coordinates are within bounds
            cx = max(0, min(cx, original_w - 1))
            cy = max(0, min(cy, original_h - 1))

            # Check if centroid is in the processing region (white=255 in mask)
            if original_mask[cy, cx] > 127:  # Inside mask (process area)
                filtered.append(detection)

        return filtered

    def _draw_mask_overlay(self, frame: np.ndarray, config, render_scale: float) -> np.ndarray:
        """
        Draw mask overlay on frame for visualization.

        Args:
            frame: Frame to draw on
            config: Configuration object
            render_scale: Scale factor for coordinates (scale_factor when rendering at proc res, 1.0 otherwise)

        Returns:
            Frame with mask overlay drawn
        """
        if not hasattr(self, '_mask_manager'):
            return frame

        h, w = frame.shape[:2]
        result = frame

        # Draw frame buffer rectangle if enabled
        if config.frame_mask_enabled and config.frame_buffer_pixels > 0:
            buffer_px = config.frame_buffer_pixels

            # Scale buffer if rendering at processing resolution
            # render_scale is scale_factor when at proc res, 1.0 when at original
            if render_scale < 1.0:
                # Rendering at processing resolution - scale buffer down
                scaled_buffer = int(buffer_px * render_scale)
            else:
                # Rendering at original resolution - use buffer as-is
                scaled_buffer = buffer_px

            color = (255, 255, 0)  # Cyan (BGR)
            thickness = 2

            # Calculate bounds
            x1 = min(scaled_buffer, w // 2)
            y1 = min(scaled_buffer, h // 2)
            x2 = max(w - scaled_buffer, w // 2)
            y2 = max(h - scaled_buffer, h // 2)

            cv2.rectangle(result, (x1, y1), (x2, y2), color, thickness)

        # Draw image mask overlay if enabled
        if config.image_mask_enabled and config.mask_image_path:
            original_w, original_h = w, h
            if self._original_frame is not None:
                original_h, original_w = self._original_frame.shape[:2]

            render_mask = self._mask_manager.get_mask_for_rendering(
                {
                    'mask_enabled': config.mask_enabled,
                    'frame_mask_enabled': False,  # Only get image mask for overlay
                    'image_mask_enabled': True,
                    'mask_image_path': config.mask_image_path,
                    'show_mask_overlay': True,
                },
                (w, h),
                (original_w, original_h)
            )

            if render_mask is not None:
                # Create semi-transparent overlay for excluded regions
                # Excluded regions (black in mask) will be tinted red
                excluded = render_mask == 0

                # Create overlay with excluded regions tinted
                overlay = result.copy()
                # Tint excluded regions with red at 30% opacity
                overlay[excluded] = (
                    overlay[excluded] * 0.7 + np.array([0, 0, 128], dtype=np.float32) * 0.3
                ).astype(np.uint8)

                result = overlay

        return result

    def _render_detections_fast(self, frame: np.ndarray, detections: List[Detection]) -> np.ndarray:
        """
        Fast rendering of detections onto a frame (used when skipping frames for FPS limiting).

        This is a simplified version of the full rendering that just draws bounding boxes
        to maintain visual continuity when frames are skipped.

        Args:
            frame: Input BGR frame
            detections: List of detections to render

        Returns:
            Annotated frame with detections drawn
        """
        if not detections:
            return frame

        with self.config_lock:
            config = self.config

        if not config.show_detections:
            return frame

        annotated_frame = frame.copy()

        # Limit detections for performance
        detections_to_render = detections
        if config.max_detections_to_render > 0 and len(detections) > config.max_detections_to_render:
            detections_to_render = sorted(
                detections,
                key=lambda d: d.confidence * d.area,
                reverse=True
            )[:config.max_detections_to_render]

        for i, detection in enumerate(detections_to_render):
            x, y, w, h = detection.bbox
            cx, cy = detection.centroid

            # Color based on detection type
            if config.use_detection_color_for_rendering and 'dominant_color' in detection.metadata:
                try:
                    bgr_color = detection.metadata['dominant_color']
                    bgr_pixel = np.uint8([[[bgr_color[0], bgr_color[1], bgr_color[2]]]])
                    hsv_pixel = cv2.cvtColor(bgr_pixel, cv2.COLOR_BGR2HSV)
                    hue = hsv_pixel[0][0][0]
                    hsv_vibrant = np.uint8([[[hue, 255, 255]]])
                    bgr_vibrant = cv2.cvtColor(hsv_vibrant, cv2.COLOR_HSV2BGR)
                    color = tuple(int(c) for c in bgr_vibrant[0][0])
                except Exception:
                    color = (255, 0, 255)
            elif detection.detection_type == 'fused':
                color = (255, 255, 0) if detection.confidence > 0.7 else (255, 128, 0)
            elif detection.detection_type == 'color_anomaly':
                color = (255, 0, 255) if detection.confidence > 0.7 else (255, 0, 128)
            else:
                color = (0, 255, 0) if detection.confidence > 0.7 else (0, 255, 255)

            # Render shape
            if config.render_shape == 0:  # Box
                cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), color, 2)
                cv2.circle(annotated_frame, (cx, cy), 3, color, -1)
            elif config.render_shape == 1:  # Circle
                diagonal = np.sqrt(w * w + h * h) / 2.0
                radius = max(5, int(diagonal * 1.1))
                cv2.circle(annotated_frame, (cx, cy), radius, color, 2)
            elif config.render_shape == 2:  # Dot
                cv2.circle(annotated_frame, (cx, cy), 5, color, -1)

            # Render text label
            if config.render_text:
                if detection.detection_type == 'fused':
                    label = f"#{i + 1} FUSED"
                elif detection.detection_type == 'color_anomaly':
                    label = f"#{i + 1} COLOR"
                else:
                    label = f"#{i + 1} MOTION"
                cv2.putText(annotated_frame, label, (x, max(15, y - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)

        return annotated_frame

    def process_frame(self, frame: np.ndarray, timestamp: float) -> Tuple[np.ndarray, List[Detection], StageTimings]:
        """
        Process a frame through the color anomaly and motion detection pipeline.

        Args:
            frame: Input BGR frame
            timestamp: Frame timestamp

        Returns:
            Tuple of (annotated_frame, detections, timings)
        """
        timings = StageTimings()
        overall_start = time.perf_counter()

        # Frame rate limiting - skip frame if we're above target FPS
        with self.config_lock:
            target_fps = self.config.target_fps

        if target_fps > 0:
            target_interval = 1.0 / target_fps
            current_time = time.perf_counter()
            elapsed = current_time - self._last_processed_time

            if elapsed < target_interval:
                # Skip this frame - return previous detections for visual continuity
                timings.total_ms = (time.perf_counter() - overall_start) * 1000
                timings.was_skipped = True

                # Render previous detections onto current frame if we have any
                if self._last_detections:
                    annotated_frame = self._render_detections_fast(frame, self._last_detections)
                    return annotated_frame, self._last_detections, timings
                return frame, [], timings

            # Update last processed time
            self._last_processed_time = current_time

        # Frame queue management
        capture_start = time.perf_counter()
        self.frame_queue.put(frame, timestamp)
        working_frame, _ = self.frame_queue.get()
        if working_frame is None:
            working_frame = frame
        timings.capture_ms = (time.perf_counter() - capture_start) * 1000

        # Preprocessing
        preprocess_start = time.perf_counter()
        with self.config_lock:
            config = self.config

        # Scale to processing resolution
        h, w = working_frame.shape[:2]
        scale_factor = 1.0

        if w > config.processing_width or h > config.processing_height:
            scale_factor = min(config.processing_width / w, config.processing_height / h)
            new_w, new_h = int(w * scale_factor), int(h * scale_factor)
            new_w = max(1, new_w)
            new_h = max(1, new_h)
            processing_frame = cv2.resize(working_frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        else:
            processing_frame = working_frame
            scale_factor = 1.0

        # Store frames for mask operations
        self._original_frame = working_frame
        self._processing_frame = processing_frame
        self._current_scale_factor = scale_factor

        # Convert to grayscale
        processing_gray = cv2.cvtColor(processing_frame, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur
        if config.blur_kernel_size > 1:
            processing_gray = cv2.GaussianBlur(
                processing_gray,
                (config.blur_kernel_size, config.blur_kernel_size),
                0
            )

        timings.preprocessing_ms = (time.perf_counter() - preprocess_start) * 1000

        # Check for camera movement
        detection_start = time.perf_counter()
        is_camera_moving = self.motion_service.check_camera_movement(processing_gray, config)

        # Calculate early stopping limit
        max_to_detect = config.max_detections_to_render * 2 if config.max_detections_to_render > 0 else 0

        # Motion detection
        motion_detections = []
        motion_start = time.perf_counter()
        if config.enable_motion and not is_camera_moving:
            motion_detections = self.motion_service.detect(processing_gray, config, max_to_detect)
            # Scale motion detections to original resolution immediately
            if scale_factor < 1.0:
                motion_detections = self._scale_detections_to_original(motion_detections, scale_factor)
        timings.motion_detection_ms = (time.perf_counter() - motion_start) * 1000

        # Color detection
        color_detections = []
        color_start = time.perf_counter()
        if config.enable_color_quantization:
            color_detections = self.color_service.detect(processing_frame, config, max_to_detect)
            # Scale color detections to original resolution immediately
            if scale_factor < 1.0:
                color_detections = self._scale_detections_to_original(color_detections, scale_factor)
        timings.color_detection_ms = (time.perf_counter() - color_start) * 1000

        timings.detection_ms = (time.perf_counter() - detection_start) * 1000

        # Fusion & Temporal Smoothing
        fusion_start = time.perf_counter()

        # Fuse motion and color detections
        detections = self._fuse_detections(motion_detections, color_detections)

        # Apply temporal voting
        detections = self._apply_temporal_voting(detections)

        # Apply detection clustering
        detections = self._apply_detection_clustering(detections)

        # Apply false positive reduction filters
        detections = self._apply_aspect_ratio_filter(detections)
        # Use working_frame (original resolution) since detections are now at original resolution
        detections = self._apply_color_exclusion_filter(detections, working_frame)

        # Apply processing region mask filter (detections are now at original resolution)
        detections = self._apply_mask_filter(detections)

        timings.fusion_ms = (time.perf_counter() - fusion_start) * 1000

        # Rendering
        render_start = time.perf_counter()

        # Choose rendering resolution
        # Note: Detections are now at ORIGINAL resolution after immediate scaling
        if config.render_at_processing_res:
            render_frame = processing_frame.copy()
            # Detections are at original res, scale DOWN for processing res rendering
            render_scale = scale_factor if scale_factor < 1.0 else 1.0
        else:
            render_frame = working_frame.copy()
            # No scaling needed - detections already at original resolution
            render_scale = 1.0

        annotated_frame = render_frame

        # Limit detections for performance
        detections_to_render = detections
        total_detections = len(detections)
        detections_dropped = 0

        if config.show_detections and detections:
            if config.max_detections_to_render > 0 and len(detections) > config.max_detections_to_render:
                detections_sorted = sorted(
                    detections,
                    key=lambda d: d.confidence * d.area,
                    reverse=True
                )
                detections_to_render = detections_sorted[:config.max_detections_to_render]
                detections_dropped = len(detections) - config.max_detections_to_render

            # Draw detections
            for i, detection in enumerate(detections_to_render):
                x, y, w, h = detection.bbox
                x_scaled = int(x * render_scale)
                y_scaled = int(y * render_scale)
                w_scaled = int(w * render_scale)
                h_scaled = int(h * render_scale)

                cx_scaled = int(detection.centroid[0] * render_scale)
                cy_scaled = int(detection.centroid[1] * render_scale)

                # Color based on detection type
                if config.use_detection_color_for_rendering and 'dominant_color' in detection.metadata:
                    try:
                        bgr_color = detection.metadata['dominant_color']
                        bgr_pixel = np.uint8([[[bgr_color[0], bgr_color[1], bgr_color[2]]]])
                        hsv_pixel = cv2.cvtColor(bgr_pixel, cv2.COLOR_BGR2HSV)
                        hue = hsv_pixel[0][0][0]
                        hsv_vibrant = np.uint8([[[hue, 255, 255]]])
                        bgr_vibrant = cv2.cvtColor(hsv_vibrant, cv2.COLOR_HSV2BGR)
                        color = tuple(int(x) for x in bgr_vibrant[0][0])
                    except Exception:
                        color = (255, 0, 255)
                elif detection.detection_type == 'fused':
                    if detection.confidence > 0.7:
                        color = (255, 255, 0)
                    elif detection.confidence > 0.4:
                        color = (255, 128, 0)
                    else:
                        color = (200, 100, 0)
                elif detection.detection_type == 'color_anomaly':
                    if detection.confidence > 0.7:
                        color = (255, 0, 255)
                    elif detection.confidence > 0.4:
                        color = (255, 0, 128)
                    else:
                        color = (200, 0, 100)
                else:
                    if detection.confidence > 0.7:
                        color = (0, 255, 0)
                    elif detection.confidence > 0.4:
                        color = (0, 255, 255)
                    else:
                        color = (0, 165, 255)

                # Render based on toggles
                if config.render_contours and detection.contour is not None:
                    scaled_contour = (detection.contour * render_scale).astype(np.int32)
                    cv2.drawContours(annotated_frame, [scaled_contour], -1, color, 2)

                if config.render_shape == 0:  # Box
                    # Add AOI radius buffer from preferences to expand the box
                    aoi_radius = self.settings_service.get_setting('AOIRadius', 15)
                    x_expanded = max(0, x_scaled - int(aoi_radius))
                    y_expanded = max(0, y_scaled - int(aoi_radius))
                    w_expanded = w_scaled + int(aoi_radius) * 2
                    h_expanded = h_scaled + int(aoi_radius) * 2
                    # Ensure expanded box doesn't exceed image bounds
                    w_expanded = min(w_expanded, annotated_frame.shape[1] - x_expanded)
                    h_expanded = min(h_expanded, annotated_frame.shape[0] - y_expanded)
                    cv2.rectangle(annotated_frame, (x_expanded, y_expanded),
                                  (x_expanded + w_expanded, y_expanded + h_expanded), color, 2)
                    cv2.circle(annotated_frame, (cx_scaled, cy_scaled), 3, color, -1)
                elif config.render_shape == 1:  # Circle
                    if detection.contour is not None:
                        scaled_contour = (detection.contour * render_scale).astype(np.int32)
                        (_, _), contour_radius = cv2.minEnclosingCircle(scaled_contour)
                        base_radius = max(5, int(contour_radius * 1.5))
                    else:
                        # Calculate diagonal distance from centroid to corner of bounding box, then add 10% margin
                        diagonal = np.sqrt(w_scaled * w_scaled + h_scaled * h_scaled) / 2.0
                        base_radius = max(5, int(diagonal * 1.1))  # 10% margin to ensure full coverage
                    # Add AOI radius buffer from preferences
                    aoi_radius = self.settings_service.get_setting('AOIRadius', 15)
                    radius = base_radius + int(aoi_radius)
                    cv2.circle(annotated_frame, (cx_scaled, cy_scaled), radius, color, 2)
                elif config.render_shape == 2:  # Dot
                    cv2.circle(annotated_frame, (cx_scaled, cy_scaled), 5, color, -1)

                if config.render_text:
                    if detection.detection_type == 'fused':
                        label = f"#{i + 1} FUSED {int(detection.area)}px"
                    elif detection.detection_type == 'color_anomaly':
                        label = f"#{i + 1} COLOR {int(detection.area)}px"
                    else:
                        label = f"#{i + 1} MOTION {int(detection.area)}px"
                    cv2.putText(annotated_frame, label, (x_scaled, max(15, y_scaled - 5)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)

            if detections_dropped > 0:
                warning_text = f"⚠ {total_detections} detections ({detections_dropped} not shown for performance)"
                cv2.putText(annotated_frame, warning_text, (10, annotated_frame.shape[0] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1, cv2.LINE_AA)

        # Show camera movement indicator
        if is_camera_moving and config.enable_motion:
            overlay = annotated_frame.copy()
            h, w = annotated_frame.shape[:2]
            cv2.rectangle(overlay, (0, 0), (w, 80), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, annotated_frame, 0.3, 0, annotated_frame)
            cv2.putText(annotated_frame, "CAMERA MOVEMENT DETECTED",
                        (w // 2 - 190, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2, cv2.LINE_AA)
            cv2.putText(annotated_frame, "Motion detection paused (color still active)",
                        (w // 2 - 210, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        # Draw mask overlay if enabled
        if config.mask_enabled and config.show_mask_overlay:
            annotated_frame = self._draw_mask_overlay(annotated_frame, config, render_scale)

        # Upscale if rendered at processing res
        if config.render_at_processing_res and scale_factor < 1.0:
            h_orig, w_orig = working_frame.shape[:2]
            annotated_frame = cv2.resize(annotated_frame, (w_orig, h_orig), interpolation=cv2.INTER_LINEAR)

        timings.render_ms = (time.perf_counter() - render_start) * 1000
        timings.total_ms = (time.perf_counter() - overall_start) * 1000

        # Update metrics
        self.metrics.update(timings, len(detections))
        self._update_fps()

        # Check for dropped frames
        dropped = self.frame_queue.reset_dropped_count()
        if dropped > 0:
            self.metrics.dropped_frames += dropped

        # Add resolution metadata
        # Note: Detections are now at original resolution (scaled immediately after detection)
        # Set both resolutions to original so no additional scaling is applied by consumers
        original_resolution = (working_frame.shape[1], working_frame.shape[0])
        for detection in detections:
            if detection.metadata is None:
                detection.metadata = {}
            # Both set to original since detections are already at original resolution
            detection.metadata.setdefault('processing_resolution', original_resolution)
            detection.metadata.setdefault('original_resolution', original_resolution)

        # Emit signals
        self.frameProcessed.emit(annotated_frame, detections, self.metrics)

        # Emit performance update every second
        current_time = time.time()
        if current_time - self._last_fps_update >= 1.0:
            self.performanceUpdate.emit(self.metrics.to_dict())
            self._last_fps_update = current_time

        # Store detections for frame skipping (visual continuity)
        self._last_detections = detections

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
        self.motion_service.reset()
        # self.logger.info("Performance metrics reset")

    def reset_for_new_video(self):
        """Reset all state for a new video session.

        This should be called when switching videos to ensure clean state:
        - Clears temporal detection history (prevents old detections affecting new video)
        - Resets background subtractor models (prevents old background affecting motion detection)
        - Resets performance metrics
        """
        # Clear temporal detection history
        self._temporal_detection_history.clear()

        # Clear last detections (for frame skipping persistence)
        self._last_detections = []

        # Reset motion service including background models
        self.motion_service.reset_background_models()

        # Reset performance metrics
        self.metrics = PerformanceMetrics()
        self._fps_counter = 0
        self._fps_start_time = time.time()
