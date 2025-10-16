import pytest
from app.helpers.ColorUtils import ColorUtils  # Adjust the import according to your project structure


def test_get_rgb_color_range_normal_case():
    base_color = (100, 150, 200)
    r_range, g_range, b_range = 10, 20, 30
    expected_min = (90, 130, 170)
    expected_max = (110, 170, 230)

    result_min, result_max = ColorUtils.get_rgb_color_range(base_color, r_range, g_range, b_range)

    assert result_min == expected_min
    assert result_max == expected_max


def test_get_rgb_color_range_exceed_max():
    base_color = (250, 240, 230)
    r_range, g_range, b_range = 10, 20, 30
    expected_min = (240, 220, 200)
    expected_max = (255, 255, 255)

    result_min, result_max = ColorUtils.get_rgb_color_range(base_color, r_range, g_range, b_range)

    assert result_min == expected_min
    assert result_max == expected_max


def test_get_rgb_color_range_below_min():
    base_color = (10, 20, 30)
    r_range, g_range, b_range = 15, 25, 35
    expected_min = (0, 0, 0)
    expected_max = (25, 45, 65)

    result_min, result_max = ColorUtils.get_rgb_color_range(base_color, r_range, g_range, b_range)

    assert result_min == expected_min
    assert result_max == expected_max


def test_get_rgb_color_range_exact_bounds():
    base_color = (0, 0, 0)
    r_range, g_range, b_range = 0, 0, 0
    expected_min = (0, 0, 0)
    expected_max = (0, 0, 0)

    result_min, result_max = ColorUtils.get_rgb_color_range(base_color, r_range, g_range, b_range)

    assert result_min == expected_min
    assert result_max == expected_max


def test_get_rgb_color_range_upper_bounds():
    base_color = (255, 255, 255)
    r_range, g_range, b_range = 0, 0, 0
    expected_min = (255, 255, 255)
    expected_max = (255, 255, 255)

    result_min, result_max = ColorUtils.get_rgb_color_range(base_color, r_range, g_range, b_range)

    assert result_min == expected_min
    assert result_max == expected_max
