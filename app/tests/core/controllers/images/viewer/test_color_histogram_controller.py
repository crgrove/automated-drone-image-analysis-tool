"""Tests for ColorHistogramController."""

from unittest.mock import MagicMock

import numpy as np

from core.controllers.images.viewer.ColorHistogramController import (
    ColorHistogramController,
)


def test_color_histogram_controller_refreshes_context_when_aois_change():
    """Same-image AOI updates should rebuild the histogram context."""
    parent = MagicMock()
    parent.is_thermal = False
    parent.current_image = 0
    parent.image_load_controller = MagicMock()

    controller = ColorHistogramController(parent)
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


def test_range_change_debounces_viewer_refresh(qtbot):
    """A burst of range changes (a drag) collapses into a single refresh."""
    parent = MagicMock()
    parent.is_thermal = False
    parent.current_image = 0
    parent.image_load_controller = MagicMock()

    controller = ColorHistogramController(parent)
    controller.on_image_data_updated(_sample_image(), [])

    refresh = parent.image_load_controller.refresh_image_preserving_view_from_cache
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
    parent = MagicMock()
    parent.is_thermal = False
    parent.current_image = 0
    parent.image_load_controller = MagicMock()

    controller = ColorHistogramController(parent)
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
