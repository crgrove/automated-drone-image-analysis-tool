"""
CoverageExtentProgressDialog - Progress dialog for coverage extent calculation.

Shows progress bar, status message, and cancel button during coverage extent generation.
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QProgressBar
from PySide6.QtCore import Qt, Signal


class CoverageExtentProgressDialog(QDialog):
    """
    Progress dialog for coverage extent calculation.

    Displays progress bar showing percentage complete, status message,
    and cancel button to interrupt the operation.
    """

    # Signal emitted when user clicks cancel
    cancel_requested = Signal()

    def __init__(self, parent=None, total_images=0):
        """
        Initialize the progress dialog.

        Args:
            parent: Parent widget
            total_images: Total number of images to process
        """
        super().__init__(parent)
        self.setWindowTitle("Generating Coverage Extent")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(400, 150)

        self.total_images = total_images
        self.cancelled = False

        # Layout
        layout = QVBoxLayout()

        # Title label
        self.title_label = QLabel("Calculating coverage extent polygons...")
        self.title_label.setAlignment(Qt.AlignCenter)
        font = self.title_label.font()
        font.setBold(True)
        self.title_label.setFont(font)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(total_images if total_images > 0 else 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        # Status label
        self.status_label = QLabel("Starting...")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel_clicked)

        # Add widgets to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.cancel_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def on_cancel_clicked(self):
        """Handle cancel button click."""
        self.cancelled = True
        self.cancel_button.setEnabled(False)
        self.cancel_button.setText("Cancelling...")
        self.status_label.setText("Cancellation requested...")
        self.cancel_requested.emit()

    def update_progress(self, current, total, status_message=""):
        """
        Update the progress bar and status message.

        Args:
            current: Current number of images processed
            total: Total number of images
            status_message: Optional status message to display
        """
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

        if status_message:
            self.status_label.setText(status_message)
        else:
            self.status_label.setText(f"Processing image {current} of {total}...")

    def set_status(self, message):
        """
        Set the status message.

        Args:
            message: Status message to display
        """
        self.status_label.setText(message)

    def is_cancelled(self):
        """
        Check if cancellation was requested.

        Returns:
            bool: True if cancelled, False otherwise
        """
        return self.cancelled
