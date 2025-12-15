"""
DetectionRenderer - Renders detections on frames.

Provides consistent rendering of detection overlays across all streaming algorithms.
"""

import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
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

    def render(self, frame: np.ndarray, detections: List[Dict],
               stats: Optional[Dict] = None) -> np.ndarray:
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

        # Make a copy to avoid modifying original
        output = frame.copy()

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

        x, y, w, h = bbox
        x, y, w, h = int(x), int(y), int(w), int(h)

        # Draw bounding box
        if self.config.show_boxes:
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                          self.config.box_color, self.config.box_thickness)

        # Build label text
        label_parts = []

        if self.config.show_ids and 'id' in detection:
            label_parts.append(f"ID:{detection['id']}")

        if 'class_name' in detection:
            label_parts.append(detection['class_name'])

        if self.config.show_confidence and 'confidence' in detection:
            conf = detection['confidence']
            label_parts.append(f"{conf:.2f}")

        # Draw label if we have text
        if label_parts and self.config.show_labels:
            label_text = " ".join(label_parts)
            self._draw_label(frame, label_text, x, y)

        return frame

    def _draw_label(self, frame: np.ndarray, text: str, x: int, y: int):
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
                          self.config.box_color, -1)
            text_color = (0, 0, 0)  # Black text on colored background
        else:
            text_color = self.config.box_color

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
