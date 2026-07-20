"""Streaming orchestrator for normalizing frame processing results."""

from typing import Dict, List, Optional, Tuple

import numpy as np

from core.services.LoggerService import LoggerService
from core.services.streaming.StreamAlgorithmService import StreamAlgorithmService
from core.services.streaming.StreamingUtils import StageTimings
from core.services.streaming.contracts import StreamDetection, StreamProcessResult


class StreamAnalyzeService:
    """Adapter-style orchestrator around a StreamAlgorithmService."""

    def __init__(self, service: StreamAlgorithmService, logger: Optional[LoggerService] = None):
        self.service = service
        self.logger = logger or LoggerService()

    def process_frame(self, frame: np.ndarray, timestamp: float) -> StreamProcessResult:
        """Run processing and normalize legacy/variant outputs into StreamProcessResult."""
        try:
            raw_result = self.service.process_frame(frame, timestamp)
            return self._normalize_result(raw_result, frame)
        except Exception as exc:
            self.logger.error(f"StreamAnalyzeService frame processing failed: {exc}")
            return StreamProcessResult(
                detections=[],
                timings=StageTimings(),
                rendered_frame=frame.copy() if frame is not None else None,
                error_message=str(exc),
            )

    def to_worker_output(self, result: StreamProcessResult) -> Tuple[List[Dict], bool]:
        """Convert normalized result to worker output tuple."""
        return result.detection_dicts(), result.was_skipped

    def _normalize_result(self, result, frame: np.ndarray) -> StreamProcessResult:
        if isinstance(result, StreamProcessResult):
            return result

        # Backward-compatible tuple support: (annotated, detections, timings)
        if isinstance(result, tuple) and len(result) == 3:
            annotated, detections, timings = result
            return StreamProcessResult(
                detections=self._normalize_detections(detections),
                timings=timings if isinstance(timings, StageTimings) else StageTimings(),
                rendered_frame=annotated,
            )

        if isinstance(result, tuple):
            tuple_len = len(result)
            self.logger.error(
                "Unsupported stream processing tuple result from "
                f"{type(self.service).__name__}: type={type(result).__name__} length={tuple_len}"
            )
            return StreamProcessResult(
                detections=[],
                timings=StageTimings(),
                rendered_frame=frame,
                error_message=f"Unsupported stream processing result tuple length: {tuple_len}",
            )

        # Backward-compatible list[dict] detections only
        if isinstance(result, list):
            return StreamProcessResult(
                detections=self._normalize_detections(result),
                timings=StageTimings(),
                rendered_frame=frame,
            )

        self.logger.error(
            "Unsupported stream processing result from "
            f"{type(self.service).__name__}: type={type(result).__name__}"
        )
        return StreamProcessResult(
            detections=[],
            timings=StageTimings(),
            rendered_frame=frame,
            error_message=f"Unsupported stream processing result type: {type(result).__name__}",
        )

    def _normalize_detections(self, detections) -> List[StreamDetection]:
        normalized: List[StreamDetection] = []
        for det in detections or []:
            if isinstance(det, StreamDetection):
                normalized.append(det)
                continue

            if isinstance(det, dict):
                normalized.append(
                    StreamDetection(
                        bbox=tuple(det.get("bbox", (0, 0, 0, 0))),
                        confidence=float(det.get("confidence", 0.0)),
                        class_name=str(det.get("class_name", det.get("detection_type", "Detection"))),
                        centroid=tuple(det["centroid"]) if det.get("centroid") is not None else None,
                        area=float(det["area"]) if det.get("area") is not None else None,
                        detection_type=str(det.get("detection_type", det.get("class_name", "generic"))),
                        timestamp=float(det.get("timestamp", 0.0)),
                        metadata=dict(det.get("metadata", {})),
                    )
                )
                continue

            # Dataclass/object fallback used by existing detection classes.
            bbox = getattr(det, "bbox", (0, 0, 0, 0))
            centroid = getattr(det, "centroid", None)
            area = getattr(det, "area", None)
            confidence = float(getattr(det, "confidence", 0.0))
            detection_type = str(getattr(det, "detection_type", "generic"))
            class_name = str(getattr(det, "class_name", detection_type))
            timestamp = float(getattr(det, "timestamp", 0.0))
            metadata = dict(getattr(det, "metadata", {}) or {})

            normalized.append(
                StreamDetection(
                    bbox=tuple(bbox),
                    confidence=confidence,
                    class_name=class_name,
                    centroid=tuple(centroid) if centroid is not None else None,
                    area=float(area) if area is not None else None,
                    detection_type=detection_type,
                    timestamp=timestamp,
                    metadata=metadata,
                )
            )

        return normalized
