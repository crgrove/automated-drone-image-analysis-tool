"""
CoverageExtentExportController - Handles coverage extent KML export.

Manages the export of geographic coverage extent for all images as KML files.
"""

from PySide6.QtWidgets import QMessageBox, QFileDialog, QApplication, QDialog
from PySide6.QtCore import QThread, Signal
from core.views.images.viewer.dialogs.ExportProgressDialog import ExportProgressDialog

from core.services.LoggerService import LoggerService
from core.services.image.CoverageExtentService import CoverageExtentService
from core.services.export.KMLGeneratorService import KMLGeneratorService


class CoverageExtentGenerationThread(QThread):
    """Thread for generating coverage extent KML files."""
    finished = Signal(dict)  # Emits coverage_data on success
    canceled = Signal()
    errorOccurred = Signal(str)
    progressUpdated = Signal(int, int, str)  # current, total, message

    def __init__(self, coverage_service, kml_service, images, output_path):
        """
        Initialize the coverage extent generation thread.

        Args:
            coverage_service (CoverageExtentService): Service for calculating coverage extents
            kml_service (KMLGeneratorService): Service for generating KML files
            images: List of image data
            output_path (str): The file path where the KML will be saved
        """
        super().__init__()
        self.coverage_service = coverage_service
        self.kml_service = kml_service
        self.images = images
        self.output_path = output_path
        self._is_canceled = False

    def run(self):
        """
        Execute the coverage extent calculation and KML generation.

        Calculates coverage extents, generates KML, and emits appropriate signals.
        """
        try:
            if not self._is_canceled:
                # Define progress callback
                def progress_callback(current, total, message):
                    if not self._is_canceled:
                        self.progressUpdated.emit(current, total, message)

                # Define cancel check
                def cancel_check():
                    return self._is_canceled

                # Calculate coverage extents
                coverage_data = self.coverage_service.calculate_coverage_extents(
                    self.images,
                    progress_callback=progress_callback,
                    cancel_check=cancel_check
                )

                # Check if cancelled
                if coverage_data.get('cancelled', False):
                    self.canceled.emit()
                    return

                # Check if we got valid data
                if coverage_data['image_count'] == 0:
                    # Still emit finished with the data so controller can show appropriate message
                    self.finished.emit(coverage_data)
                    return

                # Generate KML file
                if not self._is_canceled:
                    self.progressUpdated.emit(
                        len(self.images),
                        len(self.images),
                        "Generating KML file..."
                    )
                    self.kml_service.generate_coverage_extent_kml(coverage_data, self.output_path)

                if not self._is_canceled:
                    self.finished.emit(coverage_data)
                else:
                    self.canceled.emit()

        except Exception as e:
            self.errorOccurred.emit(str(e))

    def cancel(self):
        """
        Cancel the coverage extent generation process.

        Sets the cancellation flag and emits the canceled signal.
        """
        self._is_canceled = True


class CoverageExtentExportController:
    """
    Controller for exporting coverage extent KML files.

    Handles generation of KML files showing the geographic coverage extent
    of all images, with merged polygons for overlapping areas.
    """

    def __init__(self, parent_viewer, logger=None):
        """
        Initialize the coverage extent export controller.

        Args:
            parent_viewer: The main Viewer instance
            logger: Optional LoggerService instance
        """
        self.parent = parent_viewer
        self.logger = logger or LoggerService()
        self.coverage_thread = None
        self.progress_dialog = None

    def export_coverage_extent_kml(self):
        """Handle the export of coverage extent KML file for all images."""
        try:
            # Show confirmation dialog
            reply = QMessageBox.question(
                self.parent,
                "Generate Coverage Extent KML",
                "Generate a KML file showing the geographic coverage extent of all images?\n\n"
                "This will create polygon(s) representing the area covered by all images. "
                "Overlapping image areas will be merged into a single polygon.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply != QMessageBox.Yes:
                return

            # Show file save dialog
            file_name, _ = QFileDialog.getSaveFileName(
                self.parent,
                "Save Coverage Extent KML",
                "",
                "KML files (*.kml)"
            )

            if not file_name:  # User cancelled
                return

            # Create progress dialog
            self.progress_dialog = ExportProgressDialog(
                self.parent,
                title="Generating Coverage Extent KML",
                total_items=len(self.parent.images)
            )
            self.progress_dialog.set_title("Calculating coverage extent...")

            # Get custom altitude if available
            custom_alt = None
            if hasattr(self.parent, 'altitude_controller'):
                custom_alt = self.parent.altitude_controller.get_effective_altitude()

            coverage_service = CoverageExtentService(custom_altitude_ft=custom_alt, logger=self.logger)
            kml_service = KMLGeneratorService(custom_altitude_ft=custom_alt)

            # Create and configure thread
            self.coverage_thread = CoverageExtentGenerationThread(
                coverage_service,
                kml_service,
                self.parent.images,
                file_name
            )

            # Connect signals
            self.coverage_thread.finished.connect(
                lambda coverage_data: self._on_generation_finished(coverage_data, file_name)
            )
            self.coverage_thread.canceled.connect(self._on_generation_cancelled)
            self.coverage_thread.errorOccurred.connect(self._on_generation_error)
            self.coverage_thread.progressUpdated.connect(self._on_progress_updated)

            # Connect cancel button
            self.progress_dialog.cancel_requested.connect(self.coverage_thread.cancel)

            # Start thread
            self.coverage_thread.start()

            # Show progress dialog
            self.progress_dialog.show()
            QApplication.processEvents()

            # Block until finished
            if self.progress_dialog.exec() == QDialog.Rejected:
                self.coverage_thread.cancel()

        except Exception as e:
            self.logger.error(f"Error generating coverage extent KML: {str(e)}")
            self.parent.status_controller.show_toast("Error generating coverage extent KML", 3000, color="#F44336")
            QMessageBox.critical(
                self.parent,
                "Error",
                f"Failed to generate coverage extent KML:\n{str(e)}"
            )

    def _on_progress_updated(self, current, total, message):
        """Handle progress updates from the generation thread."""
        if self.progress_dialog:
            self.progress_dialog.update_progress(current, total, message)
            QApplication.processEvents()

    def _on_generation_finished(self, coverage_data, file_name):
        """Handle successful completion of coverage extent generation."""
        if self.progress_dialog:
            self.progress_dialog.accept()

        # Check if no valid images were found
        if coverage_data['image_count'] == 0:
            self._show_no_valid_images_error(coverage_data)
            return

        # Show success message
        self._show_success_message(coverage_data, file_name)

    def _on_generation_cancelled(self):
        """Handle cancellation of coverage extent generation."""
        if self.coverage_thread and self.coverage_thread.isRunning():
            self.coverage_thread.terminate()
            self.coverage_thread.wait()
        if self.progress_dialog and self.progress_dialog.isVisible():
            self.progress_dialog.reject()
        self.parent.status_controller.show_toast("Coverage extent generation cancelled", 3000, color="#FF9800")

    def _on_generation_error(self, error_message):
        """Handle errors during coverage extent generation."""
        if self.progress_dialog and self.progress_dialog.isVisible():
            self.progress_dialog.reject()
        self.logger.error(f"Coverage extent generation error: {error_message}")
        self.parent.status_controller.show_toast("Error generating coverage extent", 3000, color="#F44336")
        QMessageBox.critical(
            self.parent,
            "Error",
            f"Failed to generate coverage extent KML:\n{error_message}"
        )

    def _show_no_valid_images_error(self, coverage_data):
        """Show error when no valid images are found."""
        self.parent.status_controller.show_toast(
            "No valid images found for coverage extent calculation",
            3000,
            color="#F44336"
        )
        QMessageBox.warning(
            self.parent,
            "Coverage Extent",
            f"Could not calculate coverage extent.\n\n"
            f"Images processed: {coverage_data['image_count']}\n"
            f"Images skipped: {coverage_data['skipped_count']}\n\n"
            f"Images may be skipped for the following reasons:\n"
            f"  • Missing GPS data in EXIF\n"
            f"  • No valid GSD (missing altitude/focal length)\n"
            f"  • Gimbal not nadir (must be -85° to -95°)"
        )

    def _show_success_message(self, coverage_data, file_name):
        """Show success message with coverage statistics."""
        total_area_sqm = coverage_data['total_area_sqm']
        num_polygons = len(coverage_data['polygons'])

        # Honor user's distance unit preference
        if self.parent.distance_unit == 'ft':
            # English units - use acres
            total_area_acres = total_area_sqm / 4046.86  # 1 acre = 4046.86 m²
            area_display = f"{total_area_acres:.2f} acres"
            area_toast = f"{total_area_acres:.2f} acres"
        else:
            # Metric units - use km²
            total_area_sqkm = total_area_sqm / 1_000_000
            area_display = f"{total_area_sqkm:.3f} km²"
            area_toast = f"{total_area_sqkm:.3f} km²"

        self.parent.status_controller.show_toast(
            f"Coverage extent KML saved: {area_toast}",
            4000,
            color="#00C853"
        )

        # Build skip reasons explanation if any were skipped
        skip_info = ""
        if coverage_data['skipped_count'] > 0:
            skip_info = (
                "\n\nImages may be skipped for:\n"
                "  • Missing GPS data\n"
                "  • No valid GSD\n"
                "  • Gimbal not nadir"
            )

        QMessageBox.information(
            self.parent,
            "Coverage Extent KML Generated",
            f"Coverage extent KML file created successfully!\n\n"
            f"File: {file_name}\n"
            f"Images processed: {coverage_data['image_count']}\n"
            f"Images skipped: {coverage_data['skipped_count']}\n"
            f"Coverage areas: {num_polygons}\n"
            f"Total area: {area_display}{skip_info}"
        )
