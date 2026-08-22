"""Tests for AOINeighborTrackingController (the Z shortcut).

Focused on the reported crash: pressing Z (AOI neighbour tracking) took the
entire application down with no Python traceback. The cause was a native
abort(), not an exception -- ``~QThread()`` calls ``qFatal()`` when the thread
is still running, so dropping the last Python reference to a live QThread kills
the process. Two defects combined to do exactly that:

* ``_on_progress`` called ``QApplication.processEvents()``, re-entering the
  event loop from inside a slot and delivering pending key events mid-search.
* ``track_selected_aoi`` had no in-flight guard, so the reentrant press ran
  ``self._thread = QThread()`` over a still-running thread.
"""

import inspect
import sys
from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QApplication, QWidget

from core.controllers.images.viewer.neighbor.AOINeighborTrackingController import (
    AOINeighborTrackingController,
    NeighborSearchWorker,
)


@pytest.fixture(scope='session')
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def viewer(app, tmp_path, qtbot):
    """Minimal viewer stand-in carrying the attributes the controller reads."""
    widget = QWidget()
    qtbot.addWidget(widget)
    widget.images = [
        {'path': str(tmp_path / 'DJI_0001.JPG'),
         'areas_of_interest': [{'center': (100, 100), 'radius': 20, 'area': 400}]},
        {'path': str(tmp_path / 'DJI_0002.JPG'),
         'areas_of_interest': [{'center': (200, 200), 'radius': 30, 'area': 600}]},
    ]
    widget.current_image = 0
    widget.current_image_array = None
    widget.xml_path = str(tmp_path / 'ADIAT_Data.xml')
    widget.aoi_controller = MagicMock()
    widget.gallery_mode = False
    return widget


@pytest.fixture
def controller(viewer):
    return AOINeighborTrackingController(viewer)


# --------------------------------------------------------------------------- #
#  The crash: reentrancy over a running QThread                               #
# --------------------------------------------------------------------------- #

class TestReentrancyGuard:

    def test_second_search_while_one_runs_is_ignored(self, controller, viewer):
        """The regression test for the Z-key crash.

        Without the guard this reassigned self._thread, dropping the last
        reference to a running QThread -> qFatal() -> abort().
        """
        running = MagicMock()
        controller._thread = running

        controller.track_selected_aoi(image_idx=0, aoi_idx=0)

        assert controller._thread is running, \
            "an in-flight search must not be replaced"
        viewer.aoi_controller.get_selected_aoi.assert_not_called()

    def test_guard_applies_to_single_image_path_too(self, controller, viewer):
        running = MagicMock()
        controller._thread = running
        controller.track_selected_aoi()
        assert controller._thread is running

    def test_on_progress_does_not_pump_the_event_loop(self, controller):
        """processEvents() inside a slot is what let a reentrant Z press in."""
        source = inspect.getsource(controller._on_progress)
        assert 'processEvents' not in source or 'does NOT call' in source
        assert 'QApplication.processEvents()' not in source.replace(
            'QApplication.processEvents().', ''
        ).split('"""')[-1], "the executable body must not pump events"

    def test_on_progress_updates_label_without_reentering(self, controller):
        dialog = MagicMock()
        controller.progress_dialog = dialog
        controller._on_progress("halfway")
        dialog.setLabelText.assert_called_once_with("halfway")

    def test_on_progress_with_no_dialog_is_safe(self, controller):
        controller.progress_dialog = None
        controller._on_progress("ignored")  # must not raise


# --------------------------------------------------------------------------- #
#  Thread teardown must never destroy a running QThread, nor block the GUI     #
# --------------------------------------------------------------------------- #

class TestThreadTeardown:

    def test_running_thread_is_retained_not_destroyed(self, controller):
        worker, thread = MagicMock(), MagicMock()
        thread.isRunning.return_value = True
        controller._worker, controller._thread = worker, thread

        controller._cleanup_thread()

        worker.cancel.assert_called_once()
        thread.quit.assert_called_once()
        thread.wait.assert_not_called(), "must not block the GUI thread"
        assert controller._thread is None
        assert controller._retiring[thread] is worker, \
            "a running QThread must stay referenced until it reports finished"

    def test_stopped_thread_is_released_immediately(self, controller):
        worker, thread = MagicMock(), MagicMock()
        thread.isRunning.return_value = False
        controller._worker, controller._thread = worker, thread

        controller._cleanup_thread()

        thread.wait.assert_called_once()
        assert thread not in controller._retiring

    def test_release_after_finished_drops_reference(self, controller):
        worker, thread = MagicMock(), MagicMock()
        thread.isRunning.return_value = True
        controller._worker, controller._thread = worker, thread
        controller._cleanup_thread()

        controller._release_thread(thread)

        assert thread not in controller._retiring

    def test_release_survives_deleted_cpp_object(self, controller):
        thread = MagicMock()
        thread.wait.side_effect = RuntimeError("already deleted")
        controller._retiring[thread] = None
        controller._release_thread(thread)
        assert thread not in controller._retiring

    def test_cleanup_with_no_thread_is_noop(self, controller):
        controller._cleanup_thread()
        assert controller._retiring == {}


# --------------------------------------------------------------------------- #
#  Cancellation                                                               #
# --------------------------------------------------------------------------- #

class TestCancellation:

    def test_cancel_sets_flag_and_cancels_worker(self, controller):
        worker, thread = MagicMock(), MagicMock()
        thread.isRunning.return_value = False
        controller._worker, controller._thread = worker, thread

        controller._on_cancelled()

        assert controller._cancelled is True
        worker.cancel.assert_called_once()

    def test_cancelled_search_does_not_open_the_gallery(self, controller, monkeypatch):
        """`finished` is queued, so it lands after the user cancelled."""
        shown = MagicMock()
        monkeypatch.setattr(controller, '_show_gallery_dialog', shown)
        controller._cancelled = True

        controller._on_search_complete([{'image_idx': 1, 'pixel_x': 5, 'pixel_y': 5}])

        shown.assert_not_called()

    def test_completed_search_still_opens_the_gallery(self, controller, monkeypatch):
        shown = MagicMock()
        monkeypatch.setattr(controller, '_show_gallery_dialog', shown)
        controller._cancelled = False

        results = [{'image_idx': 1, 'pixel_x': 5, 'pixel_y': 5}]
        controller._on_search_complete(results)

        # The gallery is told whether the result cap truncated the search, so
        # it can say "there are more" instead of presenting the cap as the
        # answer. A complete search reports False.
        shown.assert_called_once_with(results, False)

    def test_closing_progress_dialog_does_not_read_as_cancelled(self, controller,
                                                                monkeypatch):
        """QProgressDialog emits canceled() from its own closeEvent.

        If the handler is still connected when a *completed* search closes the
        dialog, the results are silently discarded as "cancelled".
        """
        shown = MagicMock()
        monkeypatch.setattr(controller, '_show_gallery_dialog', shown)

        dialog = MagicMock()

        def emit_canceled_on_close():
            controller._on_cancelled()

        dialog.close.side_effect = emit_canceled_on_close
        # Disconnecting is what prevents that; simulate a real disconnect by
        # making close() a no-op once canceled has been disconnected.
        disconnected = {'yes': False}

        def disconnect(_handler):
            disconnected['yes'] = True

        dialog.canceled.disconnect.side_effect = disconnect

        def close():
            if not disconnected['yes']:
                emit_canceled_on_close()

        dialog.close.side_effect = close
        controller.progress_dialog = dialog

        controller._on_search_complete([{'image_idx': 1, 'pixel_x': 5, 'pixel_y': 5}])

        dialog.canceled.disconnect.assert_called_once_with(controller._on_cancelled)
        assert controller._cancelled is False
        shown.assert_called_once()

    def test_close_progress_dialog_tolerates_missing_connection(self, controller):
        dialog = MagicMock()
        dialog.canceled.disconnect.side_effect = TypeError("not connected")
        controller.progress_dialog = dialog
        controller._close_progress_dialog()
        dialog.close.assert_called_once()
        assert controller.progress_dialog is None


# --------------------------------------------------------------------------- #
#  Worker contract                                                            #
# --------------------------------------------------------------------------- #

AOI = {'center': (100, 100), 'radius': 20, 'area': 400}


def _worker(service, **overrides):
    """A worker whose AOI GPS step the caller stubs, to test the search itself.

    The GPS calculation moved onto the worker -- it decodes the image and can
    query a DEM, which froze the GUI before the progress dialog could paint.
    """
    kwargs = dict(
        neighbor_service=service, images=[], current_image_idx=0,
        current_image={'path': 'a.jpg'}, aoi_data=AOI,
    )
    kwargs.update(overrides)
    return NeighborSearchWorker(**kwargs)


def _stub_gps(monkeypatch, result):
    """Point the worker's AOIService at a fixed estimate_aoi_gps result.

    Reached through sys.modules because the package __init__ re-exports the
    controller class under the module's own name, so a plain import of the
    dotted path binds the class rather than the module.
    """
    mod = sys.modules[
        'core.controllers.images.viewer.neighbor.AOINeighborTrackingController']
    service = MagicMock()
    service.estimate_aoi_gps.return_value = result
    monkeypatch.setattr(mod, 'AOIService', lambda *a, **k: service)
    return service


class _GPS:
    """Stand-in for AOIGPSResult."""

    terrain_elevation_m = 250.0

    def to_tuple(self):
        return (32.0, -97.0)


class TestWorker:

    def test_cancel_before_run_skips_the_service(self, app):
        service = MagicMock()
        worker = _worker(service)
        finished = []
        worker.finished.connect(lambda r, t, g: finished.append((r, t)))

        worker.cancel()
        worker.run()

        service.find_aoi_in_neighbors.assert_not_called()
        assert finished == [([], False)]

    def test_run_emits_results(self, app, monkeypatch):
        _stub_gps(monkeypatch, _GPS())
        service = MagicMock()
        service.find_aoi_in_neighbors.return_value = ([{'image_idx': 1}], False)
        worker = _worker(service)
        finished = []
        worker.finished.connect(lambda r, t, g: finished.append((r, t)))

        worker.run()

        assert finished == [([{'image_idx': 1}], False)]

    def test_truncation_is_reported_to_the_controller(self, app, monkeypatch):
        """A capped search must not present its cap as the answer."""
        _stub_gps(monkeypatch, _GPS())
        service = MagicMock()
        service.find_aoi_in_neighbors.return_value = ([{'image_idx': 1}], True)
        worker = _worker(service)
        finished = []
        worker.finished.connect(lambda r, t, g: finished.append((r, t)))

        worker.run()

        assert finished == [([{'image_idx': 1}], True)]

    def test_unavailable_gps_is_reported_without_searching(self, app, monkeypatch):
        """No AOI GPS means there is nothing to look for in the other images."""
        _stub_gps(monkeypatch, None)
        service = MagicMock()
        worker = _worker(service)
        unavailable = []
        worker.gps_unavailable.connect(lambda g: unavailable.append(True))

        worker.run()

        assert unavailable == [True]
        service.find_aoi_in_neighbors.assert_not_called()

    def test_the_aoi_gps_is_computed_on_the_worker(self, app, monkeypatch):
        """Regression: this ran on the GUI thread, freezing the window before
        the progress dialog could paint -- for seconds when a DEM tile had to
        be fetched, with no sign the Z press had registered."""
        gps_service = _stub_gps(monkeypatch, _GPS())
        service = MagicMock()
        service.find_aoi_in_neighbors.return_value = ([], False)

        _worker(service).run()

        gps_service.estimate_aoi_gps.assert_called_once()

    def test_service_exception_emits_error(self, app, monkeypatch):
        _stub_gps(monkeypatch, _GPS())
        service = MagicMock()
        service.find_aoi_in_neighbors.side_effect = RuntimeError("boom")
        worker = _worker(service)
        errors = []
        worker.error.connect(lambda message, g: errors.append(message))

        worker.run()

        assert errors == ["boom"]


# --------------------------------------------------------------------------- #
#  Full-flight search scope (Z must not be blind to detection-less images)    #
# --------------------------------------------------------------------------- #

class TestFullFlightSearchScope:
    """The search must cover the whole flight, not just the AOI-bearing subset.

    The result XML only carries images that produced detections, so handing
    ``parent.images`` to the neighbor search silently skipped every capture
    with no AOIs of its own -- exactly the images a reviewer wants Z to check.
    """

    def test_search_scope_prefers_source_images(self, controller, viewer, tmp_path):
        viewer.source_images = [
            {'path': str(tmp_path / 'DJI_0000.JPG'), 'name': 'DJI_0000.JPG', 'has_aoi': False},
            {'path': viewer.images[0]['path'], 'name': 'DJI_0001.JPG', 'has_aoi': True},
            {'path': str(tmp_path / 'DJI_0001_5.JPG'), 'name': 'DJI_0001_5.JPG', 'has_aoi': False},
            {'path': viewer.images[1]['path'], 'name': 'DJI_0002.JPG', 'has_aoi': True},
        ]

        images, idx = controller._build_search_scope(viewer.images[0], 0)

        assert images is viewer.source_images
        assert idx == 1  # located by path, not by viewer index

    def test_search_scope_falls_back_without_source_images(self, controller, viewer):
        images, idx = controller._build_search_scope(viewer.images[1], 1)

        assert images is viewer.images
        assert idx == 1

    def test_search_scope_falls_back_when_current_image_missing(self, controller, viewer, tmp_path):
        viewer.source_images = [
            {'path': str(tmp_path / 'OTHER.JPG'), 'name': 'OTHER.JPG', 'has_aoi': False},
        ]

        images, idx = controller._build_search_scope(viewer.images[0], 0)

        assert images is viewer.images
        assert idx == 0


class TestGalleryClickMapsToViewerIndex:
    """Result indices live in full-flight space; navigation lives in viewer space."""

    def test_click_navigates_by_path_not_search_index(self, controller, viewer):
        # Full-flight index 3 corresponds to the viewer's image 1
        controller._neighbor_results = [
            {'image_idx': 3, 'image_path': viewer.images[1]['path'],
             'image_name': 'DJI_0002.JPG', 'pixel_x': None, 'pixel_y': None},
        ]
        viewer._load_image = MagicMock()

        controller._on_gallery_image_clicked(3)

        assert viewer.current_image == 1
        viewer._load_image.assert_called_once()

    def test_click_on_detection_less_capture_does_not_navigate(self, controller, viewer, tmp_path):
        controller._neighbor_results = [
            {'image_idx': 2, 'image_path': str(tmp_path / 'NO_AOI.JPG'),
             'image_name': 'NO_AOI.JPG', 'pixel_x': 10, 'pixel_y': 10},
        ]
        viewer._load_image = MagicMock()
        before = viewer.current_image

        controller._on_gallery_image_clicked(2)

        assert viewer.current_image == before
        viewer._load_image.assert_not_called()

    def test_detection_less_results_are_labeled_in_the_gallery(self, controller, viewer,
                                                               monkeypatch, tmp_path):
        import core.views.images.viewer.dialogs.AOINeighborGalleryDialog as gallery_module
        monkeypatch.setattr(gallery_module, 'AOINeighborGalleryDialog', MagicMock())

        results = [
            {'image_idx': 1, 'image_path': viewer.images[0]['path'],
             'image_name': 'DJI_0001.JPG', 'thumbnail': None, 'pixel_x': 0, 'pixel_y': 0},
            {'image_idx': 5, 'image_path': str(tmp_path / 'NO_AOI.JPG'),
             'image_name': 'NO_AOI.JPG', 'thumbnail': None, 'pixel_x': 0, 'pixel_y': 0},
        ]

        controller._show_gallery_dialog(results)

        assert results[0]['image_name'] == 'DJI_0001.JPG'
        assert 'no detections' in results[1]['image_name']


# --------------------------------------------------------------------------- #
#  Cancellation actually stops the work (not just the bookkeeping)            #
# --------------------------------------------------------------------------- #

class TestCancellationStopsTheSearch:

    def test_worker_passes_a_cancel_hook_the_search_can_poll(self, app, monkeypatch):
        """Regression: cancel() set a flag find_aoi_in_neighbors never read.

        Qt cannot interrupt a Python slot mid-execution, so quit() and
        requestInterruption() do nothing to a running search. Without a polled
        hook the worker kept reading EXIF and decoding full-resolution images
        for the rest of the flight after the user cancelled.
        """
        _stub_gps(monkeypatch, _GPS())
        service = MagicMock()
        service.find_aoi_in_neighbors.return_value = ([], False)
        worker = _worker(service)
        worker.run()

        should_cancel = service.find_aoi_in_neighbors.call_args.kwargs['should_cancel']
        assert should_cancel() is False
        worker.cancel()
        assert should_cancel() is True, "cancel() must be visible to the search"

    def test_search_stops_at_the_next_image_once_cancelled(self):
        """The hook is polled per image, so the search abandons promptly."""
        from core.services.image.AOINeighborService import AOINeighborService

        service = AOINeighborService.__new__(AOINeighborService)
        service.logger = MagicMock()
        service._center_gps_cache = {}
        service._coverage_meta_cache = {}

        results, truncated = service.find_aoi_in_neighbors(
            images=[{'path': f'img{i}.jpg'} for i in range(50)],
            current_image_idx=0,
            aoi_gps=(32.0, -97.0),
            should_cancel=lambda: True,
        )

        assert results == []
        assert truncated is False


# --------------------------------------------------------------------------- #
#  A retired search must not act on the live one                              #
# --------------------------------------------------------------------------- #

class TestStaleWorkerIsIgnored:

    def test_cancelled_workers_late_finish_does_not_touch_the_new_search(self, controller):
        """The reachable sequence: cancel, press Z again, worker A finishes.

        Worker A is still running and still connected. Its queued `finished`
        lands after search B has started, and _cancelled has been reset to
        False by then -- so the handler used to tear down B's thread and
        report A's empty results as B's answer.
        """
        stale_generation = controller._generation
        controller._cleanup_thread()            # retires A, bumps the generation
        live_thread = MagicMock()
        controller._thread = live_thread        # B is now running
        controller._gallery_dialog = None

        controller._on_search_complete([], generation=stale_generation)

        assert controller._thread is live_thread, \
            "a stale finish must not tear down the running search"

    def test_stale_error_is_ignored_too(self, controller):
        stale_generation = controller._generation
        controller._cleanup_thread()
        live_thread = MagicMock()
        controller._thread = live_thread

        controller._on_search_error("boom", stale_generation)

        assert controller._thread is live_thread

    def test_current_generation_is_still_handled(self, controller):
        """The guard must not swallow the search the user is waiting on."""
        controller._thread = None
        controller._gallery_dialog = None
        shown = []
        controller._show_gallery_dialog = lambda results, truncated=False: shown.append(results)

        controller._on_search_complete([{'image_idx': 0}], generation=controller._generation)

        assert shown == [[{'image_idx': 0}]]

    def test_unstamped_calls_are_handled(self, controller):
        """Callers without a generation (tests, legacy) still work."""
        controller._thread = None
        controller._gallery_dialog = None
        shown = []
        controller._show_gallery_dialog = lambda results, truncated=False: shown.append(results)

        controller._on_search_complete([{'image_idx': 0}])

        assert shown == [[{'image_idx': 0}]]


# --------------------------------------------------------------------------- #
#  The search must complete on a REAL thread, with handlers on the GUI thread  #
# --------------------------------------------------------------------------- #

class TestRealThreadedRun:
    """Regression: the app froze at the last image of every search.

    The terminal signals were connected via lambdas. A lambda has no receiver
    QObject, so Qt cannot use the controller's thread affinity and resolves the
    connection as Direct -- the completion handler then ran ON THE WORKER
    THREAD, where _cleanup_thread waits on the very thread it is running on and
    the dialog calls touch GUI objects from the wrong thread. Deadlock, with
    the progress dialog stuck on "Checking image N of N".

    Every other test in this file drives the handlers by direct call, which
    cannot see a connection-type defect. This one runs the real thread.
    """

    def _run(self, controller, viewer, qtbot, monkeypatch, results, truncated=False):
        service = MagicMock()
        service.find_aoi_in_neighbors.return_value = (results, truncated)
        controller.neighbor_service = service
        _stub_gps(monkeypatch, _GPS())

        seen = {}
        monkeypatch.setattr(
            controller, '_show_gallery_dialog',
            lambda r, t=False: seen.update(
                results=r, truncated=t, thread=QThread.currentThread()))

        with qtbot.waitSignal(controller.tracking_completed, timeout=10000):
            controller.track_selected_aoi(image_idx=0, aoi_idx=0)
        return seen

    def test_search_completes_and_tears_down(self, controller, viewer, qtbot, monkeypatch):
        seen = self._run(controller, viewer, qtbot, monkeypatch,
                         [{'image_idx': 1, 'pixel_x': 5, 'pixel_y': 5}])

        assert seen['results'] == [{'image_idx': 1, 'pixel_x': 5, 'pixel_y': 5}]
        assert controller._thread is None, "the thread must be retired"
        assert controller.progress_dialog is None, "the progress dialog must close"

    def test_completion_runs_on_the_gui_thread(self, controller, viewer, qtbot, monkeypatch):
        """The actual defect: a Direct connection ran this on the worker."""
        seen = self._run(controller, viewer, qtbot, monkeypatch,
                         [{'image_idx': 1, 'pixel_x': 5, 'pixel_y': 5}])

        assert seen['thread'] is QApplication.instance().thread(),             "terminal handlers must be queued to the GUI thread"

    def test_truncation_reaches_the_gallery(self, controller, viewer, qtbot, monkeypatch):
        seen = self._run(controller, viewer, qtbot, monkeypatch,
                         [{'image_idx': 1, 'pixel_x': 5, 'pixel_y': 5}], truncated=True)

        assert seen['truncated'] is True
