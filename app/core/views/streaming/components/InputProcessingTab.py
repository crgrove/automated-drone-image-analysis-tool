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
        preset_layout.addWidget(QLabel("Resolution:"))
        self.resolution_preset = QComboBox()

        # Common video resolutions with standard names
        self.resolution_presets = {
            "Original": None,  # Use video's native resolution
            "8K (7680x4320)": (7680, 4320),
            "5K (5120x2880)": (5120, 2880),
            "4K (3840x2160)": (3840, 2160),
            "2K (2560x1440)": (2560, 1440),
            "1080P (1920x1080)": (1920, 1080),
            "900P (1600x900)": (1600, 900),
            "720P (1280x720)": (1280, 720),
            "540P (960x540)": (960, 540),
            "360P (640x360)": (640, 360),
            "240P (426x240)": (426, 240),
            "Custom": "custom"  # Special marker for custom resolution
        }

        for preset in self.resolution_presets.keys():
            self.resolution_preset.addItem(preset)

        self.resolution_preset.setCurrentText("720P (1280x720)")
        self.resolution_preset.setToolTip("Select a preset resolution for processing. Lower resolutions are faster but less detailed.\n"
                                          "'Original' uses the video's native resolution (no downsampling).\n"
                                          "720P (1280x720) provides excellent balance between speed and detection accuracy.\n"
                                          "Select 'Custom' to manually set width and height.")
        preset_layout.addWidget(self.resolution_preset)
        res_layout.addLayout(preset_layout)

        # Custom resolution inputs (hidden by default)
        custom_layout = QGridLayout()
        self.width_label = QLabel("Width:")
        custom_layout.addWidget(self.width_label, 0, 0)
        self.processing_width = QSpinBox()
        self.processing_width.setRange(320, 3840)
        self.processing_width.setValue(1280)
        self.processing_width.setEnabled(False)
        self.processing_width.setToolTip(
            "Custom processing width in pixels (320-3840).\nOnly enabled when 'Custom' resolution is selected.\nLower values = faster processing, less detail.")
        custom_layout.addWidget(self.processing_width, 0, 1)

        self.height_label = QLabel("Height:")
        custom_layout.addWidget(self.height_label, 1, 0)
        self.processing_height = QSpinBox()
        self.processing_height.setRange(240, 2160)
        self.processing_height.setValue(720)
        self.processing_height.setEnabled(False)
        self.processing_height.setToolTip(
            "Custom processing height in pixels (240-2160).\n"
            "Only enabled when 'Custom' resolution is selected.\n"
            "Lower values = faster processing, less detail.")
        custom_layout.addWidget(self.processing_height, 1, 1)

        # Hide width/height inputs by default (only show when Custom is selected)
        self.width_label.setVisible(False)
        self.processing_width.setVisible(False)
        self.height_label.setVisible(False)
        self.processing_height.setVisible(False)

        res_layout.addLayout(custom_layout)
        layout.addWidget(res_group)

        # Performance Options
        perf_group = QGroupBox("Performance Options")
        perf_layout = QVBoxLayout(perf_group)

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
            # Show and enable width/height inputs
            self.width_label.setVisible(True)
            self.processing_width.setVisible(True)
            self.processing_width.setEnabled(True)
            self.height_label.setVisible(True)
            self.processing_height.setVisible(True)
            self.processing_height.setEnabled(True)
        else:
            # Hide and disable width/height inputs
            self.width_label.setVisible(False)
            self.processing_width.setVisible(False)
            self.processing_width.setEnabled(False)
            self.height_label.setVisible(False)
            self.processing_height.setVisible(False)
            self.processing_height.setEnabled(False)
            # Update values for when Custom is selected later
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

    def set_processing_resolution(self, width: int, height: int):
        """
        Set processing resolution from width and height values.

        Maps the dimensions to a preset if available, otherwise uses Custom mode.

        Args:
            width: Processing width in pixels
            height: Processing height in pixels
        """
        # Create reverse mapping from dimensions to preset names
        resolution_map = {
            (7680, 4320): "8K (7680x4320)",
            (5120, 2880): "5K (5120x2880)",
            (3840, 2160): "4K (3840x2160)",
            (2560, 1440): "2K (2560x1440)",
            (1920, 1080): "1080P (1920x1080)",
            (1600, 900): "900P (1600x900)",
            (1280, 720): "720P (1280x720)",
            (960, 540): "540P (960x540)",
            (640, 360): "360P (640x360)",
            (426, 240): "240P (426x240)"
        }

        preset_name = resolution_map.get((width, height))
        if preset_name:
            self.resolution_preset.setCurrentText(preset_name)
            # This will trigger on_resolution_preset_changed which will hide width/height
        else:
            # Use custom if dimensions don't match any preset
            self.resolution_preset.setCurrentText("Custom")
            # Show and set width/height inputs
            self.width_label.setVisible(True)
            self.processing_width.setVisible(True)
            self.processing_width.setEnabled(True)
            self.processing_width.setValue(width)
            self.height_label.setVisible(True)
            self.processing_height.setVisible(True)
            self.processing_height.setEnabled(True)
            self.processing_height.setValue(height)
