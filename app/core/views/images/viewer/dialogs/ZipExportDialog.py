"""ZipExportDialog - Dialog to choose between Native or Augmented export."""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton, QButtonGroup
from PySide6.QtCore import Qt


class ZipExportDialog(QDialog):
    """Dialog for choosing ZIP export mode."""

    def __init__(self, parent):
        super().__init__(parent)
        self._export_mode = 'native'
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("ZIP Export Options")
        self.setModal(True)
        self.setMinimumWidth(420)

        layout = QVBoxLayout()

        instructions = QLabel(
            "Choose what to export:\n\n"
            "- Native: Original images, TIFF masks, and XML (paths made portable).\n"
            "- Augmented: What you see in the viewer (AOIs/POIs), keeps EXIF/XMP."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        self.native_radio = QRadioButton("Export Native data (original files + XML)")
        self.augmented_radio = QRadioButton("Export Augmented images (viewer overlays + metadata)")

        self.native_radio.setChecked(True)

        button_group = QButtonGroup(self)
        button_group.addButton(self.native_radio)
        button_group.addButton(self.augmented_radio)

        layout.addWidget(self.native_radio)
        layout.addWidget(self.augmented_radio)

        buttons = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        buttons.addStretch()
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

        self.setLayout(layout)

    def get_export_mode(self):
        return 'augmented' if self.augmented_radio.isChecked() else 'native'
