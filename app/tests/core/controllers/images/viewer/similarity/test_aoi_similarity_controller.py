"""
Tests for AOISimilarityController and SimilaritySearchWorker.

Covers worker signal flow (progress/finished/error/cancel), controller AOI
resolution and guards, result-click navigation routing, and the end-to-end
QThread plumbing with both a mocked service and a real (failing) one.
"""

import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget

from core.controllers.images.viewer.similarity.AOISimilarityController import (
    AOISimilarityController,
    SimilaritySearchWorker,
)


@pytest.fixture(scope='session')
def app():
    """Create QApplication for widget tests."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def viewer(app, tmp_path, qtbot):
    """Minimal viewer stand-in: a real QWidget carrying the attributes the controller reads."""
    widget = QWidget()
    qtbot.addWidget(widget)
    widget.images = [
        {'path': str(tmp_path / 'DJI_0001.JPG'),
         'areas_of_interest': [{'center': (100, 100), 'radius': 20, 'area': 400, 'number': 1}]},
        {'path': str(tmp_path / 'DJI_0002.JPG'),
         'areas_of_interest': [{'center': (200, 200), 'radius': 30, 'area': 600, 'number': 2}]},
    ]
    widget.current_image = 0
    widget.xml_path = str(tmp_path / 'ADIAT_Data.xml')
    widget.aoi_controller = MagicMock()
    widget.gallery_controller = MagicMock()
    widget.gallery_mode = False
    return widget


@pytest.fixture
def controller(viewer):
    return AOISimilarityController(viewer)


# ---------------------------------------------------------------------------
# SimilaritySearchWorker
# ---------------------------------------------------------------------------

class TestSimilaritySearchWorker:

    def test_run_emits_progress_then_finished(self, app):
        service = MagicMock()

        def fake_find_similar(**kwargs):
            kwargs['progress_callback'](100, 200)
            return [{'image_idx': 1, 'aoi_idx': 0, 'similarity': 90}]

        service.find_similar.side_effect = fake_find_similar
        worker = SimilaritySearchWorker(service, images=[], ref_image_idx=0, ref_aoi_idx=0)

        progress, finished = [], []
        worker.progress.connect(lambda done, total: progress.append((done, total)))
        worker.finished.connect(finished.append)
        worker.run()

        assert progress == [(100, 200)]
        assert finished == [[{'image_idx': 1, 'aoi_idx': 0, 'similarity': 90}]]

    def test_cancel_before_run_skips_service(self, app):
        service = MagicMock()
        worker = SimilaritySearchWorker(service, images=[], ref_image_idx=0, ref_aoi_idx=0)
        finished = []
        worker.finished.connect(finished.append)

        worker.cancel()
        worker.run()

        assert finished == [[]]
        service.find_similar.assert_not_called()

    def test_cancel_check_reflects_cancellation(self, app):
        service = MagicMock()
        worker = SimilaritySearchWorker(service, images=[], ref_image_idx=0, ref_aoi_idx=0)

        def fake_find_similar(**kwargs):
            assert kwargs['cancel_check']() is False
            worker.cancel()
            assert kwargs['cancel_check']() is True
            return []

        service.find_similar.side_effect = fake_find_similar
        finished = []
        worker.finished.connect(finished.append)
        worker.run()
        assert finished == [[]]

    def test_service_exception_emits_error(self, app):
        service = MagicMock()
        service.find_similar.side_effect = ValueError("no thumbnail")
        worker = SimilaritySearchWorker(service, images=[], ref_image_idx=0, ref_aoi_idx=0)

        errors = []
        worker.error.connect(errors.append)
        worker.run()

        assert errors == ["no thumbnail"]


# ---------------------------------------------------------------------------
# Controller: guards and AOI resolution
# ---------------------------------------------------------------------------

class TestControllerGuards:

    def test_initialization(self, controller, viewer):
        assert controller.parent is viewer
        assert controller._similarity_service is None
        assert controller._thread is None

    def test_service_without_thumbnail_dir(self, controller):
        service = controller._get_service()
        assert service.thumbnail_cache.dataset_cache_dir is None

    def test_service_with_thumbnail_dir(self, viewer, tmp_path):
        (tmp_path / '.thumbnails').mkdir()
        controller = AOISimilarityController(viewer)
        service = controller._get_service()
        assert str(service.thumbnail_cache.dataset_cache_dir) == str(tmp_path / '.thumbnails')

    def test_no_selection_shows_message(self, controller, viewer, monkeypatch):
        info = MagicMock()
        monkeypatch.setattr(QMessageBox, 'information', info)
        viewer.aoi_controller.get_selected_aoi.return_value = None

        controller.find_similar_for_selected()

        info.assert_called_once()
        assert controller._thread is None

    def test_reentrancy_guard(self, controller):
        controller._thread = object()  # Simulate a running search
        controller.find_similar_for_selected(image_idx=0, aoi_idx=0)
        assert controller.progress_dialog is None
        controller._thread = None

    def test_invalid_image_index_ignored(self, controller):
        controller.find_similar_for_selected(image_idx=99, aoi_idx=0)
        assert controller._thread is None

    def test_invalid_aoi_index_ignored(self, controller):
        controller.find_similar_for_selected(image_idx=0, aoi_idx=99)
        assert controller._thread is None


# ---------------------------------------------------------------------------
# Controller: completion handling
# ---------------------------------------------------------------------------

class TestControllerCompletion:

    def test_empty_results_shows_info(self, controller, monkeypatch):
        info = MagicMock()
        monkeypatch.setattr(QMessageBox, 'information', info)
        controller._cancelled = False
        controller._on_search_complete([])
        info.assert_called_once()

    def test_cancelled_completion_is_silent(self, controller, monkeypatch):
        info = MagicMock()
        monkeypatch.setattr(QMessageBox, 'information', info)
        controller._cancelled = True
        controller._on_search_complete([])
        info.assert_not_called()

    def test_reference_entry_prepended(self, controller, viewer, monkeypatch):
        fake_service = MagicMock()
        reference_entry = {'image_idx': 0, 'aoi_idx': 0, 'is_reference': True, 'similarity': 100}
        fake_service.build_reference_entry.return_value = reference_entry
        controller._similarity_service = fake_service
        controller._ref_indices = (0, 0)
        controller._cancelled = False

        shown = MagicMock()
        monkeypatch.setattr(controller, '_show_results_dialog', shown)

        results = [{'image_idx': 1, 'aoi_idx': 0, 'similarity': 88, 'is_reference': False}]
        emitted = []
        controller.search_completed.connect(emitted.append)
        controller._on_search_complete(results)

        shown.assert_called_once()
        display = shown.call_args[0][0]
        assert display[0] is reference_entry
        assert display[1:] == results
        assert emitted == [results]

    def test_cancel_stops_worker_and_thread(self, controller):
        worker = MagicMock()
        thread = MagicMock()
        thread.isRunning.return_value = False   # already stopped
        controller._worker = worker
        controller._thread = thread

        controller._on_cancelled()

        worker.cancel.assert_called_once()
        thread.quit.assert_called_once()
        thread.wait.assert_called_once()
        assert controller._thread is None
        assert controller._worker is None
        assert controller._cancelled is True
        assert thread not in controller._retiring

    def test_cancel_mid_search_does_not_block_the_gui_thread(self, controller):
        """Cancelling while the worker is busy must not wait() on the GUI thread.

        _on_cancelled runs on the GUI thread; the worker is inside a long
        computation and only notices the cancel flag at its next checkpoint. A
        blocking wait() here froze the UI for the remainder of the search.
        """
        worker = MagicMock()
        thread = MagicMock()
        thread.isRunning.return_value = True    # still busy
        controller._worker = worker
        controller._thread = thread

        controller._on_cancelled()

        worker.cancel.assert_called_once()
        thread.quit.assert_called_once()
        thread.wait.assert_not_called()
        # Cleared so a new search can start immediately...
        assert controller._thread is None
        assert controller._worker is None
        # ...but both objects are retained until the thread reports finished.
        # Releasing a *running* QThread makes ~QThread() qFatal() -> abort().
        assert controller._retiring[thread] is worker

    def test_retired_thread_is_released_once_finished(self, controller):
        worker = MagicMock()
        thread = MagicMock()
        thread.isRunning.return_value = True
        controller._worker = worker
        controller._thread = thread
        controller._cleanup_thread()
        assert thread in controller._retiring

        controller._release_thread(thread)

        thread.wait.assert_called_once()
        assert thread not in controller._retiring

    def test_release_survives_deleted_cpp_object(self, controller):
        thread = MagicMock()
        thread.wait.side_effect = RuntimeError("already deleted")
        controller._retiring[thread] = None
        controller._release_thread(thread)
        assert thread not in controller._retiring

    def test_cleanup_with_no_thread_is_noop(self, controller):
        controller._thread = None
        controller._worker = None
        controller._cleanup_thread()
        assert controller._retiring == {}


class TestProgressPumpReentrancy:
    """QProgressDialog.setValue() pumps the event loop when the dialog is modal.

    Reported crash (Shift+Z on macOS):
        modalSession has been exited prematurely - check for a reentrant call
        to endModalSession:
        AttributeError: 'NoneType' object has no attribute 'setLabelText'

    setValue() re-entered the event loop mid-slot, delivering the worker's
    queued `finished`. _on_search_complete then ran nested inside _on_progress:
    it set progress_dialog to None (so the next line raised) and opened the
    results dialog inside the progress dialog's still-open Cocoa modal session.
    """

    def test_completion_during_setvalue_does_not_crash(self, controller, monkeypatch):
        """The exact reported traceback: setValue() -> nested completion."""
        shown = MagicMock()
        monkeypatch.setattr(controller, '_show_results_dialog', shown)

        results = [{'image_idx': 1, 'aoi_idx': 0, 'similarity': 88,
                    'is_reference': False, 'aoi_data': {}}]
        controller._ref_indices = (0, 0)
        service = MagicMock()
        service.build_reference_entry.return_value = {
            'image_idx': 0, 'aoi_idx': 0, 'similarity': 100, 'is_reference': True}
        controller._similarity_service = service

        dialog = MagicMock()
        dialog.maximum.return_value = 0
        # setValue() pumps the event loop, which delivers `finished`.
        dialog.setValue.side_effect = lambda _v: controller._on_search_complete(results)
        controller.progress_dialog = dialog

        controller._on_progress(1, 4)   # must not raise AttributeError

        # The label update still happened on the live dialog...
        dialog.setLabelText.assert_called_once()
        # ...and the completion ran only after the progress update finished,
        # so the results dialog never opened inside the progress modal session.
        shown.assert_called_once()
        assert controller.progress_dialog is None
        assert controller._deferred is None
        assert controller._in_progress_update is False

    def test_error_during_setvalue_is_deferred(self, controller, monkeypatch):
        warning = MagicMock()
        monkeypatch.setattr(QMessageBox, 'warning', warning)
        dialog = MagicMock()
        dialog.maximum.return_value = 0
        dialog.setValue.side_effect = lambda _v: controller._on_search_error("boom")
        controller.progress_dialog = dialog

        controller._on_progress(1, 4)

        warning.assert_called_once()
        assert controller._deferred is None

    def test_deferred_completion_wins_over_earlier_deferral(self, controller,
                                                            monkeypatch):
        """Only one terminal event per search is meaningful; the last one wins."""
        monkeypatch.setattr(controller, '_show_results_dialog', MagicMock())
        controller._in_progress_update = True
        controller._on_search_error("first")
        controller._on_search_complete([])
        assert controller._deferred[0] == controller._on_search_complete

    def test_dialog_destroyed_mid_pump_is_survivable(self, controller):
        """A RuntimeError from a deleted C++ dialog must not escape the slot."""
        dialog = MagicMock()
        dialog.maximum.return_value = 0
        dialog.setValue.side_effect = RuntimeError("wrapped C/C++ object deleted")
        controller.progress_dialog = dialog

        controller._on_progress(1, 4)   # must not raise

        assert controller._in_progress_update is False

    def test_progress_with_no_dialog_is_safe(self, controller):
        controller.progress_dialog = None
        controller._on_progress(1, 4)

    def test_progress_with_zero_total_is_ignored(self, controller):
        dialog = MagicMock()
        controller.progress_dialog = dialog
        controller._on_progress(0, 0)
        dialog.setValue.assert_not_called()

    def test_progress_dialog_does_not_self_close(self, controller, viewer,
                                                 monkeypatch):
        """autoClose/autoReset would hide the dialog from inside setValue()."""
        monkeypatch.setattr(controller, '_get_service', lambda: MagicMock())
        monkeypatch.setattr(controller, '_cleanup_thread', lambda: None)
        with patch.object(controller, '_start_search', wraps=controller._start_search):
            controller._start_search(ref_image_idx=0, ref_aoi_idx=0)
        try:
            assert controller.progress_dialog.autoClose() is False
            assert controller.progress_dialog.autoReset() is False
        finally:
            controller._cancelled = True
            if controller._thread is not None:
                controller._thread.quit()
                controller._thread.wait(5000)
            if controller.progress_dialog is not None:
                controller.progress_dialog.close()

    def test_show_results_dialog_and_cleanup(self, controller):
        results = [
            {'image_idx': 0, 'aoi_idx': 0, 'image_name': 'a.jpg', 'aoi_number': 1,
             'similarity': 100, 'thumbnail': None, 'is_reference': True},
            {'image_idx': 1, 'aoi_idx': 0, 'image_name': 'b.jpg', 'aoi_number': 2,
             'similarity': 70, 'thumbnail': None, 'is_reference': False},
        ]
        controller._total_candidates = 1
        controller._show_results_dialog(results)
        assert controller._results_dialog is not None
        assert controller._current_results == results

        controller.cleanup()
        assert controller._results_dialog is None


# ---------------------------------------------------------------------------
# Controller: result-click navigation
# ---------------------------------------------------------------------------

class TestResultNavigation:

    @pytest.fixture
    def controller_with_results(self, controller, viewer):
        aoi_data = viewer.images[1]['areas_of_interest'][0]
        controller._current_results = [
            {'image_idx': 0, 'aoi_idx': 0, 'aoi_data': viewer.images[0]['areas_of_interest'][0],
             'is_reference': True},
            {'image_idx': 1, 'aoi_idx': 0, 'aoi_data': aoi_data, 'is_reference': False},
        ]
        return controller

    def test_gallery_mode_uses_go_to_aoi(self, controller_with_results, viewer):
        viewer.gallery_mode = True
        viewer.gallery_controller.go_to_aoi.return_value = True

        controller_with_results._on_result_clicked(1)

        viewer.gallery_controller.go_to_aoi.assert_called_once_with(1, 0)
        viewer.gallery_controller.on_aoi_clicked.assert_not_called()

    def test_gallery_mode_falls_back_when_filtered_out(self, controller_with_results, viewer):
        viewer.gallery_mode = True
        viewer.gallery_controller.go_to_aoi.return_value = False

        controller_with_results._on_result_clicked(1)

        viewer.gallery_controller.on_aoi_clicked.assert_called_once_with(
            1, 0, viewer.images[1]['areas_of_interest'][0])

    def test_single_image_mode_uses_on_aoi_clicked(self, controller_with_results, viewer):
        viewer.gallery_mode = False

        controller_with_results._on_result_clicked(1)

        viewer.gallery_controller.go_to_aoi.assert_not_called()
        viewer.gallery_controller.on_aoi_clicked.assert_called_once()

    def test_out_of_range_row_ignored(self, controller_with_results, viewer):
        controller_with_results._on_result_clicked(99)
        viewer.gallery_controller.go_to_aoi.assert_not_called()
        viewer.gallery_controller.on_aoi_clicked.assert_not_called()


# ---------------------------------------------------------------------------
# End-to-end thread plumbing
# ---------------------------------------------------------------------------

class TestThreadedFlows:

    def test_success_flow_with_mocked_service(self, controller, viewer, qtbot, monkeypatch):
        fake_service = MagicMock()
        results = [{'image_idx': 1, 'aoi_idx': 0, 'similarity': 88, 'is_reference': False,
                    'aoi_data': viewer.images[1]['areas_of_interest'][0]}]
        fake_service.find_similar.return_value = results
        reference_entry = {'image_idx': 0, 'aoi_idx': 0, 'similarity': 100, 'is_reference': True}
        fake_service.build_reference_entry.return_value = reference_entry
        controller._similarity_service = fake_service

        shown = MagicMock()
        monkeypatch.setattr(controller, '_show_results_dialog', shown)

        with qtbot.waitSignal(controller.search_completed, timeout=5000):
            controller.find_similar_for_selected(image_idx=0, aoi_idx=0)

        shown.assert_called_once()
        displayed = shown.call_args[0][0]
        # Compare field-by-field rather than by deep equality: the payload
        # crosses a Signal(list) between threads, and Qt's meta-type
        # marshalling rewrites nested tuples as lists (aoi_data['center']
        # arrives as [200, 200], not (200, 200)).
        assert len(displayed) == 2
        assert displayed[0]['is_reference'] is True
        assert displayed[0]['image_idx'] == 0
        assert displayed[1]['image_idx'] == 1
        assert displayed[1]['similarity'] == 88
        assert list(displayed[1]['aoi_data']['center']) == [200, 200]
        assert controller._thread is None
        assert controller.progress_dialog is None

    def test_error_flow_with_real_service(self, controller, qtbot, monkeypatch):
        """Nonexistent images and no thumbnail cache -> the reference AOI cannot be
        analyzed -> worker error -> warning dialog and search_error signal."""
        warning = MagicMock()
        monkeypatch.setattr(QMessageBox, 'warning', warning)

        with qtbot.waitSignal(controller.search_error, timeout=5000):
            controller.find_similar_for_selected(image_idx=0, aoi_idx=0)

        warning.assert_called_once()
        assert controller._thread is None
        assert controller.progress_dialog is None


# ---------------------------------------------------------------------------
# Bulk actions
# ---------------------------------------------------------------------------

class TestBulkActions:

    @pytest.fixture
    def controller_with_results(self, controller, viewer):
        controller._current_results = [
            {'image_idx': 0, 'aoi_idx': 0, 'is_reference': True,
             'aoi_data': viewer.images[0]['areas_of_interest'][0]},
            {'image_idx': 1, 'aoi_idx': 0, 'is_reference': False,
             'aoi_data': viewer.images[1]['areas_of_interest'][0]},
        ]
        controller._results_dialog = MagicMock()
        return controller

    def test_entries_for_rows_drops_out_of_range(self, controller_with_results):
        entries = controller_with_results._entries_for_rows([0, 1, 99, -1])
        assert len(entries) == 2
        assert [entry['image_idx'] for entry in entries] == [0, 1]

    def test_bulk_flag_applies_and_refreshes(self, controller_with_results, viewer):
        viewer.status_controller = MagicMock()
        viewer.aoi_controller.set_aoi_flags_bulk.return_value = 2

        controller_with_results._on_bulk_flag([0, 1], True)

        viewer.aoi_controller.set_aoi_flags_bulk.assert_called_once_with(
            [(0, 0), (1, 0)], True)
        controller_with_results._results_dialog.refresh_status_badges.assert_called_once()
        viewer.status_controller.show_toast.assert_called_once()

    def test_bulk_unflag(self, controller_with_results, viewer):
        viewer.aoi_controller.set_aoi_flags_bulk.return_value = 2

        controller_with_results._on_bulk_flag([0, 1], False)

        viewer.aoi_controller.set_aoi_flags_bulk.assert_called_once_with(
            [(0, 0), (1, 0)], False)

    def test_bulk_flag_no_valid_rows_is_noop(self, controller_with_results, viewer):
        controller_with_results._on_bulk_flag([99], True)
        viewer.aoi_controller.set_aoi_flags_bulk.assert_not_called()

    def test_bulk_comment_applies_text(self, controller_with_results, viewer):
        viewer.aoi_controller.set_aoi_comments_bulk.return_value = 2

        with patch('core.views.images.viewer.dialogs.AOICommentDialog.AOICommentDialog') as dialog_cls:
            dialog_cls.return_value.exec.return_value = True
            dialog_cls.return_value.get_comment.return_value = 'orange tarp'
            controller_with_results._on_bulk_comment([0, 1])

        viewer.aoi_controller.set_aoi_comments_bulk.assert_called_once_with(
            [(0, 0), (1, 0)], 'orange tarp')
        controller_with_results._results_dialog.refresh_status_badges.assert_called_once()

    def test_bulk_comment_prefills_common_comment(self, controller_with_results, viewer):
        for result in controller_with_results._current_results:
            result['aoi_data']['user_comment'] = 'same note'

        with patch('core.views.images.viewer.dialogs.AOICommentDialog.AOICommentDialog') as dialog_cls:
            dialog_cls.return_value.exec.return_value = False
            controller_with_results._on_bulk_comment([0, 1])

        assert dialog_cls.call_args[0][1] == 'same note'

    def test_bulk_comment_cancel_applies_nothing(self, controller_with_results, viewer):
        with patch('core.views.images.viewer.dialogs.AOICommentDialog.AOICommentDialog') as dialog_cls:
            dialog_cls.return_value.exec.return_value = False
            controller_with_results._on_bulk_comment([0, 1])

        viewer.aoi_controller.set_aoi_comments_bulk.assert_not_called()
