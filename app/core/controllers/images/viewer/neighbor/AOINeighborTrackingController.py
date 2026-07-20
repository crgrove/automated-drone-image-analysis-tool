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
from helpers.TranslationMixin import TranslationMixin


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


class AOINeighborTrackingController(TranslationMixin, QObject):
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

    def track_selected_aoi(self, image_idx=None, aoi_idx=None):
        """
        Track a selected AOI across neighboring images.

        Triggered by the Z key. When called with no arguments, the AOI is read
        from the single-image AOIController. When called with explicit
        `image_idx` / `aoi_idx`, those are used directly — this is the path
        used from gallery mode, where the selected AOI may belong to an image
        other than the one currently displayed in the main viewer.
        """
        try:
            if image_idx is not None and aoi_idx is not None:
                # Gallery-mode selection: resolve AOI from explicit indices
                if image_idx < 0 or image_idx >= len(self.parent.images):
                    return
                current_image = self.parent.images[image_idx]
                aois = current_image.get('areas_of_interest', [])
                if aoi_idx < 0 or aoi_idx >= len(aois):
                    return
                aoi_data = aois[aoi_idx]
                current_image_idx = image_idx
            else:
                # Single-image selection: read from the AOIController
                aoi_controller = self.parent.aoi_controller
                selected_aoi = aoi_controller.get_selected_aoi()

                if not selected_aoi:
                    QMessageBox.information(
                        self.parent,
                        self.tr("No AOI Selected"),
                        self.tr("Please select an AOI first by clicking on it in the thumbnail panel.")
                    )
                    return

                aoi_data, _ = selected_aoi
                current_image_idx = self.parent.current_image
                current_image = self.parent.images[current_image_idx]

            # Get altitude override if set
            agl_override_m = None
            if hasattr(self.parent, 'altitude_controller'):
                alt_ft = self.parent.altitude_controller.get_effective_altitude()
                if alt_ft and alt_ft > 0:
                    agl_override_m = alt_ft * 0.3048

            # Only reuse the viewer's cached pixel array when we're tracking
            # an AOI on the currently-displayed image; otherwise let
            # ImageService load the correct image from disk.
            if current_image_idx == self.parent.current_image:
                img_array = self.parent.current_image_array
            else:
                img_array = None

            # Calculate the GPS coordinates of the selected AOI.
            # estimate_aoi_gps returns an AOIGPSResult dataclass; the neighbor
            # service expects a plain (lat, lon) tuple, so convert here.
            # Honor the terrain-elevation preference like the AOI label does.
            use_terrain = getattr(self.parent, 'use_terrain_elevation', True)
            aoi_service = AOIService(current_image, img_array)
            aoi_gps_result = aoi_service.estimate_aoi_gps(current_image, aoi_data, agl_override_m, use_terrain)

            if not aoi_gps_result:
                QMessageBox.warning(
                    self.parent,
                    self.tr("Cannot Calculate GPS"),
                    self.tr(
                        "Unable to calculate GPS coordinates for this AOI.\n\n"
                        "This may be due to missing image metadata (GPS, altitude, or camera info)."
                    )
                )
                return

            aoi_gps = aoi_gps_result.to_tuple()

            # Show progress dialog
            self.progress_dialog = QProgressDialog(
                self.tr("Searching for AOI in neighboring images..."),
                self.tr("Cancel"),
                0, 0,
                self.parent
            )
            self.progress_dialog.setWindowTitle(self.tr("Tracking AOI"))
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
                self.tr("Tracking Error"),
                self.tr("An error occurred while tracking the AOI:\n{error}").format(
                    error=str(e)
                )
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
                    self.tr("No Neighbors Found"),
                    self.tr("The AOI was not found in any neighboring images.")
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
                self.tr("Search Error"),
                self.tr("An error occurred during the search:\n{error}").format(
                    error=error_msg
                )
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

            # Store results for later use when zooming
            self._neighbor_results = results

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
                self.tr("Display Error"),
                self.tr("An error occurred while displaying results:\n{error}").format(
                    error=str(e)
                )
            )

    def _on_gallery_image_clicked(self, image_idx):
        """
        Handle click on an image in the gallery.

        Navigates to the clicked image and zooms to the AOI location.

        Args:
            image_idx (int): Index of the clicked image
        """
        try:
            # Find the result data for this image to get pixel coordinates
            result = None
            if hasattr(self, '_neighbor_results') and self._neighbor_results:
                result = next((r for r in self._neighbor_results if r['image_idx'] == image_idx), None)

            pixel_x = result.get('pixel_x') if result else None
            pixel_y = result.get('pixel_y') if result else None

            # Check if we need to load a new image
            needs_load = (self.parent.current_image != image_idx)

            if needs_load and pixel_x is not None and pixel_y is not None:
                # Set up zoom-after-load using viewChanged signal pattern
                self.parent.current_image = image_idx

                zoom_handler = None
                zoom_executed = False

                def zoom_when_ready():
                    nonlocal zoom_executed
                    if zoom_executed:
                        return

                    viewer = self.parent.main_image
                    if not viewer or not viewer.hasImage():
                        return

                    # Check recursion guard
                    if hasattr(viewer, '_recursion_guard') and viewer._recursion_guard:
                        return

                    # Check zoom stack is cleared (resetZoom has been called)
                    if hasattr(viewer, 'zoomStack') and len(viewer.zoomStack) != 0:
                        return

                    zoom_executed = True
                    # Zoom to the AOI location (scale 6 matches AOI click behavior)
                    if hasattr(viewer, 'zoomToArea'):
                        viewer.zoomToArea((pixel_x, pixel_y), 6)

                    # Disconnect handler
                    if zoom_handler:
                        try:
                            viewer.viewChanged.disconnect(zoom_handler)
                        except Exception:
                            pass

                # Connect signal before loading
                connected_viewer = None
                if hasattr(self.parent, 'main_image') and self.parent.main_image:
                    try:
                        self.parent.main_image.viewChanged.connect(zoom_when_ready)
                        zoom_handler = zoom_when_ready
                        connected_viewer = self.parent.main_image
                    except Exception:
                        pass

                try:
                    # Load the image
                    self.parent._load_image()

                    # Fallback: if image already loaded and zoom not executed
                    if not zoom_executed and hasattr(self.parent, 'main_image'):
                        viewer = self.parent.main_image
                        if viewer and viewer.hasImage():
                            if not getattr(viewer, '_recursion_guard', False):
                                if not viewer.zoomStack:
                                    zoom_executed = True
                                    if hasattr(viewer, 'zoomToArea'):
                                        viewer.zoomToArea((pixel_x, pixel_y), 6)
                finally:
                    # _load_image() is synchronous, so any viewChanged it emits
                    # has already fired. Unconditionally drop the transient
                    # handler; a failed/early-returning load would otherwise
                    # leave it armed on viewChanged, where a later wheel zoom
                    # would re-enter zoomToArea against a stale location.
                    if zoom_handler is not None and connected_viewer is not None:
                        try:
                            connected_viewer.viewChanged.disconnect(zoom_handler)
                        except Exception:
                            pass
            else:
                # Simple navigation without zoom, or same image
                if needs_load:
                    self.parent.current_image = image_idx
                    self.parent._load_image()

                # If same image, still zoom to location
                if not needs_load and pixel_x is not None and pixel_y is not None:
                    viewer = self.parent.main_image
                    if viewer and hasattr(viewer, 'zoomToArea'):
                        viewer.zoomToArea((pixel_x, pixel_y), 6)

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
