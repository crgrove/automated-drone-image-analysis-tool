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
		self.thresholdSlider.valueChanged.connect(self.updateThreshold)

	def getOptions(self):
		"""
		getOptions populates options based on user-selected values
		
		:return Dictionary: the option names and values
		"""
		options = dict()
		options['threshold'] = float(self.thresholdValueLabel.text())
		return options

	def updateThreshold(self):
		"""
		updateThreshold click handler for the threshold slider
		"""
		if self.thresholdSlider.value() == 0:
			self.thresholdValueLabel.setText('0')
		elif self.thresholdSlider.value() == 1000:
			self.thresholdValueLabel.setText('1')   
		else:
			self.thresholdValueLabel.setText("."+str(self.thresholdSlider.value()))
	
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
		if 'threshold' in options:
			self.thresholdValueLabel.setText(str(options['threshold']))
			self.thresholdSlider.setProperty("value", int(float(options['threshold'])*1000))