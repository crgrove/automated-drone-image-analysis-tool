from PyQt5.QtWidgets import QDialog

from core.views.components.Preferences_ui import Ui_Preferences
from core.services.SettingsService import SettingsService

class Preferences(QDialog, Ui_Preferences):
	"""Controller for the Preferences dialog box"""
	def __init__(self, parent):
		"""
		__init__ constructor to build the preferences dialog
		
		:MainWindow parent: the parent window for the dialog
		"""
		QDialog.__init__(self)
		self.parent = parent
		self.setupUi(self)
		self.maxAOIsSpinBox.setValue(self.parent.settings_service.getSetting('MaxAOIs'))
		self.themeComboBox.setCurrentText(self.parent.settings_service.getSetting('Theme'))
		self.maxAOIsSpinBox.valueChanged.connect(self.updateMaxAOIs)
		self.themeComboBox.currentTextChanged.connect(self.updateTheme)
	
	def updateMaxAOIs(self):
		"""
		updateMaxAOIs action method triggered on changes to the max areas of interest spinbox
		"""
		self.parent.settings_service.setSetting('MaxAOIs', self.maxAOIsSpinBox.value())
	def updateTheme(self):
		"""
		updateTheme action method triggered on changes to theme combobox
		"""
		self.parent.settings_service.setSetting('Theme', self.themeComboBox.currentText())
		self.parent.updateTheme(self.themeComboBox.currentText())