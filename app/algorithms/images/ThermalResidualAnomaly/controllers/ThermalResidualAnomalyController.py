from PySide6.QtWidgets import QWidget

from algorithms.AlgorithmController import AlgorithmController
from algorithms.images.ThermalResidualAnomaly.views.ThermalResidualAnomaly_ui import Ui_ThermalResidualAnomaly
from core.services.SettingsService import SettingsService


class ThermalResidualAnomalyController(QWidget, Ui_ThermalResidualAnomaly, AlgorithmController):
    """Controller for the Thermal Residual Anomaly algorithm widget."""

    def __init__(self, config, theme):
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.settings_service = SettingsService()
        self.setupUi(self)
        self._init_type_combo_data()
        self.sensitivitySlider.valueChanged.connect(self.update_sensitivity)

    def _init_type_combo_data(self):
        """Attach stable option keys so translated labels do not affect config values."""
        if self.anomalyTypeComboBox.count() >= 3:
            self.anomalyTypeComboBox.setItemData(0, 'Both')
            self.anomalyTypeComboBox.setItemData(1, 'Hot')
            self.anomalyTypeComboBox.setItemData(2, 'Cold')

    @staticmethod
    def _normalize_type(value):
        """Normalize legacy and UI values to canonical type keys."""
        normalized = str(value or 'Both').strip().lower()
        if normalized in {'hot', 'above mean', 'warmer than surroundings'}:
            return 'Hot'
        if normalized in {'cold', 'below mean', 'cooler than surroundings'}:
            return 'Cold'
        return 'Both'

    @staticmethod
    def _serialize_type(value):
        """Persist canonical type keys as the legacy labels expected by saved configs."""
        type_key = ThermalResidualAnomalyController._normalize_type(value)
        return {
            'Hot': 'Above Mean',
            'Cold': 'Below Mean',
            'Both': 'Above or Below Mean',
        }.get(type_key, 'Above or Below Mean')

    def get_options(self):
        options = dict()
        options['sensitivity'] = int(self.sensitivityValueLabel.text())
        options['type'] = self._serialize_type(self.anomalyTypeComboBox.currentData())
        return options

    def update_sensitivity(self):
        self.sensitivityValueLabel.setText(str(self.sensitivitySlider.value()))

    def _threshold_to_sensitivity(self, threshold):
        threshold = float(threshold)
        mapping = {
            1: 8.0,
            2: 7.0,
            3: 6.0,
            4: 5.0,
            5: 4.0,
            6: 3.0,
            7: 2.0,
            8: 1.7,
            9: 1.3,
            10: 1.0,
        }
        return min(mapping, key=lambda value: abs(mapping[value] - threshold))

    def validate(self):
        return None

    def load_options(self, options):
        if not isinstance(options, dict):
            return

        if 'sensitivity' in options:
            sensitivity = max(1, min(10, int(options['sensitivity'])))
            self.sensitivitySlider.setProperty("value", sensitivity)
            self.sensitivityValueLabel.setText(str(sensitivity))
        if 'threshold' in options:
            sensitivity = self._threshold_to_sensitivity(options['threshold'])
            self.sensitivitySlider.setProperty("value", sensitivity)
            self.sensitivityValueLabel.setText(str(sensitivity))
        if 'type' in options:
            type_key = self._normalize_type(options['type'])
            index = self.anomalyTypeComboBox.findData(type_key)
            if index >= 0:
                self.anomalyTypeComboBox.setCurrentIndex(index)
            else:
                self.anomalyTypeComboBox.setCurrentText(str(options['type']))

        # Legacy no-op: tolerate historic settings that still include segments.
        _ = options.get('segments')
