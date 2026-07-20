"""
Wizard controller for Thermal Residual Anomaly algorithm.

Maps wizard aggressiveness and anomaly direction to residual detector options.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QButtonGroup

from algorithms.AlgorithmController import AlgorithmController
from algorithms.images.ThermalResidualAnomaly.views.ThermalResidualAnomalyWizard_ui import Ui_ThermalResidualAnomalyWizard
from core.views.components.LabeledSlider import TextLabeledSlider


class ThermalResidualAnomalyWizardController(QWidget, Ui_ThermalResidualAnomalyWizard, AlgorithmController):
    """Wizard controller for Thermal Residual Anomaly algorithm."""

    def __init__(self, config, theme):
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.theme = theme
        self.config = config

        self.setupUi(self)
        self._wire_up_ui()

    def _wire_up_ui(self):
        type_group = QButtonGroup(self)
        type_group.addButton(self.radioTypeHot)
        type_group.addButton(self.radioTypeCold)
        type_group.addButton(self.radioTypeBoth)

        default_labels = [
            self.tr('Very \nConservative'),
            self.tr('Conservative'),
            self.tr('Moderate'),
            self.tr('Aggressive'),
            self.tr('Very \nAggressive'),
        ]
        labels = self.config.get('aggressiveness_labels', default_labels)
        labels = [self.tr(label) for label in labels]
        labels = [
            label.replace('Very\n', 'Very \n') if '\n' in label and 'Very \n' not in label else label
            for label in labels
        ]

        self.aggressivenessSlider = TextLabeledSlider(self, presets=labels)
        placeholder = self.aggressivenessSliderPlaceholder
        layout = QVBoxLayout(placeholder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.aggressivenessSlider)

    def _read_ui_state(self):
        if self.radioTypeHot.isChecked():
            anomaly_type = 'Hot'
        elif self.radioTypeCold.isChecked():
            anomaly_type = 'Cold'
        else:
            anomaly_type = 'Both'

        aggr_index = self.aggressivenessSlider.value()
        aggr_label, aggr_value = self.aggressivenessSlider.getCurrentPreset()
        return anomaly_type, aggr_index, aggr_label, aggr_value

    def get_options(self):
        options = dict()
        anomaly_type, aggr_index, aggr_label, _ = self._read_ui_state()

        sensitivity_map = {0: 1, 1: 3, 2: 5, 3: 7, 4: 10}
        sensitivity = sensitivity_map.get(aggr_index, 5)

        type_map = {'Hot': 'Hot', 'Cold': 'Cold', 'Both': 'Both'}
        type_value = type_map.get(anomaly_type, 'Both')

        options['sensitivity'] = sensitivity
        options['type'] = type_value

        options['anomaly_type'] = anomaly_type
        options['aggressiveness_index'] = aggr_index
        options['aggressiveness_label'] = aggr_label

        return options

    def validate(self):
        return None

    def load_options(self, options):
        if not isinstance(options, dict):
            return

        anomaly_type = options.get('anomaly_type', options.get('type', 'Both'))
        if anomaly_type in ('Above Mean', 'Warmer than surroundings'):
            anomaly_type = 'Hot'
        elif anomaly_type in ('Below Mean', 'Cooler than surroundings'):
            anomaly_type = 'Cold'
        elif anomaly_type in ('Above or Below Mean',):
            anomaly_type = 'Both'

        if anomaly_type == 'Hot':
            self.radioTypeHot.setChecked(True)
        elif anomaly_type == 'Cold':
            self.radioTypeCold.setChecked(True)
        else:
            self.radioTypeBoth.setChecked(True)

        aggr_index = options.get('aggressiveness_index')
        if isinstance(aggr_index, int):
            self.aggressivenessSlider.setValue(max(0, min(4, aggr_index)))
        elif 'sensitivity' in options:
            sensitivity = max(1, min(10, int(options['sensitivity'])))
            if sensitivity <= 2:
                self.aggressivenessSlider.setValue(0)
            elif sensitivity <= 4:
                self.aggressivenessSlider.setValue(1)
            elif sensitivity <= 6:
                self.aggressivenessSlider.setValue(2)
            elif sensitivity <= 8:
                self.aggressivenessSlider.setValue(3)
            else:
                self.aggressivenessSlider.setValue(4)

        # Legacy no-op for persisted historical fields.
        _ = options.get('complex_scene')
        _ = options.get('segments')
