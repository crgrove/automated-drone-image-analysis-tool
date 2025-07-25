from ast import literal_eval

from algorithms.Algorithm import AlgorithmController
from algorithms.HSVColorRange.views.HSVColorRange_ui import Ui_HSVColorRange
from algorithms.HSVColorRange.controllers.HSVColorRangeViewerController import HSVColorRangeRangeViewer
from core.services.LoggerService import LoggerService

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QColorDialog


class HSVColorRangeController(QWidget, Ui_HSVColorRange, AlgorithmController):
    """Controller for the HSV Filter algorithm widget."""

    def __init__(self, config):
        """
        Initializes the HSVColorRangeController widget and sets up the UI.

        Connects UI elements like threshold spinboxs and color selection button
        to their respective event handlers.
        """
        QWidget.__init__(self)
        AlgorithmController.__init__(self, config)
        self.logger = LoggerService()
        self.setupUi(self)
        self.viewRangeButton.hide()
        self.selectedColor = None

        # Connect button events
        self.colorButton.clicked.connect(self.color_button_clicked)
        self.viewRangeButton.clicked.connect(self.view_range_button_clicked)

    def color_button_clicked(self):
        """
        Handles the color selection button click.

        Opens a color picker dialog to allow the user to select a color.
        Updates the selected color if a valid color is chosen.
        """
        
        try:
            if self.selectedColor is not None:
                color = QColorDialog.getColor(self.selectedColor)
            else:
                color = QColorDialog.getColor()
            if color.isValid():
                self.selectedColor = color
                self.update_colors()
        except Exception as e:
            self.logger.error(e)

    def view_range_button_clicked(self):
        """
        Handles the view range button click.

        Opens the View Range dialog, displaying the selected color and
        threshold values for H, S, V.
        """
        rangeDialog = HSVColorRangeRangeViewer(
            (self.selectedColor.red(),
             self.selectedColor.green(),
             self.selectedColor.blue()),
            self.hueSpinBox.value(),
            self.saturationSpinBox.value(),
            self.valueSpinBox.value())
        rangeDialog.exec()

    def update_colors(self):
        """
        Updates the color of the selected color box and shows the view range button.
        """
        if self.selectedColor is not None:
            self.colorSample.setStyleSheet("background-color: " + self.selectedColor.name())
            self.viewRangeButton.show()

    def get_options(self):
        options = dict()
        if self.selectedColor is not None:
            options['selected_color'] = (self.selectedColor.red(), self.selectedColor.green(), self.selectedColor.blue())
            options['hue_threshold'] = self.hueSpinBox.value()
            options['saturation_threshold'] = self.saturationSpinBox.value()
            options['value_threshold'] = self.valueSpinBox.value()
        else:
            options['selected_color'] = None
            options['hue_threshold'] = None
            options['saturation_threshold'] = None
            options['value_threshold'] = None
        return options

    def validate(self):
        """
        Validates that the required values have been provided.

        Returns:
            str: An error message if validation fails, otherwise None.
        """
        if self.selectedColor is None:
            return "Please select a search color."
        return None

    def load_options(self, options):
        """
        Sets UI elements based on the provided options.

        Args:
            options (dict): The options to use to set UI attributes, including 'selected_color' and HSV thresholds.
        """
        if 'selected_color' in options:
            selected_color = literal_eval(options['selected_color'])
            self.selectedColor = QColor(selected_color[0], selected_color[1], selected_color[2])
            self.colorSample.setStyleSheet("background-color: " + self.selectedColor.name())
            self.viewRangeButton.show()

        if 'hue_threshold' in options:
            self.hueSpinBox.setValue(int(options['hue_threshold']))

        if 'saturation_threshold' in options:
            self.saturationSpinBox.setValue(int(options['saturation_threshold']))

        if 'value_threshold' in options:
            self.valueSpinBox.setValue(int(options['value_threshold']))
