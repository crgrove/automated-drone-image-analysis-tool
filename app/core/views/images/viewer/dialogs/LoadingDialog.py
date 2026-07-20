from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QMovie
from PySide6.QtCore import Qt, QSize
from helpers.TranslationMixin import TranslationMixin


class LoadingDialog(TranslationMixin, QDialog):
    """Custom dialog for showing a loading spinner and message."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Generating Report"))
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(300, 200)

        # Layout and widgets
        layout = QVBoxLayout()

        # Add spinning loader
        self.spinner_label = QLabel(self)
        self.spinner_label.setAlignment(Qt.AlignCenter)
        self.spinner_movie = QMovie(":/icons/loading.gif")  # Path to your GIF in the resource file
        self.spinner_movie.setScaledSize(QSize(50, 50))  # Adjust the size if needed
        self.spinner_label.setMovie(self.spinner_movie)
        self.spinner_movie.start()  # Start the animation

        # Add message label
        self.message_label = QLabel(self.tr("Report generation in progress..."))
        self.message_label.setAlignment(Qt.AlignCenter)

        # Add cancel button
        self.cancel_button = QPushButton(self.tr("Cancel"))
        self.cancel_button.clicked.connect(self.reject)

        # Add widgets to layout
        layout.addWidget(self.spinner_label)
        layout.addWidget(self.message_label)
        layout.addWidget(self.cancel_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        self._apply_translations()

    def showEvent(self, event):
        """Override showEvent to ensure dialog appears and receives focus on macOS."""
        super().showEvent(event)
        # On macOS, modal dialogs sometimes need explicit activation to appear
        self.activateWindow()
        self.raise_()
