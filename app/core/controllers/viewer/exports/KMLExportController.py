"""
KMLExportController - Handles KML file generation for the image viewer.

This controller manages the export of flagged AOIs to KML format for use in
geographic applications like Google Earth.
"""

from PySide6.QtWidgets import QFileDialog, QMessageBox
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

            if filtered_images:
                kml_service = KMLGeneratorService()
                kml_service.generate_kml_export(filtered_images, file_name)
                return True
            else:
                self._show_toast("No flagged AOIs to export", 3000, color="#F44336")
                return False

        except Exception as e:
            self.logger.error(f"Error generating KML file: {str(e)}")
            self._show_error(f"Failed to generate KML file: {str(e)}")
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
