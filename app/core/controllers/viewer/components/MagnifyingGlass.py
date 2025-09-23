"""
MagnifyingGlassController - Handles magnifying glass functionality for the image viewer.

This controller manages the magnifying glass widget that provides a zoomed view
of the area under the cursor when the middle mouse button is pressed.
"""

import numpy as np
import cv2
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QBrush, QCursor
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QLabel, QWidget
import qimage2ndarray

from core.services.LoggerService import LoggerService


class MagnifyingGlass:
    """
    Controller for managing the magnifying glass functionality.
    
    Provides a zoomed view of the area under the cursor when enabled.
    The magnifying glass can be toggled on/off with the middle mouse button.
    """
    
    def __init__(self, main_image_widget, logger=None, viewer=None):
        """
        Initialize the magnifying glass controller.
        
        Args:
            main_image_widget: The QtImageViewer widget that displays the main image
            logger: Optional logger instance for error reporting
            viewer: The Viewer instance that contains the image data
        """
        self.main_image = main_image_widget
        self.logger = logger or LoggerService()
        self.viewer = viewer
        
        # Magnifying glass state
        self.enabled = False
        self.widget = None
        
        # Configuration
        self.size = 400  # Size of the magnifying glass widget
        self.magnification_factor = 5.0  # Base magnification factor
        
    def toggle(self, x, y):
        """
        Toggle the magnifying glass on/off.
        
        Args:
            x (float): X coordinate where middle mouse was pressed
            y (float): Y coordinate where middle mouse was pressed
        """
        self.enabled = not self.enabled
        
        if self.enabled:
            self._show()
        else:
            self._hide()
    
    def _show(self):
        """Show the magnifying glass widget."""
        if self.widget is None:
            self._create_widget()
        
        if self.widget:
            self.widget.show()
            # Update it with current position
            current_pos = self.main_image.mapFromGlobal(QCursor.pos())
            scene_pos = self.main_image.mapToScene(current_pos)
            if self.main_image.hasImage():
                image_pos = QPoint(int(scene_pos.x()), int(scene_pos.y()))
                self.update_position(image_pos)
    
    def _hide(self):
        """Hide the magnifying glass widget."""
        if self.widget:
            self.widget.hide()
    
    def _create_widget(self):
        """Create the magnifying glass widget."""
        try:
            # Create a QLabel to display the magnified image
            self.widget = QLabel(self.main_image)
            self.widget.setFixedSize(self.size, self.size)
            
            # Style the magnifying glass with a border
            self.widget.setStyleSheet("""
                QLabel {
                    border: 2px solid #4A90E2;
                    border-radius: 200px;
                    background-color: black;
                }
            """)
            
            # Initially hide it
            self.widget.hide()
            
        except Exception as e:
            self.logger.error(f"Error creating magnifying glass: {e}")
            self.widget = None
    
    def update_position(self, image_pos):
        """
        Update the magnifying glass with the zoomed area under the cursor.
        
        Args:
            image_pos (QPoint): The position in image coordinates
        """
        if not self.widget or not self.enabled:
            return
        
        try:
            # Get the current image array from the viewer instance
            if not self.viewer or not hasattr(self.viewer, 'current_image_array'):
                return
                
            # Use the cached image array from the viewer
            img_array = self.viewer.current_image_array
            if img_array is None:
                self.logger.warning("No cached image array available for magnifying glass")
                return
            h, w = img_array.shape[:2]
            
            # Get current zoom level of the main viewer
            current_zoom = self.main_image.getZoom() if hasattr(self.main_image, 'getZoom') else 1.0
            
            # Calculate the source size for magnification
            # The source size should be such that when displayed at self.size,
            # it represents self.magnification_factor magnification relative to current zoom
            source_size = int(self.size / (self.magnification_factor * max(current_zoom, 0.1)))
            source_size = max(10, min(source_size, min(h, w)))  # Clamp to reasonable values
            
            half_size = source_size // 2
            
            # Ensure image_pos is within bounds
            x_pos = max(0, min(image_pos.x(), w - 1))
            y_pos = max(0, min(image_pos.y(), h - 1))
            
            # Calculate bounds for the source rectangle
            x_start = x_pos - half_size
            y_start = y_pos - half_size
            x_end = x_pos + half_size
            y_end = y_pos + half_size
            
            # Handle edge cases - create a padded region if necessary
            pad_left = max(0, -x_start)
            pad_top = max(0, -y_start)
            pad_right = max(0, x_end - w)
            pad_bottom = max(0, y_end - h)
            
            # Adjust coordinates to valid range
            x_start = max(0, x_start)
            y_start = max(0, y_start)
            x_end = min(w, x_end)
            y_end = min(h, y_end)
            
            # Extract the region
            region = img_array[y_start:y_end, x_start:x_end].copy()
            
            # Pad the region if we're at the edges
            if pad_left > 0 or pad_top > 0 or pad_right > 0 or pad_bottom > 0:
                padded = np.zeros((source_size, source_size, 3), dtype=np.uint8)
                padded[pad_top:pad_top + region.shape[0],
                       pad_left:pad_left + region.shape[1]] = region
                region = padded
            
            # Scale up the region to self.size using cv2 for better quality
            magnified = cv2.resize(region, (self.size, self.size), interpolation=cv2.INTER_LINEAR)
            
            # Convert to QImage and then QPixmap
            qimg = QImage(qimage2ndarray.array2qimage(magnified))
            pixmap = QPixmap.fromImage(qimg)
            
            # Draw crosshair on the magnified image
            painter = QPainter(pixmap)
            painter.setPen(QPen(QColor(255, 255, 0, 180), 2))
            center = self.size // 2
            painter.drawLine(center, 0, center, self.size)  # Vertical line
            painter.drawLine(0, center, self.size, center)  # Horizontal line
            painter.end()
            
            # Apply circular mask to make it look like a magnifying glass
            masked_pixmap = QPixmap(self.size, self.size)
            masked_pixmap.fill(Qt.transparent)
            
            painter = QPainter(masked_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Create circular clipping path
            painter.setBrush(QBrush(pixmap))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, self.size, self.size)
            
            # Draw border
            painter.setPen(QPen(QColor(74, 144, 226), 3))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(2, 2, self.size - 4, self.size - 4)
            painter.end()
            
            # Set the pixmap to the label
            self.widget.setPixmap(masked_pixmap)
            
            # Position the magnifying glass near the cursor
            cursor_pos = self.main_image.mapFromGlobal(QCursor.pos())
            
            # Offset the magnifying glass so it doesn't cover the cursor
            offset_x = 30
            offset_y = 30
            
            # Calculate position, keeping it within bounds
            new_x = cursor_pos.x() + offset_x
            new_y = cursor_pos.y() + offset_y
            
            # Adjust if it goes off the edge of the viewer
            if new_x + self.size > self.main_image.width():
                new_x = cursor_pos.x() - self.size - 30  # Show on left side
            if new_y + self.size > self.main_image.height():
                new_y = cursor_pos.y() - self.size - 30  # Show above
            
            self.widget.move(new_x, new_y)
            
        except Exception as e:
            self.logger.error(f"Error updating magnifying glass: {e}")
    
    def is_enabled(self):
        """Check if the magnifying glass is currently enabled."""
        return self.enabled
    
    def cleanup(self):
        """Clean up the magnifying glass widget."""
        if self.widget:
            self.widget.hide()
            self.widget.deleteLater()
            self.widget = None
        self.enabled = False
