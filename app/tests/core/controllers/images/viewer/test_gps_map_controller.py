"""Unit tests for GPSMapController — terrain-preference threading.

The selected-AOI map marker must use the same UseTerrainElevation
preference as the viewer's AOI label and the exports, so the pin and the
label can never disagree.
"""

import pytest
from unittest.mock import patch, MagicMock


class _Parent:
    """Minimal plain-object viewer stub (avoids MagicMock's truthy getattr)."""

    def __init__(self, use_terrain=None):
        class _AOIController:
            selected_aoi_index = 0

        self.aoi_controller = _AOIController()
        self.images = [{'name': 'img1.jpg', 'areas_of_interest': [{'center': (10, 20)}]}]
        self.current_image = 0
        if use_terrain is not None:
            self.use_terrain_elevation = use_terrain


class _RecordingAOIService:
    """Records the use_terrain argument passed to the metadata helper."""

    calls = []

    def __init__(self, *_args, **_kwargs):
        pass

    def get_aoi_gps_with_metadata(self, image, aoi, aoi_index, custom_alt_ft, use_terrain=True):
        type(self).calls.append(use_terrain)
        return {'latitude': 38.0, 'longitude': -121.0}


@pytest.fixture
def make_controller():
    def _make(parent):
        with patch('core.controllers.images.viewer.GPSMapController.AOIService',
                   _RecordingAOIService):
            from core.controllers.images.viewer.GPSMapController import GPSMapController
            controller = GPSMapController(parent)
            _RecordingAOIService.calls = []
            result = controller.get_current_aoi_gps()
            return result, _RecordingAOIService.calls
    return _make


def test_marker_honors_terrain_pref_off(make_controller):
    result, calls = make_controller(_Parent(use_terrain=False))
    assert calls == [False]
    assert result['latitude'] == 38.0
    assert result['image_name'] == 'img1.jpg'


def test_marker_honors_terrain_pref_on(make_controller):
    _result, calls = make_controller(_Parent(use_terrain=True))
    assert calls == [True]


def test_marker_defaults_to_terrain_when_pref_absent(make_controller):
    _result, calls = make_controller(_Parent(use_terrain=None))
    assert calls == [True]


# ---------------------------------------------------------------------------
# Zoom-FOV throttle (freeze regression): a single wheel notch emits viewChanged
# up to twice, and each forward reruns the map's terrain-projected FOV redraw
# synchronously. update_zoom_fov must coalesce a burst into ~one redraw per
# window so it cannot saturate the GUI thread.
# ---------------------------------------------------------------------------

def _controller_with_open_dialog():
    from core.controllers.images.viewer.GPSMapController import GPSMapController
    controller = GPSMapController(_Parent())
    dialog = MagicMock()
    dialog.isVisible.return_value = True
    controller.map_dialog = dialog
    return controller, dialog


def test_update_zoom_fov_leading_edge_draws_immediately():
    controller, dialog = _controller_with_open_dialog()

    controller.update_zoom_fov('rectA')

    dialog.update_zoom_fov.assert_called_once_with('rectA')
    assert controller._fov_throttle.isActive()


def test_update_zoom_fov_coalesces_burst_to_latest():
    controller, dialog = _controller_with_open_dialog()

    controller.update_zoom_fov('r1')   # leading edge -> drawn immediately
    controller.update_zoom_fov('r2')   # coalesced
    controller.update_zoom_fov('r3')   # coalesced (latest wins)

    # Only the leading update has drawn while the throttle window is open.
    assert dialog.update_zoom_fov.call_count == 1

    # Simulate the throttle timer firing (trailing edge).
    controller._flush_zoom_fov()
    assert dialog.update_zoom_fov.call_count == 2
    assert dialog.update_zoom_fov.call_args_list[-1].args == ('r3',)

    # Nothing left pending -> a second fire is a no-op.
    controller._flush_zoom_fov()
    assert dialog.update_zoom_fov.call_count == 2


def test_update_zoom_fov_noop_when_dialog_hidden():
    controller, dialog = _controller_with_open_dialog()
    dialog.isVisible.return_value = False

    controller.update_zoom_fov('rectA')

    dialog.update_zoom_fov.assert_not_called()
    assert not controller._fov_throttle.isActive()


def test_closing_dialog_cancels_pending_fov_redraw():
    controller, dialog = _controller_with_open_dialog()

    controller.update_zoom_fov('r1')   # leading draw + starts throttle
    controller.update_zoom_fov('r2')   # pending trailing draw

    controller.on_map_dialog_closed()

    assert not controller._fov_throttle.isActive()
    assert controller._has_pending_fov is False

    # A stray timer fire after close must not touch the (closed) dialog.
    dialog.update_zoom_fov.reset_mock()
    controller._flush_zoom_fov()
    dialog.update_zoom_fov.assert_not_called()
