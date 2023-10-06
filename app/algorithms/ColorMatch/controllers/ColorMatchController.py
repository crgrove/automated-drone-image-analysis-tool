import logging

from ast import literal_eval

from algorithms.Algorithm import AlgorithmController
from algorithms.ColorMatch.views.ColorMatch_ui import Ui_ColorMatch
from algorithms.ColorMatch.controllers.ColorMatchRangeViewerController import ColorMatchRangeViewer

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QColorDialog

from helpers.ColorUtils import ColorUtils

class ColorMatch(QWidget, Ui_ColorMatch, AlgorithmController):
	"""Controller for the Color Match algorithm widget"""

	def __init__(self):
		"""
		__init__ constructor for the widget
		"""
		QWidget.__init__(self)
		AlgorithmController.__init__(self, 'ColorMatch', 20)
		self.setupUi(self)
		self.selectedColor = None
		self.viewRangeButton.hide()
		self.colorButton.clicked.connect(self.colorButtonClicked)
		self.viewRangeButton.clicked.connect(self.viewRangeButtonClicked)

		self.rRangeSpinBox.valueChanged.connect(self.updateColors)
		self.gRangeSpinBox.valueChanged.connect(self.updateColors)
		self.bRangeSpinBox.valueChanged.connect(self.updateColors)

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
			
	def viewRangeButtonClicked(self):
		"""
		viewRangeButtonClicked click handler for the view range button
		Opens the View Range dialog
		"""
		rangeDialog = ColorMatchRangeViewer(self.lowerColor, self.upperColor)
		rangeDialog.exec()
		
	def updateColors(self):
		"""
		updateColors gets the min and max rgb colors relative to the base color and updates the colors of the color range boxes
		"""
		if self.selectedColor is not None:
			rgb = [self.selectedColor.red(),self.selectedColor.green(),self.selectedColor.blue()]
			self.lowerColor, self.upperColor = ColorUtils.getColorRange(rgb, self.rRangeSpinBox.value(), self.gRangeSpinBox.value(), self.bRangeSpinBox.value())
			#Convert the RGB tuples to hex for CSS
			hex_lower = '#%02x%02x%02x' % self.lowerColor
			hex_upper = '#%02x%02x%02x' % self.upperColor
			self.minColor.setStyleSheet("background-color: "+hex_lower)
			self.midColor.setStyleSheet("background-color: "+self.selectedColor.name())
			self.maxColor.setStyleSheet("background-color: "+hex_upper)
			self.viewRangeButton.show()

	def getOptions(self):
		"""
		getOptions populates options based on user-selected values
		
		:return Dictionary: the option names and values
		"""
		options = dict()
		options['color_range'] = [self.lowerColor, self.upperColor]
		options['selected_color'] = (self.selectedColor.red(),self.selectedColor.green(),self.selectedColor.blue())
		options['range_values']=(self.rRangeSpinBox.value(), self.gRangeSpinBox.value(), self.bRangeSpinBox.value())
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
		if 'range_values' in options and 'selected_color' in options:
			ranges = literal_eval(options['range_values'])
			self.rRangeSpinBox.setValue(ranges[0])
			self.gRangeSpinBox.setValue(ranges[1])
			self.bRangeSpinBox.setValue(ranges[2])
			selected_color = literal_eval(options['selected_color'])
			self.selectedColor = QColor(selected_color[0],selected_color[1],selected_color[2])
			self.updateColors()