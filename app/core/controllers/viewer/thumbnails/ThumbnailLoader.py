"""
Simple thumbnail loader that runs in a background thread without blocking UI.
"""

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QPixmap, QIcon, QImageReader
from PySide6.QtCore import QSize


class ThumbnailLoader(QObject):
    """Background thumbnail loader that processes thumbnails on demand."""

    thumbnail_loaded = Signal(int, QIcon)

    def __init__(self, images, thumbnail_size=(100, 56), results_dir=None):
        super().__init__()
        self.images = images
        self.thumbnail_size = QSize(*thumbnail_size)
        self.loaded_indices = set()
        self.results_dir = results_dir

    @Slot(int)
    def load_thumbnail(self, index):
        """Load a single thumbnail (called from main thread via signal)."""
        if index in self.loaded_indices:
            return
        if index < 0 or index >= len(self.images):
            return

        try:
            image_path = self.images[index].get('path', '')
            if not image_path:
                return

            # First, try to load from cache
            cached_thumb = self._load_cached_thumbnail(image_path)
            if cached_thumb:
                icon = QIcon(cached_thumb)
                self.thumbnail_loaded.emit(index, icon)
                self.loaded_indices.add(index)
                return

            # Fallback: Load from original image and scale
            reader = QImageReader(image_path)
            reader.setScaledSize(self.thumbnail_size)
            pixmap = QPixmap.fromImage(reader.read())
            if not pixmap.isNull():
                icon = QIcon(pixmap)
                self.thumbnail_loaded.emit(index, icon)
                self.loaded_indices.add(index)
        except Exception:
            pass  # Skip failed thumbnails

    def is_cached(self, image_path):
        """
        Check if a thumbnail is cached without loading it.

        Checks both new (portable) and legacy cache keys for backward compatibility.

        Args:
            image_path: Path to the original image

        Returns:
            bool: True if cached, False otherwise
        """
        try:
            import hashlib
            import os
            from pathlib import Path

            # If we don't have a results directory, can't check cache
            if not self.results_dir:
                return False

            results_path = Path(self.results_dir)
            thumb_dir = results_path / '.image_thumbnails'

            # Try new (portable) key - filename only
            filename = os.path.basename(image_path)
            path_hash = hashlib.md5(filename.encode()).hexdigest()
            thumb_path = thumb_dir / f"{path_hash}.jpg"

            if thumb_path.exists():
                return True

            # Try legacy key - absolute path
            abs_path = os.path.abspath(image_path)
            legacy_hash = hashlib.md5(abs_path.encode()).hexdigest()
            legacy_thumb_path = thumb_dir / f"{legacy_hash}.jpg"

            return legacy_thumb_path.exists()
        except Exception:
            return False

    def _load_cached_thumbnail(self, image_path):
        """
        Load a cached thumbnail if it exists.

        Tries both new (portable) and legacy cache keys for backward compatibility.

        Args:
            image_path: Path to the original image

        Returns:
            QPixmap or None
        """
        try:
            import hashlib
            import os
            from pathlib import Path

            # If we don't have a results directory, can't load cache
            if not self.results_dir:
                return None

            results_path = Path(self.results_dir)
            thumb_dir = results_path / '.image_thumbnails'

            # Try new (portable) key - filename only
            filename = os.path.basename(image_path)
            path_hash = hashlib.md5(filename.encode()).hexdigest()
            thumb_path = thumb_dir / f"{path_hash}.jpg"

            if thumb_path.exists():
                return QPixmap(str(thumb_path))

            # Try legacy key - absolute path
            abs_path = os.path.abspath(image_path)
            legacy_hash = hashlib.md5(abs_path.encode()).hexdigest()
            legacy_thumb_path = thumb_dir / f"{legacy_hash}.jpg"

            if legacy_thumb_path.exists():
                return QPixmap(str(legacy_thumb_path))

            return None
        except Exception:
            return None
