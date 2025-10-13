"""PDFExportDialog - Pure UI dialog for collecting PDF export settings."""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout
from PySide6.QtCore import Qt

from core.services.PDFSettingsService import PDFSettingsService


class PDFExportDialog(QDialog):
    """Dialog for entering organization and search name for PDF export."""

    def __init__(self, parent):
        """Initialize the PDF export settings dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.settings_service = PDFSettingsService()
        self.setupUi()
        self.load_settings()

    def setupUi(self):
        """Set up the dialog UI."""
        self.setWindowTitle("PDF Export Settings")
        self.setModal(True)
        self.setMinimumWidth(400)

        # Main layout
        layout = QVBoxLayout()

        # Instructions
        instructions = QLabel("Enter the following information for the PDF report:")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Form layout for inputs
        form_layout = QFormLayout()

        # Organization name input
        self.organization_input = QLineEdit()
        self.organization_input.setPlaceholderText("Enter organization name")
        form_layout.addRow("Organization:", self.organization_input)

        # Search name input
        self.search_name_input = QLineEdit()
        self.search_name_input.setPlaceholderText("Enter search name")
        form_layout.addRow("Search Name:", self.search_name_input)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.on_ok_clicked)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Set focus to organization input
        self.organization_input.setFocus()

    def on_ok_clicked(self):
        """Handle OK button click."""
        # Save settings before accepting
        self.save_settings()
        self.accept()

    def load_settings(self):
        """Load previously saved settings from config file."""
        settings = self.settings_service.load_settings()
        self.organization_input.setText(settings.get('organization', ''))
        self.search_name_input.setText(settings.get('search_name', ''))

    def save_settings(self):
        """Save current settings to config file."""
        self.settings_service.save_settings(
            self.organization_input.text(),
            self.search_name_input.text()
        )

    def get_organization(self):
        """Get the entered organization name.

        Returns:
            str: The organization name
        """
        return self.organization_input.text().strip()

    def get_search_name(self):
        """Get the entered search name.

        Returns:
            str: The search name
        """
        return self.search_name_input.text().strip()

