from algorithms.AlgorithmController import AlgorithmController
from algorithms.ThermalAnomaly.views.ThermalAnomaly_ui import Ui_ThermalAnomaly
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

    def get_options(self):
        """
        Populates options based on user-selected values.

        Returns:
            dict: A dictionary containing the selected option values, including
            'threshold' and 'type'.
        """
        options = dict()
        options['threshold'] = int(self.anomalySpinBox.value())
        options['segments'] = int(self.segmentsComboBox.currentText())
        options['type'] = self.anomalyTypeComboBox.currentText()
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
            self.segmentsComboBox.setCurrentText(str(options['segments']))
        if 'type' in options:
            self.anomalyTypeComboBox.setCurrentText(options['type'])
