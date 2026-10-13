"""
AOISimilarityController - Controller for finding visually similar AOIs.

Runs the AOISimilarityService on a worker thread to rank every other AOI in the
dataset against the selected one, then displays the top matches in a gallery
dialog. Mirrors the AOINeighborTrackingController threading pattern.

Also drives the "Similar & Nearby" AOI sort: the same worker-thread plumbing runs
AOISimilarityGroupingService over every AOI and hands the resulting order to the
AOIController.
"""

from pathlib import Path

from PySide6.QtCore import QObject, Signal, QThread, Qt
from PySide6.QtWidgets import QMessageBox, QProgressDialog

from core.services.image.AOISimilarityService import AOISimilarityService
from core.services.image.AOISimilarityGroupingService import AOISimilarityGroupingService, make_aoi_locator
from core.services.LoggerService import LoggerService
from helpers.TranslationMixin import TranslationMixin


class SimilaritySearchWorker(QObject):
    """Worker that runs the similarity search off the GUI thread."""

    progress = Signal(int, int)  # done, total
    finished = Signal(list)      # Ranked result dicts
    error = Signal(str)          # Error message

    def __init__(self, similarity_service, images, ref_image_idx, ref_aoi_idx):
        super().__init__()
        self.similarity_service = similarity_service
        self.images = images
        self.ref_image_idx = ref_image_idx
        self.ref_aoi_idx = ref_aoi_idx
        self._cancelled = False

    def cancel(self):
        """Cancel the search operation."""
        self._cancelled = True

    def run(self):
        """Execute the similarity search."""
        try:
            if self._cancelled:
                self.finished.emit([])
                return

            results = self.similarity_service.find_similar(
                images=self.images,
                ref_image_idx=self.ref_image_idx,
                ref_aoi_idx=self.ref_aoi_idx,
                progress_callback=self._emit_progress,
                cancel_check=lambda: self._cancelled,
            )

            self.finished.emit([] if self._cancelled else results)

        except Exception as e:
            self.error.emit(str(e))

    def _emit_progress(self, done, total):
        if not self._cancelled:
            self.progress.emit(done, total)


class SimilarityGroupingWorker(QObject):
    """Worker that orders every AOI into similar-and-nearby groups off the GUI thread."""

    progress = Signal(int, int)  # done, total
    # object, not list: the result is a dataclass, and Qt's list marshalling
    # would rewrite its tuples anyway
    finished = Signal(object)    # SimilarityGroupingResult, or None when cancelled
    error = Signal(str)          # Error message

    def __init__(self, grouping_service, images, locate_aois, max_distance_m, min_similarity):
        super().__init__()
        self.grouping_service = grouping_service
        self.images = images
        self.locate_aois = locate_aois
        self.max_distance_m = max_distance_m
        self.min_similarity = min_similarity
        self._cancelled = False

    def cancel(self):
        """Cancel the grouping operation."""
        self._cancelled = True

    def run(self):
        """Execute the grouping."""
        try:
            if self._cancelled:
                self.finished.emit(None)
                return

            result = self.grouping_service.group(
                images=self.images,
                locate_aois=self.locate_aois,
                max_distance_m=self.max_distance_m,
                min_similarity=self.min_similarity,
                progress_callback=self._emit_progress,
                cancel_check=lambda: self._cancelled,
            )

            self.finished.emit(None if self._cancelled else result)

        except Exception as e:
            self.error.emit(str(e))

    def _emit_progress(self, done, total):
        if not self._cancelled:
            self.progress.emit(done, total)


class AOISimilarityController(TranslationMixin, QObject):
    """Controller for ranking all AOIs by visual similarity to a selected AOI."""

    search_started = Signal()
    search_completed = Signal(list)  # Ranked result dicts (reference excluded)
    search_error = Signal(str)
    grouping_completed = Signal(object)  # SimilarityGroupingResult that was applied
    grouping_error = Signal(str)

    def __init__(self, parent):
        """
        Initialize the AOISimilarityController.

        Args:
            parent: The parent viewer window
        """
        super().__init__(parent)
        self.parent = parent
        self.logger = LoggerService()

        # Built lazily so the dataset .thumbnails dir can be resolved from xml_path
        self._similarity_service = None

        # Thread management
        self._worker = None
        self._thread = None
        self._cancelled = False
        # Threads still winding down, kept alive until Qt reports them
        # stopped. See _cleanup_thread for why this must not be skipped.
        self._retiring = {}
        self.progress_dialog = None
        # Reentrancy state: QProgressDialog.setValue() pumps the event loop, so
        # terminal handlers can arrive while _on_progress is mid-body.
        self._in_progress_update = False
        self._deferred = None

        # Results dialog and the entries backing it (row 0 = reference)
        self._results_dialog = None
        self._current_results = []
        self._ref_indices = None
        self._total_candidates = 0
        # True while the running worker is a sort grouping rather than a search
        self._grouping = False

    def _get_service(self):
        """Lazily build the similarity service with the dataset thumbnail cache dir."""
        if self._similarity_service is None:
            dataset_dir = None
            xml_path = getattr(self.parent, 'xml_path', None)
            if xml_path:
                thumbnail_dir = Path(xml_path).parent / '.thumbnails'
                if thumbnail_dir.exists():
                    dataset_dir = str(thumbnail_dir)
            self._similarity_service = AOISimilarityService(dataset_thumbnail_dir=dataset_dir)
        return self._similarity_service

    def find_similar_for_selected(self, image_idx=None, aoi_idx=None):
        """
        Rank all other AOIs by similarity to the selected AOI.

        Triggered by the context menu ("Find Similar AOIs") or Shift+Z. When called
        with explicit indices those are used directly (context menu and gallery mode);
        with no arguments the AOI is read from the single-image AOIController.
        """
        try:
            # One search at a time
            if self._thread is not None:
                return

            if aoi_idx is not None:
                ref_image_idx = image_idx if image_idx is not None else self.parent.current_image
                if ref_image_idx < 0 or ref_image_idx >= len(self.parent.images):
                    return
                aois = self.parent.images[ref_image_idx].get('areas_of_interest', [])
                if aoi_idx < 0 or aoi_idx >= len(aois):
                    return
                ref_aoi_idx = aoi_idx
            else:
                selected_aoi = self.parent.aoi_controller.get_selected_aoi()
                if not selected_aoi:
                    QMessageBox.information(
                        self.parent,
                        self.tr("No AOI Selected"),
                        self.tr("Please select an AOI first by clicking on it in the thumbnail panel.")
                    )
                    return
                _, ref_aoi_idx = selected_aoi
                ref_image_idx = self.parent.current_image

            self._ref_indices = (ref_image_idx, ref_aoi_idx)
            self._total_candidates = max(
                0,
                sum(len(image.get('areas_of_interest') or []) for image in self.parent.images) - 1
            )
            self._start_search(ref_image_idx=ref_image_idx, ref_aoi_idx=ref_aoi_idx)

        except Exception as e:
            self.logger.error(f"Error starting AOI similarity search: {e}")
            QMessageBox.critical(
                self.parent,
                self.tr("Similarity Search Error"),
                self.tr("An error occurred while starting the similarity search:\n{error}").format(
                    error=str(e)
                )
            )

    def _start_search(self, **worker_kwargs):
        """Start a similarity search worker for the reference AOI."""
        worker = SimilaritySearchWorker(
            similarity_service=self._get_service(),
            images=self.parent.images,
            **worker_kwargs
        )
        self._start_worker(
            worker, self._on_search_complete, self._on_search_error,
            title=self.tr("Find Similar AOIs"),
            label=self.tr("Analyzing AOIs for visual similarity..."),
        )
        self.search_started.emit()

    def sort_by_similarity_groups(self, max_distance_m, min_similarity):
        """
        Order every AOI so look-alikes that are close on the ground sit together.

        Triggered by the "Similar & Nearby" AOI sort option. On success the order
        is handed to AOIController.apply_similarity_groups; on cancel or failure
        the sort selection is restored.

        Args:
            max_distance_m (float): Largest ground distance between grouped AOIs.
            min_similarity (int): Smallest appearance similarity (0-100) between them.

        Returns:
            bool: True if the grouping started.
        """
        if self._thread is not None:
            return False
        if not any(image.get('areas_of_interest') for image in (self.parent.images or [])):
            return False

        worker = SimilarityGroupingWorker(
            grouping_service=AOISimilarityGroupingService(self._get_service()),
            images=self.parent.images,
            locate_aois=make_aoi_locator(
                custom_altitude_ft=getattr(self.parent, 'custom_agl_altitude_ft', None),
                use_terrain=getattr(self.parent, 'use_terrain_elevation', True),
            ),
            max_distance_m=max_distance_m,
            min_similarity=min_similarity,
        )
        self._start_worker(
            worker, self._on_grouping_complete, self._on_grouping_error,
            title=self.tr("Sort: Similar & Nearby"),
            label=self.tr("Grouping AOIs that look alike and are close together..."),
            grouping=True,
        )
        return True

    def _start_worker(self, worker, on_finished, on_error, title, label, grouping=False):
        """Show the progress dialog and run *worker* on its own thread."""
        self._cancelled = False
        self._grouping = grouping

        # Show progress dialog (indeterminate until the first progress signal)
        self.progress_dialog = QProgressDialog(
            label,
            self.tr("Cancel"),
            0, 0,
            self.parent
        )
        self.progress_dialog.setWindowTitle(title)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        # Own the dialog's lifetime explicitly. With autoClose/autoReset on,
        # reaching the maximum makes QProgressDialog reset and hide itself from
        # inside setValue(), which is another way the dialog disappears while
        # _on_progress is still using it.
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)
        self.progress_dialog.setValue(0)

        # Create worker and thread
        self._thread = QThread()
        self._worker = worker
        self._worker.moveToThread(self._thread)

        # Connect signals
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(on_finished)
        self._worker.error.connect(on_error)
        self.progress_dialog.canceled.connect(self._on_cancelled)

        self._thread.start()

    def _on_progress(self, done, total):
        """Handle progress updates from the worker.

        QProgressDialog.setValue() calls QApplication.processEvents() whenever
        the dialog is modal, so the event loop is re-entered *inside this slot*.
        That pump delivers the worker's queued `finished` signal, so
        _on_search_complete used to run nested here: it set progress_dialog to
        None underneath us (the next line then raised AttributeError on None)
        and opened the results dialog inside the progress dialog's still-open
        Cocoa modal session, which macOS reports as "modalSession has been
        exited prematurely - check for a reentrant call to endModalSession".

        Hence the local reference, the re-checks around the pumping call, and
        the completion deferral in _defer_while_pumping.
        """
        dialog = self.progress_dialog
        if dialog is None or total <= 0:
            return

        self._in_progress_update = True
        try:
            if dialog.maximum() != total:
                dialog.setRange(0, total)
            dialog.setValue(done)          # may re-enter the event loop
            if self.progress_dialog is not dialog:
                return                     # torn down while we were pumping
            dialog.setLabelText(
                self.tr("Analyzing AOI {done} of {total}...").format(done=done, total=total)
            )
        except RuntimeError:
            return  # dialog's C++ object was destroyed during the nested loop
        finally:
            self._in_progress_update = False
            self._flush_deferred()

    def _flush_deferred(self):
        """Run a completion/error handler that arrived during a progress pump."""
        deferred = self._deferred
        self._deferred = None
        if deferred is None:
            return
        handler, payload = deferred
        handler(payload)

    def _defer_while_pumping(self, handler, payload):
        """True if *handler* was deferred because a progress update is active.

        Terminal handlers must never run nested inside _on_progress: they close
        the progress dialog that _on_progress is still using, and they open
        another dialog inside its modal session. Deferring to the end of the
        progress update keeps the teardown ordered.
        """
        if not self._in_progress_update:
            return False
        # Last one wins: only one terminal event can be meaningful per search.
        self._deferred = (handler, payload)
        return True

    def _on_search_complete(self, results):
        """Handle search completion."""
        if self._defer_while_pumping(self._on_search_complete, results):
            return
        try:
            self._cleanup_thread()
            self._close_progress_dialog()

            if self._cancelled:
                return

            if not results:
                QMessageBox.information(
                    self.parent,
                    self.tr("No Similar AOIs"),
                    self.tr("No other AOIs could be analyzed for similarity.")
                )
                return

            # Prepend the reference AOI so it is always visible as row 0
            display_results = results
            try:
                reference_entry = self._get_service().build_reference_entry(
                    self.parent.images, *self._ref_indices)
                display_results = [reference_entry] + results
            except Exception as e:
                self.logger.error(f"Error building similarity reference entry: {e}")

            self._show_results_dialog(display_results)
            self.search_completed.emit(results)

        except Exception as e:
            self.logger.error(f"Error handling similarity search completion: {e}")

    def _on_search_error(self, error_msg):
        """Handle search error."""
        if self._defer_while_pumping(self._on_search_error, error_msg):
            return
        try:
            self._cleanup_thread()
            self._close_progress_dialog()

            if self._cancelled:
                return

            QMessageBox.warning(
                self.parent,
                self.tr("Similarity Search Error"),
                self.tr("The similarity search could not be completed:\n{error}").format(
                    error=error_msg
                )
            )

            self.search_error.emit(error_msg)

        except Exception as e:
            self.logger.error(f"Error handling similarity search error: {e}")

    def _on_grouping_complete(self, result):
        """Apply a finished similar-and-nearby grouping as the AOI sort."""
        if self._defer_while_pumping(self._on_grouping_complete, result):
            return
        try:
            self._cleanup_thread()
            self._close_progress_dialog()

            if self._cancelled:
                return  # _on_cancelled already restored the sort selection

            if result is None or not result.total:
                self._restore_sort_selection()
                return

            if result.unlocated_count == result.total:
                self._restore_sort_selection()
                QMessageBox.information(
                    self.parent,
                    self.tr("No AOI Positions"),
                    self.tr("None of the AOIs have a GPS position, so AOIs that are close "
                            "together cannot be grouped.")
                )
                return

            self.parent.aoi_controller.apply_similarity_groups(result)
            self._show_grouping_toast(result)
            self.grouping_completed.emit(result)

        except Exception as e:
            self.logger.error(f"Error applying similarity grouping: {e}")

    def _on_grouping_error(self, error_msg):
        """Handle a failed grouping: keep the previous sort and report it."""
        if self._defer_while_pumping(self._on_grouping_error, error_msg):
            return
        try:
            self._cleanup_thread()
            self._close_progress_dialog()

            if self._cancelled:
                return

            self._restore_sort_selection()
            QMessageBox.warning(
                self.parent,
                self.tr("Sort Error"),
                self.tr("The AOIs could not be sorted by similarity:\n{error}").format(error=error_msg)
            )
            self.grouping_error.emit(error_msg)

        except Exception as e:
            self.logger.error(f"Error handling similarity grouping error: {e}")

    def _show_grouping_toast(self, result):
        """Summarize the applied grouping in a status toast."""
        if not hasattr(self.parent, 'status_controller'):
            return
        if result.groups:
            message = self.tr("Sorted into {groups} group(s) of similar, nearby AOIs "
                              "({grouped} of {total} AOIs)").format(
                groups=len(result.groups), grouped=result.grouped_count, total=result.total)
            color = "#00C853"
        else:
            message = self.tr("No similar AOIs found close together - try a larger distance "
                              "or a lower similarity")
            color = "#808080"
        if result.unlocated_count:
            message += self.tr("; {count} AOI(s) without a GPS position left ungrouped").format(
                count=result.unlocated_count)
        self.parent.status_controller.show_toast(message, 4000, color=color)

    def _restore_sort_selection(self):
        """Point the sort combo back at the sort that is actually applied."""
        aoi_controller = getattr(self.parent, 'aoi_controller', None)
        if aoi_controller is not None:
            aoi_controller.restore_sort_selection()

    def _on_cancelled(self):
        """Handle cancellation from the progress dialog."""
        self._cancelled = True
        self._cleanup_thread()
        if self._grouping:
            self._restore_sort_selection()

    def _close_progress_dialog(self):
        """Close the progress dialog without triggering a spurious cancellation.

        QProgressDialog emits canceled() from its closeEvent, so the canceled
        handler must be disconnected before closing or a completed search would
        be treated as user-cancelled and its results silently dropped.
        """
        if self.progress_dialog:
            try:
                self.progress_dialog.canceled.disconnect(self._on_cancelled)
            except (RuntimeError, TypeError):
                pass
            self.progress_dialog.close()
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

    def _show_results_dialog(self, display_results):
        """
        Show the results dialog with the ranked thumbnails.

        Args:
            display_results (list): Result dicts; row 0 is the reference entry.
        """
        try:
            # Import here to avoid circular imports
            from core.views.images.viewer.dialogs.AOISimilarityResultsDialog import AOISimilarityResultsDialog

            self._current_results = display_results

            if self._results_dialog:
                self._results_dialog.close()

            self._results_dialog = AOISimilarityResultsDialog(
                self.parent, display_results, total_candidates=self._total_candidates)
            self._results_dialog.result_clicked.connect(self._on_result_clicked)
            self._results_dialog.bulk_flag_requested.connect(self._on_bulk_flag)
            self._results_dialog.bulk_comment_requested.connect(self._on_bulk_comment)
            self._results_dialog.show()

        except Exception as e:
            self.logger.error(f"Error showing similarity results dialog: {e}")
            QMessageBox.critical(
                self.parent,
                self.tr("Display Error"),
                self.tr("An error occurred while displaying results:\n{error}").format(
                    error=str(e)
                )
            )

    def _on_result_clicked(self, row):
        """
        Navigate the viewer to the clicked result's AOI.

        Args:
            row (int): Row of the clicked result in the dialog.
        """
        try:
            if row < 0 or row >= len(self._current_results):
                return
            result = self._current_results[row]
            image_idx = result['image_idx']
            aoi_idx = result['aoi_idx']
            aoi_data = result.get('aoi_data')

            gallery_controller = self.parent.gallery_controller
            if getattr(self.parent, 'gallery_mode', False):
                # go_to_aoi also syncs the gallery selection; it returns False when
                # the AOI is filtered out of the gallery, so fall through to a
                # direct load+zoom in that case.
                if gallery_controller.go_to_aoi(image_idx, aoi_idx):
                    return
            gallery_controller.on_aoi_clicked(image_idx, aoi_idx, aoi_data)

        except Exception as e:
            self.logger.error(f"Error navigating to similar AOI: {e}")

    def _entries_for_rows(self, rows):
        """Map dialog rows to their result entries, dropping out-of-range rows."""
        return [self._current_results[row] for row in rows
                if 0 <= row < len(self._current_results)]

    def _on_bulk_flag(self, rows, flagged):
        """Flag or unflag all checked result AOIs."""
        try:
            entries = self._entries_for_rows(rows)
            if not entries:
                return

            items = [(entry['image_idx'], entry['aoi_idx']) for entry in entries]
            applied = self.parent.aoi_controller.set_aoi_flags_bulk(items, flagged)

            if self._results_dialog:
                self._results_dialog.refresh_status_badges()

            if applied and hasattr(self.parent, 'status_controller'):
                if flagged:
                    message = self.tr("Flagged {count} AOI(s)").format(count=applied)
                    self.parent.status_controller.show_toast(message, 2000, color="#00C853")
                else:
                    message = self.tr("Removed flag from {count} AOI(s)").format(count=applied)
                    self.parent.status_controller.show_toast(message, 2000, color="#808080")

        except Exception as e:
            self.logger.error(f"Error applying bulk flag to similar AOIs: {e}")

    def _on_bulk_comment(self, rows):
        """Add or edit the comment on all checked result AOIs."""
        try:
            entries = self._entries_for_rows(rows)
            if not entries:
                return

            # Pre-fill with the common comment when every checked AOI agrees
            comments = {(entry.get('aoi_data') or {}).get('user_comment', '') for entry in entries}
            current_comment = comments.pop() if len(comments) == 1 else ''

            # Import here to avoid circular imports
            from core.views.images.viewer.dialogs.AOICommentDialog import AOICommentDialog
            dialog = AOICommentDialog(self.parent, current_comment)
            if not dialog.exec():
                return
            comment = dialog.get_comment()

            items = [(entry['image_idx'], entry['aoi_idx']) for entry in entries]
            applied = self.parent.aoi_controller.set_aoi_comments_bulk(items, comment)

            if self._results_dialog:
                self._results_dialog.refresh_status_badges()

            if applied and hasattr(self.parent, 'status_controller'):
                if comment:
                    message = self.tr("Comment saved on {count} AOI(s)").format(count=applied)
                    self.parent.status_controller.show_toast(message, 2000, color="#00C853")
                else:
                    message = self.tr("Comment cleared on {count} AOI(s)").format(count=applied)
                    self.parent.status_controller.show_toast(message, 2000, color="#808080")

        except Exception as e:
            self.logger.error(f"Error applying bulk comment to similar AOIs: {e}")

    def cleanup(self):
        """Clean up resources."""
        self._cleanup_thread()
        if self._results_dialog:
            self._results_dialog.close()
            self._results_dialog = None
