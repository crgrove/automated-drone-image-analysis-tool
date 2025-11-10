"""AOICreationDialog - Simple confirmation dialog for creating an AOI."""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt


class AOICreationDialog(QDialog):
    """Simple dialog to confirm AOI creation."""

    def __init__(self, parent):
        """Initialize the AOI creation confirmation dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Create AOI")
        self.setModal(True)
        self.setMinimumWidth(250)

        # Main layout
        layout = QVBoxLayout()

        # Message label
        message = QLabel("Create AOI?")
        message.setAlignment(Qt.AlignCenter)
        message.setStyleSheet("QLabel { font-size: 12pt; padding: 10px; }")
        layout.addWidget(message)

        # Buttons
        button_layout = QHBoxLayout()

        self.yes_button = QPushButton("Yes")
        self.yes_button.setDefault(True)  # Make Yes the default action
        self.yes_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.yes_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        self.setLayout(layout)
