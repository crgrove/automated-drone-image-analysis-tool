"""Viewer.apply_aoi_circle_thickness: the live-apply hook the Preferences
dialog pushes when the AOI circle thickness changes. The drawing reads the
setting itself, so the hook only has to redraw the current image; these
tests drive it directly against a stub."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from core.controllers.images.viewer.Viewer import Viewer


def _stub(visible=True, main_image=True, current_image=0):
    return SimpleNamespace(
        isVisible=MagicMock(return_value=visible),
        main_image=MagicMock() if main_image else None,
        current_image=current_image,
        image_load_controller=MagicMock(),
    )


def test_open_viewer_redraws_from_the_cached_image():
    stub = _stub()

    Viewer.apply_aoi_circle_thickness(stub)

    stub.image_load_controller.refresh_image_preserving_view_from_cache.assert_called_once_with()


def test_closed_viewer_is_not_redrawn():
    """Closing the viewer only hides it (MainWindow keeps the reference), so
    each spinbox step would otherwise re-render an image nobody can see."""
    stub = _stub(visible=False)

    Viewer.apply_aoi_circle_thickness(stub)

    stub.image_load_controller.refresh_image_preserving_view_from_cache.assert_not_called()


def test_viewer_without_an_image_widget_is_not_redrawn():
    stub = _stub(main_image=False)

    Viewer.apply_aoi_circle_thickness(stub)

    stub.image_load_controller.refresh_image_preserving_view_from_cache.assert_not_called()


def test_viewer_before_its_first_image_is_not_redrawn():
    stub = _stub(current_image=None)

    Viewer.apply_aoi_circle_thickness(stub)

    stub.image_load_controller.refresh_image_preserving_view_from_cache.assert_not_called()
