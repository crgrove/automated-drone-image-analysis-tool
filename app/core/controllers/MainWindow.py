import logging
import imghdr
import pathlib

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QFile, QThread, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QColorDialog, QFileDialog, QMessageBox, QStyle

from core.views.MainWindow_ui import Ui_MainWindow

from helpers.ColorUtils import ColorUtils

from core.controllers.Viewer import Viewer
from core.controllers.Perferences import Preferences
from core.services.AnalyzeService import AnalyzeService
from core.services.SettingsService import SettingsService
from core.services.XmlService import XmlService

"""****Import Algorithm Controllers****"""
from algorithms.ColorMatch.controllers.ColorMatchController import ColorMatch
from algorithms.RXAnomaly.controllers.RXAnomalyController import RXAnomaly
from algorithms.MatchedFilter.controllers.MatchedFilterController import MatchedFilter
"""****End Algorithm Import****"""

class MainWindow(QMainWindow, Ui_MainWindow):
	"""Controller for the Main Window (QMainWindow)."""
	def __init__(self, theme, version):
		"""
		__init__ constructor to build the ADIAT Main Window
		
		:qdarktheme theme: instance of qdarktheme that allows us to toggle light/dark mode
		:String version: the app version # to be included in the Main Window title bar
		"""
		QMainWindow.__init__(self)
		self.theme = theme
		self.setupUi(self)
		self.__threads = [] 
		self.images = None
		self.algorithmWidget = None
		self.identifierColor= (0,255,0)
		self.HistogramImgWidget.setVisible(False)
		self.KMeansWidget.setVisible(False)
		self.setWindowTitle("Automated Drone Image Analysis Tool  v"+version+" - Sponsored by TEXSAR")
		
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
		
		self.settings_service  = SettingsService()
		self.setDefaults()
		
	def identifierButtonClicked(self):
		"""
		identifierButtonClicked click handler for the object identifier color button
		Opens a color selector dialog
		"""
		currentColor = QColor(self.identifierColor[0],self.identifierColor[1],self.identifierColor[2])
		color = QColorDialog().getColor()
		if color.isValid():
			self.identifierColor = (color.red(),color.green(),color.blue())
			self.identifierColorButton.setStyleSheet("background-color: "+color.name()+";")

	def inputFolderButtonClicked(self):
		"""
		inputFolderButtonClicked click handler for the input folder button
		Opens a file/directory dialog
		"""
		if self.inputFolderLine.text() != "":
			dir = self.inputFolderLine.text()
		else:
			dir = self.settings_service.getSetting('InputFolder')
		if not isinstance(dir, str):
			dir = ""
		directory = QFileDialog.getExistingDirectory(self, "Select Directory",dir, QFileDialog.ShowDirsOnly)
		#if a directory is selected, populate the input folder textbox with the path and update the persistent settings with the latest path.
		if directory != "":
			self.inputFolderLine.setText(directory)
			path = pathlib.Path(directory)
			self.settings_service.setSetting('InputFolder', path.parent.__str__())

	def outputFolderButtonClicked(self):
		"""
		outputFolderButtonClicked click handler for the output folder button
		Opens a file/directory dialog
		"""
		if self.outputFolderLine.text() != "":
			dir = self.outputFolderLine.text()
		else:
			dir = self.settings_service.getSetting('OutputFolder')
		if not isinstance(dir, str):
			dir = ""
		directory = QFileDialog.getExistingDirectory(self, "Select Directory",dir, QFileDialog.ShowDirsOnly)
		
		#if a directory is selected, populate the input folder textbox with the path and update the persistent settings with the latest path.
		if directory != "":
			self.outputFolderLine.setText(directory)
			path = pathlib.Path(directory)
			self.settings_service.setSetting('OutputFolder', path.parent.__str__())

	def histogramButtonClicked(self):
		"""
		histogramButtonClicked click handler for the histogram reference image loaded
		Opens a file dialog
		"""
		#default the directory to the input folder directory if populated.
		if self.inputFolderLine.text() != "":
			dir = self.inputFolderLine.text()
		else:
			dir = self.settings_service.getSetting('InputFolder')
			
		filename, ok = QFileDialog.getOpenFileName(self,"Select a Reference Image", dir, "Images (*.png *.jpg)")
		if filename:
			self.histogramLine.setText(filename)
			
	def algorithmComboBoxChanged(self):
		"""
		algorithmComboBoxChanged action method for updates to the algorithm combobox
		On change loads the QWidget associated with the selected algorithm and sets the max processes spinbox to the default value for the new algorithm
		"""
		if self.algorithmWidget is not None:
			self.verticalLayout_2.removeWidget(self.algorithmWidget);
			self.algorithmWidget.deleteLater()
		
		self.algorithmName = str(self.algorithmComboBox.currentText())
		cls = globals()[self.algorithmName]
		self.algorithmWidget = cls()
		self.verticalLayout_2.addWidget(self.algorithmWidget)
		self.maxProcessesSpinBox.setProperty("value", self.algorithmWidget.default_process_count)       

	def histogramCheckboxChange(self):
		"""
		histogramCheckboxChange action method triggered on changes to the histogram checkbox
		When checked the reference image selector is displayed
		"""
		if self.histogramCheckbox.isChecked():
			self.HistogramImgWidget.setVisible(True)
		else:
			self.HistogramImgWidget.setVisible(False)
	
	def kMeansCheckboxChange(self):
		"""
		kMeansCheckboxChange action method triggered on changes to the kMeans Clustering checkbox
		When checked the number of clusters spinbox is displayed
		"""
		if self.kMeansCheckbox.isChecked():
			self.KMeansWidget.setVisible(True)
		else:
			self.KMeansWidget.setVisible(False)		
			
	def startButtonClicked(self):
		"""
		startButtonClicked click handler for triggering the image analysis process
		"""
		try:
			#ensure the algorithm-specific requirements are met.
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

			#get the algorithm-specific optins
			options = self.algorithmWidget.getOptions()

			hist_ref_path = None
			if self.histogramCheckbox.isChecked() and self.histogramLine.text() != "":
				hist_ref_path = self.histogramLine.text()
			
			kmeans_clusters = None
			if self.kMeansCheckbox.isChecked():
				kmeans_clusters = self.clustersSpinBox.value()
			
			#update the persistent settings for minimum object size and identifier color based on the current settings.
			self.settings_service.setSetting('MinObjectArea', self.minAreaSpinBox.value())
			self.settings_service.setSetting('IdentifierColor', self.identifierColor)
			
			max_aois = self.settings_service.getSetting('MaxAOIs')
			
			#Create instance of the analysis class with the selected algorithm
			self.analyzeService = AnalyzeService(1,str(self.algorithmComboBox.currentText()), self.inputFolderLine.text(),self.outputFolderLine.text(), self.identifierColor, self.minAreaSpinBox.value(), 
			    self.maxProcessesSpinBox.value(), max_aois, hist_ref_path, kmeans_clusters, options)

			#This must be done in a separate thread so that it won't block the GUI updates to the log
			thread = QThread()
			self.__threads.append((thread, self.analyzeService))
			self.analyzeService.moveToThread(thread)

			#Connecting the slots messages back from the analysis thread
			self.analyzeService.sig_msg.connect(self.onWorkerMsg)
			self.analyzeService.sig_aois.connect(self.showAOIsLimitWarning)
			self.analyzeService.sig_done.connect(self.onWorkerDone)

			thread.started.connect(self.analyzeService.processFiles)
			thread.start()
			
			self.last_output_path = self.outputFolderLine.text()
			
			self.setCancelButton(True)
		except Exception as e:
			logging.exception(e)
			
	def cancelButtonClicked(self):
		"""
		cancelButtonClicked click handler that cancelled in progress analysis
		"""
		self.analyzeService.processCancel()
		self.setCancelButton(False)
		
	def viewResultsButtonClicked(self):
		"""
		viewResultsButtonClicked click handler for launching the image viewer once analysis has been completed
		"""
		output_folder = self.outputFolderLine.text()+"/ADIAT_Results/"
		
		xmlLoader = XmlService(output_folder+"ADIAT_Data.xml")
		images = xmlLoader.getImages()		
		if len(images):
			self.setViewResultsButton(True)
			self.images = images
		else:
			self.setViewResultsButton(False)
			
		self.viewer = Viewer(self.images)
		self.viewer.show()   	
		
	def addLogEntry(self, text):
		"""
		addLogEntry adds a new line of text to the output window
		
		:String text: the text to add to the output window
		"""
		self.outputWindow.appendPlainText(text);
	
	@pyqtSlot()
	def showAOIsLimitWarning(self):
		"""
		showAOIsLimitWarning opens a message box showing a warning that the maximum number of areas of interest has been exceed
		Gives the user the options to continue or cancel the current analysis
		"""
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
		"""
		onWorkerMsg calls the addLogEntry method to add a new line to the output window
		
		:String text: the text to add to the output window
		"""
		self.addLogEntry(text)

	@pyqtSlot(int, int)
	def onWorkerDone(self, id, images_with_aois):
		"""
		onWorkerDone  Oncompletion of the analysis process adds a log entry with information specific to the results and updates button states
		
		:Int id: the id of the calling object
		:Int images_with_aois: the number of images that include areas of interest
		"""
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
		"""
		showError open a message box showing an error with the provided text
		
		:String text: the text to be included are the error message
		"""
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Critical)
		msg.setText(text)
		msg.setWindowTitle("Error Starting Processing")
		msg.setStandardButtons(QMessageBox.Ok)
		msg.exec_()
		
	def loadFile(self):
		"""
		loadFile action for the open file menu item
		Opens a file dialog and on close processes the xml file from a previously completed analysis process
		"""
		try:
			file = QFileDialog.getOpenFileName(self, "Select File")
			if file[0] != "":
				image_count = self.getSettingsFromXml(file[0])
				if image_count > 0:
					self.setViewResultsButton(True)

		except Exception as e:
			logging.exception(e)
	
	def getSettingsFromXml(self, full_path):
		"""
		getSettingsFromXml populates the UI with previously executed analysis
		
		:String full_path: the path to the XML file
		:return int: the number of images with areas of interest
		"""
		xmlLoader = XmlService(full_path)
		settings, image_count = xmlLoader.getSettings()	
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
		if 'hist_ref_path' in settings:
			self.histogramCheckbox.setChecked(True)
			self.histogramLine.setText(settings['hist_ref_path'])
		if 'kmeans_clusters' in settings:
			self.kMeansCheckbox.setChecked(True)
			self.clustersSpinBox.setValue(settings['kmeans_clusters'])
		if 'algorithm' in settings:
			self.algorithmComboBox.setCurrentText(settings['algorithm'])
			self.algorithmWidget.loadOptions(settings['options'])
		return image_count
			
	def openPreferences(self):
		"""
		openPreferences action for the preferences menu item
		Opens a dialog showing the application preferences
		"""
		pref = Preferences(self)
		pref.exec()
		
	def closeEvent(self, event):
		"""
		closeEvent closes all windows when the main window is closes.
		"""
		for window in QApplication.topLevelWidgets():
			window.close()
			
	def setStartButton(self, enabled):
		"""
		setStartButton updates the start button based on the enabled parameter
		
		:Boolean enabled: True to enable and False to disable the button
		"""
		if enabled:
			self.startButton.setStyleSheet("background-color: rgb(0, 136, 0);\n""color: rgb(228, 231, 235);")
			self.startButton.setEnabled(True)	
		else:
			self.startButton.setStyleSheet("")
			self.startButton.setEnabled(False)
			
	def setCancelButton(self, enabled):
		"""
		setCancelButton updates the cancel button based on the enabled parameter
		
		:Boolean enabled: True to enable and False to disable the button
		"""
		if enabled:
			self.cancelButton.setStyleSheet("background-color: rgb(136, 0, 0);\n""color: rgb(228, 231, 235);")
			self.cancelButton.setEnabled(True)	
		else:
			self.cancelButton.setStyleSheet("")
			self.cancelButton.setEnabled(False)
			
	def setViewResultsButton(self, enabled):
		"""
		setViewResultsButton updates the view results button based on the enabled parameter
		
		:Boolean enabled: True to enable and False to disable the button
		"""
		if enabled:
			self.viewResultsButton.setStyleSheet("background-color: rgb(0, 0, 136);\n""color: rgb(228, 231, 235);")
			self.viewResultsButton.setEnabled(True)
		else:
			self.viewResultsButton.setStyleSheet("")
			self.viewResultsButton.setEnabled(False)
			
	def setDefaults(self):
		"""
		setDefaults sets UI element default values based on persistent settings and sets default values for persistent settings if not previously set
		"""		
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
		"""
		updateTheme updates the application theme based on the theme parameter
		
		:String theme: Light or Dark
		"""
		if theme == 'Light':
			self.theme.setup_theme("light")
		else:
			self.theme.setup_theme("dark")