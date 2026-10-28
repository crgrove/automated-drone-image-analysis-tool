"""Terrain downloads stop when the window that started them closes.

Qt deletes a window's children with it, and deleting a QThread that is still
running aborts the whole process ("QThread: Destroyed while thread '' is
still running"). So the Viewer and the MainWindow stop their downloads on
close, and the MainWindow closes a viewer before replacing it, because a
replaced viewer is deleted without a closeEvent.
"""

import os
import subprocess
import sys
import textwrap
import threading
import time
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow

from core.controllers.images.TerrainAcquisitionController import TerrainAcquisitionController
from core.controllers.images.viewer.Viewer import Viewer
from core.services.terrain.TerrainAcquisitionService import AcquisitionOutcome

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))


def _service(honours_cancel=True, seconds=10.0):
    """A service whose run() plans for ``seconds``, checking cancel_check every 10 ms or not at all."""
    started = threading.Event()

    def run(images=None, bounds=None, trigger=None, cancel_check=None):
        started.set()
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if honours_cancel and cancel_check():
                return AcquisitionOutcome(trigger=trigger, cancelled=True)
            time.sleep(0.01)
        return AcquisitionOutcome(trigger=trigger)

    service = MagicMock()
    service.enabled.return_value = True
    service.run.side_effect = run
    service.started = started
    return service


def _start(owner, service):
    """Start one download for ``owner`` and return its worker once it is inside run()."""
    controller = TerrainAcquisitionController(parent=owner, settings_service=MagicMock(), logger=MagicMock())
    with patch('core.controllers.images.TerrainAcquisitionController.TerrainAcquisitionService', return_value=service):
        assert controller.ensure(images=[{'path': 'a.jpg'}])
    assert service.started.wait(5)
    return controller._worker


@pytest.fixture
def owner(qtbot):
    """A window standing in for the Viewer: closeEvent iterates its thumbnail threads, of which it has none."""
    window = QMainWindow()
    window._threads = []
    yield window
    TerrainAcquisitionController.stop_all(window)      # never leave a running thread for Qt to delete


class TestStopAll:
    def test_planning_that_checks_cancel_stops_promptly(self, owner):
        worker = _start(owner, _service())
        t = time.monotonic()

        TerrainAcquisitionController.stop_all(owner)

        assert not worker.isRunning()
        assert time.monotonic() - t < 2.0              # planning alone would take 10 s

    def test_planning_that_ignores_cancel_is_waited_out(self, owner):
        worker = _start(owner, _service(honours_cancel=False, seconds=0.3))

        TerrainAcquisitionController.stop_all(owner)

        assert not worker.isRunning()

    def test_every_download_of_the_owner_is_stopped(self, owner):
        """Exports start a new controller each time, while an older one may still run."""
        workers = [_start(owner, _service()), _start(owner, _service())]

        TerrainAcquisitionController.stop_all(owner)

        assert not any(worker.isRunning() for worker in workers)

    def test_nothing_running_is_a_no_op(self, owner):
        TerrainAcquisitionController.stop_all(owner)


def test_closing_the_viewer_stops_its_downloads(owner):
    worker = _start(owner, _service())
    event = QCloseEvent()

    Viewer.closeEvent(owner, event)

    assert not worker.isRunning()
    assert event.isAccepted()


@pytest.fixture
def window(main_window):
    yield main_window
    TerrainAcquisitionController.stop_all(main_window)     # never leave a running thread for Qt to delete


def test_closing_the_main_window_stops_its_downloads(window):
    worker = _start(window, _service())

    window.close()

    assert not worker.isRunning()


@pytest.fixture
def viewers():
    """MainWindow's Viewer class replaced by mocks, one per window opened."""
    with patch('core.controllers.images.MainWindow.Viewer', side_effect=lambda *a, **k: MagicMock()) as viewer_class:
        yield viewer_class


def test_viewing_results_again_closes_the_previous_viewer(main_window, viewers, tmp_path):
    xml = tmp_path / 'ADIAT_Data.xml'
    xml.write_text('<data/>')
    main_window.results_path = str(xml)

    main_window._viewResultsButton_clicked()
    first = main_window.viewer
    main_window._viewResultsButton_clicked()

    first.close.assert_called_once()
    main_window.viewer.close.assert_not_called()


def test_opening_results_from_a_folder_scan_closes_the_previous_viewer(main_window, viewers, tmp_path):
    xml = str(tmp_path / 'ADIAT_Data.xml')

    main_window._open_viewer_from_path(xml)
    first = main_window.viewer
    main_window._open_viewer_from_path(xml)

    first.close.assert_called_once()
    main_window.viewer.close.assert_not_called()


def test_replacing_the_owner_after_stop_all_does_not_abort():
    """The crash itself, in a child process: an abort here would otherwise take pytest down with it."""
    script = textwrap.dedent(f"""
        import sys, time
        sys.path.insert(0, {APP_DIR!r})
        from PySide6.QtWidgets import QApplication, QWidget
        app = QApplication([])
        import core.controllers.images.TerrainAcquisitionController as C
        from core.services.terrain.TerrainAcquisitionService import AcquisitionOutcome

        class SlowService:
            # planning that ignores cancellation: the longest stop_all ever has to wait
            def __init__(self, *args, **kwargs):
                pass

            def enabled(self):
                return True

            def run(self, images, bounds, trigger, cancel_check):
                time.sleep(1.0)
                return AcquisitionOutcome(trigger=trigger, cancelled=True)

        C.TerrainAcquisitionService = SlowService
        owner = QWidget()
        controller = C.TerrainAcquisitionController(parent=owner)
        assert controller.ensure(images=[{{'path': 'a.jpg'}}])
        C.TerrainAcquisitionController.stop_all(owner)
        owner = QWidget()      # what MainWindow does when it replaces self.viewer
        print('survived')
    """)
    env = dict(os.environ, QT_QPA_PLATFORM='offscreen')
    result = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True, timeout=120, env=env)

    assert result.returncode == 0, result.stderr
    assert 'survived' in result.stdout
