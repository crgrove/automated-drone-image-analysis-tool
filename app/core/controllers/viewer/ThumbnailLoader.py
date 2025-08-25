from PyQt5.QtCore import QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QImageReader, QPixmap


class ThumbnailLoader(QThread):
    """Threaded loader for generating and displaying image thumbnails."""

    thumbnail_loaded = pyqtSignal(int, QIcon)

    def __init__(self, images, start_index, end_index, existing_thumbnails, parent=None):
        """Initializes the thumbnail loader.

        Args:
            images (list): List of image data dictionaries.
            start_index (int): Starting index for thumbnail loading.
            end_index (int): Ending index for thumbnail loading.
            existing_thumbnails (list): Indices of already loaded thumbnails.
            parent (QObject, optional): Parent object for the loader.
        """
        super().__init__(parent)
        self.images = images
        self.start_index = max(start_index, 0)
        self.end_index = min(end_index, len(images))
        self.existing_thumbnails = existing_thumbnails

    def run(self):
        """Runs the thumbnail loading process."""
        for index in range(self.start_index, self.end_index):
            if index not in self.existing_thumbnails:
                image_path = self.images[index]['path']
                reader = QImageReader(image_path)
                reader.setScaledSize(QSize(100, 56))
                pixmap = QPixmap.fromImage(reader.read())
                icon = QIcon(pixmap)
                self.thumbnail_loaded.emit(index, icon)