"""
AOINeighborTrackingController - Controller for tracking AOIs across neighboring images.

Handles the logic for finding AOI appearances in neighboring images
and coordinating the display of results.
"""

from PySide6.QtCore import QObject, Signal, QThread
from PySide6.QtWidgets import QMessageBox, QProgressDialog, QApplication
from PySide6.QtCore import Qt

from core.services.image.AOINeighborService import AOINeighborService
from core.services.image.AOIService import AOIService
from core.services.LoggerService import LoggerService


class NeighborSearchWorker(QObject):
    """Worker thread for searching neighbor images."""

    progress = Signal(str)  # Progress message
    finished = Signal(list)  # Results list
    error = Signal(str)  # Error message

    def __init__(self, neighbor_service, images, current_image_idx, aoi_gps,
                 agl_override_m=None, thumbnail_radius=100):
        super().__init__()
        self.neighbor_service = neighbor_service
        self.images = images
        self.current_image_idx = current_image_idx
        self.aoi_gps = aoi_gps
        self.agl_override_m = agl_override_m
        self.thumbnail_radius = thumbnail_radius
        self._cancelled = False

    def cancel(self):
        """Cancel the search operation."""
        self._cancelled = True

    def run(self):
        """Execute the neighbor search."""
        try:
            if self._cancelled:
                self.finished.emit([])
                return

            results = self.neighbor_service.find_aoi_in_neighbors(
                images=self.images,
                current_image_idx=self.current_image_idx,
                aoi_gps=self.aoi_gps,
                agl_override_m=self.agl_override_m,
                thumbnail_radius=self.thumbnail_radius,
                progress_callback=lambda msg: self.progress.emit(msg) if not self._cancelled else None
            )

            if self._cancelled:
                self.finished.emit([])
            else:
                self.finished.emit(results)

        except Exception as e:
            self.error.emit(str(e))


class AOINeighborTrackingController(QObject):
    """Controller for tracking AOI appearances across neighboring images."""

    tracking_started = Signal()
    tracking_completed = Signal(list)  # List of neighbor results
    tracking_error = Signal(str)

    def __init__(self, parent):
        """
        Initialize the AOINeighborTrackingController.

        Args:
            parent: The parent viewer window
        """
        super().__init__(parent)
        self.parent = parent
        self.logger = LoggerService()
        self.neighbor_service = AOINeighborService()

        # Thread management
        self._worker = None
        self._thread = None

        # Dialog for displaying results
        self._gallery_dialog = None

    def track_selected_aoi(self):
        """
        Track the currently selected AOI across neighboring images.

        This method is triggered by the Z key.
        """
        try:
            # Get the currently selected AOI
            aoi_controller = self.parent.aoi_controller
            selected_aoi = aoi_controller.get_selected_aoi()

            if not selected_aoi:
                QMessageBox.information(
                    self.parent,
                    "No AOI Selected",
                    "Please select an AOI first by clicking on it in the thumbnail panel."
                )
                return

            aoi_data, aoi_index = selected_aoi

            # Get the current image
            current_image_idx = self.parent.current_image
            current_image = self.parent.images[current_image_idx]

            # Get altitude override if set
            agl_override_m = None
            if hasattr(self.parent, 'altitude_controller'):
                alt_ft = self.parent.altitude_controller.get_custom_altitude()
                if alt_ft and alt_ft > 0:
                    agl_override_m = alt_ft * 0.3048

            # Calculate the GPS coordinates of the selected AOI
            aoi_service = AOIService(current_image, self.parent.current_image_array)
            aoi_gps = aoi_service.estimate_aoi_gps(current_image, aoi_data, agl_override_m)

            if not aoi_gps:
                QMessageBox.warning(
                    self.parent,
                    "Cannot Calculate GPS",
                    "Unable to calculate GPS coordinates for this AOI.\n\n"
                    "This may be due to missing image metadata (GPS, altitude, or camera info)."
                )
                return

            # Show progress dialog
            self.progress_dialog = QProgressDialog(
                "Searching for AOI in neighboring images...",
                "Cancel",
                0, 0,
                self.parent
            )
            self.progress_dialog.setWindowTitle("Tracking AOI")
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.setMinimumDuration(0)
            self.progress_dialog.setValue(0)

            # Calculate thumbnail radius based on AOI size
            aoi_radius = aoi_data.get('radius', 50)
            thumbnail_radius = max(100, aoi_radius * 2)

            # Create worker and thread
            self._thread = QThread()
            self._worker = NeighborSearchWorker(
                neighbor_service=self.neighbor_service,
                images=self.parent.images,
                current_image_idx=current_image_idx,
                aoi_gps=aoi_gps,
                agl_override_m=agl_override_m,
                thumbnail_radius=thumbnail_radius
            )
            self._worker.moveToThread(self._thread)

            # Connect signals
            self._thread.started.connect(self._worker.run)
            self._worker.progress.connect(self._on_progress)
            self._worker.finished.connect(self._on_search_complete)
            self._worker.error.connect(self._on_search_error)
            self.progress_dialog.canceled.connect(self._on_cancelled)

            # Start the search
            self.tracking_started.emit()
            self._thread.start()

        except Exception as e:
            self.logger.error(f"Error starting AOI neighbor tracking: {e}")
            QMessageBox.critical(
                self.parent,
                "Tracking Error",
                f"An error occurred while tracking the AOI:\n{str(e)}"
            )

    def _on_progress(self, message):
        """Handle progress updates from the worker."""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.setLabelText(message)
            QApplication.processEvents()

    def _on_search_complete(self, results):
        """Handle search completion."""
        try:
            # Clean up thread
            self._cleanup_thread()

            # Close progress dialog
            if hasattr(self, 'progress_dialog') and self.progress_dialog:
                self.progress_dialog.close()
                self.progress_dialog = None

            if not results:
                QMessageBox.information(
                    self.parent,
                    "No Neighbors Found",
                    "The AOI was not found in any neighboring images."
                )
                return

            # Show the gallery dialog
            self._show_gallery_dialog(results)

            self.tracking_completed.emit(results)

        except Exception as e:
            self.logger.error(f"Error handling search completion: {e}")

    def _on_search_error(self, error_msg):
        """Handle search error."""
        try:
            # Clean up thread
            self._cleanup_thread()

            # Close progress dialog
            if hasattr(self, 'progress_dialog') and self.progress_dialog:
                self.progress_dialog.close()
                self.progress_dialog = None

            QMessageBox.critical(
                self.parent,
                "Search Error",
                f"An error occurred during the search:\n{error_msg}"
            )

            self.tracking_error.emit(error_msg)

        except Exception as e:
            self.logger.error(f"Error handling search error: {e}")

    def _on_cancelled(self):
        """Handle cancellation."""
        if self._worker:
            self._worker.cancel()
        self._cleanup_thread()

    def _cleanup_thread(self):
        """Clean up the worker thread."""
        if self._thread:
            self._thread.quit()
            self._thread.wait()
            self._thread = None
        self._worker = None

    def _show_gallery_dialog(self, results):
        """
        Show the gallery dialog with the found thumbnails.

        Args:
            results (list): List of neighbor results with thumbnails
        """
        try:
            # Import here to avoid circular imports
            from core.views.images.viewer.dialogs.AOINeighborGalleryDialog import AOINeighborGalleryDialog

            # Close existing dialog if open
            if self._gallery_dialog:
                self._gallery_dialog.close()

            # Create and show new dialog
            self._gallery_dialog = AOINeighborGalleryDialog(self.parent, results)
            self._gallery_dialog.image_clicked.connect(self._on_gallery_image_clicked)
            self._gallery_dialog.show()

        except Exception as e:
            self.logger.error(f"Error showing gallery dialog: {e}")
            QMessageBox.critical(
                self.parent,
                "Display Error",
                f"An error occurred while displaying results:\n{str(e)}"
            )

    def _on_gallery_image_clicked(self, image_idx):
        """
        Handle click on an image in the gallery.

        Args:
            image_idx (int): Index of the clicked image
        """
        try:
            # Navigate to the clicked image
            self.parent.current_image = image_idx
            self.parent._load_image()

            # Scroll thumbnail into view
            if hasattr(self.parent, 'thumbnail_controller') and self.parent.thumbnail_controller:
                if hasattr(self.parent.thumbnail_controller, 'ui_component') and self.parent.thumbnail_controller.ui_component:
                    self.parent.thumbnail_controller.ui_component.scroll_thumbnail_into_view()

        except Exception as e:
            self.logger.error(f"Error navigating to image: {e}")

    def cleanup(self):
        """Clean up resources."""
        self._cleanup_thread()
        if self._gallery_dialog:
            self._gallery_dialog.close()
            self._gallery_dialog = None
