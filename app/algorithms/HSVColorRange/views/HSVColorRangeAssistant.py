"""
HSV Color Range Assistant Tool - Version 5
Click-based selection with automatic similar pixel detection
"""

import sys
import math
import numpy as np
from typing import Optional, List, Tuple, Set
from dataclasses import dataclass
import cv2

from PyQt5.QtCore import (Qt, QPoint, QPointF, pyqtSignal, QTimer, QRectF, QRect)
from PyQt5.QtGui import (QPainter, QColor, QPen, QBrush, QPixmap, QImage, QFont,
                        QMouseEvent, QKeyEvent, QWheelEvent, QTransform, QCursor)
from PyQt5.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QSpinBox, QGroupBox, QGridLayout, 
                           QFileDialog, QSplitter, QGraphicsView, QGraphicsScene,
                           QGraphicsPixmapItem, QDialogButtonBox, QApplication,
                           QCheckBox, QGraphicsEllipseItem, QGraphicsItem,
                           QGraphicsTextItem)


@dataclass
class SelectionState:
    """Represents a selection state for undo/redo."""
    mask: np.ndarray
    pixel_count: int


class FastImageViewer(QGraphicsView):
    """Fast image viewer with click-based selection."""
    
    selectionChanged = pyqtSignal()
    cursorHSVChanged = pyqtSignal(int, int, int)  # H degrees, S percent, V percent
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Scene setup
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Image items
        self._photo = None
        self._overlay = None
        self._hsv_text_item = None
        
        # Image data
        self.image = None  # Original image (BGR)
        self.image_hsv = None  # HSV version
        self.selection_mask = None  # Boolean mask
        
        # Selection state
        self.radius = 10  # Selection radius
        self.tolerance = 10  # Color tolerance for similar pixels
        self.ctrl_pressed = False
        
        # Selected HSV values set - for tracking what colors are selected
        self.selected_hsv_ranges = []  # List of (h_min, h_max, s_min, s_max, v_min, v_max)
        
        # Undo/redo
        self.undo_stack = []
        self.redo_stack = []
        
        # View setup
        self.setRenderHint(QPainter.Antialiasing)
        self.setMouseTracking(True)
        
        # Custom cursor
        self.custom_cursor = None
        self.update_custom_cursor()
        
    def update_custom_cursor(self):
        """Create a circular cursor matching selection radius with center dot."""
        # Calculate actual radius in screen pixels
        zoom = self.transform().m11() if self.transform() else 1.0
        screen_radius = int(self.radius * zoom)
        screen_radius = max(10, min(200, screen_radius))
        
        # Create cursor pixmap
        cursor_size = screen_radius * 2 + 4
        pixmap = QPixmap(cursor_size, cursor_size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = cursor_size // 2
        
        # Draw outer circle (white with black outline for visibility)
        painter.setPen(QPen(QColor(0, 0, 0, 255), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center - screen_radius, center - screen_radius, 
                          screen_radius * 2, screen_radius * 2)
        
        painter.setPen(QPen(QColor(255, 255, 255, 255), 1))
        painter.drawEllipse(center - screen_radius, center - screen_radius, 
                          screen_radius * 2, screen_radius * 2)
        
        # Draw center dot
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(255, 0, 0, 255)))  # Red dot
        painter.drawEllipse(center - 2, center - 2, 4, 4)
        
        # Draw crosshair
        painter.setPen(QPen(QColor(255, 255, 255, 200), 1))
        painter.drawLine(center - 6, center, center - 2, center)
        painter.drawLine(center + 2, center, center + 6, center)
        painter.drawLine(center, center - 6, center, center - 2)
        painter.drawLine(center, center + 2, center, center + 6)
        
        painter.end()
        
        # Create cursor
        self.custom_cursor = QCursor(pixmap, center, center)
        
    def load_image(self, filepath: str) -> bool:
        """Load an image from file."""
        try:
            # Read image
            self.image = cv2.imread(filepath)
            if self.image is None:
                return False
                
            # Convert to HSV
            self.image_hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
            
            # Initialize masks
            h, w = self.image.shape[:2]
            self.selection_mask = np.zeros((h, w), dtype=bool)
            
            # Clear selected HSV ranges
            self.selected_hsv_ranges = []
            
            # Convert to RGB for display
            image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            height, width, channel = image_rgb.shape
            bytes_per_line = 3 * width
            qimg = QImage(image_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # Clear old items before clearing scene
            self._photo = None
            self._overlay = None
            self._hsv_text_item = None
            
            # Clear scene
            self.scene.clear()
            
            # Add image
            pixmap = QPixmap.fromImage(qimg)
            self._photo = self.scene.addPixmap(pixmap)
            
            # Create empty overlay
            self.create_overlay()
            
            # Add HSV text item
            self._hsv_text_item = QGraphicsTextItem()
            self._hsv_text_item.setDefaultTextColor(QColor(255, 255, 0))
            self._hsv_text_item.setFont(QFont("Arial", 10, QFont.Bold))
            self._hsv_text_item.setZValue(10)
            self.scene.addItem(self._hsv_text_item)
            
            # Fit in view
            self.fitInView(self._photo, Qt.KeepAspectRatio)
            
            # Update cursor after zoom
            self.update_custom_cursor()
            
            # Clear undo/redo
            self.undo_stack.clear()
            self.redo_stack.clear()
            
            return True
            
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
            
    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard shortcuts."""
        if event.key() == Qt.Key_Control:
            self.ctrl_pressed = True
            self.update_cursor_display()
        elif event.key() == Qt.Key_BracketLeft:
            self.set_radius(max(1, self.radius - 2))
        elif event.key() == Qt.Key_BracketRight:
            self.set_radius(min(50, self.radius + 2))
        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            if event.modifiers() & Qt.ShiftModifier:
                self.redo()
            else:
                self.undo()
        else:
            super().keyPressEvent(event)
            
    def keyReleaseEvent(self, event: QKeyEvent):
        """Handle key release."""
        if event.key() == Qt.Key_Control:
            self.ctrl_pressed = False
            self.update_cursor_display()
        super().keyReleaseEvent(event)
        
    def update_cursor_display(self):
        """Update cursor based on current state."""
        if self.ctrl_pressed:
            self.setCursor(self.custom_cursor if self.custom_cursor else Qt.CrossCursor)
            # Don't change drag mode here - let mouse press handle it
        else:
            self.setCursor(Qt.ArrowCursor)
            # Don't change drag mode here - let mouse press handle it
            
    def get_hsv_at_pos(self, scene_pos: QPointF) -> Optional[Tuple[int, int, int]]:
        """Get HSV value at position."""
        if self.image_hsv is None:
            return None
            
        x, y = int(scene_pos.x()), int(scene_pos.y())
        h, w = self.image_hsv.shape[:2]
        
        if 0 <= x < w and 0 <= y < h:
            hsv = self.image_hsv[y, x]
            return int(hsv[0]), int(hsv[1]), int(hsv[2])
        return None
        
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move."""
        scene_pos = self.mapToScene(event.pos())
        
        # Update HSV display
        if self._hsv_text_item and self.image_hsv is not None:
            hsv = self.get_hsv_at_pos(scene_pos)
            if hsv:
                h, s, v = hsv
                # Convert to standard ranges for display
                h_deg = h * 2  # OpenCV uses 0-179, standard is 0-360
                s_pct = int((s / 255) * 100)
                v_pct = int((v / 255) * 100)
                
                text = f"H:{h_deg}° S:{s_pct}% V:{v_pct}%"
                self._hsv_text_item.setPlainText(text)
                
                # Scale text to remain readable at all zoom levels
                zoom = self.transform().m11()
                scale_factor = 1.0 / zoom  # Inverse scale to maintain constant screen size
                scale_factor = max(0.5, min(5.0, scale_factor))  # Limit scaling range
                self._hsv_text_item.setScale(scale_factor)
                
                # Position text near cursor, adjusted for scale
                text_offset = 15 / zoom  # Adjust offset based on zoom
                text_pos = scene_pos + QPointF(text_offset, text_offset)
                self._hsv_text_item.setPos(text_pos)
                self._hsv_text_item.show()
                
                # Emit signal with the values
                self.cursorHSVChanged.emit(h_deg, s_pct, v_pct)
            else:
                self._hsv_text_item.hide()
                
        super().mouseMoveEvent(event)
            
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press - click to select similar pixels."""
        if event.button() == Qt.LeftButton:
            if self.ctrl_pressed:
                pos = self.mapToScene(event.pos())
                if self.is_in_image(pos):
                    # Save current state for undo
                    self.save_undo_state()
                    
                    # Get pixels in radius
                    center_x, center_y = int(pos.x()), int(pos.y())
                    h, w = self.image_hsv.shape[:2]
                    
                    # Determine if we're adding or removing
                    is_erasing = bool(event.modifiers() & Qt.ShiftModifier)
                    
                    # Collect HSV values from circle area
                    hsv_values = []
                    for dy in range(-self.radius, self.radius + 1):
                        for dx in range(-self.radius, self.radius + 1):
                            if dx*dx + dy*dy <= self.radius*self.radius:
                                px, py = center_x + dx, center_y + dy
                                if 0 <= px < w and 0 <= py < h:
                                    hsv_values.append(self.image_hsv[py, px])
                    
                    if hsv_values:
                        hsv_values = np.array(hsv_values)
                        
                        # Calculate range of selected pixels - use int to avoid overflow
                        h_min = int(np.min(hsv_values[:, 0]))
                        h_max = int(np.max(hsv_values[:, 0]))
                        s_min = int(np.min(hsv_values[:, 1]))
                        s_max = int(np.max(hsv_values[:, 1]))
                        v_min = int(np.min(hsv_values[:, 2]))
                        v_max = int(np.max(hsv_values[:, 2]))
                        
                        # Add tolerance - use int to avoid overflow
                        tolerance = int(self.tolerance)
                        h_min = max(0, h_min - tolerance)
                        h_max = min(179, h_max + tolerance)
                        s_min = max(0, s_min - tolerance)
                        s_max = min(255, s_max + tolerance)
                        v_min = max(0, v_min - tolerance)
                        v_max = min(255, v_max + tolerance)
                        
                        # Find all pixels in image matching this range
                        lower = np.array([h_min, s_min, v_min], dtype=np.uint8)
                        upper = np.array([h_max, s_max, v_max], dtype=np.uint8)
                        matching_mask = cv2.inRange(self.image_hsv, lower, upper) > 0
                        
                        # Update selection mask
                        if is_erasing:
                            self.selection_mask = self.selection_mask & ~matching_mask
                        else:
                            self.selection_mask = self.selection_mask | matching_mask
                            # Add to selected ranges
                            self.selected_hsv_ranges.append((h_min, h_max, s_min, s_max, v_min, v_max))
                        
                        # Update overlay
                        self.create_overlay()
                        
                        # Emit change signal
                        self.selectionChanged.emit()
                    
                    return
            else:
                # Enable panning when CTRL is not pressed
                self.setDragMode(QGraphicsView.ScrollHandDrag)
                    
        # Default handling (pan)
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release."""
        if event.button() == Qt.LeftButton:
            # Reset drag mode after panning
            self.setDragMode(QGraphicsView.NoDrag)
        super().mouseReleaseEvent(event)
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Double click to fit image."""
        if self._photo:
            self.fitInView(self._photo, Qt.KeepAspectRatio)
            self.update_custom_cursor()
            
    def wheelEvent(self, event: QWheelEvent):
        """Zoom with mouse wheel."""
        if self._photo:
            # Scale factor
            scale_factor = 1.15
            
            if event.angleDelta().y() > 0:
                # Zoom in
                self.scale(scale_factor, scale_factor)
            else:
                # Zoom out
                self.scale(1/scale_factor, 1/scale_factor)
                
            # Update cursor for new zoom level
            self.update_custom_cursor()
            
            # Update HSV text scale if visible
            if self._hsv_text_item and self._hsv_text_item.isVisible():
                zoom = self.transform().m11()
                text_scale = 1.0 / zoom
                text_scale = max(0.5, min(5.0, text_scale))
                self._hsv_text_item.setScale(text_scale)
            
            # Update cursor display if CTRL is pressed
            if self.ctrl_pressed:
                self.setCursor(self.custom_cursor if self.custom_cursor else Qt.CrossCursor)
                
    def enterEvent(self, event):
        """Handle mouse enter."""
        super().enterEvent(event)
        self.setFocus()  # Ensure we receive keyboard events
        
    def leaveEvent(self, event):
        """Handle mouse leave."""
        super().leaveEvent(event)
        if self._hsv_text_item:
            self._hsv_text_item.hide()
            
    def create_overlay(self):
        """Create or update the selection overlay."""
        if self.image is None:
            return
            
        h, w = self.image.shape[:2]
        
        # Create RGBA overlay
        overlay_array = np.zeros((h, w, 4), dtype=np.uint8)
        
        # Set white with transparency where mask is True
        overlay_array[self.selection_mask] = [255, 255, 255, 100]
        
        # Ensure C-contiguous array
        overlay_array = np.ascontiguousarray(overlay_array)
        
        # Convert to QImage
        bytes_per_line = 4 * w
        overlay = QImage(overlay_array.data, w, h, bytes_per_line, QImage.Format_RGBA8888)
        overlay = overlay.copy()
        
        # Remove old overlay if it exists and belongs to this scene
        if self._overlay and self._overlay.scene() == self.scene:
            self.scene.removeItem(self._overlay)
            self._overlay = None
            
        # Add new overlay
        pixmap = QPixmap.fromImage(overlay)
        self._overlay = self.scene.addPixmap(pixmap)
        self._overlay.setZValue(1)  # Above photo
        
    def set_radius(self, radius):
        """Set selection radius and update cursor."""
        self.radius = radius
        self.update_custom_cursor()
        
        # Update cursor immediately if Ctrl is pressed
        if self.ctrl_pressed:
            self.setCursor(self.custom_cursor if self.custom_cursor else Qt.CrossCursor)
            
    def set_tolerance(self, tolerance):
        """Set color tolerance for similar pixel detection."""
        self.tolerance = tolerance
        
    def is_in_image(self, scene_pos: QPointF) -> bool:
        """Check if position is within image bounds."""
        if self.image is None:
            return False
        h, w = self.image.shape[:2]
        x, y = int(scene_pos.x()), int(scene_pos.y())
        return 0 <= x < w and 0 <= y < h
        
    def save_undo_state(self):
        """Save current state for undo."""
        if self.selection_mask is not None:
            state = SelectionState(
                mask=self.selection_mask.copy(),
                pixel_count=np.sum(self.selection_mask)
            )
            self.undo_stack.append(state)
            # Limit stack size
            if len(self.undo_stack) > 50:
                self.undo_stack.pop(0)
            # Clear redo stack
            self.redo_stack.clear()
            
    def undo(self):
        """Undo last action."""
        if len(self.undo_stack) > 1:
            # Save current to redo
            current = SelectionState(
                mask=self.selection_mask.copy(),
                pixel_count=np.sum(self.selection_mask)
            )
            self.redo_stack.append(current)
            
            # Restore previous
            self.undo_stack.pop()  # Remove current
            prev = self.undo_stack[-1]
            self.selection_mask = prev.mask.copy()
            
            # Update display
            self.create_overlay()
            self.selectionChanged.emit()
            
    def redo(self):
        """Redo last undone action."""
        if self.redo_stack:
            # Save current
            self.save_undo_state()
            
            # Restore
            state = self.redo_stack.pop()
            self.selection_mask = state.mask.copy()
            
            # Update display
            self.create_overlay()
            self.selectionChanged.emit()
            
    def reset_selection(self):
        """Clear all selections."""
        if self.selection_mask is not None:
            self.save_undo_state()
            self.selection_mask.fill(False)
            self.selected_hsv_ranges.clear()
            self.create_overlay()
            self.selectionChanged.emit()
            
    def get_selected_pixels_hsv(self) -> Optional[np.ndarray]:
        """Get HSV values of selected pixels."""
        if self.image_hsv is None or not np.any(self.selection_mask):
            return None
        return self.image_hsv[self.selection_mask]


class HSVColorRangeAssistant(QDialog):
    """Main dialog for HSV Color Range Assistant tool."""
    
    rangeAccepted = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("HSV Color Range Assistant - Click Selection")
        self.setModal(True)
        self.resize(1200, 800)
        
        # Initialize ranges
        self.hsv_ranges = {
            'h_center': 0, 's_center': 0, 'v_center': 0,
            'h_minus': 0, 'h_plus': 0,
            's_minus': 0, 's_plus': 0,
            'v_minus': 0, 'v_plus': 0
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # Main content
        splitter = QSplitter(Qt.Horizontal)
        
        # Image viewer
        self.viewer = FastImageViewer()
        self.viewer.selectionChanged.connect(self.on_selection_changed)
        splitter.addWidget(self.viewer)
        
        # Right panel
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([700, 500])
        layout.addWidget(splitter)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def create_toolbar(self) -> QWidget:
        """Create toolbar."""
        toolbar = QWidget()
        layout = QHBoxLayout(toolbar)
        
        # Browse button
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_image)
        layout.addWidget(browse_btn)
        
        # Reset button
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_selection)
        layout.addWidget(reset_btn)
        
        # Selection radius
        layout.addWidget(QLabel("Selection Radius:"))
        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(1, 50)
        self.radius_spin.setValue(10)
        self.radius_spin.setSuffix(" px")
        self.radius_spin.valueChanged.connect(self.on_radius_changed)
        layout.addWidget(self.radius_spin)
        
        # Color tolerance
        layout.addWidget(QLabel("Color Tolerance:"))
        self.tolerance_spin = QSpinBox()
        self.tolerance_spin.setRange(0, 50)
        self.tolerance_spin.setValue(10)
        self.tolerance_spin.setToolTip("HSV tolerance for matching similar pixels")
        self.tolerance_spin.valueChanged.connect(self.on_tolerance_changed)
        layout.addWidget(self.tolerance_spin)
        
        
        layout.addStretch()
        
        # Help text
        help_text = QLabel(
            "CTRL+Click: Select similar colors | CTRL+SHIFT+Click: Remove | [ ] : Radius"
        )
        help_text.setStyleSheet("color: #666;")
        layout.addWidget(help_text)
        
        return toolbar
        
    def create_right_panel(self) -> QWidget:
        """Create right panel with info and controls."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Color info
        color_group = QGroupBox("Selected Color")
        color_layout = QGridLayout(color_group)
        
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(60, 60)
        self.color_preview.setStyleSheet("border: 1px solid black;")
        color_layout.addWidget(QLabel("Color:"), 0, 0)
        color_layout.addWidget(self.color_preview, 0, 1)
        
        self.hex_label = QLabel("#000000")
        color_layout.addWidget(QLabel("HEX:"), 1, 0)
        color_layout.addWidget(self.hex_label, 1, 1)
        
        self.hsv_label = QLabel("H:0 S:0 V:0")
        color_layout.addWidget(QLabel("HSV:"), 2, 0)
        color_layout.addWidget(self.hsv_label, 2, 1)
        
        layout.addWidget(color_group)
        
        # Ranges with separate minus/plus controls
        range_group = QGroupBox("HSV Ranges")
        range_layout = QGridLayout(range_group)
        
        # Headers
        range_layout.addWidget(QLabel("Channel"), 0, 0)
        range_layout.addWidget(QLabel("Center"), 0, 1)
        range_layout.addWidget(QLabel("- Buffer"), 0, 2)
        range_layout.addWidget(QLabel("+ Buffer"), 0, 3)
        range_layout.addWidget(QLabel("Final Range"), 0, 4)
        
        # H range
        range_layout.addWidget(QLabel("Hue:"), 1, 0)
        self.h_center_label = QLabel("0°")
        range_layout.addWidget(self.h_center_label, 1, 1)
        
        self.h_minus_buffer = QSpinBox()
        self.h_minus_buffer.setRange(0, 360)
        self.h_minus_buffer.setSuffix("°")
        self.h_minus_buffer.valueChanged.connect(self.update_ranges)
        range_layout.addWidget(self.h_minus_buffer, 1, 2)
        
        self.h_plus_buffer = QSpinBox()
        self.h_plus_buffer.setRange(0, 360)
        self.h_plus_buffer.setSuffix("°")
        self.h_plus_buffer.valueChanged.connect(self.update_ranges)
        range_layout.addWidget(self.h_plus_buffer, 1, 3)
        
        self.h_range_label = QLabel("0-0")
        range_layout.addWidget(self.h_range_label, 1, 4)
        
        # S range
        range_layout.addWidget(QLabel("Sat:"), 2, 0)
        self.s_center_label = QLabel("0%")
        range_layout.addWidget(self.s_center_label, 2, 1)
        
        self.s_minus_buffer = QSpinBox()
        self.s_minus_buffer.setRange(0, 100)
        self.s_minus_buffer.setSuffix("%")
        self.s_minus_buffer.valueChanged.connect(self.update_ranges)
        range_layout.addWidget(self.s_minus_buffer, 2, 2)
        
        self.s_plus_buffer = QSpinBox()
        self.s_plus_buffer.setRange(0, 100)
        self.s_plus_buffer.setSuffix("%")
        self.s_plus_buffer.valueChanged.connect(self.update_ranges)
        range_layout.addWidget(self.s_plus_buffer, 2, 3)
        
        self.s_range_label = QLabel("0-0")
        range_layout.addWidget(self.s_range_label, 2, 4)
        
        # V range
        range_layout.addWidget(QLabel("Val:"), 3, 0)
        self.v_center_label = QLabel("0%")
        range_layout.addWidget(self.v_center_label, 3, 1)
        
        self.v_minus_buffer = QSpinBox()
        self.v_minus_buffer.setRange(0, 100)
        self.v_minus_buffer.setSuffix("%")
        self.v_minus_buffer.valueChanged.connect(self.update_ranges)
        range_layout.addWidget(self.v_minus_buffer, 3, 2)
        
        self.v_plus_buffer = QSpinBox()
        self.v_plus_buffer.setRange(0, 100)
        self.v_plus_buffer.setSuffix("%")
        self.v_plus_buffer.valueChanged.connect(self.update_ranges)
        range_layout.addWidget(self.v_plus_buffer, 3, 3)
        
        self.v_range_label = QLabel("0-0")
        range_layout.addWidget(self.v_range_label, 3, 4)
        
        layout.addWidget(range_group)
        
        # Stats
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_group)
        self.pixel_count_label = QLabel("Selected Pixels: 0")
        self.selected_percent_label = QLabel("Coverage: 0%")
        stats_layout.addWidget(self.pixel_count_label)
        stats_layout.addWidget(self.selected_percent_label)
        layout.addWidget(stats_group)
        
        # Preview
        preview_group = QGroupBox("Mask Preview")
        preview_layout = QVBoxLayout(preview_group)
        self.preview_label = QLabel()
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setStyleSheet("border: 1px solid black; background: black;")
        self.preview_label.setScaledContents(True)
        preview_layout.addWidget(self.preview_label)
        layout.addWidget(preview_group)
        
        layout.addStretch()
        return panel
        
    def browse_image(self):
        """Browse for image file."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if filepath:
            self.viewer.load_image(filepath)
            
    def reset_selection(self):
        """Reset selection."""
        self.viewer.reset_selection()
        
    def on_radius_changed(self, value):
        """Update selection radius."""
        self.viewer.set_radius(value)
        
    def on_tolerance_changed(self, value):
        """Update color tolerance."""
        self.viewer.set_tolerance(value)
        
        
    def on_selection_changed(self):
        """Handle selection change."""
        self.update_ranges()
        
    def update_ranges(self):
        """Update HSV ranges from selection."""
        pixels = self.viewer.get_selected_pixels_hsv()
        
        if pixels is None or len(pixels) == 0:
            self.pixel_count_label.setText("Selected Pixels: 0")
            self.selected_percent_label.setText("Coverage: 0%")
            return
            
        # Update pixel count
        pixel_count = len(pixels)
        total_pixels = self.viewer.image.shape[0] * self.viewer.image.shape[1]
        percentage = (pixel_count / total_pixels) * 100
        self.pixel_count_label.setText(f"Selected Pixels: {pixel_count:,}")
        self.selected_percent_label.setText(f"Coverage: {percentage:.1f}%")
        
        # Calculate average
        h_mean = float(np.mean(pixels[:, 0]))
        s_mean = float(np.mean(pixels[:, 1]))
        v_mean = float(np.mean(pixels[:, 2]))
        
        # Calculate ranges
        h_min = float(np.min(pixels[:, 0]))
        h_max = float(np.max(pixels[:, 0]))
        s_min = float(np.min(pixels[:, 1]))
        s_max = float(np.max(pixels[:, 1]))
        v_min = float(np.min(pixels[:, 2]))
        v_max = float(np.max(pixels[:, 2]))
        
        # Get buffers
        h_minus_buffer = float(self.h_minus_buffer.value() / 2)  # Convert to OpenCV scale
        h_plus_buffer = float(self.h_plus_buffer.value() / 2)
        s_minus_buffer = float(self.s_minus_buffer.value() * 2.55)
        s_plus_buffer = float(self.s_plus_buffer.value() * 2.55)
        v_minus_buffer = float(self.v_minus_buffer.value() * 2.55)
        v_plus_buffer = float(self.v_plus_buffer.value() * 2.55)
        
        # Calculate deviations
        h_deviation_minus = h_mean - h_min
        h_deviation_plus = h_max - h_mean
        s_deviation_minus = s_mean - s_min
        s_deviation_plus = s_max - s_mean
        v_deviation_minus = v_mean - v_min
        v_deviation_plus = v_max - v_mean
        
        # Store ranges
        self.hsv_ranges = {
            'h_center': h_mean,
            's_center': s_mean,
            'v_center': v_mean,
            'h_minus': h_deviation_minus + h_minus_buffer,
            'h_plus': h_deviation_plus + h_plus_buffer,
            's_minus': s_deviation_minus + s_minus_buffer,
            's_plus': s_deviation_plus + s_plus_buffer,
            'v_minus': v_deviation_minus + v_minus_buffer,
            'v_plus': v_deviation_plus + v_plus_buffer
        }
        
        # Update displays
        self.update_displays()
        self.update_preview()
        
    def update_displays(self):
        """Update UI displays."""
        if not self.hsv_ranges:
            return
            
        # Color preview
        h = int(self.hsv_ranges['h_center'])
        s = int(self.hsv_ranges['s_center'])
        v = int(self.hsv_ranges['v_center'])
        
        # Convert to RGB
        hsv_color = np.array([[[h, s, v]]], dtype=np.uint8)
        rgb = cv2.cvtColor(hsv_color, cv2.COLOR_HSV2RGB)[0, 0]
        
        hex_color = "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
        self.color_preview.setStyleSheet(f"background-color: {hex_color}; border: 1px solid black;")
        self.hex_label.setText(hex_color.upper())
        self.hsv_label.setText(f"H:{h*2} S:{int(s/2.55)} V:{int(v/2.55)}")
        
        # Update center labels
        self.h_center_label.setText(f"{h*2}°")
        self.s_center_label.setText(f"{int(s/2.55)}%")
        self.v_center_label.setText(f"{int(v/2.55)}%")
        
        # Calculate final ranges
        h_low = max(0, h - self.hsv_ranges['h_minus'])
        h_high = min(179, h + self.hsv_ranges['h_plus'])
        s_low = max(0, s - self.hsv_ranges['s_minus'])
        s_high = min(255, s + self.hsv_ranges['s_plus'])
        v_low = max(0, v - self.hsv_ranges['v_minus'])
        v_high = min(255, v + self.hsv_ranges['v_plus'])
        
        # Update range labels
        self.h_range_label.setText(f"{int(h_low*2)}°-{int(h_high*2)}°")
        self.s_range_label.setText(f"{int(s_low/2.55)}%-{int(s_high/2.55)}%")
        self.v_range_label.setText(f"{int(v_low/2.55)}%-{int(v_high/2.55)}%")
            
    def update_preview(self):
        """Update mask preview."""
        if self.viewer.image_hsv is None:
            return
            
        # Calculate bounds
        h = float(self.hsv_ranges['h_center'])
        s = float(self.hsv_ranges['s_center'])
        v = float(self.hsv_ranges['v_center'])
        
        h_minus = float(self.hsv_ranges['h_minus'])
        h_plus = float(self.hsv_ranges['h_plus'])
        s_minus = float(self.hsv_ranges['s_minus'])
        s_plus = float(self.hsv_ranges['s_plus'])
        v_minus = float(self.hsv_ranges['v_minus'])
        v_plus = float(self.hsv_ranges['v_plus'])
        
        # Calculate bounds with proper clamping
        lower = np.array([
            int(np.clip(h - h_minus, 0, 179)),
            int(np.clip(s - s_minus, 0, 255)),
            int(np.clip(v - v_minus, 0, 255))
        ], dtype=np.uint8)
        
        upper = np.array([
            int(np.clip(h + h_plus, 0, 179)),
            int(np.clip(s + s_plus, 0, 255)),
            int(np.clip(v + v_plus, 0, 255))
        ], dtype=np.uint8)
        
        # Create mask
        mask = cv2.inRange(self.viewer.image_hsv, lower, upper)
        
        # Resize for preview
        preview = cv2.resize(mask, (300, 200))
        
        # Convert to QPixmap
        h, w = preview.shape
        qimg = QImage(preview.data, w, h, w, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimg)
        self.preview_label.setPixmap(pixmap)
        
    def accept(self):
        """Accept and emit ranges."""
        # Convert ranges to normalized format expected by HSV picker
        normalized_ranges = {
            'h_center': self.hsv_ranges['h_center'],  # Keep in OpenCV scale
            's_center': self.hsv_ranges['s_center'],  # Keep in OpenCV scale  
            'v_center': self.hsv_ranges['v_center'],  # Keep in OpenCV scale
            'h_minus': self.hsv_ranges['h_minus'] / 179,  # Convert to 0-1
            'h_plus': self.hsv_ranges['h_plus'] / 179,    # Convert to 0-1
            's_minus': self.hsv_ranges['s_minus'] / 255,  # Convert to 0-1
            's_plus': self.hsv_ranges['s_plus'] / 255,    # Convert to 0-1
            'v_minus': self.hsv_ranges['v_minus'] / 255,  # Convert to 0-1
            'v_plus': self.hsv_ranges['v_plus'] / 255     # Convert to 0-1
        }
        self.rangeAccepted.emit(normalized_ranges)
        super().accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = HSVColorRangeAssistant()
    dialog.show()
    sys.exit(app.exec_())