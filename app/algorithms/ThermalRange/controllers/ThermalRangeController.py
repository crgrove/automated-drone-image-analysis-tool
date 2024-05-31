from algorithms.Algorithm import AlgorithmController
from algorithms.ThermalRange.views.ThermalRange_ui import Ui_ThermalRange
from core.services.SettingsService import SettingsService

from PyQt5.QtWidgets import QWidget

class ThermalRangeController(QWidget, Ui_ThermalRange, AlgorithmController):
	"""Controller for the Thermal Range algorithm widget"""

	def __init__(self):
		"""
		__init__ constructor for the widget
		"""
		QWidget.__init__(self)
		AlgorithmController.__init__(self, 'ThermalRange', 10, True)
		self.settings_service  = SettingsService()
		self.setupUi(self)
		if self.settings_service.getSetting('TemperatureUnit') == 'Fahrenheit':
			self.convertTemperatureRanges()
		self.minTempSpinBox.editingFinished.connect(self.updateMinTemp)
		self.maxTempSpinBox.editingFinished.connect(self.updateMaxTemp)

	def getOptions(self):
		"""
		getOptions populates options based on user-selected values
		
		:return Dictionary: the option names and values
		"""
		options = dict()
		if self.settings_service.getSetting('TemperatureUnit') == 'Fahrenheit':
			options['minTemp'] = self.convertFahrenheitToCelsius(int(self.minTempSpinBox.value()))
			options['maxTemp'] = self.convertFahrenheitToCelsius(int(self.maxTempSpinBox.value()))
		else:
			options['minTemp'] = int(self.minTempSpinBox.value())
			options['maxTemp'] = int(self.maxTempSpinBox.value())
			
		options['colorMap'] = self.colorMapComboBox.currentText()
		return options

	def updateMinTemp(self):
		"""
		updateMinTemp change handler for the minTemp slider
		"""
		if self.minTempSpinBox.value() > self.maxTempSpinBox.value():
			self.maxTempSpinBox.setValue(self.minTempSpinBox.value())
	
	def updateMaxTemp(self):
		"""
		updateMaxTemp change handler for the maxTemp slider
		"""
		if self.minTempSpinBox.value() > self.maxTempSpinBox.value():
			self.minTempSpinBox.setValue(self.maxTempSpinBox.value())
			
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
		if self.settings_service.getSetting('TemperatureUnit') == 'Fahrenheit':
			if 'minTemp' in options:
				self.minTempSpinBox.setValue(int(self.convertCelsiusToFahrenheit(float(options['minTemp']))))
			if 'maxTemp' in options:
				self.maxTempSpinBox.setValue(int(self.convertCelsiusToFahrenheit(float(options['maxTemp']))))
		else:
			if 'minTemp' in options:
				self.minTempSpinBox.setValue(int(float(options['minTemp'])))
			if 'maxTemp' in options:
				self.maxTempSpinBox.setValue(int(float(options['maxTemp'])))				
		self.colorMapComboBox.setCurrentText(options['colorMap'])
			
	def convertTemperatureRanges(self):
		"""
		convertTemperatureRanges modifies the temperate range controls to accept Fahrenheit instead of Celsius
		"""
		self.minTempLabel.setText('Minimum Temp ('+u'\N{DEGREE SIGN}'+' F)') 
		self.minTempSpinBox.setMinimum(-20)
		self.minTempSpinBox.setMaximum(120)
		self.minTempSpinBox.setValue(95)
		self.maxTempLabel.setText('Maximum Temp ('+u'\N{DEGREE SIGN}'+' F)') 
		self.maxTempSpinBox.setMinimum(-20)
		self.maxTempSpinBox.setMaximum(200)
		self.maxTempSpinBox.setValue(105)

	def convertFahrenheitToCelsius(self, value):
		"""
		convertFahrenheitToCelsius converts a Fahrenheit value to Celsius
		
		:int value: the value to be converted
		:return float: the converted value
		"""
		return (value - 32)/1.8000
	
	def convertCelsiusToFahrenheit(self, value):
		"""
		convertCelsiusToFahrenheit converts a Celsius value to Fahrenheit
		
		:int value: the value to be converted
		:return float: the converted value
		"""
		return (value * 1.8000)+32