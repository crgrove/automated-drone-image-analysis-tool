"""Tests for RecentColorsService."""
import pytest
from unittest.mock import MagicMock, patch
from core.services.color.RecentColorsService import RecentColorsService, get_recent_colors_service
from core.services.SettingsService import SettingsService


@pytest.fixture
def mock_settings_service():
    """Create a mock SettingsService."""
    mock = MagicMock(spec=SettingsService)
    mock.get_setting.return_value = []
    return mock


@pytest.fixture
def recent_colors_service(mock_settings_service):
    """Create a RecentColorsService with mocked SettingsService."""
    service = RecentColorsService()
    service.settings_service = mock_settings_service
    service.logger = MagicMock()  # Mock the logger to avoid initialization issues
    return service


def test_add_hsv_color(recent_colors_service, mock_settings_service):
    """Test adding an HSV color to recent history."""
    color_data = {
        'selected_color': (255, 0, 0),
        'hsv_ranges': {
            'h': 0.5,
            's': 0.8,
            'v': 0.9,
            'h_minus': 0.1,
            'h_plus': 0.1,
            's_minus': 0.2,
            's_plus': 0.2,
            'v_minus': 0.1,
            'v_plus': 0.1
        }
    }
    
    recent_colors_service.add_hsv_color(color_data)
    
    # Verify set_setting was called
    mock_settings_service.set_setting.assert_called_once()
    call_args = mock_settings_service.set_setting.call_args
    assert call_args[0][0] == 'RecentHSVColors'
    assert len(call_args[0][1]) == 1
    assert call_args[0][1][0] == color_data


def test_add_rgb_color(recent_colors_service, mock_settings_service):
    """Test adding an RGB color to recent history."""
    color_data = {
        'selected_color': (255, 0, 0),
        'range_values': (10, 10, 10),
        'color_range': [[245, 0, 0], [255, 10, 10]]
    }
    
    recent_colors_service.add_rgb_color(color_data)
    
    # Verify set_setting was called
    mock_settings_service.set_setting.assert_called_once()
    call_args = mock_settings_service.set_setting.call_args
    assert call_args[0][0] == 'RecentRGBColors'
    assert len(call_args[0][1]) == 1
    assert call_args[0][1][0] == color_data


def test_add_matched_filter_color(recent_colors_service, mock_settings_service):
    """Test adding a Matched Filter color to recent history."""
    color_data = {
        'selected_color': (255, 0, 0),
        'match_filter_threshold': 0.3
    }
    
    recent_colors_service.add_matched_filter_color(color_data)
    
    # Verify set_setting was called
    mock_settings_service.set_setting.assert_called_once()
    call_args = mock_settings_service.set_setting.call_args
    assert call_args[0][0] == 'RecentMatchedFilterColors'
    assert len(call_args[0][1]) == 1
    assert call_args[0][1][0] == color_data


def test_get_recent_hsv_colors(recent_colors_service, mock_settings_service):
    """Test retrieving recent HSV colors."""
    expected_colors = [
        {'selected_color': (255, 0, 0), 'hsv_ranges': {}},
        {'selected_color': (0, 255, 0), 'hsv_ranges': {}}
    ]
    mock_settings_service.get_setting.return_value = expected_colors
    
    result = recent_colors_service.get_recent_hsv_colors()
    
    assert result == expected_colors
    mock_settings_service.get_setting.assert_called_once_with('RecentHSVColors')


def test_get_recent_rgb_colors(recent_colors_service, mock_settings_service):
    """Test retrieving recent RGB colors."""
    expected_colors = [
        {'selected_color': (255, 0, 0), 'range_values': (10, 10, 10)},
        {'selected_color': (0, 255, 0), 'range_values': (20, 20, 20)}
    ]
    mock_settings_service.get_setting.return_value = expected_colors
    
    result = recent_colors_service.get_recent_rgb_colors()
    
    assert result == expected_colors
    mock_settings_service.get_setting.assert_called_once_with('RecentRGBColors')


def test_remove_duplicate_color(recent_colors_service, mock_settings_service):
    """Test that duplicate colors are removed when adding."""
    existing_colors = [
        {'selected_color': (255, 0, 0), 'hsv_ranges': {'h': 0.5}},
        {'selected_color': (0, 255, 0), 'hsv_ranges': {'h': 0.3}}
    ]
    mock_settings_service.get_setting.return_value = existing_colors
    
    # Add the same color as the first one
    new_color = {'selected_color': (255, 0, 0), 'hsv_ranges': {'h': 0.6}}
    recent_colors_service.add_hsv_color(new_color)
    
    # Verify the duplicate was removed and new one added at front
    call_args = mock_settings_service.set_setting.call_args
    saved_colors = call_args[0][1]
    assert len(saved_colors) == 2
    assert saved_colors[0] == new_color
    assert saved_colors[1] == existing_colors[1]


def test_max_recent_colors_limit(recent_colors_service, mock_settings_service):
    """Test that only MAX_RECENT_COLORS are kept."""
    # Create 10 existing colors
    existing_colors = [
        {'selected_color': (i * 10, 0, 0), 'hsv_ranges': {}}
        for i in range(10)
    ]
    mock_settings_service.get_setting.return_value = existing_colors
    
    # Add a new color
    new_color = {'selected_color': (255, 255, 255), 'hsv_ranges': {}}
    recent_colors_service.add_hsv_color(new_color)
    
    # Verify only 10 colors are kept
    call_args = mock_settings_service.set_setting.call_args
    saved_colors = call_args[0][1]
    assert len(saved_colors) == 10
    assert saved_colors[0] == new_color  # New color is at front
    assert saved_colors[-1] == existing_colors[8]  # Last old color was dropped


def test_singleton_pattern():
    """Test that RecentColorsService follows singleton pattern."""
    service1 = get_recent_colors_service()
    service2 = get_recent_colors_service()
    assert service1 is service2

