"""
RenderingTab - Shared Rendering tab for streaming algorithms.

This tab provides common controls for rendering options that are used
across all streaming detection algorithms.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout,
                               QLabel, QSpinBox, QCheckBox, QComboBox, QGroupBox)
from PySide6.QtCore import Qt


class RenderingTab(QWidget):
    """Shared Rendering tab widget for streaming algorithms."""

    def __init__(self, parent=None, show_detection_color_option: bool = True):
        """
        Initialize the Rendering tab.

        Args:
            parent: Parent widget
            show_detection_color_option: Whether to show the "Use Detection Color" option
                                        (some algorithms may not need this)
        """
        super().__init__(parent)
        self.show_detection_color_option = show_detection_color_option
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)

        # Shape Options
        shape_group = QGroupBox("Shape Options")
        shape_layout = QGridLayout(shape_group)

        shape_layout.addWidget(QLabel("Shape Mode:"), 0, 0)
        self.render_shape = QComboBox()
        self.render_shape.addItems(["Box", "Circle", "Dot", "Off"])
        self.render_shape.setCurrentText("Circle")
        self.render_shape.setToolTip("Shape to draw around detections:\n\n"
                                     "• Box: Rectangle around detection bounding box.\n"
                                     "  Use for: Precise boundaries, technical visualization.\n\n"
                                     "• Circle: Circle encompassing detection (150% of contour radius).\n"
                                     "  Use for: General use, cleaner look (default).\n\n"
                                     "• Dot: Small dot at detection centroid.\n"
                                     "  Use for: Minimal overlay, fast rendering.\n\n"
                                     "• Off: No shape overlay (only thumbnails/text if enabled).\n"
                                     "  Use for: Clean video with minimal overlays.")
        shape_layout.addWidget(self.render_shape, 0, 1)

        layout.addWidget(shape_group)

        # Text & Contours
        vis_group = QGroupBox("Visual Options")
        vis_layout = QVBoxLayout(vis_group)

        self.render_text = QCheckBox("Show Text Labels (slower)")
        self.render_text.setToolTip("Displays text labels near detections showing detection information.\n"
                                    "Adds ~5-15ms processing overhead depending on detection count.\n"
                                    "Labels show: detection type, confidence, area.\n"
                                    "Recommended: OFF for speed, ON for debugging/analysis.")
        vis_layout.addWidget(self.render_text)

        self.render_contours = QCheckBox("Show Contours (slowest)")
        self.render_contours.setToolTip("Draws exact detection contours (pixel-precise boundaries).\n"
                                        "Adds ~10-20ms processing overhead (very expensive).\n"
                                        "Shows exact shape detected by algorithm.\n"
                                        "Recommended: OFF for speed, ON only for detailed analysis.")
        vis_layout.addWidget(self.render_contours)

        if self.show_detection_color_option:
            self.use_detection_color = QCheckBox("Use Detection Color (hue @ 100% sat/val for color anomalies)")
            self.use_detection_color.setChecked(True)  # Default ON
            self.use_detection_color.setToolTip("Color the detection overlay based on detected color.\n"
                                                "For color anomalies: Uses the detected hue at 100% saturation/value.\n"
                                                "For motion detections: Uses default color (green/blue).\n"
                                                "Helps visually identify what color was detected.\n"
                                                "Recommended: ON for color detection, OFF for motion-only.")
            vis_layout.addWidget(self.use_detection_color)

        layout.addWidget(vis_group)

        # Detection Limits
        limit_group = QGroupBox("Performance Limits")
        limit_layout = QGridLayout(limit_group)

        limit_layout.addWidget(QLabel("Max Detections:"), 0, 0)
        self.max_detections_to_render = QSpinBox()
        self.max_detections_to_render.setRange(0, 1000)
        self.max_detections_to_render.setValue(100)
        self.max_detections_to_render.setSpecialValueText("Unlimited")
        self.max_detections_to_render.setToolTip("Maximum number of detections to render on screen (0-1000).\n"
                                                 "Prevents rendering slowdown when hundreds of detections occur.\n"
                                                 "Shows highest confidence detections first.\n"
                                                 "0 = Unlimited (may cause lag with many detections).\n"
                                                 "Recommended: 100 for general use, 50 for complex rendering (text+contours).")
        limit_layout.addWidget(self.max_detections_to_render, 0, 1)

        layout.addWidget(limit_group)
        layout.addStretch()

    def get_config(self) -> dict:
        """
        Get current rendering configuration.

        Returns:
            Dictionary with rendering configuration values
        """
        # Map shape text to integer (0=Box, 1=Circle, 2=Dot, 3=Off)
        shape_map = {
            "Box": 0,
            "Circle": 1,
            "Dot": 2,
            "Off": 3
        }

        config = {
            'render_shape': shape_map.get(self.render_shape.currentText(), 1),
            'render_text': self.render_text.isChecked(),
            'render_contours': self.render_contours.isChecked(),
            'max_detections_to_render': self.max_detections_to_render.value(),
        }

        # Only include if the option exists
        if self.show_detection_color_option and hasattr(self, 'use_detection_color'):
            config['use_detection_color_for_rendering'] = self.use_detection_color.isChecked()

        return config

    def set_config(self, config: dict):
        """
        Set rendering configuration from dictionary.

        Args:
            config: Dictionary with rendering configuration values
        """
        # Map integer to shape text (0=Box, 1=Circle, 2=Dot, 3=Off)
        shape_map = {
            0: "Box",
            1: "Circle",
            2: "Dot",
            3: "Off"
        }

        if 'render_shape' in config:
            shape_text = shape_map.get(config['render_shape'], "Circle")
            self.render_shape.setCurrentText(shape_text)

        if 'render_text' in config:
            self.render_text.setChecked(bool(config['render_text']))

        if 'render_contours' in config:
            self.render_contours.setChecked(bool(config['render_contours']))

        if 'max_detections_to_render' in config:
            self.max_detections_to_render.setValue(config['max_detections_to_render'])

        if 'use_detection_color_for_rendering' in config and self.show_detection_color_option:
            if hasattr(self, 'use_detection_color'):
                self.use_detection_color.setChecked(bool(config['use_detection_color_for_rendering']))
