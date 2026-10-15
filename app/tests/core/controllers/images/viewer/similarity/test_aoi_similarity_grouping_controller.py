"""
Tests for the "Similar & Nearby" sort flow in AOISimilarityController.

Covers SimilarityGroupingWorker signals, start guards, applying/restoring the
sort on completion, cancel and error, and the end-to-end
QThread plumbing with a mocked grouping service.
"""

import sys

import pytest
from unittest.mock import MagicMock
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget

from core.controllers.images.viewer.similarity.AOISimilarityController import (
    AOISimilarityController,
    SimilarityGroupingWorker,
)
from core.services.image.AOISimilarityGroupingService import SimilarityGroupingResult

# The package re-exports the class under the module's name, so patch via sys.modules
controller_module = sys.modules[AOISimilarityController.__module__]


@pytest.fixture(scope='session')
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def viewer(app, tmp_path, qtbot):
    widget = QWidget()
    qtbot.addWidget(widget)
    widget.images = [
        {'path': str(tmp_path / 'DJI_0001.JPG'),
         'areas_of_interest': [{'center': (100, 100), 'radius': 20, 'area': 400}]},
        {'path': str(tmp_path / 'DJI_0002.JPG'),
         'areas_of_interest': [{'center': (200, 200), 'radius': 30, 'area': 600}]},
    ]
    widget.current_image = 0
    widget.xml_path = str(tmp_path / 'ADIAT_Data.xml')
    widget.aoi_controller = MagicMock()
    widget.gallery_controller = MagicMock()
    widget.status_controller = MagicMock()
    widget.gallery_mode = False
    return widget


@pytest.fixture
def controller(viewer):
    return AOISimilarityController(viewer)


def make_result(groups=((0, 0), (1, 0)), unlocated=0):
    order = [(0, 0), (1, 0)]
    return SimilarityGroupingResult(
        order=order,
        ranks={('a', 0, 0): 0, ('b', 0, 0): 1},
        groups=[list(groups)] if groups else [],
        unlocated_count=unlocated,
    )


class TestGroupingWorker:

    def test_run_emits_progress_then_result(self, app):
        service = MagicMock()
        result = make_result()

        def fake_group(**kwargs):
            kwargs['progress_callback'](1, 2)
            assert kwargs['max_distance_m'] == 15.0
            assert kwargs['min_similarity'] == 70
            return result

        service.group.side_effect = fake_group
        worker = SimilarityGroupingWorker(service, [], MagicMock(), 15.0, 70)
        progress, finished = [], []
        worker.progress.connect(lambda done, total: progress.append((done, total)))
        worker.finished.connect(finished.append)
        worker.run()

        assert progress == [(1, 2)]
        assert finished == [result]

    def test_cancel_before_run_skips_service(self, app):
        service = MagicMock()
        worker = SimilarityGroupingWorker(service, [], MagicMock(), 15.0, 70)
        finished = []
        worker.finished.connect(finished.append)
        worker.cancel()
        worker.run()
        assert finished == [None]
        service.group.assert_not_called()

    def test_service_exception_emits_error(self, app):
        service = MagicMock()
        service.group.side_effect = ValueError("bad distance")
        worker = SimilarityGroupingWorker(service, [], MagicMock(), 15.0, 70)
        errors = []
        worker.error.connect(errors.append)
        worker.run()
        assert errors == ["bad distance"]


class TestStartGuards:

    def test_busy_controller_does_not_start(self, controller):
        controller._thread = MagicMock()
        assert controller.sort_by_similarity_groups(15.0, 70) is False

    def test_dataset_without_aois_does_not_start(self, controller, viewer):
        viewer.images = [{'path': 'a.jpg', 'areas_of_interest': []}]
        assert controller.sort_by_similarity_groups(15.0, 70) is False


class TestGroupingCompletion:

    def test_result_is_applied_and_summarized(self, controller, viewer):
        result = make_result()
        emitted = []
        controller.grouping_completed.connect(emitted.append)
        controller._cancelled = False

        controller._on_grouping_complete(result)

        viewer.aoi_controller.apply_similarity_groups.assert_called_once_with(result)
        viewer.status_controller.show_toast.assert_called_once()
        assert "1 group" in viewer.status_controller.show_toast.call_args[0][0]
        assert emitted == [result]

    def test_no_groups_still_applies_with_hint(self, controller, viewer):
        controller._cancelled = False
        controller._on_grouping_complete(make_result(groups=None))
        viewer.aoi_controller.apply_similarity_groups.assert_called_once()
        assert "No similar AOIs" in viewer.status_controller.show_toast.call_args[0][0]

    def test_unlocated_aois_are_mentioned(self, controller, viewer):
        controller._cancelled = False
        controller._on_grouping_complete(make_result(unlocated=1))
        assert "1 AOI(s) without a GPS position" in viewer.status_controller.show_toast.call_args[0][0]

    def test_no_positions_at_all_keeps_previous_sort(self, controller, viewer, monkeypatch):
        info = MagicMock()
        monkeypatch.setattr(QMessageBox, 'information', info)
        controller._cancelled = False

        controller._on_grouping_complete(make_result(groups=None, unlocated=2))

        info.assert_called_once()
        viewer.aoi_controller.apply_similarity_groups.assert_not_called()
        viewer.aoi_controller.restore_sort_selection.assert_called_once()

    def test_cancelled_completion_is_silent(self, controller, viewer):
        controller._cancelled = True
        controller._on_grouping_complete(None)
        viewer.aoi_controller.apply_similarity_groups.assert_not_called()

    def test_error_restores_sort_and_warns(self, controller, viewer, monkeypatch):
        warning = MagicMock()
        monkeypatch.setattr(QMessageBox, 'warning', warning)
        errors = []
        controller.grouping_error.connect(errors.append)
        controller._cancelled = False

        controller._on_grouping_error("boom")

        warning.assert_called_once()
        viewer.aoi_controller.restore_sort_selection.assert_called_once()
        assert errors == ["boom"]

    def test_cancel_restores_sort(self, controller, viewer):
        controller._grouping = True
        controller._on_cancelled()
        viewer.aoi_controller.restore_sort_selection.assert_called_once()

    def test_cancelling_a_search_does_not_touch_the_sort(self, controller, viewer):
        controller._grouping = False
        controller._on_cancelled()
        viewer.aoi_controller.restore_sort_selection.assert_not_called()

    def test_completion_during_progress_pump_is_deferred(self, controller, viewer):
        result = make_result()
        controller._cancelled = False
        dialog = MagicMock()
        dialog.maximum.return_value = 0
        dialog.setValue.side_effect = lambda value: controller._on_grouping_complete(result)
        controller.progress_dialog = dialog

        controller._on_progress(1, 2)

        viewer.aoi_controller.apply_similarity_groups.assert_called_once_with(result)


class TestThreadedGrouping:

    def test_success_flow_with_mocked_grouping(self, controller, viewer, qtbot, monkeypatch):
        result = make_result()
        grouping_cls = MagicMock()
        grouping_cls.return_value.group.return_value = result
        monkeypatch.setattr(controller_module, 'AOISimilarityGroupingService', grouping_cls)

        with qtbot.waitSignal(controller.grouping_completed, timeout=5000) as blocker:
            assert controller.sort_by_similarity_groups(20.0, 80) is True

        assert blocker.args == [result]  # object signal: the dataclass arrives intact
        kwargs = grouping_cls.return_value.group.call_args.kwargs
        assert kwargs['max_distance_m'] == 20.0
        assert kwargs['min_similarity'] == 80
        assert kwargs['images'] is viewer.images
        viewer.aoi_controller.apply_similarity_groups.assert_called_once_with(result)
        assert controller._thread is None
        assert controller.progress_dialog is None

    def test_viewer_gps_settings_reach_the_locator(self, controller, viewer, qtbot, monkeypatch):
        grouping_cls = MagicMock()
        grouping_cls.return_value.group.return_value = make_result()
        make_locator = MagicMock()
        monkeypatch.setattr(controller_module, 'AOISimilarityGroupingService', grouping_cls)
        monkeypatch.setattr(controller_module, 'make_aoi_locator', make_locator)
        viewer.custom_agl_altitude_ft = 300
        viewer.use_terrain_elevation = False

        with qtbot.waitSignal(controller.grouping_completed, timeout=5000):
            controller.sort_by_similarity_groups(15.0, 70)

        make_locator.assert_called_once_with(custom_altitude_ft=300, use_terrain=False)
        assert grouping_cls.return_value.group.call_args.kwargs['locate_aois'] is make_locator.return_value

    def test_error_flow_with_mocked_grouping(self, controller, viewer, qtbot, monkeypatch):
        grouping_cls = MagicMock()
        grouping_cls.return_value.group.side_effect = RuntimeError("no luck")
        monkeypatch.setattr(controller_module, 'AOISimilarityGroupingService', grouping_cls)
        monkeypatch.setattr(QMessageBox, 'warning', MagicMock())

        with qtbot.waitSignal(controller.grouping_error, timeout=5000):
            controller.sort_by_similarity_groups(15.0, 70)

        viewer.aoi_controller.restore_sort_selection.assert_called_once()
        assert controller._thread is None
