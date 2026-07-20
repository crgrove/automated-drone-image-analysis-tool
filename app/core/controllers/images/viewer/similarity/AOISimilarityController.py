"""
AOISimilarityController - Controller for finding visually similar AOIs.

Runs the AOISimilarityService on a worker thread to rank every other AOI in the
dataset against the selected one, then displays the top matches in a gallery
dialog. Mirrors the AOINeighborTrackingController threading pattern.
"""

from pathlib import Path

from PySide6.QtCore import QObject, Signal, QThread, Qt
from PySide6.QtWidgets import QMessageBox, QProgressDialog

from core.services.image.AOISimilarityService import AOISimilarityService
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


class AOISimilarityController(TranslationMixin, QObject):
    """Controller for ranking all AOIs by visual similarity to a selected AOI."""

    search_started = Signal()
    search_completed = Signal(list)  # Ranked result dicts (reference excluded)
    search_error = Signal(str)

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
        self.progress_dialog = None

        # Results dialog and the entries backing it (row 0 = reference)
        self._results_dialog = None
        self._current_results = []
        self._ref_indices = None
        self._total_candidates = 0

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
        """Show the progress dialog and start the worker thread."""
        self._cancelled = False

        # Show progress dialog (indeterminate until the first progress signal)
        self.progress_dialog = QProgressDialog(
            self.tr("Analyzing AOIs for visual similarity..."),
            self.tr("Cancel"),
            0, 0,
            self.parent
        )
        self.progress_dialog.setWindowTitle(self.tr("Find Similar AOIs"))
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setValue(0)

        # Create worker and thread
        self._thread = QThread()
        self._worker = SimilaritySearchWorker(
            similarity_service=self._get_service(),
            images=self.parent.images,
            **worker_kwargs
        )
        self._worker.moveToThread(self._thread)

        # Connect signals
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_search_complete)
        self._worker.error.connect(self._on_search_error)
        self.progress_dialog.canceled.connect(self._on_cancelled)

        self.search_started.emit()
        self._thread.start()

    def _on_progress(self, done, total):
        """Handle progress updates from the worker."""
        if self.progress_dialog and total > 0:
            if self.progress_dialog.maximum() != total:
                self.progress_dialog.setRange(0, total)
            self.progress_dialog.setValue(done)
            self.progress_dialog.setLabelText(
                self.tr("Analyzing AOI {done} of {total}...").format(done=done, total=total)
            )

    def _on_search_complete(self, results):
        """Handle search completion."""
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

    def _on_cancelled(self):
        """Handle cancellation from the progress dialog."""
        self._cancelled = True
        if self._worker:
            self._worker.cancel()
        self._cleanup_thread()

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
        """Clean up the worker thread."""
        if self._thread:
            self._thread.quit()
            self._thread.wait()
            self._thread = None
        self._worker = None

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
