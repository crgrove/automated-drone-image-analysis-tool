"""PDFExportDialog - Dialog for collecting PDF export settings."""

import os
import json
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout
from PySide6.QtCore import Qt


class PDFExportDialog(QDialog):
    """Dialog for entering organization and search name for PDF export."""

    def __init__(self, parent):
        """Initialize the PDF export settings dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.config_path = self._get_config_path()
        self.setupUi()
        self.load_settings()

    def _get_config_path(self):
        """Get the path to the PDF export config file.

        Returns:
            str: Path to the config JSON file
        """
        # Store config in user's home directory
        config_dir = os.path.join(os.path.expanduser("~"), ".adiat")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "pdf_export_settings.json")

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
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    settings = json.load(f)
                    self.organization_input.setText(settings.get('organization', ''))
                    self.search_name_input.setText(settings.get('search_name', ''))
        except Exception:
            # If loading fails, just use empty values
            pass

    def save_settings(self):
        """Save current settings to config file."""
        try:
            settings = {
                'organization': self.organization_input.text().strip(),
                'search_name': self.search_name_input.text().strip()
            }
            with open(self.config_path, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception:
            # If saving fails, just continue (settings won't persist)
            pass

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
