"""
PDFExportController - Handles PDF report generation for the image viewer.

This controller manages the export of flagged AOIs to PDF format with
background processing and progress tracking.
"""

from PySide6.QtWidgets import QFileDialog, QDialog, QMessageBox, QApplication, QWidget
from PySide6.QtCore import QThread, Signal
from core.views.images.viewer.dialogs.ExportProgressDialog import ExportProgressDialog
from helpers.TranslationMixin import TranslationMixin
from core.views.images.viewer.dialogs.PDFExportDialog import PDFExportDialog
from core.services.export.PdfGeneratorService import PdfGeneratorService
from core.services.LoggerService import LoggerService


class PdfGenerationThread(QThread):
    """Thread for generating the PDF report."""
    success = Signal()  # Renamed from 'finished' to avoid conflict with QThread.finished
    canceled = Signal()
    errorOccurred = Signal(str)
    progressUpdated = Signal(int, int, str)  # current, total, message

    def __init__(self, pdf_generator, output_path):
        """Initializes the PdfGenerationThread.

        Args:
            pdf_generator (PdfGeneratorService): The PDF generator instance responsible for creating the report.
            output_path (str): The file path where the generated PDF will be saved.
        """
        super().__init__()
        self.pdf_generator = pdf_generator
        self.output_path = output_path
        self._is_canceled = False

    def run(self):
        """Executes the PDF generation process.

        If the process is not canceled, it generates the PDF report and emits
        the `finished` signal upon successful completion.
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

                error_message = self.pdf_generator.generate_report(
                    self.output_path,
                    progress_callback=progress_callback,
                    cancel_check=cancel_check
                )
                if error_message:
                    self.errorOccurred.emit(error_message)  # Emit error if there's an error message
                else:
                    self.success.emit()  # Emit success if successful
        except Exception as e:
            self.errorOccurred.emit(str(e))  # Emit error if an exception occurs

    def cancel(self):
        """Cancels the PDF generation process.

        Sets the `_is_canceled` flag to True and emits the `canceled` signal.
        """
        self._is_canceled = True
        self.canceled.emit()


class PDFExportController(TranslationMixin):
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

            # Get settings from dialog
            organization = settings_dialog.get_organization()
            search_name = settings_dialog.get_search_name()
            include_images_without_flagged_aois = settings_dialog.get_include_images_without_flagged_aois()

            # Filter images based on user preference to check if there are any images to export
            original_images = images
            filtered_images = []

            for idx, img in enumerate(images):
                if not img.get("hidden", False):
                    # Create a copy of the image data
                    img_copy = img.copy()
                    # Check if this image has flagged AOIs
                    has_flagged_aois = idx in flagged_aois and len(flagged_aois[idx]) > 0

                    if has_flagged_aois:
                        # This image has flagged AOIs - filter to only include flagged ones
                        flagged_indices = flagged_aois[idx]
                        filtered_aois = [
                            aoi for i, aoi in enumerate(img['areas_of_interest'])
                            if i in flagged_indices
                        ]
                        img_copy['areas_of_interest'] = filtered_aois

                        # Always include images with flagged AOIs
                        filtered_images.append(img_copy)
                    else:
                        # This image has NO flagged AOIs
                        if include_images_without_flagged_aois:
                            # Include image with ALL its AOIs
                            filtered_images.append(img_copy)

            # Check if there are any images to export BEFORE showing file dialog
            if not filtered_images:
                if include_images_without_flagged_aois:
                    QMessageBox.warning(
                        self.parent,
                        self.tr("No Images to Export"),
                        self.tr(
                            "There are no images available to include in the PDF report.\n\n"
                            "All images may be hidden or there are no images in the dataset."
                        )
                    )
                else:
                    QMessageBox.warning(
                        self.parent,
                        self.tr("No Images to Export"),
                        self.tr(
                            "There are no images with flagged AOIs to include in the PDF report.\n\n"
                            "Please flag at least one AOI, or check 'Include images without flagged AOIs' "
                            "to include all images in the report."
                        )
                    )
                return False

            # Open file dialog for PDF export
            file_name, _ = QFileDialog.getSaveFileName(
                self.parent,
                self.tr("Save PDF File"),
                "",
                self.tr("PDF files (*.pdf)")
            )

            if not file_name:  # User cancelled
                return False

            # Create PDF generator with filtered images
            pdf_generator = PdfGeneratorService(
                self.parent,
                organization=organization,
                search_name=search_name,
                images=filtered_images,
                include_images_without_flagged_aois=include_images_without_flagged_aois,
            )

            # Store all images for map generation
            pdf_generator.all_images_for_map = original_images

            # Count total flagged AOIs for progress dialog
            total_aois = sum(len(img.get('areas_of_interest', [])) for img in filtered_images)

            # Validate parent widget - ensure it's a valid QWidget instance
            # This prevents access violations in test environments where the parent
            # might not be fully initialized or might be a mock object
            parent_widget = self.parent
            if parent_widget is not None:
                # Check if it's a valid QWidget and not deleted
                if not isinstance(parent_widget, QWidget):
                    parent_widget = None
                else:
                    # Additional check: ensure widget is not deleted
                    try:
                        # Try to access a property that requires valid widget
                        _ = parent_widget.isWidgetType()
                    except (RuntimeError, AttributeError):
                        # Widget has been deleted or is invalid
                        parent_widget = None

            # Create and show the progress dialog
            self.progress_dialog = ExportProgressDialog(
                parent_widget,
                title=self.tr("Generating PDF Report"),
                total_items=total_aois
            )
            self.progress_dialog.set_title(self.tr("Generating PDF Report..."))

            # Disconnect old thread signals if it exists
            if self.pdf_thread is not None:
                try:
                    self.pdf_thread.success.disconnect()
                    self.pdf_thread.canceled.disconnect()
                    self.pdf_thread.errorOccurred.disconnect()
                    self.pdf_thread.progressUpdated.disconnect()
                except Exception:
                    pass  # Ignore if already disconnected

            # Create PDF generation thread
            self.pdf_thread = PdfGenerationThread(pdf_generator, file_name)

            # Connect signals
            self.pdf_thread.success.connect(self._on_pdf_generation_finished)
            self.pdf_thread.canceled.connect(self._on_pdf_generation_cancelled)
            self.pdf_thread.errorOccurred.connect(self._on_pdf_generation_error)
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
            self.logger.error(f"Error generating PDF file: {str(e)}")
            self._show_error(
                self.tr("Failed to generate PDF file: {error}").format(error=str(e))
            )
            return False

    def _on_progress_updated(self, current, total, message):
        """Handles progress updates from the PDF generation thread."""
        if self.progress_dialog:
            self.progress_dialog.update_progress(current, total, message)
            QApplication.processEvents()  # Keep UI responsive

    def _on_pdf_generation_finished(self):
        """Handles successful completion of PDF generation."""
        if self.progress_dialog:
            self.progress_dialog.accept()
        QMessageBox.information(
            self.parent,
            self.tr("Success"),
            self.tr("PDF report generated successfully!")
        )

    def _on_pdf_generation_cancelled(self):
        """Handles cancellation of PDF generation."""
        if self.pdf_thread and self.pdf_thread.isRunning():
            self.pdf_thread.terminate()  # Forcefully terminate the thread
            self.pdf_thread.wait()      # Wait for the thread to terminate completely
        # Close the progress dialog
        if self.progress_dialog and self.progress_dialog.isVisible():
            self.progress_dialog.reject()  # Close the dialog

    def _on_pdf_generation_error(self, error_message):
        """Handles errors during PDF generation."""
        if self.progress_dialog and self.progress_dialog.isVisible():
            self.progress_dialog.reject()  # Close the progress dialog
        self._show_error(
            self.tr("PDF generation failed: {error}").format(error=error_message)
        )

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
            QMessageBox.critical(self.parent, self.tr("Error"), text)
