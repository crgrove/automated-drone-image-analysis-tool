"""
CalTopoMethodDialog - Dialog for selecting CalTopo export method.

Allows users to choose between browser-based authentication or API-based
authentication for CalTopo exports.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QGroupBox
)
from PySide6.QtCore import Qt
from helpers.TranslationMixin import TranslationMixin
from PySide6.QtGui import QFont


class CalTopoMethodDialog(TranslationMixin, QDialog):
    """
    Dialog for selecting CalTopo export method.

    Provides options to choose between:
    - Browser-based authentication (traditional login)
    - API-based authentication (recommended for Teams accounts)
    """

    def __init__(self, parent=None):
        """
        Initialize the CalTopo method selection dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle(self.tr("CalTopo Export Method"))
        self.setMinimumWidth(450)
        self.setModal(True)

        self._setup_ui()
        self._apply_translations()

    def _setup_ui(self):
        """
        Set up the dialog UI.

        Creates and configures all UI elements including title, description,
        radio buttons for method selection, and action buttons.
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title
        title_label = QLabel(self.tr("Select CalTopo Export Method"))
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Description
        description_label = QLabel(self.tr(
            "Choose how you want to authenticate with CalTopo:"
        ))
        description_label.setWordWrap(True)
        description_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(description_label)

        # Method selection
        method_group = QGroupBox(self.tr("Export Method"))
        method_layout = QVBoxLayout()
        method_layout.setSpacing(10)

        self.api_radio = QRadioButton(self.tr("API (Recommended for CalTopo Team Account)"))
        self.api_radio.setChecked(True)  # Default to API
        self.api_radio.setToolTip(self.tr(
            "Use CalTopo Team API with service account credentials.\n"
            "Best for Teams accounts with service accounts configured."
        ))

        self.browser_radio = QRadioButton(self.tr("Browser Login"))
        self.browser_radio.setToolTip(self.tr(
            "Use browser-based authentication.\n"
            "Log in through an embedded browser window."
        ))

        self.method_group = QButtonGroup(self)
        self.method_group.addButton(self.api_radio, 0)
        self.method_group.addButton(self.browser_radio, 1)

        method_layout.addWidget(self.api_radio)
        method_layout.addWidget(self.browser_radio)
        method_group.setLayout(method_layout)
        layout.addWidget(method_group)

        # Info text
        info_label = QLabel(self.tr(
            "API method requires Team ID and Credential Secret from your\n"
            "CalTopo Team Admin page. Browser method uses your regular login."
        ))
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #888; font-size: 10px; padding: 5px;")
        layout.addWidget(info_label)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.continue_button = QPushButton(self.tr("Continue"))
        self.continue_button.setDefault(True)
        self.continue_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton(self.tr("Cancel"))
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.continue_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def get_selected_method(self):
        """
        Get the selected export method.

        Returns:
            str: 'api' or 'browser'
        """
        return 'api' if self.api_radio.isChecked() else 'browser'
