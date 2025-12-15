"""
Comprehensive tests for wizard controllers.

Tests the wizard interface for configuring algorithms.
"""

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from unittest.mock import patch, MagicMock

# Try to import wizard controllers, skip tests if not available
try:
    from algorithms.images.ColorRange.controllers.ColorRangeWizardController import ColorRangeWizardController
    from algorithms.images.HSVColorRange.controllers.HSVColorRangeWizardController import HSVColorRangeWizardController
    from algorithms.images.MatchedFilter.controllers.MatchedFilterWizardController import MatchedFilterWizardController
    _WIZARD_DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    _WIZARD_DEPENDENCIES_AVAILABLE = False
    _WIZARD_IMPORT_ERROR = str(e)


@pytest.fixture(scope='session')
def app():
    """Create QApplication for widget tests."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def color_range_config():
    """Sample ColorRange algorithm config."""
    return {
        'name': 'ColorRange',
        'label': 'Color Range (RGB)',
        'controller': 'ColorRangeController',
        'wizard_controller': 'ColorRangeWizardController',
        'service': 'ColorRangeService',
        'combine_overlapping_aois': True,
        'platforms': ['Windows', 'Darwin'],
        'type': 'RGB'
    }


@pytest.fixture
def hsv_color_range_config():
    """Sample HSVColorRange algorithm config."""
    return {
        'name': 'HSVColorRange',
        'label': 'Color Range (HSV)',
        'controller': 'HSVColorRangeController',
        'wizard_controller': 'HSVColorRangeWizardController',
        'service': 'HSVColorRangeService',
        'combine_overlapping_aois': True,
        'platforms': ['Windows', 'Darwin'],
        'type': 'RGB'
    }


def test_color_range_wizard_initialization(app, color_range_config):
    """Test ColorRangeWizardController initialization."""
    if not _WIZARD_DEPENDENCIES_AVAILABLE:
        pytest.skip(f"Wizard dependencies not available: {_WIZARD_IMPORT_ERROR}")
    wizard = ColorRangeWizardController(color_range_config, 'Dark')

    assert wizard is not None
    assert wizard.name == color_range_config['name']
    assert wizard.is_thermal == (color_range_config['type'] == 'Thermal')
    assert wizard.theme == 'Dark'
    assert len(wizard.color_rows) == 0


def test_color_range_wizard_add_color(app, color_range_config, qtbot):
    """Test adding a color to ColorRangeWizardController."""
    if not _WIZARD_DEPENDENCIES_AVAILABLE:
        pytest.skip(f"Wizard dependencies not available: {_WIZARD_IMPORT_ERROR}")
    wizard = ColorRangeWizardController(color_range_config, 'Dark')

    # Simulate adding a color
    test_color = QColor(100, 150, 200)
    wizard._on_color_selected_from_menu(test_color)

    # Should have one color row now
    assert len(wizard.color_rows) > 0


def test_color_range_wizard_get_options(app, color_range_config):
    """Test getting options from ColorRangeWizardController."""
    if not _WIZARD_DEPENDENCIES_AVAILABLE:
        pytest.skip(f"Wizard dependencies not available: {_WIZARD_IMPORT_ERROR}")
    wizard = ColorRangeWizardController(color_range_config, 'Dark')

    # Add a color
    test_color = QColor(100, 150, 200)
    wizard._on_color_selected_from_menu(test_color)

    options = wizard.get_options()

    assert 'color_ranges' in options
    assert len(options['color_ranges']) > 0


def test_hsv_color_range_wizard_initialization(app, hsv_color_range_config):
    """Test HSVColorRangeWizardController initialization."""
    if not _WIZARD_DEPENDENCIES_AVAILABLE:
        pytest.skip(f"Wizard dependencies not available: {_WIZARD_IMPORT_ERROR}")
    wizard = HSVColorRangeWizardController(hsv_color_range_config, 'Dark')

    assert wizard is not None
    assert wizard.name == hsv_color_range_config['name']
    assert wizard.is_thermal == (hsv_color_range_config['type'] == 'Thermal')
    assert wizard.theme == 'Dark'


def test_matched_filter_wizard_initialization(app):
    """Test MatchedFilterWizardController initialization."""
    if not _WIZARD_DEPENDENCIES_AVAILABLE:
        pytest.skip(f"Wizard dependencies not available: {_WIZARD_IMPORT_ERROR}")
    config = {
        'name': 'MatchedFilter',
        'label': 'Matched Filter',
        'controller': 'MatchedFilterController',
        'wizard_controller': 'MatchedFilterWizardController',
        'service': 'MatchedFilterService',
        'combine_overlapping_aois': True,
        'platforms': ['Windows', 'Darwin'],
        'type': 'RGB'
    }

    wizard = MatchedFilterWizardController(config, 'Dark')

    assert wizard is not None
    assert wizard.name == config['name']
    assert wizard.is_thermal == (config['type'] == 'Thermal')
