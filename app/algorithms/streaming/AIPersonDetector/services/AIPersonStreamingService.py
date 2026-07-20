"""Streaming AI person detector service backed by ONNX Runtime."""

from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional, Tuple
import time
from collections import deque
import cv2
import numpy as np
import sys
import os

from PySide6.QtCore import QObject, Signal

from core.services.LoggerService import LoggerService
from core.services.streaming.MaskManager import MaskManager
from core.services.streaming.StreamingUtils import StageTimings

try:
    import onnxruntime as ort
    ONNXRUNTIME_AVAILABLE = True
except Exception:  # pragma: no cover - environment dependent
    ort = None
    ONNXRUNTIME_AVAILABLE = False


@dataclass
class AIPersonStreamingConfig:
    """Configuration for streaming AI person detection."""
    confidence_threshold: float = 0.50
    cpu_only: bool = False
    high_resolution_model: bool = False
    render_text: bool = True
    max_detections_to_render: int = 25
    processing_width: Optional[int] = 1280
    processing_height: Optional[int] = 720
    target_fps: Optional[int] = None
    render_shape: int = 0  # 0=Box, 1=Circle, 2=Dot, 3=Off
    mask_enabled: bool = False
    frame_mask_enabled: bool = False
    image_mask_enabled: bool = False
    frame_buffer_pixels: int = 50
    mask_image_path: Optional[str] = None
    show_mask_overlay: bool = False
    enable_temporal_voting: bool = False
    temporal_window_frames: int = 5
    temporal_threshold_frames: int = 3
    enable_aspect_ratio_filter: bool = False
    min_aspect_ratio: float = 0.2
    max_aspect_ratio: float = 5.0
    nms_iou_threshold: float = 0.45
    # Default ON for SAR. The old default whole-frame stretch-resized to a square model
    # input, which crushed targets (~0.33x) and aspect-distorted them. Tiling preserves
    # per-target resolution; letterbox preserves aspect. Frames larger than the tile are
    # tiled at full source resolution; smaller frames take the (now letterboxed) single pass.
    enable_tiled_inference: bool = True
    tile_size_px: Optional[int] = None
    tile_overlap_ratio: float = 0.20
    use_letterbox_preprocessing: bool = True
    # Backward compatibility aliases for older persisted configs/tests.
    show_labels: Optional[bool] = None
    max_detections: Optional[int] = None

    def __post_init__(self):
        """Normalize legacy sentinel fields and aliases."""
        if self.show_labels is not None:
            self.render_text = bool(self.show_labels)
        if self.max_detections is not None:
            self.max_detections_to_render = int(self.max_detections)

        if self.processing_width is not None:
            self.processing_width = int(self.processing_width)
            if self.processing_width <= 0 or self.processing_width >= 99999:
                self.processing_width = None
        if self.processing_height is not None:
            self.processing_height = int(self.processing_height)
            if self.processing_height <= 0 or self.processing_height >= 99999:
                self.processing_height = None
        if self.target_fps is not None:
            self.target_fps = int(self.target_fps)
            if self.target_fps <= 0:
                self.target_fps = None

        self.max_detections_to_render = max(0, int(self.max_detections_to_render))


@dataclass
class AIPersonDetection:
    """Container for a person detection."""
    bbox: Tuple[int, int, int, int]
    centroid: Tuple[int, int]
    area: float
    confidence: float
    timestamp: float
    detection_type: str = "person"
    metadata: Dict = field(default_factory=dict)


class AIPersonStreamingService(QObject):
    """Run ONNX person detection on streaming frames."""

    performanceUpdate = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LoggerService()
        self._config = AIPersonStreamingConfig()
        self._config_lock = Lock()
        self._mask_manager = MaskManager()
        self._session_cache = {}
        self._timings: List[float] = []
        self._max_timing_samples = 60
        self._detection_history = deque(maxlen=5)
        self._tile_fps_samples = deque(maxlen=30)
        self._last_processed_time = 0.0
        self._last_output_detections: List[AIPersonDetection] = []
        self._last_inference_used_tiles = False
        self._tiled_inference_fallback_active = False

    def update_config(self, config: AIPersonStreamingConfig):
        """Update detector configuration thread-safely."""
        with self._config_lock:
            self._config = config

    def get_config(self) -> AIPersonStreamingConfig:
        """Return current immutable config snapshot."""
        with self._config_lock:
            return AIPersonStreamingConfig(**self._config.__dict__)

    def process_frame(self, frame: np.ndarray, timestamp: float, render_detections: bool = True):
        """Process one frame and return annotated frame, detections, timings."""
        timings = StageTimings()
        total_start = time.perf_counter()
        try:
            if frame is None or frame.size == 0:
                timings.total_ms = (time.perf_counter() - total_start) * 1000.0
                return frame, [], timings

            cfg = self.get_config()
            if self._should_skip_frame(cfg):
                timings.was_skipped = True
                timings.total_ms = (time.perf_counter() - total_start) * 1000.0
                return frame, list(self._last_output_detections), timings

            if not ONNXRUNTIME_AVAILABLE:
                timings.total_ms = (time.perf_counter() - total_start) * 1000.0
                return frame, [], timings

            pre_start = time.perf_counter()
            if self._should_use_tiled_inference(frame, cfg):
                processing_frame, scale_x, scale_y = frame, 1.0, 1.0
            else:
                processing_frame, scale_x, scale_y = self._prepare_processing_frame(frame, cfg)
            timings.preprocessing_ms = (time.perf_counter() - pre_start) * 1000.0

            detect_start = time.perf_counter()
            raw_boxes = self._infer(processing_frame, cfg)
            timings.detection_ms = (time.perf_counter() - detect_start) * 1000.0

            detections = self._to_detection_objects(
                raw_boxes=raw_boxes,
                scale_x=scale_x,
                scale_y=scale_y,
                timestamp=timestamp,
                confidence_threshold=cfg.confidence_threshold,
                max_detections=0,
            )
            detections = self._apply_mask_filter(detections, frame.shape, cfg)
            detections = self._apply_aspect_ratio_filter(detections, cfg)
            detections = self._apply_temporal_voting(detections, cfg)
            if cfg.max_detections_to_render > 0:
                detections = detections[:cfg.max_detections_to_render]

            annotated = frame
            if render_detections or cfg.show_mask_overlay:
                render_start = time.perf_counter()
                annotated = self._annotate_frame(frame, detections, cfg)
                timings.render_ms = (time.perf_counter() - render_start) * 1000.0

            timings.total_ms = (time.perf_counter() - total_start) * 1000.0
            self._record_performance(timings.total_ms, len(detections))
            self._update_tiled_inference_fallback(timings.total_ms)
            self._last_output_detections = list(detections)
            return annotated, detections, timings
        except Exception as exc:
            self.logger.error(f"AIPerson streaming frame processing failed: {exc}")
            timings.total_ms = (time.perf_counter() - total_start) * 1000.0
            return frame, [], timings

    def _prepare_processing_frame(self, frame: np.ndarray, cfg: AIPersonStreamingConfig):
        """Resize frame for detection if processing resolution is configured."""
        src_h, src_w = frame.shape[:2]
        target_w = int(cfg.processing_width) if cfg.processing_width is not None else src_w
        target_h = int(cfg.processing_height) if cfg.processing_height is not None else src_h

        if cfg.processing_width is None or cfg.processing_height is None:
            return frame, 1.0, 1.0

        target_w = max(10, min(target_w, src_w))
        target_h = max(10, min(target_h, src_h))
        if target_w == src_w and target_h == src_h:
            return frame, 1.0, 1.0

        resized = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_AREA)
        scale_x = float(src_w) / float(target_w)
        scale_y = float(src_h) / float(target_h)
        return resized, scale_x, scale_y

    def _infer(self, frame_bgr: np.ndarray, cfg: AIPersonStreamingConfig):
        """Run ONNX inference and return raw boxes in frame coordinates."""
        self._last_inference_used_tiles = False
        if self._should_use_tiled_inference(frame_bgr, cfg):
            self._last_inference_used_tiles = True
            tile_size = self._resolve_tile_size(cfg)
            overlap_ratio = max(0.0, min(float(cfg.tile_overlap_ratio), 0.5))
            return self._infer_tiled(frame_bgr, cfg, tile_size, overlap_ratio)
        return self._apply_nms(self._infer_single_frame(frame_bgr, cfg), cfg.nms_iou_threshold)

    def _should_skip_frame(self, cfg: AIPersonStreamingConfig) -> bool:
        """Skip work when the algorithm-specific FPS cap would be exceeded."""
        if cfg.target_fps is None or cfg.target_fps <= 0:
            return False
        now = time.perf_counter()
        if self._last_processed_time <= 0.0:
            self._last_processed_time = now
            return False
        interval = 1.0 / float(cfg.target_fps)
        if now - self._last_processed_time < interval:
            return True
        self._last_processed_time = now
        return False

    def _resolve_tile_size(self, cfg: AIPersonStreamingConfig) -> int:
        """Resolve tile size based on model selection and optional override."""
        if cfg.tile_size_px is not None and cfg.tile_size_px > 0:
            return int(cfg.tile_size_px)
        return 1536 if cfg.high_resolution_model else 960

    def _should_use_tiled_inference(self, frame_bgr: np.ndarray, cfg: AIPersonStreamingConfig) -> bool:
        """Return whether SAR tiled inference should run for this frame."""
        if not cfg.enable_tiled_inference or self._tiled_inference_fallback_active:
            return False
        tile_size = self._resolve_tile_size(cfg)
        frame_h, frame_w = frame_bgr.shape[:2]
        return frame_w > tile_size or frame_h > tile_size

    def _infer_tiled(
        self,
        frame_bgr: np.ndarray,
        cfg: AIPersonStreamingConfig,
        tile_size: int,
        overlap_ratio: float,
    ) -> List[Tuple[int, int, int, int, float]]:
        """Run tiled inference and merge results in frame coordinates."""
        frame_h, frame_w = frame_bgr.shape[:2]
        step = max(1, int(round(tile_size * (1.0 - overlap_ratio))))
        x_positions = self._build_tile_positions(frame_w, tile_size, step)
        y_positions = self._build_tile_positions(frame_h, tile_size, step)

        raw_boxes: List[Tuple[int, int, int, int, float]] = []
        for y in y_positions:
            for x in x_positions:
                tile = frame_bgr[y:min(y + tile_size, frame_h), x:min(x + tile_size, frame_w)]
                raw_boxes.extend(self._infer_single_frame(tile, cfg, offset=(x, y)))
        return self._apply_nms(raw_boxes, cfg.nms_iou_threshold)

    @staticmethod
    def _build_tile_positions(length: int, tile_size: int, step: int) -> List[int]:
        """Build tile origins that fully cover one axis."""
        if length <= tile_size:
            return [0]
        positions = list(range(0, max(1, length - tile_size + 1), step))
        if positions[-1] != length - tile_size:
            positions.append(length - tile_size)
        return positions

    def _infer_single_frame(
        self,
        frame_bgr: np.ndarray,
        cfg: AIPersonStreamingConfig,
        offset: Tuple[int, int] = (0, 0),
    ) -> List[Tuple[int, int, int, int, float]]:
        """Run ONNX inference against a single full-frame or tile crop."""
        session = self._get_session(cfg)
        input_name = session.get_inputs()[0].name
        model_size = 1024 if cfg.high_resolution_model else 640

        input_tensor, scale_x, scale_y, pad_x, pad_y = self._prepare_model_input(frame_bgr, model_size, cfg)
        predictions = session.run(None, {input_name: input_tensor})[0]
        if getattr(predictions, "ndim", 0) == 3:
            predictions = predictions[0]

        frame_h, frame_w = frame_bgr.shape[:2]
        offset_x, offset_y = offset
        raw_boxes: List[Tuple[int, int, int, int, float]] = []
        for pred in predictions:
            if len(pred) < 6:
                continue
            x1, y1, x2, y2, conf, cls = pred[:6]
            if int(cls) != 0:
                continue

            bx1 = int(round((float(x1) - pad_x) / scale_x))
            by1 = int(round((float(y1) - pad_y) / scale_y))
            bx2 = int(round((float(x2) - pad_x) / scale_x))
            by2 = int(round((float(y2) - pad_y) / scale_y))

            bx1 = max(0, min(frame_w, bx1))
            by1 = max(0, min(frame_h, by1))
            bx2 = max(0, min(frame_w, bx2))
            by2 = max(0, min(frame_h, by2))
            if bx2 <= bx1 or by2 <= by1:
                continue

            raw_boxes.append(
                (
                    bx1 + offset_x,
                    by1 + offset_y,
                    bx2 + offset_x,
                    by2 + offset_y,
                    float(conf),
                )
            )
        return raw_boxes

    def _prepare_model_input(
        self,
        frame_bgr: np.ndarray,
        model_size: int,
        cfg: AIPersonStreamingConfig,
    ) -> Tuple[np.ndarray, float, float, float, float]:
        """Prepare a square ONNX input using aspect-preserving letterbox by default."""
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        frame_h, frame_w = rgb.shape[:2]

        if not cfg.use_letterbox_preprocessing:
            resized = cv2.resize(rgb, (model_size, model_size), interpolation=cv2.INTER_LINEAR)
            input_tensor = resized.astype(np.float32) / 255.0
            input_tensor = np.transpose(input_tensor, (2, 0, 1))
            input_tensor = np.expand_dims(input_tensor, axis=0)
            scale_x = model_size / max(frame_w, 1)
            scale_y = model_size / max(frame_h, 1)
            return input_tensor, float(scale_x), float(scale_y), 0.0, 0.0

        scale = min(model_size / max(frame_w, 1), model_size / max(frame_h, 1))
        resized_w = max(1, int(round(frame_w * scale)))
        resized_h = max(1, int(round(frame_h * scale)))
        resized = cv2.resize(rgb, (resized_w, resized_h), interpolation=cv2.INTER_LINEAR)

        canvas = np.zeros((model_size, model_size, 3), dtype=np.uint8)
        pad_x = (model_size - resized_w) // 2
        pad_y = (model_size - resized_h) // 2
        canvas[pad_y:pad_y + resized_h, pad_x:pad_x + resized_w] = resized

        input_tensor = canvas.astype(np.float32) / 255.0
        input_tensor = np.transpose(input_tensor, (2, 0, 1))
        input_tensor = np.expand_dims(input_tensor, axis=0)
        return input_tensor, float(scale), float(scale), float(pad_x), float(pad_y)

    def _apply_nms(
        self,
        raw_boxes: List[Tuple[int, int, int, int, float]],
        iou_threshold: float,
    ) -> List[Tuple[int, int, int, int, float]]:
        """Apply IoU-based non-maximum suppression."""
        if not raw_boxes:
            return []
        sorted_boxes = sorted(raw_boxes, key=lambda item: float(item[4]), reverse=True)
        kept: List[Tuple[int, int, int, int, float]] = []
        while sorted_boxes:
            best = sorted_boxes.pop(0)
            kept.append(best)
            sorted_boxes = [
                candidate for candidate in sorted_boxes
                if self._raw_box_iou(best, candidate) < iou_threshold
            ]
        return kept

    @staticmethod
    def _raw_box_iou(
        box_a: Tuple[int, int, int, int, float],
        box_b: Tuple[int, int, int, int, float],
    ) -> float:
        """Compute IoU between two raw x1/y1/x2/y2 boxes."""
        ax1, ay1, ax2, ay2, _ = box_a
        bx1, by1, bx2, by2, _ = box_b
        inter_x1 = max(ax1, bx1)
        inter_y1 = max(ay1, by1)
        inter_x2 = min(ax2, bx2)
        inter_y2 = min(ay2, by2)
        if inter_x2 <= inter_x1 or inter_y2 <= inter_y1:
            return 0.0
        inter_area = float((inter_x2 - inter_x1) * (inter_y2 - inter_y1))
        area_a = float(max(0, ax2 - ax1) * max(0, ay2 - ay1))
        area_b = float(max(0, bx2 - bx1) * max(0, by2 - by1))
        denominator = area_a + area_b - inter_area
        if denominator <= 0.0:
            return 0.0
        return inter_area / denominator

    def _to_detection_objects(
        self,
        raw_boxes: List[Tuple[int, int, int, int, float]],
        scale_x: float,
        scale_y: float,
        timestamp: float,
        confidence_threshold: float,
        max_detections: int
    ) -> List[AIPersonDetection]:
        """Convert raw boxes to streaming detection objects."""
        detections: List[AIPersonDetection] = []
        for x1, y1, x2, y2, conf in raw_boxes:
            if conf < confidence_threshold:
                continue

            sx1 = int(x1 * scale_x)
            sy1 = int(y1 * scale_y)
            sx2 = int(x2 * scale_x)
            sy2 = int(y2 * scale_y)
            w = max(0, sx2 - sx1)
            h = max(0, sy2 - sy1)
            if w == 0 or h == 0:
                continue

            detections.append(
                AIPersonDetection(
                    bbox=(sx1, sy1, w, h),
                    centroid=(sx1 + (w // 2), sy1 + (h // 2)),
                    area=float(w * h),
                    confidence=float(conf),
                    timestamp=float(timestamp),
                    detection_type="person",
                    metadata={"model": "onnx_ai_person"}
                )
            )

        detections.sort(key=lambda d: d.confidence, reverse=True)
        if max_detections > 0:
            detections = detections[:max_detections]
        return detections

    def _apply_mask_filter(
        self,
        detections: List[AIPersonDetection],
        frame_shape: Tuple[int, int, int],
        cfg: AIPersonStreamingConfig,
    ) -> List[AIPersonDetection]:
        """Reject detections outside the configured processing mask."""
        if not cfg.mask_enabled:
            return detections

        original_resolution = (int(frame_shape[1]), int(frame_shape[0]))
        mask = self._mask_manager.get_mask(
            {
                "mask_enabled": cfg.mask_enabled,
                "frame_mask_enabled": cfg.frame_mask_enabled,
                "image_mask_enabled": cfg.image_mask_enabled,
                "frame_buffer_pixels": cfg.frame_buffer_pixels,
                "mask_image_path": cfg.mask_image_path,
                "show_mask_overlay": cfg.show_mask_overlay,
            },
            original_resolution=original_resolution,
            processing_resolution=None,
        )
        if mask is None:
            return detections

        filtered: List[AIPersonDetection] = []
        for detection in detections:
            cx, cy = detection.centroid
            if 0 <= cx < mask.shape[1] and 0 <= cy < mask.shape[0] and mask[cy, cx] > 0:
                filtered.append(detection)
        return filtered

    def _apply_aspect_ratio_filter(
        self,
        detections: List[AIPersonDetection],
        cfg: AIPersonStreamingConfig,
    ) -> List[AIPersonDetection]:
        """Filter implausible person boxes by aspect ratio."""
        if not cfg.enable_aspect_ratio_filter:
            return detections
        filtered: List[AIPersonDetection] = []
        for detection in detections:
            _, _, width, height = detection.bbox
            if width <= 0 or height <= 0:
                continue
            aspect_ratio = float(width) / float(height)
            if cfg.min_aspect_ratio <= aspect_ratio <= cfg.max_aspect_ratio:
                filtered.append(detection)
        return filtered

    def _apply_temporal_voting(
        self,
        detections: List[AIPersonDetection],
        cfg: AIPersonStreamingConfig,
    ) -> List[AIPersonDetection]:
        """Require detections to persist across a configurable temporal window."""
        if not cfg.enable_temporal_voting:
            self._detection_history.append(list(detections))
            return detections

        recent_frames = list(self._detection_history)
        recent_frames.append(list(detections))
        if len(recent_frames) > cfg.temporal_window_frames:
            recent_frames = recent_frames[-cfg.temporal_window_frames:]

        stabilized: List[AIPersonDetection] = []
        for detection in detections:
            matched_cluster: List[AIPersonDetection] = []
            matched_frames = 0
            for frame_detections in recent_frames:
                best_match = None
                best_iou = 0.0
                for candidate in frame_detections:
                    iou = self._bbox_iou(detection.bbox, candidate.bbox)
                    if iou >= 0.3 and iou > best_iou:
                        best_match = candidate
                        best_iou = iou
                if best_match is not None:
                    matched_cluster.append(best_match)
                    matched_frames += 1

            if matched_frames >= cfg.temporal_threshold_frames and matched_cluster:
                stabilized.append(max(matched_cluster, key=lambda item: float(item.confidence)))

        self._detection_history.append(list(detections))
        stabilized.sort(key=lambda detection: float(detection.confidence), reverse=True)
        return stabilized

    @staticmethod
    def _bbox_iou(bbox_a: Tuple[int, int, int, int], bbox_b: Tuple[int, int, int, int]) -> float:
        """Compute IoU for x/y/w/h bounding boxes."""
        ax, ay, aw, ah = bbox_a
        bx, by, bw, bh = bbox_b
        ax2 = ax + aw
        ay2 = ay + ah
        bx2 = bx + bw
        by2 = by + bh
        inter_x1 = max(ax, bx)
        inter_y1 = max(ay, by)
        inter_x2 = min(ax2, bx2)
        inter_y2 = min(ay2, by2)
        if inter_x2 <= inter_x1 or inter_y2 <= inter_y1:
            return 0.0
        inter_area = float((inter_x2 - inter_x1) * (inter_y2 - inter_y1))
        area_a = float(max(0, aw) * max(0, ah))
        area_b = float(max(0, bw) * max(0, bh))
        denominator = area_a + area_b - inter_area
        if denominator <= 0.0:
            return 0.0
        return inter_area / denominator

    def _annotate_frame(self, frame: np.ndarray, detections: List[AIPersonDetection], cfg: AIPersonStreamingConfig):
        """Render detections to an output frame."""
        annotated = frame.copy()
        if cfg.mask_enabled and cfg.show_mask_overlay:
            annotated = self._draw_mask_overlay(annotated, cfg)
        for det in detections:
            x, y, w, h = det.bbox

            if cfg.render_shape == 0:
                cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 200, 255), 2)
                cv2.circle(annotated, det.centroid, 2, (0, 200, 255), -1)
            elif cfg.render_shape == 1:
                radius = max(4, int(max(w, h) * 0.5))
                cv2.circle(annotated, det.centroid, radius, (0, 200, 255), 2)
            elif cfg.render_shape == 2:
                cv2.circle(annotated, det.centroid, 4, (0, 200, 255), -1)

            if cfg.render_text:
                label = f"Person {det.confidence:.2f}"
                cv2.putText(
                    annotated,
                    label,
                    (det.centroid[0] - 40, max(16, y - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 200, 255),
                    1,
                    cv2.LINE_AA
                )
        return annotated

    def _draw_mask_overlay(self, frame: np.ndarray, cfg: AIPersonStreamingConfig) -> np.ndarray:
        """Draw the active processing mask on the rendered frame."""
        render_resolution = (int(frame.shape[1]), int(frame.shape[0]))
        mask = self._mask_manager.get_mask_for_rendering(
            {
                "mask_enabled": cfg.mask_enabled,
                "frame_mask_enabled": cfg.frame_mask_enabled,
                "image_mask_enabled": cfg.image_mask_enabled,
                "frame_buffer_pixels": cfg.frame_buffer_pixels,
                "mask_image_path": cfg.mask_image_path,
                "show_mask_overlay": cfg.show_mask_overlay,
            },
            render_resolution=render_resolution,
            original_resolution=render_resolution,
        )
        if mask is None:
            return frame

        overlay = frame.copy()
        excluded = mask == 0
        overlay[excluded] = (0.5 * overlay[excluded]).astype(np.uint8)
        frame = cv2.addWeighted(frame, 0.75, overlay, 0.25, 0.0)

        bounds = self._mask_manager.get_frame_bounds(
            {
                "mask_enabled": cfg.mask_enabled,
                "frame_mask_enabled": cfg.frame_mask_enabled,
                "frame_buffer_pixels": cfg.frame_buffer_pixels,
            },
            resolution=render_resolution,
            scale_factor=1.0,
        )
        if bounds is not None:
            x1, y1, x2, y2 = bounds
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 1)
        return frame

    def _record_performance(self, total_ms: float, detection_count: int):
        """Emit basic performance metrics."""
        self._timings.append(total_ms)
        if len(self._timings) > self._max_timing_samples:
            self._timings.pop(0)
        avg_ms = float(np.mean(self._timings)) if self._timings else 0.0
        fps = (1000.0 / avg_ms) if avg_ms > 0 else 0.0
        self.performanceUpdate.emit(
            {
                "fps": fps,
                "avg_processing_time_ms": avg_ms,
                "detections_count": detection_count,
                "tiled_inference_fallback": self._tiled_inference_fallback_active,
            }
        )

    def _update_tiled_inference_fallback(self, total_ms: float) -> None:
        """Disable tiled inference automatically when it becomes too slow."""
        if not self._last_inference_used_tiles:
            self._tile_fps_samples.clear()
            return

        frame_fps = (1000.0 / total_ms) if total_ms > 0 else 0.0
        self._tile_fps_samples.append(frame_fps)
        if len(self._tile_fps_samples) < self._tile_fps_samples.maxlen:
            return

        avg_tile_fps = float(np.mean(self._tile_fps_samples)) if self._tile_fps_samples else 0.0
        if avg_tile_fps < 8.0:
            self._tiled_inference_fallback_active = True

    def _get_session(self, cfg: AIPersonStreamingConfig):
        """Get cached ONNX session for current model/provider settings."""
        model_path = self._resolve_model_path(cfg)
        cache_key = (model_path, bool(cfg.cpu_only))
        cached = self._session_cache.get(cache_key)
        if cached is not None:
            return cached

        if not ONNXRUNTIME_AVAILABLE or ort is None:
            raise RuntimeError("onnxruntime is not available")

        providers = ["CPUExecutionProvider"] if cfg.cpu_only else ["DmlExecutionProvider", "CPUExecutionProvider"]
        session_options = ort.SessionOptions()
        session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        session_options.enable_mem_pattern = False
        session_options.enable_profiling = False
        session_options.intra_op_num_threads = 1

        try:
            session = ort.InferenceSession(model_path, sess_options=session_options, providers=providers)
        except Exception:
            session = ort.InferenceSession(model_path, sess_options=session_options, providers=["CPUExecutionProvider"])

        self._session_cache[cache_key] = session
        return session

    def _resolve_model_path(self, cfg: AIPersonStreamingConfig) -> str:
        """Resolve ONNX model path for source and frozen builds."""
        model_name = "ai_person_model_V3_1024.onnx" if cfg.high_resolution_model else "ai_person_model_V3_640.onnx"
        if getattr(sys, "frozen", False):
            return os.path.join(
                sys._MEIPASS,
                "algorithms",
                "models",
                "AIPersonDetector",
                model_name
            )

        model_path = (
            Path(__file__).resolve().parents[3]
            / "models"
            / "AIPersonDetector"
            / model_name
        )
        return str(model_path)

    def reset(self) -> None:
        """Reset rolling runtime state while keeping sessions cached."""
        self._timings.clear()
        self._detection_history.clear()
        self._tile_fps_samples.clear()
        self._last_output_detections = []
        self._last_processed_time = 0.0
        self._last_inference_used_tiles = False
        self._tiled_inference_fallback_active = False

    def cleanup(self) -> None:
        """Release in-memory runtime state and ONNX session cache."""
        self.reset()
        self._session_cache.clear()
