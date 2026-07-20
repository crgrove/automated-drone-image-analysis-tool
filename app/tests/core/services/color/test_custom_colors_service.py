"""
Comprehensive tests for CustomColorsService.

Tests custom color management and persistence.
"""

import pytest
from core.services.color.CustomColorsService import CustomColorsService, get_custom_colors_service


@pytest.fixture
def custom_colors_service():
    """Fixture providing a CustomColorsService instance."""
    return CustomColorsService()


def test_custom_colors_service_initialization(custom_colors_service):
    """Test CustomColorsService initialization."""
    assert custom_colors_service is not None
    assert custom_colors_service.settings_service is not None


def test_get_custom_colors_service_singleton():
    """Test that get_custom_colors_service returns singleton."""
    service1 = get_custom_colors_service()
    service2 = get_custom_colors_service()

    assert service1 is service2


def test_add_custom_color_rgb(custom_colors_service):
    """Test adding a custom color as RGB tuple."""
    index = custom_colors_service.add_custom_color_rgb((100, 150, 200))

    assert index >= 0
    assert index < CustomColorsService.MAX_CUSTOM_COLORS


def test_add_custom_color_rgb_duplicate(custom_colors_service):
    """Test adding duplicate color returns existing index."""
    index1 = custom_colors_service.add_custom_color_rgb((100, 150, 200))
    index2 = custom_colors_service.add_custom_color_rgb((100, 150, 200))

    assert index1 == index2


def test_get_custom_colors(custom_colors_service):
    """Test getting all custom colors."""
    colors = custom_colors_service.get_custom_colors()

    assert isinstance(colors, list)
    assert len(colors) == CustomColorsService.MAX_CUSTOM_COLORS


def test_save_custom_colors(custom_colors_service):
    """Test saving custom colors to settings."""
    custom_colors_service.add_custom_color_rgb((100, 150, 200))
    custom_colors_service.save_custom_colors()

    # Verify colors were saved
    colors_json = custom_colors_service.settings_service.get_setting('custom_colors')
    assert colors_json is not None


def test_add_fills_empty_slots():
    """Test that colors fill empty slots first."""
    svc = CustomColorsService()
    # Clear internal state to avoid stale settings
    svc._colors = [None] * svc.MAX_CUSTOM_COLORS

    idx0 = svc.add_custom_color_rgb((10, 20, 30))
    idx1 = svc.add_custom_color_rgb((40, 50, 60))
    assert idx0 != idx1

    colors = svc.get_custom_colors()
    assert (10, 20, 30) in colors
    assert (40, 50, 60) in colors
