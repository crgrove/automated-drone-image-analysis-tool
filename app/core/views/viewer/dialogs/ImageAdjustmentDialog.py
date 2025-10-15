"""
ImageAdjustmentDialog.py - Real-time image adjustment dialog for ADIAT

Provides exposure, highlights, shadows, clarity, and radius adjustments
with real-time preview similar to Paint.NET functionality.

Features:
- Real-time updates while dragging sliders (sliderMoved signal)
- Fallback updates when sliders are released (valueChanged signal)
- Direct integer value entry via textbox inputs for precise control
- Input validation with range checking and automatic reversion
- Bidirectional synchronization between sliders and input fields
- Configurable debouncing for performance vs. responsiveness
- Use set_immediate_updates(True) for instant updates without delay
"""

import numpy as np
import cv2
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QSlider, QLineEdit, QPushButton, QGroupBox
)


class ImageAdjustmentDialog(QDialog):
    """
    Dialog for real-time image adjustments including exposure, highlights, shadows, clarity, and radius.

    Signals:
        imageAdjusted: Emitted when adjustments are applied with the adjusted QPixmap
    """

    imageAdjusted = Signal(QPixmap)

    def __init__(self, parent=None, original_pixmap=None):
        """
        Initialize the Image Adjustment Dialog.

        Args:
            parent: Parent widget
            original_pixmap (QPixmap): Original image to adjust
        """
        super().__init__(parent)
        self._setup_ui()  # Create UI programmatically

        self.original_pixmap = original_pixmap
        self.original_image = None
        self.adjusted_image = None

        # Performance optimization: debounce timer for real-time updates
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._apply_real_time_adjustments)
        self.debounce_delay = 50  # milliseconds - reduced for more responsive updates
        self.enable_debouncing = True  # Set to False for immediate updates (lower performance)

        # Performance monitoring
        self.update_count = 0
        self.last_update_time = 0

        # Convert QPixmap to numpy array for processing
        if original_pixmap:
            self._pixmap_to_array()

        # Connect signals
        self._connect_signals()

        # Initialize adjustments
        self.adjustments = {
            'exposure': 0,
            'highlights': 0,
            'shadows': 0,
            'clarity': 0,
            'radius': 10
        }

    def _setup_ui(self):
        """Create UI widgets programmatically."""
        self.setWindowTitle("Image Adjustment")
        self.setModal(False)
        self.resize(400, 400)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Create adjustment controls group
        adjustments_group = QGroupBox("Adjustments")
        grid_layout = QGridLayout()

        # Helper function to create slider row
        def create_slider_row(label_text, min_val, max_val, default_val, row):
            # Label
            label = QLabel(label_text)
            grid_layout.addWidget(label, row, 0)

            # Slider
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(min_val)
            slider.setMaximum(max_val)
            slider.setValue(default_val)
            slider.setTickPosition(QSlider.TicksBelow)
            slider.setTickInterval((max_val - min_val) // 10)
            grid_layout.addWidget(slider, row, 1)

            # Value input
            value_input = QLineEdit()
            value_input.setText(str(default_val))
            value_input.setMaximumWidth(60)
            grid_layout.addWidget(value_input, row, 2)

            return slider, value_input

        # Create sliders for each adjustment
        self.exposureSlider, self.exposureValueInput = create_slider_row(
            "Exposure:", -200, 200, 0, 0
        )
        self.highlightsSlider, self.highlightsValueInput = create_slider_row(
            "Highlights:", -200, 200, 0, 1
        )
        self.shadowsSlider, self.shadowsValueInput = create_slider_row(
            "Shadows:", -200, 200, 0, 2
        )
        self.claritySlider, self.clarityValueInput = create_slider_row(
            "Clarity:", -200, 200, 0, 3
        )
        self.radiusSlider, self.radiusValueInput = create_slider_row(
            "Radius:", 1, 100, 10, 4
        )

        adjustments_group.setLayout(grid_layout)
        main_layout.addWidget(adjustments_group)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.resetButton = QPushButton("Reset")
        self.applyButton = QPushButton("Apply")
        self.closeButton = QPushButton("Close")

        button_layout.addWidget(self.resetButton)
        button_layout.addWidget(self.applyButton)
        button_layout.addWidget(self.closeButton)

        main_layout.addLayout(button_layout)

    def _connect_signals(self):
        """Connect slider and button signals."""
        # Slider connections for real-time updates
        # Use sliderMoved for real-time updates while dragging
        self.exposureSlider.sliderMoved.connect(self._on_exposure_changed)
        self.highlightsSlider.sliderMoved.connect(self._on_highlights_changed)
        self.shadowsSlider.sliderMoved.connect(self._on_shadows_changed)
        self.claritySlider.sliderMoved.connect(self._on_clarity_changed)
        self.radiusSlider.sliderMoved.connect(self._on_radius_changed)

        # Also connect valueChanged for when slider is released or clicked
        self.exposureSlider.valueChanged.connect(self._on_exposure_changed)
        self.highlightsSlider.valueChanged.connect(self._on_highlights_changed)
        self.shadowsSlider.valueChanged.connect(self._on_shadows_changed)
        self.claritySlider.valueChanged.connect(self._on_clarity_changed)
        self.radiusSlider.valueChanged.connect(self._on_radius_changed)

        # Input field connections for direct value entry
        self.exposureValueInput.textChanged.connect(self._on_exposure_input_changed)
        self.highlightsValueInput.textChanged.connect(self._on_highlights_input_changed)
        self.shadowsValueInput.textChanged.connect(self._on_shadows_input_changed)
        self.clarityValueInput.textChanged.connect(self._on_clarity_input_changed)
        self.radiusValueInput.textChanged.connect(self._on_radius_input_changed)

        # Button connections
        self.resetButton.clicked.connect(self._reset_adjustments)
        self.applyButton.clicked.connect(self._apply_adjustments)
        self.closeButton.clicked.connect(self.close)

    def _pixmap_to_array(self):
        """Convert QPixmap to numpy array for processing."""
        if not self.original_pixmap:
            return

        qimage = self.original_pixmap.toImage()
        qimage = qimage.convertToFormat(QImage.Format_RGB888)

        width = qimage.width()
        height = qimage.height()
        ptr = qimage.bits()

        # PySide6/Python 3.8+ compatibility: memoryview.setsize() was removed
        # Instead, we use the size directly from the QImage
        byte_count = qimage.sizeInBytes()
        ptr = ptr[:byte_count]  # Slice to the correct size

        # Convert to numpy array
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 3))
        self.original_image = arr.copy()
        self.adjusted_image = arr.copy()

    def _array_to_pixmap(self, image_array):
        """Convert numpy array to QPixmap."""
        if image_array is None:
            return None

        height, width, channel = image_array.shape
        bytes_per_line = 3 * width

        # Ensure values are in valid range
        image_array = np.clip(image_array, 0, 255).astype(np.uint8)

        qimage = QImage(image_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(qimage)

    def _on_exposure_changed(self, value):
        """Handle exposure slider changes."""
        self.adjustments['exposure'] = value
        # Synchronize input field with slider
        if self.exposureValueInput.text() != str(value):
            self.exposureValueInput.setText(str(value))
        self._schedule_update()

    def _on_highlights_changed(self, value):
        """Handle highlights slider changes."""
        self.adjustments['highlights'] = value
        # Synchronize input field with slider
        if self.highlightsValueInput.text() != str(value):
            self.highlightsValueInput.setText(str(value))
        self._schedule_update()

    def _on_shadows_changed(self, value):
        """Handle shadows slider changes."""
        self.adjustments['shadows'] = value
        # Synchronize input field with slider
        if self.shadowsValueInput.text() != str(value):
            self.shadowsValueInput.setText(str(value))
        self._schedule_update()

    def _on_clarity_changed(self, value):
        """Handle clarity slider changes."""
        self.adjustments['clarity'] = value
        # Synchronize input field with slider
        if self.clarityValueInput.text() != str(value):
            self.clarityValueInput.setText(str(value))
        self._schedule_update()

    def _on_radius_changed(self, value):
        """Handle radius slider changes."""
        self.adjustments['radius'] = value
        # Synchronize input field with slider
        if self.radiusValueInput.text() != str(value):
            self.radiusValueInput.setText(str(value))
        self._schedule_update()

    def _on_exposure_input_changed(self, text):
        """Handle exposure input field changes."""
        try:
            value = int(text)
            # Validate range (-200 to 200)
            if -200 <= value <= 200:
                self.adjustments['exposure'] = value
                # Synchronize slider with input field
                if self.exposureSlider.value() != value:
                    self.exposureSlider.setValue(value)
                self._schedule_update()
            else:
                # Out of range, revert to current slider value
                self.exposureValueInput.setText(str(self.exposureSlider.value()))
        except ValueError:
            # Invalid input, revert to current slider value
            self.exposureValueInput.setText(str(self.exposureSlider.value()))

    def _on_highlights_input_changed(self, text):
        """Handle highlights input field changes."""
        try:
            value = int(text)
            # Validate range (-200 to 200)
            if -200 <= value <= 200:
                self.adjustments['highlights'] = value
                # Synchronize slider with input field
                if self.highlightsSlider.value() != value:
                    self.highlightsSlider.setValue(value)
                self._schedule_update()
            else:
                # Out of range, revert to current slider value
                self.highlightsValueInput.setText(str(self.highlightsSlider.value()))
        except ValueError:
            # Invalid input, revert to current slider value
            self.highlightsValueInput.setText(str(self.highlightsSlider.value()))

    def _on_shadows_input_changed(self, text):
        """Handle shadows input field changes."""
        try:
            value = int(text)
            # Validate range (-200 to 200)
            if -200 <= value <= 200:
                self.adjustments['shadows'] = value
                # Synchronize slider with input field
                if self.shadowsSlider.value() != value:
                    self.shadowsSlider.setValue(value)
                self._schedule_update()
            else:
                # Out of range, revert to current slider value
                self.shadowsValueInput.setText(str(self.shadowsSlider.value()))
        except ValueError:
            # Invalid input, revert to current slider value
            self.shadowsValueInput.setText(str(self.shadowsSlider.value()))

    def _on_clarity_input_changed(self, text):
        """Handle clarity input field changes."""
        try:
            value = int(text)
            # Validate range (-200 to 200)
            if -200 <= value <= 200:
                self.adjustments['clarity'] = value
                # Synchronize slider with input field
                if self.claritySlider.value() != value:
                    self.claritySlider.setValue(value)
                self._schedule_update()
            else:
                # Out of range, revert to current slider value
                self.clarityValueInput.setText(str(self.claritySlider.value()))
        except ValueError:
            # Invalid input, revert to current slider value
            self.clarityValueInput.setText(str(self.claritySlider.value()))

    def _on_radius_input_changed(self, text):
        """Handle radius input field changes."""
        try:
            value = int(text)
            # Validate range (1 to 100)
            if 1 <= value <= 100:
                self.adjustments['radius'] = value
                # Synchronize slider with input field
                if self.radiusSlider.value() != value:
                    self.radiusSlider.setValue(value)
                self._schedule_update()
            else:
                # Out of range, revert to current slider value
                self.radiusValueInput.setText(str(self.radiusSlider.value()))
        except ValueError:
            # Invalid input, revert to current slider value
            self.radiusValueInput.setText(str(self.radiusSlider.value()))

    def _schedule_update(self):
        """Schedule a debounced update to improve performance."""
        self.update_count += 1

        if self.enable_debouncing and self.debounce_delay > 0:
            self.update_timer.stop()
            self.update_timer.start(self.debounce_delay)
        else:
            # Apply updates immediately if debouncing is disabled
            self._apply_real_time_adjustments()

    def set_immediate_updates(self, enabled=True):
        """
        Enable or disable immediate updates for real-time responsiveness.

        Args:
            enabled (bool): If True, disables debouncing for immediate updates.
                           If False, enables debouncing for better performance.
        """
        if enabled:
            self.enable_debouncing = False
            self.debounce_delay = 0
        else:
            self.enable_debouncing = True
            self.debounce_delay = 50

    def _apply_real_time_adjustments(self):
        """Apply adjustments in real-time and emit signal."""
        if self.original_image is None:
            return

        # Start with original image
        adjusted = self.original_image.astype(np.float32)

        # Apply exposure adjustment (affects entire image) - optimized for expanded range
        if self.adjustments['exposure'] != 0:
            # Scale exposure factor calculation for expanded range
            exposure_factor = 2 ** (self.adjustments['exposure'] / 100.0)
            adjusted = adjusted * exposure_factor

        # Apply highlights and shadows adjustments with radius consideration
        if self.adjustments['highlights'] != 0 or self.adjustments['shadows'] != 0:
            adjusted = self._apply_highlights_shadows(adjusted)

        # Apply clarity adjustment
        if self.adjustments['clarity'] != 0:
            adjusted = self._apply_clarity(adjusted)

        # Clip values and convert back
        adjusted = np.clip(adjusted, 0, 255).astype(np.uint8)
        self.adjusted_image = adjusted

        # Convert to pixmap and emit signal
        adjusted_pixmap = self._array_to_pixmap(adjusted)
        if adjusted_pixmap:
            self.imageAdjusted.emit(adjusted_pixmap)

    def _apply_highlights_shadows(self, image):
        """Apply highlights and shadows adjustments with radius consideration."""
        radius = max(1, int(self.adjustments['radius']))
        # Scale adjustment factors for expanded range
        highlights_adj = self.adjustments['highlights'] / 200.0
        shadows_adj = self.adjustments['shadows'] / 200.0

        # Convert to grayscale for luminance mask
        gray = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_RGB2GRAY)

        # Create luminance masks with gaussian blur for smooth transitions
        kernel_size = radius * 2 + 1
        blurred = cv2.GaussianBlur(gray, (kernel_size, kernel_size), radius / 3.0)

        # Normalize to 0-1 range
        luminance = blurred.astype(np.float32) / 255.0

        # Create highlight and shadow masks
        highlight_mask = luminance  # Bright areas
        shadow_mask = 1.0 - luminance  # Dark areas

        # Apply adjustments
        result = image.copy()

        if highlights_adj != 0:
            # Reduce or increase highlights
            highlight_factor = 1.0 + (highlights_adj * highlight_mask[..., np.newaxis])
            result = result * highlight_factor

        if shadows_adj != 0:
            # Increase or decrease shadows
            shadow_factor = 1.0 + (shadows_adj * shadow_mask[..., np.newaxis])
            result = result * shadow_factor

        return result

    def _apply_clarity(self, image):
        """Apply clarity adjustment (unsharp mask effect)."""
        # Scale clarity strength for expanded range
        clarity_strength = self.adjustments['clarity'] / 200.0

        if abs(clarity_strength) < 0.01:
            return image

        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_RGB2GRAY)

        # Create unsharp mask
        kernel_size = 5
        blurred = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 1.0)
        mask = gray.astype(np.float32) - blurred.astype(np.float32)

        # Apply mask to each channel
        result = image.copy()
        for i in range(3):
            channel = result[:, :, i]
            if clarity_strength > 0:
                # Increase clarity
                result[:, :, i] = channel + (mask * clarity_strength * 0.5)
            else:
                # Decrease clarity (soften)
                result[:, :, i] = channel + (mask * clarity_strength * 0.3)

        return result

    def _reset_adjustments(self):
        """Reset all adjustments to default values."""
        # Reset sliders to default values
        self.exposureSlider.setValue(0)
        self.highlightsSlider.setValue(0)
        self.shadowsSlider.setValue(0)
        self.claritySlider.setValue(0)
        self.radiusSlider.setValue(10)

        # Reset input fields to default values
        self.exposureValueInput.setText("0")
        self.highlightsValueInput.setText("0")
        self.shadowsValueInput.setText("0")
        self.clarityValueInput.setText("0")
        self.radiusValueInput.setText("10")

        # Reset adjustments dict
        self.adjustments = {
            'exposure': 0,
            'highlights': 0,
            'shadows': 0,
            'clarity': 0,
            'radius': 10
        }

        # Apply reset
        self._apply_real_time_adjustments()

    def _apply_adjustments(self):
        """Apply current adjustments and close dialog."""
        self._apply_real_time_adjustments()
        self.accept()

    def get_adjusted_pixmap(self):
        """Get the current adjusted pixmap."""
        if self.adjusted_image is not None:
            return self._array_to_pixmap(self.adjusted_image)
        return self.original_pixmap
