"""
Simple thumbnail loader that runs in a background thread without blocking UI.
"""

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QPixmap, QIcon, QImageReader
from PySide6.QtCore import QSize


class ThumbnailLoader(QObject):
    """Background thumbnail loader that processes thumbnails on demand."""

    thumbnail_loaded = Signal(int, QIcon)

    def __init__(self, images, thumbnail_size=(100, 56)):
        super().__init__()
        self.images = images
        self.thumbnail_size = QSize(*thumbnail_size)
        self.loaded_indices = set()

    @Slot(int)
    def load_thumbnail(self, index):
        """Load a single thumbnail (called from main thread via signal)."""
        if index in self.loaded_indices:
            return
        if index < 0 or index >= len(self.images):
            return

        try:
            # Load thumbnail
            image_path = self.images[index].get('path', '')
            if image_path:
                reader = QImageReader(image_path)
                reader.setScaledSize(self.thumbnail_size)
                pixmap = QPixmap.fromImage(reader.read())
                if not pixmap.isNull():
                    icon = QIcon(pixmap)
                    self.thumbnail_loaded.emit(index, icon)
                    self.loaded_indices.add(index)
        except Exception:
            pass  # Skip failed thumbnails
