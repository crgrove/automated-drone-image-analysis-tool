"""Unit tests for PixelInfoController."""

import numpy as np
import pytest
from unittest.mock import MagicMock
from PySide6.QtCore import QPoint

from core.controllers.images.viewer.PixelInfoController import PixelInfoController


def _parent(algorithm="ColorRange", temperature_unit="F", image_array=None, has_thermal=False):
    parent = MagicMock()
    parent.messages = {}
    parent.settings = {"algorithm": algorithm}
    parent.temperature_unit = temperature_unit
    parent.current_image_array = image_array
    if image_array is not None:
        parent.main_image.hasImage.return_value = True
    else:
        parent.main_image.hasImage.return_value = False

    if has_thermal:
        thermal = MagicMock()
        thermal.temperature_data = np.ones((50, 50), dtype=np.float32) * 25.0
        thermal.get_temperature_at_point = lambda x, y: 25.0 if 0 <= x < 50 and 0 <= y < 50 else None
        parent.thermal_controller = thermal
    else:
        # Simulate no thermal_controller attribute at all
        parent.thermal_controller = MagicMock()
        parent.thermal_controller.temperature_data = None

    return parent


@pytest.fixture
def controller():
    return PixelInfoController(MagicMock())


# ---------------------------------------------------------------------------
# update_cursor_info dispatch
# ---------------------------------------------------------------------------

def test_update_cursor_info_thermal_path():
    parent = _parent(has_thermal=True)
    controller = PixelInfoController(parent)
    controller.update_cursor_info(QPoint(10, 10))
    assert parent.messages["Temperature"] == "25.0° F at (10, 10)"


def test_update_cursor_info_clears_previous_messages():
    parent = _parent()
    parent.messages["Cursor Position"] = "old"
    parent.messages["Color Values"] = "old"
    controller = PixelInfoController(parent)
    controller.update_cursor_info(QPoint(-1, -1))
    assert parent.messages["Cursor Position"] is None
    assert parent.messages["Color Values"] is None


# ---------------------------------------------------------------------------
# Temperature display
# ---------------------------------------------------------------------------

def test_temperature_display_off_image_clears():
    parent = _parent(has_thermal=True)
    controller = PixelInfoController(parent)
    controller._update_temperature_display(QPoint(-1, -1))
    assert parent.messages["Temperature"] is None


def test_temperature_display_out_of_bounds_clears():
    parent = _parent(has_thermal=True)
    # get_temperature_at_point will return None for out-of-bounds
    controller = PixelInfoController(parent)
    controller._update_temperature_display(QPoint(999, 999))
    assert parent.messages["Temperature"] is None


def test_temperature_display_formats_value():
    parent = _parent(has_thermal=True, temperature_unit="C")
    controller = PixelInfoController(parent)
    controller._update_temperature_display(QPoint(20, 30))
    assert parent.messages["Temperature"] == "25.0° C at (20, 30)"


# ---------------------------------------------------------------------------
# Color value display
# ---------------------------------------------------------------------------

def test_color_display_off_image():
    img = np.ones((50, 50, 3), dtype=np.uint8) * 100
    parent = _parent(image_array=img)
    controller = PixelInfoController(parent)
    controller._update_color_value_display(QPoint(-1, -1))
    # No "Color Values" set when cursor is off image
    assert parent.messages.get("Color Values") != "R: 100, G: 100, B: 100 at (-1, -1)"


def test_color_display_shows_rgb_for_color_range():
    img = np.zeros((50, 50, 3), dtype=np.uint8)
    img[10, 20] = [100, 150, 200]
    parent = _parent(algorithm="ColorRange", image_array=img)
    controller = PixelInfoController(parent)
    controller._update_color_value_display(QPoint(20, 10))
    assert parent.messages["Color Values"] == "R: 100, G: 150, B: 200 at (20, 10)"


def test_color_display_shows_hsv_for_hsv_algorithm():
    img = np.zeros((50, 50, 3), dtype=np.uint8)
    img[10, 20] = [255, 0, 0]  # pure red
    parent = _parent(algorithm="HSVColorRange", image_array=img)
    controller = PixelInfoController(parent)
    controller._update_color_value_display(QPoint(20, 10))
    # Pure red RGB -> HSV h=0
    assert "H: 0" in parent.messages["Color Values"]
    assert "S: 100" in parent.messages["Color Values"]
    assert "V: 100" in parent.messages["Color Values"]


def test_color_display_skips_thermal_algorithms():
    img = np.ones((50, 50, 3), dtype=np.uint8) * 100
    parent = _parent(algorithm="ThermalRange", image_array=img)
    controller = PixelInfoController(parent)
    controller._update_color_value_display(QPoint(20, 10))
    assert parent.messages.get("Color Values") is None
    assert parent.messages["Temperature"] is None


def test_color_display_out_of_bounds_ignored():
    img = np.ones((20, 20, 3), dtype=np.uint8) * 100
    parent = _parent(algorithm="ColorRange", image_array=img)
    controller = PixelInfoController(parent)
    controller._update_color_value_display(QPoint(100, 100))
    assert "Color Values" not in parent.messages or parent.messages.get("Color Values") is None


def test_color_display_no_image_array():
    parent = _parent(algorithm="ColorRange", image_array=None)
    controller = PixelInfoController(parent)
    controller._update_color_value_display(QPoint(10, 10))
    # No color values should be set since main_image.hasImage() is False
    assert parent.messages.get("Color Values") is None


# ---------------------------------------------------------------------------
# _format_color_display_for_algorithm
# ---------------------------------------------------------------------------

def test_format_color_rgb_for_color_range(controller):
    result = controller._format_color_display_for_algorithm("ColorRange", 100, 150, 200, 5, 10)
    assert result == "R: 100, G: 150, B: 200 at (5, 10)"


def test_format_color_rgb_for_matched_filter(controller):
    result = controller._format_color_display_for_algorithm("MatchedFilter", 50, 60, 70, 1, 2)
    assert "R: 50" in result


def test_format_color_hsv_for_hsv_algo(controller):
    # Pure green RGB (0, 255, 0) -> HSV h=120°
    result = controller._format_color_display_for_algorithm("HSVColorRange", 0, 255, 0, 1, 2)
    assert "H: 120" in result


def test_format_color_hsv_for_rxanomaly(controller):
    result = controller._format_color_display_for_algorithm("RXAnomaly", 0, 0, 255, 1, 2)
    assert "H:" in result
    assert "S:" in result
    assert "V:" in result


def test_format_color_hsv_for_mrmap(controller):
    result = controller._format_color_display_for_algorithm("MRMap", 128, 128, 128, 0, 0)
    assert "H:" in result


def test_format_color_unknown_algorithm_falls_back_to_rgb(controller):
    result = controller._format_color_display_for_algorithm("Unknown", 10, 20, 30, 0, 0)
    assert "R: 10" in result
