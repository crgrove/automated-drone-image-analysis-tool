from algorithms.Algorithm import AlgorithmController
from algorithms.MRMap.views.MRMap_ui import Ui_MRMap

from PyQt5.QtWidgets import QWidget


class MRMapController(QWidget, Ui_MRMap, AlgorithmController):
    """Controller for the RX Anomaly algorithm widget."""

    def __init__(self):
        """
        Initializes the MRMapController widget and sets up the UI.

        Connects the threshold slider to the updatethreshold handler.
        """
        QWidget.__init__(self)
        AlgorithmController.__init__(self, 'MRMap', False)
        self.setupUi(self)
        self.thresholdSlider.valueChanged.connect(self.updatethreshold)

    def get_options(self):
        """
        Populates options based on user-selected values.

        Returns:
            dict: A dictionary containing the selected option values, including 'threshold', 'segments', and 'window'.
        """
        options = dict()
        options['threshold'] = int(self.thresholdValueLabel.text())
        options['segments'] = int(self.segmentsComboBox.currentText())
        options['window'] = self.windowSpinBox.value()
        return options

    def updatethreshold(self):
        """
        Handles changes to the threshold slider.

        Updates the threshold value label based on the current slider position.
        """
        self.thresholdValueLabel.setText(str(self.thresholdSlider.value()))

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
            options (dict): The options to use to set UI attributes, including 'threshold', 'segments', and 'version'.
        """
        if 'threshold' in options:
            self.thresholdValueLabel.setText(str(options['threshold']))
            self.thresholdSlider.setProperty("value", int(options['threshold']))
        if 'segments' in options:
            self.segmentsComboBox.setCurrentText(str(options['segments']))
        if 'window' in options:
            self.windowSpinBox.setValue(int(options['window']))
