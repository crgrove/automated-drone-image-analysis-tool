import logging
import imghdr
import pathlib

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QFontDatabase, QFont, QIcon, QColor
from PyQt5.QtCore import QFile, QTextStream, QTranslator, QLocale, QThread, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QColorDialog, QFileDialog, QMessageBox

from views.MainWindow_ui import Ui_MainWindow

from helpers.ColorUtils import ColorUtils
from helpers.XmlLoader import XmlLoader

from  controllers.Viewer import Viewer
from services.AnalyzeService import AnalyzeService
from services.SettingsService import SettingsService


"""****Import Algorithms****"""
from algorithms import *
#from algorithms.ColorMatch.controllers.ColorMatchController import ColorMatch
#from algorithms.ColorAnomaly.controllers.ColorAnomalyController import ColorAnomaly
"""****End Algorithm Import****"""

class MainWindow(QMainWindow, Ui_MainWindow):
	"""Main Window."""

	def __init__(self):
		QMainWindow.__init__(self)
		self.setupUi(self)
		self.__threads = [] 
		self.images = None
		self.algorithmWidget = None
		self.identifierColor= (0,255,0)
		self.HistogramImgWidget.setVisible(False)
		#Adding slots for GUI elements
		self.identifierColorButton.clicked.connect(self.identifierButtonClicked)
		self.inputFolderButton.clicked.connect(self.inputFolderButtonClicked)
		self.outputFolderButton.clicked.connect(self.outputFolderButtonClicked)
		self.startButton.clicked.connect(self.startButtonClicked)
		self.viewResultsButton.clicked.connect(self.viewResultsButtonClicked)
		self.actionLoadFile.triggered.connect(self.loadFile)
		self.algorithmComboBox.currentTextChanged.connect(self.algorithmComboBoxChanged)
		self.algorithmComboBoxChanged()
		
		self.HistogramCheckbox.stateChanged.connect(self.histogramCheckboxChange)
		self.HistogramButton.clicked.connect(self.histogramButtonClicked)
		
		self.inputFolderLine.setReadOnly(True)
		self.outputFolderLine.setReadOnly(True)
		self.HistogramLine.setReadOnly(True)
		
		self.settingsService  = SettingsService();

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
			dir = self.settingsService.getSetting('InputFolder')
		if not isinstance(dir, str):
			dir = ""
		directory = QFileDialog.getExistingDirectory(self, "Select Directory",dir, QFileDialog.ShowDirsOnly)
		if directory != "":
			self.inputFolderLine.setText(directory)
			path = pathlib.Path(directory)
			self.settingsService.setSetting('InputFolder', path.parent.__str__())

	def outputFolderButtonClicked(self):
		if self.outputFolderLine.text() != "":
			dir = self.outputFolderLine.text()
		else:
			dir = self.settingsService.getSetting('OutputFolder')
		if not isinstance(dir, str):
			dir = ""
		directory = QFileDialog.getExistingDirectory(self, "Select Directory",dir, QFileDialog.ShowDirsOnly)
		if directory != "":
			self.outputFolderLine.setText(directory)
			path = pathlib.Path(directory)

			self.settingsService.setSetting('OutputFolder', path.parent.__str__())

	def histogramButtonClicked(self):
		if self.inputFolderLine.text() != "":
			dir = self.inputFolderLine.text()
		else:
			dir = self.settingsService.getSetting('InputFolder')
		filename, ok = QFileDialog.getOpenFileName(self,"Select a Reference Image", dir, "Images (*.png *.jpg)")
		if filename:
			self.HistogramLine.setText(filename)
			
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
			self.startButton.setEnabled(False)
			self.viewResultsButton.setEnabled(False)
			self.addLogEntry("--- Starting image processing ---")

			options = self.algorithmWidget.getOptions()

			hist_ref_path = None
			if self.HistogramCheckbox.isChecked() and self.HistogramLine.text() != "":
				hist_ref_path = self.HistogramLine.text()
			#Create instance of the analysis class with the selected algoritm (only ColorMatch for now)
			analyze = AnalyzeService(1,str(self.algorithmComboBox.currentText()), self.inputFolderLine.text(),self.outputFolderLine.text(), self.identifierColor, self.minAreaSpinBox.value(), self.maxThreadsSpinBox.value(), hist_ref_path, options)

			#This must be done in a seperate thread so that it won't block the GUI updates to the log
			thread = QThread()
			self.__threads.append((thread, analyze))
			analyze.moveToThread(thread)

			#Connecting the slots messages back from the analysis thread
			analyze.sig_msg.connect(self.onWorkerMsg)
			analyze.sig_done.connect(self.onWorkerDone)

			thread.started.connect(analyze.processFiles)
			thread.start()
		except Exception as e:
			logging.exception(e)

	def algorithmComboBoxChanged(self):
		if self.algorithmWidget is not None:
			self.verticalLayout_2.removeWidget(self.algorithmWidget);
			self.algorithmWidget.deleteLater()    
		self.algorithmName = str(self.algorithmComboBox.currentText())
		cls = globals()[self.algorithmName]
		self.algorithmWidget = cls()
		self.verticalLayout_2.addWidget(self.algorithmWidget)
		#if self.algorithmName == "ColorAnomaly":
		#	self.maxThreadsSpinBox.setProperty("value", 1)
		#	self.maxThreadsSpinBox.setEnabled(False)
		#else:
		#	self.maxThreadsSpinBox.setEnabled(True)
	def viewResultsButtonClicked(self):
		self.viewer = Viewer(self.outputFolderLine.text()+"/ADIAT_Results/", self.images)
		self.viewer.show()          

	def histogramCheckboxChange(self):
		if self.HistogramCheckbox.isChecked():
			self.HistogramImgWidget.setVisible(True)
		else:
			self.HistogramImgWidget.setVisible(False)
		
	def showError(self, text):
		msg = QMessageBox()
		msg.setIcon(QMessageBox.Critical)
		msg.setText(text)
		msg.setWindowTitle("Error Starting Processing")
		msg.setStandardButtons(QMessageBox.Ok)
		msg.exec_()

	def addLogEntry(self, text):
		self.outputWindow.appendPlainText(text);
	
	@pyqtSlot(str)
	def onWorkerMsg(self, text):
		self.addLogEntry(text)

	@pyqtSlot(int, int)
	def onWorkerDone(self, id, aois):
		self.addLogEntry("--- Image processing completed ---")
		if aois > 0:
			self.addLogEntry(str(aois) +" Images with areas of interest identified")
			self.viewResultsButton.setStyleSheet("background-color: rgb(0, 0, 255);\n""color: rgb(255, 255, 255);")
			self.viewResultsButton.setEnabled(True);
		else:
			self.addLogEntry("No areas of interest identified")
			self.viewResultsButton.setStyleSheet("")
			self.viewResultsButton.setEnabled(False)
		self.startButton.setEnabled(True)

		for thread, analyze in self.__threads:
			thread.quit()

	def loadFile(self):
		try:
			file = QFileDialog.getOpenFileName(self, "Select File")
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
				if 'num_threads' in settings:
					self.maxThreadsSpinBox.setValue(settings['num_threads'])
				if 'min_area' in settings:
					self.minAreaSpinBox.setValue(int(settings['min_area']))
				if 'algorithm' in settings:
					self.algorithm = settings['algorithm']
					self.algorithmComboBoxChanged();
					self.algorithmWidget.loadOptions(settings['options'])

				if len(images):
					self.viewResultsButton.setStyleSheet("background-color: rgb(0, 0, 255);\n""color: rgb(255, 255, 255);")
					self.viewResultsButton.setEnabled(True)
					self.images = images
				else:
					self.viewResultsButton.setStyleSheet("")
					self.viewResultsButton.setEnabled(False)
		except Exception as e:
			logging.exception(e)
	def closeEvent(self, event):
		for window in QApplication.topLevelWidgets():
			window.close()