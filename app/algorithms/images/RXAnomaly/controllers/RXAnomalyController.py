from algorithms.AlgorithmController import AlgorithmController
from algorithms.images.RXAnomaly.views.RXAnomaly_ui import Ui_RXAnomaly

from PySide6.QtWidgets import QWidget


class RXAnomalyController(QWidget, Ui_RXAnomaly, AlgorithmController):
    """Controller for the RX Anomaly algorithm widget."""

    def __init__(self, config, theme):
        """
        Initializes the RXAnomalyController widget and sets up the UI.

        Connects the sensitivity slider to the update_sensitivity handler.

        Args:
            config (dict): Algorithm config information.
            theme (str): Name of the active theme used to resolve icon paths.
        """
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.setupUi(self)
        self._init_segments_combo_data()
        self.fixComboBoxForMacOS(self.segmentsComboBox)
        self.sensitivitySlider.valueChanged.connect(self.update_sensitivity)

    def _init_segments_combo_data(self):
        """Attach stable numeric values so translated labels do not affect config values."""
        for index in range(self.segmentsComboBox.count()):
            text = self.segmentsComboBox.itemText(index)
            try:
                self.segmentsComboBox.setItemData(index, int(text))
            except ValueError:
                continue

    def get_options(self):
        """
        Populates options based on user-selected values.

        Returns:
            dict: A dictionary containing the selected option values, including 'sensitivity' and 'segments'.
        """
        options = dict()
        options['sensitivity'] = int(self.sensitivityValueLabel.text())
        options['segments'] = int(self.segmentsComboBox.currentData())
        return options

    def update_sensitivity(self):
        """
        Handles changes to the sensitivity slider.

        Updates the sensitivity value label based on the current slider position.
        """
        self.sensitivityValueLabel.setText(str(self.sensitivitySlider.value()))

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
            options (dict): The options to use to set UI attributes, including 'sensitivity' and 'segments'.
        """
        if 'sensitivity' in options:
            self.sensitivityValueLabel.setText(str(options['sensitivity']))
            self.sensitivitySlider.setProperty("value", int(options['sensitivity']))
        if 'segments' in options:
            index = self.segmentsComboBox.findData(int(options['segments']))
            if index >= 0:
                self.segmentsComboBox.setCurrentIndex(index)
            else:
                self.segmentsComboBox.setCurrentText(str(options['segments']))
