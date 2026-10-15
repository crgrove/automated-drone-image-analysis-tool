"""qtbot tests for the Rectilinear Shape advanced panel and wizard page.

Covers option round-tripping, preset switching, validation, older and
XML-stringified option dicts, the cm/inch display, and the wizard -> main
panel handoff MainWindow performs.
"""

from unittest.mock import patch

import pytest

from algorithms.images.RectilinearShape.controllers.RectilinearShapeController import RectilinearShapeController
from algorithms.images.RectilinearShape.controllers.RectilinearShapeWizardController import (
    RectilinearShapeWizardController,
)
from algorithms.images.RectilinearShape.services.RectilinearPresets import (
    DEFAULT_OPTIONS,
    PRESET_SIZES_CM,
    SENSITIVITY_TO_CONFIDENCE,
)


def _config():
    return {
        'name': 'RectilinearShape',
        'label': 'Rectilinear Shape (Man-Made Objects)',
        'controller': 'RectilinearShapeController',
        'wizard_controller': 'RectilinearShapeWizardController',
        'service': 'RectilinearShapeService',
        'combine_overlapping_aois': False,
        'platforms': ['Windows', 'Darwin', 'Linux'],
        'type': 'RGB',
    }


def _with_unit(unit):
    """Patch the DistanceUnit setting both controllers read at construction."""
    return patch('core.services.SettingsService.SettingsService.get_setting', return_value=unit)


@pytest.fixture
def panel(app, qtbot):
    with _with_unit('Meters'):
        widget = RectilinearShapeController(_config(), 'Dark')
    qtbot.addWidget(widget)
    return widget


@pytest.fixture
def wizard(app, qtbot):
    with _with_unit('Meters'):
        widget = RectilinearShapeWizardController(_config(), 'Dark')
    qtbot.addWidget(widget)
    return widget


def _select(combo, preset):
    combo.setCurrentIndex(combo.findData(preset))


# --- advanced panel -----------------------------------------------------------

def test_the_panel_starts_at_the_defaults(panel):
    assert panel.get_options() == DEFAULT_OPTIONS
    assert panel.validate() is None
    assert not panel.is_thermal


def test_every_option_round_trips(panel, qtbot):
    options = dict(
        DEFAULT_OPTIONS,
        target_preset='custom',
        long_side_cm_min=42.0, long_side_cm_max=90.0, short_side_cm_min=25.0, short_side_cm_max=50.0,
        size_tolerance=0.35, angle_tolerance_deg=8.0, min_edge_contrast=14.0, min_edge_support=0.6,
        use_boxiness=False, min_boxiness=0.5, min_short_side_px=16, min_confidence=65.0,
        max_detections_per_image=10, fallback_gsd_cm=1.25, debug_output=True,
    )
    panel.load_options(options)
    assert panel.get_options() == options
    assert not panel.minBoxinessSpinBox.isEnabled()


@pytest.mark.parametrize('preset', list(PRESET_SIZES_CM))
def test_choosing_a_preset_fills_the_sizes(panel, preset):
    _select(panel.presetComboBox, preset)
    long_min, long_max, short_min, short_max = PRESET_SIZES_CM[preset]
    assert panel.longMinSpinBox.value() == pytest.approx(long_min)
    assert panel.shortMaxSpinBox.value() == pytest.approx(short_max)
    options = panel.get_options()
    assert options['target_preset'] == preset
    assert (options['long_side_cm_min'], options['long_side_cm_max'],
            options['short_side_cm_min'], options['short_side_cm_max']) == PRESET_SIZES_CM[preset]


def test_editing_a_size_makes_the_target_custom(panel):
    _select(panel.presetComboBox, 'cooler_box')
    panel.longMaxSpinBox.setValue(120.0)
    options = panel.get_options()
    assert options['target_preset'] == 'custom'
    assert options['long_side_cm_max'] == 120.0
    # The other sizes keep what the preset put there.
    assert options['long_side_cm_min'] == PRESET_SIZES_CM['cooler_box'][0]


def test_choosing_custom_keeps_the_sizes(panel):
    _select(panel.presetComboBox, 'tent_small')
    _select(panel.presetComboBox, 'custom')
    assert panel.get_options()['long_side_cm_min'] == PRESET_SIZES_CM['tent_small'][0]


@pytest.mark.parametrize('spin_box, value, message', [
    ('longMinSpinBox', 100.0, 'long side'),
    ('shortMinSpinBox', 60.0, 'short side'),
    ('shortMaxSpinBox', 90.0, 'short side range'),
])
def test_validation_rejects_disordered_sizes(panel, spin_box, value, message):
    getattr(panel, spin_box).setValue(value)
    error = panel.validate()
    assert error is not None
    assert message in error


def test_options_saved_by_an_earlier_build_load_with_defaults(panel):
    """A dict missing newer keys must load, the missing keys taking their defaults."""
    panel.load_options({'target_preset': 'suitcase_flat', 'min_confidence': 60.0})
    options = panel.get_options()
    assert options['target_preset'] == 'suitcase_flat'
    assert options['min_confidence'] == 60.0
    assert options['use_boxiness'] is True
    assert options['max_detections_per_image'] == 25


def test_options_read_back_from_adiat_data_load(panel):
    """ADIAT_Data.xml stores every value as a string and every falsy value as ''."""
    panel.load_options({
        'target_preset': 'custom',
        'long_side_cm_min': '40.0', 'long_side_cm_max': '70.0',
        'short_side_cm_min': '25.0', 'short_side_cm_max': '45.0',
        'size_tolerance': '0.3', 'use_boxiness': '', 'debug_output': 'True',
        'fallback_gsd_cm': '', 'min_short_side_px': '14', 'max_detections_per_image': '5',
    })
    options = panel.get_options()
    assert options['long_side_cm_max'] == 70.0
    assert options['size_tolerance'] == pytest.approx(0.3)
    assert options['use_boxiness'] is False
    assert options['debug_output'] is True
    assert options['fallback_gsd_cm'] is None
    assert options['min_short_side_px'] == 14
    assert options['max_detections_per_image'] == 5


def test_an_unknown_preset_loads_as_custom_with_its_sizes(panel):
    panel.load_options({'target_preset': 'kayak', 'long_side_cm_min': 250.0, 'long_side_cm_max': 400.0,
                        'short_side_cm_min': 50.0, 'short_side_cm_max': 90.0})
    options = panel.get_options()
    assert options['target_preset'] == 'custom'
    assert options['long_side_cm_max'] == 400.0


def test_a_zero_fallback_means_none(panel):
    panel.fallbackGsdSpinBox.setValue(0.0)
    assert panel.get_options()['fallback_gsd_cm'] is None
    assert panel.fallbackGsdSpinBox.text() == 'None'


def test_sizes_display_in_inches_and_store_in_cm(app, qtbot):
    with _with_unit('Feet'):
        panel = RectilinearShapeController(_config(), 'Dark')
    qtbot.addWidget(panel)
    assert panel.longMaxSpinBox.suffix().strip() == 'in'
    assert panel.longMaxSpinBox.value() == pytest.approx(80.0 / 2.54, abs=0.01)
    # A preset's sizes are exact, not read back through the inch display.
    assert panel.get_options()['long_side_cm_max'] == 80.0
    panel.longMaxSpinBox.setValue(40.0)
    assert panel.get_options()['long_side_cm_max'] == pytest.approx(101.6)


# --- wizard -------------------------------------------------------------------

def test_the_wizard_defaults_to_any_suitcase_at_medium(wizard):
    options = wizard.get_options()
    assert options['target_preset'] == 'suitcase_any'
    assert options['sensitivity'] == 'medium'
    assert options['min_confidence'] == SENSITIVITY_TO_CONFIDENCE['medium']
    assert not wizard.customSizeWidget.isEnabled()
    assert wizard.validate() is None


@pytest.mark.parametrize('index, sensitivity', [(0, 'low'), (1, 'medium'), (2, 'high')])
def test_sensitivity_maps_to_the_emission_threshold(wizard, index, sensitivity):
    wizard.sensitivitySlider.setValue(index)
    options = wizard.get_options()
    assert options['sensitivity'] == sensitivity
    assert options['min_confidence'] == SENSITIVITY_TO_CONFIDENCE[sensitivity]


def test_higher_sensitivity_shows_more(wizard):
    thresholds = []
    for index in range(3):
        wizard.sensitivitySlider.setValue(index)
        thresholds.append(wizard.get_options()['min_confidence'])
    assert thresholds == sorted(thresholds, reverse=True)


def test_custom_sizes_are_editable_only_for_custom(wizard):
    _select(wizard.presetComboBox, 'custom')
    assert wizard.customSizeWidget.isEnabled()
    wizard.longMinSpinBox.setValue(30.0)
    wizard.longMaxSpinBox.setValue(45.0)
    wizard.shortMinSpinBox.setValue(15.0)
    wizard.shortMaxSpinBox.setValue(30.0)
    options = wizard.get_options()
    assert (options['long_side_cm_min'], options['long_side_cm_max'],
            options['short_side_cm_min'], options['short_side_cm_max']) == (30.0, 45.0, 15.0, 30.0)
    _select(wizard.presetComboBox, 'cooler_box')
    assert not wizard.customSizeWidget.isEnabled()
    assert wizard.longMaxSpinBox.value() == PRESET_SIZES_CM['cooler_box'][1]


def test_the_wizard_validates_custom_sizes(wizard):
    _select(wizard.presetComboBox, 'custom')
    wizard.longMinSpinBox.setValue(90.0)
    assert wizard.validate() is not None


def test_the_wizard_emits_every_service_key(wizard):
    """MainWindow feeds the wizard's dict to the advanced panel's load_options."""
    assert set(DEFAULT_OPTIONS) <= set(wizard.get_options())


def test_the_wizard_restores_its_page(wizard):
    _select(wizard.presetComboBox, 'tent_small')
    wizard.sensitivitySlider.setValue(2)
    saved = wizard.get_options()
    wizard.load_options(DEFAULT_OPTIONS)
    wizard.load_options(saved)
    assert wizard.presetComboBox.currentData() == 'tent_small'
    assert wizard.sensitivitySlider.value() == 2


def test_the_wizard_restores_sensitivity_from_a_threshold_alone(wizard):
    wizard.load_options({'min_confidence': '65.0'})
    assert wizard.sensitivitySlider.value() == 0


def test_the_wizard_hands_off_to_the_advanced_panel(wizard, panel):
    _select(wizard.presetComboBox, 'cooler_box')
    wizard.sensitivitySlider.setValue(2)
    handed_off = wizard.get_options()
    panel.load_options(handed_off)
    received = panel.get_options()
    assert received['target_preset'] == 'cooler_box'
    assert received['min_confidence'] == SENSITIVITY_TO_CONFIDENCE['high']
    for key in DEFAULT_OPTIONS:
        assert received[key] == handed_off[key]
