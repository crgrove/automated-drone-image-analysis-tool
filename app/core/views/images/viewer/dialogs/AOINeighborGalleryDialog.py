"""
AOINeighborGalleryDialog - Dialog for displaying AOI appearances in neighboring images.

Displays a gallery of thumbnails showing where an AOI appears across multiple
images in the flight path. Supports zoom, pan, and navigation to specific images.
"""

import numpy as np
import cv2
from pathlib import Path
from PySide6.QtCore import Qt, QSize, Signal, QRectF, QPointF, QTimer
from PySide6.QtGui import (
    QImage, QPixmap, QPainter, QColor, QPen, QFont, QBrush,
    QWheelEvent, QMouseEvent, QTransform
)
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QScrollArea, QWidget, QFrame, QGridLayout, QSizePolicy,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsTextItem,
    QGraphicsRectItem
)

from core.services.LoggerService import LoggerService
from helpers.TranslationMixin import TranslationMixin


class ThumbnailItem:
    """Represents a single thumbnail in the gallery."""

    def __init__(self, image_idx, image_name, thumbnail, pixel_x, pixel_y, is_current=False):
        self.image_idx = image_idx
        self.image_name = image_name
        self.thumbnail = thumbnail
        self.pixel_x = pixel_x
        self.pixel_y = pixel_y
        self.is_current = is_current


class NeighborGalleryView(QGraphicsView):
    """
    Custom graphics view for displaying AOI neighbor thumbnails.

    Supports zoom with mouse wheel and pan with right-click drag.
    """

    thumbnail_clicked = Signal(int)  # Emits image_idx when a thumbnail is clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LoggerService()

        # Create scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Enable antialiasing
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)

        # Configure view
        self.setDragMode(QGraphicsView.NoDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))

        # Zoom state
        self._zoom = 1.0
        self._min_zoom = 0.1
        self._max_zoom = 10.0

        # Pan state
        self._panning = False
        self._pan_start = QPointF()

        # Thumbnail items (for click detection)
        self._thumbnail_rects = []  # List of (QRectF, image_idx)

        # Selection tracking
        self._selected_index = -1  # Currently selected thumbnail
        self._border_items = []  # List of (image_idx, border_rect) for updating borders
        self._results = []  # Store results for reference

        # Style settings
        self.thumbnail_spacing = 20
        self.thumbnail_size = 200
        self.label_height = 25
        self.current_highlight_width = 4

    def load_thumbnails(self, results):
        """
        Load thumbnails from neighbor search results.

        Args:
            results (list): List of dicts with thumbnail info
        """
        self.scene.clear()
        self._thumbnail_rects = []
        self._border_items = []
        self._results = results or []
        self._selected_index = -1

        if not results:
            return

        # Calculate layout
        x = self.thumbnail_spacing
        y = self.thumbnail_spacing

        for result in results:
            try:
                # Convert numpy array to QPixmap
                thumbnail = result.get('thumbnail')
                if thumbnail is None:
                    continue

                # Resize to consistent size
                height, width = thumbnail.shape[:2]
                scale = self.thumbnail_size / max(width, height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                thumbnail_resized = cv2.resize(thumbnail, (new_width, new_height),
                                               interpolation=cv2.INTER_LANCZOS4)

                # Convert to QImage and QPixmap
                # Use bytes conversion to ensure data is fully copied and stable
                if len(thumbnail_resized.shape) == 2:
                    # Grayscale
                    thumbnail_contiguous = np.ascontiguousarray(thumbnail_resized, dtype=np.uint8)
                    image_data = thumbnail_contiguous.tobytes()
                    qimage = QImage(image_data, new_width, new_height,
                                    new_width, QImage.Format_Grayscale8).copy()
                else:
                    # RGB - ensure contiguous memory layout
                    thumbnail_rgb = cv2.cvtColor(thumbnail_resized, cv2.COLOR_RGB2BGR)
                    thumbnail_rgb = cv2.cvtColor(thumbnail_rgb, cv2.COLOR_BGR2RGB)
                    thumbnail_contiguous = np.ascontiguousarray(thumbnail_rgb, dtype=np.uint8)
                    image_data = thumbnail_contiguous.tobytes()
                    bytes_per_line = 3 * new_width
                    qimage = QImage(image_data, new_width, new_height,
                                    bytes_per_line, QImage.Format_RGB888).copy()

                # Create pixmap from the copied QImage
                pixmap = QPixmap.fromImage(qimage)

                # Skip if pixmap creation failed
                if pixmap.isNull():
                    self.logger.warning("Failed to create pixmap for thumbnail")
                    continue

                # Create pixmap item
                pixmap_item = QGraphicsPixmapItem(pixmap)
                pixmap_item.setPos(x + (self.thumbnail_size - new_width) / 2,
                                   y + (self.thumbnail_size - new_height) / 2)
                self.scene.addItem(pixmap_item)

                # Draw border/highlight
                is_current = result.get('is_current', False)
                border_color = QColor(0, 200, 0) if is_current else QColor(100, 100, 100)
                border_width = self.current_highlight_width if is_current else 2

                border_rect = QGraphicsRectItem(x - border_width/2, y - border_width/2,
                                                self.thumbnail_size + border_width,
                                                self.thumbnail_size + border_width)
                border_rect.setPen(QPen(border_color, border_width))
                border_rect.setBrush(QBrush(Qt.NoBrush))
                self.scene.addItem(border_rect)

                # Store border item for selection updates
                image_idx = result.get('image_idx', -1)
                self._border_items.append((image_idx, border_rect, is_current))

                # Store rect for click detection
                click_rect = QRectF(x, y, self.thumbnail_size, self.thumbnail_size)
                self._thumbnail_rects.append((click_rect, image_idx))

                # Add label
                image_name = result.get('image_name', 'Unknown')
                label_text = f"{image_name}"
                if is_current:
                    label_text += " (Current)"

                text_item = QGraphicsTextItem(label_text)
                text_item.setDefaultTextColor(QColor(255, 255, 255))
                font = QFont("Arial", 9)
                text_item.setFont(font)

                # Center the label
                text_width = text_item.boundingRect().width()
                text_x = x + (self.thumbnail_size - text_width) / 2
                text_item.setPos(text_x, y + self.thumbnail_size + 5)
                self.scene.addItem(text_item)

                # Move to next position
                x += self.thumbnail_size + self.thumbnail_spacing

            except Exception as e:
                self.logger.error(f"Error loading thumbnail: {e}")
                continue

        # Set scene rect
        total_width = x + self.thumbnail_spacing
        total_height = self.thumbnail_size + self.label_height + 2 * self.thumbnail_spacing
        self.scene.setSceneRect(0, 0, total_width, total_height)

        # Reset transform and set a reasonable initial scale
        # Don't fit all thumbnails - let user scroll horizontally
        self.resetTransform()
        self._zoom = 1.0

        # If content is wider than view, just show from the start
        # If content fits, center it
        view_width = self.viewport().width()
        if total_width <= view_width:
            # Content fits - center it
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        else:
            # Content is wider - show at 1:1 scale, scrollable
            self.centerOn(self.thumbnail_spacing + self.thumbnail_size / 2,
                          self.thumbnail_spacing + self.thumbnail_size / 2)

    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for zooming."""
        # Get zoom factor
        zoom_factor = 1.15
        if event.angleDelta().y() > 0:
            # Zoom in - no upper limit
            self._zoom *= zoom_factor
            self.scale(zoom_factor, zoom_factor)
        else:
            # Zoom out - keep minimum limit
            if self._zoom > self._min_zoom:
                self._zoom /= zoom_factor
                self.scale(1 / zoom_factor, 1 / zoom_factor)

        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for panning and clicking."""
        if event.button() == Qt.RightButton:
            # Start panning
            self._panning = True
            self._pan_start = event.position()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        elif event.button() == Qt.LeftButton:
            # Check if clicked on a thumbnail
            scene_pos = self.mapToScene(event.pos())
            for rect, image_idx in self._thumbnail_rects:
                if rect.contains(scene_pos):
                    self.select_thumbnail(image_idx)
                    self.thumbnail_clicked.emit(image_idx)
                    event.accept()
                    return
            super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release."""
        if event.button() == Qt.RightButton:
            self._panning = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for panning."""
        if self._panning:
            delta = event.position() - self._pan_start
            self._pan_start = event.position()

            # Scroll the view
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - int(delta.x())
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - int(delta.y())
            )
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def reset_view(self):
        """Reset zoom and fit all thumbnails in view."""
        self._zoom = 1.0
        self.resetTransform()
        if self.scene.sceneRect().width() > 0:
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def select_thumbnail(self, image_idx):
        """
        Update selection highlighting to the specified thumbnail.

        Args:
            image_idx (int): Index of the image to select
        """
        self._selected_index = image_idx

        for idx, border_rect, is_current in self._border_items:
            if idx == image_idx:
                # Selected thumbnail gets bright green border
                border_rect.setPen(QPen(QColor(0, 200, 0), self.current_highlight_width))
            elif is_current:
                # Original/current image gets dimmer green when not selected
                border_rect.setPen(QPen(QColor(0, 150, 0), 3))
            else:
                # Other thumbnails get gray border
                border_rect.setPen(QPen(QColor(100, 100, 100), 2))


class AOINeighborGalleryDialog(TranslationMixin, QDialog):
    """
    Dialog for displaying AOI appearances across neighboring images.

    Shows thumbnails of where the selected AOI appears in the flight path,
    allowing the user to quickly review the AOI across multiple images.
    """

    image_clicked = Signal(int)  # Emits image_idx when user clicks a thumbnail

    def __init__(self, parent=None, results=None):
        """
        Initialize the AOI Neighbor Gallery dialog.

        Args:
            parent: Parent widget (usually the Viewer)
            results (list): List of dicts with thumbnail info from neighbor search
        """
        super().__init__(parent)
        self.logger = LoggerService()
        self.results = results or []
        self._thumbnails_loaded = False

        # Setup dialog
        self.setWindowTitle(self.tr("AOI in Neighboring Images"))
        self.setModal(False)  # Non-modal so user can interact with main window

        # Set window flags
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # Create UI
        self._setup_ui()
        self._apply_translations()

        # Set initial size (thumbnails loaded in showEvent when viewport is ready)
        self.resize(900, 400)

    def showEvent(self, event):
        """Load thumbnails when dialog is shown (viewport is ready)."""
        super().showEvent(event)
        # Only load once, after dialog is visible and viewport has valid size
        if not self._thumbnails_loaded and self.results:
            self._thumbnails_loaded = True
            # Use a small delay to ensure viewport is fully initialized
            QTimer.singleShot(10, lambda: self.gallery_view.load_thumbnails(self.results))

    def _setup_ui(self):
        """Create the dialog UI components."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Info label
        info_text = (
            f"Found AOI in {len(self.results)} image(s). "
            "Use mouse wheel to zoom, right-click drag to pan. "
            "Click a thumbnail to navigate to that image."
        )
        self.info_label = QLabel(info_text)
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("QLabel { color: #aaa; padding: 5px; }")
        main_layout.addWidget(self.info_label)

        # Gallery view
        self.gallery_view = NeighborGalleryView(self)
        self.gallery_view.setMinimumHeight(250)
        self.gallery_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gallery_view.thumbnail_clicked.connect(self._on_thumbnail_clicked)
        main_layout.addWidget(self.gallery_view)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Reset View button
        reset_button = QPushButton(self.tr("Reset View"))
        reset_button.setMinimumHeight(35)
        reset_button.clicked.connect(self.gallery_view.reset_view)
        reset_button.setToolTip(self.tr("Reset zoom and fit all thumbnails in view"))
        button_layout.addWidget(reset_button)

        # Spacer
        button_layout.addStretch()

        # Close button
        close_button = QPushButton(self.tr("Close"))
        close_button.setMinimumHeight(35)
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def _on_thumbnail_clicked(self, image_idx):
        """
        Handle thumbnail click.

        Args:
            image_idx (int): Index of the clicked image
        """
        self.image_clicked.emit(image_idx)

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.key() == Qt.Key_Escape:
            self.close()
            event.accept()
        elif event.key() == Qt.Key_R:
            # Reset view
            self.gallery_view.reset_view()
            event.accept()
        else:
            super().keyPressEvent(event)
