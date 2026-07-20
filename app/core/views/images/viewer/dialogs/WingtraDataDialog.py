"""
WingtraDataDialog - Dialog showing Wingtra CSV import summary.

Shown after CSV is parsed, images matched, and AGL computed from terrain.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox
)
from PySide6.QtCore import Qt

from helpers.TranslationMixin import TranslationMixin


class WingtraDataDialog(TranslationMixin, QDialog):
    """Dialog showing Wingtra CSV import summary and confirmation."""

    def __init__(self, parent, matched_count: int, unmatched_csv_count: int,
                 unmatched_images_count: int, agl_computed_count: int = 0,
                 distance_unit: str = 'ft'):
        """
        Initialize the dialog.

        Args:
            parent: Parent widget
            matched_count: Number of successfully matched images
            unmatched_csv_count: Number of CSV entries without matching images
            unmatched_images_count: Number of result images without CSV data
            agl_computed_count: Number of images with terrain-derived AGL
            distance_unit: User's preferred distance unit ('ft' or 'm')
        """
        super().__init__(parent)
        self.distance_unit = distance_unit
        self.matched_count = matched_count
        self.unmatched_csv_count = unmatched_csv_count
        self.unmatched_images_count = unmatched_images_count
        self.agl_computed_count = agl_computed_count

        self._setup_ui()

    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle(self.tr("Wingtra Data Import"))
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Summary section
        summary_group = QGroupBox(self.tr("Import Summary"))
        summary_layout = QVBoxLayout(summary_group)

        summary_text = self.tr(
            "<b>Matched images:</b> {matched}<br>"
            "<b>CSV entries without match:</b> {unmatched_csv}<br>"
            "<b>Result images without CSV data:</b> {unmatched_images}"
        ).format(
            matched=self.matched_count,
            unmatched_csv=self.unmatched_csv_count,
            unmatched_images=self.unmatched_images_count,
        )

        summary_label = QLabel(summary_text)
        summary_label.setTextFormat(Qt.RichText)
        summary_layout.addWidget(summary_label)
        layout.addWidget(summary_group)

        # Terrain / AGL section
        terrain_group = QGroupBox(self.tr("Altitude & GSD"))
        terrain_layout = QVBoxLayout(terrain_group)

        if self.agl_computed_count > 0:
            terrain_text = self.tr(
                "<b>AGL computed from terrain:</b> {agl_count} of {matched_count} images<br>"
                "<br>"
                "Per-image AGL is derived from the CSV altitude (ASL) minus "
                "terrain elevation at each GPS location. GSD will be calculated "
                "automatically using the camera sensor data and focal length."
            ).format(
                agl_count=self.agl_computed_count,
                matched_count=self.matched_count,
            )
        else:
            terrain_text = self.tr(
                "<b>Terrain data unavailable</b> - AGL could not be computed.<br>"
                "<br>"
                "Orientation (yaw/pitch/roll) will still be applied from the CSV. "
                "GSD and altitude displays require terrain data or a manual "
                "altitude override (Shift+O) after import."
            )

        terrain_label = QLabel(terrain_text)
        terrain_label.setTextFormat(Qt.RichText)
        terrain_label.setWordWrap(True)
        terrain_layout.addWidget(terrain_label)
        layout.addWidget(terrain_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton(self.tr("Cancel"))
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.ok_button = QPushButton(self.tr("Apply Wingtra Data"))
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)

        layout.addLayout(button_layout)

    def showEvent(self, event):
        """Override showEvent to ensure dialog receives focus on macOS."""
        super().showEvent(event)
        self.activateWindow()
        self.raise_()
