"""
InputProcessingTab - Shared Input & Processing tab for streaming algorithms.

This tab provides common controls for processing resolution and performance options
that are used across all streaming detection algorithms.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QLabel, QSpinBox, QCheckBox, QComboBox, QGroupBox)
from PySide6.QtCore import Qt


class InputProcessingTab(QWidget):
    """Shared Input & Processing tab widget for streaming algorithms."""

    def __init__(self, parent=None):
        """Initialize the Input & Processing tab."""
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)

        # Processing Resolution
        res_group = QGroupBox("Processing Resolution")
        res_layout = QVBoxLayout(res_group)

        # Dropdown for preset resolutions
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Preset:"))
        self.resolution_preset = QComboBox()

        # Common 16:9 resolutions
        self.resolution_presets = {
            "Original": None,  # Use video's native resolution
            "426x240": (426, 240),
            "640x360": (640, 360),
            "960x540": (960, 540),
            "1280x720": (1280, 720),
            "1600x900": (1600, 900),
            "1920x1080": (1920, 1080),
            "2560x1440": (2560, 1440),
            "3200x1800": (3200, 1800),
            "3840x2160": (3840, 2160),
            "5120x2880": (5120, 2880),
            "7680x4320": (7680, 4320),
            "Custom": "custom"  # Special marker for custom resolution
        }

        for preset in self.resolution_presets.keys():
            self.resolution_preset.addItem(preset)

        self.resolution_preset.setCurrentText("1280x720")
        self.resolution_preset.setToolTip("Select a preset resolution for processing. Lower resolutions are faster but less detailed.\n"
                                          "'Original' uses the video's native resolution (no downsampling).\n"
                                          "720p (1280x720) provides excellent balance between speed and detection accuracy.\n"
                                          "Select 'Custom' to manually set width and height.")
        preset_layout.addWidget(self.resolution_preset)
        res_layout.addLayout(preset_layout)

        # Custom resolution inputs (hidden by default)
        custom_layout = QGridLayout()
        custom_layout.addWidget(QLabel("Width:"), 0, 0)
        self.processing_width = QSpinBox()
        self.processing_width.setRange(320, 3840)
        self.processing_width.setValue(1280)
        self.processing_width.setEnabled(False)
        self.processing_width.setToolTip(
            "Custom processing width in pixels (320-3840).\nOnly enabled when 'Custom' preset is selected.\nLower values = faster processing, less detail.")
        custom_layout.addWidget(self.processing_width, 0, 1)

        custom_layout.addWidget(QLabel("Height:"), 1, 0)
        self.processing_height = QSpinBox()
        self.processing_height.setRange(240, 2160)
        self.processing_height.setValue(720)
        self.processing_height.setEnabled(False)
        self.processing_height.setToolTip(
            "Custom processing height in pixels (240-2160).\nOnly enabled when 'Custom' preset is selected.\nLower values = faster processing, less detail.")
        custom_layout.addWidget(self.processing_height, 1, 1)

        res_layout.addLayout(custom_layout)
        layout.addWidget(res_group)

        # Performance Options
        perf_group = QGroupBox("Performance Options")
        perf_layout = QVBoxLayout(perf_group)

        self.threaded_capture = QCheckBox("Use Threaded Capture")
        self.threaded_capture.setChecked(True)  # Default ON
        self.threaded_capture.setToolTip("Enables background video decoding in a separate thread.\n"
                                         "Allows processing to happen in parallel with video capture.\n"
                                         "Improves performance especially for high-resolution videos (2K/4K).\n"
                                         "Highly recommended for all video sources. No downsides.")
        perf_layout.addWidget(self.threaded_capture)

        self.render_at_processing_res = QCheckBox("Render at Processing Resolution (faster for high-res)")
        self.render_at_processing_res.setChecked(True)  # Default ON
        self.render_at_processing_res.setToolTip("Renders detection overlays at processing resolution instead of original video resolution.\n"
                                                 "Significantly faster for high-resolution videos (1080p+) with minimal visual impact.\n"
                                                 "Example: Processing at 720p but video is 4K - renders at 720p then upscales.\n"
                                                 "Recommended: ON for high-res videos, OFF for native 720p or lower.")
        perf_layout.addWidget(self.render_at_processing_res)

        layout.addWidget(perf_group)
        layout.addStretch()

    def on_resolution_preset_changed(self, preset_name: str):
        """Handle resolution preset change."""
        if preset_name == "Custom":
            self.processing_width.setEnabled(True)
            self.processing_height.setEnabled(True)
        else:
            self.processing_width.setEnabled(False)
            self.processing_height.setEnabled(False)
            if preset_name != "Original" and preset_name in self.resolution_presets:
                width, height = self.resolution_presets[preset_name]
                self.processing_width.setValue(width)
                self.processing_height.setValue(height)

    def get_processing_resolution(self) -> tuple:
        """Get current processing resolution as (width, height)."""
        preset_name = self.resolution_preset.currentText()
        if preset_name == "Custom":
            return (self.processing_width.value(), self.processing_height.value())
        elif preset_name == "Original":
            return (99999, 99999)  # Special marker for "no downsampling"
        elif preset_name in self.resolution_presets:
            return self.resolution_presets[preset_name]
        else:
            return (1280, 720)  # Default

