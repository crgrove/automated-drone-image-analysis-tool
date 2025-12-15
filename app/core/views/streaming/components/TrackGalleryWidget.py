"""
TrackGalleryWidget - Gallery widget for confirmed track detections with click-to-seek.

Displays confirmed detections as clickable thumbnails in a grid layout.
Clicking a thumbnail emits a signal to seek the video to that detection's timestamp.
"""

import cv2
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
from PySide6.QtGui import QImage, QPixmap, QIcon
from PySide6.QtCore import Qt, Signal, QSize


class TrackGalleryWidget(QWidget):
    """Displays confirmed detections as clickable thumbnails in a gallery view.

    Features:
    - Icon mode display with configurable thumbnail size
    - Click-to-seek: clicking a thumbnail emits track_clicked signal
    - Auto-updates count label
    - Newest detections appear first
    """

    # Emitted when user clicks a gallery item, passes the Track object
    track_clicked = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the gallery UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Header
        self.header = QLabel("Detection Gallery")
        self.header.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(self.header)

        # Gallery list widget (icon mode per design doc)
        self.gallery_list = QListWidget()
        self.gallery_list.setViewMode(QListWidget.IconMode)
        self.gallery_list.setResizeMode(QListWidget.Adjust)
        self.gallery_list.setIconSize(QSize(120, 120))
        self.gallery_list.setMovement(QListWidget.Static)
        self.gallery_list.setSpacing(8)
        self.gallery_list.setWrapping(True)
        self.gallery_list.setUniformItemSizes(True)
        self.gallery_list.itemClicked.connect(self._on_item_clicked)

        # Styling for dark theme compatibility
        self.gallery_list.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                border: 1px solid #555;
            }
            QListWidget::item {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
                color: #ffffff;
            }
            QListWidget::item:selected {
                background-color: #4a90d9;
                border: 2px solid #5ba0e9;
            }
            QListWidget::item:hover {
                background-color: #4c4c4c;
                border: 1px solid #666;
            }
        """)

        layout.addWidget(self.gallery_list)

        # Count label
        self.count_label = QLabel("0 detections")
        self.count_label.setStyleSheet("color: #888;")
        layout.addWidget(self.count_label)

    def add_track(self, track):
        """Add a confirmed track to the gallery.

        Args:
            track: Track object with thumbnail, first_timestamp, etc.
        """
        if track.saved_to_gallery:
            return

        # Get thumbnail from track
        thumb = track.thumbnail
        if thumb is None or thumb.size == 0:
            return

        # Convert BGR thumbnail to QIcon
        h, w = thumb.shape[:2]
        if len(thumb.shape) == 3:
            # Color image - convert BGR to RGB
            rgb = cv2.cvtColor(thumb, cv2.COLOR_BGR2RGB)
            bytes_per_line = 3 * w
            q_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        else:
            # Grayscale
            q_img = QImage(thumb.data, w, h, w, QImage.Format_Grayscale8)

        # Scale to icon size while maintaining aspect ratio
        pixmap = QPixmap.fromImage(q_img)
        scaled_pixmap = pixmap.scaled(
            self.gallery_list.iconSize(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        icon = QIcon(scaled_pixmap)

        # Create item with icon and frame number label
        item = QListWidgetItem(icon, f"Frame {track.first_frame_index}")

        # Store track object in item data for retrieval on click
        item.setData(Qt.UserRole, track)

        # Insert at beginning (newest first)
        self.gallery_list.insertItem(0, item)

        # Mark track as saved to prevent duplicates
        track.saved_to_gallery = True

        # Update count
        self._update_count()

    def _on_item_clicked(self, item: QListWidgetItem):
        """Handle gallery item click - emit track for seeking."""
        track = item.data(Qt.UserRole)
        if track:
            self.track_clicked.emit(track)

    def _update_count(self):
        """Update the detection count label."""
        count = self.gallery_list.count()
        if count == 1:
            self.count_label.setText("1 detection")
        else:
            self.count_label.setText(f"{count} detections")

    def clear(self):
        """Clear all gallery items."""
        self.gallery_list.clear()
        self._update_count()

    def set_icon_size(self, size: int):
        """Set the thumbnail icon size.

        Args:
            size: Icon size in pixels (both width and height)
        """
        self.gallery_list.setIconSize(QSize(size, size))
