"""Connection details page for the streaming setup wizard."""

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QVBoxLayout

try:
    import cv2
except ImportError:
    cv2 = None

from .BasePage import BasePage
from core.views.components.LabeledSlider import TextLabeledSlider


class StreamConnectionPage(BasePage):
    """Page for providing stream URL/path and auto-connect preference."""

    def setup_ui(self) -> None:
        # Initialize HDMI device combo with placeholder
        if hasattr(self.dialog, "deviceComboBox"):
            self.dialog.deviceComboBox.clear()
            self.dialog.deviceComboBox.addItem(
                self.tr("Click Scan to find devices..."),
                None
            )
            self.dialog.deviceComboBox.setEnabled(False)
            self.dialog.labelHdmiDevices.setVisible(False)
            self.dialog.deviceComboBox.setVisible(False)
            self.dialog.scanDevicesButton.setVisible(False)

        # Create resolution slider with user-friendly labels
        # Map: 25% = 480p, 50% = 720p, 75% = 1080p, 100% = 4K
        if hasattr(self.dialog, "resolutionSliderWidget"):
            layout = QVBoxLayout(self.dialog.resolutionSliderWidget)
            layout.setContentsMargins(0, 0, 0, 0)

            # Presets: (label, percentage_value)
            resolution_presets = [
                (self.tr("480p"), 25),
                (self.tr("720p"), 50),
                (self.tr("1080p"), 75),
                (self.tr("4K"), 100)
            ]

            self.resolution_slider = TextLabeledSlider(
                parent=self.dialog.resolutionSliderWidget,
                presets=resolution_presets
            )
            # Set default to 1080p (index 2)
            self.resolution_slider.setValue(2)
            layout.addWidget(self.resolution_slider)

    def connect_signals(self) -> None:
        self.dialog.streamUrlLineEdit.textChanged.connect(self._on_stream_url_changed)
        self.dialog.browseButton.clicked.connect(self._on_browse_clicked)
        self.dialog.autoConnectCheckBox.stateChanged.connect(self._on_auto_connect_changed)
        if hasattr(self.dialog, "scanDevicesButton"):
            self.dialog.scanDevicesButton.clicked.connect(self._on_scan_devices_clicked)
        if hasattr(self.dialog, "deviceComboBox"):
            self.dialog.deviceComboBox.currentIndexChanged.connect(self._on_device_selected)
        if hasattr(self, "resolution_slider"):
            self.resolution_slider.valueChanged.connect(self._on_resolution_changed)

    def load_data(self) -> None:
        # Don't load previous file selection - start fresh each time
        stream_url = self.wizard_data.get("stream_url", "")
        auto_connect_raw = self.wizard_data.get("auto_connect", False)

        if stream_url:
            self.dialog.streamUrlLineEdit.setText(stream_url)
        self.dialog.autoConnectCheckBox.setChecked(bool(auto_connect_raw))

        self._apply_stream_type_settings()

        # Load resolution preference
        default_resolution_str = self.settings_service.get_setting("StreamingProcessingResolution", "75%")
        # Convert "75%" to 75
        try:
            default_resolution = int(default_resolution_str.rstrip('%'))
        except (ValueError, AttributeError):
            default_resolution = 75

        # Get current resolution from wizard_data (as integer) or use default
        current_resolution = self.wizard_data.get("processing_resolution")
        if current_resolution is None:
            current_resolution = default_resolution
        elif isinstance(current_resolution, str):
            # Handle string like "75%"
            try:
                current_resolution = int(current_resolution.rstrip('%'))
            except (ValueError, AttributeError):
                current_resolution = default_resolution

        # Map percentage to slider index
        # 25% = index 0 (480p), 50% = index 1 (720p), 75% = index 2 (1080p), 100% = index 3 (4K)
        resolution_to_index = {25: 0, 50: 1, 75: 2, 100: 3}
        slider_index = resolution_to_index.get(current_resolution, 2)  # Default to 1080p

        if hasattr(self, "resolution_slider"):
            self.resolution_slider.setValue(slider_index)

        # Initialize wizard data
        self.wizard_data["stream_url"] = self.dialog.streamUrlLineEdit.text().strip()
        self.wizard_data["auto_connect"] = self.dialog.autoConnectCheckBox.isChecked()
        self.wizard_data["processing_resolution"] = current_resolution

    def on_enter(self) -> None:
        self._apply_stream_type_settings()

    def validate(self) -> bool:
        return bool(self.dialog.streamUrlLineEdit.text().strip())

    def save_data(self) -> None:
        self.wizard_data["stream_url"] = self.dialog.streamUrlLineEdit.text().strip()
        self.wizard_data["auto_connect"] = self.dialog.autoConnectCheckBox.isChecked()
        if hasattr(self, "resolution_slider"):
            # Get the numeric value (percentage) from the selected preset
            numeric_value = self.resolution_slider.getNumericValue()
            if numeric_value is not None:
                self.wizard_data["processing_resolution"] = numeric_value
            else:
                # Fallback: map index to percentage
                index = self.resolution_slider.value()
                index_to_resolution = {0: 25, 1: 50, 2: 75, 3: 100}
                self.wizard_data["processing_resolution"] = index_to_resolution.get(index, 75)

    def _apply_stream_type_settings(self) -> None:
        stream_type = self.wizard_data.get("stream_type", "File")
        settings = self._get_stream_type_settings(stream_type)
        self.dialog.labelConnectionInstructions.setText(settings["instructions"])
        self.dialog.labelStreamUrl.setText(settings["field_label"])
        self.dialog.streamUrlLineEdit.setPlaceholderText(settings["placeholder"])
        self.dialog.browseButton.setVisible(settings["show_browse"])

        # HDMI-specific UI
        is_hdmi = stream_type == "HDMI Capture"
        if hasattr(self.dialog, "labelHdmiDevices"):
            self.dialog.labelHdmiDevices.setVisible(is_hdmi)
        if hasattr(self.dialog, "deviceComboBox"):
            self.dialog.deviceComboBox.setVisible(is_hdmi)
            self.dialog.deviceComboBox.setEnabled(is_hdmi)
        if hasattr(self.dialog, "scanDevicesButton"):
            self.dialog.scanDevicesButton.setVisible(is_hdmi)

        # Auto-populate sensible defaults when switching types
        current_value = self.dialog.streamUrlLineEdit.text().strip()
        if not current_value and settings.get("default_value"):
            self.dialog.streamUrlLineEdit.setText(settings["default_value"])

    def _get_stream_type_settings(self, stream_type: str) -> dict:
        mapping = {
            "File": {
                "instructions": self.tr(
                    "Choose the video file you want to analyze. Use Browse to pick a file from disk."
                ),
                "field_label": self.tr("Video File:"),
                "placeholder": self.tr("Click Browse to select a video file..."),
                "show_browse": True,
                "default_value": "",
            },
            "HDMI Capture": {
                "instructions": self.tr(
                    "Enter the capture device index (0, 1, 2, ...) for your HDMI input."
                ),
                "field_label": self.tr("Device Index:"),
                "placeholder": self.tr("0"),
                "show_browse": False,
                "default_value": "0",
            },
            "RTMP Stream": {
                "instructions": self.tr(
                    "Enter the RTMP URL provided by your streaming server (rtmp://server:port/app/key)."
                ),
                "field_label": self.tr("Stream URL:"),
                "placeholder": self.tr("rtmp://server:port/app/streamKey"),
                "show_browse": False,
                "default_value": "",
            },
        }
        return mapping.get(stream_type, mapping["File"])

    def _on_scan_devices_clicked(self) -> None:
        """Scan for available HDMI capture devices using OpenCV."""
        if cv2 is None:
            # If OpenCV is not available, we cannot scan
            self.dialog.deviceComboBox.clear()
            self.dialog.deviceComboBox.addItem(
                self.tr("OpenCV not available; enter index manually."),
                None
            )
            self.dialog.deviceComboBox.setEnabled(False)
            return

        self.dialog.deviceComboBox.clear()
        found_any = False
        max_devices = 10
        for index in range(max_devices):
            cap = cv2.VideoCapture(index)
            if cap is not None and cap.isOpened():
                found_any = True
                label = self.tr("Device {index}").format(index=index)
                self.dialog.deviceComboBox.addItem(label, index)
                cap.release()
            else:
                if cap is not None:
                    cap.release()

        if not found_any:
            self.dialog.deviceComboBox.addItem(
                self.tr("No capture devices found."),
                None
            )
            self.dialog.deviceComboBox.setEnabled(False)
        else:
            self.dialog.deviceComboBox.setEnabled(True)
            # Select first device and update URL field
            self.dialog.deviceComboBox.setCurrentIndex(0)
            self._sync_device_to_url()

    def _on_device_selected(self, index: int) -> None:
        """Update URL field when a device is selected from the combo box."""
        if index < 0:
            return
        self._sync_device_to_url()

    def _sync_device_to_url(self) -> None:
        """Sync selected device index into the URL field and wizard data."""
        if not hasattr(self.dialog, "deviceComboBox"):
            return
        data = self.dialog.deviceComboBox.currentData()
        if data is None:
            return
        self.dialog.streamUrlLineEdit.setText(str(data))
        self.wizard_data["stream_url"] = str(data)

    def _on_stream_url_changed(self, text: str) -> None:
        cleaned = text.strip()
        if os.name == "nt":
            cleaned = cleaned.replace("/", "\\")
        self.wizard_data["stream_url"] = cleaned
        if hasattr(self, "on_validation_changed"):
            self.on_validation_changed()

    def _on_auto_connect_changed(self, state: int) -> None:
        self.wizard_data["auto_connect"] = state == Qt.Checked

    def _on_browse_clicked(self) -> None:
        current = self.dialog.streamUrlLineEdit.text().strip() or os.getcwd()
        file_path, _ = QFileDialog.getOpenFileName(
            self.dialog,
            self.tr("Select Video File"),
            current,
            self.tr(
                "Video Files (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm);;All Files (*)"
            ),
        )
        if file_path:
            self.dialog.streamUrlLineEdit.setText(file_path)

    def _on_resolution_changed(self, index: int) -> None:
        """Handle resolution slider change."""
        # Map slider index to percentage value
        index_to_resolution = {0: 25, 1: 50, 2: 75, 3: 100}
        resolution_value = index_to_resolution.get(index, 75)
        self.wizard_data["processing_resolution"] = resolution_value
