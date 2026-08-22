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


# --------------------------------------------------------------------------- #
#  _apply_pending_view_zoom: the load pipeline's final step, consuming the    #
#  zoom the initiating navigation requested (Viewer.request_zoom_after_load)  #
# --------------------------------------------------------------------------- #

def test_apply_pending_view_zoom_invokes_the_consumed_request():
    controller, parent = _controller()
    parent.current_image = 4
    apply_zoom = MagicMock()
    parent.take_pending_view_zoom = MagicMock(return_value=apply_zoom)

    controller._apply_pending_view_zoom()

    parent.take_pending_view_zoom.assert_called_once_with(4)
    apply_zoom.assert_called_once_with()


def test_applied_zoom_logs_nothing():
    """Success path: no log line, at any level. One per gallery AOI click."""
    controller, parent = _controller()
    parent.current_image = 4
    parent.main_image.zoomStack = [object()]        # the zoom took effect
    parent.take_pending_view_zoom = MagicMock(return_value=MagicMock())
    controller.logger = MagicMock()

    controller._apply_pending_view_zoom()

    controller.logger.warning.assert_not_called()
    controller.logger.debug.assert_not_called()
    controller.logger.info.assert_not_called()


def test_unzoomed_landing_logs_nothing():
    """Nor when the requested zoom declined: the guards are silent by design."""
    controller, parent = _controller()
    parent.current_image = 4
    parent.main_image.zoomStack = []                # the zoom did NOT take
    parent.take_pending_view_zoom = MagicMock(return_value=MagicMock())
    controller.logger = MagicMock()

    controller._apply_pending_view_zoom()

    controller.logger.warning.assert_not_called()


def test_apply_pending_view_zoom_noop_when_nothing_pending():
    controller, parent = _controller()
    parent.take_pending_view_zoom = MagicMock(return_value=None)

    controller._apply_pending_view_zoom()  # nothing to invoke, no error


def test_apply_pending_view_zoom_contains_request_failures():
    """A failing zoom callable must not fail the image load."""
    controller, parent = _controller()
    parent.take_pending_view_zoom = MagicMock(
        return_value=MagicMock(side_effect=RuntimeError("boom")))

    controller._apply_pending_view_zoom()  # logged, not raised


def test_apply_pending_view_zoom_requires_the_viewer_api():
    """A missing take_pending_view_zoom must raise loudly, not no-op.

    Silently skipping the consumption step would mean every requested zoom
    stops applying (gallery clicks land un-zoomed - the original field
    bug) with no error anywhere. The pipeline treats the Viewer API as a
    hard dependency.
    """
    import pytest
    controller, parent = _controller()
    del parent.take_pending_view_zoom  # MagicMock: removes the auto-attr

    with pytest.raises(AttributeError):
        controller._apply_pending_view_zoom()


def test_image_name_is_shown_with_the_full_name_on_hover():
    """The header clips the name, and video frames differ only in the tail
    ("..._262.5s.jpg") - the part that gets cut off is the part that
    identifies the image, so hovering has to give the whole name back."""
    controller, parent = _controller()
    name = 'DJI_20260815165537_0001_Z.MP4_262.5s.jpg'

    controller._show_image_name(name)

    parent.fileNameLabel.setText.assert_called_once_with(name)
    parent.fileNameLabel.setToolTip.assert_called_once_with(name)
