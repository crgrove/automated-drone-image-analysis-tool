"""
CleanupTab - Shared Cleanup tab for streaming algorithms.

This tab provides common controls for temporal voting and detection cleanup
that are used across streaming detection algorithms.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout,
                               QLabel, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox)


class CleanupTab(QWidget):
    """Shared Cleanup tab widget for streaming algorithms."""

    def __init__(self, parent=None):
        """
        Initialize the Cleanup tab.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)

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
                                                  "Must be <= Window Frames.\n"
                                                  "Recommended: 3 out of 5 (detection in 60% of frames).")
        window_layout.addWidget(self.temporal_threshold_frames, 1, 1)

        temporal_layout.addLayout(window_layout)
        layout.addWidget(temporal_group)

        # Detection Cleanup
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
                                         "Example: 0.2 = reject if height is more than 5x width.")
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
        Get current cleanup configuration.

        Returns:
            Dictionary with cleanup configuration values
        """
        return {
            'enable_temporal_voting': self.enable_temporal_voting.isChecked(),
            'temporal_window_frames': self.temporal_window_frames.value(),
            'temporal_threshold_frames': self.temporal_threshold_frames.value(),
            'enable_aspect_ratio_filter': self.enable_aspect_ratio_filter.isChecked(),
            'min_aspect_ratio': self.min_aspect_ratio.value(),
            'max_aspect_ratio': self.max_aspect_ratio.value(),
            'enable_detection_clustering': self.enable_detection_clustering.isChecked(),
            'clustering_distance': self.clustering_distance.value(),
        }

    def set_config(self, config: dict):
        """
        Set cleanup configuration from dictionary.

        Args:
            config: Dictionary with cleanup configuration values
        """
        if 'enable_temporal_voting' in config:
            self.enable_temporal_voting.setChecked(bool(config['enable_temporal_voting']))

        if 'temporal_window_frames' in config:
            self.temporal_window_frames.setValue(config['temporal_window_frames'])

        if 'temporal_threshold_frames' in config:
            self.temporal_threshold_frames.setValue(config['temporal_threshold_frames'])

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
