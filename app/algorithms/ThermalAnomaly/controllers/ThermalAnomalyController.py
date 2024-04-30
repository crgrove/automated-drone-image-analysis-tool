from algorithms.Algorithm import AlgorithmController
from algorithms.ThermalAnomaly.views.ThermalAnomaly_ui import Ui_ThermalAnomaly
from core.services.SettingsService import SettingsService

from PyQt5.QtWidgets import QWidget

class ThermalAnomalyController(QWidget, Ui_ThermalAnomaly, AlgorithmController):
	"""Controller for the Thermal Anomaly algorithm widget"""

	def __init__(self):
		"""
		__init__ constructor for the widget
		"""
		QWidget.__init__(self)
		AlgorithmController.__init__(self, 'ThermalAnomaly', 10, True)
		self.settings_service  = SettingsService()
		self.setupUi(self)
		self.anomalySlider.valueChanged.connect(self.updateThreshold)

	def getOptions(self):
		"""
		getOptions populates options based on user-selected values
		
		:return Dictionary: the option names and values
		"""
		options = dict()
		options['threshold'] = int(self.anomalyThresholdLabel.text())
		options['type'] = self.anomalyTypeComboBox.currentText()
		options['colorMap'] = self.colorMapComboBox.currentText()
		return options
	
	def updateThreshold(self):
		"""
		updateThreshold click handler for the sensitivity slider
		"""
		self.anomalyThresholdLabel.setText(str(self.anomalySlider.value()))
			
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
			self.anomalyThresholdLabel.setText(str(options['threshold']))
			self.anomalySlider.setProperty("value", int(options['sensitivity']))	
		self.anomalyTypeComboBox.setCurrentText(options['type'])
		self.colorMapComboBox.setCurrentText(options['colorMap'])