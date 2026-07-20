"""Unit tests for AOIOverlayController — selected-AOI overlay lifecycle."""

import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def overlay_controller():
    """An AOIOverlayController with the graphics item patched to a mock."""
    with patch(
        "core.controllers.images.viewer.AOIOverlayController.AOISelectionOverlay"
    ):
        from core.controllers.images.viewer.AOIOverlayController import AOIOverlayController
        parent = MagicMock()
        parent.main_image._is_destroyed = False
        parent.current_image_service.get_average_gsd.return_value = 2.5
        parent.altitude_controller.get_effective_altitude.return_value = None
        parent.showAOIsButton.isChecked.return_value = True
        parent.showRulerButton.isChecked.return_value = True
        parent.settings_service.get_setting.return_value = 'Feet'
        # Yield inside the patch context so the lazily-created overlay item
        # (built in _ensure_item during the test) is the mocked class.
        controller = AOIOverlayController(parent)
        yield controller
        # The controller is a QObject and the MagicMock parent records the
        # calls it receives (installEventFilter(self), connect(...)), forming
        # a reference cycle. Break it on teardown so the QObject is freed by
        # refcounting while QApplication is alive -- a late cycle collection
        # during interpreter shutdown would segfault.
        parent.reset_mock()
        controller.parent = None


def _aoi(**extra):
    aoi = {'center': (100, 120), 'radius': 60, 'number': 9}
    aoi.update(extra)
    return aoi


def test_show_for_aoi_configures_and_shows(overlay_controller):
    overlay_controller.show_for_aoi(_aoi())
    item = overlay_controller._overlay_item
    assert item is not None
    item.configure.assert_called_once()
    item.show.assert_called_once()


def test_show_for_aoi_passes_ruler_model_when_gsd_available(overlay_controller):
    overlay_controller.show_for_aoi(_aoi())
    # configure(center, radius, number, ruler_model)
    args = overlay_controller._overlay_item.configure.call_args.args
    assert args[0] == (100, 120)
    assert args[2] == 9
    assert args[3] is not None  # ruler model built from the 2.50 cm/px GSD


def test_ruler_omitted_when_gsd_missing(overlay_controller):
    overlay_controller.parent.current_image_service = None
    overlay_controller.show_for_aoi(_aoi())
    args = overlay_controller._overlay_item.configure.call_args.args
    assert args[3] is None  # no GSD -> no ruler, but the badge still shows


def test_ruler_omitted_when_ruler_toggle_off(overlay_controller):
    """Turning the ruler off drops the ruler but keeps the circle + number badge."""
    overlay_controller.parent.showRulerButton.isChecked.return_value = False
    overlay_controller.show_for_aoi(_aoi())

    item = overlay_controller._overlay_item
    args = item.configure.call_args.args
    assert args[2] == 9       # number badge still configured
    assert args[3] is None    # ruler model omitted
    item.show.assert_called()  # overlay still shown (circles are on)
    item.hide.assert_not_called()


def test_ruler_shown_when_ruler_toggle_on(overlay_controller):
    """With the ruler toggle on and a GSD available, the ruler model is built."""
    overlay_controller.parent.showRulerButton.isChecked.return_value = True
    overlay_controller.show_for_aoi(_aoi())

    args = overlay_controller._overlay_item.configure.call_args.args
    assert args[3] is not None


def test_ruler_visible_defaults_true_when_button_absent(overlay_controller):
    """Missing the button (older layout) defaults to showing the ruler."""
    del overlay_controller.parent.showRulerButton
    assert overlay_controller._ruler_visible() is True


def test_refresh_hides_when_circles_off(overlay_controller):
    overlay_controller.show_for_aoi(_aoi())
    item = overlay_controller._overlay_item
    overlay_controller.parent.showAOIsButton.isChecked.return_value = False

    overlay_controller.refresh()
    item.hide.assert_called()


def test_clear_hides_and_forgets_aoi(overlay_controller):
    overlay_controller.show_for_aoi(_aoi())
    item = overlay_controller._overlay_item

    overlay_controller.clear()
    assert overlay_controller._current_aoi is None
    item.hide.assert_called()


def test_show_for_aoi_ignores_non_dict(overlay_controller):
    overlay_controller.show_for_aoi("not an aoi")
    assert overlay_controller._current_aoi is None


def test_show_for_aoi_resets_ruler_angle(overlay_controller):
    """Selecting an AOI starts its ruler horizontal (rotation is not kept)."""
    overlay_controller.show_for_aoi(_aoi())
    overlay_controller._overlay_item.reset_ruler_angle.assert_called_once()


def test_current_gsd_cm_uses_average_gsd_with_altitude(overlay_controller):
    """The ruler GSD matches the Measure tool: average GSD + corrected altitude."""
    overlay_controller.parent.altitude_controller.get_effective_altitude.return_value = 180.0
    overlay_controller.parent.current_image_service.get_average_gsd.return_value = 2.5

    assert overlay_controller._current_gsd_cm() == 2.5
    # The user-corrected altitude is forwarded, exactly as the Measure tool does.
    overlay_controller.parent.current_image_service.get_average_gsd.assert_called_with(
        custom_altitude_ft=180.0
    )


def test_current_gsd_cm_none_without_service(overlay_controller):
    overlay_controller.parent.current_image_service = None
    assert overlay_controller._current_gsd_cm() is None
