"""
ColorPickerImageViewer - Standalone image viewer component with eyedropper tool.

This component allows users to:
- Load an image from file
- Select a pixel from the image using an eyedropper tool
- Get the selected color as RGB tuple

Can be used by multiple algorithms for color selection.
"""

import cv2
import numpy as np
import os
from PySide6.QtCore import Qt, QPointF, Signal, QPoint
from PySide6.QtGui import (
    QImage, QPixmap, QPainter, QPen, QBrush, QColor, QCursor, QMouseEvent, QWheelEvent, QTransform
)
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QFileDialog,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget, QSizePolicy,
    QMessageBox
)

try:
    import qimage2ndarray
except ImportError:
    qimage2ndarray = None


class _FitView(QGraphicsView):
    """
    QGraphicsView that auto-fits the current pixmap when the parent viewer
    is at no-zoom (zoom_factor == 1.0). This keeps the image fitted as the
    window is resized without interfering when the user has zoomed.
    """

    def __init__(self, owner):
        super().__init__()
        self._owner = owner

    def resizeEvent(self, event):
        super().resizeEvent(event)
        try:
            if self._owner and getattr(self._owner, 'pixmap_item', None) is not None:
                if getattr(self._owner, 'zoom_factor', 1.0) == 1.0:
                    self.fitInView(self._owner.pixmap_item, Qt.KeepAspectRatio)
        except Exception:
            # Best-effort fit; ignore resize-time errors
            pass


class ColorPickerImageViewer(QWidget):
    """
    Standalone image viewer with eyedropper tool for color selection.

    Signals:
        colorSelected(r, g, b): Emitted when a pixel is selected. RGB values are 0-255.
    """

    colorSelected = Signal(int, int, int)  # r, g, b

    def __init__(self, parent=None):
        """
        Initialize the ColorPickerImageViewer.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Image data
        self.image_array = None  # numpy array (BGR format from cv2)
        self.image_rgb = None    # numpy array (RGB format for display)
        self.pixmap_item = None  # QGraphicsPixmapItem

        # Eyedropper state
        self.eyedropper_active = False

        # Setup UI
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Button layout
        button_layout = QHBoxLayout()

        self.load_button = QPushButton("Load Image")
        # Avoid passing the clicked(bool) argument into load_image
        self.load_button.clicked.connect(lambda: self.load_image())
        button_layout.addWidget(self.load_button)

        self.eyedropper_button = QPushButton("Color Selector")
        self.eyedropper_button.setCheckable(True)
        self.eyedropper_button.clicked.connect(self.toggle_eyedropper)
        self.eyedropper_button.setEnabled(False)  # Disabled until image is loaded
        button_layout.addWidget(self.eyedropper_button)

        button_layout.addStretch()

        # Color info label (hidden until a color is selected)
        self.color_label = QLabel("")
        self.color_label.setVisible(False)
        self.color_label.setStyleSheet("padding: 5px; border: 1px solid #ccc;")
        button_layout.addWidget(self.color_label)

        layout.addLayout(button_layout)

        # Image viewer
        self.viewer = _FitView(self)
        self.scene = QGraphicsScene()
        self.viewer.setScene(self.scene)
        self.viewer.setRenderHint(QPainter.Antialiasing)
        self.viewer.setMouseTracking(True)
        # Enable panning by default (when eyedropper is not active)
        self.viewer.setDragMode(QGraphicsView.ScrollHandDrag)

        # Zoom state
        self.zoom_factor = 1.0
        self.min_zoom = 1.0  # Do not allow zooming out beyond no-zoom
        self.max_zoom = 10.0

        layout.addWidget(self.viewer)

        # Override mouse events for custom handling
        self.viewer.mousePressEvent = self._on_mouse_press
        self.viewer.mouseMoveEvent = self._on_mouse_move
        self.viewer.wheelEvent = self._on_wheel_event
        self.viewer.mouseDoubleClickEvent = self._on_double_click

        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.viewer.setMinimumSize(400, 300)

    def load_image(self, filepath=None):
        """
        Load an image from file.

        Args:
            filepath: Optional file path. If None, opens file dialog.

        Returns:
            bool: True if image loaded successfully, False otherwise.
        """
        # QPushButton.clicked emits a bool; treat booleans like "no filepath provided"
        if filepath is None or isinstance(filepath, bool):
            initial_dir = os.path.expanduser("~")
            filepath, _ = QFileDialog.getOpenFileName(
                self,
                "Select Image",
                initial_dir,
                "Image Files (*.png *.jpg *.jpeg *.bmp *.tif *.tiff);;All Files (*)"
            )

        if not filepath:
            return False

        try:
            # Load image using OpenCV
            img = cv2.imread(filepath)
            if img is None:
                QMessageBox.warning(self, "Error", f"Could not load image: {filepath}")
                return False

            # Store image arrays
            self.image_array = img  # BGR format
            self.image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # RGB for display

            # Convert to QPixmap
            # Make sure we have a contiguous array
            image_rgb_contiguous = np.ascontiguousarray(self.image_rgb)

            if qimage2ndarray:
                qimg = qimage2ndarray.array2qimage(image_rgb_contiguous)
            else:
                # Fallback: manual conversion
                height, width, channel = image_rgb_contiguous.shape
                bytes_per_line = 3 * width
                # Create a copy of the data to ensure it persists
                image_bytes = image_rgb_contiguous.tobytes()
                qimg = QImage(
                    image_bytes,
                    width,
                    height,
                    bytes_per_line,
                    QImage.Format_RGB888
                )

            pixmap = QPixmap.fromImage(qimg)

            # Update scene
            self.scene.clear()
            self.pixmap_item = self.scene.addPixmap(pixmap)
            self.scene.setSceneRect(pixmap.rect())

            # Fit image in view
            self.viewer.setTransform(QTransform())  # reset any previous zoom/pan
            self.viewer.fitInView(self.pixmap_item, Qt.KeepAspectRatio)

            # Reset zoom factor
            self.zoom_factor = 1.0

            # Force update
            self.viewer.update()
            self.viewer.viewport().update()

            # Enable eyedropper button
            self.eyedropper_button.setEnabled(True)
            # Hide selected color box until a color is picked
            self.color_label.setVisible(False)

            return True

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading image: {str(e)}")
            return False

    def toggle_eyedropper(self, checked):
        """
        Toggle eyedropper mode.

        Args:
            checked: Whether eyedropper should be active
        """
        self.eyedropper_active = checked

        # Enable/disable panning based on eyedropper state
        if checked:
            self.viewer.setDragMode(QGraphicsView.NoDrag)
        else:
            self.viewer.setDragMode(QGraphicsView.ScrollHandDrag)

        if checked:
            # Change cursor to eyedropper
            # Create a larger pixmap for better visibility
            pixmap = QPixmap(24, 24)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)

            # Draw eyedropper icon (simple representation)
            # Draw dropper body (vertical line)
            pen = QPen(QColor(0, 0, 0), 2)
            painter.setPen(pen)
            painter.drawLine(12, 2, 12, 14)

            # Draw dropper tip (angled lines)
            painter.drawLine(12, 14, 8, 18)
            painter.drawLine(12, 14, 16, 18)
            painter.drawLine(8, 18, 16, 18)

            # Draw tip circle
            painter.drawEllipse(10, 18, 4, 4)

            # Draw white outline for better visibility
            pen = QPen(QColor(255, 255, 255), 1)
            painter.setPen(pen)
            painter.drawLine(12, 2, 12, 14)
            painter.drawLine(12, 14, 8, 18)
            painter.drawLine(12, 14, 16, 18)
            painter.drawLine(8, 18, 16, 18)
            painter.drawEllipse(10, 18, 4, 4)

            painter.end()

            # Hotspot at the tip of the dropper (bottom center)
            cursor = QCursor(pixmap, 12, 20)
            self.viewer.setCursor(cursor)
            self.eyedropper_button.setText("Cancel")
        else:
            # Reset cursor
            self.viewer.setCursor(Qt.ArrowCursor)
            self.eyedropper_button.setText("Color Selector")

    def _on_mouse_press(self, event: QMouseEvent):
        """Handle mouse press events."""
        # Handle eyedropper selection
        if self.eyedropper_active and event.button() == Qt.LeftButton:
            if self.pixmap_item is None:
                event.accept()
                return

            # Get scene position
            scene_pos = self.viewer.mapToScene(event.pos())

            # Get pixel coordinates in image
            # Map scene position to pixmap item's local coordinates
            item_pos = self.pixmap_item.mapFromScene(scene_pos)
            pixmap_rect = self.pixmap_item.boundingRect()

            # Check if click is within image bounds (in item coordinates)
            if not pixmap_rect.contains(item_pos):
                event.accept()
                return

            # Get actual pixmap size
            pixmap = self.pixmap_item.pixmap()
            if pixmap is None:
                event.accept()
                return
            pixmap_width = pixmap.width()
            pixmap_height = pixmap.height()

            # Normalize to pixmap coordinates (0 to pixmap width/height)
            # Then scale to image array dimensions
            if pixmap_rect.width() <= 0 or pixmap_rect.height() <= 0 or self.image_rgb is None:
                event.accept()
                return

            x = int((item_pos.x() / pixmap_rect.width()) * pixmap_width)
            y = int((item_pos.y() / pixmap_rect.height()) * pixmap_height)

            # Clamp to pixmap bounds first
            x = max(0, min(x, pixmap_width - 1))
            y = max(0, min(y, pixmap_height - 1))

            # Scale to image array dimensions if different
            img_height, img_width = self.image_rgb.shape[:2]
            if pixmap_width != img_width or pixmap_height != img_height:
                x = int((x / pixmap_width) * img_width)
                y = int((y / pixmap_height) * img_height)
            x = max(0, min(x, img_width - 1))
            y = max(0, min(y, img_height - 1))

            # Get pixel color (RGB format)
            pixel = self.image_rgb[y, x]
            r, g, b = int(pixel[0]), int(pixel[1]), int(pixel[2])

            # Compute HSV for display (OpenCV: H[0-179], S/V[0-255])
            rgb_px = np.uint8([[[r, g, b]]])
            hsv_px = cv2.cvtColor(rgb_px, cv2.COLOR_RGB2HSV)[0][0]
            # Cast to float before arithmetic to avoid uint8 overflow
            h_deg = int(round(float(hsv_px[0]) * 2.0))
            s_pct = int(round(float(hsv_px[1]) * (100.0 / 255.0)))
            v_pct = int(round(float(hsv_px[2]) * (100.0 / 255.0)))

            # Update color label (make visible upon first selection)
            color_hex = f"#{r:02x}{g:02x}{b:02x}"
            self.color_label.setVisible(True)
            self.color_label.setText(f"RGB: ({r}, {g}, {b}) {color_hex} | HSV: ({h_deg}°, {s_pct}%, {v_pct}%)")
            self.color_label.setStyleSheet(
                f"padding: 5px; background-color: rgb({r}, {g}, {b}); "
                f"border: 1px solid #ccc; color: {'white' if (r + g + b) < 384 else 'black'};"
            )

            # Emit signal
            self.colorSelected.emit(r, g, b)

            # Deactivate eyedropper after selection
            self.eyedropper_button.setChecked(False)
            self.toggle_eyedropper(False)

            event.accept()
            return

        # Handle right-click to reset zoom
        if event.button() == Qt.RightButton and not self.eyedropper_active:
            if self.pixmap_item is not None:
                self.viewer.setTransform(QTransform())
                self.viewer.fitInView(self.pixmap_item, Qt.KeepAspectRatio)
                self.zoom_factor = 1.0
                event.accept()
                return

        # Call original handler for other interactions (including panning)
        QGraphicsView.mousePressEvent(self.viewer, event)

    def _on_mouse_move(self, event: QMouseEvent):
        """Handle mouse move events to show color preview."""
        if self.eyedropper_active and self.pixmap_item is not None:
            # Get scene position
            scene_pos = self.viewer.mapToScene(event.pos())

            # Map scene position to pixmap item's local coordinates
            item_pos = self.pixmap_item.mapFromScene(scene_pos)
            pixmap_rect = self.pixmap_item.boundingRect()

            # Check if mouse is within image bounds (in item coordinates)
            if pixmap_rect.contains(item_pos):
                # Do not show hover preview until a color has been selected
                if not self.color_label.isVisible():
                    QGraphicsView.mouseMoveEvent(self.viewer, event)
                    return

                # Get actual pixmap size
                pixmap = self.pixmap_item.pixmap()
                if pixmap is None:
                    QGraphicsView.mouseMoveEvent(self.viewer, event)
                    return
                pixmap_width = pixmap.width()
                pixmap_height = pixmap.height()

                # Normalize to pixmap coordinates, then scale to image array dimensions
                if pixmap_rect.width() > 0 and pixmap_rect.height() > 0 and self.image_rgb is not None:
                    x = int((item_pos.x() / pixmap_rect.width()) * pixmap_width)
                    y = int((item_pos.y() / pixmap_rect.height()) * pixmap_height)

                    # Clamp to pixmap bounds first
                    x = max(0, min(x, pixmap_width - 1))
                    y = max(0, min(y, pixmap_height - 1))

                    # Scale to image array dimensions if different
                    img_height, img_width = self.image_rgb.shape[:2]
                    if pixmap_width != img_width or pixmap_height != img_height:
                        x = int((x / pixmap_width) * img_width)
                        y = int((y / pixmap_height) * img_height)
                        x = max(0, min(x, img_width - 1))
                        y = max(0, min(y, img_height - 1))

                    # Get pixel color
                    pixel = self.image_rgb[y, x]
                    r, g, b = int(pixel[0]), int(pixel[1]), int(pixel[2])

                    # Update color label with preview (include HSV)
                    rgb_px = np.uint8([[[r, g, b]]])
                    hsv_px = cv2.cvtColor(rgb_px, cv2.COLOR_RGB2HSV)[0][0]
                    # Cast to float before arithmetic to avoid uint8 overflow
                    h_deg = int(round(float(hsv_px[0]) * 2.0))
                    s_pct = int(round(float(hsv_px[1]) * (100.0 / 255.0)))
                    v_pct = int(round(float(hsv_px[2]) * (100.0 / 255.0)))
                    color_hex = f"#{r:02x}{g:02x}{b:02x}"
                    self.color_label.setText(f"RGB: ({r}, {g}, {b}) {color_hex} | HSV: {h_deg}°, {s_pct}%, {v_pct}% (hover)")
                    self.color_label.setStyleSheet(
                        f"padding: 5px; background-color: rgb({r}, {g}, {b}); "
                        f"border: 1px solid #ccc; color: {'white' if (r + g + b) < 384 else 'black'};"
                    )

        # Call original handler
        QGraphicsView.mouseMoveEvent(self.viewer, event)

    def _on_wheel_event(self, event: QWheelEvent):
        """Handle mouse wheel events for zooming."""
        if self.eyedropper_active:
            # Don't zoom when eyedropper is active
            event.ignore()
            return

        if self.pixmap_item is None:
            event.ignore()
            return

        # Get zoom factor from wheel delta
        delta = event.angleDelta().y()
        zoom_delta = 1.15 if delta > 0 else 1 / 1.15

        # Calculate new zoom
        new_zoom = self.zoom_factor * zoom_delta
        new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))

        if new_zoom != self.zoom_factor:
            # Get scene position under mouse
            scene_pos = self.viewer.mapToScene(event.pos())

            # Apply zoom
            self._zoom_at_point(scene_pos, new_zoom / self.zoom_factor)
            self.zoom_factor = new_zoom

        event.accept()

    def _zoom_at_point(self, scene_pos: QPointF, factor: float):
        """Zoom at a specific point in the scene."""
        # Get current transform
        transform = self.viewer.transform()

        # Scale around the point
        transform.translate(scene_pos.x(), scene_pos.y())
        transform.scale(factor, factor)
        transform.translate(-scene_pos.x(), -scene_pos.y())

        # Apply transform
        self.viewer.setTransform(transform)

    def _on_double_click(self, event: QMouseEvent):
        """Handle double-click events."""
        if event.button() == Qt.LeftButton and not self.eyedropper_active:
            if self.pixmap_item is not None:
                # Zoom in at mouse position
                scene_pos = self.viewer.mapToScene(event.pos())
                self._zoom_at_point(scene_pos, 1.5)
                self.zoom_factor *= 1.5
                self.zoom_factor = min(self.zoom_factor, self.max_zoom)
                event.accept()
                return

        QGraphicsView.mouseDoubleClickEvent(self.viewer, event)

    def get_current_color(self):
        """
        Get the currently selected color.

        Returns:
            tuple: (r, g, b) tuple or None if no color selected
        """
        text = self.color_label.text()
        if "RGB:" in text and "No color selected" not in text:
            # Extract RGB values from label text
            import re
            match = re.search(r'RGB:\s*\((\d+),\s*(\d+),\s*(\d+)\)', text)
            if match:
                return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
        return None

    def set_image_from_array(self, image_array):
        """
        Set image from numpy array.

        Args:
            image_array: numpy array in BGR format (as from cv2.imread)
        """
        if image_array is None:
            return False

        try:
            self.image_array = image_array
            self.image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)

            # Convert to QPixmap
            # Make sure we have a contiguous array
            image_rgb_contiguous = np.ascontiguousarray(self.image_rgb)

            if qimage2ndarray:
                qimg = qimage2ndarray.array2qimage(image_rgb_contiguous)
            else:
                height, width, channel = image_rgb_contiguous.shape
                bytes_per_line = 3 * width
                # Create a copy of the data to ensure it persists
                image_bytes = image_rgb_contiguous.tobytes()
                qimg = QImage(
                    image_bytes,
                    width,
                    height,
                    bytes_per_line,
                    QImage.Format_RGB888
                )

            pixmap = QPixmap.fromImage(qimg)

            # Update scene
            self.scene.clear()
            self.pixmap_item = self.scene.addPixmap(pixmap)
            self.scene.setSceneRect(pixmap.rect())

            # Fit image in view
            self.viewer.setTransform(QTransform())  # reset any previous zoom/pan
            self.viewer.fitInView(self.pixmap_item, Qt.KeepAspectRatio)

            # Reset zoom factor
            self.zoom_factor = 1.0

            # Force update
            self.viewer.update()
            self.viewer.viewport().update()

            # Enable eyedropper button
            self.eyedropper_button.setEnabled(True)
            # Hide selected color box until a color is picked
            self.color_label.setVisible(False)

            return True

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error setting image: {str(e)}")
            return False
