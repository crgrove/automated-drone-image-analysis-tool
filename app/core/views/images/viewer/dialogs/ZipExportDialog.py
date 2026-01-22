"""ZipExportDialog - Dialog to choose between Native or Augmented export."""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton, QButtonGroup, QCheckBox
from PySide6.QtCore import Qt
from helpers.TranslationMixin import TranslationMixin


class ZipExportDialog(TranslationMixin, QDialog):
    """Dialog for choosing ZIP export mode."""

    def __init__(self, parent):
        super().__init__(parent)
        self._export_mode = 'native'
        self._setup_ui()
        self._apply_translations()

    def _setup_ui(self):
        self.setWindowTitle(self.tr("ZIP Export Options"))
        self.setModal(True)
        self.setMinimumWidth(420)

        layout = QVBoxLayout()

        instructions = QLabel(
            self.tr(
                "Choose what to export:\n\n"
                "- Native: Original images, TIFF masks, and XML (paths made portable).\n"
                "- Augmented: What you see in the viewer (AOIs/POIs), keeps EXIF/XMP."
            )
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        self.native_radio = QRadioButton(self.tr("Export Native data (original files + XML)"))
        self.augmented_radio = QRadioButton(self.tr("Export Augmented images (viewer overlays + metadata)"))

        self.native_radio.setChecked(True)

        button_group = QButtonGroup(self)
        button_group.addButton(self.native_radio)
        button_group.addButton(self.augmented_radio)

        layout.addWidget(self.native_radio)
        layout.addWidget(self.augmented_radio)

        # Add spacing before checkbox
        layout.addSpacing(10)

        # Checkbox for including images without flagged AOIs
        self.include_no_flagged_checkbox = QCheckBox(self.tr("Include images without flagged AOIs"))
        self.include_no_flagged_checkbox.setChecked(False)  # Default: only export images with flagged AOIs
        self.include_no_flagged_checkbox.setToolTip(self.tr(
            "When unchecked, only images with at least one flagged AOI will be exported.\n"
            "When checked, all images will be exported regardless of flagged AOI status."
        ))
        layout.addWidget(self.include_no_flagged_checkbox)

        buttons = QHBoxLayout()
        ok_btn = QPushButton(self.tr("OK"))
        cancel_btn = QPushButton(self.tr("Cancel"))
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        buttons.addStretch()
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

        self.setLayout(layout)

    def get_export_mode(self):
        return 'augmented' if self.augmented_radio.isChecked() else 'native'

    def should_include_images_without_flagged_aois(self):
        """Return whether to include images without flagged AOIs."""
        return self.include_no_flagged_checkbox.isChecked()
