import logging
from ast import literal_eval

from algorithms.Algorithm import AlgorithmController
from algorithms.MatchedFilter.views.MatchedFilter_ui import Ui_MatchedFilter

from PyQt5.QtGui import  QColor
from PyQt5.QtWidgets import QWidget, QColorDialog

class MatchedFilter(QWidget, Ui_MatchedFilter, AlgorithmController):
    """Controller for the Matched Filter algorithm widget"""

    def __init__(self):
        """
		__init__ constructor for the widget
		"""
        QWidget.__init__(self)
        AlgorithmController.__init__(self, 'MatchedFilter', 10)
        self.setupUi(self)
        self.selectedColor = None
        self.thresholdSlider.valueChanged.connect(self.updateThreshold)
        self.colorButton.clicked.connect(self.colorButtonClicked)

    def colorButtonClicked(self):
        """
		colorButtonClicked click handler for the base color selector
		Opens a color picker dialog
		"""
        try:
            if self.selectedColor is not None:
                    self.selectedColor = QColorDialog().getColor(self.selectedColor)
            else:
                    self.selectedColor = QColorDialog().getColor()
            if self.selectedColor.isValid():
                self.updateColors();
        except Exception as e:
            logging.exception(e)

    def updateColors(self):
        """
		updateColors updates the color of the selected color box
		"""
        if self.selectedColor is not None:
            self.colorSample.setStyleSheet("background-color: "+self.selectedColor.name())
    
    def updateThreshold(self):
        """
		updateThreshold click handler for the threshold slider
		"""
        if self.thresholdSlider.value() == .1:
            self.thresholdValueLabel.setText('.1')
        elif self.thresholdSlider.value() == 10:
            self.thresholdValueLabel.setText('1')   
        else:
            self.thresholdValueLabel.setText("."+str(self.thresholdSlider.value()))
    
    def getOptions(self):
        """
		getOptions populates options based on user-selected values
		
		:return Dictionary: the option names and values
		"""
        options = dict()
        options['selected_color'] = (self.selectedColor.red(),self.selectedColor.green(),self.selectedColor.blue())
        options['match_filter_threshold'] = float(self.thresholdValueLabel.text())
        return options

    def validate(self):
        """
		validate validates that the required values have been provided
		
		:return String: error message
		"""
        if self.selectedColor is None:
            return "Please select a search color."
        return None;

    def loadOptions(self, options):
        """
		loadOptions sets UI elements based on options
		
		:Dictionary options: the options to use to set attributes
		"""
        if 'selected_color' in options:
            selected_color = literal_eval(options['selected_color'])
            self.selectedColor = QColor(selected_color[0],selected_color[1],selected_color[2])
        if 'match_filter_threshold' in options:
            self.thresholdValueLabel.setText(str(options['match_filter_threshold']))
            self.thresholdSlider.setProperty("value", int(float(options['threshold'])*10))