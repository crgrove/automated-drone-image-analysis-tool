"""Wizard dialog for configuring streaming detection before launch."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog

from core.views.streaming.StreamingGuide_ui import Ui_StreamingGuide
from core.services.SettingsService import SettingsService
from .guidePages import (
    StreamSourcePage,
    StreamConnectionPage,
    StreamImageCapturePage,
    StreamTargetSizePage,
    StreamAlgorithmPage,
    StreamAlgorithmParametersPage
)


class StreamingGuide(QDialog, Ui_StreamingGuide):
    """Multi-step wizard for streaming setup."""

    wizardCompleted = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.settings_service = SettingsService()
        self.current_page = 0
        self.total_pages = 6

        skip_setting = self.settings_service.get_setting("SkipStreamingGuide", "No")
        skip_guide = False
        if isinstance(skip_setting, str):
            skip_guide = skip_setting.strip().lower() in {"yes", "true", "1"}
        elif isinstance(skip_setting, bool):
            skip_guide = skip_setting
        else:
            skip_guide = bool(skip_setting)

        # Initialize wizard_data - algorithm starts as None and will be set by user selection
        # This ensures it resets between wizard sessions but persists when going back/forward
        self.wizard_data = {
            "stream_type": "File",
            "stream_url": "",
            "auto_connect": False,
            "algorithm": None,
            "processing_resolution": 75,  # Changed to integer for slider (25, 50, 75, 100)
            "skip_guide": skip_guide,
            "object_size_min": 1,
            "object_size_max": 6,
            "altitude": 100,  # Default altitude in feet
            "altitude_unit": "ft",  # Default unit
            "drone": None,
            "drone_sensors": [],
            "gsd_list": [],
        }

        self.pages = [
            StreamSourcePage(self.wizard_data, self.settings_service, self),
            StreamConnectionPage(self.wizard_data, self.settings_service, self),
            StreamImageCapturePage(self.wizard_data, self.settings_service, self),
            StreamTargetSizePage(self.wizard_data, self.settings_service, self),
            StreamAlgorithmPage(self.wizard_data, self.settings_service, self),
            StreamAlgorithmParametersPage(self.wizard_data, self.settings_service, self),
        ]

        if hasattr(self, "skipGuideCheckBox"):
            self.skipGuideCheckBox.setChecked(skip_guide)

        # Allow pages to trigger validation updates
        self.pages[0].on_validation_changed = self._update_navigation_buttons
        self.pages[1].on_validation_changed = self._update_navigation_buttons
        self.pages[2].on_validation_changed = self._update_navigation_buttons
        self.pages[3].on_validation_changed = self._update_navigation_buttons
        self.pages[4].on_validation_changed = self._update_navigation_buttons
        self.pages[5].on_validation_changed = self._update_navigation_buttons

        for page in self.pages:
            page.setup_ui()
            page.connect_signals()
            page.load_data()

        self.setWindowTitle("ADIAT Streaming Setup Guide")

        self.continueButton.clicked.connect(self._on_continue)
        self.backButton.clicked.connect(self._on_back)
        self.cancelButton.clicked.connect(self.reject)

        # Connect skip guide checkbox (in button area, shared across pages)
        if hasattr(self, "skipGuideCheckBox"):
            from PySide6.QtCore import Qt
            self.skipGuideCheckBox.stateChanged.connect(self._on_skip_guide_changed)

        # Call on_enter for the initial page
        if self.current_page < len(self.pages):
            self.pages[self.current_page].on_enter()

        self._update_navigation_buttons()

    def _on_skip_guide_changed(self, state: int) -> None:
        """Handle skip guide checkbox change in button area."""
        from PySide6.QtCore import Qt
        self.wizard_data["skip_guide"] = state == Qt.Checked

    def _on_continue(self) -> None:
        if self.current_page < len(self.pages):
            self.pages[self.current_page].save_data()
            if not self.pages[self.current_page].validate():
                return

        if self.current_page < self.total_pages - 1:
            if self.current_page < len(self.pages):
                self.pages[self.current_page].on_exit()
            self.current_page += 1
            self.stackedWidget.setCurrentIndex(self.current_page)
            if self.current_page < len(self.pages):
                self.pages[self.current_page].on_enter()
            self._update_navigation_buttons()
        else:
            self._complete_wizard()

    def _on_back(self) -> None:
        if self.current_page > 0:
            if self.current_page < len(self.pages):
                self.pages[self.current_page].on_exit()
                self.pages[self.current_page].save_data()

            self.current_page -= 1
            self.stackedWidget.setCurrentIndex(self.current_page)
            if self.current_page < len(self.pages):
                self.pages[self.current_page].on_enter()
            self._update_navigation_buttons()

    def _update_navigation_buttons(self) -> None:
        self.backButton.setEnabled(self.current_page > 0)
        if self.current_page == self.total_pages - 1:
            self.continueButton.setText("Open Stream Viewer")
        else:
            self.continueButton.setText("Continue")

        valid = True
        if self.current_page < len(self.pages):
            valid = self.pages[self.current_page].validate()
        self.continueButton.setEnabled(valid)

    def _complete_wizard(self) -> None:
        for page in self.pages:
            page.save_data()

        # Persist preferences
        self.settings_service.set_setting("StreamingSourceType", self.wizard_data["stream_type"])
        self.settings_service.set_setting("StreamingSourceUrl", self.wizard_data["stream_url"])
        self.settings_service.set_setting("StreamingAutoConnect", "Yes" if self.wizard_data["auto_connect"] else "No")
        if self.wizard_data.get("algorithm"):
            self.settings_service.set_setting("StreamingAlgorithm", self.wizard_data["algorithm"])
        if self.wizard_data.get("processing_resolution"):
            # Convert integer to percentage string for storage
            resolution_pct = f"{self.wizard_data['processing_resolution']}%"
            self.settings_service.set_setting("StreamingProcessingResolution", resolution_pct)

        # Save skip guide preference (from last page or button area)
        skip_value = "Yes" if self.wizard_data.get("skip_guide", False) else "No"
        self.settings_service.set_setting("SkipStreamingGuide", skip_value)

        self.wizardCompleted.emit(self.wizard_data)
        self.accept()

    def reject(self) -> None:
        try:
            # Save skip guide preference from checkbox if it exists
            if hasattr(self, "skipGuideCheckBox"):
                skip_val = self.skipGuideCheckBox.isChecked()
            else:
                skip_val = self.wizard_data.get("skip_guide", False)
            skip_value = "Yes" if skip_val else "No"
            self.settings_service.set_setting("SkipStreamingGuide", skip_value)
        finally:
            super().reject()
