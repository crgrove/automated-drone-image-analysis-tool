"""Tests for CoordinateController's cursor-position GPS resolution."""

from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QApplication

from core.controllers.images.viewer.CoordinateController import CoordinateController


@pytest.fixture(scope='session')
def app():
    return QApplication.instance() or QApplication([])


class _StubParent:
    """Plain stub: a MagicMock would fake custom_agl_altitude_ft comparisons."""

    def __init__(self):
        self.current_image = 0
        self.images = [{'path': 'img.jpg'}]
        self.position_format = 'Lat/Long - Decimal Degrees'
        self.use_terrain_elevation = True
        self.aoi_controller = MagicMock()
        self.status_controller = MagicMock()
        self.messages = {}


def _gps_result(lat=36.5, lon=-118.25, source='terrain'):
    result = MagicMock()
    result.latitude = lat
    result.longitude = lon
    result.elevation_source = source
    return result


def _controller(with_result=True):
    parent = _StubParent()
    controller = CoordinateController(parent)
    service = MagicMock()
    service.estimate_pixel_gps.return_value = _gps_result() if with_result else None
    parent.aoi_controller.get_aoi_service.return_value = service
    return controller, parent, service


def test_resolve_cursor_coords_formats_and_reports_source(app):
    controller, parent, service = _controller()
    resolved = controller.resolve_cursor_coords(150, 200)

    assert resolved is not None
    lat, lon, coord_text, tooltip = resolved
    assert lat == 36.5 and lon == -118.25
    assert '36.5' in coord_text
    assert 'terrain' in tooltip
    service.estimate_pixel_gps.assert_called_once_with(
        parent.images[0], 150, 200, custom_altitude_ft=None, use_terrain=True)


def test_resolve_passes_custom_altitude_when_set(app):
    controller, parent, service = _controller()
    parent.custom_agl_altitude_ft = 300
    controller.resolve_cursor_coords(10, 10)
    assert service.estimate_pixel_gps.call_args.kwargs['custom_altitude_ft'] == 300


def test_resolve_returns_none_when_unresolvable(app):
    controller, parent, service = _controller(with_result=False)
    assert controller.resolve_cursor_coords(10, 10) is None


def test_resolve_returns_none_without_current_image(app):
    controller, parent, _ = _controller()
    parent.current_image = -1
    assert controller.resolve_cursor_coords(10, 10) is None


def test_copy_cursor_coordinates_copies_formatted_text(app):
    controller, parent, _ = _controller()
    with patch.object(controller, 'copy_coords_to_clipboard') as mock_copy:
        controller.copy_cursor_coordinates(10, 10)
    coord_text = mock_copy.call_args.args[0]
    assert '36.5' in coord_text


def test_copy_cursor_coordinates_toasts_when_unavailable(app):
    controller, parent, _ = _controller(with_result=False)
    with patch.object(controller, 'copy_coords_to_clipboard') as mock_copy:
        controller.copy_cursor_coordinates(10, 10)
    mock_copy.assert_not_called()
    parent.status_controller.show_toast.assert_called_once()


def test_show_cursor_coordinates_passes_decimal_coords_to_popup(app):
    controller, parent, _ = _controller()
    with patch.object(controller, 'show_coordinates_popup') as mock_popup:
        controller.show_cursor_coordinates(10, 10)
    assert mock_popup.call_args.kwargs['decimal_coords'] == (36.5, -118.25)


def test_open_in_maps_prefers_explicit_coords(app):
    controller, parent, _ = _controller()
    controller.current_decimal_coords = (1.0, 2.0)  # viewer-level (image center)
    with patch(
        'core.controllers.images.viewer.CoordinateController.QDesktopServices'
    ) as mock_desktop:
        controller.open_in_maps((10.5, -20.25))
    url = mock_desktop.openUrl.call_args.args[0].toString()
    assert '10.5,-20.25' in url


def test_open_in_maps_falls_back_to_viewer_coords(app):
    controller, parent, _ = _controller()
    controller.current_decimal_coords = (1.0, 2.0)
    with patch(
        'core.controllers.images.viewer.CoordinateController.QDesktopServices'
    ) as mock_desktop:
        controller.open_in_maps()
    url = mock_desktop.openUrl.call_args.args[0].toString()
    assert '1.0,2.0' in url
