import pytest
import numpy as np
from helpers.ColorUtils import ColorUtils


def test_get_rgb_color_range_normal_case():
    """Test RGB color range calculation with normal values."""
    base_color = (100, 150, 200)
    r_range, g_range, b_range = 10, 20, 30
    expected_min = (90, 130, 170)
    expected_max = (110, 170, 230)

    result_min, result_max = ColorUtils.get_rgb_color_range(base_color, r_range, g_range, b_range)

    assert result_min == expected_min
    assert result_max == expected_max


def test_get_rgb_color_range_exceed_max():
    """Test RGB color range when values exceed 255."""
    base_color = (250, 240, 230)
    r_range, g_range, b_range = 10, 20, 30
    expected_min = (240, 220, 200)
    expected_max = (255, 255, 255)

    result_min, result_max = ColorUtils.get_rgb_color_range(base_color, r_range, g_range, b_range)

    assert result_min == expected_min
    assert result_max == expected_max


def test_get_rgb_color_range_below_min():
    """Test RGB color range when values go below 0."""
    base_color = (10, 20, 30)
    r_range, g_range, b_range = 15, 25, 35
    expected_min = (0, 0, 0)
    expected_max = (25, 45, 65)

    result_min, result_max = ColorUtils.get_rgb_color_range(base_color, r_range, g_range, b_range)

    assert result_min == expected_min
    assert result_max == expected_max


def test_get_rgb_color_range_exact_bounds():
    """Test RGB color range with zero range."""
    base_color = (0, 0, 0)
    r_range, g_range, b_range = 0, 0, 0
    expected_min = (0, 0, 0)
    expected_max = (0, 0, 0)

    result_min, result_max = ColorUtils.get_rgb_color_range(base_color, r_range, g_range, b_range)

    assert result_min == expected_min
    assert result_max == expected_max


def test_get_rgb_color_range_upper_bounds():
    """Test RGB color range at maximum values."""
    base_color = (255, 255, 255)
    r_range, g_range, b_range = 0, 0, 0
    expected_min = (255, 255, 255)
    expected_max = (255, 255, 255)

    result_min, result_max = ColorUtils.get_rgb_color_range(base_color, r_range, g_range, b_range)

    assert result_min == expected_min
    assert result_max == expected_max


def test_get_hsv_color_range_normal_case():
    """Test HSV color range calculation with normal values (no wraparound)."""
    hsv = (90, 128, 200)  # H=90, S=128, V=200
    h_range, s_range, v_range = 10, 20, 30

    result = ColorUtils.get_hsv_color_range(hsv, h_range, s_range, v_range)

    assert len(result) == 1  # No wraparound, single range
    lower, upper = result[0]
    assert lower[0] == 80  # H - h_range
    assert upper[0] == 100  # H + h_range
    assert lower[1] == 108  # S - s_range
    assert upper[1] == 148  # S + s_range
    assert lower[2] == 170  # V - v_range
    assert upper[2] == 230  # V + v_range


def test_get_hsv_color_range_lower_wraparound():
    """Test HSV color range with lower hue wraparound (e.g., H=5, range=10)."""
    hsv = (5, 128, 200)
    h_range, s_range, v_range = 10, 20, 30

    result = ColorUtils.get_hsv_color_range(hsv, h_range, s_range, v_range)

    assert len(result) == 2  # Wraparound, two ranges
    # First range: [175, 179] (wraparound at lower bound)
    # Second range: [0, 15] (normal range)
    lower1, upper1 = result[0]
    lower2, upper2 = result[1]

    assert lower1[0] == 175  # 180 + (5 - 10) = 175
    assert upper1[0] == 179
    assert lower2[0] == 0
    assert upper2[0] == 15  # 5 + 10 = 15


def test_get_hsv_color_range_upper_wraparound():
    """Test HSV color range with upper hue wraparound (e.g., H=175, range=10)."""
    hsv = (175, 128, 200)
    h_range, s_range, v_range = 10, 20, 30

    result = ColorUtils.get_hsv_color_range(hsv, h_range, s_range, v_range)

    assert len(result) == 2  # Wraparound, two ranges
    lower1, upper1 = result[0]
    lower2, upper2 = result[1]

    assert lower1[0] == 165  # 175 - 10 = 165
    assert upper1[0] == 179
    assert lower2[0] == 0
    assert upper2[0] == 5  # (175 + 10) - 180 = 5


def test_get_hsv_color_range_large_hue_range():
    """Test HSV color range with very large hue range (select all hues)."""
    hsv = (90, 128, 200)
    h_range, s_range, v_range = 90, 20, 30  # h_range >= 90 selects all

    result = ColorUtils.get_hsv_color_range(hsv, h_range, s_range, v_range)

    assert len(result) == 1
    lower, upper = result[0]
    assert lower[0] == 0
    assert upper[0] == 179  # Full hue range


def test_get_hsv_color_range_saturation_bounds():
    """Test HSV color range saturation bounds clamping."""
    hsv = (90, 10, 200)
    h_range, s_range, v_range = 5, 20, 30

    result = ColorUtils.get_hsv_color_range(hsv, h_range, s_range, v_range)
    lower, upper = result[0]

    assert lower[1] == 0  # Clamped to 0
    assert upper[1] == 30  # 10 + 20 = 30


def test_get_hsv_color_range_value_bounds():
    """Test HSV color range value bounds clamping."""
    hsv = (90, 128, 250)
    h_range, s_range, v_range = 5, 20, 30

    result = ColorUtils.get_hsv_color_range(hsv, h_range, s_range, v_range)
    lower, upper = result[0]

    assert lower[2] == 220  # 250 - 30 = 220
    assert upper[2] == 255  # Clamped to 255


def test_parse_rgb_string_with_parentheses():
    """Test parsing RGB string with parentheses."""
    rgb_str = "(100, 150, 200)"
    result = ColorUtils.parse_rgb_string(rgb_str)

    assert result == (100, 150, 200)


def test_parse_rgb_string_with_brackets():
    """Test parsing RGB string with brackets."""
    rgb_str = "[100, 150, 200]"
    result = ColorUtils.parse_rgb_string(rgb_str)

    assert result == (100, 150, 200)


def test_parse_rgb_string_with_braces():
    """Test parsing RGB string with braces."""
    rgb_str = "{100, 150, 200}"
    result = ColorUtils.parse_rgb_string(rgb_str)

    assert result == (100, 150, 200)


def test_parse_rgb_string_no_brackets():
    """Test parsing RGB string without brackets."""
    rgb_str = "100, 150, 200"
    result = ColorUtils.parse_rgb_string(rgb_str)

    assert result == (100, 150, 200)


def test_parse_rgb_string_invalid():
    """Test parsing invalid RGB string."""
    invalid_strings = [
        "not a color",
        "100, 150",  # Only 2 values
        "100, 150, 200, 250",  # Too many values
        "",
        "abc, def, ghi"
    ]

    for invalid_str in invalid_strings:
        result = ColorUtils.parse_rgb_string(invalid_str)
        assert result is None


def test_parse_rgb_string_non_string():
    """Test parsing non-string input."""
    result = ColorUtils.parse_rgb_string(123)
    assert result is None

    result = ColorUtils.parse_rgb_string(None)
    assert result is None
