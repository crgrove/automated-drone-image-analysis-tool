import logging
import imghdr
import pathlib

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QFile, QTextStream, QTranslator, QLocale, QThread, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QColorDialog, QFileDialog, QMessageBox, QStyle

from core.views.MainWindow_ui import Ui_MainWindow

from helpers.ColorUtils import ColorUtils
from helpers.XmlLoader import XmlLoader

from core.controllers.Viewer import Viewer
from core.controllers.Perferences import Preferences
from core.services.AnalyzeService import AnalyzeService
from core.services.SettingsService import SettingsService

"""****Import Algorithms****"""
from algorithms.ColorMatch.controllers.ColorMatchController import ColorMatch
from algorithms.RXAnomaly.controllers.RXAnomalyController import RXAnomaly
from algorithms.MatchedFilter.controllers.MatchedFilterController import MatchedFilter
"""****End Algorithm Import****"""

class MainWindow(QMainWindow, Ui_MainWindow):
	"""Main Window."""

	def __init__(self, theme):
		QMainWindow.__init__(self)
		self.theme = theme
		self.setupUi(self)
		self.__threads = [] 
		self.images = None
		self.algorithmWidget = None
		self.identifierColor= (0,255,0)
		self.HistogramImgWidget.setVisible(False)
		self.KMeansWidget.setVisible(False)
		
		#Adding slots for GUI elements
		self.identifierColorButton.clicked.connect(self.identifierButtonClicked)
		self.inputFolderButton.clicked.connect(self.inputFolderButtonClicked)
		self.outputFolderButton.clicked.connect(self.outputFolderButtonClicked)
		self.startButton.clicked.connect(self.startButtonClicked)
		self.cancelButton.clicked.connect(self.cancelButtonClicked)
		self.viewResultsButton.clicked.connect(self.viewResultsButtonClicked)
		self.actionLoadFile.triggered.connect(self.loadFile)
		self.actionPreferences.triggered.connect(self.openPreferences)
		self.algorithmComboBox.currentTextChanged.connect(self.algorithmComboBoxChanged)
		self.algorithmComboBoxChanged()
		
		self.histogramCheckbox.stateChanged.connect(self.histogramCheckboxChange)
		self.histogramButton.clicked.connect(self.histogramButtonClicked)
		
		self.kMeansCheckbox.stateChanged.connect(self.kMeansCheckboxChange)		
		self.inputFolderLine.setReadOnly(True)
		self.outputFolderLine.setReadOnly(True)
		self.histogramLine.setReadOnly(True)
		
		self.settings_service  = SettingsService()
		self.setDefaults()
			
	def identifierButtonClicked(self):
		currentColor = QColor(self.identifierColor[0],self.identifierColor[1],self.identifierColor[2])
		color = QColorDialog().getColor()
		if color.isValid():
			self.identifierColor = (color.red(),color.green(),color.blue())
			self.identifierColorButton.setStyleSheet("background-color: "+color.name()+";")

	def inputFolderButtonClicked(self):
		if self.inputFolderLine.text() != "":
			dir = self.inputFolderLine.text()
		else:
			dir = self.settings_service.getSetting('InputFolder')
		if not isinstance(dir, str):
			dir = ""
		directory = QFileDialog.getExistingDirectory(self, "Select Directory",dir, QFileDialog.ShowDirsOnly)
		if directory != "":
			self.inputFolderLine.setText(directory)
			path = pathlib.Path(directory)
			self.settings_service.setSetting('InputFolder', path.parent.__str__())

	def outputFolderButtonClicked(self):
		if self.outputFolderLine.text() != "":
			dir = self.outputFolderLine.text()
		else:
			dir = self.settings_service.getSetting('OutputFolder')
		if not isinstance(dir, str):
			dir = ""
		directory = QFileDialog.getExistingDirectory(self, "Select Directory",dir, QFileDialog.ShowDirsOnly)
		if directory != "":
			self.outputFolderLine.setText(directory)
			path = pathlib.Path(directory)

			self.settings_service.setSetting('OutputFolder', path.parent.__str__())

	def histogramButtonClicked(self):
		if self.inputFolderLine.text() != "":
			dir = self.inputFolderLine.text()
		else:
			dir = self.settings_service.getSetting('InputFolder')
		filename, ok = QFileDialog.getOpenFileName(self,"Select a Reference Image", dir, "Images (*.png *.jpg)")
		if filename:
			self.histogramLine.setText(filename)
			
	def startButtonClicked(self):
		try:
			alg_validation = self.algorithmWidget.validate()
			
			if alg_validation is not None:
				self.showError(alg_validation)
				return;
			#verify that the directories have been set.
			if self.inputFolderLine.text() == "" or self.outputFolderLine == "" :
				self.showError("Please set the input and output directories.")
				return;
			self.setStartButton(False)
			self.setViewResultsButton(False)
			self.addLogEntry("--- Starting image processing ---")

			options = self.algorithmWidget.getOptions()

			hist_ref_path = None
			if self.histogramCheckbox.isChecked() and self.histogramLine.text() != "":
				hist_ref_path = self.histogramLine.text()
			
			kmeans_clusters = None
			if self.kMeansCheckbox.isChecked():
				kmeans_clusters = self.clustersSpinBox.value()
			
			self.settings_service.setSetting('MinObjectArea', self.minAreaSpinBox.value())
			self.settings_service.setSetting('IdentifierColor', self.identifierColor)
			maxAOIs = self.settings_service.getSetting('MaxAOIs')
			#Create instance of the analysis class with the selected algoritm (only ColorMatch for now)
			self.analyzeService = AnalyzeService(1,str(self.algorithmComboBox.currentText()), self.inputFolderLine.text(),self.outputFolderLine.text(), self.identifierColor, self.minAreaSpinBox.value(), 
			    self.maxProcessesSpinBox.value(), maxAOIs, hist_ref_path, kmeans_clusters, options)

			#This must be done in a seperate thread so that it won't block the GUI updates to the log
			thread = QThread()
			self.__threads.append((thread, self.analyzeService))
			self.analyzeService.moveToThread(thread)

			#Connecting the slots messages back from the analysis thread
			self.analyzeService.sig_msg.connect(self.onWorkerMsg)
			self.analyzeService.sig_aois.connect(self.showAOIsLimitWarning)
			self.analyzeService.sig_done.connect(self.onWorkerDone)

			thread.started.connect(self.analyzeService.processFiles)
			thread.start()
			self.setCancelButton(True)
		except Exception as e:
			logging.exception(e)
			
	def cancelButtonClicked(self):
		self.analyzeService.processCancel()
		self.setCancelButton(False)
	
	def algorithmComboBoxChanged(self):
		if self.algorithmWidget is not None:
			self.verticalLayout_2.removeWidget(self.algorithmWidget);
			self.algorithmWidget.deleteLater()
		
		self.algorithmName = str(self.algorithmComboBox.currentText())
		cls = globals()[self.algorithmName]
		self.algorithmWidget = cls()
		self.verticalLayout_2.addWidget(self.algorithmWidget)
		self.maxProcessesSpinBox.setProperty("value", self.algorithmWidget.default_process_count)
		#if self.algorithmName == "ColorAnomaly":
		#	self.maxThreadsSpinBox.setProperty("value", 1)
		#	self.maxThreadsSpinBox.setEnabled(False)
		#else:
		#	self.maxThreadsSpinBox.setEnabled(True)
	def viewResultsButtonClicked(self):
		self.viewer = Viewer(self.outputFolderLine.text()+"/ADIAT_Results/", self.images)
		self.viewer.show()          

	def histogramCheckboxChange(self):
		if self.histogramCheckbox.isChecked():
			self.HistogramImgWidget.setVisible(True)
		else:
			self.HistogramImgWidget.setVisible(False)
	
	def kMeansCheckboxChange(self):
		if self.kMeansCheckbox.isChecked():
			self.KMeansWidget.setVisible(True)
		else:
			self.KMeansWidget.setVisible(False)
		
	def addLogEntry(self, text):
		self.outputWindow.appendPlainText(text);
	
	@pyqtSlot()
	def showAOIsLimitWarning(self):
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Question)
		msg.setText("Area of Interest Limit ("+str(self.settings_service.getSetting('MaxAOIs'))+") exceeded.  Would you like to proceed with the current execution?")
		msg.setWindowTitle("Area of Interest Limit Exceeded")
		msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
		result = msg.exec_()
		if result == QMessageBox.No:
			self.cancelButtonClicked()
	
	@pyqtSlot(str)
	def onWorkerMsg(self, text):
		self.addLogEntry(text)

	@pyqtSlot(int, int)
	def onWorkerDone(self, id, images_with_aois):
		self.addLogEntry("--- Image Processing Completed ---")
		if images_with_aois > 0:
			self.addLogEntry(str(images_with_aois) +" images with areas of interest identified")
			self.setViewResultsButton(True)
		else:
			self.addLogEntry("No areas of interest identified")
			self.setViewResultsButton(False)
		self.setStartButton(True)
		self.setCancelButton(False)

		for thread, analyze in self.__threads:
			thread.quit()
			
	def showError(self, text):
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Critical)
		msg.setText(text)
		msg.setWindowTitle("Error Starting Processing")
		msg.setStandardButtons(QMessageBox.Ok)
		msg.exec_()
		
	def loadFile(self):
		try:
			file = QFileDialog.getOpenFileName(self, "Select File", "C:\\Users\\charl\\Pictures\\drone\\2023_08_30\\150ft\\output\\ADIAT_Results")
			if file[0] != "":
				xmlLoader = XmlLoader(file[0])
				settings, images = xmlLoader.parseFile()
				if 'output_dir' in settings:
					self.outputFolderLine.setText(settings['output_dir'])
				if 'input_dir' in settings:
					self.inputFolderLine.setText(settings['input_dir'])
				if 'identifier_color' in settings:
					self.identifierColor = settings['identifier_color']
					color = QColor(self.identifierColor[0],self.identifierColor[1],self.identifierColor[2])
					self.identifierColorButton.setStyleSheet("background-color: "+color.name()+";")
				if 'num_processes' in settings:
					self.maxProcessesSpinBox.setValue(settings['num_processes'])
				if 'min_area' in settings:
					self.minAreaSpinBox.setValue(int(settings['min_area']))
				if 'algorithm' in settings:
					self.algorithmComboBox.setCurrentText(settings['algorithm'])
					self.algorithmWidget.loadOptions(settings['options'])

				if len(images):
					self.setViewResultsButton(True)
					self.images = images
				else:
					self.setViewResultsButton(False)
		except Exception as e:
			logging.exception(e)
	
	def openPreferences(self):
		pref = Preferences(self)
		pref.exec()
		
	def closeEvent(self, event):
		for window in QApplication.topLevelWidgets():
			window.close()
			
	def setStartButton(self, enabled):
		if enabled:
			self.startButton.setStyleSheet("background-color: rgb(0, 136, 0);\n""color: rgb(228, 231, 235);")
			self.startButton.setEnabled(True)	
		else:
			self.startButton.setStyleSheet("")
			self.startButton.setEnabled(False)
			
	def setCancelButton(self, enabled):
		if enabled:
			self.cancelButton.setStyleSheet("background-color: rgb(136, 0, 0);\n""color: rgb(228, 231, 235);")
			self.cancelButton.setEnabled(True)	
		else:
			self.cancelButton.setStyleSheet("")
			self.cancelButton.setEnabled(False)
			
	def setViewResultsButton(self, enabled):
		if enabled:
			self.viewResultsButton.setStyleSheet("background-color: rgb(0, 0, 136);\n""color: rgb(228, 231, 235);")
			self.viewResultsButton.setEnabled(True)
		else:
			self.viewResultsButton.setStyleSheet("")
			self.viewResultsButton.setEnabled(False)
			
	def setDefaults(self):
		minArea = self.settings_service.getSetting('MinObjectArea')
		if isinstance(minArea, int):
			self.minAreaSpinBox.setProperty("value", minArea)
			
		idColor = self.settings_service.getSetting('IdentifierColor')
		if isinstance(idColor, tuple):
			self.identifierColor = idColor
			color = QColor(self.identifierColor[0],self.identifierColor[1],self.identifierColor[2])
			self.identifierColorButton.setStyleSheet("background-color: "+color.name()+";")
			
		maxAOIs = self.settings_service.getSetting('MaxAOIs')
		if not isinstance(maxAOIs, int):
			self.settings_service.setSetting('MaxAOIs', 100)
			
		theme = self.settings_service.getSetting('Theme')
		if theme == None:
			self.settings_service.setSetting('Theme', 'Dark')
			theme = 'Dark'
		self.updateTheme(theme)
		
	def updateTheme(self, theme):
		if theme == 'Light':
			self.theme.setup_theme("light")
		else:
			self.theme.setup_theme("dark")