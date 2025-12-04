"""Stream source selection page for the streaming setup wizard."""

from PySide6.QtWidgets import QButtonGroup

from .BasePage import BasePage
from helpers.IconHelper import IconHelper


class StreamSourcePage(BasePage):
    """Page for selecting video source type."""

    def setup_ui(self) -> None:
        # Apply icons if available (non-critical)
        try:
            self.dialog.fileButton.setIcon(IconHelper.create_icon("fa6s.folder-open", "Dark"))
            self.dialog.hdmiButton.setIcon(IconHelper.create_icon("fa6s.video", "Dark"))
            self.dialog.rtmpButton.setIcon(IconHelper.create_icon("fa6s.wifi", "Dark"))
        except Exception:
            pass

        # Make buttons mutually exclusive
        self.button_group = QButtonGroup(self.dialog)
        self.button_group.setExclusive(True)
        for btn in (self.dialog.fileButton, self.dialog.hdmiButton, self.dialog.rtmpButton):
            btn.setCheckable(True)
            self.button_group.addButton(btn)
        self.dialog.fileButton.setChecked(True)

    def connect_signals(self) -> None:
        self.dialog.fileButton.clicked.connect(lambda: self._on_stream_type_changed("File"))
        self.dialog.hdmiButton.clicked.connect(lambda: self._on_stream_type_changed("HDMI Capture"))
        self.dialog.rtmpButton.clicked.connect(lambda: self._on_stream_type_changed("RTMP Stream"))

    def load_data(self) -> None:
        stream_type = self.wizard_data.get("stream_type") or self.settings_service.get_setting(
            "StreamingSourceType", "File"
        )

        self._set_stream_type(stream_type)

        # Initialize wizard data
        self.wizard_data["stream_type"] = self._current_stream_type()

    def validate(self) -> bool:
        return True

    def save_data(self) -> None:
        self.wizard_data["stream_type"] = self._current_stream_type()

    def _on_stream_type_changed(self, stream_type: str) -> None:
        self.wizard_data["stream_type"] = stream_type
        if hasattr(self, "on_validation_changed"):
            self.on_validation_changed()

    def _current_stream_type(self) -> str:
        if self.dialog.hdmiButton.isChecked():
            return "HDMI Capture"
        if self.dialog.rtmpButton.isChecked():
            return "RTMP Stream"
        return "File"

    def _set_stream_type(self, stream_type: str) -> None:
        if stream_type == "HDMI Capture":
            self.dialog.hdmiButton.setChecked(True)
        elif stream_type == "RTMP Stream":
            self.dialog.rtmpButton.setChecked(True)
        else:
            self.dialog.fileButton.setChecked(True)
