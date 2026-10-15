"""
Tests for duplicate marking in AOISimilarityController: the D-key flow
(candidate ranking worker -> picker -> AOIController) and the Find Similar
dialog's Mark Duplicate / Not Duplicate bulk actions.
"""

import numpy as np
import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QApplication, QWidget

from core.controllers.images.viewer.similarity.AOISimilarityController import (
    AOISimilarityController,
    DuplicateCandidateWorker,
)
from core.services.AOIDuplicateService import DuplicateChange

CONTROLLER_MODULE = 'core.controllers.images.viewer.similarity.AOISimilarityController'
PICKER = 'core.views.images.viewer.dialogs.AOIDuplicatePickerDialog.AOIDuplicatePickerDialog'


@pytest.fixture(scope='session')
def app():
    return QApplication.instance() or QApplication([])


def _images(tmp_path):
    """#1 flagged (image 0), #2 unflagged (image 0), #3 unflagged (image 1)."""
    return [
        {'path': str(tmp_path / 'DJI_0001.JPG'), 'name': 'DJI_0001.JPG',
         'areas_of_interest': [{'center': (100, 100), 'radius': 20, 'area': 400, 'number': 1, 'flagged': True},
                               {'center': (300, 300), 'radius': 20, 'area': 400, 'number': 2}]},
        {'path': str(tmp_path / 'DJI_0002.JPG'), 'name': 'DJI_0002.JPG',
         'areas_of_interest': [{'center': (200, 200), 'radius': 30, 'area': 600, 'number': 3}]},
    ]


@pytest.fixture
def viewer(app, tmp_path, qtbot):
    widget = QWidget()
    qtbot.addWidget(widget)
    widget.images = _images(tmp_path)
    widget.current_image = 0
    widget.xml_path = str(tmp_path / 'ADIAT_Data.xml')
    widget.distance_unit = 'm'
    widget.aoi_controller = MagicMock()
    widget.aoi_controller.unmark_duplicate.return_value = False
    widget.gallery_controller = MagicMock()
    widget.status_controller = MagicMock()
    widget.gallery_mode = False
    return widget


@pytest.fixture
def controller(viewer):
    return AOISimilarityController(viewer)


def _fake_service():
    service = MagicMock()
    service.get_descriptor.side_effect = lambda path, aoi: aoi['number']
    service.compare.return_value = 0.1
    service.get_crop.return_value = np.zeros((180, 180, 3), dtype=np.uint8)
    return service


# ---------------------------------------------------------------------------
# DuplicateCandidateWorker
# ---------------------------------------------------------------------------

class TestDuplicateCandidateWorker:

    def test_run_emits_ranked_candidates_with_thumbnails(self, app, tmp_path):
        images = _images(tmp_path)
        worker = DuplicateCandidateWorker(_fake_service(), images, (1, 0), [(0, 0), (0, 1)],
                                          locate_aois=None)
        finished = []
        worker.finished.connect(finished.append)

        worker.run()

        payload = finished[0]
        assert payload['source']['number'] == 3
        assert payload['source']['image_name'] == 'DJI_0002.JPG'
        assert payload['source']['thumbnail'] is not None
        assert [entry['candidate'].number for entry in payload['candidates']] == [1, 2]
        assert payload['candidates'][0]['candidate'].similarity == 90
        assert payload['candidates'][0]['thumbnail'] is not None

    def test_candidates_are_capped(self, app, tmp_path, monkeypatch):
        monkeypatch.setattr(DuplicateCandidateWorker, 'MAX_CANDIDATES', 1)
        worker = DuplicateCandidateWorker(_fake_service(), _images(tmp_path), (1, 0), [(0, 0), (0, 1)], None)
        finished = []
        worker.finished.connect(finished.append)

        worker.run()

        assert len(finished[0]['candidates']) == 1

    def test_unreadable_thumbnail_is_none(self, app, tmp_path):
        service = _fake_service()
        service.get_crop.side_effect = OSError("gone")
        worker = DuplicateCandidateWorker(service, _images(tmp_path), (1, 0), [(0, 0)], None)
        finished = []
        worker.finished.connect(finished.append)

        worker.run()

        assert finished[0]['source']['thumbnail'] is None
        assert finished[0]['candidates'][0]['thumbnail'] is None

    def test_cancel_emits_none(self, app, tmp_path):
        worker = DuplicateCandidateWorker(_fake_service(), _images(tmp_path), (1, 0), [(0, 0)], None)
        finished = []
        worker.finished.connect(finished.append)

        worker.cancel()
        worker.run()

        assert finished == [None]

    def test_exception_emits_error(self, app, tmp_path):
        worker = DuplicateCandidateWorker(_fake_service(), _images(tmp_path), (1, 0), [(0, 0)], None)
        errors = []
        worker.error.connect(errors.append)

        with patch(f'{CONTROLLER_MODULE}.AOIDuplicateService.rank_candidates', side_effect=RuntimeError("boom")):
            worker.run()

        assert errors == ["boom"]


# ---------------------------------------------------------------------------
# mark_duplicate_for_selected
# ---------------------------------------------------------------------------

class TestMarkDuplicateEntry:

    def test_d_on_a_duplicate_unmarks_without_a_search(self, controller, viewer):
        viewer.aoi_controller.unmark_duplicate.return_value = True
        controller._start_worker = MagicMock()

        controller.mark_duplicate_for_selected(image_idx=0, aoi_idx=1)

        viewer.aoi_controller.unmark_duplicate.assert_called_once_with(0, 1)
        controller._start_worker.assert_not_called()

    def test_no_candidates_explains_what_to_do(self, controller, viewer):
        viewer.images[0]['areas_of_interest'][0]['flagged'] = False
        controller._start_worker = MagicMock()

        with patch(f'{CONTROLLER_MODULE}.QMessageBox.information') as info:
            controller.mark_duplicate_for_selected(image_idx=1, aoi_idx=0)

        info.assert_called_once()
        assert 'Flag' in info.call_args[0][2]
        controller._start_worker.assert_not_called()

    def test_no_selection_shows_message(self, controller, viewer):
        viewer.aoi_controller.get_selected_aoi.return_value = None

        with patch(f'{CONTROLLER_MODULE}.QMessageBox.information') as info:
            controller.mark_duplicate_for_selected()

        info.assert_called_once()

    def test_single_image_selection_uses_current_image(self, controller, viewer):
        viewer.current_image = 1
        viewer.aoi_controller.get_selected_aoi.return_value = ({}, 0)
        controller._start_worker = MagicMock()

        controller.mark_duplicate_for_selected()

        worker = controller._start_worker.call_args[0][0]
        assert worker.source == (1, 0)
        assert worker.candidates == [(0, 0)]

    @pytest.mark.parametrize('image_idx, aoi_idx', [(5, 0), (0, 9), (-1, 0)])
    def test_invalid_indices_are_ignored(self, controller, viewer, image_idx, aoi_idx):
        controller._start_worker = MagicMock()

        controller.mark_duplicate_for_selected(image_idx=image_idx, aoi_idx=aoi_idx)

        controller._start_worker.assert_not_called()

    def test_progress_only_shows_when_ranking_is_slow(self, controller):
        controller._start_worker = MagicMock()

        controller.mark_duplicate_for_selected(image_idx=1, aoi_idx=0)

        assert controller._start_worker.call_args.kwargs['min_duration_ms'] == 500

    def test_busy_controller_ignores_the_key(self, controller):
        controller._thread = MagicMock()
        controller._start_worker = MagicMock()

        controller.mark_duplicate_for_selected(image_idx=1, aoi_idx=0)

        controller._start_worker.assert_not_called()


# ---------------------------------------------------------------------------
# Picker -> AOIController
# ---------------------------------------------------------------------------

def _candidate(image_idx=0, aoi_idx=0):
    candidate = MagicMock()
    candidate.image_idx, candidate.aoi_idx = image_idx, aoi_idx
    return candidate


def _payload():
    return {'source': {'image_idx': 1, 'aoi_idx': 0, 'number': 3, 'image_name': 'DJI_0002.JPG',
                       'thumbnail': None},
            'candidates': [{'candidate': _candidate(), 'thumbnail': None}]}


class TestPickerCompletion:

    def test_accepted_choice_is_stored(self, controller, viewer):
        viewer.aoi_controller.set_aoi_duplicates_bulk.return_value = DuplicateChange(
            primary=(0, 0), changed=[(1, 0)], touched=[(1, 0)])

        with patch(PICKER) as picker_cls:
            picker_cls.return_value.exec.return_value = True
            picker_cls.return_value.selected_candidate.return_value = _candidate(0, 0)
            controller._on_duplicate_candidates_complete(_payload())

        picker_cls.assert_called_once()
        assert picker_cls.call_args.kwargs['distance_unit'] == 'm'
        viewer.aoi_controller.set_aoi_duplicates_bulk.assert_called_once_with([(1, 0)], (0, 0))
        message = viewer.status_controller.show_toast.call_args[0][0]
        assert message == "AOI #3 marked as a duplicate of AOI #1"

    def test_cancelled_picker_marks_nothing(self, controller, viewer):
        with patch(PICKER) as picker_cls:
            picker_cls.return_value.exec.return_value = False
            controller._on_duplicate_candidates_complete(_payload())

        viewer.aoi_controller.set_aoi_duplicates_bulk.assert_not_called()

    def test_cancelled_ranking_shows_no_picker(self, controller):
        with patch(PICKER) as picker_cls:
            controller._on_duplicate_candidates_complete(None)
        picker_cls.assert_not_called()

    def test_error_is_reported(self, controller):
        with patch(f'{CONTROLLER_MODULE}.QMessageBox.warning') as warning:
            controller._on_duplicate_candidates_error("no metadata")
        assert "no metadata" in warning.call_args[0][2]

    def test_threaded_flow_end_to_end(self, controller, viewer, qtbot):
        controller._similarity_service = _fake_service()
        viewer.aoi_controller.set_aoi_duplicates_bulk.return_value = DuplicateChange(
            primary=(0, 0), changed=[(1, 0)], touched=[(1, 0)])

        with patch(f'{CONTROLLER_MODULE}.make_aoi_locator', return_value=lambda image: []), \
                patch(PICKER) as picker_cls:
            picker_cls.return_value.exec.return_value = True
            picker_cls.return_value.selected_candidate.side_effect = (
                lambda: picker_cls.call_args[0][2][0]['candidate'])
            controller.mark_duplicate_for_selected(image_idx=1, aoi_idx=0)
            qtbot.waitUntil(lambda: viewer.aoi_controller.set_aoi_duplicates_bulk.called, timeout=5000)

        viewer.aoi_controller.set_aoi_duplicates_bulk.assert_called_once_with([(1, 0)], (0, 0))
        qtbot.waitUntil(lambda: not controller._retiring, timeout=5000)


class TestMarkDuplicatesToast:

    def test_unflagged_primary_warns_it_is_not_reported(self, controller, viewer):
        viewer.aoi_controller.set_aoi_duplicates_bulk.return_value = DuplicateChange(
            primary=(0, 1), changed=[(1, 0)], touched=[(1, 0)])

        controller._mark_duplicates([(1, 0)], (0, 1))

        message = viewer.status_controller.show_toast.call_args[0][0]
        assert "not flagged" in message
        assert viewer.status_controller.show_toast.call_args.kwargs['color'] == "#FFA726"

    def test_nothing_changed_says_so(self, controller, viewer):
        viewer.aoi_controller.set_aoi_duplicates_bulk.return_value = DuplicateChange(primary=(0, 0))

        controller._mark_duplicates([(1, 0)], (0, 0))

        assert "Already" in viewer.status_controller.show_toast.call_args[0][0]

    def test_unusable_primary_is_silent(self, controller, viewer):
        viewer.aoi_controller.set_aoi_duplicates_bulk.return_value = DuplicateChange()

        controller._mark_duplicates([(1, 0)], (0, 0))

        viewer.status_controller.show_toast.assert_not_called()


# ---------------------------------------------------------------------------
# Find Similar dialog bulk actions
# ---------------------------------------------------------------------------

class TestBulkDuplicate:

    @pytest.fixture
    def controller_with_results(self, controller, viewer):
        controller._current_results = [
            {'image_idx': 0, 'aoi_idx': 0, 'is_reference': True, 'aoi_data': viewer.images[0]['areas_of_interest'][0]},
            {'image_idx': 0, 'aoi_idx': 1, 'aoi_data': viewer.images[0]['areas_of_interest'][1]},
            {'image_idx': 1, 'aoi_idx': 0, 'aoi_data': viewer.images[1]['areas_of_interest'][0]},
        ]
        controller._results_dialog = MagicMock()
        return controller

    def test_mark_links_checked_rows_to_the_reference(self, controller_with_results, viewer):
        viewer.aoi_controller.set_aoi_duplicates_bulk.return_value = DuplicateChange(
            primary=(0, 0), changed=[(0, 1), (1, 0)], touched=[(0, 1), (1, 0)])

        controller_with_results._on_bulk_duplicate([1, 2], True)

        viewer.aoi_controller.set_aoi_duplicates_bulk.assert_called_once_with([(0, 1), (1, 0)], (0, 0))
        controller_with_results._results_dialog.refresh_status_badges.assert_called_once()
        assert "Marked 2 AOI(s) as duplicates of AOI #1" in viewer.status_controller.show_toast.call_args[0][0]

    def test_not_duplicate_clears_checked_rows(self, controller_with_results, viewer):
        viewer.aoi_controller.clear_aoi_duplicates_bulk.return_value = DuplicateChange(
            changed=[(0, 1)], touched=[(0, 1)])

        controller_with_results._on_bulk_duplicate([1], False)

        viewer.aoi_controller.clear_aoi_duplicates_bulk.assert_called_once_with([(0, 1)])
        controller_with_results._results_dialog.refresh_status_badges.assert_called_once()

    def test_no_valid_rows_is_noop(self, controller_with_results, viewer):
        controller_with_results._on_bulk_duplicate([42], True)

        viewer.aoi_controller.set_aoi_duplicates_bulk.assert_not_called()

    def test_external_reference_cannot_be_a_primary(self, controller_with_results, viewer):
        controller_with_results._current_results[0]['aoi_idx'] = None

        controller_with_results._on_bulk_duplicate([1], True)

        viewer.aoi_controller.set_aoi_duplicates_bulk.assert_not_called()
