"""
DetectionRenderer - Renders detections on frames.

Provides consistent rendering of detection overlays across all streaming algorithms.
"""

import cv2
import numpy as np
from typing import Any, List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class RenderConfig:
    """Configuration for detection rendering."""
    show_boxes: bool = True
    show_labels: bool = True
    show_confidence: bool = True
    show_ids: bool = True
    box_color: Tuple[int, int, int] = (0, 255, 0)  # BGR
    box_thickness: int = 2
    label_font_scale: float = 0.6
    label_thickness: int = 2
    label_background: bool = True
    show_stats_overlay: bool = False


class DetectionRenderer:
    """
    Renders detection overlays on frames.

    Provides consistent visualization of detections across all streaming algorithms.
    """

    def __init__(self, config: Optional[RenderConfig] = None):
        self.config = config or RenderConfig()

    def render(
        self,
        frame: np.ndarray,
        detections: List[Dict],
        stats: Optional[Dict] = None,
        copy_frame: bool = True,
    ) -> np.ndarray:
        """
        Render detections on frame.

        Args:
            frame: Input frame (BGR format)
            detections: List of detection dictionaries with keys:
                - bbox: (x, y, w, h)
                - confidence: float (0-1)
                - class_name: str
                - id: int (optional)
            stats: Optional statistics to display (fps, processing time, etc.)

        Returns:
            Frame with detections rendered
        """
        if frame is None or len(frame.shape) != 3:
            return frame

        output = frame.copy() if copy_frame else frame

        # Render each detection
        for detection in detections:
            output = self._render_detection(output, detection)

        # Render statistics overlay if enabled
        if self.config.show_stats_overlay and stats:
            output = self._render_stats(output, stats)

        return output

    def _render_detection(self, frame: np.ndarray, detection: Dict) -> np.ndarray:
        """Render a single detection on the frame."""
        bbox = detection.get('bbox')
        if not bbox:
            return frame

        metadata = self._get_detection_metadata(detection)
        x, y, w, h = bbox
        x, y, w, h = int(x), int(y), int(w), int(h)
        if metadata.get("render_skip"):
            return frame

        centroid = detection.get("centroid")
        if centroid is None:
            centroid = (x + (w // 2), y + (h // 2))
        cx, cy = int(centroid[0]), int(centroid[1])

        color = self._resolve_color(detection, metadata)
        render_shape = metadata.get("render_shape")
        render_contours = bool(metadata.get("render_contours", False))
        render_padding = int(metadata.get("render_padding", 0) or 0)
        contour = self._normalize_contour(metadata.get("contour", detection.get("contour")))

        # Draw bounding box
        if render_shape is None:
            if self.config.show_boxes:
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, self.config.box_thickness)
        else:
            self._draw_detection_shape(
                frame=frame,
                render_shape=int(render_shape),
                bbox=(x, y, w, h),
                centroid=(cx, cy),
                color=color,
                contour=contour,
                padding=render_padding,
            )

        if render_contours and contour is not None and render_shape != 3:
            cv2.drawContours(frame, [contour], -1, color, 1)

        # Build label text
        label_text = self._build_label_text(detection, metadata)
        show_label = bool(metadata.get("render_text", self.config.show_labels))

        # Draw label if we have text
        if label_text and show_label and render_shape != 3:
            self._draw_label(frame, label_text, x, y, color)

        return frame

    def _get_detection_metadata(self, detection: Dict[str, Any]) -> Dict[str, Any]:
        """Return the metadata dictionary for a detection."""
        metadata = detection.get("metadata", {})
        if isinstance(metadata, dict):
            return metadata
        return {}

    def _resolve_color(self, detection: Dict[str, Any], metadata: Dict[str, Any]) -> Tuple[int, int, int]:
        """Resolve a per-detection render color, falling back to the renderer default."""
        raw_color = metadata.get("render_color", detection.get("render_color"))
        if isinstance(raw_color, (tuple, list)) and len(raw_color) == 3:
            try:
                return tuple(int(channel) for channel in raw_color)
            except (TypeError, ValueError):
                pass
        return self.config.box_color

    def _normalize_contour(self, contour: Any) -> Optional[np.ndarray]:
        """Convert contour-like data into an OpenCV-compatible array."""
        if contour is None:
            return None
        contour_array = np.asarray(contour)
        if contour_array.size == 0:
            return None
        return contour_array.astype(np.int32)

    def _draw_detection_shape(
        self,
        frame: np.ndarray,
        render_shape: int,
        bbox: Tuple[int, int, int, int],
        centroid: Tuple[int, int],
        color: Tuple[int, int, int],
        contour: Optional[np.ndarray],
        padding: int,
    ) -> None:
        """Draw the normalized detection shape."""
        x, y, w, h = bbox
        cx, cy = centroid

        if render_shape == 0:
            x_expanded = max(0, x - padding)
            y_expanded = max(0, y - padding)
            w_expanded = min(w + (padding * 2), frame.shape[1] - x_expanded)
            h_expanded = min(h + (padding * 2), frame.shape[0] - y_expanded)
            cv2.rectangle(
                frame,
                (x_expanded, y_expanded),
                (x_expanded + w_expanded, y_expanded + h_expanded),
                color,
                self.config.box_thickness,
            )
            cv2.circle(frame, (cx, cy), 3, color, -1)
            return

        if render_shape == 1:
            if contour is not None:
                (_, _), contour_radius = cv2.minEnclosingCircle(contour)
                base_radius = max(5, int(contour_radius * 1.5))
            else:
                diagonal = float(np.sqrt((w * w) + (h * h))) / 2.0
                base_radius = max(5, int(diagonal * 1.1))
            cv2.circle(frame, (cx, cy), base_radius + padding, color, self.config.box_thickness)
            return

        if render_shape == 2:
            cv2.circle(frame, (cx, cy), 5, color, -1)

    def _build_label_text(self, detection: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Build a detection label, allowing adapters to override it."""
        if metadata.get("render_label") is not None:
            return str(metadata["render_label"])

        label_parts = []

        if self.config.show_ids and 'id' in detection:
            label_parts.append(f"ID:{detection['id']}")

        if 'class_name' in detection:
            label_parts.append(str(detection['class_name']))

        show_confidence = bool(metadata.get("show_confidence", self.config.show_confidence))
        if show_confidence and 'confidence' in detection:
            try:
                conf = float(detection['confidence'])
                label_parts.append(f"{conf:.2f}")
            except (TypeError, ValueError):
                pass

        return " ".join(label_parts)

    def _draw_label(self, frame: np.ndarray, text: str, x: int, y: int, color: Tuple[int, int, int]):
        """Draw a label with background."""
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = self.config.label_font_scale
        thickness = self.config.label_thickness

        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(
            text, font, font_scale, thickness
        )

        # Position label above box (or below if too close to top)
        label_y = y - 10 if y > 30 else y + text_height + 10

        # Draw background rectangle if enabled
        if self.config.label_background:
            bg_y1 = label_y - text_height - 5
            bg_y2 = label_y + 5
            cv2.rectangle(frame, (x, bg_y1), (x + text_width, bg_y2),
                          color, -1)
            text_color = (0, 0, 0)  # Black text on colored background
        else:
            text_color = color

        # Draw text
        cv2.putText(frame, text, (x, label_y), font, font_scale,
                    text_color, thickness, cv2.LINE_AA)

    def _render_stats(self, frame: np.ndarray, stats: Dict) -> np.ndarray:
        """Render statistics overlay on frame."""
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        thickness = 1
        color = (0, 255, 0)  # Green

        # Position in top-left corner
        x, y = 10, 20
        line_height = 20

        # Draw background
        bg_height = len(stats) * line_height + 10
        cv2.rectangle(frame, (5, 5), (250, bg_height), (0, 0, 0), -1)
        cv2.rectangle(frame, (5, 5), (250, bg_height), color, 1)

        # Draw each stat
        for key, value in stats.items():
            text = f"{key}: {value}"
            cv2.putText(frame, text, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)
            y += line_height

        return frame

    def update_config(self, config: RenderConfig):
        """Update rendering configuration."""
        self.config = config

    def set_box_color(self, color: Tuple[int, int, int]):
        """Set bounding box color (BGR format)."""
        self.config.box_color = color

    def set_show_labels(self, show: bool):
        """Enable/disable label rendering."""
        self.config.show_labels = show

    def set_show_confidence(self, show: bool):
        """Enable/disable confidence scores."""
        self.config.show_confidence = show

    def set_show_stats(self, show: bool):
        """Enable/disable statistics overlay."""
        self.config.show_stats_overlay = show
