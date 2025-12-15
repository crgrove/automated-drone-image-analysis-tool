"""General settings page for streaming setup wizard."""

import os
from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import Qt

from .BasePage import BasePage


class StreamGeneralPage(BasePage):
    """Recording folder and preference toggles page."""

    def setup_ui(self) -> None:
        pass

    def connect_signals(self) -> None:
        self.dialog.recordingDirBrowseButton.clicked.connect(self._on_browse_clicked)
        self.dialog.recordingDirLineEdit.textChanged.connect(self._on_recording_dir_changed)
        self.dialog.autoRecordCheckBox.stateChanged.connect(self._on_auto_record_changed)
        self.dialog.skipGuideCheckBox.stateChanged.connect(self._on_skip_changed)

    def load_data(self) -> None:
        default_dir = self.settings_service.get_setting("StreamingRecordingDir", "./recordings")
        directory = self.wizard_data.get("recording_dir") or default_dir
        self.dialog.recordingDirLineEdit.setText(directory)

        auto_record_raw = self.wizard_data.get("auto_record")
        if auto_record_raw is None:
            auto_record_setting = self.settings_service.get_setting("StreamingAutoRecord", "No")
            auto_record_raw = str(auto_record_setting).strip().lower() in ("yes", "true", "1")
        self.dialog.autoRecordCheckBox.setChecked(bool(auto_record_raw))

        skip_raw = self.settings_service.get_setting("SkipStreamingGuide", "No")
        skip_val = self.wizard_data.get("skip_guide")
        if skip_val is None:
            skip_val = str(skip_raw).strip().lower() == "yes"
        self.dialog.skipGuideCheckBox.setChecked(skip_val)

        self.wizard_data["recording_dir"] = self.dialog.recordingDirLineEdit.text().strip()
        self.wizard_data["auto_record"] = self.dialog.autoRecordCheckBox.isChecked()
        self.wizard_data["skip_guide"] = self.dialog.skipGuideCheckBox.isChecked()

    def validate(self) -> bool:
        return bool(self.dialog.recordingDirLineEdit.text().strip())

    def save_data(self) -> None:
        self.wizard_data["recording_dir"] = self.dialog.recordingDirLineEdit.text().strip()
        self.wizard_data["auto_record"] = self.dialog.autoRecordCheckBox.isChecked()
        self.wizard_data["skip_guide"] = self.dialog.skipGuideCheckBox.isChecked()

    def _on_browse_clicked(self) -> None:
        current_dir = self.dialog.recordingDirLineEdit.text().strip() or os.getcwd()
        directory = QFileDialog.getExistingDirectory(self.dialog, "Select Recording Folder", current_dir)
        if directory:
            self.dialog.recordingDirLineEdit.setText(directory)

    def _on_recording_dir_changed(self, directory: str) -> None:
        cleaned = directory.strip() or "./recordings"
        self.wizard_data["recording_dir"] = cleaned
        if hasattr(self, "on_validation_changed"):
            self.on_validation_changed()

    def _on_auto_record_changed(self, state: int) -> None:
        self.wizard_data["auto_record"] = state == Qt.Checked

    def _on_skip_changed(self, state: int) -> None:
        self.wizard_data["skip_guide"] = state == Qt.Checked
