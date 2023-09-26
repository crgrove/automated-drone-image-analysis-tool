from PyQt5.QtGui import QFontDatabase, QFont, QIcon, QColor, QImage, QPainterPath
from PyQt5.QtCore import Qt, QFile, QTextStream, QTranslator, QLocale, QThread, pyqtSlot, QRect, QSize
from PyQt5.QtWidgets import QDialog

from core.views.components.Preferences_ui import Ui_Preferences
from core.services.SettingsService import SettingsService

class Preferences(QDialog, Ui_Preferences):
	def __init__(self, parent=None):
		QDialog.__init__(self)
		self.parent = parent
		self.setupUi(self)
		self.maxAOIsSpinBox.setValue(self.parent.settings_service.getSetting('MaxAOIs'))
		self.themeComboBox.setCurrentText(self.parent.settings_service.getSetting('Theme'))
		self.maxAOIsSpinBox.valueChanged.connect(self.updateMaxAOIs)
		self.themeComboBox.currentTextChanged.connect(self.updateTheme)
	
	def updateMaxAOIs(self):
		self.parent.settings_service.setSetting('MaxAOIs', self.maxAOIsSpinBox.value())
	def updateTheme(self):
		self.parent.settings_service.setSetting('Theme', self.themeComboBox.currentText())
		self.parent.updateTheme(self.themeComboBox.currentText())