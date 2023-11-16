from PyQt5 import QtCore
class SettingsService:
	"""Provides the ability to get and set persistent settings"""

	def __init__(self):
		"""
		__init__ constructor for the settings service
		"""
		self.settings = QtCore.QSettings('ADIAT')
		
	def setSetting(self, name, value):
		"""
		setSetting sets a given setting in QSettings
		
		:String name: the name of the setting
		:String value: the value of the setting
		"""
		self.settings.setValue(name, value)
	
	def getSetting(self,name):
		"""
		getSetting retrieves a given setting from QSettings
		
		:String name: the name of the setting
		:return String: the value of the setting
		"""
		return self.settings.value(name)