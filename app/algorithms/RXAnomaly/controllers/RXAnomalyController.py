from algorithms.Algorithm import AlgorithmController
from algorithms.RXAnomaly.views.RXAnomaly_ui import Ui_RXAnomaly

from PyQt5.QtWidgets import QWidget

class RXAnomaly(QWidget, Ui_RXAnomaly, AlgorithmController):
	"""Controller for the RX Anomaly algorithm widget"""

	def __init__(self):
		"""
		__init__ constructor for the widget
		"""
		QWidget.__init__(self)
		AlgorithmController.__init__(self, 'RXAnomaly', 10)
		self.setupUi(self)
		self.sensitivitySlider.valueChanged.connect(self.updateSensitivity)

	def getOptions(self):
		"""
		getOptions populates options based on user-selected values
		
		:return Dictionary: the option names and values
		"""
		options = dict()
		options['sensitivity'] = int(self.sensitivityValueLabel.text())
		options['segments'] = int(self.segmentsComboBox.currentText())
		return options

	def updateSensitivity(self):
		"""
		updateSensitivity click handler for the sensitivity slider
		"""
		self.sensitivityValueLabel.setText(str(self.sensitivitySlider.value()))
	
	def validate(self):
		"""
		validate validates that the required values have been provided
		
		:return String: error message
		"""
		return None;

	def loadOptions(self, options):
		"""
		loadOptions sets UI elements based on options
		
		:Dictionary options: the options to use to set attributes
		"""
		if 'sensitivity' in options:
			self.sensitivityValueLabel.setText(str(options['sensitivity']))
			self.sensitivityValueLabel.setText(str(options['sensitivity']))
			self.sensitivitySlider.setProperty("value", int(options['sensitivity']))
		if 'segment' in options:
			self.segmentsComboBox.setCurrentText(str(options['segment']))