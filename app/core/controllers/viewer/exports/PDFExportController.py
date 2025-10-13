"""
PDFExportController - Handles PDF report generation for the image viewer.

This controller manages the export of flagged AOIs to PDF format with
background processing and progress tracking.
"""

from PySide6.QtWidgets import QFileDialog, QDialog, QMessageBox, QApplication
from core.controllers.viewer.exports.PdfGenerationThread import PdfGenerationThread
from core.views.viewer.dialogs.ExportProgressDialog import ExportProgressDialog
from core.views.viewer.dialogs.PDFExportDialog import PDFExportDialog
from core.services.PdfGeneratorService import PdfGeneratorService
from core.services.LoggerService import LoggerService


class PDFExportController:
    """
    Controller for managing PDF export functionality.

    Handles the export of flagged AOIs to PDF format with background
    processing, progress tracking, and cancellation support.
    """

    def __init__(self, parent_widget, logger=None):
        """
        Initialize the PDF export controller.

        Args:
            parent_widget: The parent widget for dialogs
            logger: Optional logger instance for error reporting
        """
        self.parent = parent_widget
        self.logger = logger or LoggerService()
        self.pdf_thread = None
        self.progress_dialog = None

    def export_pdf(self, images, flagged_aois):
        """
        Export flagged AOIs to PDF format.

        Args:
            images: List of image data dictionaries
            flagged_aois: Dictionary mapping image indices to sets of flagged AOI indices

        Returns:
            bool: True if export was initiated successfully, False otherwise
        """
        try:
            # Show settings dialog first
            settings_dialog = PDFExportDialog(self.parent)
            if settings_dialog.exec() != QDialog.Accepted:
                return False  # User cancelled

            # Get organization and search name from dialog
            organization = settings_dialog.get_organization()
            search_name = settings_dialog.get_search_name()

            # Open file dialog for PDF export
            file_name, _ = QFileDialog.getSaveFileName(
                self.parent,
                "Save PDF File",
                "",
                "PDF files (*.pdf)"
            )

            if not file_name:  # User cancelled
                return False

            # Filter images to only include those with flagged AOIs
            original_images = images
            filtered_images = []

            for idx, img in enumerate(images):
                if not img.get("hidden", False):
                    # Check if this image has flagged AOIs
                    if idx in flagged_aois and flagged_aois[idx]:
                        # Create a copy of the image data with only flagged AOIs
                        img_copy = img.copy()
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
                self._show_toast("No flagged AOIs to include in PDF", 3000, color="#F44336")
                return False

            # Create PDF generator with both all images and filtered images
            pdf_generator = PdfGeneratorService(self.parent, organization=organization, search_name=search_name)

            # Store all images for map generation
            pdf_generator.all_images_for_map = original_images

            # Temporarily replace images with filtered version for PDF generation
            self.parent.images = filtered_images

            # Count total flagged AOIs for progress dialog
            total_aois = sum(len(img.get('areas_of_interest', [])) for img in filtered_images)

            # Create and show the progress dialog
            self.progress_dialog = ExportProgressDialog(
                self.parent,
                title="Generating PDF Report",
                total_items=total_aois
            )
            self.progress_dialog.set_title("Generating PDF Report...")
            
            # Create PDF generation thread
            self.pdf_thread = PdfGenerationThread(pdf_generator, file_name)

            # Connect signals
            self.pdf_thread.finished.connect(
                lambda: self._on_pdf_generation_finished(original_images)
            )
            self.pdf_thread.canceled.connect(
                lambda: self._on_pdf_generation_cancelled(original_images)
            )
            self.pdf_thread.errorOccurred.connect(
                lambda e: self._on_pdf_generation_error(e, original_images)
            )
            self.pdf_thread.progressUpdated.connect(
                self._on_progress_updated
            )

            # Connect cancel button to thread
            self.progress_dialog.cancel_requested.connect(self.pdf_thread.cancel)

            self.pdf_thread.start()

            # Show the progress dialog
            self.progress_dialog.show()
            QApplication.processEvents()  # Make dialog visible immediately

            # Use exec to block until finished
            if self.progress_dialog.exec() == QDialog.Rejected:
                self.pdf_thread.cancel()

            return True

        except Exception as e:
            # Restore original images in case of error
            if 'original_images' in locals():
                self.parent.images = original_images
            self.logger.error(f"Error generating PDF file: {str(e)}")
            self._show_error(f"Failed to generate PDF file: {str(e)}")
            return False

    def _on_progress_updated(self, current, total, message):
        """Handles progress updates from the PDF generation thread."""
        if self.progress_dialog:
            self.progress_dialog.update_progress(current, total, message)
            QApplication.processEvents()  # Keep UI responsive

    def _on_pdf_generation_finished(self, original_images=None):
        """Handles successful completion of PDF generation."""
        if original_images is not None:
            self.parent.images = original_images
        if self.progress_dialog:
            self.progress_dialog.accept()
        QMessageBox.information(self.parent, "Success", "PDF report generated successfully!")

    def _on_pdf_generation_cancelled(self, original_images=None):
        """Handles cancellation of PDF generation."""
        if original_images is not None:
            self.parent.images = original_images
        if self.pdf_thread and self.pdf_thread.isRunning():
            self.pdf_thread.terminate()  # Forcefully terminate the thread
            self.pdf_thread.wait()      # Wait for the thread to terminate completely
        # Close the progress dialog
        if self.progress_dialog and self.progress_dialog.isVisible():
            self.progress_dialog.reject()  # Close the dialog

    def _on_pdf_generation_error(self, error_message, original_images=None):
        """Handles errors during PDF generation."""
        if original_images is not None:
            self.parent.images = original_images
        if self.progress_dialog and self.progress_dialog.isVisible():
            self.progress_dialog.reject()  # Close the progress dialog
        self._show_error(f"PDF generation failed: {error_message}")

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
