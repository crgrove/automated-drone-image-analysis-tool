"""
ImageAdjustmentDialog.py - Real-time image adjustment dialog for ADIAT

Provides exposure, highlights, shadows, clarity, and radius adjustments
with real-time preview similar to Paint.NET functionality.
"""

import numpy as np
import cv2
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog

from core.views.components.ImageAdjustmentDialog_ui import Ui_ImageAdjustmentDialog


class ImageAdjustmentDialog(QDialog, Ui_ImageAdjustmentDialog):
    """
    Dialog for real-time image adjustments including exposure, highlights, shadows, clarity, and radius.
    
    Signals:
        imageAdjusted: Emitted when adjustments are applied with the adjusted QPixmap
    """
    
    imageAdjusted = pyqtSignal(QPixmap)
    
    def __init__(self, parent=None, original_pixmap=None):
        """
        Initialize the Image Adjustment Dialog.
        
        Args:
            parent: Parent widget
            original_pixmap (QPixmap): Original image to adjust
        """
        super().__init__(parent)
        self.setupUi(self)
        
        self.original_pixmap = original_pixmap
        self.original_image = None
        self.adjusted_image = None
        
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
    
    def _connect_signals(self):
        """Connect slider and button signals."""
        # Slider connections for real-time updates
        self.exposureSlider.valueChanged.connect(self._on_exposure_changed)
        self.highlightsSlider.valueChanged.connect(self._on_highlights_changed)
        self.shadowsSlider.valueChanged.connect(self._on_shadows_changed)
        self.claritySlider.valueChanged.connect(self._on_clarity_changed)
        self.radiusSlider.valueChanged.connect(self._on_radius_changed)
        
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
        ptr.setsize(qimage.byteCount())
        
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
        self.exposureValue.setText(str(value))
        self._apply_real_time_adjustments()
    
    def _on_highlights_changed(self, value):
        """Handle highlights slider changes."""
        self.adjustments['highlights'] = value
        self.highlightsValue.setText(str(value))
        self._apply_real_time_adjustments()
    
    def _on_shadows_changed(self, value):
        """Handle shadows slider changes."""
        self.adjustments['shadows'] = value
        self.shadowsValue.setText(str(value))
        self._apply_real_time_adjustments()
    
    def _on_clarity_changed(self, value):
        """Handle clarity slider changes."""
        self.adjustments['clarity'] = value
        self.clarityValue.setText(str(value))
        self._apply_real_time_adjustments()
    
    def _on_radius_changed(self, value):
        """Handle radius slider changes."""
        self.adjustments['radius'] = value
        self.radiusValue.setText(str(value))
        self._apply_real_time_adjustments()
    
    def _apply_real_time_adjustments(self):
        """Apply adjustments in real-time and emit signal."""
        if self.original_image is None:
            return
        
        # Start with original image
        adjusted = self.original_image.astype(np.float32)
        
        # Apply exposure adjustment (affects entire image)
        if self.adjustments['exposure'] != 0:
            exposure_factor = 2 ** (self.adjustments['exposure'] / 50.0)
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
        highlights_adj = self.adjustments['highlights'] / 100.0
        shadows_adj = self.adjustments['shadows'] / 100.0
        
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
        clarity_strength = self.adjustments['clarity'] / 100.0
        
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
        # Reset sliders
        self.exposureSlider.setValue(0)
        self.highlightsSlider.setValue(0)
        self.shadowsSlider.setValue(0)
        self.claritySlider.setValue(0)
        self.radiusSlider.setValue(10)
        
        # Reset adjustments dict
        self.adjustments = {
            'exposure': 0,
            'highlights': 0,
            'shadows': 0,
            'clarity': 0,
            'radius': 10
        }
        
        # Update value labels
        self.exposureValue.setText("0")
        self.highlightsValue.setText("0")
        self.shadowsValue.setText("0")
        self.clarityValue.setText("0")
        self.radiusValue.setText("10")
        
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