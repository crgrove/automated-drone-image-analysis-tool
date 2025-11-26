"""
Comprehensive tests for CustomColorsService.

Tests custom color management and persistence.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor
from core.services.color.CustomColorsService import CustomColorsService, get_custom_colors_service


@pytest.fixture(scope='session')
def app():
    """Create QApplication for widget tests."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def custom_colors_service():
    """Fixture providing a CustomColorsService instance."""
    return CustomColorsService()


def test_custom_colors_service_initialization(custom_colors_service):
    """Test CustomColorsService initialization."""
    assert custom_colors_service is not None
    assert custom_colors_service.settings_service is not None


def test_get_custom_colors_service_singleton(app):
    """Test that get_custom_colors_service returns singleton."""
    service1 = get_custom_colors_service()
    service2 = get_custom_colors_service()

    assert service1 is service2


def test_add_custom_color(custom_colors_service, app):
    """Test adding a custom color."""
    color = QColor(100, 150, 200)
    index = custom_colors_service.add_custom_color(color)

    assert index >= 0
    assert index < CustomColorsService.MAX_CUSTOM_COLORS


def test_add_custom_color_duplicate(custom_colors_service, app):
    """Test adding duplicate color returns existing index."""
    color = QColor(100, 150, 200)
    index1 = custom_colors_service.add_custom_color(color)
    index2 = custom_colors_service.add_custom_color(color)

    assert index1 == index2


def test_get_custom_colors(custom_colors_service, app):
    """Test getting all custom colors."""
    colors = custom_colors_service.get_custom_colors()

    assert isinstance(colors, list)
    assert len(colors) == CustomColorsService.MAX_CUSTOM_COLORS


def test_save_custom_colors(custom_colors_service, app):
    """Test saving custom colors to settings."""
    color = QColor(100, 150, 200)
    custom_colors_service.add_custom_color(color)
    custom_colors_service.save_custom_colors()

    # Verify colors were saved
    colors_json = custom_colors_service.settings_service.get_setting('custom_colors')
    assert colors_json is not None


def test_sync_with_dialog(custom_colors_service, app):
    """Test syncing colors after dialog use."""
    custom_colors_service.sync_with_dialog()
    # Should not raise exception
    assert True
