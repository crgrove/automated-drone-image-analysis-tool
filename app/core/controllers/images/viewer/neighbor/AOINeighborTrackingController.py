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
from helpers.PathHelper import path_match_key


class NeighborSearchWorker(QObject):
    """Worker thread for searching neighbor images.

    Owns the AOI's own GPS calculation as well as the search. That calculation
    decodes the source image and can query a DEM over the network, so on the
    GUI thread it froze the window for seconds -- and did so *before* the
    progress dialog could paint, which is the worst place for it: the user has
    pressed Z and has no indication anything is happening.
    """

    # The generation rides in the signal rather than being bound into a lambda
    # at connect time. A lambda has no receiver QObject, so Qt cannot use the
    # controller's thread affinity and resolves the connection as Direct: the
    # handler then ran ON THE WORKER THREAD, where _cleanup_thread waits on the
    # very thread it is running on and the dialog calls touch GUI objects from
    # the wrong thread. That deadlocked the app at the last image of the search.
    # Bound methods of the controller keep the connection queued to the GUI thread.
    progress = Signal(str)               # Progress message
    finished = Signal(list, bool, int)   # Results, cap-truncated, generation
    error = Signal(str, int)             # Error message, generation
    gps_unavailable = Signal(int)        # The AOI's own GPS is not computable

    def __init__(self, neighbor_service, images, current_image_idx,
                 current_image, aoi_data, img_array=None, use_terrain=True,
                 agl_override_m=None, thumbnail_radius=100, generation=0):
        super().__init__()
        self.generation = generation
        self.neighbor_service = neighbor_service
        self.images = images
        self.current_image_idx = current_image_idx
        self.current_image = current_image
        self.aoi_data = aoi_data
        self.img_array = img_array
        self.use_terrain = use_terrain
        self.agl_override_m = agl_override_m
        self.thumbnail_radius = thumbnail_radius
        self._cancelled = False

    def cancel(self):
        """Cancel the search operation."""
        self._cancelled = True

    def run(self):
        """Compute the AOI's GPS, then find it in the other captures."""
        try:
            if self._cancelled:
                self.finished.emit([], False, self.generation)
                return

            self.progress.emit(self.tr("Locating the selected AOI..."))
            aoi_service = AOIService(self.current_image, self.img_array)
            aoi_gps_result = aoi_service.estimate_aoi_gps(
                self.current_image, self.aoi_data,
                self.agl_override_m, self.use_terrain
            )
            if aoi_gps_result is None:
                self.gps_unavailable.emit(self.generation)
                return

            if self._cancelled:
                self.finished.emit([], False, self.generation)
                return

            results, truncated = self.neighbor_service.find_aoi_in_neighbors(
                images=self.images,
                current_image_idx=self.current_image_idx,
                aoi_gps=aoi_gps_result.to_tuple(),
                agl_override_m=self.agl_override_m,
                thumbnail_radius=self.thumbnail_radius,
                # The ground elevation the forward calculation settled on, so
                # each candidate is projected from its height above THAT point
                # rather than above its own.
                aoi_terrain_elevation_m=aoi_gps_result.terrain_elevation_m,
                # Actually stops the search. cancel() used to only set a flag
                # that nothing read, so a cancelled search ran to completion.
                should_cancel=lambda: self._cancelled,
                progress_callback=lambda msg: self.progress.emit(msg) if not self._cancelled else None
            )

            if self._cancelled:
                self.finished.emit([], False, self.generation)
            else:
                self.finished.emit(results, truncated, self.generation)

        except Exception as e:
            self.error.emit(str(e), self.generation)


class AOINeighborTrackingController(TranslationMixin, QObject):
    """Controller for tracking AOI appearances across neighboring images."""

    tracking_started = Signal()
    tracking_completed = Signal(list)  # List of neighbor results
    tracking_error = Signal(str)

    # Half-width of the crop taken around the projected point, in pixels of
    # the source image. Covers the inter-image metadata disagreement measured
    # on real flights (see track_selected_aoi), so the AOI is inside the
    # thumbnail even though the projected centre is off by metres.
    UNCERTAINTY_RADIUS_PX = 400

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
        self._cancelled = False
        # Bumped whenever a search is retired. A cancelled worker is still
        # running and still connected, and its queued `finished` arrives after
        # the next search has started; without a generation stamp that late
        # signal tore down the NEW thread and reported "No Neighbors Found"
        # for a search that was still running.
        self._generation = 0
        # Threads still winding down, kept alive until Qt reports them
        # stopped. See _cleanup_thread for why this must not be skipped.
        self._retiring = {}
        # Reentrancy state: a modal QProgressDialog can pump the event loop, so
        # terminal handlers can arrive while _on_progress is mid-body.
        self._in_progress_update = False
        self._deferred = None

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
            # One search at a time. Without this, a second Z press while a
            # search is running reassigns self._thread and drops the last
            # Python reference to a *running* QThread. ~QThread() answers that
            # with qFatal(), which abort()s the process immediately -- the
            # whole application dies with no Python traceback. A reentrant
            # press is easy to produce: key auto-repeat, or an event loop
            # re-entered from inside a slot.
            if self._thread is not None:
                return

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

            # Honor the terrain-elevation preference like the AOI label does.
            # The AOI's own GPS is computed on the worker thread (see
            # NeighborSearchWorker.run): it decodes the source image and can
            # query a DEM over the network, and doing that here froze the
            # window before the progress dialog below could even paint.
            use_terrain = getattr(self.parent, 'use_terrain_elevation', True)

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
            # Own the dialog's lifetime explicitly; see AOISimilarityController.
            self.progress_dialog.setAutoClose(False)
            self.progress_dialog.setAutoReset(False)
            self.progress_dialog.setValue(0)

            # Size the crop to the POSITIONAL UNCERTAINTY, not to the AOI.
            #
            # The projection is only as good as each image's own gimbal/GPS
            # metadata, and neighbouring captures disagree about where the same
            # ground object is. Measured on a real DJI flight: the same tarp
            # placed 1.5 m apart by adjacent frames, rising to ~4 m five frames
            # out. At the 1.33 cm/px GSD of that flight, 4 m is ~300 px.
            #
            # A radius derived from the AOI (max(100, radius*2) = 100 px here)
            # produced a 200 px crop covering 2.7 m of ground -- narrower than
            # the error -- so the object sat just outside almost every
            # thumbnail and the whole gallery looked like bare ground. The
            # crop has to be wide enough that the AOI is inside it even when
            # the metadata is off by metres; the red circle marks the
            # projected point, and the reviewer's eye finds the object near it.
            aoi_radius = aoi_data.get('radius', 50)
            thumbnail_radius = max(self.UNCERTAINTY_RADIUS_PX, aoi_radius * 2)

            # Search the full flight, not just the AOI-bearing subset from the
            # XML: an image that produced no detections of its own can still
            # show this AOI. Viewer.source_images already holds every capture
            # from the original flight folder.
            search_images, search_idx = self._build_search_scope(current_image, current_image_idx)

            # Create worker and thread
            self._cancelled = False
            self._thread = QThread()
            self._worker = NeighborSearchWorker(
                neighbor_service=self.neighbor_service,
                images=search_images,
                current_image_idx=search_idx,
                current_image=current_image,
                aoi_data=aoi_data,
                img_array=img_array,
                use_terrain=use_terrain,
                agl_override_m=agl_override_m,
                thumbnail_radius=thumbnail_radius,
                generation=self._generation,
            )
            self._worker.moveToThread(self._thread)

            # Connect signals. The terminal handlers carry the generation this
            # search was started with, so a previous worker's late signal is
            # recognised as stale instead of acting on the current search.
            self._thread.started.connect(self._worker.run)
            self._worker.progress.connect(self._on_progress)
            self._worker.finished.connect(self._on_search_complete)
            self._worker.error.connect(self._on_search_error)
            self._worker.gps_unavailable.connect(self._on_gps_unavailable)
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

    def _build_search_scope(self, current_image, current_image_idx):
        """Choose the image list to search and locate the current image in it.

        Returns the viewer's full-flight ``source_images`` when available so
        the search also covers captures that produced no detections of their
        own; otherwise falls back to the AOI subset. The current image is
        matched by path because indices differ between the two lists.

        Args:
            current_image (dict): Viewer image the tracked AOI belongs to
            current_image_idx (int): Index of that image in the viewer's list

        Returns:
            tuple: (images list to search, index of current_image within it)
        """
        current_path = current_image.get('path')
        source_images = getattr(self.parent, 'source_images', None)
        if source_images and current_path:
            current_key = path_match_key(current_path)
            for idx, img in enumerate(source_images):
                if path_match_key(img.get('path')) == current_key:
                    return source_images, idx
        # Legacy viewers without source_images, or the current image is
        # missing from the source folder listing: search the AOI subset
        return self.parent.images, current_image_idx

    def _on_progress(self, message):
        """Handle progress updates from the worker.

        Deliberately does NOT call QApplication.processEvents(). This slot is
        already queued onto the GUI thread from the worker, so the label
        repaints on its own as soon as the slot returns and the event loop
        continues -- pumping events here bought nothing and re-entered the
        event loop from inside a slot, which delivered pending key events mid
        search. A reentrant Z press then reassigned self._thread and abort()ed
        the process (see track_selected_aoi), and a nested queued `finished`
        could open the results dialog from inside this handler.
        """
        dialog = getattr(self, 'progress_dialog', None)
        if dialog is None:
            return
        self._in_progress_update = True
        try:
            dialog.setLabelText(message)
        except RuntimeError:
            return  # dialog's C++ object was destroyed during a nested loop
        finally:
            self._in_progress_update = False
            self._flush_deferred()

    def _flush_deferred(self):
        """Run a completion/error handler that arrived during a progress pump."""
        deferred = self._deferred
        self._deferred = None
        if deferred is None:
            return
        deferred()

    def _defer_while_pumping(self, run):
        """True if *run* was deferred because a progress update is active.

        Terminal handlers must never run nested inside _on_progress: they close
        the progress dialog that _on_progress is still using, and they open
        another dialog inside its modal session, which macOS reports as
        "modalSession has been exited prematurely".

        Takes a zero-argument callable so the deferred replay carries every
        argument the handler was called with, including which search it belongs
        to.
        """
        if not self._in_progress_update:
            return False
        # Last one wins: only one terminal event can be meaningful per search.
        self._deferred = run
        return True

    def _is_stale(self, generation):
        """True when *generation* belongs to a search that has been retired.

        A cancelled worker keeps running -- Qt cannot interrupt a Python slot
        mid-execution -- and stays connected to these handlers. Its `finished`
        is queued, so it lands after the user has started the next search.
        Acting on it tore down the live thread and reported the cancelled
        search's (empty) results as the new search's answer.
        """
        return generation is not None and generation != self._generation

    def _on_gps_unavailable(self, generation=None):
        """The AOI's own GPS could not be computed, so there is nothing to find."""
        if self._is_stale(generation):
            return
        if self._defer_while_pumping(
                lambda: self._on_gps_unavailable(generation=generation)):
            return
        try:
            self._cleanup_thread()
            self._close_progress_dialog()
            if self._cancelled:
                return
            QMessageBox.warning(
                self.parent,
                self.tr("Cannot Calculate GPS"),
                self.tr(
                    "Unable to calculate GPS coordinates for this AOI.\n\n"
                    "This may be due to missing image metadata (GPS, altitude, or camera info)."
                )
            )
        except Exception as e:
            self.logger.error(f"Error reporting unavailable AOI GPS: {e}")

    def _on_search_complete(self, results, truncated=False, generation=None):
        """Handle search completion."""
        if self._is_stale(generation):
            return
        if self._defer_while_pumping(
                lambda: self._on_search_complete(results, truncated, generation=generation)):
            return
        try:
            # Clean up thread
            self._cleanup_thread()

            self._close_progress_dialog()

            # The worker emits `finished` even when cancelled, and that signal
            # is queued, so it lands after _on_cancelled has already run.
            # Without this the gallery still opened for a search the user
            # explicitly cancelled.
            if self._cancelled:
                return

            if not results:
                QMessageBox.information(
                    self.parent,
                    self.tr("No Neighbors Found"),
                    self.tr("The AOI was not found in any neighboring images.")
                )
                return

            # Show the gallery dialog
            self._show_gallery_dialog(results, truncated)

            self.tracking_completed.emit(results)

        except Exception as e:
            self.logger.error(f"Error handling search completion: {e}")

    def _on_search_error(self, error_msg, generation=None):
        """Handle search error."""
        if self._is_stale(generation):
            return
        if self._defer_while_pumping(
                lambda: self._on_search_error(error_msg, generation)):
            return
        try:
            # Clean up thread
            self._cleanup_thread()

            self._close_progress_dialog()

            if self._cancelled:
                return

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
        self._cancelled = True
        self._cleanup_thread()
        # Close it here rather than leaving it to the worker's `finished`:
        # that signal is now correctly ignored as stale, so nothing else would
        # release the dialog, and the next search would overwrite the
        # reference and strand this one as a child of the viewer.
        self._close_progress_dialog()

    def _close_progress_dialog(self):
        """Close the progress dialog without triggering a spurious cancellation.

        QProgressDialog emits canceled() from its closeEvent, so the canceled
        handler must be disconnected before closing or a *completed* search
        would be treated as user-cancelled and its results silently dropped.
        """
        if getattr(self, 'progress_dialog', None):
            try:
                self.progress_dialog.canceled.disconnect(self._on_cancelled)
            except (RuntimeError, TypeError):
                pass
            self.progress_dialog.close()
            # Parented to the viewer, so Qt owns it: without this each search
            # strands a QProgressDialog alive for the session.
            try:
                self.progress_dialog.deleteLater()
            except RuntimeError:
                pass  # C++ object already gone
            self.progress_dialog = None

    def _cleanup_thread(self):
        """Release the worker thread without ever destroying a running one.

        Two hazards make the obvious teardown wrong:

        * ``~QThread()`` calls ``qFatal()`` -- an immediate ``abort()`` that
          takes the whole application down with no Python traceback -- if the
          thread is still running. Dropping the last Python reference to a live
          QThread is therefore a hard crash, not an exception.
        * Destroying the worker while its ``run()`` is still executing on that
          thread is a use-after-free on the C++ object.

        Blocking on ``wait()`` here is not the answer either: this runs on the
        GUI thread, and when the user cancels mid-search the worker is inside a
        long computation, so ``wait()`` froze the UI for the rest of the search.

        Instead both objects are moved to ``self._retiring``, which holds them
        alive while the thread unwinds, and are released from the thread's own
        ``finished`` signal. ``self._thread`` is cleared immediately so a new
        search can start right away.
        """
        thread, worker = self._thread, self._worker
        self._thread = None
        self._worker = None
        # Anything still connected from this search is now stale by definition.
        # Bumping here (rather than only when a new search starts) means a
        # cancelled worker's late signals are ignored even if the user never
        # presses Z again.
        self._generation += 1
        if thread is None:
            return

        if worker is not None:
            worker.cancel()

        # Hold both alive until Qt reports the thread stopped.
        self._retiring[thread] = worker
        thread.finished.connect(lambda t=thread: self._release_thread(t))
        thread.requestInterruption()
        thread.quit()
        if not thread.isRunning():
            # Already stopped, so `finished` will not fire again.
            self._release_thread(thread)

    def _release_thread(self, thread):
        """Drop the retained references once *thread* has actually stopped."""
        try:
            # Returns promptly: `finished` is emitted from the thread's own
            # unwind, so this only covers the last instructions of that unwind.
            thread.wait(5000)
        except RuntimeError:
            pass  # C++ object already gone
        self._retiring.pop(thread, None)

    def _show_gallery_dialog(self, results, truncated=False):
        """
        Show the gallery dialog with the found thumbnails.

        Args:
            results (list): List of neighbor results with thumbnails
            truncated (bool): The result cap stopped the search early, so the
                count shown is a floor rather than the answer.
        """
        try:
            # Import here to avoid circular imports
            from core.views.images.viewer.dialogs.AOINeighborGalleryDialog import AOINeighborGalleryDialog

            # Store results for later use when zooming
            self._neighbor_results = results

            # Label results from captures outside the viewer's result set so a
            # reviewer understands why clicking them cannot navigate
            viewer_keys = {path_match_key(img.get('path')) for img in self.parent.images}
            for result in results:
                if path_match_key(result.get('image_path')) not in viewer_keys:
                    result['image_name'] = result.get('image_name', '') + self.tr(" (no detections)")

            # Close existing dialog if open
            if self._gallery_dialog:
                self._gallery_dialog.close()

            # Create and show new dialog
            self._gallery_dialog = AOINeighborGalleryDialog(self.parent, results, truncated)
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

            # Result indices refer to the searched full-flight list; the viewer
            # navigates its own AOI-subset list, so map back by path.
            viewer_idx = None
            result_path = result.get('image_path') if result else None
            if result_path:
                result_key = path_match_key(result_path)
                viewer_idx = next(
                    (i for i, img in enumerate(self.parent.images)
                     if path_match_key(img.get('path')) == result_key),
                    None
                )
            elif 0 <= image_idx < len(self.parent.images):
                # No result payload: treat the index as a viewer index (legacy)
                viewer_idx = image_idx

            if viewer_idx is None:
                # A capture with no detections isn't in the viewer's list; the
                # gallery thumbnail is all there is to show for it (same
                # convention as source-only markers on the GPS map)
                self.logger.info(
                    f"Neighbor result {result_path} is not in the result set (no detections); not navigating"
                )
                return

            pixel_x = result.get('pixel_x') if result else None
            pixel_y = result.get('pixel_y') if result else None

            # Check if we need to load a new image
            needs_load = (self.parent.current_image != viewer_idx)

            if needs_load and pixel_x is not None and pixel_y is not None:
                # State the framing intent with the navigation; the load
                # pipeline applies it as its own final step (same mechanism
                # as the gallery's AOI click - Viewer.load_image_with_zoom).
                self.parent.load_image_with_zoom(
                    viewer_idx, lambda: self._zoom_main_image(pixel_x, pixel_y))
            else:
                # Simple navigation without zoom, or same image
                if needs_load:
                    self.parent.current_image = viewer_idx
                    self.parent._load_image()

                # If same image, still zoom to location
                if not needs_load and pixel_x is not None and pixel_y is not None:
                    self._zoom_main_image(pixel_x, pixel_y)

            # Scroll thumbnail into view
            if hasattr(self.parent, 'thumbnail_controller') and self.parent.thumbnail_controller:
                if hasattr(self.parent.thumbnail_controller, 'ui_component') and self.parent.thumbnail_controller.ui_component:
                    self.parent.thumbnail_controller.ui_component.scroll_thumbnail_into_view()

        except Exception as e:
            self.logger.error(f"Error navigating to image: {e}")

    def _zoom_main_image(self, pixel_x, pixel_y):
        """Zoom the main viewer to a pixel location (scale 6 matches AOI clicks)."""
        viewer = getattr(self.parent, 'main_image', None)
        if viewer and hasattr(viewer, 'zoomToArea'):
            viewer.zoomToArea((pixel_x, pixel_y), 6)

    def cleanup(self):
        """Clean up resources."""
        self._cleanup_thread()
        if self._gallery_dialog:
            self._gallery_dialog.close()
            self._gallery_dialog = None
