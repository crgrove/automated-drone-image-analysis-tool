"""PDFExportDialog - Pure UI dialog for collecting PDF export settings."""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QCheckBox
from PySide6.QtCore import Qt
from helpers.TranslationMixin import TranslationMixin

from core.services.export.PDFSettingsService import PDFSettingsService


class PDFExportDialog(TranslationMixin, QDialog):
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
        self._apply_translations()

    def setupUi(self):
        """Set up the dialog UI."""
        self.setWindowTitle(self.tr("PDF Export Settings"))
        self.setModal(True)
        self.setMinimumWidth(400)

        # Main layout
        layout = QVBoxLayout()

        # Instructions
        instructions = QLabel(self.tr("Enter the following information for the PDF report:"))
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Form layout for inputs
        form_layout = QFormLayout()

        # Organization name input
        self.organization_input = QLineEdit()
        self.organization_input.setPlaceholderText(self.tr("Enter organization name"))
        form_layout.addRow(self.tr("Organization:"), self.organization_input)

        # Search name input
        self.search_name_input = QLineEdit()
        self.search_name_input.setPlaceholderText(self.tr("Enter search name"))
        form_layout.addRow(self.tr("Search Name:"), self.search_name_input)

        layout.addLayout(form_layout)

        # Options section
        options_label = QLabel(self.tr("Export Options:"))
        options_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(options_label)

        # Include images without flagged AOIs checkbox
        self.include_images_without_flagged_aois = QCheckBox(self.tr("Include images without flagged AOIs"))
        self.include_images_without_flagged_aois.setToolTip(self.tr(
            "When checked, all images will be included in the PDF report, even if they don't have any flagged AOIs. "
            "When unchecked, only images with flagged AOIs will be included."
        ))
        layout.addWidget(self.include_images_without_flagged_aois)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton(self.tr("OK"))
        self.ok_button.clicked.connect(self.on_ok_clicked)
        self.cancel_button = QPushButton(self.tr("Cancel"))
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Set focus to organization input
        self.organization_input.setFocus()

    def showEvent(self, event):
        """Override showEvent to ensure dialog receives focus on macOS."""
        super().showEvent(event)
        # On macOS, modal dialogs sometimes need explicit focus
        self.activateWindow()
        self.raise_()
        # Set focus to the first input field so users can type immediately
        if hasattr(self, 'organization_input'):
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
        self.include_images_without_flagged_aois.setChecked(settings.get('include_images_without_flagged_aois', False))

    def save_settings(self):
        """Save current settings to config file."""
        self.settings_service.save_settings(
            self.organization_input.text(),
            self.search_name_input.text(),
            self.include_images_without_flagged_aois.isChecked()
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

    def get_include_images_without_flagged_aois(self):
        """Get whether to include images without flagged AOIs.

        Returns:
            bool: True if images without flagged AOIs should be included
        """
        return self.include_images_without_flagged_aois.isChecked()
