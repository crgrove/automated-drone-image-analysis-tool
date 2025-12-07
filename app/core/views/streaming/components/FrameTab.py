"""
FrameTab - Shared Frame/Mask tab for streaming algorithms.

This tab provides controls for defining processing regions using either
a pixel buffer from edges (Frame Mode), an image mask (Image Mask Mode),
or both combined. White areas are processed, black areas are excluded.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QLabel, QSpinBox, QCheckBox,
                               QGroupBox, QPushButton, QFileDialog,
                               QLineEdit, QMessageBox)
from PySide6.QtCore import Qt, Signal
from typing import Optional, Dict, Any
import os


class FrameTab(QWidget):
    """
    Shared Frame tab widget for streaming algorithms.

    Provides two combinable modes:
    - Frame Buffer: Exclude a uniform pixel buffer from all edges
    - Image Mask: Load a black/white image as a mask

    Both modes can be enabled together - masks are combined with AND logic.

    Signals:
        configChanged: Emitted when any configuration value changes
    """

    configChanged = Signal()

    def __init__(self, parent=None):
        """Initialize the Frame tab."""
        super().__init__(parent)
        self._mask_image_path: Optional[str] = None
        self._video_aspect_ratio: Optional[float] = None
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)

        # Enable checkbox
        self.enable_mask = QCheckBox("Enable Processing Region Mask")
        self.enable_mask.setChecked(False)
        self.enable_mask.setToolTip(
            "Enable to restrict detection processing to a specific region of the video.\n"
            "Useful for excluding edges, UI overlays, or focusing on specific areas.\n"
            "Improves performance by not processing masked regions."
        )
        layout.addWidget(self.enable_mask)

        # Container for all mask settings (enabled/disabled with checkbox)
        self.settings_container = QWidget()
        settings_layout = QVBoxLayout(self.settings_container)
        settings_layout.setContentsMargins(0, 0, 0, 0)

        # Frame Buffer Mode with checkbox
        self.enable_frame_buffer = QCheckBox("Enable Frame Buffer")
        self.enable_frame_buffer.setToolTip(
            "Exclude a uniform border from all edges of the video.\n"
            "Enter the number of pixels to exclude from each edge.\n"
            "The inner area will be processed for detections."
        )
        self.enable_frame_buffer.setChecked(True)
        settings_layout.addWidget(self.enable_frame_buffer)

        # Frame Mode Settings
        self.frame_settings_group = QGroupBox("Frame Buffer Settings")
        frame_layout = QGridLayout(self.frame_settings_group)
        frame_layout.setColumnMinimumWidth(0, 120)
        frame_layout.setColumnStretch(1, 1)

        frame_layout.addWidget(QLabel("Buffer (pixels):"), 0, 0)
        self.buffer_spinbox = QSpinBox()
        self.buffer_spinbox.setRange(0, 1000)
        self.buffer_spinbox.setValue(50)
        self.buffer_spinbox.setToolTip(
            "Number of pixels to exclude from all edges (0-1000).\n"
            "A value of 50 excludes 50 pixels from top, bottom, left, and right.\n"
            "Useful for removing UI overlays or camera lens distortion at edges.\n"
            "This value is based on the original video resolution."
        )
        frame_layout.addWidget(self.buffer_spinbox, 0, 1)

        settings_layout.addWidget(self.frame_settings_group)

        # Image Mask Mode with checkbox
        self.enable_image_mask = QCheckBox("Enable Image Mask")
        self.enable_image_mask.setToolTip(
            "Load a black/white image as a custom mask.\n"
            "White areas will be processed, black areas excluded.\n"
            "The mask will be scaled to match the video resolution."
        )
        self.enable_image_mask.setChecked(False)
        settings_layout.addWidget(self.enable_image_mask)

        # Image Mask Settings
        self.image_settings_group = QGroupBox("Image Mask Settings")
        image_layout = QVBoxLayout(self.image_settings_group)

        # File selection row
        file_layout = QHBoxLayout()
        self.mask_path_display = QLineEdit()
        self.mask_path_display.setReadOnly(True)
        self.mask_path_display.setPlaceholderText("No mask image selected")
        file_layout.addWidget(self.mask_path_display)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.setToolTip("Select a black/white image file to use as mask")
        file_layout.addWidget(self.browse_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setToolTip("Clear the selected mask image")
        file_layout.addWidget(self.clear_button)

        image_layout.addLayout(file_layout)

        # Info label
        info_label = QLabel("White = Process, Black = Exclude")
        info_label.setStyleSheet("color: gray; font-style: italic;")
        image_layout.addWidget(info_label)

        self.image_settings_group.setEnabled(False)
        settings_layout.addWidget(self.image_settings_group)

        # Visualization settings
        vis_group = QGroupBox("Visualization")
        vis_layout = QVBoxLayout(vis_group)

        self.show_mask_overlay = QCheckBox("Show mask overlay on video")
        self.show_mask_overlay.setChecked(True)
        self.show_mask_overlay.setToolTip(
            "Display the processing region on the rendered video.\n"
            "Frame mode: Shows a cyan rectangle outline of the processed area.\n"
            "Image mask: Shows a semi-transparent overlay of excluded regions."
        )
        vis_layout.addWidget(self.show_mask_overlay)

        settings_layout.addWidget(vis_group)

        layout.addWidget(self.settings_container)
        layout.addStretch()

        # Initial state - disable settings when mask is disabled
        self._update_enabled_state()

    def connect_signals(self):
        """Connect UI signals."""
        self.enable_mask.toggled.connect(self._on_enable_changed)
        self.enable_frame_buffer.toggled.connect(self._on_frame_buffer_toggled)
        self.enable_image_mask.toggled.connect(self._on_image_mask_toggled)
        self.buffer_spinbox.valueChanged.connect(self._emit_config_changed)
        self.browse_button.clicked.connect(self._on_browse_clicked)
        self.clear_button.clicked.connect(self._on_clear_clicked)
        self.show_mask_overlay.toggled.connect(self._emit_config_changed)

    def _on_enable_changed(self, enabled: bool):
        """Handle enable/disable toggle."""
        self._update_enabled_state()
        self._emit_config_changed()

    def _update_enabled_state(self):
        """Update enabled state of settings based on enable checkbox."""
        enabled = self.enable_mask.isChecked()
        self.settings_container.setEnabled(enabled)

    def _on_frame_buffer_toggled(self, checked: bool):
        """Handle frame buffer checkbox toggle."""
        self.frame_settings_group.setEnabled(checked)
        self._emit_config_changed()

    def _on_image_mask_toggled(self, checked: bool):
        """Handle image mask checkbox toggle."""
        self.image_settings_group.setEnabled(checked)
        self._emit_config_changed()

    def _on_browse_clicked(self):
        """Handle browse button click for image mask selection."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Mask Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)"
        )

        if file_path:
            self._validate_and_set_mask_image(file_path)

    def _on_clear_clicked(self):
        """Handle clear button click to remove mask image."""
        self._mask_image_path = None
        self.mask_path_display.clear()
        self.mask_path_display.setPlaceholderText("No mask image selected")
        self._emit_config_changed()

    def _validate_and_set_mask_image(self, file_path: str):
        """Validate mask image and set it if valid."""
        from core.services.streaming.MaskManager import MaskManager

        # Validate the image
        is_valid, error_msg, dimensions = MaskManager.validate_mask_image(
            file_path,
            self._video_aspect_ratio
        )

        if not is_valid:
            QMessageBox.warning(
                self, "Invalid Image",
                error_msg or "Could not load the selected image. Please choose a valid image file."
            )
            return

        # If there's an aspect ratio warning, show it
        if error_msg:  # This is the aspect ratio mismatch warning
            result = QMessageBox.warning(
                self, "Aspect Ratio Mismatch",
                f"{error_msg}\n\n"
                "The mask will be scaled to fit, which may cause distortion.\n\n"
                "Do you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if result != QMessageBox.Yes:
                return

        self._mask_image_path = file_path
        self.mask_path_display.setText(os.path.basename(file_path))
        self._emit_config_changed()

    def set_video_aspect_ratio(self, aspect_ratio: float):
        """
        Set the video aspect ratio for validation when loading mask images.

        Args:
            aspect_ratio: Video width / height ratio (e.g., 16/9 = 1.778)
        """
        self._video_aspect_ratio = aspect_ratio

    def set_video_resolution(self, width: int, height: int):
        """
        Set the video resolution for aspect ratio validation.

        Args:
            width: Video width in pixels
            height: Video height in pixels
        """
        if height > 0:
            self._video_aspect_ratio = width / height

    def _emit_config_changed(self):
        """Emit config changed signal."""
        self.configChanged.emit()

    def get_config(self) -> Dict[str, Any]:
        """
        Get current frame/mask configuration.

        Returns:
            Dictionary with mask configuration:
            - mask_enabled: bool
            - frame_mask_enabled: bool
            - image_mask_enabled: bool
            - frame_buffer_pixels: int
            - mask_image_path: str or None
            - show_mask_overlay: bool
        """
        return {
            'mask_enabled': self.enable_mask.isChecked(),
            'frame_mask_enabled': self.enable_frame_buffer.isChecked(),
            'image_mask_enabled': self.enable_image_mask.isChecked(),
            'frame_buffer_pixels': self.buffer_spinbox.value(),
            'mask_image_path': self._mask_image_path,
            'show_mask_overlay': self.show_mask_overlay.isChecked(),
        }

    def set_config(self, config: Dict[str, Any]):
        """
        Set frame/mask configuration from dictionary.

        Args:
            config: Dictionary with mask configuration keys
        """
        # Block signals to prevent multiple emissions
        self.blockSignals(True)

        try:
            if 'mask_enabled' in config:
                self.enable_mask.setChecked(bool(config['mask_enabled']))

            if 'frame_mask_enabled' in config:
                self.enable_frame_buffer.setChecked(bool(config['frame_mask_enabled']))
                self._on_frame_buffer_toggled(bool(config['frame_mask_enabled']))

            if 'image_mask_enabled' in config:
                self.enable_image_mask.setChecked(bool(config['image_mask_enabled']))
                self._on_image_mask_toggled(bool(config['image_mask_enabled']))

            if 'frame_buffer_pixels' in config:
                self.buffer_spinbox.setValue(int(config['frame_buffer_pixels']))

            if 'mask_image_path' in config and config['mask_image_path']:
                self._mask_image_path = config['mask_image_path']
                self.mask_path_display.setText(os.path.basename(config['mask_image_path']))

            if 'show_mask_overlay' in config:
                self.show_mask_overlay.setChecked(bool(config['show_mask_overlay']))

            self._update_enabled_state()
        finally:
            self.blockSignals(False)
