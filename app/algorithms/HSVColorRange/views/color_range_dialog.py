"""
Color Range Dialog - Enhanced HSV color selection dialog

Uses the new HSVRangePickerWidget to provide an advanced interface for
selecting HSV color ranges with real-time visual feedback.
"""

import cv2
import numpy as np
from typing import Tuple, Optional

from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QImage, QColor, QPainter, QBrush, QPen
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QCheckBox, QGroupBox,
                            QSizePolicy, QGridLayout, QColorDialog)

from .hsv_range_picker import HSVRangePickerWidget
from core.services.CustomColorsService import get_custom_colors_service


class ColorRangeDialog(QDialog):
    """Advanced color range selection dialog with live preview."""
    
    # Signal emitted when color selection is accepted
    colorSelected = pyqtSignal(dict)  # HSV range data
    
    def __init__(self, initial_image=None, initial_hsv=(0, 1, 1), 
                 initial_ranges=None, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("HSV Color Range Selection")
        self.setModal(True)
        self.resize(1000, 800)
        
        # Store initial values
        self.original_image = initial_image
        self.processed_image = None
        
        # Initialize ranges
        if initial_ranges is None:
            initial_ranges = {
                'h_minus': 20/360, 'h_plus': 20/360,
                's_minus': 0.2, 's_plus': 0.2,
                'v_minus': 0.2, 'v_plus': 0.2
            }
        
        # Setup UI
        self.setup_ui()
        
        # Set initial values
        h, s, v = initial_hsv
        self.color_picker.set_hsv(h, s, v)
        self.color_picker.h_minus = initial_ranges['h_minus']
        self.color_picker.h_plus = initial_ranges['h_plus']
        self.color_picker.s_minus = initial_ranges['s_minus']
        self.color_picker.s_plus = initial_ranges['s_plus']
        self.color_picker.v_minus = initial_ranges['v_minus']
        self.color_picker.v_plus = initial_ranges['v_plus']
        self.color_picker.update_display()
        
        # Connect signals
        self.connect_signals()
        
        # Setup preview timer
        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self.update_preview)
        self.preview_timer.setSingleShot(True)
        
        # Initial preview update
        if self.original_image is not None:
            self.update_preview()
            
    def setup_ui(self):
        """Setup the dialog UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left side - Color picker
        picker_group = QGroupBox("Color Range Selection")
        picker_layout = QVBoxLayout(picker_group)
        
        self.color_picker = HSVRangePickerWidget()
        picker_layout.addWidget(self.color_picker)
        
        # Add custom colors section
        custom_colors_widget = self.create_custom_colors_widget()
        picker_layout.addWidget(custom_colors_widget)
        
        content_layout.addWidget(picker_group)
        
        # Right side - Preview (if image provided)
        if self.original_image is not None:
            preview_group = self.create_preview_panel()
            content_layout.addWidget(preview_group)
            
        main_layout.addLayout(content_layout)
        
        # Bottom buttons
        button_layout = self.create_button_layout()
        main_layout.addLayout(button_layout)
        
    def create_preview_panel(self):
        """Create the image preview panel."""
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        # Original image
        self.original_label = QLabel("Original Image")
        self.original_label.setAlignment(Qt.AlignCenter)
        self.original_label.setStyleSheet("QLabel { background-color: black; border: 1px solid gray; }")
        self.original_label.setMinimumSize(300, 225)
        self.original_label.setScaledContents(True)
        
        # Processed image  
        self.processed_label = QLabel("Filtered Result")
        self.processed_label.setAlignment(Qt.AlignCenter)
        self.processed_label.setStyleSheet("QLabel { background-color: black; border: 1px solid gray; }")
        self.processed_label.setMinimumSize(300, 225)
        self.processed_label.setScaledContents(True)
        
        # Show mask option
        self.show_mask_cb = QCheckBox("Show mask only")
        self.show_mask_cb.toggled.connect(self.on_preview_option_changed)
        
        preview_layout.addWidget(QLabel("Original:"))
        preview_layout.addWidget(self.original_label)
        preview_layout.addWidget(QLabel("Result:"))
        preview_layout.addWidget(self.processed_label)
        preview_layout.addWidget(self.show_mask_cb)
        preview_layout.addStretch()
        
        # Set initial original image
        if self.original_image is not None:
            self.set_image_to_label(self.original_label, self.original_image)
            
        return preview_group
        
    def create_button_layout(self):
        """Create the bottom button layout."""
        button_layout = QHBoxLayout()
        
        # Test button (if image available)
        if self.original_image is not None:
            self.test_button = QPushButton("Test on Image")
            self.test_button.clicked.connect(self.update_preview)
            button_layout.addWidget(self.test_button)
            
        button_layout.addStretch()
        
        # Standard dialog buttons
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        return button_layout
    
    def create_custom_colors_widget(self):
        """Create custom colors widget with swatches."""
        custom_frame = QFrame()
        custom_frame.setFrameStyle(QFrame.StyledPanel)
        custom_layout = QVBoxLayout(custom_frame)
        
        # Title and buttons
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Custom Colors"))
        
        # Standard color dialog button
        std_dialog_btn = QPushButton("Standard Dialog...")
        std_dialog_btn.setMaximumWidth(120)
        std_dialog_btn.clicked.connect(self.open_standard_dialog)
        header_layout.addWidget(std_dialog_btn)
        
        # Add current color button
        add_btn = QPushButton("Add Current")
        add_btn.setMaximumWidth(100)
        add_btn.clicked.connect(self.add_current_to_custom)
        header_layout.addWidget(add_btn)
        
        header_layout.addStretch()
        custom_layout.addLayout(header_layout)
        
        # Color swatches grid
        swatch_grid = QGridLayout()
        swatch_grid.setSpacing(4)
        
        self.color_swatches = []
        custom_colors_service = get_custom_colors_service()
        
        for i in range(16):  # 16 custom colors (4x4 grid)
            row = i // 4
            col = i % 4
            
            swatch = ColorSwatchButton(i)
            swatch.colorSelected.connect(self.on_custom_color_selected)
            self.color_swatches.append(swatch)
            swatch_grid.addWidget(swatch, row, col)
        
        custom_layout.addLayout(swatch_grid)
        
        # Load existing custom colors
        self.refresh_custom_colors()
        
        return custom_frame
    
    def refresh_custom_colors(self):
        """Refresh the custom color swatches from QColorDialog."""
        for i, swatch in enumerate(self.color_swatches):
            color = QColorDialog.customColor(i)
            swatch.set_color(color if color.isValid() else None)
    
    def on_custom_color_selected(self, color):
        """Handle selection of a custom color swatch."""
        if color and color.isValid():
            h, s, v, _ = color.getHsvF()
            self.color_picker.set_hsv(h, s, v)
    
    def add_current_to_custom(self):
        """Add the current color to custom colors."""
        h, s, v = self.color_picker.h, self.color_picker.s, self.color_picker.v
        color = QColor.fromHsvF(h, s, v)
        
        custom_colors_service = get_custom_colors_service()
        custom_colors_service.add_custom_color(color)
        
        # Refresh display
        self.refresh_custom_colors()
    
    def open_standard_dialog(self):
        """Open standard QColorDialog for more options."""
        # Get current color
        h, s, v = self.color_picker.h, self.color_picker.s, self.color_picker.v
        current_color = QColor.fromHsvF(h, s, v)
        
        # Ensure custom colors are loaded
        custom_colors_service = get_custom_colors_service()
        
        # Open dialog
        color = QColorDialog.getColor(current_color, self, "Select Color")
        
        # Sync custom colors
        custom_colors_service.sync_with_dialog()
        self.refresh_custom_colors()
        
        # Apply selected color
        if color.isValid():
            h, s, v, _ = color.getHsvF()
            self.color_picker.set_hsv(h, s, v)
        
    def connect_signals(self):
        """Connect color picker signals."""
        self.color_picker.colorChanged.connect(self.on_color_changed)
        self.color_picker.rangeChanged.connect(self.on_range_changed)
        
    def on_color_changed(self, h, s, v):
        """Handle color changes."""
        # Delayed preview update to avoid too frequent updates
        if self.original_image is not None:
            self.preview_timer.start(100)  # 100ms delay
            
    def on_range_changed(self, h_minus, h_plus, s_minus, s_plus, v_minus, v_plus):
        """Handle range changes."""
        # Delayed preview update
        if self.original_image is not None:
            self.preview_timer.start(100)
            
    def on_preview_option_changed(self):
        """Handle preview option changes."""
        if self.original_image is not None:
            self.update_preview()
            
    def update_preview(self):
        """Update the preview image with current HSV settings."""
        if self.original_image is None:
            return
            
        try:
            # Get current HSV ranges
            ranges = self.color_picker.get_hsv_ranges()
            center_h, center_s, center_v = ranges['center']
            (h_minus, h_plus), (s_minus, s_plus), (v_minus, v_plus) = ranges['ranges']
            
            # Calculate HSV bounds
            h_low = max(0, center_h - h_minus)
            h_high = min(179, center_h + h_plus)
            s_low = max(0, center_s - s_minus)
            s_high = min(255, center_s + s_plus)
            v_low = max(0, center_v - v_minus)
            v_high = min(255, center_v + v_plus)
            
            # Convert image to HSV
            hsv_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2HSV)
            
            # Create mask
            mask = cv2.inRange(hsv_image, 
                             np.array([h_low, s_low, v_low]),
                             np.array([h_high, s_high, v_high]))
            
            # Create result image
            if hasattr(self, 'show_mask_cb') and self.show_mask_cb.isChecked():
                # Show mask as grayscale
                result = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            else:
                # Show masked original
                result = cv2.bitwise_and(self.original_image, self.original_image, mask=mask)
                
            # Update preview
            self.set_image_to_label(self.processed_label, result)
            self.processed_image = result
            
        except Exception as e:
            print(f"Error updating preview: {e}")
            
    def set_image_to_label(self, label, cv_image):
        """Convert OpenCV image to QPixmap and set to label."""
        try:
            if len(cv_image.shape) == 3:
                # Color image
                height, width, channels = cv_image.shape
                bytes_per_line = channels * width
                rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
                q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            else:
                # Grayscale image
                height, width = cv_image.shape
                q_image = QImage(cv_image.data, width, height, width, QImage.Format_Grayscale8)
                
            pixmap = QPixmap.fromImage(q_image)
            label.setPixmap(pixmap)
            
        except Exception as e:
            print(f"Error setting image to label: {e}")
            
    def get_hsv_ranges(self):
        """Get the selected HSV ranges."""
        ranges = self.color_picker.get_hsv_ranges()
        
        return {
            'center_hsv': ranges['center'],
            'h_range': ranges['ranges'][0],
            's_range': ranges['ranges'][1], 
            'v_range': ranges['ranges'][2],
            'h': self.color_picker.h,
            's': self.color_picker.s,
            'v': self.color_picker.v,
            'h_minus': self.color_picker.h_minus,
            'h_plus': self.color_picker.h_plus,
            's_minus': self.color_picker.s_minus,
            's_plus': self.color_picker.s_plus,
            'v_minus': self.color_picker.v_minus,
            'v_plus': self.color_picker.v_plus
        }
        
    def accept(self):
        """Accept dialog and emit color selection signal."""
        color_data = self.get_hsv_ranges()
        self.colorSelected.emit(color_data)
        super().accept()


class ColorSwatchButton(QPushButton):
    """Custom button widget for color swatches."""
    
    colorSelected = pyqtSignal(QColor)
    
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.color = None
        self.setFixedSize(32, 32)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self.on_clicked)
        self.update_display()
    
    def set_color(self, color):
        """Set the color of this swatch."""
        self.color = color
        self.update_display()
    
    def update_display(self):
        """Update the visual display of the swatch."""
        if self.color and self.color.isValid():
            # Set background to the color
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.color.name()};
                    border: 2px solid #666;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    border: 2px solid #fff;
                }}
            """)
            self.setToolTip(f"RGB: ({self.color.red()}, {self.color.green()}, {self.color.blue()})")
        else:
            # Empty swatch
            self.setStyleSheet("""
                QPushButton {
                    background-color: #444;
                    border: 1px dashed #666;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    border: 1px dashed #888;
                }
            """)
            self.setToolTip("Empty slot - add a custom color")
    
    def on_clicked(self):
        """Handle click on swatch."""
        if self.color and self.color.isValid():
            self.colorSelected.emit(self.color)
    
    def paintEvent(self, event):
        """Custom paint for better color display."""
        super().paintEvent(event)
        
        if self.color and self.color.isValid():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw a small white/black checkmark for visibility
            painter.setPen(Qt.white if self.color.lightness() < 128 else Qt.black)
            if self.index == 0:  # Mark the most recent with a small dot
                painter.drawEllipse(self.width() - 8, 4, 4, 4)


# Standalone function to show color picker dialog
def show_color_picker_dialog(image=None, initial_hsv=(0, 1, 1), initial_ranges=None, parent=None):
    """
    Show color picker dialog and return selected HSV ranges.
    
    Args:
        image: Optional OpenCV image for preview
        initial_hsv: Initial HSV values (0-1 range)
        initial_ranges: Initial range values
        parent: Parent widget
        
    Returns:
        dict: HSV range data if accepted, None if cancelled
    """
    dialog = ColorRangeDialog(image, initial_hsv, initial_ranges, parent)
    
    if dialog.exec_() == QDialog.Accepted:
        return dialog.get_hsv_ranges()
    else:
        return None


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test with a sample image
    test_image = np.zeros((300, 400, 3), dtype=np.uint8)
    test_image[:, :100] = [0, 0, 255]    # Red
    test_image[:, 100:200] = [0, 255, 0]  # Green  
    test_image[:, 200:300] = [255, 0, 0]  # Blue
    test_image[:, 300:] = [255, 255, 255] # White
    
    result = show_color_picker_dialog(test_image)
    if result:
        print("Selected HSV ranges:", result)
    else:
        print("Dialog cancelled")
        
    sys.exit(app.exec_())