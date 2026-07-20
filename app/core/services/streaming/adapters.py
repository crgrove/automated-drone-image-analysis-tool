"""Adapters that normalize existing streaming services to a common contract."""

from dataclasses import asdict, is_dataclass
from typing import Any, Dict

import cv2
import numpy as np

from core.services.LoggerService import LoggerService
from core.services.streaming.StreamAlgorithmService import StreamAlgorithmService
from core.services.streaming.StreamingUtils import StageTimings
from core.services.streaming.contracts import StreamDetection, StreamProcessResult


def _dataclass_to_dict(value: Any) -> Dict[str, Any]:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return dict(value)
    return {}


def _merge_dataclass_config(raw_config: Any, current_config: Any):
    if raw_config is None:
        return current_config
    if type(raw_config) is type(current_config):
        return raw_config
    if not isinstance(raw_config, dict):
        return current_config

    merged_data = dict(current_config.__dict__)
    for key in merged_data.keys():
        if key in raw_config:
            merged_data[key] = raw_config[key]
    return type(current_config)(**merged_data)


def _attach_service_parent(adapter: StreamAlgorithmService, service: Any, logger: LoggerService) -> None:
    """Attach an unparented service to its adapter and warn on conflicting ownership."""
    current_parent = service.parent()
    if current_parent is None:
        service.setParent(adapter)
        return

    if current_parent is not adapter:
        logger.warning(
            f"{type(adapter).__name__} received {type(service).__name__} with existing parent "
            f"{type(current_parent).__name__}; adapter will not take ownership."
        )


def _get_render_padding(service: Any) -> int:
    """Read the AOI padding preference when available."""
    settings_service = getattr(service, "settings_service", None)
    if settings_service is None or not hasattr(settings_service, "get_setting"):
        return 0
    try:
        return int(settings_service.get_setting("AOIRadius", 15))
    except Exception:
        return 0


def _limit_render_indices(detections: Any, max_to_render: int):
    """Return the indices that should be rendered when a cap is configured."""
    if max_to_render <= 0 or len(detections) <= max_to_render:
        return set(range(len(detections)))

    ranked = sorted(
        range(len(detections)),
        key=lambda idx: float(getattr(detections[idx], "confidence", 0.0)) * float(getattr(detections[idx], "area", 0.0)),
        reverse=True,
    )
    return set(ranked[:max_to_render])


class AIPersonStreamAdapter(StreamAlgorithmService):
    """Contract adapter for AIPersonStreamingService."""

    def __init__(self, service: Any, parent=None):
        super().__init__(parent)
        self._logger = LoggerService()
        self._service = service
        _attach_service_parent(self, self._service, self._logger)

    def update_config(self, config: Dict[str, Any]) -> None:
        current = self._service.get_config()
        merged = _merge_dataclass_config(config, current)
        self._service.update_config(merged)

    def get_config(self) -> Dict[str, Any]:
        return _dataclass_to_dict(self._service.get_config())

    def process_frame(self, frame, timestamp: float) -> StreamProcessResult:
        cfg = self._service.get_config()
        original_resolution = (int(frame.shape[1]), int(frame.shape[0]))
        try:
            annotated, detections, timings = self._service.process_frame(
                frame,
                timestamp,
                render_detections=False,
            )
        except TypeError:
            annotated, detections, timings = self._service.process_frame(frame, timestamp)
        normalized = []
        for detection in detections:
            metadata = dict(detection.metadata or {})
            metadata.update({
                "render_shape": int(getattr(cfg, "render_shape", 0)),
                "render_text": bool(getattr(cfg, "render_text", getattr(cfg, "show_labels", False))),
                "render_color": (0, 200, 255),
                "original_resolution": original_resolution,
            })
            if metadata["render_text"]:
                metadata["render_label"] = f"Person {float(detection.confidence):.2f}"
            normalized.append(
                StreamDetection(
                    bbox=tuple(detection.bbox),
                    confidence=float(detection.confidence),
                    class_name="Person",
                    centroid=tuple(detection.centroid),
                    area=float(detection.area),
                    detection_type=str(detection.detection_type),
                    timestamp=float(detection.timestamp),
                    metadata=metadata,
                )
            )
        return StreamProcessResult(
            detections=normalized,
            timings=timings if isinstance(timings, StageTimings) else StageTimings(),
            rendered_frame=annotated,
        )

    def reset(self) -> None:
        self._service.reset()

    def cleanup(self) -> None:
        self._service.cleanup()


class ColorDetectionStreamAdapter(StreamAlgorithmService):
    """Contract adapter for ColorDetectionService."""

    def __init__(self, service: Any, parent=None):
        super().__init__(parent)
        self._logger = LoggerService()
        self._service = service
        _attach_service_parent(self, self._service, self._logger)

    def _get_current_config(self):
        return self._service.get_config()

    def update_config(self, config: Dict[str, Any]) -> None:
        current = self._get_current_config()
        merged = _merge_dataclass_config(config, current)
        self._service.update_config(merged)

    def get_config(self) -> Dict[str, Any]:
        return _dataclass_to_dict(self._get_current_config())

    def process_frame(self, frame, timestamp: float) -> StreamProcessResult:
        cfg = self._get_current_config()
        original_resolution = (int(frame.shape[1]), int(frame.shape[0]))
        detections = self._service.detect_colors(frame, timestamp)
        if hasattr(self._service, "create_overlay_frame"):
            annotated = self._service.create_overlay_frame(frame)
        else:
            annotated = self._service.create_annotated_frame(frame, [])
        render_indices = _limit_render_indices(detections, int(getattr(cfg, "max_detections_to_render", 0) or 0))
        render_padding = _get_render_padding(self._service)
        normalized = []
        for index, detection in enumerate(detections):
            color_id = detection.color_id if detection.color_id is not None else 0
            metadata = dict(detection.metadata or {})
            metadata.setdefault("color_id", color_id)
            metadata.setdefault("mean_color", detection.mean_color)
            metadata.setdefault("processing_resolution", original_resolution)
            metadata.setdefault("original_resolution", original_resolution)
            if getattr(cfg, "use_detection_color_for_rendering", False) and detection.color is not None:
                render_color = detection.color
            elif detection.detection_type == "fused":
                render_color = (255, 128, 0)
            elif detection.detection_type == "motion":
                render_color = (0, 255, 0)
            elif float(detection.confidence) > 0.8:
                render_color = (0, 255, 0)
            elif float(detection.confidence) > 0.5:
                render_color = (0, 255, 255)
            else:
                render_color = (0, 0, 255)
            metadata.update({
                "render_shape": int(getattr(cfg, "render_shape", 0)),
                "render_text": bool(getattr(cfg, "render_text", False)),
                "render_contours": bool(getattr(cfg, "render_contours", False)),
                "render_color": tuple(int(channel) for channel in render_color),
                "render_padding": render_padding,
                "render_skip": index not in render_indices,
            })
            if getattr(detection, "contour", None) is not None:
                metadata["contour"] = detection.contour
            if metadata["render_text"]:
                label = f"#{index + 1}"
                if detection.detection_type != "color":
                    label += f" [{detection.detection_type}]"
                label += f" {float(detection.confidence):.2f}"
                if "persistence_votes" in metadata:
                    label += f" P{metadata['persistence_votes']}"
                if "temporal_votes" in metadata:
                    label += f" V{metadata['temporal_votes']}"
                if "cluster_size" in metadata:
                    label += f" C{metadata['cluster_size']}"
                metadata["render_label"] = label
            normalized.append(
                StreamDetection(
                    bbox=tuple(detection.bbox),
                    confidence=float(detection.confidence),
                    class_name=f"Color_{color_id}",
                    centroid=tuple(detection.centroid),
                    area=float(detection.area),
                    detection_type=str(detection.detection_type),
                    timestamp=float(detection.timestamp),
                    metadata=metadata,
                )
            )

        return StreamProcessResult(
            detections=normalized,
            timings=StageTimings(),
            rendered_frame=annotated,
        )

    def reset(self) -> None:
        self._service.reset()

    def cleanup(self) -> None:
        self._service.cleanup()


class ColorAnomalyMotionStreamAdapter(StreamAlgorithmService):
    """Contract adapter for ColorAnomalyAndMotionDetectionOrchestrator."""

    def __init__(self, service: Any, parent=None):
        super().__init__(parent)
        self._logger = LoggerService()
        self._service = service
        _attach_service_parent(self, self._service, self._logger)

    def update_config(self, config: Dict[str, Any]) -> None:
        current = self._service.config
        merged = _merge_dataclass_config(config, current)
        self._service.update_config(merged)

    def get_config(self) -> Dict[str, Any]:
        return _dataclass_to_dict(self._service.config)

    def process_frame(self, frame, timestamp: float) -> StreamProcessResult:
        cfg = self._service.config
        try:
            annotated, detections, timings = self._service.process_frame(
                frame,
                timestamp,
                render_detections=False,
            )
        except TypeError:
            annotated, detections, timings = self._service.process_frame(frame, timestamp)
        render_indices = _limit_render_indices(detections, int(getattr(cfg, "max_detections_to_render", 0) or 0))
        render_padding = _get_render_padding(self._service)
        normalized = []
        for index, detection in enumerate(detections):
            metadata = dict(detection.metadata or {})
            if getattr(cfg, "use_detection_color_for_rendering", False) and 'dominant_color' in metadata:
                try:
                    bgr_color = metadata['dominant_color']
                    hsv_pixel = np.uint8([[[bgr_color[0], bgr_color[1], bgr_color[2]]]])
                    hue = cv2.cvtColor(hsv_pixel, cv2.COLOR_BGR2HSV)[0][0][0]
                    vibrant = np.uint8([[[hue, 255, 255]]])
                    render_color = tuple(int(channel) for channel in cv2.cvtColor(vibrant, cv2.COLOR_HSV2BGR)[0][0])
                except Exception:
                    render_color = (255, 0, 255)
            elif detection.detection_type == 'fused':
                render_color = (255, 255, 0) if float(detection.confidence) > 0.7 else (
                    (255, 128, 0) if float(detection.confidence) > 0.4 else (200, 100, 0)
                )
            elif detection.detection_type == 'color_anomaly':
                render_color = (255, 0, 255) if float(detection.confidence) > 0.7 else (
                    (255, 0, 128) if float(detection.confidence) > 0.4 else (200, 0, 100)
                )
            else:
                render_color = (0, 255, 0) if float(detection.confidence) > 0.7 else (
                    (0, 255, 255) if float(detection.confidence) > 0.4 else (0, 165, 255)
                )
            metadata.update({
                "render_shape": int(getattr(cfg, "render_shape", 0)),
                "render_text": bool(getattr(cfg, "render_text", False)),
                "render_contours": bool(getattr(cfg, "render_contours", False)),
                "render_color": tuple(int(channel) for channel in render_color),
                "render_padding": render_padding,
                "render_skip": index not in render_indices,
            })
            if getattr(detection, "contour", None) is not None:
                metadata["contour"] = detection.contour
            if metadata["render_text"]:
                if detection.detection_type == 'fused':
                    metadata["render_label"] = f"#{index + 1} FUSED {int(detection.area)}px"
                elif detection.detection_type == 'color_anomaly':
                    metadata["render_label"] = f"#{index + 1} COLOR {int(detection.area)}px"
                else:
                    metadata["render_label"] = f"#{index + 1} MOTION {int(detection.area)}px"
            normalized.append(
                StreamDetection(
                    bbox=tuple(detection.bbox),
                    confidence=float(detection.confidence),
                    class_name=str(detection.detection_type),
                    centroid=tuple(detection.centroid),
                    area=float(detection.area),
                    detection_type=str(detection.detection_type),
                    timestamp=float(detection.timestamp),
                    metadata=metadata,
                )
            )

        return StreamProcessResult(
            detections=normalized,
            timings=timings if isinstance(timings, StageTimings) else StageTimings(),
            rendered_frame=annotated,
        )

    def reset(self) -> None:
        self._service.reset()

    def cleanup(self) -> None:
        self._service.cleanup()
