from algorithms.AlgorithmController import AlgorithmController
from algorithms.images.ThermalAnomaly.views.ThermalAnomaly_ui import Ui_ThermalAnomaly
from core.services.SettingsService import SettingsService

from PySide6.QtWidgets import QWidget


class ThermalAnomalyController(QWidget, Ui_ThermalAnomaly, AlgorithmController):
    """Controller for the Thermal Anomaly algorithm widget."""

    def __init__(self, config, theme):
        """
        Initializes the ThermalAnomalyController widget and sets up the UI.

        Args:
            config (dict): Algorithm config information.
            theme (str): Name of the active theme used to resolve icon paths.
        """
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.settings_service = SettingsService()
        self.setupUi(self)
        self._init_combo_data()

    def _init_combo_data(self):
        """Attach stable option keys so translated labels do not affect config values."""
        if self.anomalyTypeComboBox.count() >= 3:
            self.anomalyTypeComboBox.setItemData(0, 'Both')
            self.anomalyTypeComboBox.setItemData(1, 'Hot')
            self.anomalyTypeComboBox.setItemData(2, 'Cold')

        for index in range(self.segmentsComboBox.count()):
            text = self.segmentsComboBox.itemText(index)
            try:
                self.segmentsComboBox.setItemData(index, int(text))
            except ValueError:
                continue

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
        """Persist canonical type keys as the legacy labels expected by the service."""
        type_key = ThermalAnomalyController._normalize_type(value)
        return {
            'Hot': 'Above Mean',
            'Cold': 'Below Mean',
            'Both': 'Above or Below Mean',
        }.get(type_key, 'Above or Below Mean')

    def get_options(self):
        """
        Populates options based on user-selected values.

        Returns:
            dict: A dictionary containing the selected option values, including
            'threshold' and 'type'.
        """
        options = dict()
        options['threshold'] = int(self.anomalySpinBox.value())
        options['segments'] = int(self.segmentsComboBox.currentData())
        options['type'] = self._serialize_type(self.anomalyTypeComboBox.currentData())
        return options

    def validate(self):
        """
        Validates that the required values have been provided.

        Returns:
            str: An error message if validation fails, otherwise None.
        """
        return None

    def load_options(self, options):
        """
        Sets UI elements based on the provided options.

        Args:
            options (dict): The options to use to set UI attributes, including
            'threshold' and 'type'.
        """
        if 'threshold' in options:
            self.anomalySpinBox.setValue(int(options['threshold']))
        if 'segments' in options:
            index = self.segmentsComboBox.findData(int(options['segments']))
            if index >= 0:
                self.segmentsComboBox.setCurrentIndex(index)
            else:
                self.segmentsComboBox.setCurrentText(str(options['segments']))
        if 'type' in options:
            type_key = self._normalize_type(options['type'])
            index = self.anomalyTypeComboBox.findData(type_key)
            if index >= 0:
                self.anomalyTypeComboBox.setCurrentIndex(index)
            else:
                self.anomalyTypeComboBox.setCurrentText(str(options['type']))
