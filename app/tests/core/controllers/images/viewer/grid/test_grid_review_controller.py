"""Unit tests for GridReviewController — grid review sweep lifecycle."""

import pytest
from unittest.mock import patch, MagicMock

from PySide6.QtCore import Qt, QRectF
from PySide6.QtWidgets import QMessageBox


def _key_event(key, modifiers=Qt.NoModifier):
    event = MagicMock()
    event.key.return_value = key
    event.modifiers.return_value = modifiers
    return event


def _image(grid_review=None, hidden=False):
    return {
        'xml': MagicMock(),
        'path': 'img.jpg',
        'hidden': hidden,
        'grid_review': grid_review,
        'areas_of_interest': [],
    }


@pytest.fixture
def controller(app):
    """A GridReviewController with the overlay item patched to a mock."""
    with patch(
        "core.controllers.images.viewer.grid.GridReviewController.GridOverlayItem"
    ):
        from core.controllers.images.viewer.grid.GridReviewController import GridReviewController
        parent = MagicMock()
        parent.images = [_image(), _image()]
        parent.current_image = 0
        parent.gallery_mode = False
        parent.messages = {}
        parent.main_image._is_destroyed = False
        parent.main_image.sceneRect.return_value = QRectF(0, 0, 800, 600)
        parent._get_current_image_gsd.return_value = None
        # Settings mocks fall through to controller defaults (4x4, auto-mark).
        parent.settings_service.get_setting.return_value = None
        parent.settings_service.get_bool_setting.return_value = True

        controller = GridReviewController(parent)
        yield controller
        # Break the QObject<->MagicMock reference cycle on teardown so the
        # controller is freed while QApplication is still alive.
        parent.reset_mock()
        controller.parent = None


def test_handle_key_inactive_passes_keys_through(controller):
    assert controller.handle_key(_key_event(Qt.Key_Space)) is False
    assert controller.handle_key(_key_event(Qt.Key_Right)) is False
    assert controller.handle_key(_key_event(Qt.Key_X)) is False
    assert controller.active is False


def test_s_key_activates_and_zooms_to_first_cell(controller):
    assert controller.handle_key(_key_event(Qt.Key_S)) is True
    assert controller.active is True
    assert controller.current_cell == 0
    # 800x600 at the 4x4 default -> cell 0 is (0, 0, 200, 150); the zoom
    # rect is expanded by 8% per side so neighboring slivers are visible.
    zoom_rect = controller.parent.main_image.zoomToRect.call_args.args[0]
    assert zoom_rect == QRectF(-16.0, -12.0, 232.0, 174.0)


def test_activation_refused_in_gallery_mode(controller):
    controller.parent.gallery_mode = True
    controller.handle_key(_key_event(Qt.Key_S))
    assert controller.active is False
    controller.parent.status_controller.show_toast.assert_called_once()


def test_activation_resumes_at_first_unreviewed_cell(controller):
    controller.parent.images[0]['grid_review'] = {'rows': 2, 'cols': 2, 'reviewed': {0}}
    controller.activate()
    # Stored grid dims win over defaults; serpentine order on 2x2 is
    # [0, 1, 3, 2] and cell 0 is already reviewed.
    assert (controller._rows, controller._cols) == (2, 2)
    assert controller.current_cell == 1


def test_space_marks_current_cell_and_advances(controller):
    controller.activate()
    controller.handle_key(_key_event(Qt.Key_Space))

    image = controller.parent.images[0]
    assert image['grid_review']['reviewed'] == {0}
    assert controller.current_cell == 1
    controller.parent.xml_service.set_image_grid_review.assert_called_with(
        image['xml'], 4, 4, {0}
    )
    # The save is debounced, not written synchronously on every mark.
    controller.parent.xml_service.save_xml_file.assert_not_called()
    assert controller._save_pending is True


def test_space_follows_serpentine_into_second_row(controller):
    controller.parent.images[0]['grid_review'] = {'rows': 2, 'cols': 2, 'reviewed': set()}
    controller.activate()
    controller.handle_key(_key_event(Qt.Key_Space))  # 0 -> 1
    controller.handle_key(_key_event(Qt.Key_Space))  # 1 -> 3 (row 1 runs right-to-left)
    assert controller.current_cell == 3
    assert controller.parent.images[0]['grid_review']['reviewed'] == {0, 1}


def test_space_on_last_cell_flushes_and_advances_image(controller):
    controller.parent.images[0]['grid_review'] = {'rows': 2, 'cols': 2, 'reviewed': {0, 1, 3}}
    controller.activate()
    assert controller.current_cell == 2  # last cell in serpentine order

    controller.handle_key(_key_event(Qt.Key_Space))

    assert controller.parent.images[0]['grid_review']['reviewed'] == {0, 1, 2, 3}
    controller.parent.xml_service.save_xml_file.assert_called_once()
    controller.parent._nextImageButton_clicked.assert_called_once()


def test_arrows_move_without_marking(controller):
    controller.activate()
    controller.handle_key(_key_event(Qt.Key_Right))
    assert controller.current_cell == 1
    controller.handle_key(_key_event(Qt.Key_Down))
    assert controller.current_cell == 5
    controller.handle_key(_key_event(Qt.Key_Left))
    assert controller.current_cell == 4
    controller.handle_key(_key_event(Qt.Key_Up))
    assert controller.current_cell == 0
    assert controller.parent.images[0]['grid_review'] is None


def test_arrows_clamp_at_grid_edges(controller):
    controller.activate()
    controller.handle_key(_key_event(Qt.Key_Left))
    controller.handle_key(_key_event(Qt.Key_Up))
    assert controller.current_cell == 0


def test_backspace_steps_back_without_unmarking(controller):
    controller.activate()
    controller.handle_key(_key_event(Qt.Key_Space))
    assert controller.current_cell == 1
    controller.handle_key(_key_event(Qt.Key_Backspace))
    assert controller.current_cell == 0
    assert controller.parent.images[0]['grid_review']['reviewed'] == {0}


def test_x_toggles_reviewed_state(controller):
    controller.activate()
    controller.handle_key(_key_event(Qt.Key_X))
    assert controller.parent.images[0]['grid_review']['reviewed'] == {0}
    controller.handle_key(_key_event(Qt.Key_X))
    assert controller.parent.images[0]['grid_review']['reviewed'] == set()


def test_escape_deactivates_and_restores_view(controller):
    controller.activate()
    controller.handle_key(_key_event(Qt.Key_Space))
    controller.handle_key(_key_event(Qt.Key_Escape))

    assert controller.active is False
    assert controller.current_cell is None
    controller.parent.main_image.resetZoom.assert_called()
    # Pending marks are flushed on exit.
    controller.parent.xml_service.save_xml_file.assert_called_once()
    assert controller.parent.messages['Grid Review'] is None


def test_apply_grid_to_all_applies_to_every_image(controller):
    """Bulk apply stamps the chosen grid onto every image and saves once."""
    controller.parent.images = [
        _image(),
        _image(grid_review={'rows': 4, 'cols': 4, 'reviewed': set()}),
    ]
    controller._apply_grid_to_all(3, 3)

    for img in controller.parent.images:
        assert (img['grid_review']['rows'], img['grid_review']['cols']) == (3, 3)
    assert controller.parent.xml_service.set_image_grid_review.call_count == 2
    controller.parent.xml_service.save_xml_file.assert_called_once()


def test_apply_grid_to_all_keeps_same_size_progress(controller):
    """An image already at the target size keeps its reviewed cells."""
    controller.parent.images = [_image(grid_review={'rows': 3, 'cols': 3, 'reviewed': {0, 4}})]
    controller._apply_grid_to_all(3, 3)
    assert controller.parent.images[0]['grid_review']['reviewed'] == {0, 4}


def test_apply_grid_to_all_resets_conflicting_on_yes(controller):
    """Confirming Yes resets progress recorded at a different size."""
    controller.parent.images = [_image(grid_review={'rows': 4, 'cols': 4, 'reviewed': {0, 5}})]
    with patch.object(QMessageBox, 'question', return_value=QMessageBox.Yes):
        controller._apply_grid_to_all(3, 3)
    grid = controller.parent.images[0]['grid_review']
    assert (grid['rows'], grid['cols']) == (3, 3)
    assert grid['reviewed'] == set()


def test_apply_grid_to_all_keeps_conflicting_on_no(controller):
    """Answering No leaves started images at their own size and progress."""
    controller.parent.images = [
        _image(grid_review={'rows': 4, 'cols': 4, 'reviewed': {0, 5}}),
        _image(),
    ]
    with patch.object(QMessageBox, 'question', return_value=QMessageBox.No):
        controller._apply_grid_to_all(3, 3)
    started = controller.parent.images[0]['grid_review']
    assert (started['rows'], started['cols']) == (4, 4)
    assert started['reviewed'] == {0, 5}
    # The unstarted image still takes the new size.
    assert (controller.parent.images[1]['grid_review']['rows'],
            controller.parent.images[1]['grid_review']['cols']) == (3, 3)


def test_apply_grid_to_all_cancel_aborts(controller):
    """Cancel makes no changes and writes nothing."""
    controller.parent.images = [_image(grid_review={'rows': 4, 'cols': 4, 'reviewed': {0, 5}})]
    with patch.object(QMessageBox, 'question', return_value=QMessageBox.Cancel):
        controller._apply_grid_to_all(3, 3)
    grid = controller.parent.images[0]['grid_review']
    assert (grid['rows'], grid['cols']) == (4, 4)
    assert grid['reviewed'] == {0, 5}
    controller.parent.xml_service.save_xml_file.assert_not_called()


def test_sub_guide_setting_controls_subdivisions(controller):
    """The focus guide maps to 3 subdivisions when on, 1 when off."""
    controller.parent.settings_service.get_bool_setting.return_value = True
    assert controller._subdivisions() == 3
    controller.parent.settings_service.get_bool_setting.return_value = False
    assert controller._subdivisions() == 1


def test_activate_configures_overlay_with_subdivisions(controller):
    """The overlay is configured with the focus-guide subdivision count."""
    controller.activate()
    subdivisions = controller._overlay_item.configure.call_args.args[6]
    assert subdivisions == 3


def test_status_message_reports_progress(controller):
    controller.activate()
    message = controller.parent.messages['Grid Review']
    assert "1/16" in message
    assert "1/2" in message


def test_on_image_loaded_inactive_hides_overlay(controller):
    controller.activate()
    overlay = controller._overlay_item
    controller.deactivate()
    overlay.hide.reset_mock()

    controller.on_image_loaded()
    overlay.hide.assert_called()
    controller.parent.main_image.zoomToRect.reset_mock()
    assert controller.active is False


def test_on_image_loaded_active_resumes_sweep_on_new_image(controller):
    controller.activate()
    controller.handle_key(_key_event(Qt.Key_Space))

    controller.parent.current_image = 1
    controller.parent.images[1]['grid_review'] = {'rows': 2, 'cols': 2, 'reviewed': {0, 1}}
    controller.on_image_loaded()

    # The image change flushed the pending save and resumed at the new
    # image's first unreviewed cell (serpentine [0, 1, 3, 2] -> 3).
    controller.parent.xml_service.save_xml_file.assert_called_once()
    assert controller.current_cell == 3
    assert (controller._rows, controller._cols) == (2, 2)


def test_cleanup_flushes_pending_save(controller):
    controller.activate()
    controller.handle_key(_key_event(Qt.Key_Space))
    controller.parent.xml_service.save_xml_file.assert_not_called()

    controller.cleanup()
    controller.parent.xml_service.save_xml_file.assert_called_once()
    # A second cleanup with nothing pending does not save again.
    controller.cleanup()
    controller.parent.xml_service.save_xml_file.assert_called_once()
