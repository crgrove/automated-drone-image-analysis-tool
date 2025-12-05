"""
CalTopoCredentialDialog - Dialog for entering CalTopo API credentials.

Allows users to enter Team ID, Credential ID, and Credential Secret
for CalTopo Team API access.
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QLineEdit, QMessageBox, QCheckBox, QApplication)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QDesktopServices
from core.services.export.CalTopoAPIService import CalTopoAPIService


class CalTopoCredentialDialog(QDialog):
    """
    Dialog for entering CalTopo API credentials.

    Prompts user for Team ID, Credential ID, and Credential Secret.
    """

    def __init__(self, parent=None, existing_credentials=None, ask_to_change=False):
        """
        Initialize the credential dialog.

        Args:
            parent: Parent widget
            existing_credentials: Tuple of (team_id, credential_id, credential_secret) if credentials exist
            ask_to_change: If True, show a checkbox asking if user wants to change credentials
        """
        super().__init__(parent)
        self.setWindowTitle("CalTopo API Credentials")
        self.setModal(True)
        self.resize(500, 300)

        self.existing_credentials = existing_credentials
        self.ask_to_change = ask_to_change
        self.credentials = None

        self.setup_ui()

        # If credentials exist and we're asking to change, pre-fill but disable
        if existing_credentials and ask_to_change:
            team_id, credential_id, credential_secret = existing_credentials
            self.team_id_input.setText(team_id or "")
            self.credential_id_input.setText(credential_id or "")
            self.team_id_input.setEnabled(False)
            self.credential_id_input.setEnabled(False)
            if credential_secret:
                self.credential_secret_input.setText(credential_secret)
                self.credential_secret_input.setEchoMode(QLineEdit.Password)
            self.credential_secret_input.setPlaceholderText("Enter new credential secret...")
        elif existing_credentials:
            # Pre-fill existing credentials
            team_id, credential_id, credential_secret = existing_credentials
            self.team_id_input.setText(team_id or "")
            self.credential_id_input.setText(credential_id or "")
            if credential_secret:
                self.credential_secret_input.setText(credential_secret)
                self.credential_secret_input.setEchoMode(QLineEdit.Password)

    def setup_ui(self):
        """
        Set up the dialog UI.

        Creates and arranges all UI elements including title, instructions,
        input fields for credentials, and action buttons.
        """
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title_label = QLabel("CalTopo Team API Credentials")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Instructions
        instructions = QLabel(
            "Enter your CalTopo Team API credentials.\n"
            "These can be found in the Team Admin page under Service Accounts."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(instructions)

        # Link to documentation
        doc_link_layout = QHBoxLayout()
        doc_link_layout.addStretch()
        doc_link_label = QLabel(
            '<a href="https://training.caltopo.com/all_users/team-accounts/teamapi#keysids">'
            'How to get your API credentials</a>'
        )
        doc_link_label.setOpenExternalLinks(True)
        doc_link_label.setStyleSheet("color: #1E88E5; padding: 5px; text-decoration: underline;")
        doc_link_label.setToolTip("Opens CalTopo API documentation in your browser")
        doc_link_layout.addWidget(doc_link_label)
        layout.addLayout(doc_link_layout)

        # Change credentials checkbox (if asking to change)
        if self.ask_to_change and self.existing_credentials:
            self.change_checkbox = QCheckBox("Change credentials")
            self.change_checkbox.setChecked(False)
            self.change_checkbox.stateChanged.connect(self.on_change_checkbox_changed)
            layout.addWidget(self.change_checkbox)

        # Team ID
        team_id_layout = QVBoxLayout()
        team_id_label = QLabel("Team ID:")
        self.team_id_input = QLineEdit()
        self.team_id_input.setPlaceholderText("6-digit alphanumeric Team ID")
        team_id_layout.addWidget(team_id_label)
        team_id_layout.addWidget(self.team_id_input)
        layout.addLayout(team_id_layout)

        # Credential ID
        credential_id_layout = QVBoxLayout()
        credential_id_label = QLabel("Credential ID:")
        self.credential_id_input = QLineEdit()
        self.credential_id_input.setPlaceholderText("Credential ID")
        credential_id_layout.addWidget(credential_id_label)
        credential_id_layout.addWidget(self.credential_id_input)
        layout.addLayout(credential_id_layout)

        # Credential Secret
        credential_secret_layout = QVBoxLayout()
        credential_secret_label = QLabel("Credential Secret:")
        self.credential_secret_input = QLineEdit()
        self.credential_secret_input.setPlaceholderText("Credential Secret (will be encrypted)")
        self.credential_secret_input.setEchoMode(QLineEdit.Password)
        credential_secret_layout.addWidget(credential_secret_label)
        credential_secret_layout.addWidget(self.credential_secret_input)
        layout.addLayout(credential_secret_layout)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.test_button = QPushButton("Test Credentials")
        self.test_button.clicked.connect(self.on_test_clicked)
        self.test_button.setToolTip("Test the credentials by calling the CalTopo API")

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.on_ok_clicked)
        self.ok_button.setDefault(True)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.test_button)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Initial state for change checkbox
        if self.ask_to_change and self.existing_credentials:
            self.on_change_checkbox_changed()

    def showEvent(self, event):
        """Override showEvent to ensure dialog receives focus on macOS."""
        super().showEvent(event)
        # On macOS, modal dialogs sometimes need explicit focus
        self.activateWindow()
        self.raise_()
        # Set focus to the first input field so users can type immediately
        if hasattr(self, 'team_id_input'):
            self.team_id_input.setFocus()

    def on_change_checkbox_changed(self):
        """
        Handle change credentials checkbox state change.

        Enables or disables credential input fields based on checkbox state,
        and restores original values if unchecked.
        """
        if hasattr(self, 'change_checkbox'):
            checked = self.change_checkbox.isChecked()
            self.team_id_input.setEnabled(checked)
            self.credential_id_input.setEnabled(checked)
            self.credential_secret_input.setEnabled(True)  # Always allow secret entry

            if not checked:
                # Restore original values
                if self.existing_credentials:
                    team_id, credential_id, credential_secret = self.existing_credentials
                    self.team_id_input.setText(team_id or "")
                    self.credential_id_input.setText(credential_id or "")
                    if credential_secret:
                        self.credential_secret_input.setText(credential_secret)
                        self.credential_secret_input.setEchoMode(QLineEdit.Password)
                    else:
                        self.credential_secret_input.clear()
                else:
                    self.credential_secret_input.clear()
                self.credential_secret_input.setPlaceholderText("Enter credential secret...")

    def on_ok_clicked(self):
        """
        Handle OK button click.

        Validates input fields and accepts the dialog with the entered
        credentials, or uses existing credentials if change was not requested.
        """
        # Check if we should use existing credentials
        if self.ask_to_change and hasattr(self, 'change_checkbox') and not self.change_checkbox.isChecked():
            # User chose not to change credentials
            self.credentials = self.existing_credentials
            self.accept()
            return

        # Validate inputs
        team_id = self.team_id_input.text().strip()
        credential_id = self.credential_id_input.text().strip()
        credential_secret = self.credential_secret_input.text().strip()

        if not team_id:
            QMessageBox.warning(self, "Invalid Input", "Please enter a Team ID.")
            return

        if not credential_id:
            QMessageBox.warning(self, "Invalid Input", "Please enter a Credential ID.")
            return

        if not credential_secret:
            QMessageBox.warning(self, "Invalid Input", "Please enter a Credential Secret.")
            return

        self.credentials = (team_id, credential_id, credential_secret)
        self.accept()

    def on_test_clicked(self):
        """
        Handle Test Credentials button click.

        Validates the entered credentials by making a test API call to CalTopo.
        Shows success or error message based on the result.
        """
        # Get current values
        team_id = self.team_id_input.text().strip()
        credential_id = self.credential_id_input.text().strip()
        credential_secret = self.credential_secret_input.text().strip()

        # Validate inputs
        if not team_id:
            QMessageBox.warning(self, "Invalid Input", "Please enter a Team ID.")
            return

        if not credential_id:
            QMessageBox.warning(self, "Invalid Input", "Please enter a Credential ID.")
            return

        if not credential_secret:
            QMessageBox.warning(self, "Invalid Input", "Please enter a Credential Secret.")
            return

        # Disable test button during test
        self.test_button.setEnabled(False)
        self.test_button.setText("Testing...")
        QApplication.processEvents()

        try:
            # Create API service
            api_service = CalTopoAPIService()

            # Test credentials by calling get_account_data
            success, account_data = api_service.get_account_data(
                team_id, credential_id, credential_secret
            )

            if success and account_data:
                QMessageBox.information(
                    self,
                    "Credentials Valid",
                    "The credentials are valid and successfully authenticated with CalTopo API."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Credentials Invalid",
                    "The credentials failed to authenticate with CalTopo API.\n\n"
                    "Please check:\n"
                    "• Team ID is correct\n"
                    "• Credential ID is correct\n"
                    "• Credential Secret is correct (copy it exactly as shown)\n"
                    "• Your service account has the required permissions"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Test Error",
                f"An error occurred while testing credentials:\n\n{str(e)}"
            )
        finally:
            # Re-enable test button
            self.test_button.setEnabled(True)
            self.test_button.setText("Test Credentials")
            QApplication.processEvents()

    def get_credentials(self):
        """Get the entered credentials.

        Returns:
            tuple: (team_id, credential_id, credential_secret) or None if cancelled
        """
        return self.credentials
