"""
GalleryUIComponent - Handles UI display for the AOI gallery view.

This component manages the QListView with grid layout, custom delegates,
and visual rendering of AOIs from all loaded images.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QListView, QPushButton, QFrame,
                               QAbstractItemView, QStyledItemDelegate, QStyle,
                               QStyleOptionViewItem, QApplication)
from PySide6.QtCore import Qt, QSize, QRect, QTimer, Signal, QModelIndex, QEvent, QObject
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QFontMetrics, QPixmap, QIcon, QKeyEvent
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
        self.gallery_controller = None  # Will be set by GalleryUIComponent
        
        # Create flag icons (same as single-image mode)
        self.flag_icon_active = qta.icon('fa6s.flag', color='#FF7043').pixmap(16, 16)
        self.flag_icon_inactive = qta.icon('fa6s.flag', color='#808080').pixmap(16, 16)

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
            user_data = index.data(Qt.UserRole)

            if not user_data:
                painter.restore()
                return

            aoi_data = user_data.get('aoi_data', {})

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

            # Draw flag icon in bottom-right corner (same as single-image mode)
            flagged = aoi_data.get('flagged', False)
            flag_icon = self.flag_icon_active if flagged else self.flag_icon_inactive
            flag_x = thumbnail_rect.right() - 20
            flag_y = thumbnail_rect.bottom() - 20
            painter.drawPixmap(flag_x, flag_y, flag_icon)

            # Draw comment indicator in top-left corner
            comment = aoi_data.get('user_comment', '').strip()
            if comment:
                # Use similar icon approach for comments
                comment_x = thumbnail_rect.left() + 5
                comment_y = thumbnail_rect.top() + 5
                # Draw a simple colored circle to indicate comment
                painter.setBrush(QColor(255, 215, 0))  # Gold color for comments
                painter.setPen(QPen(QColor(255, 255, 255), 1))
                painter.drawEllipse(comment_x, comment_y, 16, 16)
                # Draw text indicator
                painter.setPen(QPen(QColor(0, 0, 0), 2))
                font = painter.font()
                font.setPointSize(8)
                font.setBold(True)
                painter.setFont(font)
                painter.drawText(QRect(comment_x, comment_y, 16, 16), Qt.AlignCenter, "C")

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

        except Exception:
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


class GalleryUIComponent(QObject):
    """
    UI component for the AOI gallery view.

    Manages the QListView with grid layout and handles visual display.
    """

    # Signal for when an AOI is clicked
    aoi_clicked = Signal(int, int)  # image_idx, aoi_idx
    # Emitted when the view is first laid out with a valid size
    view_ready = Signal()

    def __init__(self, gallery_controller):
        """
        Initialize the gallery UI component.

        Args:
            gallery_controller: Reference to the GalleryController
        """
        super().__init__()
        self.gallery_controller = gallery_controller
        self.logger = LoggerService()

        # UI elements (will be set by controller)
        self.gallery_widget = None
        self.gallery_view = None
        self.count_label = None

        # Track when the view has a valid geometry and initial thumbnails are queued
        self._initial_thumbnails_loaded = False

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
        # Enable keyboard focus so keyboard shortcuts work
        self.gallery_view.setFocusPolicy(Qt.StrongFocus)
        
        # Override keyPressEvent to forward F key to parent window (like QtImageViewer does)
        original_keyPressEvent = self.gallery_view.keyPressEvent
        def keyPressEvent(event):
            if event.key() == Qt.Key_F and event.modifiers() == Qt.NoModifier:
                # Forward F key to parent window's keyPressEvent
                if self.gallery_view.window():
                    self.gallery_view.window().keyPressEvent(event)
                return
            original_keyPressEvent(event)
        self.gallery_view.keyPressEvent = keyPressEvent

        # Set fixed grid size for consistent columns
        self.gallery_view.setGridSize(QSize(200, 200))  # Width, Height (thumbnail + spacing)

        # Set custom delegate
        delegate = AOIGalleryDelegate(self.gallery_view)
        delegate.gallery_controller = self.gallery_controller
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

        # Listen for layout/visibility changes and handle flag button clicks
        self.gallery_view.installEventFilter(self)
        self.gallery_view.viewport().installEventFilter(self)

        # Connect to view signals to trigger thumbnail loading when view becomes visible
        # (handled in eventFilter and showEvent)

        layout.addWidget(self.gallery_view)

        self.gallery_widget = widget
        return widget

    def _create_header_widget(self):
        """Create the header widget (empty - main AOI title is used instead)."""
        # Return empty widget - the main AOI header title will be updated instead
        header = QWidget()
        header.setFixedHeight(0)  # Make it invisible
        header.setMaximumHeight(0)

        # Keep count_label for internal tracking (but don't display it)
        self.count_label = QLabel("0 AOIs")
        self.count_label.setVisible(False)  # Hidden - we'll update main title instead

        return header

    def set_model(self, model):
        """Set the data model for the gallery view."""
        if self.gallery_view:
            self.gallery_view.setModel(model)
            # Connect model changes to update header
            model.modelReset.connect(self._on_model_changed)
            model.rowsInserted.connect(lambda *_: self._on_model_changed())
            # Update count label (will update header if in gallery mode)
            self._update_count_label(model.rowCount())
            # Connect model readiness signals to trigger initial thumbnail loading
            model.modelReset.connect(self._on_model_ready)
            model.rowsInserted.connect(lambda *_: self._on_model_ready())

    def _on_model_changed(self):
        """Handle model changes - update header and reload thumbnails if in gallery mode."""
        if self.gallery_view and self.gallery_view.model():
            count = self.gallery_view.model().rowCount()
            self._update_count_label(count)

            # When model changes (e.g., after filtering/sorting), reload visible thumbnails
            # Reset the flag so thumbnails can be reloaded
            self._initial_thumbnails_loaded = False

            # Always trigger thumbnail loading when model changes
            # The model's _queue_visible_thumbnails() queues initial items, but we need to
            # ensure visible items are prioritized
            if self.gallery_widget and self.gallery_widget.isVisible():
                # Check if viewport is ready
                viewport_rect = self.gallery_view.viewport().rect() if self.gallery_view else QRect()
                if viewport_rect.width() > 0 and viewport_rect.height() > 0:
                    self._load_visible_thumbnails()
                    self._initial_thumbnails_loaded = True

    def _update_count_label(self, count):
        """Update the count label with the number of AOIs."""
        if self.count_label:
            self.count_label.setText(f"{count} AOI{'s' if count != 1 else ''}")

        # Also update the main AOI header title when in gallery mode
        if (self.gallery_controller and
                hasattr(self.gallery_controller.parent, 'gallery_mode') and
                self.gallery_controller.parent.gallery_mode and
                hasattr(self.gallery_controller.parent, 'areaCountLabel')):
            self._update_main_aoi_header(count)

    def _update_main_aoi_header(self, count):
        """Update the main AOI header title to show gallery mode with count."""
        if (self.gallery_controller and
                hasattr(self.gallery_controller.parent, 'areaCountLabel')):
            area_count_label = self.gallery_controller.parent.areaCountLabel
            if area_count_label:
                # Format: "# Areas of Interest - Gallery Mode" (matching single-image format)
                area_text = f"{count} {'Area' if count == 1 else 'Areas'} of Interest"
                area_count_label.setText(area_text)

    def _on_item_clicked(self, index):
        """Handle item click in the gallery."""
        try:
            if not index.isValid():
                return

            # Set the clicked item as the current selection (needed for keyboard shortcuts)
            self.gallery_view.setCurrentIndex(index)
            # Give focus to the gallery view so keyboard shortcuts work
            self.gallery_view.setFocus()

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
        self._load_visible_thumbnails()

    def _load_visible_thumbnails(self):
        """Queue thumbnails for currently visible items."""
        try:
            if not self.gallery_view or not self.gallery_view.model():
                return

            model = self.gallery_view.model()

            # Get visible rectangle
            visible_rect = self.gallery_view.viewport().rect()
            if visible_rect.width() <= 0 or visible_rect.height() <= 0:
                return

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

    def _on_model_ready(self):
        """Triggered when the model resets or rows are inserted."""
        try:
            # Always reload thumbnails when model resets (model may have been filtered/sorted)
            if self.gallery_widget and self.gallery_widget.isVisible():
                # Reset flag to allow reloading
                self._initial_thumbnails_loaded = False
                # Load thumbnails if viewport is ready
                model = self.gallery_view.model() if self.gallery_view else None
                viewport_rect = self.gallery_view.viewport().rect() if self.gallery_view else QRect()
                if model and model.rowCount() > 0 and viewport_rect.width() > 0 and viewport_rect.height() > 0:
                    self._load_visible_thumbnails()
                    self._initial_thumbnails_loaded = True
                    if not hasattr(self, '_view_ready_emitted'):
                        self.view_ready.emit()
                        self._view_ready_emitted = True
        except Exception as e:
            self.logger.debug(f"Error in _on_model_ready: {e}")

    def eventFilter(self, obj, event):
        """Watch for the first time the view/viewport has a valid size, handle flag button clicks, and keyboard events."""
        try:
            # Handle mouse clicks on flag button
            if (obj == self.gallery_view.viewport() and 
                    event.type() == QEvent.MouseButtonPress and
                    event.button() == Qt.LeftButton):
                # Get the item at the click position
                index = self.gallery_view.indexAt(event.pos())
                if index.isValid():
                    # Get model and delegate
                    model = self.gallery_view.model()
                    delegate = self.gallery_view.itemDelegate()
                    
                    if model and delegate and hasattr(delegate, 'gallery_controller'):
                        # Get item rect
                        option = QStyleOptionViewItem()
                        option.initFrom(self.gallery_view)
                        option.rect = self.gallery_view.visualRect(index)
                        
                        # Check if click is on flag button using delegate's logic
                        user_data = index.data(Qt.UserRole)
                        if user_data:
                            aoi_data = user_data.get('aoi_data', {})
                            image_idx = user_data.get('image_idx')
                            aoi_idx = user_data.get('aoi_idx')
                            
                            if image_idx is not None and aoi_idx is not None:
                                # Calculate thumbnail rect
                                thumbnail_size = QSize(180, 180)
                                item_spacing = 10
                                thumbnail_rect = QRect(
                                    option.rect.left() + item_spacing // 2,
                                    option.rect.top() + item_spacing // 2,
                                    thumbnail_size.width(),
                                    thumbnail_size.height()
                                )
                                
                                # Check if click is on flag button (bottom-right corner, 16x16 icon)
                                flag_rect = QRect(thumbnail_rect.right() - 20, thumbnail_rect.bottom() - 20, 16, 16)
                                if flag_rect.contains(event.pos()):
                                    # Ensure this item is selected before toggling
                                    if self.gallery_view.currentIndex() != index:
                                        self.gallery_view.setCurrentIndex(index)
                                    # Toggle flag
                                    if delegate.gallery_controller:
                                        delegate.gallery_controller.toggle_aoi_flag_by_index(image_idx, aoi_idx)
                                    # Prevent the click from propagating to cause other selections
                                    event.accept()
                                    return True
                                
                                # Check if click is on comment button (top-left corner, 16x16 icon)
                                comment_rect = QRect(thumbnail_rect.left() + 5, thumbnail_rect.top() + 5, 16, 16)
                                if comment_rect.contains(event.pos()):
                                    # Could add comment editing here in the future
                                    # For now, just accept the event to prevent item selection
                                    event.accept()
                                    return True
            
            # Watch for the first time the view/viewport has a valid size
            if event.type() in (QEvent.Show, QEvent.Resize, QEvent.LayoutRequest):
                if (self.gallery_widget and self.gallery_widget.isVisible() and
                        not self._initial_thumbnails_loaded):
                    # Ensure we have a model with rows and a valid viewport size
                    model = self.gallery_view.model() if self.gallery_view else None
                    viewport_rect = self.gallery_view.viewport().rect() if self.gallery_view else QRect()
                    if model and model.rowCount() > 0 and viewport_rect.width() > 0 and viewport_rect.height() > 0:
                        self._load_visible_thumbnails()
                        self._initial_thumbnails_loaded = True
                        self.view_ready.emit()
        except Exception:
            pass
        return super().eventFilter(obj, event)

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
