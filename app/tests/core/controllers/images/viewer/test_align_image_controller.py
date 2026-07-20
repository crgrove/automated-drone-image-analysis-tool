"""Tests for AlignImageController's estimate/heading wiring.

The controller seeds the Align Image dialog with the footprint estimate and the
camera heading used to build it, so the photo starts oriented to match the map.
"""

from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QApplication, QDialog

from core.controllers.images.viewer.AlignImageController import AlignImageController


_DIALOG = "core.controllers.images.viewer.AlignImageController.AlignImageDialog"
_CES = "core.controllers.images.viewer.AlignImageController.CoverageExtentService"


@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])


def _controller(image):
    parent = MagicMock()
    parent.images = [image]
    parent.current_image = 0
    parent.custom_agl_altitude_ft = None
    parent.use_terrain_elevation = True
    return AlignImageController(parent)


def test_get_estimated_corners_returns_service_yaw(app):
    """The heading the estimate used is returned alongside the corners."""
    controller = _controller({'path': 'x.jpg'})
    corners_in = [(1.0, 1.0), (1.0, 2.0), (2.0, 2.0), (2.0, 1.0)]
    with patch(_CES) as ces:
        service = ces.return_value
        service.get_image_fov_corners.return_value = corners_in
        service.last_camera_yaw = 42.0
        corners, yaw = controller._get_estimated_corners(
            {'path': 'x.jpg'}, {'latitude': 40.0, 'longitude': -105.0})

    assert yaw == 42.0
    assert len(corners) == 4


def test_get_estimated_corners_fallback_square_yaw_none(app):
    """A failed estimate falls back to a square and reports no heading."""
    controller = _controller({'path': 'x.jpg'})
    with patch(_CES) as ces:
        ces.return_value.get_image_fov_corners.side_effect = RuntimeError("boom")
        corners, yaw = controller._get_estimated_corners(
            {'path': 'x.jpg'}, {'latitude': 40.0, 'longitude': -105.0})

    assert yaw is None
    assert len(corners) == 4


def test_open_dialog_uses_camera_yaw_as_rotation(app):
    """Camera yaw from the estimate is passed as the dialog's rotation."""
    image = {'path': 'x.jpg', 'bearing': 12.0}
    controller = _controller(image)
    corners = [(1.0, 1.0), (1.0, 2.0), (2.0, 2.0), (2.0, 1.0)]
    with patch.object(controller, '_get_image_gps',
                      return_value={'latitude': 40.0, 'longitude': -105.0}), \
            patch.object(controller, '_get_estimated_corners',
                         return_value=(corners, 97.5)), \
            patch.object(controller, '_is_offline_only', return_value=False), \
            patch(_DIALOG) as dialog_cls:
        dialog_cls.return_value.exec.return_value = QDialog.DialogCode.Rejected
        controller.open_dialog()

    # AlignImageDialog(parent, image_path, estimated_corners, bearing, ...)
    args, _ = dialog_cls.call_args
    assert args[3] == pytest.approx(97.5)


def test_open_dialog_falls_back_to_bearing_when_no_yaw(app):
    """With no camera yaw available the image's bearing orients the photo."""
    image = {'path': 'x.jpg', 'bearing': 12.0}
    controller = _controller(image)
    corners = [(1.0, 1.0), (1.0, 2.0), (2.0, 2.0), (2.0, 1.0)]
    with patch.object(controller, '_get_image_gps',
                      return_value={'latitude': 40.0, 'longitude': -105.0}), \
            patch.object(controller, '_get_estimated_corners',
                         return_value=(corners, None)), \
            patch.object(controller, '_is_offline_only', return_value=False), \
            patch(_DIALOG) as dialog_cls:
        dialog_cls.return_value.exec.return_value = QDialog.DialogCode.Rejected
        controller.open_dialog()

    args, _ = dialog_cls.call_args
    assert args[3] == pytest.approx(12.0)
