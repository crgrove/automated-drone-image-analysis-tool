"""Streaming AI Person Detector controller."""

from typing import Any, Dict, List, Optional
import numpy as np

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QVBoxLayout

from core.controllers.streaming.base import StreamAlgorithmController
from core.services.LoggerService import LoggerService
from core.services.streaming import StreamAlgorithmCapabilities
from core.services.streaming.adapters import AIPersonStreamAdapter
from helpers.TranslationMixin import TranslationMixin
from algorithms.streaming.AIPersonDetector.services import (
    AIPersonStreamingService,
    AIPersonStreamingConfig,
)
from algorithms.streaming.AIPersonDetector.views import AIPersonDetectorControlWidget


class AIPersonDetectorController(TranslationMixin, StreamAlgorithmController):
    """Controller for streaming ONNX person detection."""

    _CAPABILITIES = StreamAlgorithmCapabilities(
        supports_mask_controls=True,
        supports_render_at_processing_resolution=False,
        supports_render_contours=False,
        supports_use_detection_color=False,
        supports_temporal_voting=True,
        supports_aspect_ratio_filter=True,
        supports_detection_clustering=False,
    )

    def __init__(self, algorithm_config: Dict[str, Any], theme: str, parent=None):
        super().__init__(algorithm_config, theme, parent)
        self.logger = LoggerService()
        self.provides_custom_rendering = False
        # Source type ("File"/"RTMP Stream"/"HDMI Capture") threaded from the wizard via
        # set_config; used to auto-select the 1024 model for file sources. None until applied.
        self._stream_type: Optional[str] = None

        # IMPORTANT: no parent so this QObject can move to the worker thread.
        self.person_detector = AIPersonStreamingService(parent=None)
        self.stream_service = AIPersonStreamAdapter(self.person_detector)
        self.person_detector.performanceUpdate.connect(self._on_performance_update)

        if hasattr(self, "control_widget"):
            self._on_config_changed(self.control_widget.get_config())

        self.detection_count = 0

    def setup_ui(self):
        """Build controls for the streaming algorithm."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        self.control_widget = AIPersonDetectorControlWidget(capabilities=self.get_stream_capabilities())
        self.control_widget.configChanged.connect(self._on_config_changed)
        layout.addWidget(self.control_widget)

    def get_stream_capabilities(self) -> StreamAlgorithmCapabilities:
        """Declare which shared streaming controls are supported by this algorithm."""
        return self._CAPABILITIES

    def process_frame(self, frame: np.ndarray, timestamp: float) -> List[Dict]:
        """Process frame and emit detections plus rendered frame."""
        try:
            result = self.stream_service.process_frame(frame, timestamp)
            detection_dicts = result.detection_dicts()
            self.detection_count += len(detection_dicts)
            self.detectionsReady.emit(detection_dicts)
            self.frameProcessed.emit(result.rendered_frame if result.rendered_frame is not None else frame.copy())
            return detection_dicts
        except Exception as exc:
            self.logger.error(f"AIPersonDetectorController frame processing failed: {exc}")
            self.frameProcessed.emit(frame.copy())
            return []

    @Slot(dict)
    def _on_config_changed(self, config: Dict[str, Any]):
        """Apply widget config to service."""
        service_config = self._to_service_config(config)
        self.person_detector.update_config(service_config)
        self._emit_config_changed()

    @Slot(dict)
    def _on_performance_update(self, metrics: dict):
        """Forward performance information to status line."""
        fps = float(metrics.get("fps", 0.0))
        processing_ms = float(metrics.get("avg_processing_time_ms", 0.0))
        status = self.tr("FPS: {fps} | Processing: {ms}ms").format(
            fps=f"{fps:.1f}",
            ms=f"{processing_ms:.1f}",
        )
        if metrics.get("tiled_inference_fallback"):
            status = self.tr("{status} | Tile fallback active").format(status=status)
        self._emit_status(status)

    def _to_service_config(self, config: Dict[str, Any]) -> AIPersonStreamingConfig:
        """Convert UI config dictionary to service config dataclass."""
        if "confidence_threshold" in config:
            confidence = float(config.get("confidence_threshold", 0.5))
        else:
            confidence_percent = float(config.get("person_detector_confidence", 50))
            confidence = confidence_percent / 100.0

        confidence = max(0.01, min(1.0, confidence))
        render_shape = int(config.get("render_shape", 0))
        max_detections = self._normalize_optional_positive_int(
            config.get("max_detections_to_render", config.get("max_detections", 25))
        ) or 25
        render_text = bool(config.get("render_text", config.get("show_labels", True)))
        processing_width = self._normalize_optional_positive_int(config.get("processing_width"))
        processing_height = self._normalize_optional_positive_int(config.get("processing_height"))
        target_fps = self._normalize_optional_positive_int(config.get("target_fps"))

        cpu_only = bool(config.get("cpu_only", False))
        # Auto-engage the 1024 model on GPU for the detail-first usecases: a file source
        # (high-res recording for deep analysis, threaded in as stream_type) or an explicit
        # full/native processing resolution (Input tab -> "Original", processing_width=None).
        # Downscaled live feeds (720P/1080P) keep the faster 640 model. The explicit
        # "Use 1024 model" checkbox still forces it on.
        is_file_source = str(config.get("stream_type") or self._stream_type or "").strip().lower() == "file"
        high_resolution_model = bool(config.get("high_resolution_model", False)) or (
            not cpu_only and (is_file_source or processing_width is None)
        )

        return AIPersonStreamingConfig(
            confidence_threshold=confidence,
            cpu_only=cpu_only,
            high_resolution_model=high_resolution_model,
            render_text=render_text,
            max_detections_to_render=max_detections,
            processing_width=processing_width,
            processing_height=processing_height,
            target_fps=target_fps,
            render_shape=max(0, min(3, render_shape)),
            mask_enabled=bool(config.get("mask_enabled", False)),
            frame_mask_enabled=bool(config.get("frame_mask_enabled", False)),
            image_mask_enabled=bool(config.get("image_mask_enabled", False)),
            frame_buffer_pixels=int(config.get("frame_buffer_pixels", 50)),
            mask_image_path=config.get("mask_image_path"),
            show_mask_overlay=bool(config.get("show_mask_overlay", False)),
            enable_temporal_voting=bool(config.get("enable_temporal_voting", False)),
            temporal_window_frames=int(config.get("temporal_window_frames", 5)),
            temporal_threshold_frames=int(config.get("temporal_threshold_frames", 3)),
            enable_aspect_ratio_filter=bool(config.get("enable_aspect_ratio_filter", False)),
            min_aspect_ratio=float(config.get("min_aspect_ratio", 0.2)),
            max_aspect_ratio=float(config.get("max_aspect_ratio", 5.0)),
        )

    @staticmethod
    def _normalize_optional_positive_int(value: Any) -> Optional[int]:
        """Normalize legacy sentinel and source/native values to Optional[int]."""
        if value is None:
            return None
        try:
            normalized = int(value)
        except (TypeError, ValueError):
            return None
        if normalized <= 0 or normalized >= 99999:
            return None
        return normalized

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration from controls."""
        config = dict(self.control_widget.get_config())
        for unsupported_key in (
            "render_at_processing_res",
            "render_contours",
            "use_detection_color_for_rendering",
            "enable_detection_clustering",
            "clustering_distance",
        ):
            config.pop(unsupported_key, None)
        return config

    def set_config(self, config: Dict[str, Any]):
        """Apply configuration into controls/service."""
        filtered_config = dict(config or {})
        # Source type isn't a widget control, so it would be lost in the control-widget
        # round-trip below; capture it for model auto-selection in _to_service_config.
        if filtered_config.get("stream_type") is not None:
            self._stream_type = filtered_config.pop("stream_type")
        for unsupported_key in (
            "render_at_processing_res",
            "render_contours",
            "use_detection_color_for_rendering",
            "enable_detection_clustering",
            "clustering_distance",
        ):
            filtered_config.pop(unsupported_key, None)
        self.control_widget.set_config(filtered_config)
        self._on_config_changed(self.control_widget.get_config())

    def get_stream_service(self):
        """Return normalized streaming service used by worker processing."""
        return self.stream_service

    def get_stats(self) -> Dict[str, str]:
        """Get algorithm-specific statistics."""
        return {
            "Total Detections": str(self.detection_count)
        }

    def reset(self):
        """Reset algorithm state for a new stream session."""
        self.person_detector.reset()
        self.detection_count = 0

    def cleanup(self):
        """Release algorithm resources for stream shutdown/switch."""
        self.person_detector.cleanup()
