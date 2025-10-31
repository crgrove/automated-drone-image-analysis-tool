"""
GalleryUIComponent - Handles UI display for the AOI gallery view.

This component manages the QListView with grid layout, custom delegates,
and visual rendering of AOIs from all loaded images.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QListView, QPushButton, QFrame, QAbstractItemView,
                                QStyledItemDelegate, QStyle, QStyleOptionViewItem)
from PySide6.QtCore import Qt, QSize, QRect, QTimer, Signal, QModelIndex
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QFontMetrics, QPixmap, QIcon
import qtawesome as qta

from core.services.LoggerService import LoggerService


class AOIGalleryDelegate(QStyledItemDelegate):
    """Custom delegate for rendering AOI gallery items with overlays."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thumbnail_size = QSize(180, 180)
        self.item_spacing = 10
        # Cache the size hint for consistency and performance
        # Only thumbnail + spacing, no text overlay needed
        self._cached_size_hint = QSize(190, 190)

    def sizeHint(self, option, index):
        """Return the size hint for each item."""
        # Return cached size hint for consistency and performance
        return self._cached_size_hint

    def paint(self, painter, option, index):
        """Custom paint for AOI gallery items."""
        painter.save()

        try:
            # Get data from model
            icon = index.data(Qt.DecorationRole)
            text = index.data(Qt.DisplayRole)
            user_data = index.data(Qt.UserRole)

            if not user_data:
                painter.restore()
                return

            aoi_data = user_data.get('aoi_data', {})
            image_idx = user_data.get('image_idx', -1)
            aoi_idx = user_data.get('aoi_idx', -1)

            # Calculate layout rectangles
            thumbnail_rect = QRect(
                option.rect.left() + self.item_spacing // 2,
                option.rect.top() + self.item_spacing // 2,
                self.thumbnail_size.width(),
                self.thumbnail_size.height()
            )

            # Draw selection highlight if selected
            if option.state & QStyle.State_Selected:
                painter.fillRect(option.rect, QColor(100, 150, 255, 50))
                painter.setPen(QPen(QColor(100, 150, 255), 2))
                painter.drawRect(option.rect.adjusted(1, 1, -1, -1))

            # Draw thumbnail background
            painter.fillRect(thumbnail_rect, QColor(40, 40, 40))

            # Draw thumbnail image
            if icon and not icon.isNull():
                pixmap = icon.pixmap(self.thumbnail_size)
                # Center the pixmap in the thumbnail rect
                scaled_size = pixmap.size().scaled(self.thumbnail_size, Qt.KeepAspectRatio)
                x_offset = (self.thumbnail_size.width() - scaled_size.width()) // 2
                y_offset = (self.thumbnail_size.height() - scaled_size.height()) // 2
                target_rect = QRect(
                    thumbnail_rect.left() + x_offset,
                    thumbnail_rect.top() + y_offset,
                    scaled_size.width(),
                    scaled_size.height()
                )
                painter.drawPixmap(target_rect, pixmap)

            # Draw thumbnail border
            painter.setPen(QPen(QColor(100, 100, 100), 1))
            painter.drawRect(thumbnail_rect)

            # Draw flagged indicator
            flagged = aoi_data.get('flagged', False)
            if flagged:
                flag_rect = QRect(thumbnail_rect.right() - 30, thumbnail_rect.top() + 5, 25, 25)
                painter.fillRect(flag_rect, QColor(255, 50, 50, 200))
                painter.setPen(QPen(QColor(255, 255, 255), 2))
                painter.drawText(flag_rect, Qt.AlignCenter, "🚩")

            # Draw comment indicator
            comment = aoi_data.get('user_comment', '').strip()
            if comment:
                comment_rect = QRect(thumbnail_rect.left() + 5, thumbnail_rect.top() + 5, 25, 25)
                painter.fillRect(comment_rect, QColor(50, 150, 255, 200))
                painter.setPen(QPen(QColor(255, 255, 255), 2))
                painter.drawText(comment_rect, Qt.AlignCenter, "💬")

            # Draw color swatch indicator (bottom-left corner of thumbnail)
            color_info = user_data.get('color_info')
            if color_info:
                color_rgb = color_info.get('rgb')
                if color_rgb:
                    # 12x12 pixel swatch in bottom-left corner
                    swatch_size = 12
                    swatch_rect = QRect(
                        thumbnail_rect.left() + 5,
                        thumbnail_rect.bottom() - swatch_size - 5,
                        swatch_size,
                        swatch_size
                    )
                    # Draw fully opaque color swatch
                    painter.fillRect(swatch_rect, QColor(color_rgb[0], color_rgb[1], color_rgb[2]))
                    # Draw white border (1px)
                    painter.setPen(QPen(QColor(255, 255, 255), 1))
                    painter.drawRect(swatch_rect)

        except Exception as e:
            # Fallback to default rendering on error
            pass

        painter.restore()

    def _get_confidence_color(self, confidence):
        """Get color based on confidence level."""
        if confidence >= 0.8:
            return QColor(50, 255, 50)  # Green
        elif confidence >= 0.5:
            return QColor(255, 200, 50)  # Yellow
        else:
            return QColor(255, 100, 50)  # Orange/Red


class GalleryUIComponent:
    """
    UI component for the AOI gallery view.

    Manages the QListView with grid layout and handles visual display.
    """

    # Signal for when an AOI is clicked
    aoi_clicked = Signal(int, int)  # image_idx, aoi_idx

    def __init__(self, gallery_controller):
        """
        Initialize the gallery UI component.

        Args:
            gallery_controller: Reference to the GalleryController
        """
        self.gallery_controller = gallery_controller
        self.logger = LoggerService()

        # UI elements (will be set by controller)
        self.gallery_widget = None
        self.gallery_view = None
        self.count_label = None

        # Scroll debounce timer for performance
        self.scroll_timer = QTimer()
        self.scroll_timer.setSingleShot(True)
        self.scroll_timer.setInterval(100)  # 100ms debounce

    def create_gallery_widget(self, parent=None):
        """
        Create the main gallery widget.

        Args:
            parent: Parent widget

        Returns:
            QWidget: The gallery widget
        """
        # Create main widget
        widget = QWidget(parent)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Create header with controls
        header = self._create_header_widget()
        layout.addWidget(header)

        # Create gallery list view
        self.gallery_view = QListView()
        self.gallery_view.setViewMode(QListView.IconMode)
        self.gallery_view.setResizeMode(QListView.Adjust)
        self.gallery_view.setUniformItemSizes(True)  # Items have consistent size for better performance
        self.gallery_view.setSpacing(10)
        self.gallery_view.setWrapping(True)
        self.gallery_view.setFlow(QListView.LeftToRight)
        self.gallery_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.gallery_view.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.gallery_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Set fixed grid size for consistent columns
        self.gallery_view.setGridSize(QSize(200, 200))  # Width, Height (thumbnail + spacing)

        # Set custom delegate
        delegate = AOIGalleryDelegate(self.gallery_view)
        self.gallery_view.setItemDelegate(delegate)

        # Style the view
        self.gallery_view.setStyleSheet("""
            QListView {
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 4px;
            }
            QListView::item {
                background-color: transparent;
            }
            QListView::item:hover {
                background-color: rgba(100, 150, 255, 30);
            }
        """)

        # Connect signals
        self.gallery_view.clicked.connect(self._on_item_clicked)
        self.gallery_view.verticalScrollBar().valueChanged.connect(self._on_scroll)

        # Timer for delayed thumbnail loading
        self.thumbnail_load_timer = QTimer()
        self.thumbnail_load_timer.setSingleShot(True)
        self.thumbnail_load_timer.timeout.connect(self._load_visible_thumbnails)
        self.thumbnail_load_timer.setInterval(50)  # Faster response

        layout.addWidget(self.gallery_view)

        self.gallery_widget = widget
        return widget

    def _create_header_widget(self):
        """Create the header widget with title and controls."""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(5, 5, 5, 5)

        # Title label
        title = QLabel("AOI Gallery - All Images")
        title_font = title.font()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Count label
        self.count_label = QLabel("0 AOIs")
        header_layout.addWidget(self.count_label)

        return header

    def set_model(self, model):
        """Set the data model for the gallery view."""
        if self.gallery_view:
            self.gallery_view.setModel(model)
            self._update_count_label(model.rowCount())
            # Trigger initial thumbnail loading after a short delay
            self.thumbnail_load_timer.start()

    def _update_count_label(self, count):
        """Update the count label with the number of AOIs."""
        if self.count_label:
            self.count_label.setText(f"{count} AOI{'s' if count != 1 else ''}")

    def _on_item_clicked(self, index):
        """Handle item click in the gallery."""
        try:
            if not index.isValid():
                return

            # Get AOI info from model
            model = self.gallery_view.model()
            aoi_info = model.get_aoi_info(index)

            if aoi_info:
                image_idx, aoi_idx, aoi_data = aoi_info
                # Notify controller
                self.gallery_controller.on_aoi_clicked(image_idx, aoi_idx, aoi_data)

        except Exception as e:
            self.logger.error(f"Error handling gallery item click: {e}")

    def _on_scroll(self, value):
        """Handle scroll events for lazy loading."""
        # Debounce scroll events
        if self.scroll_timer.isActive():
            self.scroll_timer.stop()
        self.scroll_timer.timeout.connect(self._handle_scroll_end)
        self.scroll_timer.start()

    def _handle_scroll_end(self):
        """Handle scroll end for potential optimizations."""
        # Trigger loading of visible thumbnails after scroll
        self.thumbnail_load_timer.start()

    def _load_visible_thumbnails(self):
        """Queue thumbnails for currently visible items."""
        try:
            if not self.gallery_view or not self.gallery_view.model():
                return

            model = self.gallery_view.model()

            # Get visible rectangle
            visible_rect = self.gallery_view.viewport().rect()

            # Get visible item range (with buffer)
            first_visible = self.gallery_view.indexAt(visible_rect.topLeft())
            last_visible = self.gallery_view.indexAt(visible_rect.bottomRight())

            if not first_visible.isValid():
                return

            start_row = first_visible.row()
            end_row = last_visible.row() if last_visible.isValid() else start_row + 20

            # Use the model's new queueing method
            # Queue visible with high priority
            model.queue_thumbnails_for_range(start_row, end_row, high_priority=True)

            # Queue buffer zones with normal priority
            buffer_start = max(0, start_row - 20)
            buffer_end = min(model.rowCount() - 1, end_row + 20)

            # Before visible
            if buffer_start < start_row:
                model.queue_thumbnails_for_range(buffer_start, start_row - 1, high_priority=False)

            # After visible
            if buffer_end > end_row:
                model.queue_thumbnails_for_range(end_row + 1, buffer_end, high_priority=False)

        except Exception as e:
            self.logger.error(f"Error queuing visible thumbnails: {e}")


    def refresh_gallery(self):
        """Refresh the gallery display."""
        if self.gallery_view and self.gallery_view.model():
            model = self.gallery_view.model()
            self.gallery_view.viewport().update()
            self._update_count_label(model.rowCount())

    def clear_gallery(self):
        """Clear the gallery display."""
        if self.gallery_view:
            model = self.gallery_view.model()
            if model:
                model.set_aoi_items([])
            self._update_count_label(0)

    def get_visible_range(self):
        """
        Get the range of visible items in the gallery.

        Returns:
            Tuple of (first_visible_index, last_visible_index)
        """
        if not self.gallery_view:
            return (0, 0)

        try:
            # Get visible rectangle
            visible_rect = self.gallery_view.viewport().rect()
            top_index = self.gallery_view.indexAt(visible_rect.topLeft())
            bottom_index = self.gallery_view.indexAt(visible_rect.bottomRight())

            if not top_index.isValid():
                return (0, 0)

            first = top_index.row()
            last = bottom_index.row() if bottom_index.isValid() else first + 20

            return (first, last)

        except Exception:
            return (0, 0)
