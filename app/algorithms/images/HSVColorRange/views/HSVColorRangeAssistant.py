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

from PySide6.QtCore import (Qt, QPoint, QPointF, Signal, QRectF, QRect)
from PySide6.QtGui import (QPainter, QColor, QPen, QBrush, QPixmap, QImage, QFont,
                           QMouseEvent, QKeyEvent, QWheelEvent, QTransform, QCursor)
from PySide6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QSpinBox, QGroupBox, QGridLayout,
                               QFileDialog, QSplitter, QGraphicsView, QGraphicsScene,
                               QGraphicsPixmapItem, QDialogButtonBox, QApplication,
                               QCheckBox, QGraphicsEllipseItem, QGraphicsItem,
                               QGraphicsTextItem, QMessageBox)


@dataclass
class SelectionState:
    """Represents a selection state for undo/redo."""
    mask: np.ndarray
    pixel_count: int


class FastImageViewer(QGraphicsView):
    """Fast image viewer with click-based selection.

    Interactive image viewer that allows users to select pixels by clicking
    and automatically expands selection to similar colors. Supports undo/redo
    and real-time HSV value display.

    Attributes:
        selectionChanged: Signal emitted when selection changes.
        cursorHSVChanged: Signal emitted when cursor moves over image.
            Emits (H, S, V) values.
    """

    selectionChanged = Signal()
    cursorHSVChanged = Signal(int, int, int)  # H degrees, S percent, V percent

    def __init__(self, parent=None):
        """Initialize the fast image viewer.

        Args:
            parent: Parent widget. Defaults to None.
        """
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
        self.radius = 1  # Selection radius (default 1 px)
        self.tolerance = 2  # Color tolerance for similar pixels (default 2)
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
        """Create a circular cursor matching selection radius with center dot.

        Generates a custom cursor that shows the selection radius as a circle
        with a center dot and crosshair for precise pixel selection.
        """
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
        """Load an image from file.

        Args:
            filepath: Path to the image file.

        Returns:
            True if image loaded successfully, False otherwise.
        """
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
        """Handle keyboard shortcuts.

        Supports:
        - Ctrl: Enable erase mode
        - [ / ]: Decrease/increase selection radius
        - Ctrl+Z: Undo
        - Ctrl+Shift+Z: Redo

        Args:
            event: Key press event.
        """
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
        """Handle key release.

        Updates cursor display when Ctrl key is released.

        Args:
            event: Key release event.
        """
        if event.key() == Qt.Key_Control:
            self.ctrl_pressed = False
            self.update_cursor_display()
        super().keyReleaseEvent(event)

    def update_cursor_display(self):
        """Update cursor based on current state.

        Shows custom cursor when Ctrl is pressed (erase mode), otherwise
        shows default arrow cursor.
        """
        if self.ctrl_pressed:
            self.setCursor(self.custom_cursor if self.custom_cursor else Qt.CrossCursor)
            # Don't change drag mode here - let mouse press handle it
        else:
            self.setCursor(Qt.ArrowCursor)
            # Don't change drag mode here - let mouse press handle it

    def get_hsv_at_pos(self, scene_pos: QPointF) -> Optional[Tuple[int, int, int]]:
        """Get HSV value at position.

        Args:
            scene_pos: Scene position as QPointF.

        Returns:
            HSV tuple (H, S, V) if position is within image bounds, None otherwise.
        """
        if self.image_hsv is None:
            return None

        x, y = int(scene_pos.x()), int(scene_pos.y())
        h, w = self.image_hsv.shape[:2]

        if 0 <= x < w and 0 <= y < h:
            hsv = self.image_hsv[y, x]
            return int(hsv[0]), int(hsv[1]), int(hsv[2])
        return None

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move.

        Updates HSV text display at cursor position and emits cursorHSVChanged signal.

        Args:
            event: Mouse move event.
        """
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
        """Handle mouse press - click to select similar pixels.

        When Ctrl is pressed, selects or erases pixels based on color similarity.
        Otherwise enables panning mode.

        Args:
            event: Mouse press event.
        """
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
                            if dx * dx + dy * dy <= self.radius * self.radius:
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
        """Handle mouse release.

        Resets drag mode after panning.

        Args:
            event: Mouse release event.
        """
        if event.button() == Qt.LeftButton:
            # Reset drag mode after panning
            self.setDragMode(QGraphicsView.NoDrag)
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Double click to fit image.

        Fits the image to view and updates cursor.

        Args:
            event: Mouse double click event.
        """
        if self._photo:
            self.fitInView(self._photo, Qt.KeepAspectRatio)
            self.update_custom_cursor()

    def wheelEvent(self, event: QWheelEvent):
        """Zoom with mouse wheel.

        Zooms in/out and updates cursor and HSV text scale.

        Args:
            event: Wheel event.
        """
        if self._photo:
            # Scale factor
            scale_factor = 1.15

            if event.angleDelta().y() > 0:
                # Zoom in
                self.scale(scale_factor, scale_factor)
            else:
                # Zoom out
                self.scale(1 / scale_factor, 1 / scale_factor)

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
        """Handle mouse enter.

        Sets focus to receive keyboard events.

        Args:
            event: Enter event.
        """
        super().enterEvent(event)
        self.setFocus()  # Ensure we receive keyboard events

    def leaveEvent(self, event):
        """Handle mouse leave.

        Hides HSV text display when mouse leaves the viewer.

        Args:
            event: Leave event.
        """
        super().leaveEvent(event)
        if self._hsv_text_item:
            self._hsv_text_item.hide()

    def create_overlay(self):
        """Create or update the selection overlay.

        Generates a semi-transparent white overlay showing selected pixels
        on top of the image.
        """
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
        """Set selection radius and update cursor.

        Args:
            radius: Selection radius in pixels.
        """
        self.radius = radius
        self.update_custom_cursor()

        # Update cursor immediately if Ctrl is pressed
        if self.ctrl_pressed:
            self.setCursor(self.custom_cursor if self.custom_cursor else Qt.CrossCursor)

    def set_tolerance(self, tolerance):
        """Set color tolerance for similar pixel detection.

        Args:
            tolerance: Color tolerance value for HSV range expansion.
        """
        self.tolerance = tolerance

    def is_in_image(self, scene_pos: QPointF) -> bool:
        """Check if position is within image bounds.

        Args:
            scene_pos: Scene position as QPointF.

        Returns:
            True if position is within image bounds, False otherwise.
        """
        if self.image is None:
            return False
        h, w = self.image.shape[:2]
        x, y = int(scene_pos.x()), int(scene_pos.y())
        return 0 <= x < w and 0 <= y < h

    def save_undo_state(self):
        """Save current state for undo.

        Saves a copy of the current selection mask to the undo stack.
        Limits stack size to 50 states and clears redo stack.
        """
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
        """Undo last action.

        Restores the previous selection state from the undo stack and
        updates the display.
        """
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
        """Redo last undone action.

        Restores the next selection state from the redo stack and
        updates the display.
        """
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
        """Clear all selections.

        Clears the selection mask, overlay, and selected HSV ranges.
        Updates the display and emits selectionChanged signal.
        """
        if self.selection_mask is not None:
            self.save_undo_state()
            self.selection_mask.fill(False)
            self.selected_hsv_ranges.clear()
            self.create_overlay()
            self.selectionChanged.emit()

    def get_selected_pixels_hsv(self) -> Optional[np.ndarray]:
        """Get HSV values of selected pixels.

        Returns:
            Numpy array of HSV values for selected pixels, or None if no
            image is loaded or no pixels are selected.
        """
        if self.image_hsv is None or not np.any(self.selection_mask):
            return None
        return self.image_hsv[self.selection_mask]


class HSVColorRangeAssistant(QDialog):
    """Main dialog for HSV Color Range Assistant tool.

    Interactive tool for selecting HSV color ranges by clicking on
    image pixels. Provides real-time mask preview and range adjustment.

    Attributes:
        rangeAccepted: Signal emitted when ranges are accepted.
            Emits dictionary with HSV range parameters.
        hsv_ranges: Dictionary containing HSV range parameters.
    """

    rangeAccepted = Signal(dict)

    def __init__(self, parent=None):
        """Initialize the HSV Color Range Assistant dialog.

        Args:
            parent: Parent widget. Defaults to None.
        """
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
        """Set up the user interface.

        Creates toolbar, image viewer, and mask preview sections.
        Sets up signal connections for interactive color selection.
        """
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)

        # Main content
        splitter = QSplitter(Qt.Horizontal)

        # Image viewer
        self.viewer = FastImageViewer()
        self.viewer.setToolTip(
            "Interactive image viewer with color selection.\n\n"
            "NAVIGATION:\n"
            "• Mouse wheel: Zoom in/out\n"
            "• Left-click drag: Pan around image\n"
            "• Double-click: Fit image to view\n\n"
            "COLOR SELECTION:\n"
            "• Hold CTRL + Left-click: Select similar colors\n"
            "• Hold CTRL+SHIFT + Left-click: Remove/erase selection\n"
            "• [ ] keys: Adjust selection radius\n"
            "• CTRL+Z: Undo last selection\n"
            "• CTRL+SHIFT+Z: Redo\n\n"
            "DISPLAY:\n"
            "• White overlay = selected pixels\n"
            "• Yellow text = HSV values at cursor position\n"
            "• Circular cursor appears when holding CTRL"
        )
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
        """Create toolbar.

        Creates a toolbar widget with buttons for browsing images,
        resetting selection, and showing help.

        Returns:
            QWidget containing the toolbar.
        """
        toolbar = QWidget()
        layout = QHBoxLayout(toolbar)

        # Browse button
        browse_btn = QPushButton("Browse...")
        browse_btn.setToolTip(
            "Browse for an image file to load.\n"
            "Opens a file dialog to select an image from your computer.\n"
            "• Supported formats: PNG, JPG, JPEG, BMP\n"
            "• Load an image to start selecting colors\n"
            "The image will be displayed in the main viewer on the left."
        )
        browse_btn.clicked.connect(self.browse_image)
        layout.addWidget(browse_btn)

        # Reset button
        reset_btn = QPushButton("Reset")
        reset_btn.setToolTip(
            "Reset all selections and start over.\n"
            "• Clears all selected pixels (white overlay)\n"
            "• Resets HSV ranges to defaults\n"
            "• Clears the mask preview\n"
            "• Undoable with CTRL+Z\n"
            "Use this to start fresh without reloading the image."
        )
        reset_btn.clicked.connect(self.reset_selection)
        layout.addWidget(reset_btn)

        # Selection radius
        radius_label = QLabel("Selection Radius:")
        radius_label.setToolTip(
            "Size of the circular selection cursor.\n"
            "Determines how many pixels are sampled when you CTRL+Click."
        )
        layout.addWidget(radius_label)
        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(1, 50)
        self.radius_spin.setValue(1)  # Default 1 px
        self.radius_spin.setSuffix(" px")
        self.radius_spin.setToolTip(
            "Set the selection cursor radius in pixels.\n"
            "• Range: 1-50 pixels\n"
            "• Default: 1 pixel (single pixel selection)\n"
            "Larger radius:\n"
            "• Samples more pixels when clicking\n"
            "• Averages colors within the circle\n"
            "• Good for selecting gradients or textured areas\n"
            "Smaller radius:\n"
            "• More precise selection\n"
            "• Better for solid colors\n"
            "Keyboard shortcuts: [ decrease, ] increase by 2 pixels"
        )
        self.radius_spin.valueChanged.connect(self.on_radius_changed)
        layout.addWidget(self.radius_spin)

        # Color tolerance
        tolerance_label = QLabel("Color Tolerance:")
        tolerance_label.setToolTip(
            "HSV color matching tolerance.\n"
            "Controls how similar colors must be to get selected."
        )
        layout.addWidget(tolerance_label)
        self.tolerance_spin = QSpinBox()
        self.tolerance_spin.setRange(0, 50)
        self.tolerance_spin.setValue(2)  # Default 2
        self.tolerance_spin.setToolTip(
            "Set color tolerance for similar pixel detection.\n"
            "• Range: 0-50\n"
            "• Default: 2\n"
            "When you CTRL+Click, pixels are selected if their HSV values are within this tolerance:\n"
            "• 0: Exact match only (very strict)\n"
            "• 2-5: Small variations (recommended for most cases)\n"
            "• 10+: Large variations (may select too many colors)\n"
            "Higher tolerance:\n"
            "• Selects more similar colors\n"
            "• Good for images with lighting variation\n"
            "• May include unwanted colors\n"
            "Lower tolerance:\n"
            "• More precise color matching\n"
            "• May miss some pixels of target color"
        )
        self.tolerance_spin.valueChanged.connect(self.on_tolerance_changed)
        layout.addWidget(self.tolerance_spin)

        layout.addStretch()

        # Help text
        help_text = QLabel(
            "CTRL+Click: Select similar colors | CTRL+SHIFT+Click: Remove | [ ] : Radius"
        )
        help_text.setStyleSheet("color: #666;")
        layout.addWidget(help_text)

        # Help button (right side)
        help_btn = QPushButton("Help")
        help_btn.setToolTip(
            "Show detailed help and instructions.\n"
            "Opens a dialog with:\n"
            "• Step-by-step usage instructions\n"
            "• Navigation controls explanation\n"
            "• Color selection techniques\n"
            "• Keyboard shortcuts reference\n"
            "Click here if you're unsure how to use this tool."
        )
        help_btn.clicked.connect(self.show_help)
        layout.addWidget(help_btn)

        return toolbar

    def create_right_panel(self) -> QWidget:
        """Create right panel with info and controls.

        Creates the right panel containing color preview, HSV range controls,
        statistics, and mask preview.

        Returns:
            QWidget containing the right panel.
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Color info
        color_group = QGroupBox("Selected Color")
        color_group.setToolTip(
            "Average color of all selected pixels.\n"
            "Shows the center/mean color that will be used for HSV range detection."
        )
        color_layout = QGridLayout(color_group)

        color_label = QLabel("Color:")
        color_label.setToolTip(
            "Visual preview of the average selected color.\n"
            "This is the center color calculated from all selected pixels."
        )
        color_layout.addWidget(color_label, 0, 0)
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(60, 60)
        self.color_preview.setStyleSheet("border: 1px solid black;")
        self.color_preview.setToolTip(
            "Color swatch showing the average of all selected pixels.\n"
            "This becomes the center color for HSV range detection."
        )
        color_layout.addWidget(self.color_preview, 0, 1)

        hex_info_label = QLabel("HEX:")
        hex_info_label.setToolTip(
            "Hexadecimal representation of the selected color.\n"
            "Format: #RRGGBB"
        )
        color_layout.addWidget(hex_info_label, 1, 0)
        self.hex_label = QLabel("#000000")
        self.hex_label.setToolTip(
            "Hex color code of the average selected color.\n"
            "Can be used to identify the exact RGB color value."
        )
        color_layout.addWidget(self.hex_label, 1, 1)

        hsv_info_label = QLabel("HSV:")
        hsv_info_label.setToolTip(
            "HSV values of the selected color.\n"
            "H = Hue (0-360°), S = Saturation (0-100%), V = Value (0-100%)"
        )
        color_layout.addWidget(hsv_info_label, 2, 0)
        self.hsv_label = QLabel("H:0 S:0 V:0")
        self.hsv_label.setToolTip(
            "HSV color values of the average selected color.\n"
            "This is the center point of your color range."
        )
        color_layout.addWidget(self.hsv_label, 2, 1)

        layout.addWidget(color_group)

        # Ranges with separate minus/plus controls
        range_group = QGroupBox("HSV Ranges")
        range_group.setToolTip(
            "HSV color range configuration.\n"
            "Defines the detection range for each HSV channel.\n"
            "Center values are calculated from selected pixels.\n"
            "Buffer values add extra tolerance to catch color variations."
        )
        range_layout = QGridLayout(range_group)

        # Headers
        channel_header = QLabel("Channel")
        channel_header.setToolTip("HSV color channel (Hue, Saturation, Value)")
        range_layout.addWidget(channel_header, 0, 0)

        center_header = QLabel("Center")
        center_header.setToolTip("Average value of selected pixels for this channel")
        range_layout.addWidget(center_header, 0, 1)

        minus_header = QLabel("- Buffer")
        minus_header.setToolTip("Extra tolerance below center value (lower bound buffer)")
        range_layout.addWidget(minus_header, 0, 2)

        plus_header = QLabel("+ Buffer")
        plus_header.setToolTip("Extra tolerance above center value (upper bound buffer)")
        range_layout.addWidget(plus_header, 0, 3)

        final_header = QLabel("Final Range")
        final_header.setToolTip("Complete detection range (min-max) after applying buffers")
        range_layout.addWidget(final_header, 0, 4)

        # H range
        hue_label = QLabel("Hue:")
        hue_label.setToolTip("Hue channel (color type): 0-360 degrees on color wheel")
        range_layout.addWidget(hue_label, 1, 0)

        self.h_center_label = QLabel("0°")
        self.h_center_label.setToolTip(
            "Center hue value (average of selected pixels).\n"
            "Automatically calculated from your selection.\n"
            "Range: 0-360° (red=0°, green=120°, blue=240°)"
        )
        range_layout.addWidget(self.h_center_label, 1, 1)

        self.h_minus_buffer = QSpinBox()
        self.h_minus_buffer.setRange(0, 360)
        self.h_minus_buffer.setSuffix("°")
        self.h_minus_buffer.setToolTip(
            "Hue lower bound buffer (subtract from center).\n"
            "• Range: 0-360°\n"
            "• Adds tolerance below the center hue\n"
            "• Larger values detect more hues in the minus direction\n"
            "• Keep narrow to avoid detecting unwanted colors\n"
            "WARNING: Total hue range (minus + plus) > 60° may cause false positives"
        )
        self.h_minus_buffer.valueChanged.connect(self.update_ranges)
        range_layout.addWidget(self.h_minus_buffer, 1, 2)

        self.h_plus_buffer = QSpinBox()
        self.h_plus_buffer.setRange(0, 360)
        self.h_plus_buffer.setSuffix("°")
        self.h_plus_buffer.setToolTip(
            "Hue upper bound buffer (add to center).\n"
            "• Range: 0-360°\n"
            "• Adds tolerance above the center hue\n"
            "• Larger values detect more hues in the plus direction\n"
            "• Keep narrow to avoid detecting unwanted colors\n"
            "WARNING: Total hue range (minus + plus) > 60° may cause false positives"
        )
        self.h_plus_buffer.valueChanged.connect(self.update_ranges)
        range_layout.addWidget(self.h_plus_buffer, 1, 3)

        self.h_range_label = QLabel("0-0")
        self.h_range_label.setToolTip(
            "Final hue detection range.\n"
            "Shows the complete min-max hue range that will be detected.\n"
            "Calculated as: (center - minus buffer) to (center + plus buffer)"
        )
        range_layout.addWidget(self.h_range_label, 1, 4)

        # Hue warning label
        self.h_warning_label = QLabel("WARNING: Too wide of a Hue range can result in false positives!")
        self.h_warning_label.setStyleSheet("color: yellow; font-size: 10px;")
        self.h_warning_label.setVisible(False)
        self.h_warning_label.setToolTip(
            "Hue range warning.\n"
            "Your total hue range exceeds 60°.\n"
            "Wide hue ranges may detect many different colors.\n"
            "Consider narrowing the buffers for more accurate detection."
        )
        range_layout.addWidget(self.h_warning_label, 2, 0, 1, 5)  # Span across columns

        # S range
        sat_label = QLabel("Sat:")
        sat_label.setToolTip("Saturation channel (color intensity): 0-100%")
        range_layout.addWidget(sat_label, 3, 0)

        self.s_center_label = QLabel("0%")
        self.s_center_label.setToolTip(
            "Center saturation value (average of selected pixels).\n"
            "Automatically calculated from your selection.\n"
            "Range: 0-100% (0%=gray, 100%=vivid color)"
        )
        range_layout.addWidget(self.s_center_label, 3, 1)

        self.s_minus_buffer = QSpinBox()
        self.s_minus_buffer.setRange(0, 100)
        self.s_minus_buffer.setSuffix("%")
        self.s_minus_buffer.setToolTip(
            "Saturation lower bound buffer (subtract from center).\n"
            "• Range: 0-100%\n"
            "• Adds tolerance below the center saturation\n"
            "• Larger values detect more desaturated/grayish colors\n"
            "• Be careful: very low saturation includes gray colors\n"
            "WARNING: Lower bound < 25% may include unwanted gray/desaturated colors"
        )
        self.s_minus_buffer.valueChanged.connect(self.update_ranges)
        range_layout.addWidget(self.s_minus_buffer, 3, 2)

        self.s_plus_buffer = QSpinBox()
        self.s_plus_buffer.setRange(0, 100)
        self.s_plus_buffer.setSuffix("%")
        self.s_plus_buffer.setToolTip(
            "Saturation upper bound buffer (add to center).\n"
            "• Range: 0-100%\n"
            "• Adds tolerance above the center saturation\n"
            "• Larger values detect more saturated/vivid colors\n"
            "• Higher saturation generally safe to increase"
        )
        self.s_plus_buffer.valueChanged.connect(self.update_ranges)
        range_layout.addWidget(self.s_plus_buffer, 3, 3)

        self.s_range_label = QLabel("0-0")
        self.s_range_label.setToolTip(
            "Final saturation detection range.\n"
            "Shows the complete min-max saturation range that will be detected.\n"
            "Calculated as: (center - minus buffer) to (center + plus buffer)"
        )
        range_layout.addWidget(self.s_range_label, 3, 4)

        # Saturation warning label
        self.s_warning_label = QLabel("WARNING: Too low of a Saturation level can result in false positives!")
        self.s_warning_label.setStyleSheet("color: yellow; font-size: 10px;")
        self.s_warning_label.setVisible(False)
        self.s_warning_label.setToolTip(
            "Saturation range warning.\n"
            "Your lower saturation bound is below 25%.\n"
            "Low saturation includes grayish/washed out colors.\n"
            "May detect unwanted gray or desaturated objects."
        )
        range_layout.addWidget(self.s_warning_label, 4, 0, 1, 5)

        # V range
        val_label = QLabel("Val:")
        val_label.setToolTip("Value channel (brightness): 0-100%")
        range_layout.addWidget(val_label, 5, 0)

        self.v_center_label = QLabel("0%")
        self.v_center_label.setToolTip(
            "Center value/brightness (average of selected pixels).\n"
            "Automatically calculated from your selection.\n"
            "Range: 0-100% (0%=black, 100%=bright)"
        )
        range_layout.addWidget(self.v_center_label, 5, 1)

        self.v_minus_buffer = QSpinBox()
        self.v_minus_buffer.setRange(0, 100)
        self.v_minus_buffer.setSuffix("%")
        self.v_minus_buffer.setToolTip(
            "Value lower bound buffer (subtract from center).\n"
            "• Range: 0-100%\n"
            "• Adds tolerance below the center brightness\n"
            "• Larger values detect darker versions of the color\n"
            "• Be careful: very low value includes very dark/black colors\n"
            "WARNING: Lower bound < 25% may include unwanted shadows or dark objects"
        )
        self.v_minus_buffer.valueChanged.connect(self.update_ranges)
        range_layout.addWidget(self.v_minus_buffer, 5, 2)

        self.v_plus_buffer = QSpinBox()
        self.v_plus_buffer.setRange(0, 100)
        self.v_plus_buffer.setSuffix("%")
        self.v_plus_buffer.setToolTip(
            "Value upper bound buffer (add to center).\n"
            "• Range: 0-100%\n"
            "• Adds tolerance above the center brightness\n"
            "• Larger values detect brighter versions of the color\n"
            "• Higher brightness generally safe to increase"
        )
        self.v_plus_buffer.valueChanged.connect(self.update_ranges)
        range_layout.addWidget(self.v_plus_buffer, 5, 3)

        self.v_range_label = QLabel("0-0")
        self.v_range_label.setToolTip(
            "Final value/brightness detection range.\n"
            "Shows the complete min-max brightness range that will be detected.\n"
            "Calculated as: (center - minus buffer) to (center + plus buffer)"
        )
        range_layout.addWidget(self.v_range_label, 5, 4)

        # Value warning label
        self.v_warning_label = QLabel("WARNING: Too low of a Value level can result in false positives!")
        self.v_warning_label.setStyleSheet("color: yellow; font-size: 10px;")
        self.v_warning_label.setVisible(False)
        self.v_warning_label.setToolTip(
            "Value range warning.\n"
            "Your lower value bound is below 25%.\n"
            "Low value includes very dark colors.\n"
            "May detect unwanted shadows or dark objects."
        )
        range_layout.addWidget(self.v_warning_label, 6, 0, 1, 5)

        layout.addWidget(range_group)

        # Stats
        stats_group = QGroupBox("Statistics")
        stats_group.setToolTip(
            "Statistics about your current selection.\n"
            "Shows how many pixels are selected and what percentage of the image they represent."
        )
        stats_layout = QVBoxLayout(stats_group)
        self.pixel_count_label = QLabel("Selected Pixels: 0")
        self.pixel_count_label.setToolTip(
            "Number of pixels currently selected.\n"
            "Shows the total count of white-highlighted pixels in the main viewer.\n"
            "Updates in real-time as you select colors."
        )
        stats_layout.addWidget(self.pixel_count_label)
        self.selected_percent_label = QLabel("Coverage: 0%")
        self.selected_percent_label.setToolTip(
            "Percentage of image covered by selection.\n"
            "Shows what portion of the total image is selected.\n"
            "• Low %: Precise selection, may miss some target pixels\n"
            "• High %: Broad selection, may include unwanted areas"
        )
        stats_layout.addWidget(self.selected_percent_label)
        layout.addWidget(stats_group)

        # Preview
        preview_group = QGroupBox("Mask Preview")
        preview_group.setToolTip(
            "Black and white preview of the detection mask.\n"
            "Shows what pixels will be detected with current HSV ranges and buffers."
        )
        preview_layout = QVBoxLayout(preview_group)
        self.preview_label = QLabel()
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setMinimumWidth(300)
        self.preview_label.setStyleSheet("border: 1px solid black; background: black;")
        self.preview_label.setScaledContents(False)  # We handle scaling manually
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setToolTip(
            "Grayscale mask preview.\n"
            "• White pixels: Will be detected with current settings\n"
            "• Black pixels: Will NOT be detected\n"
            "Updates automatically when you adjust buffers.\n"
            "Use this to verify your HSV range captures the target without false positives."
        )
        preview_layout.addWidget(self.preview_label)
        layout.addWidget(preview_group)

        layout.addStretch()
        return panel

    def browse_image(self):
        """Browse for image file.

        Opens a file dialog to select an image and loads it into the viewer.
        """
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if filepath:
            self.viewer.load_image(filepath)

    def reset_selection(self):
        """Reset selection.

        Clears all selections in the viewer and resets displays.
        """
        self.viewer.reset_selection()

    def on_radius_changed(self, value):
        """Update selection radius.

        Args:
            value: New selection radius value.
        """
        self.viewer.set_radius(value)

    def on_tolerance_changed(self, value):
        """Update color tolerance.

        Args:
            value: New color tolerance value.
        """
        self.viewer.set_tolerance(value)

    def on_selection_changed(self):
        """Handle selection change.

        Called when the viewer's selection changes. Updates HSV ranges
        and displays based on the new selection.
        """
        self.update_ranges()

    def update_ranges(self):
        """Update HSV ranges from selection.

        Calculates HSV center values and ranges from selected pixels,
        applies buffer values, and updates all displays and preview.
        """
        pixels = self.viewer.get_selected_pixels_hsv()

        if pixels is None or len(pixels) == 0:
            self.pixel_count_label.setText("Selected Pixels: 0")
            self.selected_percent_label.setText("Coverage: 0%")
            # Clear the mask preview when no pixels are selected
            self.preview_label.clear()
            # Reset all color and HSV range displays to defaults
            self.reset_displays()
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

    def reset_displays(self):
        """Reset all display values to defaults.

        Resets color preview, labels, and HSV ranges to default/empty state.
        Hides all warning labels.
        """
        # Reset color preview to neutral gray
        self.color_preview.setStyleSheet("background-color: #808080; border: 1px solid black;")
        self.hex_label.setText("#000000")
        self.hsv_label.setText("H:0 S:0 V:0")

        # Reset center labels
        self.h_center_label.setText("0°")
        self.s_center_label.setText("0%")
        self.v_center_label.setText("0%")

        # Reset range labels
        self.h_range_label.setText("0°-0°")
        self.s_range_label.setText("0%-0%")
        self.v_range_label.setText("0%-0%")

        # Reset the hsv_ranges to default
        self.hsv_ranges = {
            'h_center': 0, 's_center': 0, 'v_center': 0,
            'h_minus': 0, 'h_plus': 0,
            's_minus': 0, 's_plus': 0,
            'v_minus': 0, 'v_plus': 0
        }

        # Hide all warning labels
        if hasattr(self, 'h_warning_label'):
            self.h_warning_label.setVisible(False)
        if hasattr(self, 's_warning_label'):
            self.s_warning_label.setVisible(False)
        if hasattr(self, 'v_warning_label'):
            self.v_warning_label.setVisible(False)

    def update_displays(self):
        """Update UI displays.

        Updates color preview, center labels, range labels, and warning
        labels based on current HSV ranges.
        """
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
        self.hsv_label.setText(f"H:{h * 2} S:{int(s / 2.55)} V:{int(v / 2.55)}")

        # Update center labels
        self.h_center_label.setText(f"{h * 2}°")
        self.s_center_label.setText(f"{int(s / 2.55)}%")
        self.v_center_label.setText(f"{int(v / 2.55)}%")

        # Calculate final ranges
        h_low = max(0, h - self.hsv_ranges['h_minus'])
        h_high = min(179, h + self.hsv_ranges['h_plus'])
        s_low = max(0, s - self.hsv_ranges['s_minus'])
        s_high = min(255, s + self.hsv_ranges['s_plus'])
        v_low = max(0, v - self.hsv_ranges['v_minus'])
        v_high = min(255, v + self.hsv_ranges['v_plus'])

        # Update range labels
        self.h_range_label.setText(f"{int(h_low * 2)}°-{int(h_high * 2)}°")
        self.s_range_label.setText(f"{int(s_low / 2.55)}%-{int(s_high / 2.55)}%")
        self.v_range_label.setText(f"{int(v_low / 2.55)}%-{int(v_high / 2.55)}%")

        # Check and update warning labels
        self.check_range_warnings()

    def update_preview(self):
        """Update mask preview.

        Generates a grayscale mask preview showing which pixels will be
        detected with the current HSV ranges. Scales the preview to fit
        the preview label while maintaining aspect ratio.
        """
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

        # Get the actual image dimensions
        if self.viewer.image_hsv is not None:
            img_height, img_width = self.viewer.image_hsv.shape[:2]
        else:
            img_height, img_width = mask.shape

        # Calculate preview size maintaining aspect ratio
        # Set maximum bounds for the preview
        max_width = 300
        max_height = 200

        # Scale to fit within bounds while maintaining aspect ratio
        scale = min(max_width / img_width, max_height / img_height)
        preview_width = int(img_width * scale)
        preview_height = int(img_height * scale)

        # Resize for preview maintaining aspect ratio
        preview = cv2.resize(mask, (preview_width, preview_height))

        # Convert to QPixmap
        h, w = preview.shape
        qimg = QImage(preview.data, w, h, w, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimg)

        # Scale the pixmap to fit the label while preserving aspect ratio
        self.preview_label.setPixmap(pixmap.scaled(
            self.preview_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))

    def check_range_warnings(self):
        """Check and display warning labels based on range values.

        Shows warning labels when HSV ranges are too wide (e.g., saturation
        or value lower bounds below 25%), which may result in false positives.
        """
        # Check Saturation warning - if lower bound is in the bottom 25% (< 64 out of 255)
        s_center = self.hsv_ranges.get('s_center', 0)
        s_minus = self.hsv_ranges.get('s_minus', 0)
        s_low = max(0, s_center - s_minus)

        # Show warning if saturation lower bound is less than 25% (64/255)
        self.s_warning_label.setVisible(s_low < 64)

        # Check Value warning - if lower bound is in the bottom 25% (< 64 out of 255)
        v_center = self.hsv_ranges.get('v_center', 0)
        v_minus = self.hsv_ranges.get('v_minus', 0)
        v_low = max(0, v_center - v_minus)

        # Show warning if value lower bound is less than 25% (64/255)
        self.v_warning_label.setVisible(v_low < 64)

        # Check Hue warning - if range is wider than 60 degrees (30 in OpenCV's 0-179 scale)
        h_minus = self.hsv_ranges.get('h_minus', 0)
        h_plus = self.hsv_ranges.get('h_plus', 0)

        # Calculate total hue range width (it's simply the sum of both buffers)
        h_range = h_minus + h_plus

        # Show warning if hue range is more than 30 (60 degrees in 360 scale, 30 in 180 scale)
        self.h_warning_label.setVisible(h_range > 30)

    def show_help(self):
        """
        Show help dialog with instructions.

        Displays a comprehensive help dialog explaining how to use the
        HSV Color Range Assistant tool, including navigation, selection,
        and range adjustment instructions.
        """
        help_text = """
<h2>HSV Color Range Assistant - Help</h2>

<p>This tool helps you pick the HSV color range of a specific color in a photo.
Click on the BROWSE button to open an image.</p>

<h3>Navigation:</h3>
<p>• Use the mouse scroll wheel to zoom in/out of the image<br>
• Use the left mouse button to drag the image around and pan it</p>

<h3>Color Selection:</h3>
<p>• Hold the <b>CTRL/OPTION key</b> while left clicking on a color in the image that you want to select<br>
• All pixels in the image that share that HSV color value will be selected and highlighted in white</p>

<h3>Selection Radius:</h3>
        <p>You can adjust the Selection Radius of the mouse cursor to be larger or smaller.
        When you CTRL click it will select all colors within that radius of the mouse cursor.</p>

<h3>Corrections:</h3>
<p>If you make a mistake you can UNDO the last selection or you can press the RESET button to start over.</p>

<h3>Mask Preview:</h3>
        <p>On the right side the Mask Preview section will show you what pixels in the image were selected.
        If you see pixels outside of your target object that you are selecting that means you may need to
        adjust the Color Tolerance or be more careful with your selections.</p>
"""

        msg = QMessageBox(self)
        msg.setWindowTitle("HSV Color Range Assistant - Help")
        msg.setTextFormat(Qt.RichText)
        msg.setText(help_text)
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    def accept(self):
        """
        Accept and emit ranges.

        Overrides QDialog.accept() to emit the rangeAccepted signal with
        the current HSV ranges before closing the dialog.
        """
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
    sys.exit(app.exec())
