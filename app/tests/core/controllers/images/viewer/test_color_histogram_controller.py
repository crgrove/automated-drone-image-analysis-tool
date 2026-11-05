"""Tests for ColorHistogramController."""

from unittest.mock import MagicMock

import numpy as np

import core.controllers.images.viewer.ColorHistogramController as controller_module
from core.controllers.images.viewer.ColorHistogramController import (
    ColorHistogramController,
)


def _controller(dialog_open=True):
    """A controller on a mock viewer, optionally with its dialog showing.

    The histogram is only built while the dialog is open, so tests of the
    histogram's own behaviour run with a visible (mock) dialog.
    """
    parent = MagicMock()
    parent.is_thermal = False
    parent.current_image = 0
    parent.image_load_controller = MagicMock()
    controller = ColorHistogramController(parent)
    if dialog_open:
        controller.dialog = MagicMock()
        controller.dialog.isVisible.return_value = True
    return controller


def test_color_histogram_controller_refreshes_context_when_aois_change():
    """Same-image AOI updates should rebuild the histogram context."""
    controller = _controller()
    image_array = np.array(
        [
            [[255, 0, 0], [0, 255, 0]],
            [[0, 0, 255], [255, 255, 0]],
        ],
        dtype=np.uint8
    )

    controller.on_image_data_updated(
        image_array,
        [{'detected_pixels': [(0, 0)]}]
    )
    assert controller.current_context['histogram_data']['anomaly_pixels'] == 1

    controller.on_image_data_updated(
        image_array,
        [{'detected_pixels': [(0, 0), (1, 0), (0, 1)]}]
    )
    assert controller.current_context['histogram_data']['anomaly_pixels'] == 3


def _sample_image():
    return np.array(
        [
            [[255, 0, 0], [0, 255, 0]],
            [[0, 0, 255], [255, 255, 0]],
        ],
        dtype=np.uint8
    )


def test_closed_dialog_skips_histogram_build():
    """An image load with the dialog closed must not build the histogram.

    The build is a full-frame HSV pass plus AOI rasterisation - over a second
    per 48 MP frame - and nothing reads it until the dialog opens.
    """
    controller = _controller(dialog_open=False)
    controller.service.build_histogram_context = MagicMock()

    controller.on_image_data_updated(_sample_image(), [])

    controller.service.build_histogram_context.assert_not_called()
    assert controller.get_visibility_mask() is None
    assert controller.get_hover_mask() is None


def test_open_dialog_builds_histogram_on_demand(monkeypatch):
    """Opening the dialog builds the histogram for the image already loaded."""
    monkeypatch.setattr(controller_module, 'ColorHistogramDialog', MagicMock())
    controller = _controller(dialog_open=False)
    controller.on_image_data_updated(_sample_image(), [])

    controller.open_dialog()

    assert controller.has_histogram_data()
    controller.dialog.set_histogram_context.assert_called_with(controller.current_context)


def test_range_change_debounces_viewer_refresh(qtbot):
    """A burst of range changes (a drag) collapses into a single refresh."""
    controller = _controller()
    controller.on_image_data_updated(_sample_image(), [])

    refresh = controller.parent.image_load_controller.refresh_image_preserving_view_from_cache
    refresh.reset_mock()

    full_min, full_max = controller._full_range()
    span = full_max - full_min
    for frac in (0.1, 0.2, 0.3, 0.4, 0.5):
        controller._on_range_changed(full_min, full_min + span * frac)

    # No synchronous refresh during the burst; one debounced refresh after.
    assert refresh.call_count == 0
    assert controller._refresh_timer.isActive()
    qtbot.wait(controller._refresh_timer.interval() + 80)
    assert refresh.call_count == 1


def test_visibility_mask_is_cached():
    """get_visibility_mask computes once per (image, range) and reuses it."""
    controller = _controller()
    controller.on_image_data_updated(_sample_image(), [])

    full_min, full_max = controller._full_range()
    # A range narrower than the full span forces a real mask build.
    controller.active_range = (full_min, full_min)

    sentinel = np.array([[True, False], [False, True]])
    controller.service.build_component_mask = MagicMock(return_value=sentinel)

    first = controller.get_visibility_mask()
    second = controller.get_visibility_mask()

    assert first is second
    assert controller.service.build_component_mask.call_count == 1
