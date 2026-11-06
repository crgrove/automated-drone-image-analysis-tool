"""
CombinedPdfExportController - Exports a folder of results into one PDF.

Part of the results-folder scan's combined export (CombinedExportController
collects the options and the save path): runs CombinedPdfReportService on a
worker thread and shows the standard export progress dialog.
"""

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from core.services.LoggerService import LoggerService
from core.services.SettingsService import SettingsService
from core.services.export.CombinedPdfReportService import CombinedPdfReportService
from core.views.images.viewer.dialogs.ExportProgressDialog import ExportProgressDialog
from helpers.TranslationMixin import TranslationMixin


class CombinedPdfGenerationThread(QThread):
    """Worker thread for the collated report build."""

    success = Signal()
    canceled = Signal()
    errorOccurred = Signal(str)
    progressUpdated = Signal(int, int, str)

    def __init__(self, service, output_path, xml_paths):
        super().__init__()
        self.service = service
        self.output_path = output_path
        self.xml_paths = xml_paths
        self._is_canceled = False

    def run(self):
        try:
            def progress_callback(current, total, message):
                if not self._is_canceled:
                    self.progressUpdated.emit(current, total, message)

            def cancel_check():
                return self._is_canceled

            self.service.generate_combined_report(
                self.output_path,
                self.xml_paths,
                progress_callback=progress_callback,
                cancel_check=cancel_check,
            )
            if self._is_canceled:
                self.canceled.emit()
            else:
                self.success.emit()
        except Exception as e:
            self.errorOccurred.emit(str(e))

    def cancel(self):
        self._is_canceled = True


class CombinedPdfExportController(TranslationMixin):
    """Controller for the combined (multi-run) PDF export."""

    def __init__(self, parent_widget, logger=None):
        """
        Args:
            parent_widget: Parent for the dialogs (MainWindow).
            logger: Optional LoggerService override.
        """
        self.parent = parent_widget
        self.logger = logger or LoggerService()
        self.pdf_thread = None
        self.progress_dialog = None
        self._recovery_session = None

    def generate_combined_pdf(self, output_path, xml_paths, options, recovery_session=None):
        """Build one PDF from the scanned results, behind a progress dialog.

        Returns once the build has finished, failed or been cancelled.

        Args:
            output_path: Destination PDF path, already chosen by the user.
            xml_paths: The ADIAT_Data.xml files to collate.
            options: Report options exposing get_organization(),
                get_search_name(), get_include_images_without_flagged_aois()
                and get_map_tile_source() (CombinedExportDialog).
            recovery_session: Optional RecoverySession from the scan, so an
                XML that travelled without its images (a reviewer's copy)
                can find them under the scanned tree.

        Returns:
            bool: True when the build was started, False when it failed to.
        """
        self._recovery_session = recovery_session
        try:
            service = self._build_service(options)

            self.progress_dialog = ExportProgressDialog(
                self.parent,
                title=self.tr("Generating Combined PDF"),
                total_items=100)
            self.progress_dialog.set_title(self.tr("Preparing combined report..."))

            self.pdf_thread = CombinedPdfGenerationThread(service, output_path, xml_paths)
            self.pdf_thread.success.connect(self._on_success)
            self.pdf_thread.errorOccurred.connect(self._on_error)
            self.pdf_thread.progressUpdated.connect(self._on_progress)
            self.pdf_thread.canceled.connect(self._on_cancelled)
            self.progress_dialog.cancel_requested.connect(self.pdf_thread.cancel)

            self.pdf_thread.start()
            self.progress_dialog.show()
            QApplication.processEvents()
            if self.progress_dialog.exec() == QDialog.Rejected:
                self.pdf_thread.cancel()
            return True

        except Exception as e:
            self.logger.error(f"Combined PDF export failed to start: {e}")
            QMessageBox.critical(
                self.parent,
                self.tr("Error"),
                self.tr("Failed to generate combined PDF: {error}").format(error=str(e)))
            return False

    def _build_service(self, options):
        """Assemble the report service from the export options + app preferences."""
        settings_service = SettingsService()
        distance_setting = settings_service.get_setting('DistanceUnit', 'Feet')
        distance_unit = 'ft' if str(distance_setting).lower() in ('feet', 'ft') else 'm'
        return CombinedPdfReportService(
            organization=options.get_organization(),
            search_name=options.get_search_name(),
            include_images_without_flagged_aois=(
                options.get_include_images_without_flagged_aois()),
            map_tile_source=options.get_map_tile_source(),
            position_format=settings_service.get_setting(
                'PositionFormat', 'Lat/Long - Decimal Degrees'),
            distance_unit=distance_unit,
            use_terrain_elevation=settings_service.get_bool_setting(
                'UseTerrainElevation', True),
            recovery_session=self._recovery_session,
        )

    def _on_progress(self, current, total, message):
        if self.progress_dialog:
            self.progress_dialog.update_progress(current, total, message)
            QApplication.processEvents()

    def _on_success(self):
        if self.progress_dialog:
            self.progress_dialog.accept()
        QMessageBox.information(
            self.parent,
            self.tr("Export Complete"),
            self.tr("The combined PDF report was created."))

    def _on_error(self, error_message):
        if self.progress_dialog and self.progress_dialog.isVisible():
            self.progress_dialog.reject()
        QMessageBox.critical(
            self.parent,
            self.tr("Export Failed"),
            self.tr("Failed to generate combined PDF: {error}").format(
                error=error_message))

    def _on_cancelled(self):
        if self.progress_dialog and self.progress_dialog.isVisible():
            self.progress_dialog.reject()
