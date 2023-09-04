from PyQt5 import QtCore
class SettingsService:

	def __init__(self):
		self.settings = QtCore.QSettings('ADIAT')
		
	def setSetting(self, name, value):
		self.settings.setValue(name, value)
	
	def getSetting(self,name):
		return self.settings.value(name)