from algorithms.AlgorithmController import AlgorithmController
from algorithms.ThermalRange.views.ThermalRange_ui import Ui_ThermalRange
from core.services.SettingsService import SettingsService

from PySide6.QtWidgets import QWidget


class ThermalRangeController(QWidget, Ui_ThermalRange, AlgorithmController):
    """Controller for the Thermal Range algorithm widget."""

    def __init__(self, config, theme):
        """
        Initializes the ThermalRangeController widget and sets up the UI.

        If the temperature unit is set to Fahrenheit in the settings, converts
        the temperature ranges to Fahrenheit.

        Args:
            config (dict): Algorithm config information.
            theme (str): Name of the active theme used to resolve icon paths.
        """
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.settings_service = SettingsService()
        self.setupUi(self)
        if self.settings_service.get_setting('TemperatureUnit') == 'Fahrenheit':
            self.convert_temperature_ranges()
        self.minTempSpinBox.editingFinished.connect(self.update_min_temp)
        self.maxTempSpinBox.editingFinished.connect(self.update_max_temp)

    def get_options(self):
        """
        Populates options based on user-selected values.

        Returns:
            dict: A dictionary containing option names and values, including
            'minTemp' and 'maxTemp'.
        """
        options = dict()
        if self.settings_service.get_setting('TemperatureUnit') == 'Fahrenheit':
            options['minTemp'] = self.convert_fahrenheit_to_celsius(int(self.minTempSpinBox.value()))
            options['maxTemp'] = self.convert_fahrenheit_to_celsius(int(self.maxTempSpinBox.value()))
        else:
            options['minTemp'] = int(self.minTempSpinBox.value())
            options['maxTemp'] = int(self.maxTempSpinBox.value())

        return options

    def update_min_temp(self):
        """
        Handles changes to the minimum temperature slider.

        Ensures that the minimum temperature does not exceed the maximum
        temperature by adjusting the maximum temperature if necessary.
        """
        if self.minTempSpinBox.value() > self.maxTempSpinBox.value():
            self.maxTempSpinBox.setValue(self.minTempSpinBox.value())

    def update_max_temp(self):
        """
        Handles changes to the maximum temperature slider.

        Ensures that the maximum temperature does not fall below the minimum
        temperature by adjusting the minimum temperature if necessary.
        """
        if self.minTempSpinBox.value() > self.maxTempSpinBox.value():
            self.minTempSpinBox.setValue(self.maxTempSpinBox.value())

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
            'minTemp' and 'maxTemp'.
        """
        if self.settings_service.get_setting('TemperatureUnit') == 'Fahrenheit':
            if 'minTemp' in options:
                self.minTempSpinBox.setValue(int(self.convert_celsius_to_fahrenheit(float(options['minTemp']))))
            if 'maxTemp' in options:
                self.maxTempSpinBox.setValue(int(self.convert_celsius_to_fahrenheit(float(options['maxTemp']))))
        else:
            if 'minTemp' in options:
                self.minTempSpinBox.setValue(int(float(options['minTemp'])))
            if 'maxTemp' in options:
                self.maxTempSpinBox.setValue(int(float(options['maxTemp'])))

    def convert_temperature_ranges(self):
        """
        Modifies the temperature range controls to accept Fahrenheit values
        instead of Celsius.

        Sets the minimum and maximum values for temperature spin boxes
        accordingly and adjusts the displayed unit labels.
        """
        self.minTempLabel.setText('Minimum Temp (' + u'\N{DEGREE SIGN}' + ' F)')
        self.minTempSpinBox.setMinimum(-20)
        self.minTempSpinBox.setMaximum(120)
        self.minTempSpinBox.setValue(95)
        self.maxTempLabel.setText('Maximum Temp (' + u'\N{DEGREE SIGN}' + ' F)')
        self.maxTempSpinBox.setMinimum(-20)
        self.maxTempSpinBox.setMaximum(200)
        self.maxTempSpinBox.setValue(105)

    def convert_fahrenheit_to_celsius(self, value):
        """
        Converts a Fahrenheit value to Celsius.

        Args:
            value (int): The Fahrenheit value to convert.

        Returns:
            float: The converted Celsius value.
        """
        return (value - 32) / 1.8000

    def convert_celsius_to_fahrenheit(self, value):
        """
        Converts a Celsius value to Fahrenheit.

        Args:
            value (int): The Celsius value to convert.

        Returns:
            float: The converted Fahrenheit value.
        """
        return (value * 1.8000) + 32
