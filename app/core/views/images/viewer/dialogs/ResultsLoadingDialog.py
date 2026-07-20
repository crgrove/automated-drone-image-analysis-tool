"""ResultsLoadingDialog - heartbeat status while a results file opens.

A small, frame-light, always-on-top window shown for the duration of
`Viewer.__init__` so the user has visible feedback during the synchronous
phases (path validation, source-folder scan, WALDO pre-pass coordination,
AOI initialisation, first-image decode). Without it, the app looks frozen
between picking a results file and the viewer appearing.

The dialog is intentionally **non-modal**: the WALDO pre-pass shows its own
modal dialog on top of this one, so we don't want a second modal fighting
for focus. `set_status()` is the only API the caller needs, and each call
processes pending events so the label repaints between long synchronous
operations.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar, QApplication
)
from PySide6.QtCore import Qt

from helpers.TranslationMixin import TranslationMixin


class ResultsLoadingDialog(TranslationMixin, QDialog):
    """Indeterminate progress + status text while the viewer initialises."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Loading Results"))
        self.setModal(False)
        self.setWindowFlags(
            Qt.Dialog
            | Qt.CustomizeWindowHint
            | Qt.WindowTitleHint
            | Qt.WindowStaysOnTopHint
        )
        self.setFixedSize(420, 130)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        self._title = QLabel(self.tr("Opening results..."))
        title_font = self._title.font()
        title_font.setBold(True)
        self._title.setFont(title_font)
        layout.addWidget(self._title)

        self._bar = QProgressBar()
        # Indeterminate: no min/max progression, just the busy animation.
        self._bar.setRange(0, 0)
        self._bar.setTextVisible(False)
        layout.addWidget(self._bar)

        self._status = QLabel(self.tr("Preparing..."))
        self._status.setWordWrap(True)
        layout.addWidget(self._status)

    def set_status(self, status_text: str):
        """Update the visible status line and pump pending events.

        Calls QApplication.processEvents so the label repaints even when
        the caller is mid-way through a synchronous phase on the GUI
        thread (e.g. PIL.open across hundreds of images).
        """
        self._status.setText(status_text)
        QApplication.processEvents()

    def showEvent(self, event):
        super().showEvent(event)
        self.activateWindow()
        self.raise_()
