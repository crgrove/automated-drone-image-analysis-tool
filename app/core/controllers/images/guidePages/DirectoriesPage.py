"""
Directories page for the Image Analysis Guide wizard.
"""

import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog

from .BasePage import BasePage


class DirectoriesPage(BasePage):
    """Page for selecting input and output directories."""

    def setup_ui(self):
        """Initialize UI components."""
        # Ensure browse buttons use default styling (no focus)
        self.dialog.inputDirectoryButton.setFocusPolicy(Qt.NoFocus)
        self.dialog.outputDirectoryButton.setFocusPolicy(Qt.NoFocus)

    def on_enter(self):
        """Called when the page is entered - clear focus from all buttons."""
        # Clear focus from the dialog to ensure no buttons have focus
        if self.dialog.focusWidget():
            self.dialog.focusWidget().clearFocus()

    def connect_signals(self):
        """Connect UI signals to handlers."""
        self.dialog.inputDirectoryButton.clicked.connect(self._on_input_directory_browse)
        self.dialog.outputDirectoryButton.clicked.connect(self._on_output_directory_browse)
        self.dialog.inputDirectoryLineEdit.textChanged.connect(self._on_input_directory_changed)
        self.dialog.outputDirectoryLineEdit.textChanged.connect(self._on_output_directory_changed)

    def load_data(self):
        """Load directory preferences if available."""
        # Directories are loaded from wizard_data defaults
        pass

    def validate(self) -> bool:
        """Validate that both directories are set."""
        input_dir = self.dialog.inputDirectoryLineEdit.text().strip()
        output_dir = self.dialog.outputDirectoryLineEdit.text().strip()
        return bool(input_dir and output_dir)

    def save_data(self):
        """Save directory paths to wizard_data."""
        self.wizard_data['input_directory'] = self.dialog.inputDirectoryLineEdit.text().strip()
        self.wizard_data['output_directory'] = self.dialog.outputDirectoryLineEdit.text().strip()

    def _on_input_directory_browse(self):
        """Handle input directory browse button click."""
        current_dir = self.dialog.inputDirectoryLineEdit.text() or self.settings_service.get_setting('InputFolder', '')
        directory = QFileDialog.getExistingDirectory(
            self.dialog,
            "Select Input Directory",
            current_dir,
            QFileDialog.ShowDirsOnly
        )
        if directory:
            if os.name == 'nt':
                directory = directory.replace('/', '\\')
            self.dialog.inputDirectoryLineEdit.setText(directory)
            # Note: Setting the text will trigger textChanged signal,
            # which calls _on_input_directory_changed(), which triggers the callback.
            # No need to call the callback directly here.

    def _on_output_directory_browse(self):
        """Handle output directory browse button click."""
        current_dir = self.dialog.outputDirectoryLineEdit.text() or self.settings_service.get_setting('OutputFolder', '')
        directory = QFileDialog.getExistingDirectory(
            self.dialog,
            "Select Output Directory",
            current_dir,
            QFileDialog.ShowDirsOnly
        )
        if directory:
            if os.name == 'nt':
                directory = directory.replace('/', '\\')
            self.dialog.outputDirectoryLineEdit.setText(directory)
            # Note: Setting the text will trigger textChanged signal,
            # which calls _on_output_directory_changed(), which updates wizard_data
            # and triggers the validation callback.

    def _on_output_directory_changed(self, text):
        """Handle output directory text change."""
        self.wizard_data['output_directory'] = text
        # Notify main dialog to update navigation buttons
        if hasattr(self, 'on_validation_changed'):
            self.on_validation_changed()

    def _on_input_directory_changed(self, text):
        """Handle input directory text change."""
        self.wizard_data['input_directory'] = text
        # Trigger scan if callback is available
        if text and hasattr(self, 'on_input_directory_changed'):
            self.on_input_directory_changed()
        # Notify main dialog to update navigation buttons
        if hasattr(self, 'on_validation_changed'):
            self.on_validation_changed()
