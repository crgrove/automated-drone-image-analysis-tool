"""
ColorAnomalyAndMotionDetectionOrchestrator.py - Orchestrator for color anomaly and motion detection

Coordinates MotionDetectionService and ColorAnomalyService to provide unified
color anomaly and motion detection with fusion, temporal smoothing, and filtering.
"""

from core.services.LoggerService import LoggerService
from core.services.streaming.StreamingUtils import (
    FrameQueue, PerformanceMetrics, StageTimings, TimingOverlayRenderer
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

        # Configuration
        self.config = ColorAnomalyAndMotionDetectionConfig()
        self.config_lock = Lock()

        # Sub-services
        self.motion_service = MotionDetectionService()
        self.color_service = ColorAnomalyService()

        # Performance tracking
        self.metrics = PerformanceMetrics()
        self.frame_queue = FrameQueue()
        self.timing_renderer = TimingOverlayRenderer()

        # FPS calculation
        self._fps_counter = 0
        self._fps_start_time = time.time()
        self._last_fps_update = time.time()

        # Temporal voting state
        self._temporal_detection_history: deque = deque(maxlen=self.config.temporal_window_frames)

        # Previous frame for camera movement detection
        self._prev_gray: Optional[np.ndarray] = None

        self.logger.info("Color anomaly and motion detection orchestrator initialized")

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

        self.logger.info("Orchestrator configuration updated")

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

                region_hsv = frame_hsv[y:y+h, x:x+w]
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
        is_camera_moving = False
        if config.pause_on_camera_movement and self._prev_gray is not None:
            is_camera_moving = self.motion_service.check_camera_movement(processing_gray, config)

        # Calculate early stopping limit
        max_to_detect = config.max_detections_to_render * 2 if config.max_detections_to_render > 0 else 0

        # Motion detection
        motion_detections = []
        motion_start = time.perf_counter()
        if config.enable_motion and not is_camera_moving:
            motion_detections = self.motion_service.detect(processing_gray, config, max_to_detect)
        timings.motion_detection_ms = (time.perf_counter() - motion_start) * 1000

        # Color detection
        color_detections = []
        color_start = time.perf_counter()
        if config.enable_color_quantization:
            color_detections = self.color_service.detect(processing_frame, config, max_to_detect)
        timings.color_detection_ms = (time.perf_counter() - color_start) * 1000

        timings.detection_ms = (time.perf_counter() - detection_start) * 1000

        # Store current frame for next camera movement check
        self._prev_gray = processing_gray.copy()

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
        detections = self._apply_color_exclusion_filter(detections, processing_frame)

        timings.fusion_ms = (time.perf_counter() - fusion_start) * 1000

        # Rendering
        render_start = time.perf_counter()

        # Choose rendering resolution
        if config.render_at_processing_res:
            render_frame = processing_frame.copy()
            render_inverse_scale = 1.0
        else:
            render_frame = working_frame.copy()
            render_inverse_scale = 1.0 / scale_factor if scale_factor > 0.0 else 1.0

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
                x_scaled = int(x * render_inverse_scale)
                y_scaled = int(y * render_inverse_scale)
                w_scaled = int(w * render_inverse_scale)
                h_scaled = int(h * render_inverse_scale)

                cx_scaled = int(detection.centroid[0] * render_inverse_scale)
                cy_scaled = int(detection.centroid[1] * render_inverse_scale)

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
                    scaled_contour = (detection.contour * render_inverse_scale).astype(np.int32)
                    cv2.drawContours(annotated_frame, [scaled_contour], -1, color, 2)

                if config.render_shape == 0:  # Box
                    cv2.rectangle(annotated_frame, (x_scaled, y_scaled),
                                  (x_scaled + w_scaled, y_scaled + h_scaled), color, 2)
                    cv2.circle(annotated_frame, (cx_scaled, cy_scaled), 3, color, -1)
                elif config.render_shape == 1:  # Circle
                    if detection.contour is not None:
                        scaled_contour = (detection.contour * render_inverse_scale).astype(np.int32)
                        (_, _), contour_radius = cv2.minEnclosingCircle(scaled_contour)
                        radius = max(5, int(contour_radius * 1.5))
                    else:
                        base_radius = np.sqrt(detection.area) * render_inverse_scale / 2
                        radius = max(5, int(base_radius * 1.5))
                    cv2.circle(annotated_frame, (cx_scaled, cy_scaled), radius, color, 2)
                elif config.render_shape == 2:  # Dot
                    cv2.circle(annotated_frame, (cx_scaled, cy_scaled), 5, color, -1)

                if config.render_text:
                    if detection.detection_type == 'fused':
                        label = f"#{i+1} FUSED {int(detection.area)}px"
                    elif detection.detection_type == 'color_anomaly':
                        label = f"#{i+1} COLOR {int(detection.area)}px"
                    else:
                        label = f"#{i+1} MOTION {int(detection.area)}px"
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
                        (w//2 - 190, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2, cv2.LINE_AA)
            cv2.putText(annotated_frame, "Motion detection paused (color still active)",
                        (w//2 - 210, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        # Add timing overlay
        if config.show_timing_overlay:
            annotated_frame = self.timing_renderer.render(annotated_frame, self.metrics, timings)

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
        processing_resolution = (processing_frame.shape[1], processing_frame.shape[0])
        original_resolution = (working_frame.shape[1], working_frame.shape[0])
        for detection in detections:
            if detection.metadata is None:
                detection.metadata = {}
            detection.metadata.setdefault('processing_resolution', processing_resolution)
            detection.metadata.setdefault('original_resolution', original_resolution)

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
        self.motion_service.reset()
        self.logger.info("Performance metrics reset")

