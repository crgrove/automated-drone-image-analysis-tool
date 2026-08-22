"""
WaldoFlightLogDialog - Calibrate and apply a ForeFlight track log's attitude.

Two-phase modal mirroring WaldoClockCorrectionDialog:

1. Calibration (worker thread): reads per-image metadata, then fits each
   candidate CSV's clock offset against the image GPS positions and the
   attitude channel's lag against coordinated-turn physics. The first
   candidate whose fit is accepted wins; a bad fit means "wrong log for
   this folder" and is skipped.
2. Confirmation + apply (worker thread): shows the fit statistics for the
   operator to sanity-check, then stamps per-image camera attitude and the
   refined capture time. In auto mode (remembered acceptance) the
   confirmation page is skipped and a silent re-apply runs with progress.
"""

from typing import List, Optional, Tuple

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QPlainTextEdit, QCheckBox
)

from helpers.TranslationMixin import TranslationMixin

from core.services.waldo import WaldoMetadataService, WaldoProcessResult
from core.services.waldo.WaldoFlightLog import (
    FlightLogFit,
    FlightLogTrack,
    WaldoFlightLogService,
)


class _CalibrateWorker(QThread):
    progress = Signal(int, int, str)
    finished_with_result = Signal(object)  # (fit|None, track|None, records, fail_reason)

    def __init__(self, metadata_service: WaldoMetadataService,
                 flight_service: WaldoFlightLogService,
                 image_paths: List[str], candidate_logs: List[str]):
        super().__init__()
        self._metadata_service = metadata_service
        self._flight_service = flight_service
        self._image_paths = image_paths
        self._candidate_logs = candidate_logs
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            records, cancelled = self._metadata_service.collect_flight_log_records(
                self._image_paths,
                progress_cb=lambda i, n, name: self.progress.emit(i, n, name),
                cancel_cb=lambda: self._cancelled,
            )
            if cancelled:
                self.finished_with_result.emit((None, None, [], "cancelled"))
                return
            images = [(r.capture_epoch, r.lat, r.lon) for r in records
                      if r.error is None and r.capture_epoch is not None and r.lat is not None]
            if not images:
                self.finished_with_result.emit(
                    (None, None, records, self.tr("No images with resolvable GPS + capture time.")))
                return
            reason = self.tr("No ForeFlight track log found for this folder.")
            for log_path in self._candidate_logs:
                if self._cancelled:
                    self.finished_with_result.emit((None, None, records, "cancelled"))
                    return
                self.progress.emit(0, 0, self.tr("Calibrating {name}...").format(
                    name=log_path.rsplit('\\', 1)[-1].rsplit('/', 1)[-1]))
                fit = self._flight_service.calibrate(log_path, images)
                if fit.accepted:
                    track = self._flight_service.parse(log_path)
                    self.finished_with_result.emit((fit, track, records, None))
                    return
                reason = fit.reason
            self.finished_with_result.emit((None, None, records, reason))
        except Exception as e:
            self.finished_with_result.emit((None, None, [], f"{e!r}"))


class _ApplyWorker(QThread):
    progress = Signal(int, int, str)
    finished_with_result = Signal(object)

    def __init__(self, metadata_service: WaldoMetadataService, records,
                 fit: FlightLogFit, track: FlightLogTrack):
        super().__init__()
        self._metadata_service = metadata_service
        self._records = records
        self._fit = fit
        self._track = track
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            result = self._metadata_service.apply_flight_log_attitude(
                self._records, self._fit, self._track,
                progress_cb=lambda i, n, name: self.progress.emit(i, n, name),
                cancel_cb=lambda: self._cancelled,
            )
        except Exception as e:
            result = WaldoProcessResult()
            result.errors.append(("<service>", f"{e!r}"))
        self.finished_with_result.emit(result)


class WaldoFlightLogDialog(TranslationMixin, QDialog):
    """Calibration + confirmation + progress dialog for the flight-log stage."""

    def __init__(self, parent, metadata_service: WaldoMetadataService,
                 flight_service: WaldoFlightLogService,
                 image_paths: List[str], candidate_logs: List[str],
                 auto_apply: bool = False):
        from PySide6.QtWidgets import QWidget
        if parent is not None and not isinstance(parent, QWidget):
            parent = None
        super().__init__(parent)
        self.setWindowTitle(self.tr("WALDO Flight Track Log"))
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.resize(600, 400)

        self._metadata_service = metadata_service
        self._flight_service = flight_service
        self._image_paths = image_paths
        self._candidate_logs = candidate_logs
        self._auto_apply = auto_apply
        self._worker: Optional[QThread] = None
        self._records = []
        self._track: Optional[FlightLogTrack] = None
        self._result: WaldoProcessResult = WaldoProcessResult()

        # Outcome flags the caller reads after exec():
        self.applied = False
        self.declined = False
        self.remember_choice = False
        self.fit: Optional[FlightLogFit] = None

        layout = QVBoxLayout(self)

        self._intro_label = QLabel(self.tr(
            "An aircraft track log can supply the true per-image camera "
            "attitude (bank and pitch) and a GPS-accurate capture time, "
            "making image footprints and AOI positions substantially more "
            "accurate."))
        self._intro_label.setWordWrap(True)
        layout.addWidget(self._intro_label)

        self._stats_label = QLabel()
        self._stats_label.setWordWrap(True)
        self._stats_label.setVisible(False)
        layout.addWidget(self._stats_label)

        self._remember_check = QCheckBox(self.tr("Remember my choice for this folder"))
        self._remember_check.setChecked(True)
        self._remember_check.setVisible(False)
        layout.addWidget(self._remember_check)

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        layout.addWidget(self._progress)

        self._status_label = QLabel(self.tr("Reading image metadata..."))
        self._status_label.setWordWrap(True)
        layout.addWidget(self._status_label)

        self._summary = QPlainTextEdit()
        self._summary.setReadOnly(True)
        self._summary.setVisible(False)
        layout.addWidget(self._summary, 1)

        button_row = QHBoxLayout()
        button_row.addStretch()
        self._apply_button = QPushButton(self.tr("Apply Flight Log"))
        self._apply_button.clicked.connect(self._on_apply)
        self._apply_button.setVisible(False)
        button_row.addWidget(self._apply_button)
        self._decline_button = QPushButton(self.tr("Not Now"))
        self._decline_button.clicked.connect(self._on_decline)
        self._decline_button.setVisible(False)
        button_row.addWidget(self._decline_button)
        self._cancel_button = QPushButton(self.tr("Cancel"))
        self._cancel_button.clicked.connect(self._on_cancel)
        button_row.addWidget(self._cancel_button)
        self._ok_button = QPushButton(self.tr("OK"))
        self._ok_button.clicked.connect(self.accept)
        self._ok_button.setVisible(False)
        button_row.addWidget(self._ok_button)
        layout.addLayout(button_row)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def showEvent(self, event):
        super().showEvent(event)
        self.activateWindow()
        self.raise_()
        if self._worker is None:
            self._start_calibration()

    def closeEvent(self, event):
        if self._worker is not None and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait(2000)
        super().closeEvent(event)

    @property
    def result_data(self) -> WaldoProcessResult:
        return self._result

    # ------------------------------------------------------------------
    # Calibration phase
    # ------------------------------------------------------------------

    def _start_calibration(self):
        self._worker = _CalibrateWorker(
            self._metadata_service, self._flight_service,
            self._image_paths, self._candidate_logs)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished_with_result.connect(self._on_calibrated)
        self._worker.start()

    def _on_calibrated(self, payload: Tuple):
        fit, track, records, fail_reason = payload
        self._records = records
        self._track = track
        self.fit = fit

        if fit is None:
            if fail_reason == "cancelled" or self._auto_apply:
                # Silent for auto mode: a remembered log that stops fitting
                # (file moved, folder re-tasked) must not nag on every open.
                self.reject()
                return
            self._progress.setVisible(False)
            self._status_label.setText(self.tr(
                "The track log does not match these images: {reason}").format(
                    reason=fail_reason))
            self._cancel_button.setVisible(False)
            self._ok_button.setVisible(True)
            return

        if self._auto_apply:
            self._start_apply()
            return

        offset = fit.clock_offset_s
        clock_line = self.tr(
            "Camera clock is {n:.1f} s {direction} of GPS time").format(
                n=abs(offset), direction=self.tr("ahead") if offset < 0 else self.tr("behind"))
        lines = [
            self.tr("Track log: {name}").format(name=fit.log_path),
            clock_line,
            self.tr("Images sit {d:.0f} m from the flight track on average "
                    "({p:.0%} matched)").format(d=fit.mean_track_dist_m,
                                                p=fit.matched_fraction),
        ]
        if fit.attitude_reliable:
            lines.append(self.tr(
                "Attitude channel verified against turn physics "
                "(correlation {c:.2f}, recorded {lag:+.0f} s late)").format(
                    c=fit.lag_correlation, lag=fit.attitude_lag_s))
            lines.append(self.tr(
                "Bank during capture: {lo:+.1f}° to {hi:+.1f}°").format(
                    lo=fit.bank_min_deg, hi=fit.bank_max_deg))
        else:
            lines.append(self.tr(
                "Attitude channel is NOT reliable (correlation {c:.2f}) - "
                "only the capture-time refinement will be stamped").format(
                    c=fit.lag_correlation))
        self._stats_label.setText("\n".join(f"• {line}" for line in lines))
        self._stats_label.setVisible(True)
        self._remember_check.setVisible(True)
        self._progress.setVisible(False)
        self._status_label.setVisible(False)
        self._apply_button.setVisible(True)
        self._apply_button.setDefault(True)
        self._decline_button.setVisible(True)
        self._cancel_button.setVisible(False)

    # ------------------------------------------------------------------
    # Apply phase
    # ------------------------------------------------------------------

    def _on_apply(self):
        self.remember_choice = self._remember_check.isChecked()
        self._start_apply()

    def _start_apply(self):
        for w in (self._intro_label, self._stats_label, self._remember_check,
                  self._apply_button, self._decline_button):
            w.setVisible(False)
        self._progress.setRange(0, max(1, len(self._records)))
        self._progress.setValue(0)
        self._progress.setVisible(True)
        self._status_label.setText(self.tr("Stamping flight-log attitude..."))
        self._status_label.setVisible(True)
        self._cancel_button.setVisible(True)

        self._worker = _ApplyWorker(
            self._metadata_service, self._records, self.fit, self._track)
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
        if total > 0:
            if self._progress.maximum() != total:
                self._progress.setRange(0, total)
            self._progress.setValue(current)
        elif self._progress.maximum() != 0:
            self._progress.setRange(0, 0)
        self._status_label.setText(status_text)

    def _on_finished(self, result: WaldoProcessResult):
        self._result = result
        self.applied = not result.cancelled
        if self._auto_apply:
            # Silent re-apply: no summary page, just finish.
            self.accept()
            return
        self._status_label.setVisible(False)
        self._progress.setRange(0, max(1, self._progress.value() or 1))
        self._progress.setValue(self._progress.maximum())

        lines = []
        lines.append(self.tr("Stamped:          {n}").format(n=result.processed))
        lines.append(self.tr("Already current:  {n}").format(n=result.already_current))
        lines.append(self.tr("Errors:           {n}").format(n=len(result.errors)))
        for note in result.notes:
            lines.append("")
            lines.append(note)
        if result.cancelled:
            lines.append("")
            lines.append(self.tr("Cancelled - remaining images are unstamped."))
        for name, msg in result.errors[:20]:
            lines.append(f"  {name}: {msg}")
        self._summary.setPlainText("\n".join(lines))
        self._summary.setVisible(True)
        self._cancel_button.setVisible(False)
        self._ok_button.setVisible(True)
        self._ok_button.setDefault(True)
        self._ok_button.setFocus()
