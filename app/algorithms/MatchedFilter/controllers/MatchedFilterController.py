from ast import literal_eval

from algorithms.Algorithm import AlgorithmController
from algorithms.MatchedFilter.views.MatchedFilter_ui import Ui_MatchedFilter
from algorithms.MatchedFilter.controllers.MatchedFilterRangeViewerController import MatchedFilterRangeViewer
from core.services.LoggerService import LoggerService

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QColorDialog


class MatchedFilterController(QWidget, Ui_MatchedFilter, AlgorithmController):
    """Controller for the Matched Filter algorithm widget."""

    def __init__(self):
        """
        Initializes the MatchedFilterController widget and sets up the UI.

        Connects UI elements like threshold slider and color selection button
        to their respective event handlers.
        """
        QWidget.__init__(self)
        AlgorithmController.__init__(self, 'MatchedFilter', False)
        self.logger = LoggerService()
        self.setupUi(self)
        self.viewRangeButton.hide()
        self.selectedColor = None
        self.thresholdSlider.valueChanged.connect(self.updateThreshold)
        self.colorButton.clicked.connect(self.colorButtonClicked)
        self.viewRangeButton.clicked.connect(self.viewRangeButtonClicked)

    def colorButtonClicked(self):
        """
        Handles the color selection button click.

        Opens a color picker dialog to allow the user to select a color.
        Updates the selected color if a valid color is chosen.
        """
        try:
            if self.selectedColor is not None:
                self.selectedColor = QColorDialog().getColor(self.selectedColor)
            else:
                self.selectedColor = QColorDialog().getColor()
            if self.selectedColor.isValid():
                self.updateColors()
        except Exception as e:
            self.logger.error(e)

    def viewRangeButtonClicked(self):
        """
        Handles the view range button click.

        Opens the View Range dialog, displaying the selected color and
        threshold value.
        """
        rangeDialog = MatchedFilterRangeViewer(
            (self.selectedColor.red(),
             self.selectedColor.green(),
             self.selectedColor.blue()),
            float(self.thresholdValueLabel.text()))
        rangeDialog.exec()

    def updateColors(self):
        """
        Updates the color of the selected color box and shows the view range button.
        """
        if self.selectedColor is not None:
            self.colorSample.setStyleSheet("background-color: " + self.selectedColor.name())
            self.viewRangeButton.show()

    def updateThreshold(self):
        """
        Handles the threshold slider value change event.

        Updates the threshold value label based on the current slider position.
        """
        if self.thresholdSlider.value() == .1:
            self.thresholdValueLabel.setText('.1')
        elif self.thresholdSlider.value() == 10:
            self.thresholdValueLabel.setText('1')
        else:
            self.thresholdValueLabel.setText("." + str(self.thresholdSlider.value()))

    def getOptions(self):
        """
        Populates options based on user-selected values.

        Returns:
            dict: A dictionary containing selected options, including 'selected_color' and 'match_filter_threshold'.
        """
        options = dict()
        options['selected_color'] = (self.selectedColor.red(), self.selectedColor.green(), self.selectedColor.blue())
        options['match_filter_threshold'] = float(self.thresholdValueLabel.text())
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

    def loadOptions(self, options):
        """
        Sets UI elements based on the provided options.

        Args:
            options (dict): The options to use to set UI attributes, including 'selected_color' and 'match_filter_threshold'.
        """
        if 'selected_color' in options:
            selected_color = literal_eval(options['selected_color'])
            self.selectedColor = QColor(selected_color[0], selected_color[1], selected_color[2])
            self.viewRangeButton.show()
        if 'match_filter_threshold' in options:
            self.thresholdValueLabel.setText(str(options['match_filter_threshold']))
            self.thresholdSlider.setProperty("value", int(float(options['match_filter_threshold']) * 10))
