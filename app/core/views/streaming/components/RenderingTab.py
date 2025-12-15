"""
RenderingTab - Shared Rendering tab for streaming algorithms.

This tab provides common controls for rendering options that are used
across all streaming detection algorithms.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout,
                               QLabel, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QGroupBox)
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
                                                 "Recommended: 10 for general use, 50 for complex rendering (text+contours).")
        limit_layout.addWidget(self.max_detections_to_render, 0, 1)

        layout.addWidget(limit_group)

        # Temporal Voting
        temporal_group = QGroupBox("Temporal Voting")
        temporal_layout = QVBoxLayout(temporal_group)

        self.enable_temporal_voting = QCheckBox("Enable Temporal Voting (reduce flicker)")
        self.enable_temporal_voting.setChecked(True)
        self.enable_temporal_voting.setToolTip("Smooths detections across frames using temporal consistency.\n"
                                               "Detections must appear in N out of M consecutive frames to be confirmed.\n"
                                               "Significantly reduces flickering false positives.\n"
                                               "Recommended: ON for all use cases (default).")
        temporal_layout.addWidget(self.enable_temporal_voting)

        window_layout = QGridLayout()
        window_layout.setColumnMinimumWidth(0, 160)
        window_layout.setColumnStretch(1, 1)
        window_layout.addWidget(QLabel("Window Frames (M):"), 0, 0)
        self.temporal_window_frames = QSpinBox()
        self.temporal_window_frames.setRange(2, 30)
        self.temporal_window_frames.setValue(5)  # Default 5
        self.temporal_window_frames.setToolTip("Size of temporal voting window (2-30 frames).\n"
                                               "Detections must appear in N out of M consecutive frames.\n"
                                               "Larger values = longer memory, more stable, slower response to new objects.\n"
                                               "Smaller values = shorter memory, faster response, less stable.\n"
                                               "Recommended: 5 for 30fps (~167ms window), 7 for 60fps.")
        window_layout.addWidget(self.temporal_window_frames, 0, 1)

        window_layout.addWidget(QLabel("Threshold (N of M):"), 1, 0)
        self.temporal_threshold_frames = QSpinBox()
        self.temporal_threshold_frames.setRange(1, 30)
        self.temporal_threshold_frames.setValue(3)  # Default 3
        self.temporal_threshold_frames.setToolTip("Number of frames within window where detection must appear (N of M).\n"
                                                  "Higher values = more stringent, filters transient false positives.\n"
                                                  "Lower values = more lenient, faster response to new objects.\n"
                                                  "Must be ≤ Window Frames.\n"
                                                  "Recommended: 3 out of 5 (detection in 60% of frames).")
        window_layout.addWidget(self.temporal_threshold_frames, 1, 1)

        temporal_layout.addLayout(window_layout)

        layout.addWidget(temporal_group)

        # Detection Cleanup (aspect ratio + clustering)
        cleanup_group = QGroupBox("Detection Cleanup")
        cleanup_layout = QVBoxLayout(cleanup_group)

        # Aspect Ratio Filter
        self.enable_aspect_ratio_filter = QCheckBox("Enable Aspect Ratio Filtering")
        self.enable_aspect_ratio_filter.setChecked(False)  # Default OFF
        self.enable_aspect_ratio_filter.setToolTip("Filter out very thin or stretched detections based on width/height.\n"
                                                   "Useful for removing wires, long shadows, or other non-object shapes.\n"
                                                   "Most users can leave this OFF unless you see many long skinny false detections.")
        cleanup_layout.addWidget(self.enable_aspect_ratio_filter)

        ratio_layout = QGridLayout()
        ratio_layout.setColumnMinimumWidth(0, 160)
        ratio_layout.setColumnStretch(1, 1)
        ratio_layout.addWidget(QLabel("Min Ratio:"), 0, 0)
        self.min_aspect_ratio = QDoubleSpinBox()
        self.min_aspect_ratio.setRange(0.1, 10.0)
        self.min_aspect_ratio.setValue(0.2)
        self.min_aspect_ratio.setSingleStep(0.1)
        self.min_aspect_ratio.setToolTip("Minimum width/height ratio to keep (0.1-10.0).\n"
                                         "Lower values = allow taller, thinner detections.\n"
                                         "Higher values = require detections to be more square.\n"
                                         "Example: 0.2 ≈ reject if height is more than 5× width.")
        ratio_layout.addWidget(self.min_aspect_ratio, 0, 1)

        ratio_layout.addWidget(QLabel("Max Ratio:"), 1, 0)
        self.max_aspect_ratio = QDoubleSpinBox()
        self.max_aspect_ratio.setRange(0.1, 20.0)
        self.max_aspect_ratio.setValue(5.0)
        self.max_aspect_ratio.setSingleStep(0.1)
        self.max_aspect_ratio.setToolTip("Maximum width/height ratio to keep (0.1-20.0).\n"
                                         "Lower values = reject very wide, thin detections.\n"
                                         "Higher values = allow wider objects such as vehicles or long equipment.")
        ratio_layout.addWidget(self.max_aspect_ratio, 1, 1)

        cleanup_layout.addLayout(ratio_layout)

        # Detection Clustering
        clustering_group = QGroupBox("Detection Clustering")
        clustering_layout = QVBoxLayout(clustering_group)

        self.enable_detection_clustering = QCheckBox("Enable Detection Clustering")
        self.enable_detection_clustering.setChecked(False)  # Default OFF
        self.enable_detection_clustering.setToolTip("Optionally merge nearby detections into a single, larger detection.\n"
                                                    "Useful when one object appears as many small adjacent detections.\n"
                                                    "Most users can leave this OFF unless objects look fragmented.")
        clustering_layout.addWidget(self.enable_detection_clustering)

        cluster_dist_layout = QGridLayout()
        cluster_dist_layout.setColumnMinimumWidth(0, 160)
        cluster_dist_layout.setColumnStretch(1, 1)
        cluster_dist_layout.addWidget(QLabel("Clustering Distance (px):"), 0, 0)
        self.clustering_distance = QSpinBox()
        self.clustering_distance.setRange(0, 500)
        self.clustering_distance.setValue(50)  # Default 50px
        self.clustering_distance.setToolTip("Maximum distance between detection centers to merge them (0-500 pixels).\n"
                                            "Lower values = only merge very close detections.\n"
                                            "Higher values = merge detections that are farther apart (may over-merge).")
        cluster_dist_layout.addWidget(self.clustering_distance, 0, 1)

        clustering_layout.addLayout(cluster_dist_layout)
        cleanup_layout.addWidget(clustering_group)

        layout.addWidget(cleanup_group)
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
            # Temporal Voting
            'enable_temporal_voting': self.enable_temporal_voting.isChecked(),
            'temporal_window_frames': self.temporal_window_frames.value(),
            'temporal_threshold_frames': self.temporal_threshold_frames.value(),
            # Detection Cleanup
            'enable_aspect_ratio_filter': self.enable_aspect_ratio_filter.isChecked(),
            'min_aspect_ratio': self.min_aspect_ratio.value(),
            'max_aspect_ratio': self.max_aspect_ratio.value(),
            'enable_detection_clustering': self.enable_detection_clustering.isChecked(),
            'clustering_distance': self.clustering_distance.value(),
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

        # Temporal Voting
        if 'enable_temporal_voting' in config:
            self.enable_temporal_voting.setChecked(bool(config['enable_temporal_voting']))
        if 'temporal_window_frames' in config:
            self.temporal_window_frames.setValue(config['temporal_window_frames'])
        if 'temporal_threshold_frames' in config:
            self.temporal_threshold_frames.setValue(config['temporal_threshold_frames'])

        # Detection Cleanup
        if 'enable_aspect_ratio_filter' in config:
            self.enable_aspect_ratio_filter.setChecked(bool(config['enable_aspect_ratio_filter']))
        if 'min_aspect_ratio' in config:
            self.min_aspect_ratio.setValue(config['min_aspect_ratio'])
        if 'max_aspect_ratio' in config:
            self.max_aspect_ratio.setValue(config['max_aspect_ratio'])
        if 'enable_detection_clustering' in config:
            self.enable_detection_clustering.setChecked(bool(config['enable_detection_clustering']))
        if 'clustering_distance' in config:
            self.clustering_distance.setValue(config['clustering_distance'])
