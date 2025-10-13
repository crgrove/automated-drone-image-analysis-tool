"""
KMLExportController - Handles KML file generation for the image viewer.

This controller manages the export of flagged AOIs to KML format for use in
geographic applications like Google Earth.
"""

from PySide6.QtWidgets import QFileDialog, QMessageBox, QDialog, QApplication
from core.controllers.viewer.exports.KMLGenerationThread import KMLGenerationThread
from core.views.viewer.dialogs.ExportProgressDialog import ExportProgressDialog
from core.services.KMLGeneratorService import KMLGeneratorService
from core.services.LoggerService import LoggerService


class KMLExportController:
    """
    Controller for managing KML export functionality.

    Handles the export of flagged AOIs to KML format, filtering images
    and AOIs based on flag status.
    """

    def __init__(self, parent_widget, logger=None):
        """
        Initialize the KML export controller.

        Args:
            parent_widget: The parent widget for dialogs
            logger: Optional logger instance for error reporting
        """
        self.parent = parent_widget
        self.logger = logger or LoggerService()
        self.kml_thread = None
        self.progress_dialog = None

    def export_kml(self, images, flagged_aois):
        """
        Export flagged AOIs to KML format.

        Args:
            images: List of image data dictionaries
            flagged_aois: Dictionary mapping image indices to sets of flagged AOI indices

        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            # Open file dialog for KML export
            file_name, _ = QFileDialog.getSaveFileName(
                self.parent,
                "Save KML File",
                "",
                "KML files (*.kml)"
            )

            if not file_name:  # User cancelled
                return False

            # Filter images and their AOIs based on flags
            filtered_images = []
            for idx, img in enumerate(images):
                if not img.get("hidden", False):
                    # Create a copy of the image data
                    img_copy = img.copy()

                    # Filter AOIs to only include flagged ones
                    if idx in flagged_aois and flagged_aois[idx]:
                        flagged_indices = flagged_aois[idx]
                        filtered_aois = [
                            aoi for i, aoi in enumerate(img['areas_of_interest'])
                            if i in flagged_indices
                        ]
                        img_copy['areas_of_interest'] = filtered_aois

                        # Only include image if it has flagged AOIs
                        if filtered_aois:
                            filtered_images.append(img_copy)

            if not filtered_images:
                self._show_toast("No flagged AOIs to export", 3000, color="#F44336")
                return False

            # Get custom altitude if viewer has one set
            custom_alt = None
            if hasattr(self.parent, 'custom_agl_altitude_ft') and self.parent.custom_agl_altitude_ft and self.parent.custom_agl_altitude_ft > 0:
                custom_alt = self.parent.custom_agl_altitude_ft

            # Count total flagged AOIs for progress dialog
            total_aois = 0
            for img in filtered_images:
                aois = img.get('areas_of_interest', [])
                total_aois += sum(1 for aoi in aois if aoi.get('flagged', False))

            # Create KML generator service
            kml_service = KMLGeneratorService(custom_altitude_ft=custom_alt)

            # Create and show progress dialog
            self.progress_dialog = ExportProgressDialog(
                self.parent,
                title="Generating KML File",
                total_items=total_aois
            )
            self.progress_dialog.set_title("Exporting KML...")

            # Create KML generation thread
            self.kml_thread = KMLGenerationThread(kml_service, filtered_images, file_name)

            # Connect signals
            self.kml_thread.finished.connect(self._on_kml_generation_finished)
            self.kml_thread.canceled.connect(self._on_kml_generation_cancelled)
            self.kml_thread.errorOccurred.connect(self._on_kml_generation_error)
            self.kml_thread.progressUpdated.connect(self._on_progress_updated)

            # Connect cancel button
            self.progress_dialog.cancel_requested.connect(self.kml_thread.cancel)

            # Start the thread
            self.kml_thread.start()

            # Show progress dialog
            self.progress_dialog.show()
            QApplication.processEvents()

            # Block until finished
            if self.progress_dialog.exec() == QDialog.Rejected:
                self.kml_thread.cancel()

            return True

        except Exception as e:
            self.logger.error(f"Error generating KML file: {str(e)}")
            self._show_error(f"Failed to generate KML file: {str(e)}")
            return False

    def _on_progress_updated(self, current, total, message):
        """Handle progress updates from the KML generation thread."""
        if self.progress_dialog:
            self.progress_dialog.update_progress(current, total, message)
            QApplication.processEvents()

    def _on_kml_generation_finished(self):
        """Handle successful completion of KML generation."""
        if self.progress_dialog:
            self.progress_dialog.accept()
        self._show_toast("KML file exported successfully!", 3000, color="#00C853")

    def _on_kml_generation_cancelled(self):
        """Handle cancellation of KML generation."""
        if self.kml_thread and self.kml_thread.isRunning():
            self.kml_thread.terminate()
            self.kml_thread.wait()
        if self.progress_dialog and self.progress_dialog.isVisible():
            self.progress_dialog.reject()
        self._show_toast("KML export cancelled", 3000, color="#FFA726")

    def _on_kml_generation_error(self, error_message):
        """Handle errors during KML generation."""
        if self.progress_dialog and self.progress_dialog.isVisible():
            self.progress_dialog.reject()
        self._show_error(f"KML generation failed: {error_message}")

    def _show_toast(self, text, msec=3000, color="#00C853"):
        """Show a toast message if the parent has this method."""
        if hasattr(self.parent, '_show_toast'):
            self.parent._show_toast(text, msec, color)

    def _show_error(self, text):
        """Show an error message if the parent has this method."""
        if hasattr(self.parent, '_show_error'):
            self.parent._show_error(text)
        else:
            # Fallback to message box
            QMessageBox.critical(self.parent, "Error", text)
