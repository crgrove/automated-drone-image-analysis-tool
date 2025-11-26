"""
ExportProgressDialog - Generic progress dialog for export operations.

Shows progress bar, status message, and cancel button during export operations.
Can be used for PDF exports, KML exports, and other export operations.
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QProgressBar, QWidget
from PySide6.QtCore import Qt, Signal


class ExportProgressDialog(QDialog):
    """
    Generic progress dialog for export operations.

    Displays progress bar showing percentage complete, status message,
    and cancel button to interrupt the operation.
    """

    # Signal emitted when user clicks cancel
    cancel_requested = Signal()

    def __init__(self, parent=None, title="Exporting", total_items=0):
        """
        Initialize the progress dialog.

        Args:
            parent: Parent widget
            title: Title for the dialog window
            total_items: Total number of items to process
        """
        # Validate parent widget to prevent access violations
        # This is especially important in test environments
        if parent is not None and not isinstance(parent, QWidget):
            parent = None
        elif parent is not None:
            # Additional check: ensure widget is not deleted
            try:
                _ = parent.isWidgetType()
            except (RuntimeError, AttributeError):
                # Widget has been deleted or is invalid
                parent = None

        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(400, 150)

        self.total_items = total_items
        self.cancelled = False

        # Layout
        layout = QVBoxLayout()

        # Title label
        self.title_label = QLabel("Processing...")
        self.title_label.setAlignment(Qt.AlignCenter)
        font = self.title_label.font()
        font.setBold(True)
        self.title_label.setFont(font)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(total_items if total_items > 0 else 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        # Status label
        self.status_label = QLabel("Starting...")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Cancel button
        self.cancel_button = QPushButton("Cancel")

        # Add widgets to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.cancel_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

        # Connect signal after layout is set to ensure widget hierarchy is established
        # This helps avoid access violations in test environments
        self.cancel_button.clicked.connect(self.on_cancel_clicked)

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
            current: Current number of items processed
            total: Total number of items
            status_message: Optional status message to display
        """
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

        if status_message:
            self.status_label.setText(status_message)
        else:
            self.status_label.setText(f"Processing item {current} of {total}...")

    def set_status(self, message):
        """
        Set the status message.

        Args:
            message: Status message to display
        """
        self.status_label.setText(message)

    def set_title(self, title):
        """
        Set the title label text.

        Args:
            title: Title text to display
        """
        self.title_label.setText(title)

    def is_cancelled(self):
        """
        Check if cancellation was requested.

        Returns:
            bool: True if cancelled, False otherwise
        """
        return self.cancelled
