"""
ZipExportController - Handles ZIP file generation for the image viewer.

This controller manages the export of image files to ZIP format for
easy distribution and archiving.
"""

from PySide6.QtWidgets import QFileDialog, QMessageBox
from core.services.ZipBundleService import ZipBundleService
from core.services.LoggerService import LoggerService


class ZipExportController:
    """
    Controller for managing ZIP export functionality.

    Handles the export of image files to ZIP format, filtering out
    hidden images from the bundle.
    """

    def __init__(self, parent_widget, logger=None):
        """
        Initialize the ZIP export controller.

        Args:
            parent_widget: The parent widget for dialogs
            logger: Optional logger instance for error reporting
        """
        self.parent = parent_widget
        self.logger = logger or LoggerService()

    def export_zip(self, images):
        """
        Export image files to ZIP format.

        Args:
            images: List of image data dictionaries

        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            # Open file dialog for ZIP export
            file_name, _ = QFileDialog.getSaveFileName(
                self.parent,
                "Save Zip File",
                "",
                "Zip files (*.zip)"
            )

            if not file_name:  # User cancelled
                return False

            # Filter out hidden images
            file_paths = [img['path'] for img in images if not img.get('hidden', False)]

            if not file_paths:
                self._show_toast("No images to export", 3000, color="#F44336")
                return False

            zip_generator = ZipBundleService()
            zip_generator.generate_zip_file(file_paths, file_name)

            self._show_toast(f"ZIP file created with {len(file_paths)} images", 3000, color="#00C853")
            return True

        except Exception as e:
            self.logger.error(f"Error generating Zip file: {str(e)}")
            self._show_error(f"Failed to generate Zip file: {str(e)}")
            return False

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
