"""Tests for ImageLoadController overlay handling."""

from unittest.mock import MagicMock

from core.controllers.images.viewer.image.ImageLoadController import ImageLoadController


def _controller():
    parent = MagicMock()
    parent.main_image.getZoom.return_value = 2.5
    parent.showOverlayToggle.isChecked.return_value = True
    controller = ImageLoadController(parent)
    return controller, parent


def _image_service():
    svc = MagicMock()
    svc.get_camera_yaw.return_value = 90.0
    svc.get_average_gsd.return_value = 3.2
    return svc


def test_update_overlay_refreshes_scale_bar_on_load():
    """The scale bar must be refreshed at load with the current zoom, so it
    appears without the user having to manually rescale (regression: it was
    only updated on a zoomChanged signal that often does not fire)."""
    controller, parent = _controller()

    controller._update_overlay(_image_service())

    parent._update_scale_bar.assert_called_once_with(2.5)
    parent.overlay.rotate_north_icon.assert_called_once()
    parent.overlay.update_visibility.assert_called_once()
    parent.overlay._place_overlay.assert_called()


def test_update_overlay_skips_scale_bar_when_no_image():
    """No scale-bar refresh is attempted when there is no main image."""
    controller, parent = _controller()
    parent.main_image = None

    controller._update_overlay(_image_service())

    parent._update_scale_bar.assert_not_called()
