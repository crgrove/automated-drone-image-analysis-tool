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
    from algorithms.images.AIPersonDetector.controllers.AIPersonDetectorWizardController import AIPersonDetectorWizardController
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


def test_hsv_color_range_wizard_recent_color_handler_wired(app, hsv_color_range_config):
    """The wizard must register an on_recent_color_selected handler.

    Regression: without it, choosing a color from the Recent Colors list was
    silently dropped because the recent-color data shape did not match the HSV
    picker handler.
    """
    if not _WIZARD_DEPENDENCIES_AVAILABLE:
        pytest.skip(f"Wizard dependencies not available: {_WIZARD_IMPORT_ERROR}")
    wizard = HSVColorRangeWizardController(hsv_color_range_config, 'Dark')

    assert wizard.color_selection_menu.on_recent_color_selected is not None


def test_hsv_color_range_wizard_recent_color_with_ranges(app, hsv_color_range_config):
    """A recent HSV color carrying ranges adds a row in HSV-picker mode."""
    if not _WIZARD_DEPENDENCIES_AVAILABLE:
        pytest.skip(f"Wizard dependencies not available: {_WIZARD_IMPORT_ERROR}")
    wizard = HSVColorRangeWizardController(hsv_color_range_config, 'Dark')

    hsv_ranges = {
        'h': 0.5, 's': 0.6, 'v': 0.7,
        'h_minus': 0.1, 'h_plus': 0.1,
        's_minus': 0.2, 's_plus': 0.2,
        'v_minus': 0.2, 'v_plus': 0.2,
    }
    color_data = {'selected_color': (0, 170, 255), 'hsv_ranges': hsv_ranges}

    wizard._on_recent_color_selected(color_data)

    assert len(wizard.color_rows) == 1
    row = wizard.color_rows[0]
    assert row.get_rgb() == (0, 170, 255)
    assert row.has_hsv_ranges()
    assert row.get_hsv_ranges_fractional() == hsv_ranges


def test_hsv_color_range_wizard_recent_color_without_ranges(app, hsv_color_range_config):
    """A recent color without ranges falls back to the default tolerance preset."""
    if not _WIZARD_DEPENDENCIES_AVAILABLE:
        pytest.skip(f"Wizard dependencies not available: {_WIZARD_IMPORT_ERROR}")
    wizard = HSVColorRangeWizardController(hsv_color_range_config, 'Dark')

    wizard._on_recent_color_selected({'selected_color': (10, 20, 30)})

    assert len(wizard.color_rows) == 1
    row = wizard.color_rows[0]
    assert row.get_rgb() == (10, 20, 30)
    assert not row.has_hsv_ranges()


def test_hsv_color_range_wizard_recent_color_menu_flow(app, hsv_color_range_config):
    """End-to-end: choosing from the Recent Colors dialog adds the color.

    Exercises the full ColorSelectionMenu path that was previously broken for the
    wizard, proving the recent selection is no longer silently discarded.
    """
    if not _WIZARD_DEPENDENCIES_AVAILABLE:
        pytest.skip(f"Wizard dependencies not available: {_WIZARD_IMPORT_ERROR}")
    wizard = HSVColorRangeWizardController(hsv_color_range_config, 'Dark')

    hsv_ranges = {
        'h': 0.25, 's': 0.5, 'v': 0.75,
        'h_minus': 0.05, 'h_plus': 0.05,
        's_minus': 0.1, 's_plus': 0.1,
        'v_minus': 0.1, 'v_plus': 0.1,
    }
    color_data = {'selected_color': (0, 128, 200), 'hsv_ranges': hsv_ranges}

    menu = wizard.color_selection_menu
    with patch.object(menu._recent_colors_service, 'get_recent_hsv_colors', return_value=[color_data]), \
         patch('algorithms.Shared.views.ColorSelectionMenu.RecentColorsDialog') as MockDialog:
        dialog = MockDialog.return_value
        dialog.exec.return_value = True
        dialog.get_selected_color_data.return_value = color_data
        menu._select_from_recent_colors()

    assert len(wizard.color_rows) == 1
    row = wizard.color_rows[0]
    assert row.get_rgb() == (0, 128, 200)
    assert row.has_hsv_ranges()


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


@pytest.fixture
def ai_person_detector_config():
    """Sample AIPersonDetector algorithm config."""
    return {
        'name': 'AIPersonDetector',
        'label': 'AI Person Detector',
        'controller': 'AIPersonDetectorController',
        'wizard_controller': 'AIPersonDetectorWizardController',
        'service': 'AIPersonDetectorService',
        'combine_overlapping_aois': False,
        'platforms': ['Windows', 'Darwin'],
        'type': 'RGB'
    }


def test_ai_person_detector_wizard_get_options_mapping(app, ai_person_detector_config):
    """Each slider preset maps to its confidence percent."""
    if not _WIZARD_DEPENDENCIES_AVAILABLE:
        pytest.skip(f"Wizard dependencies not available: {_WIZARD_IMPORT_ERROR}")
    wizard = AIPersonDetectorWizardController(ai_person_detector_config, 'Dark')

    for index, percent in {0: 90, 1: 70, 2: 50, 3: 30, 4: 10}.items():
        wizard.confidenceSlider.setValue(index)
        options = wizard.get_options()
        assert options['person_detector_confidence'] == percent
        assert options['confidence_index'] == index
        assert options['cpu_only'] is False


def test_ai_person_detector_wizard_load_options_prefers_index(app, ai_person_detector_config):
    """confidence_index restores the slider position directly."""
    if not _WIZARD_DEPENDENCIES_AVAILABLE:
        pytest.skip(f"Wizard dependencies not available: {_WIZARD_IMPORT_ERROR}")
    wizard = AIPersonDetectorWizardController(ai_person_detector_config, 'Dark')

    wizard.load_options({'confidence_index': 3, 'person_detector_confidence': 90})

    assert wizard.confidenceSlider.value() == 3


def test_ai_person_detector_wizard_load_options_percent_scale(app, ai_person_detector_config):
    """Regression: percent-scale confidence maps to the matching preset.

    Previously the reverse mapping compared percent values against 0-1
    fraction thresholds, so any saved config without confidence_index
    snapped to Very Confident.
    """
    if not _WIZARD_DEPENDENCIES_AVAILABLE:
        pytest.skip(f"Wizard dependencies not available: {_WIZARD_IMPORT_ERROR}")
    wizard = AIPersonDetectorWizardController(ai_person_detector_config, 'Dark')

    for percent, expected_index in [(90, 0), (70, 1), (50, 2), (30, 3), (10, 4)]:
        wizard.load_options({'person_detector_confidence': percent})
        assert wizard.confidenceSlider.value() == expected_index, \
            f"{percent}% should map to index {expected_index}"


def test_ai_person_detector_wizard_load_options_fraction_scale(app, ai_person_detector_config):
    """Legacy 0-1 fraction confidence values map onto the same presets."""
    if not _WIZARD_DEPENDENCIES_AVAILABLE:
        pytest.skip(f"Wizard dependencies not available: {_WIZARD_IMPORT_ERROR}")
    wizard = AIPersonDetectorWizardController(ai_person_detector_config, 'Dark')

    for fraction, expected_index in [(0.9, 0), (0.7, 1), (0.5, 2), (0.3, 3), (0.1, 4)]:
        wizard.load_options({'person_detector_confidence': fraction})
        assert wizard.confidenceSlider.value() == expected_index, \
            f"fraction {fraction} should map to index {expected_index}"


def test_ai_person_detector_wizard_load_options_invalid_input(app, ai_person_detector_config):
    """Non-dict options and malformed values leave the slider unchanged."""
    if not _WIZARD_DEPENDENCIES_AVAILABLE:
        pytest.skip(f"Wizard dependencies not available: {_WIZARD_IMPORT_ERROR}")
    wizard = AIPersonDetectorWizardController(ai_person_detector_config, 'Dark')
    wizard.confidenceSlider.setValue(1)

    wizard.load_options(None)
    wizard.load_options('not a dict')
    wizard.load_options({'person_detector_confidence': 'garbage'})

    assert wizard.confidenceSlider.value() == 1
