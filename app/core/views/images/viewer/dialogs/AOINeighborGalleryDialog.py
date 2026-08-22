"""
AOINeighborGalleryDialog - Dialog for displaying AOI appearances in neighboring images.

Displays a gallery of thumbnails showing where an AOI appears across multiple
images in the flight path. Supports zoom, pan, and navigation to specific images.
"""

import numpy as np
import cv2
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import (
    QImage, QPixmap, QPainter, QColor, QPen, QFont, QBrush,
    QWheelEvent, QMouseEvent
)
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsTextItem,
    QGraphicsRectItem
)

from core.services.LoggerService import LoggerService
from helpers.TranslationMixin import TranslationMixin


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
        self._current_rect = None  # Cell of the originating capture, if shown

        # Style settings
        self.thumbnail_spacing = 20
        self.thumbnail_size = 200
        self.label_height = 25
        self.current_highlight_width = 4

    def load_thumbnails(self, results):
        """
        Load thumbnails from neighbor search results.

        Laid out as a single horizontal strip, scrolled sideways. This is the
        established shape of this gallery and reviewers navigate it by
        position along the flight; a wrapping grid was tried and reverted.

        Args:
            results (list): List of dicts with thumbnail info
        """
        self.scene.clear()
        self._thumbnail_rects = []
        self._border_items = []
        self._results = results or []
        self._selected_index = -1
        self._current_rect = None

        if not results:
            return

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

                border_rect = QGraphicsRectItem(x - border_width / 2, y - border_width / 2,
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
                if is_current:
                    self._current_rect = click_rect

                # Add label
                image_name = result.get('image_name', self.tr("Unknown"))
                label_text = f"{image_name}"
                if is_current:
                    label_text += self.tr(" (Current)")

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
                # Advance regardless: leaving x put stacked the next thumbnail
                # on top of this one and mis-routed its clicks.
                self.logger.error(f"Error loading thumbnail: {e}")
                x += self.thumbnail_size + self.thumbnail_spacing
                continue

        total_width = x + self.thumbnail_spacing
        total_height = self.thumbnail_size + self.label_height + 2 * self.thumbnail_spacing
        self.scene.setSceneRect(0, 0, total_width, total_height)

        self.reset_view()

    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for zooming.

        Both bounds are enforced against the transform actually applied, so
        _zoom cannot drift from the view's real scale. It used to: zoom-in was
        unbounded while _zoom kept counting, so a user who scrolled in and back
        out ended up far below the nominal floor with the view no longer
        matching the number.
        """
        zoom_factor = 1.15
        if event.angleDelta().y() > 0:
            target = min(self._max_zoom, self._zoom * zoom_factor)
        else:
            target = max(self._min_zoom, self._zoom / zoom_factor)

        if target != self._zoom:
            self.scale(target / self._zoom, target / self._zoom)
            self._zoom = target

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
        """Return to 1:1 and bring the originating image into view.

        Deliberately NOT fitInView on the whole scene: with a capped 50
        results that scales every thumbnail to roughly 16 px, which is not a
        view of anything. 1:1 keeps them legible and the strip scrolls.

        The originating capture is the one the reviewer is oriented by, so it
        is what the view lands on -- previously it could be anywhere in the
        strip with nothing to lead the eye to it.
        """
        self._zoom = 1.0
        self.resetTransform()
        if self.scene.sceneRect().width() <= 0:
            return
        if self._current_rect is not None:
            self.centerOn(self._current_rect.center())
        else:
            self.centerOn(self.thumbnail_spacing + self.thumbnail_size / 2,
                          self.thumbnail_spacing + self.thumbnail_size / 2)

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

    def __init__(self, parent=None, results=None, truncated=False):
        """
        Initialize the AOI Neighbor Gallery dialog.

        Args:
            parent: Parent widget (usually the Viewer)
            results (list): List of dicts with thumbnail info from neighbor search
            truncated (bool): The search stopped at its result cap with
                candidates unchecked, so the count is a floor, not the answer.
        """
        super().__init__(parent)
        self.logger = LoggerService()
        self.results = results or []
        self.truncated = truncated
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
        """Load thumbnails when the dialog is shown.

        Loads directly rather than after a settle timer (CLAUDE.md 2.9). The
        strip's geometry does not depend on the viewport width -- it is one
        row, scrolled sideways -- so there is nothing to wait for; the timer
        only ever created a window in which a closed dialog still received the
        callback and cleared an already-deleted scene.
        """
        super().showEvent(event)
        if not self._thumbnails_loaded and self.results:
            self._thumbnails_loaded = True
            self.gallery_view.load_thumbnails(self.results)

    def _info_text(self):
        """The header line, translated and honest about a capped search.

        Built through tr().format() rather than an f-string: an interpolated
        string can never match a catalogue entry, so the old version was
        untranslatable in every language. The truncated wording matters as
        much -- presenting the cap ("Found AOI in 50 image(s)") as the answer
        told a searcher the AOI appears in 50 captures when the real number
        was unknown and larger.
        """
        if self.truncated:
            return self.tr(
                "Showing the {count} nearest images containing this AOI; there are more. "
                "Use mouse wheel to zoom, right-click drag to pan. "
                "Click a thumbnail to navigate to that image."
            ).format(count=len(self.results))
        return self.tr(
            "Found AOI in {count} image(s). "
            "Use mouse wheel to zoom, right-click drag to pan. "
            "Click a thumbnail to navigate to that image."
        ).format(count=len(self.results))

    def _setup_ui(self):
        """Create the dialog UI components."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Info label
        self.info_label = QLabel(self._info_text())
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("QLabel { color: palette(placeholder-text); padding: 5px; }")
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

    def _apply_translations(self):
        """Re-translate, including the interpolated header the mixin cannot.

        The base implementation round-trips each QLabel's *current* text
        through tr(), which for an already-interpolated string is a no-op, so
        the header has to be rebuilt from its source form.
        """
        super()._apply_translations()
        if getattr(self, 'info_label', None) is not None:
            self.info_label.setText(self._info_text())

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
