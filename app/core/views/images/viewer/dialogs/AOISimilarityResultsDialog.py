"""
AOISimilarityResultsDialog - Dialog for displaying AOIs ranked by visual similarity.

Displays a horizontal gallery of AOI thumbnails ranked by similarity to a reference
AOI. Row 0 is the reference itself; every other tile shows its similarity score.
Adapted from AOINeighborGalleryDialog, but keyed by result row rather than image
index because multiple AOIs from the same image can appear in the results.
"""

import numpy as np
import cv2
from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QTimer
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


class SimilarityGalleryView(TranslationMixin, QGraphicsView):
    """
    Graphics view for displaying similarity-ranked AOI thumbnails.

    Supports zoom with mouse wheel and pan with right-click drag.
    """

    thumbnail_clicked = Signal(int)  # Emits the result row when a thumbnail is clicked
    selection_changed = Signal(int)  # Emits the number of checked rows

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

        # Pan state
        self._panning = False
        self._pan_start = QPointF()

        # Thumbnail items (for click detection)
        self._thumbnail_rects = []  # List of (QRectF, row)

        # Selection tracking
        self._selected_row = -1
        self._border_items = []  # List of (row, border_rect, is_reference)
        self._results = []

        # Checkbox state (bulk actions)
        self._checked_rows = set()
        self._checkbox_rects = []  # List of (QRectF, row) for hit-testing
        self._checkbox_items = {}  # row -> (box_item, tick_item)

        # Status badges (flag / comment), refreshed after bulk actions
        self._badge_items = {}  # row -> (flag_item, comment_item)

        # Style settings
        self.thumbnail_spacing = 20
        self.thumbnail_size = 200
        self.label_height = 60  # Three caption lines per tile
        self.reference_highlight_width = 4
        self.checkbox_size = 22

    def load_thumbnails(self, results):
        """
        Load thumbnails from similarity search results.

        Args:
            results (list): Result dicts; row 0 is expected to be the reference entry.
        """
        self.scene.clear()
        self._thumbnail_rects = []
        self._border_items = []
        self._results = results or []
        self._selected_row = -1
        self._checked_rows = set()
        self._checkbox_rects = []
        self._checkbox_items = {}
        self._badge_items = {}
        self.selection_changed.emit(0)

        if not results:
            return

        x = self.thumbnail_spacing
        y = self.thumbnail_spacing

        for row, result in enumerate(results):
            try:
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

                # Convert to QImage and QPixmap (copy so the buffer stays valid)
                if len(thumbnail_resized.shape) == 2:
                    thumbnail_contiguous = np.ascontiguousarray(thumbnail_resized, dtype=np.uint8)
                    qimage = QImage(thumbnail_contiguous.tobytes(), new_width, new_height,
                                    new_width, QImage.Format_Grayscale8).copy()
                else:
                    thumbnail_contiguous = np.ascontiguousarray(thumbnail_resized, dtype=np.uint8)
                    qimage = QImage(thumbnail_contiguous.tobytes(), new_width, new_height,
                                    3 * new_width, QImage.Format_RGB888).copy()

                pixmap = QPixmap.fromImage(qimage)
                if pixmap.isNull():
                    self.logger.warning("Failed to create pixmap for similarity thumbnail")
                    continue

                pixmap_item = QGraphicsPixmapItem(pixmap)
                pixmap_item.setPos(x + (self.thumbnail_size - new_width) / 2,
                                   y + (self.thumbnail_size - new_height) / 2)
                self.scene.addItem(pixmap_item)

                # Border: reference tile is highlighted green
                is_reference = result.get('is_reference', False)
                border_color = QColor(0, 200, 0) if is_reference else QColor(100, 100, 100)
                border_width = self.reference_highlight_width if is_reference else 2

                border_rect = QGraphicsRectItem(x - border_width / 2, y - border_width / 2,
                                                self.thumbnail_size + border_width,
                                                self.thumbnail_size + border_width)
                border_rect.setPen(QPen(border_color, border_width))
                border_rect.setBrush(QBrush(Qt.NoBrush))
                self.scene.addItem(border_rect)
                self._border_items.append((row, border_rect, is_reference))

                # Store rect for click detection
                click_rect = QRectF(x, y, self.thumbnail_size, self.thumbnail_size)
                self._thumbnail_rects.append((click_rect, row))

                # Checkbox (top-left) for bulk actions — only rows backed by a real AOI
                if result.get('aoi_idx') is not None:
                    self._add_checkbox(row, x, y)

                # Status badges (top-right): flag and comment indicators
                self._add_status_badges(row, result, x, y)

                # Caption line 1: similarity badge (or "Reference")
                if is_reference:
                    badge_text = self.tr("Reference")
                    badge_color = QColor(0, 200, 0)
                else:
                    similarity = result.get('similarity', 0)
                    badge_text = f"{similarity}%"
                    badge_color = self._similarity_color(similarity)
                self._add_caption(badge_text, badge_color, x, y + self.thumbnail_size + 5, bold=True)

                # Caption line 2: image name
                image_name = result.get('image_name') or self.tr("Unknown")
                self._add_caption(image_name, QColor(255, 255, 255),
                                  x, y + self.thumbnail_size + 22)

                # Caption line 3: AOI number (fallback to 1-based index within its image;
                # external query images have no AOI, so their line is left blank)
                aoi_number = result.get('aoi_number')
                aoi_idx = result.get('aoi_idx')
                if aoi_number is not None:
                    aoi_text = self.tr("AOI #{number}").format(number=aoi_number)
                elif aoi_idx is not None:
                    aoi_text = self.tr("AOI {index}").format(index=aoi_idx + 1)
                else:
                    aoi_text = ""
                if aoi_text:
                    self._add_caption(aoi_text, QColor(170, 170, 170),
                                      x, y + self.thumbnail_size + 39)

                x += self.thumbnail_size + self.thumbnail_spacing

            except Exception as e:
                self.logger.error(f"Error loading similarity thumbnail (row {row}): {e}")
                continue

        # Set scene rect
        total_width = x + self.thumbnail_spacing
        total_height = self.thumbnail_size + self.label_height + 2 * self.thumbnail_spacing
        self.scene.setSceneRect(0, 0, total_width, total_height)

        # Reset transform; show from the start if content is wider than the view
        self.resetTransform()
        self._zoom = 1.0
        view_width = self.viewport().width()
        if total_width <= view_width:
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        else:
            self.centerOn(self.thumbnail_spacing + self.thumbnail_size / 2,
                          self.thumbnail_spacing + self.thumbnail_size / 2)

    def _add_caption(self, text, color, tile_x, text_y, bold=False):
        """Add a centered caption line under a tile."""
        text_item = QGraphicsTextItem(text)
        text_item.setDefaultTextColor(color)
        font = QFont("Arial", 9)
        font.setBold(bold)
        text_item.setFont(font)
        text_width = text_item.boundingRect().width()
        text_item.setPos(tile_x + (self.thumbnail_size - text_width) / 2, text_y)
        self.scene.addItem(text_item)

    def _add_checkbox(self, row, tile_x, tile_y):
        """Add a selection checkbox at the tile's top-left corner."""
        size = self.checkbox_size
        box_rect = QRectF(tile_x + 6, tile_y + 6, size, size)

        box_item = QGraphicsRectItem(box_rect)
        box_item.setPen(QPen(QColor(255, 255, 255), 2))
        box_item.setBrush(QBrush(QColor(0, 0, 0, 140)))
        self.scene.addItem(box_item)

        tick_item = QGraphicsTextItem("✓")
        tick_item.setDefaultTextColor(QColor(0, 230, 0))
        tick_font = QFont("Arial", 12)
        tick_font.setBold(True)
        tick_item.setFont(tick_font)
        tick_bounds = tick_item.boundingRect()
        tick_item.setPos(box_rect.x() + (size - tick_bounds.width()) / 2,
                         box_rect.y() + (size - tick_bounds.height()) / 2)
        tick_item.setVisible(False)
        self.scene.addItem(tick_item)

        self._checkbox_rects.append((box_rect, row))
        self._checkbox_items[row] = (box_item, tick_item)

    def _add_status_badges(self, row, result, tile_x, tile_y):
        """Add flag/comment indicator badges at the tile's top-right corner."""
        aoi_data = result.get('aoi_data') or {}

        flag_item = QGraphicsTextItem("⚑")
        flag_item.setDefaultTextColor(QColor(255, 82, 82))
        flag_font = QFont("Arial", 13)
        flag_font.setBold(True)
        flag_item.setFont(flag_font)
        flag_item.setPos(tile_x + self.thumbnail_size - 28, tile_y + 2)
        flag_item.setVisible(bool(aoi_data.get('flagged')))
        self.scene.addItem(flag_item)

        comment_item = QGraphicsTextItem("\U0001F5E8")
        comment_item.setDefaultTextColor(QColor(255, 214, 0))
        comment_item.setFont(QFont("Arial", 11))
        comment_item.setPos(tile_x + self.thumbnail_size - 28, tile_y + 24)
        comment_item.setVisible(bool(aoi_data.get('user_comment')))
        self.scene.addItem(comment_item)

        self._badge_items[row] = (flag_item, comment_item)

    def refresh_status_badges(self, results=None):
        """Update flag/comment badges from the (live) result AOI dicts."""
        results = results if results is not None else self._results
        for row, (flag_item, comment_item) in self._badge_items.items():
            if row < len(results):
                aoi_data = results[row].get('aoi_data') or {}
                flag_item.setVisible(bool(aoi_data.get('flagged')))
                comment_item.setVisible(bool(aoi_data.get('user_comment')))

    def toggle_row_checked(self, row):
        """Toggle the checkbox state of a row."""
        self.set_row_checked(row, row not in self._checked_rows)

    def set_row_checked(self, row, checked):
        """Set the checkbox state of a row (no-op for rows without a checkbox)."""
        if row not in self._checkbox_items:
            return
        if checked:
            self._checked_rows.add(row)
        else:
            self._checked_rows.discard(row)

        box_item, tick_item = self._checkbox_items[row]
        tick_item.setVisible(checked)
        box_item.setPen(QPen(QColor(0, 230, 0) if checked else QColor(255, 255, 255), 2))
        self.selection_changed.emit(len(self._checked_rows))

    def set_all_checked(self, checked):
        """Check or uncheck every checkable row."""
        for row in self._checkbox_items:
            if checked:
                self._checked_rows.add(row)
            else:
                self._checked_rows.discard(row)
            box_item, tick_item = self._checkbox_items[row]
            tick_item.setVisible(checked)
            box_item.setPen(QPen(QColor(0, 230, 0) if checked else QColor(255, 255, 255), 2))
        self.selection_changed.emit(len(self._checked_rows))

    def get_checked_rows(self):
        """Return the checked rows in ascending order."""
        return sorted(self._checked_rows)

    @staticmethod
    def _similarity_color(similarity):
        """Color-code a similarity score (matches AOI confidence color conventions)."""
        if similarity >= 75:
            return QColor(76, 175, 80)    # Green (#4CAF50)
        if similarity >= 50:
            return QColor(255, 215, 0)    # Gold (#FFD700)
        return QColor(170, 170, 170)      # Gray

    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for zooming."""
        zoom_factor = 1.15
        if event.angleDelta().y() > 0:
            self._zoom *= zoom_factor
            self.scale(zoom_factor, zoom_factor)
        else:
            if self._zoom > self._min_zoom:
                self._zoom /= zoom_factor
                self.scale(1 / zoom_factor, 1 / zoom_factor)
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for panning and clicking."""
        if event.button() == Qt.RightButton:
            self._panning = True
            self._pan_start = event.position()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        elif event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            # Checkboxes take priority over tile navigation
            for rect, row in self._checkbox_rects:
                if rect.contains(scene_pos):
                    self.toggle_row_checked(row)
                    event.accept()
                    return
            for rect, row in self._thumbnail_rects:
                if rect.contains(scene_pos):
                    self.select_thumbnail(row)
                    self.thumbnail_clicked.emit(row)
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

    def select_thumbnail(self, row):
        """
        Update selection highlighting to the specified result row.

        Args:
            row (int): Result row to select.
        """
        self._selected_row = row

        for item_row, border_rect, is_reference in self._border_items:
            if item_row == row:
                border_rect.setPen(QPen(QColor(0, 200, 0), self.reference_highlight_width))
            elif is_reference:
                border_rect.setPen(QPen(QColor(0, 150, 0), 3))
            else:
                border_rect.setPen(QPen(QColor(100, 100, 100), 2))


class AOISimilarityResultsDialog(TranslationMixin, QDialog):
    """
    Dialog for displaying AOIs ranked by visual similarity to a reference AOI.

    Shows the reference AOI followed by the top matches; clicking a thumbnail
    emits result_clicked with its row so the controller can navigate to it.
    """

    result_clicked = Signal(int)          # Emits the result row when the user clicks a thumbnail
    bulk_flag_requested = Signal(list, bool)  # (checked rows, desired flag state)
    bulk_comment_requested = Signal(list)     # (checked rows)

    def __init__(self, parent=None, results=None, total_candidates=0):
        """
        Initialize the similarity results dialog.

        Args:
            parent: Parent widget (usually the Viewer)
            results (list): Result dicts; row 0 is the reference entry.
            total_candidates (int): Total number of AOIs that were ranked.
        """
        super().__init__(parent)
        self.logger = LoggerService()
        self.results = results or []
        self.total_candidates = total_candidates
        self._thumbnails_loaded = False

        self.setWindowTitle(self.tr("Similar AOIs"))
        self.setModal(False)  # Non-modal so user can interact with main window
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self._setup_ui()
        self._apply_translations()

        # Set initial size (thumbnails loaded in showEvent when viewport is ready)
        self.resize(900, 430)

    def showEvent(self, event):
        """Load thumbnails when dialog is shown (viewport is ready)."""
        super().showEvent(event)
        if not self._thumbnails_loaded and self.results:
            self._thumbnails_loaded = True
            # Small delay to ensure the viewport is fully initialized
            QTimer.singleShot(10, lambda: self.gallery_view.load_thumbnails(self.results))

    def _setup_ui(self):
        """Create the dialog UI components."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Info label
        shown = max(0, len(self.results) - 1)  # Exclude the reference tile
        reference_label = self._reference_label()
        info_text = self.tr(
            "Top {shown} of {total} AOIs ranked by similarity to {reference}. "
            "Use mouse wheel to zoom, right-click drag to pan. "
            "Click a thumbnail to jump to that AOI."
        ).format(shown=shown, total=self.total_candidates, reference=reference_label)
        self.info_label = QLabel(info_text)
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("QLabel { color: palette(placeholder-text); padding: 5px; }")
        main_layout.addWidget(self.info_label)

        # Gallery view
        self.gallery_view = SimilarityGalleryView(self)
        self.gallery_view.setMinimumHeight(280)
        self.gallery_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gallery_view.thumbnail_clicked.connect(self._on_thumbnail_clicked)
        self.gallery_view.selection_changed.connect(self._on_selection_changed)
        main_layout.addWidget(self.gallery_view)

        # Selection / bulk-action bar
        selection_layout = QHBoxLayout()
        selection_layout.setSpacing(10)

        self.select_all_button = QPushButton(self.tr("Select All"))
        self.select_all_button.clicked.connect(lambda: self.gallery_view.set_all_checked(True))
        selection_layout.addWidget(self.select_all_button)

        self.select_none_button = QPushButton(self.tr("Clear Selection"))
        self.select_none_button.clicked.connect(lambda: self.gallery_view.set_all_checked(False))
        selection_layout.addWidget(self.select_none_button)

        self.selection_label = QLabel(self.tr("{count} selected").format(count=0))
        self.selection_label.setStyleSheet("QLabel { color: palette(placeholder-text); padding: 0 8px; }")
        selection_layout.addWidget(self.selection_label)

        selection_layout.addStretch()

        self.flag_button = QPushButton(self.tr("Flag"))
        self.flag_button.setToolTip(self.tr("Flag all checked AOIs"))
        self.flag_button.setEnabled(False)
        self.flag_button.clicked.connect(lambda: self._emit_bulk_flag(True))
        selection_layout.addWidget(self.flag_button)

        self.unflag_button = QPushButton(self.tr("Unflag"))
        self.unflag_button.setToolTip(self.tr("Remove the flag from all checked AOIs"))
        self.unflag_button.setEnabled(False)
        self.unflag_button.clicked.connect(lambda: self._emit_bulk_flag(False))
        selection_layout.addWidget(self.unflag_button)

        self.comment_button = QPushButton(self.tr("Comment..."))
        self.comment_button.setToolTip(self.tr("Add or edit the comment on all checked AOIs"))
        self.comment_button.setEnabled(False)
        self.comment_button.clicked.connect(self._emit_bulk_comment)
        selection_layout.addWidget(self.comment_button)

        main_layout.addLayout(selection_layout)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        reset_button = QPushButton(self.tr("Reset View"))
        reset_button.setMinimumHeight(35)
        reset_button.clicked.connect(self.gallery_view.reset_view)
        reset_button.setToolTip(self.tr("Reset zoom and fit all thumbnails in view"))
        button_layout.addWidget(reset_button)

        button_layout.addStretch()

        close_button = QPushButton(self.tr("Close"))
        close_button.setMinimumHeight(35)
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def _on_selection_changed(self, count):
        """Update the selection label and bulk-action button states."""
        self.selection_label.setText(self.tr("{count} selected").format(count=count))
        has_selection = count > 0
        self.flag_button.setEnabled(has_selection)
        self.unflag_button.setEnabled(has_selection)
        self.comment_button.setEnabled(has_selection)

    def _emit_bulk_flag(self, flagged):
        rows = self.gallery_view.get_checked_rows()
        if rows:
            self.bulk_flag_requested.emit(rows, flagged)

    def _emit_bulk_comment(self):
        rows = self.gallery_view.get_checked_rows()
        if rows:
            self.bulk_comment_requested.emit(rows)

    def refresh_status_badges(self):
        """Refresh flag/comment badges from the live result AOI dicts."""
        self.gallery_view.refresh_status_badges(self.results)

    def _reference_label(self):
        """Human-readable label for the reference AOI (row 0 of results)."""
        if self.results:
            number = self.results[0].get('aoi_number')
            if number is not None:
                return self.tr("AOI #{number}").format(number=number)
        return self.tr("the selected AOI")

    def _on_thumbnail_clicked(self, row):
        """
        Handle thumbnail click.

        Args:
            row (int): Result row of the clicked thumbnail.
        """
        self.result_clicked.emit(row)

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.key() == Qt.Key_Escape:
            self.close()
            event.accept()
        elif event.key() == Qt.Key_R:
            self.gallery_view.reset_view()
            event.accept()
        else:
            super().keyPressEvent(event)
