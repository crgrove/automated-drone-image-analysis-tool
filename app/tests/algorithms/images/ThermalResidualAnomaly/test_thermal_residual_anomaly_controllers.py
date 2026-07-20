from algorithms.images.ThermalResidualAnomaly.controllers.ThermalResidualAnomalyController import ThermalResidualAnomalyController
from algorithms.images.ThermalResidualAnomaly.controllers.ThermalResidualAnomalyWizardController import ThermalResidualAnomalyWizardController


def _config():
    return {
        'name': 'ThermalResidualAnomaly',
        'label': 'Temperature Residual Anomaly',
        'controller': 'ThermalResidualAnomalyController',
        'wizard_controller': 'ThermalResidualAnomalyWizardController',
        'service': 'ThermalResidualAnomalyService',
        'combine_overlapping_aois': True,
        'platforms': ['Windows'],
        'type': 'Thermal'
    }


def test_standard_controller_get_options_excludes_segments(app, qtbot):
    controller = ThermalResidualAnomalyController(_config(), 'Dark')
    qtbot.addWidget(controller)

    controller.sensitivitySlider.setValue(8)
    controller.anomalyTypeComboBox.setCurrentText('Below Mean')

    options = controller.get_options()

    assert options['sensitivity'] == 8
    assert options['type'] == 'Below Mean'
    assert 'threshold' not in options
    assert 'segments' not in options


def test_standard_controller_load_options_tolerates_legacy_segments(app, qtbot):
    controller = ThermalResidualAnomalyController(_config(), 'Dark')
    qtbot.addWidget(controller)

    controller.load_options({'threshold': 3, 'type': 'Above Mean', 'segments': 16})

    assert controller.sensitivitySlider.value() == 6
    assert controller.anomalyTypeComboBox.currentText() == 'Above Mean'


def test_wizard_get_options_excludes_complex_scene_and_segments(app, qtbot):
    wizard = ThermalResidualAnomalyWizardController(_config(), 'Dark')
    qtbot.addWidget(wizard)

    wizard.radioTypeCold.setChecked(True)
    wizard.aggressivenessSlider.setValue(1)

    options = wizard.get_options()

    assert options['sensitivity'] == 3
    assert options['type'] == 'Cold'
    assert options['anomaly_type'] == 'Cold'
    assert 'segments' not in options
    assert 'complex_scene' not in options


def test_wizard_load_options_tolerates_legacy_fields(app, qtbot):
    wizard = ThermalResidualAnomalyWizardController(_config(), 'Dark')
    qtbot.addWidget(wizard)

    wizard.load_options({'anomaly_type': 'Hot', 'aggressiveness_index': 4, 'complex_scene': True, 'segments': 9})

    assert wizard.radioTypeHot.isChecked()
    assert wizard.aggressivenessSlider.value() == 4
