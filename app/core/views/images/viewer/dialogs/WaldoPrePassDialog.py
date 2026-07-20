"""
WaldoPrePassDialog - Modal progress dialog for the WALDO metadata pre-pass.

Spawns a QThread that runs WaldoMetadataService.process_folder. Shows a
progress bar with the current filename, then transitions to a summary
panel listing processed/already-current/error counts.
"""

from typing import List

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QProgressBar, QWidget,
    QHBoxLayout, QPlainTextEdit
)

from helpers.TranslationMixin import TranslationMixin

from core.services.waldo import (
    WaldoMetadataService,
    WaldoProcessResult,
)


class _WaldoWorker(QThread):
    progress = Signal(int, int, str)
    finished_with_result = Signal(object)

    def __init__(self, service: WaldoMetadataService, image_paths: List[str]):
        super().__init__()
        self._service = service
        self._image_paths = image_paths
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            result = self._service.process_folder(
                self._image_paths,
                progress_cb=lambda i, n, name: self.progress.emit(i, n, name),
                cancel_cb=lambda: self._cancelled,
            )
        except Exception as e:
            result = WaldoProcessResult()
            result.errors.append(("<service>", f"{e!r}"))
        self.finished_with_result.emit(result)


class WaldoPrePassDialog(TranslationMixin, QDialog):
    """Modal dialog driving the WALDO pre-pass on a folder of images."""

    def __init__(self, parent, service: WaldoMetadataService, image_paths: List[str]):
        if parent is not None and not isinstance(parent, QWidget):
            parent = None
        super().__init__(parent)
        self.setWindowTitle(self.tr("Preparing WALDO Images"))
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.resize(520, 220)

        self._service = service
        self._image_paths = image_paths
        self._result: WaldoProcessResult = WaldoProcessResult()
        self._worker: _WaldoWorker = _WaldoWorker(service, image_paths)

        layout = QVBoxLayout(self)

        self._title_label = QLabel(self.tr("Synthesising WALDO metadata..."))
        font = self._title_label.font()
        font.setBold(True)
        self._title_label.setFont(font)
        layout.addWidget(self._title_label)

        self._progress = QProgressBar()
        self._progress.setMinimum(0)
        self._progress.setMaximum(max(1, len(image_paths)))
        self._progress.setValue(0)
        layout.addWidget(self._progress)

        self._current_label = QLabel(self.tr("Initialising..."))
        self._current_label.setWordWrap(True)
        layout.addWidget(self._current_label)

        self._summary = QPlainTextEdit()
        self._summary.setReadOnly(True)
        self._summary.setVisible(False)
        layout.addWidget(self._summary, 1)

        button_row = QHBoxLayout()
        button_row.addStretch()
        self._cancel_button = QPushButton(self.tr("Cancel"))
        self._cancel_button.clicked.connect(self._on_cancel)
        button_row.addWidget(self._cancel_button)
        self._ok_button = QPushButton(self.tr("OK"))
        self._ok_button.clicked.connect(self.accept)
        self._ok_button.setVisible(False)
        button_row.addWidget(self._ok_button)
        layout.addLayout(button_row)

        self._worker.progress.connect(self._on_progress)
        self._worker.finished_with_result.connect(self._on_finished)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def showEvent(self, event):
        super().showEvent(event)
        self.activateWindow()
        self.raise_()
        if not self._worker.isRunning():
            self._worker.start()

    def closeEvent(self, event):
        if self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait(2000)
        super().closeEvent(event)

    @property
    def result_data(self) -> WaldoProcessResult:
        return self._result

    # ------------------------------------------------------------------
    # Worker callbacks
    # ------------------------------------------------------------------

    def _on_progress(self, current: int, total: int, status_text: str):
        # total == 0 is the worker's signal that this is an indeterminate phase
        # (e.g. loading the EGM96 grid). Switch the bar to busy mode and just
        # show the phase description; otherwise tick determinate progress.
        if total == 0:
            if self._progress.maximum() != 0 or self._progress.minimum() != 0:
                self._progress.setRange(0, 0)
        else:
            if self._progress.minimum() != 0 or self._progress.maximum() != total:
                self._progress.setRange(0, total)
            self._progress.setValue(current)
        self._current_label.setText(status_text)

    def _on_finished(self, result: WaldoProcessResult):
        self._result = result
        self._title_label.setText(
            self.tr("WALDO Pre-Pass Complete") if not result.cancelled
            else self.tr("WALDO Pre-Pass Cancelled")
        )
        self._current_label.setVisible(False)
        self._progress.setMaximum(max(1, self._progress.value()))
        self._progress.setValue(self._progress.maximum())

        lines = []
        lines.append(self.tr("Processed:        {n}").format(n=result.processed))
        lines.append(self.tr("Already up-to-date: {n}").format(n=result.already_current))
        lines.append(self.tr("Skipped (non-WALDO): {n}").format(n=result.skipped))
        lines.append(self.tr("Errors:           {n}").format(n=len(result.errors)))
        if result.errors:
            lines.append("")
            lines.append(self.tr("Per-image errors:"))
            for name, msg in result.errors:
                lines.append(f"  {name}: {msg}")
        self._summary.setPlainText("\n".join(lines))
        self._summary.setVisible(True)
        self._cancel_button.setVisible(False)
        self._ok_button.setVisible(True)
        self._ok_button.setDefault(True)
        self._ok_button.setFocus()
        self.adjustSize()

    def _on_cancel(self):
        self._worker.cancel()
        self._cancel_button.setEnabled(False)
        self._cancel_button.setText(self.tr("Cancelling..."))
        self._current_label.setText(self.tr("Cancellation requested..."))
