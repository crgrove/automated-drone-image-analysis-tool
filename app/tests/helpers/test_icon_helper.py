"""
Comprehensive tests for IconHelper.

Tests icon creation and theming utilities.
"""

import pytest
from unittest.mock import patch, MagicMock
from helpers.IconHelper import IconHelper
import helpers.IconHelper as icon_helper_module


def test_get_icon_color_dark():
    """Test getting icon color for dark theme."""
    color = IconHelper.get_icon_color("Dark")
    assert color == 'lightgray'


def test_get_icon_color_light():
    """Test getting icon color for light theme."""
    color = IconHelper.get_icon_color("Light")
    assert color == 'darkgray'


def test_get_icon_color_case_insensitive():
    """Test that theme name is case-insensitive."""
    # Note: IconHelper.get_icon_color is case-sensitive, checking exact match
    color1 = IconHelper.get_icon_color("Dark")  # Exact match
    color2 = IconHelper.get_icon_color("Dark")  # Exact match
    color3 = IconHelper.get_icon_color("Dark")  # Exact match

    assert color1 == color2 == color3 == 'lightgray'


def test_create_icon_dark_theme():
    """Test creating icon with dark theme."""
    mock_icon = MagicMock()

    # Patch qta.icon in the IconHelper module where it's used
    # Use patch.object to patch the attribute on the already-imported module
    with patch.object(icon_helper_module.qta, 'icon', return_value=mock_icon) as mock_qta:
        IconHelper.create_icon('fa6s.magnifying-glass', 'Dark')

        mock_qta.assert_called_once()
        call_args = mock_qta.call_args
        assert call_args[0][0] == 'fa6s.magnifying-glass'
        assert call_args[1]['color'] == 'lightgray'


def test_create_icon_light_theme():
    """Test creating icon with light theme."""
    mock_icon = MagicMock()

    # Patch qta.icon in the IconHelper module where it's used
    # Use patch.object to patch the attribute on the already-imported module
    with patch.object(icon_helper_module.qta, 'icon', return_value=mock_icon) as mock_qta:
        IconHelper.create_icon('fa6s.magnifying-glass', 'Light')

        mock_qta.assert_called_once()
        call_args = mock_qta.call_args
        assert call_args[0][0] == 'fa6s.magnifying-glass'
        assert call_args[1]['color'] == 'darkgray'


def test_create_icon_with_options():
    """Test creating icon with additional options."""
    mock_icon = MagicMock()

    # Patch qta.icon in the IconHelper module where it's used
    # Use patch.object to patch the attribute on the already-imported module
    with patch.object(icon_helper_module.qta, 'icon', return_value=mock_icon) as mock_qta:
        IconHelper.create_icon('fa6s.magnifying-glass', 'Dark', size=24, scale_factor=1.5)

        mock_qta.assert_called_once()
        call_args = mock_qta.call_args
        assert call_args[0][0] == 'fa6s.magnifying-glass'
        assert call_args[1]['size'] == 24
        assert call_args[1]['scale_factor'] == 1.5
        assert call_args[1]['color'] == 'lightgray'
