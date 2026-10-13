"""The D key marks the selected AOI as a duplicate (Viewer.keyPressEvent routing)."""

from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication

from core.controllers.images.viewer.Viewer import Viewer


@pytest.fixture(scope='session')
def app():
    return QApplication.instance() or QApplication([])


def _viewer(gallery_mode):
    viewer = MagicMock()
    viewer.grid_review_controller.handle_key.return_value = False
    viewer.gallery_mode = gallery_mode
    viewer._resolve_gallery_selected_aoi.return_value = (2, 3)
    return viewer


def _press(viewer, key=Qt.Key_D, modifiers=Qt.NoModifier, auto_repeat=False):
    event = QKeyEvent(QEvent.KeyPress, key, modifiers, "", auto_repeat)
    Viewer.keyPressEvent(viewer, event)


def test_d_in_single_image_mode_uses_the_selected_aoi(app):
    viewer = _viewer(gallery_mode=False)
    _press(viewer)
    viewer.similarity_controller.mark_duplicate_for_selected.assert_called_once_with()


def test_d_in_gallery_mode_passes_the_gallery_selection(app):
    viewer = _viewer(gallery_mode=True)
    _press(viewer)
    viewer.similarity_controller.mark_duplicate_for_selected.assert_called_once_with(image_idx=2, aoi_idx=3)


def test_d_in_gallery_mode_without_selection_does_nothing(app):
    viewer = _viewer(gallery_mode=True)
    viewer._resolve_gallery_selected_aoi.return_value = None
    _press(viewer)
    viewer.similarity_controller.mark_duplicate_for_selected.assert_not_called()


def test_held_d_does_not_repeat(app):
    viewer = _viewer(gallery_mode=False)
    _press(viewer, auto_repeat=True)
    viewer.similarity_controller.mark_duplicate_for_selected.assert_not_called()


def test_shift_d_is_not_bound(app):
    viewer = _viewer(gallery_mode=False)
    _press(viewer, modifiers=Qt.ShiftModifier)
    viewer.similarity_controller.mark_duplicate_for_selected.assert_not_called()
