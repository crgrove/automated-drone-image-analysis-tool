"""
Review or New Analysis page for the Image Analysis Guide wizard.

This is the first page that asks users if they want to review existing
analysis results or start a new analysis.
"""

import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QWidget, QFrame, QMessageBox, QApplication
)
from PySide6.QtGui import QFont

from .BasePage import BasePage


class ReviewOrNewPage(BasePage):
    """First page for choosing between reviewing existing results or starting new analysis."""

    def setup_ui(self):
        """Initialize UI components."""
        # The page is now defined in the .ui file, so we access it via the dialog
        # The UI file creates these as attributes of the dialog
        self.pageWidget = self.dialog.pageReviewOrNew

        # Access UI widgets directly from the dialog (they're created by setupUi)
        self.reviewButton = self.dialog.reviewButton
        self.newAnalysisButton = self.dialog.newAnalysisButton
        self.buttonContainer = self.dialog.buttonContainer
        self.labelInstructions = self.dialog.labelInstructions
        self.fileSelectorWidget = self.dialog.fileSelectorWidget
        self.filePathLabel = self.dialog.filePathLabel
        self.browseFileButton = self.dialog.browseFileButton

        # Ensure file selector is initially hidden
        self.fileSelectorWidget.setVisible(False)

    def connect_signals(self):
        """Connect UI signals to handlers."""
        self.reviewButton.clicked.connect(self._on_review_clicked)
        self.newAnalysisButton.clicked.connect(self._on_new_analysis_clicked)
        self.browseFileButton.clicked.connect(self._on_browse_file)

    def load_data(self):
        """Load data from wizard_data or preferences into UI."""
        # No data to load for this page
        pass

    def validate(self) -> bool:
        """Validate that the page is ready to proceed."""
        # If review is selected, file must be selected
        if self.wizard_data.get('review_mode') == 'review':
            return bool(self.wizard_data.get('review_file_path'))
        # If new analysis is selected, always valid
        return self.wizard_data.get('review_mode') == 'new'

    def save_data(self):
        """Save data from UI into wizard_data."""
        # Data is saved in the click handlers
        pass

    def on_enter(self):
        """Called when the page is entered."""
        # Reset state when entering this page
        self.wizard_data['review_mode'] = None
        self.wizard_data['review_file_path'] = None
        self.fileSelectorWidget.setVisible(False)
        self.filePathLabel.setText("No file selected")
        self.reviewButton.setEnabled(True)
        self.newAnalysisButton.setEnabled(True)
        # Show buttons and instructions again when re-entering the page
        self.buttonContainer.setVisible(True)
        self.labelInstructions.setVisible(True)

    def _on_review_clicked(self):
        """Handle review button click - show file selector."""
        self.wizard_data['review_mode'] = 'review'
        # Hide the button container and instructions, show file selector
        self.buttonContainer.setVisible(False)
        self.labelInstructions.setVisible(False)
        self.fileSelectorWidget.setVisible(True)
        # Update navigation buttons
        if hasattr(self, 'on_validation_changed'):
            self.on_validation_changed()

    def _on_new_analysis_clicked(self):
        """Handle new analysis button click - proceed to next page."""
        self.wizard_data['review_mode'] = 'new'
        # Hide the button container
        self.buttonContainer.setVisible(False)
        self.fileSelectorWidget.setVisible(False)
        # Update navigation buttons - this will enable continue
        if hasattr(self, 'on_validation_changed'):
            self.on_validation_changed()
        # Automatically proceed to the next page
        # Save data first, then trigger continue
        self.save_data()
        if self.validate():
            # Process events to ensure UI updates (visibility changes, button states) are applied
            QApplication.processEvents()
            self.dialog._on_continue()

    def _on_browse_file(self):
        """Handle browse file button click - open file dialog."""
        # Get last used directory or default to user's home
        last_dir = self.settings_service.get_setting('OutputFolder', '')
        if not last_dir:
            last_dir = os.path.expanduser('~')

        file_path, _ = QFileDialog.getOpenFileName(
            self.dialog,
            "Select ADIAT Results File",
            last_dir,
            "XML Files (*.xml);;All Files (*)"
        )

        if file_path:
            # Validate that it's an ADIAT results file
            if not os.path.basename(file_path).startswith('ADIAT_Data'):
                # Show warning but allow selection
                reply = QMessageBox.warning(
                    self.dialog,
                    "File Name Warning",
                    "The selected file does not appear to be an ADIAT_Data.xml file.\n\n"
                    "Do you want to continue with this file?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return

            # Save file path
            if os.name == 'nt':
                file_path = file_path.replace('/', '\\')

            self.wizard_data['review_file_path'] = file_path
            self.filePathLabel.setText(file_path)

            # Update navigation buttons
            if hasattr(self, 'on_validation_changed'):
                self.on_validation_changed()

            # Give focus to the "Load Results" button (continue button)
            # This will be enabled now that a file is selected
            self.dialog.continueButton.setFocus()

            # If file is selected and review mode is active, we can proceed
            # The continue button should now be enabled
