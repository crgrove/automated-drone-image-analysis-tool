"""
InputProcessingTab - Shared Input & Processing tab for streaming algorithms.

This tab provides common controls for processing resolution and performance options
that are used across all streaming detection algorithms.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QLabel, QSpinBox, QCheckBox, QComboBox, QGroupBox)
from PySide6.QtCore import Qt
from core.services.streaming.contracts import StreamAlgorithmCapabilities
from helpers.TranslationMixin import TranslationMixin


class InputProcessingTab(TranslationMixin, QWidget):
    """Shared Input & Processing tab widget for streaming algorithms."""

    def __init__(self, parent=None, capabilities: StreamAlgorithmCapabilities | None = None):
        """Initialize the Input & Processing tab."""
        super().__init__(parent)
        self.capabilities = capabilities or StreamAlgorithmCapabilities()
        self.setup_ui()
        self.apply_capabilities(self.capabilities)
        self._apply_translations()

    def setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)

        # Processing Resolution
        res_group = QGroupBox(self.tr("Processing Resolution"))
        res_layout = QVBoxLayout(res_group)

        # Dropdown for preset resolutions
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel(self.tr("Resolution:")))
        self.resolution_preset = QComboBox()

        # Common video resolutions: stable internal key -> (display label, dimensions)
        self.resolution_presets = [
            ("original", self.tr("Original"), None),
            ("8K", "8K (7680x4320)", (7680, 4320)),
            ("5K", "5K (5120x2880)", (5120, 2880)),
            ("4K", "4K (3840x2160)", (3840, 2160)),
            ("2K", "2K (2560x1440)", (2560, 1440)),
            ("1080P", "1080P (1920x1080)", (1920, 1080)),
            ("900P", "900P (1600x900)", (1600, 900)),
            ("720P", "720P (1280x720)", (1280, 720)),
            ("540P", "540P (960x540)", (960, 540)),
            ("360P", "360P (640x360)", (640, 360)),
            ("240P", "240P (426x240)", (426, 240)),
            ("custom", self.tr("Custom"), "custom"),
        ]
        self._resolution_dims = {key: dims for key, _, dims in self.resolution_presets}

        for key, label, _ in self.resolution_presets:
            self.resolution_preset.addItem(label, key)

        self.resolution_preset.setCurrentIndex(self.resolution_preset.findData("720P"))
        self.resolution_preset.setToolTip(self.tr(
            "Select a preset resolution for processing. Lower resolutions are faster but less detailed.\n"
            "'Original' uses the video's native resolution (no downsampling).\n"
            "720P (1280x720) provides excellent balance between speed and detection accuracy.\n"
            "Select 'Custom' to manually set width and height."
        ))
        preset_layout.addWidget(self.resolution_preset)
        res_layout.addLayout(preset_layout)

        # Custom resolution inputs (hidden by default)
        custom_layout = QGridLayout()
        self.width_label = QLabel(self.tr("Width:"))
        custom_layout.addWidget(self.width_label, 0, 0)
        self.processing_width = QSpinBox()
        self.processing_width.setRange(320, 3840)
        self.processing_width.setValue(1280)
        self.processing_width.setEnabled(False)
        self.processing_width.setToolTip(self.tr(
            "Custom processing width in pixels (320-3840).\n"
            "Only enabled when 'Custom' resolution is selected.\n"
            "Lower values = faster processing, less detail."
        ))
        custom_layout.addWidget(self.processing_width, 0, 1)

        self.height_label = QLabel(self.tr("Height:"))
        custom_layout.addWidget(self.height_label, 1, 0)
        self.processing_height = QSpinBox()
        self.processing_height.setRange(240, 2160)
        self.processing_height.setValue(720)
        self.processing_height.setEnabled(False)
        self.processing_height.setToolTip(self.tr(
            "Custom processing height in pixels (240-2160).\n"
            "Only enabled when 'Custom' resolution is selected.\n"
            "Lower values = faster processing, less detail."
        ))
        custom_layout.addWidget(self.processing_height, 1, 1)

        # Hide width/height inputs by default (only show when Custom is selected)
        self.width_label.setVisible(False)
        self.processing_width.setVisible(False)
        self.height_label.setVisible(False)
        self.processing_height.setVisible(False)

        res_layout.addLayout(custom_layout)
        layout.addWidget(res_group)

        # Performance Options
        perf_group = QGroupBox(self.tr("Performance Options"))
        perf_layout = QVBoxLayout(perf_group)

        # Frame Rate selection
        fps_layout = QHBoxLayout()
        self.frame_rate_label = QLabel(self.tr("Frame Rate:"))
        fps_layout.addWidget(self.frame_rate_label)
        self.frame_rate_preset = QComboBox()

        # Frame rate options: stable key -> (display label, fps value).
        self.frame_rate_presets = [
            ("source", self.tr("Source FPS"), None),
            ("30", "30 FPS", 30),
            ("25", "25 FPS", 25),
            ("20", "20 FPS", 20),
            ("15", "15 FPS", 15),
            ("10", "10 FPS", 10),
            ("5", "5 FPS", 5),
        ]
        self._frame_rate_values = {key: fps for key, _, fps in self.frame_rate_presets}

        for key, label, _ in self.frame_rate_presets:
            self.frame_rate_preset.addItem(label, key)

        self.frame_rate_preset.setCurrentIndex(self.frame_rate_preset.findData("source"))
        self.frame_rate_preset.setToolTip(self.tr(
            "Limit the frame rate for processing.\n\n"
            "• Source FPS - Follow the source cadence (live sources may apply a safety cap)\n"
            "• 30 FPS - Good balance of smoothness and performance\n"
            "• 25 FPS - Standard for PAL video\n"
            "• 20 FPS - Reduced CPU usage\n"
            "• 15 FPS - Lower CPU usage\n"
            "• 10 FPS - Significant CPU savings\n"
            "• 5 FPS - Maximum CPU savings, may miss fast objects\n\n"
            "Lower frame rates reduce CPU usage but may miss fast-moving objects.\n"
            "Detections persist between skipped frames for visual continuity."
        ))
        fps_layout.addWidget(self.frame_rate_preset)
        fps_layout.addStretch()
        perf_layout.addLayout(fps_layout)

        self.render_at_processing_res = QCheckBox(self.tr("Render at Processing Resolution (faster for high-res)"))
        self.render_at_processing_res.setChecked(True)  # Default ON
        self.render_at_processing_res.setToolTip(self.tr(
            "Renders detection overlays at processing resolution instead of original video resolution.\n"
            "Significantly faster for high-resolution videos (1080p+) with minimal visual impact.\n"
            "Example: Processing at 720p but video is 4K - renders at 720p then upscales.\n"
            "Recommended: ON for high-res videos, OFF for native 720p or lower."
        ))
        perf_layout.addWidget(self.render_at_processing_res)

        layout.addWidget(perf_group)
        layout.addStretch()

    def apply_capabilities(self, capabilities: StreamAlgorithmCapabilities):
        """Apply shared-control capability gating."""
        self.capabilities = capabilities
        supports_render_at_processing = bool(capabilities.supports_render_at_processing_resolution)
        self.render_at_processing_res.setVisible(supports_render_at_processing)
        if not supports_render_at_processing:
            self.render_at_processing_res.setChecked(False)

    def on_resolution_preset_changed(self, _value=None):
        """Handle resolution preset change. Reads stable key from currentData()."""
        preset_key = self.resolution_preset.currentData()
        if preset_key == "custom":
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
            dims = self._resolution_dims.get(preset_key)
            if isinstance(dims, tuple):
                width, height = dims
                self.processing_width.setValue(width)
                self.processing_height.setValue(height)

    def get_processing_resolution(self) -> tuple:
        """Get current processing resolution as (width, height)."""
        preset_key = self.resolution_preset.currentData()
        if preset_key == "custom":
            return (self.processing_width.value(), self.processing_height.value())
        if preset_key == "original":
            return (None, None)
        dims = self._resolution_dims.get(preset_key)
        if isinstance(dims, tuple):
            return dims
        return (1280, 720)

    def set_processing_resolution(self, width: int | None, height: int | None):
        """
        Set processing resolution from width and height values.

        Maps the dimensions to a preset if available, otherwise uses Custom mode.

        Args:
            width: Processing width in pixels
            height: Processing height in pixels
        """
        def _select(preset_key: str):
            self.resolution_preset.setCurrentIndex(self.resolution_preset.findData(preset_key))
            self.on_resolution_preset_changed()

        # Treat missing/sentinel values as "original" (no downsampling).
        if width is None or height is None:
            _select("original")
            return

        try:
            width = int(width)
            height = int(height)
        except (TypeError, ValueError):
            _select("original")
            return

        if width >= 99999 or height >= 99999:
            _select("original")
            return

        # Reverse map dimensions -> stable preset key
        dims_to_key = {dims: key for key, _, dims in self.resolution_presets if isinstance(dims, tuple)}
        preset_key = dims_to_key.get((width, height))
        if preset_key:
            _select(preset_key)
        else:
            _select("custom")
            self.processing_width.setValue(width)
            self.processing_height.setValue(height)

    def get_target_fps(self) -> int | None:
        """Get the target frame rate for processing.

        Returns:
            Target FPS value, or None for 'Source FPS'
        """
        return self._frame_rate_values.get(self.frame_rate_preset.currentData())

    def set_target_fps(self, fps: int | None):
        """Set the target frame rate.

        Args:
            fps: Target FPS value (None or 0 = Source FPS)
        """
        normalized_fps = None if fps is None or int(fps) <= 0 else int(fps)
        fps_to_key = {value: key for key, value in self._frame_rate_values.items()}
        preset_key = fps_to_key.get(normalized_fps, "source")
        self.frame_rate_preset.setCurrentIndex(self.frame_rate_preset.findData(preset_key))
