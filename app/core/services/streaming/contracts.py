"""Common data contracts for streaming analysis services."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from core.services.streaming.StreamingUtils import StageTimings


BBox = Tuple[int, int, int, int]


@dataclass(frozen=True)
class FocusTarget:
    """Immutable request to focus the streaming video display on a point.

    Both fields are expressed in SOURCE-frame pixel coordinates (top-left
    origin):

    * ``center_xy``: the ``(x, y)`` point to center the zoom on.
    * ``reference_size``: the ``(width, height)`` of the source frame that
      ``center_xy`` was measured against. The display maps the point into its
      current full-resolution scene independently on each axis, so a focus
      target stays correct even if the displayed resolution differs from the
      resolution the point was captured at.

    A focus target is intentionally resolution-agnostic and never carries a
    processing resolution: streaming coordinates are already in source space
    (see :class:`StreamDetection`).
    """

    center_xy: Tuple[int, int]
    reference_size: Tuple[int, int]


@dataclass(frozen=True)
class StreamAlgorithmCapabilities:
    """Declare which shared streaming controls an algorithm supports."""

    supports_mask_controls: bool = True
    supports_render_at_processing_resolution: bool = True
    supports_render_contours: bool = True
    supports_use_detection_color: bool = True
    supports_temporal_voting: bool = True
    supports_aspect_ratio_filter: bool = True
    supports_detection_clustering: bool = True


@dataclass
class StreamDetection:
    """Normalized detection payload used by all streaming algorithms.

    Coordinate contract: ``bbox`` and ``centroid`` are expressed in
    SOURCE-frame pixel coordinates (the resolution of the frame handed to the
    algorithm), with a top-left origin. Services that run detection at a
    reduced processing resolution MUST scale coordinates back to source space
    before returning them, so consumers never need ``processing_resolution`` to
    interpret a detection. Anything that focuses the display on a detection
    should therefore use ``centroid``/``bbox`` directly (see
    :class:`FocusTarget`).
    """

    bbox: BBox
    confidence: float
    class_name: str
    centroid: Optional[Tuple[int, int]] = None
    area: Optional[float] = None
    detection_type: str = "generic"
    timestamp: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert detection to a viewer-friendly dictionary."""
        payload: Dict[str, Any] = {
            "bbox": self.bbox,
            "confidence": self.confidence,
            "class_name": self.class_name,
            "detection_type": self.detection_type,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }
        if self.centroid is not None:
            payload["centroid"] = self.centroid
        if self.area is not None:
            payload["area"] = self.area
        return payload


@dataclass
class StreamProcessResult:
    """Normalized frame processing result used by streaming services."""

    detections: List[StreamDetection] = field(default_factory=list)
    timings: StageTimings = field(default_factory=StageTimings)
    rendered_frame: Optional[np.ndarray] = None
    error_message: Optional[str] = None

    @property
    def was_skipped(self) -> bool:
        """True when the frame was intentionally skipped."""
        return bool(getattr(self.timings, "was_skipped", False))

    def detection_dicts(self) -> List[Dict[str, Any]]:
        """Return detections in the application's dictionary shape."""
        return [det.to_dict() for det in self.detections]
