"""
WaldoClockCorrectionDialog - Confirm and apply a camera clock correction.

Shown when the WALDO pre-pass detects the clock-fault signature (timezone
inconsistent with GPS longitude + capture time ~half a day ahead of the
file write time). Presents the evidence and the proposed correction with
editable values; on Apply, a worker thread stamps a corrected capture UTC
into the waldo XMP namespace of every image (non-destructive - the EXIF
fields are never modified). Sun/shadow features prefer the corrected time.

Can also run in auto mode (no confirmation page) to re-apply a previously
accepted correction to images that were added since.
"""

from datetime import datetime
from typing import List, Optional
from zoneinfo import ZoneInfo

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QPushButton,
    QProgressBar, QWidget, QPlainTextEdit, QSpinBox, QLineEdit, QCheckBox
)

from helpers.TranslationMixin import TranslationMixin

from core.services.waldo import (
    WaldoMetadataService,
    WaldoProcessResult,
    ClockCorrectionProposal,
)


class _ClockWorker(QThread):
    progress = Signal(int, int, str)
    finished_with_result = Signal(object)

    def __init__(self, service: WaldoMetadataService, image_paths: List[str],
                 face_shift_h: float, tz_name: Optional[str],
                 fixed_offset_h: Optional[float]):
        super().__init__()
        self._service = service
        self._image_paths = image_paths
        self._face_shift_h = face_shift_h
        self._tz_name = tz_name
        self._fixed_offset_h = fixed_offset_h
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            result = self._service.apply_clock_correction(
                self._image_paths,
                self._face_shift_h,
                tz_name=self._tz_name,
                fixed_offset_h=self._fixed_offset_h,
                progress_cb=lambda i, n, name: self.progress.emit(i, n, name),
                cancel_cb=lambda: self._cancelled,
            )
        except Exception as e:
            result = WaldoProcessResult()
            result.errors.append(("<service>", f"{e!r}"))
        self.finished_with_result.emit(result)


class WaldoClockCorrectionDialog(TranslationMixin, QDialog):
    """Confirmation + progress dialog for the WALDO clock correction."""

    def __init__(self, parent, service: WaldoMetadataService,
                 image_paths: List[str], proposal: ClockCorrectionProposal,
                 auto_apply: bool = False):
        if parent is not None and not isinstance(parent, QWidget):
            parent = None
        super().__init__(parent)
        self.setWindowTitle(self.tr("WALDO Camera Clock Correction"))
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.resize(560, 360)

        self._service = service
        self._image_paths = image_paths
        self._proposal = proposal
        self._auto_apply = auto_apply
        self._worker: Optional[_ClockWorker] = None
        self._result: WaldoProcessResult = WaldoProcessResult()

        # Outcome flags the controller reads after exec():
        self.applied = False          # worker ran to completion (not cancelled)
        self.declined = False         # user chose Not Now
        self.remember_choice = False  # persist the decision for this folder
        self.accepted_face_shift_h: Optional[int] = None
        self.accepted_tz_text: Optional[str] = None

        layout = QVBoxLayout(self)

        self._intro_label = QLabel(self.tr(
            "The camera clock on these images appears to be misconfigured:"))
        self._intro_label.setWordWrap(True)
        layout.addWidget(self._intro_label)

        self._evidence = QLabel("\n".join(f"• {line}" for line in proposal.evidence))
        self._evidence.setWordWrap(True)
        layout.addWidget(self._evidence)

        self._explain_label = QLabel(self.tr(
            "ADIAT can stamp a corrected capture time into the image metadata. "
            "This is non-destructive: the original EXIF fields are not changed, "
            "and sun/shadow calculations will use the corrected time. Check the "
            "preview against when the flight actually flew - if it is off by "
            "12 hours, adjust the clock face error."))
        self._explain_label.setWordWrap(True)
        layout.addWidget(self._explain_label)

        form = QFormLayout()
        self._shift_spin = QSpinBox()
        self._shift_spin.setRange(-24, 24)
        self._shift_spin.setValue(proposal.face_shift_h)
        self._shift_spin.setSuffix(self.tr(" hours"))
        form.addRow(self.tr("Clock face error to remove:"), self._shift_spin)

        self._tz_edit = QLineEdit()
        default_tz = proposal.tz_name or (
            f"{proposal.fixed_offset_h:+.1f}" if proposal.fixed_offset_h is not None else "")
        self._tz_edit.setText(default_tz)
        self._tz_edit.setToolTip(self.tr(
            "IANA time zone name (e.g. America/Los_Angeles) or a fixed UTC "
            "offset in hours (e.g. -7)"))
        form.addRow(self.tr("True camera time zone:"), self._tz_edit)
        self._form_widget = QWidget()
        self._form_widget.setLayout(form)
        layout.addWidget(self._form_widget)

        self._preview_label = QLabel()
        self._preview_label.setWordWrap(True)
        layout.addWidget(self._preview_label)

        self._remember_check = QCheckBox(self.tr("Remember my choice for this folder"))
        self._remember_check.setChecked(True)
        layout.addWidget(self._remember_check)

        self._progress = QProgressBar()
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        self._status_label = QLabel()
        self._status_label.setWordWrap(True)
        self._status_label.setVisible(False)
        layout.addWidget(self._status_label)

        self._summary = QPlainTextEdit()
        self._summary.setReadOnly(True)
        self._summary.setVisible(False)
        layout.addWidget(self._summary, 1)

        button_row = QHBoxLayout()
        button_row.addStretch()
        self._apply_button = QPushButton(self.tr("Apply Correction"))
        self._apply_button.clicked.connect(self._on_apply)
        self._apply_button.setDefault(True)
        button_row.addWidget(self._apply_button)
        self._decline_button = QPushButton(self.tr("Not Now"))
        self._decline_button.clicked.connect(self._on_decline)
        button_row.addWidget(self._decline_button)
        self._cancel_button = QPushButton(self.tr("Cancel"))
        self._cancel_button.clicked.connect(self._on_cancel)
        self._cancel_button.setVisible(False)
        button_row.addWidget(self._cancel_button)
        self._ok_button = QPushButton(self.tr("OK"))
        self._ok_button.clicked.connect(self.accept)
        self._ok_button.setVisible(False)
        button_row.addWidget(self._ok_button)
        layout.addLayout(button_row)

        self._shift_spin.valueChanged.connect(self._update_preview)
        self._tz_edit.textChanged.connect(self._update_preview)
        self._update_preview()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def showEvent(self, event):
        super().showEvent(event)
        self.activateWindow()
        self.raise_()
        if self._auto_apply and self._worker is None:
            self._start_worker()

    def closeEvent(self, event):
        if self._worker is not None and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait(2000)
        super().closeEvent(event)

    @property
    def result_data(self) -> WaldoProcessResult:
        return self._result

    # ------------------------------------------------------------------
    # Correction parameters
    # ------------------------------------------------------------------

    def _parse_tz_input(self):
        """Return (tz_name, fixed_offset_h) from the editable field.

        Accepts an IANA zone name or a numeric UTC offset in hours.
        Returns (None, None) when the input is unusable.
        """
        text = self._tz_edit.text().strip()
        if not text:
            return None, None
        try:
            ZoneInfo(text)
            return text, None
        except Exception:
            pass
        try:
            offset = float(text.replace("UTC", "").strip())
            if -14.0 <= offset <= 14.0:
                return None, offset
        except ValueError:
            pass
        return None, None

    def _update_preview(self):
        tz_name, fixed_offset = self._parse_tz_input()
        if tz_name is None and fixed_offset is None:
            self._preview_label.setText(self.tr(
                "Enter a valid time zone (IANA name or UTC offset in hours)."))
            self._apply_button.setEnabled(False)
            return
        try:
            face_dt = datetime.strptime(self._proposal.sample_face, "%Y:%m:%d %H:%M:%S")
            corrected = WaldoMetadataService.compute_corrected_utc(
                face_dt, self._shift_spin.value(), tz_name, fixed_offset)
            self._preview_label.setText(self.tr(
                "{name}: camera says {before}  →  corrected {after}").format(
                    name=self._proposal.sample_name,
                    before=self._proposal.sample_face,
                    after=corrected.strftime("%Y-%m-%d %H:%M:%S UTC")))
            self._apply_button.setEnabled(True)
        except Exception:
            self._preview_label.setText(self.tr("Correction preview unavailable."))
            self._apply_button.setEnabled(False)

    # ------------------------------------------------------------------
    # Buttons / worker
    # ------------------------------------------------------------------

    def _on_apply(self):
        tz_name, fixed_offset = self._parse_tz_input()
        if tz_name is None and fixed_offset is None:
            return
        self.remember_choice = self._remember_check.isChecked()
        self.accepted_face_shift_h = self._shift_spin.value()
        self.accepted_tz_text = self._tz_edit.text().strip()
        self._start_worker()

    def _start_worker(self):
        tz_name, fixed_offset = self._parse_tz_input()
        if tz_name is None and fixed_offset is None:
            return
        for w in (self._intro_label, self._evidence, self._explain_label,
                  self._form_widget, self._preview_label, self._remember_check,
                  self._apply_button, self._decline_button):
            w.setVisible(False)
        self._progress.setRange(0, max(1, len(self._image_paths)))
        self._progress.setValue(0)
        self._progress.setVisible(True)
        self._status_label.setText(self.tr("Stamping corrected capture times..."))
        self._status_label.setVisible(True)
        self._cancel_button.setVisible(True)

        self._worker = _ClockWorker(
            self._service, self._image_paths,
            float(self._shift_spin.value()), tz_name, fixed_offset)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished_with_result.connect(self._on_finished)
        self._worker.start()

    def _on_decline(self):
        self.declined = True
        self.remember_choice = self._remember_check.isChecked()
        self.reject()

    def _on_cancel(self):
        if self._worker is not None:
            self._worker.cancel()
        self._cancel_button.setEnabled(False)
        self._cancel_button.setText(self.tr("Cancelling..."))

    def _on_progress(self, current: int, total: int, status_text: str):
        if total > 0 and self._progress.maximum() != total:
            self._progress.setRange(0, total)
        self._progress.setValue(current)
        self._status_label.setText(status_text)

    def _on_finished(self, result: WaldoProcessResult):
        self._result = result
        self.applied = not result.cancelled
        self._status_label.setVisible(False)
        self._progress.setMaximum(max(1, self._progress.value()))
        self._progress.setValue(self._progress.maximum())

        lines = []
        lines.append(self.tr("Corrected:        {n}").format(n=result.processed))
        lines.append(self.tr("Already corrected: {n}").format(n=result.already_current))
        lines.append(self.tr("Errors:           {n}").format(n=len(result.errors)))
        if result.cancelled:
            lines.append("")
            lines.append(self.tr("Cancelled - remaining images are uncorrected."))
        for name, msg in result.errors[:20]:
            lines.append(f"  {name}: {msg}")
        self._summary.setPlainText("\n".join(lines))
        self._summary.setVisible(True)
        self._cancel_button.setVisible(False)
        self._ok_button.setVisible(True)
        self._ok_button.setDefault(True)
        self._ok_button.setFocus()
