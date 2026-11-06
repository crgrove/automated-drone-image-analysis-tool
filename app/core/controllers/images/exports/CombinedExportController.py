"""
CombinedExportController - The results-folder scan's combined export.

The scan already found every ADIAT_Data.xml; this controller asks which
outputs to make (CombinedExportDialog) and makes each from the same runs and
the same AOI scope:

- a KML of the detections (CombinedDetectionsService, on a worker thread);
- the detections as CalTopo markers, each with its report photo
  (CombinedCalTopoExportController);
- the combined PDF report (CombinedPdfExportController).

Every save location is asked for before anything runs, and the outputs run
in order of how soon they need the operator: the KML (none), CalTopo (a
sign-in and a map choice), then the PDF, which can take minutes. Nobody is
called back to answer a prompt after a long unattended build.
"""

import os

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from core.controllers.images.exports.CombinedCalTopoExportController import CombinedCalTopoExportController
from core.controllers.images.exports.CombinedPdfExportController import CombinedPdfExportController
from core.services.LoggerService import LoggerService
from core.services.SettingsService import SettingsService
from core.services.export.CombinedDetectionsService import CombinedDetectionsService
from core.views.images.viewer.dialogs.CalTopoMethodDialog import CalTopoMethodDialog
from core.views.images.viewer.dialogs.CombinedExportDialog import CombinedExportDialog
from core.views.images.viewer.dialogs.ExportProgressDialog import ExportProgressDialog
from helpers.TranslationMixin import TranslationMixin


class CombinedRunLoadThread(QThread):
    """Worker thread that reads and merges the scanned results files."""

    loaded = Signal(list)
    errorOccurred = Signal(str)

    def __init__(self, service, xml_paths):
        super().__init__()
        self.service = service
        self.xml_paths = xml_paths

    def run(self):
        try:
            self.loaded.emit(self.service.load_runs(self.xml_paths))
        except Exception as e:
            self.errorOccurred.emit(str(e))


class CombinedKmlExportThread(QThread):
    """Worker thread for the detections KML."""

    success = Signal(dict)
    canceled = Signal()
    errorOccurred = Signal(str)
    progressUpdated = Signal(int, int, str)

    def __init__(self, service, output_path, runs):
        super().__init__()
        self.service = service
        self.output_path = output_path
        self.runs = runs
        self._is_canceled = False

    def run(self):
        try:
            summary = self.service.generate_kml(
                self.output_path,
                self.runs,
                progress_callback=self.progressUpdated.emit,
                cancel_check=lambda: self._is_canceled,
            )
            if summary is None:
                self.canceled.emit()
            else:
                self.success.emit(summary)
        except Exception as e:
            self.errorOccurred.emit(str(e))

    def cancel(self):
        self._is_canceled = True


class CombinedExportController(TranslationMixin):
    """Controller for the combined (multi-run) export: PDF, KML and CalTopo."""

    def __init__(self, parent_widget, logger=None):
        """
        Args:
            parent_widget: Parent for the dialogs (MainWindow).
            logger: Optional LoggerService override.
        """
        self.parent = parent_widget
        self.logger = logger or LoggerService()
        # Held so a running QThread is never garbage collected
        self._load_thread = None
        self._kml_thread = None

    def export(self, results, recovery_session=None):
        """Ask for the outputs, then make each from the scanned results.

        Args:
            results: List of ResultsScanResult from the folder scan.
            recovery_session: Optional RecoverySession from the scan, so an
                XML that travelled without its images (a reviewer's copy)
                can find them under the scanned tree.

        Returns:
            bool: True when at least one output was attempted, False when
            there was nothing to export or the operator cancelled.
        """
        xml_paths = [r.xml_path for r in results if getattr(r, 'xml_path', None)]
        if not xml_paths:
            QMessageBox.warning(
                self.parent,
                self.tr("Nothing to Export"),
                self.tr("The scan found no results files to collate."))
            return False

        dialog = CombinedExportDialog(self.parent)
        if dialog.exec() != QDialog.Accepted:
            return False

        # Loaded before any save prompt, so "nothing to export" comes first
        runs = []
        detections_service = None
        map_outputs = dialog.should_export_kml() or dialog.should_export_caltopo()
        if map_outputs:
            detections_service = CombinedDetectionsService(
                include_images_without_flagged_aois=dialog.get_include_images_without_flagged_aois(),
                use_terrain_elevation=SettingsService().get_bool_setting('UseTerrainElevation', True),
                recovery_session=recovery_session,
                logger=self.logger,
            )
            runs = self._load_runs(detections_service, xml_paths)
            if runs is None:
                return False
            if not runs:
                # The PDF covers the same AOIs, so it would be empty too
                QMessageBox.information(
                    self.parent,
                    self.tr("Nothing to Export"),
                    self.tr(
                        "None of the scanned results have AOIs to export on this computer.\n\n"
                        "Flag AOIs in the viewer, or check 'Include images without flagged AOIs'."))
                return False

        pdf_path = self._ask_pdf_path() if dialog.should_export_pdf() else None
        kml_path = self._ask_kml_path(pdf_path) if dialog.should_export_kml() else None
        if not (pdf_path or kml_path or dialog.should_export_caltopo()):
            return False

        if kml_path:
            self._export_kml(detections_service, kml_path, runs)
        if dialog.should_export_caltopo():
            self._export_caltopo(
                runs, dialog.should_attach_caltopo_photos(), detections_service.use_terrain_elevation)
        if pdf_path:
            CombinedPdfExportController(self.parent, self.logger).generate_combined_pdf(
                pdf_path, xml_paths, dialog, recovery_session=recovery_session)
        return True

    def _ask_pdf_path(self):
        """Save location for the report, or None if the operator cancelled."""
        file_name, _ = QFileDialog.getSaveFileName(
            self.parent,
            self.tr("Save Combined PDF"),
            "",
            self.tr("PDF files (*.pdf)"))
        return file_name or None

    def _ask_kml_path(self, pdf_path):
        """Save location for the KML, offered beside the report when there is one."""
        suggested = os.path.splitext(pdf_path)[0] + ".kml" if pdf_path else ""
        file_name, _ = QFileDialog.getSaveFileName(
            self.parent,
            self.tr("Save Detections KML"),
            suggested,
            self.tr("KML files (*.kml);;KMZ files (*.kmz)"))
        return file_name or None

    def _load_runs(self, service, xml_paths):
        """Read and merge the results files on a worker thread.

        Returns:
            list: RunReportContexts with AOIs in scope (possibly empty), or
            None when reading failed (already reported) or was cancelled.
        """
        progress_dialog = ExportProgressDialog(
            self.parent, title=self.tr("Reading Results"), total_items=100)
        progress_dialog.set_title(self.tr("Reading results files..."))
        outcome = {}

        def on_loaded(runs):
            outcome['runs'] = runs
            progress_dialog.accept()

        def on_error(error_message):
            outcome['error'] = error_message
            progress_dialog.reject()

        self._load_thread = CombinedRunLoadThread(service, xml_paths)
        self._load_thread.loaded.connect(on_loaded)
        self._load_thread.errorOccurred.connect(on_error)
        # Reading cannot be interrupted; Cancel stops waiting on it
        progress_dialog.cancel_requested.connect(progress_dialog.reject)

        self._load_thread.start()
        progress_dialog.exec()
        self._load_thread.wait()

        if 'error' in outcome:
            self.logger.error(f"Combined export: reading results failed: {outcome['error']}")
            QMessageBox.critical(
                self.parent,
                self.tr("Export Failed"),
                self.tr("Failed to read the results files: {error}").format(error=outcome['error']))
            return None
        return outcome.get('runs')

    def _export_kml(self, service, output_path, runs):
        """Write the detections KML behind a progress dialog and report it."""
        progress_dialog = ExportProgressDialog(
            self.parent, title=self.tr("Exporting Detections KML"), total_items=100)
        progress_dialog.set_title(self.tr("Placing detections..."))
        outcome = {}

        def on_progress(current, total, message):
            progress_dialog.update_progress(current, total, message)

        def on_success(summary):
            outcome['summary'] = summary
            progress_dialog.accept()

        def on_error(error_message):
            outcome['error'] = error_message
            progress_dialog.reject()

        self._kml_thread = CombinedKmlExportThread(service, output_path, runs)
        self._kml_thread.progressUpdated.connect(on_progress)
        self._kml_thread.success.connect(on_success)
        self._kml_thread.errorOccurred.connect(on_error)
        self._kml_thread.canceled.connect(progress_dialog.reject)
        progress_dialog.cancel_requested.connect(self._kml_thread.cancel)

        self._kml_thread.start()
        progress_dialog.exec()
        self._kml_thread.wait()

        if 'error' in outcome:
            self.logger.error(f"Combined KML export to {output_path} failed: {outcome['error']}")
            QMessageBox.critical(
                self.parent,
                self.tr("Export Failed"),
                self.tr("Failed to export the detections KML: {error}").format(error=outcome['error']))
            return False
        if 'summary' not in outcome:
            return False  # Cancelled; nothing was written

        summary = outcome['summary']
        message = self.tr("Exported {count} detection(s) to:\n{path}").format(
            count=summary['exported'], path=output_path)
        if summary['unplaced']:
            message += "\n\n" + self.tr(
                "{count} AOI(s) were left out: neither they nor their image "
                "have a GPS position.").format(count=summary['unplaced'])
        QMessageBox.information(self.parent, self.tr("Export Complete"), message)
        return True

    def _export_caltopo(self, runs, include_photos, use_terrain_elevation):
        """Add the detections to a CalTopo map; CalTopo reports the outcome."""
        method_dialog = CalTopoMethodDialog(self.parent)
        if method_dialog.exec() != QDialog.Accepted:
            return False
        controller = CombinedCalTopoExportController(
            self.parent, runs, use_terrain_elevation=use_terrain_elevation, logger=self.logger)
        return controller.export_detections(method_dialog.get_selected_method(), include_photos)
