import logging

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QFontDatabase, QFont, QIcon, QColor
from PyQt5.QtCore import QFile, QTextStream, QTranslator, QLocale, QThread, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QColorDialog, QFileDialog, QMessageBox

from ..views.MainWindow_ui import Ui_MainWindow

from ..helpers.ColorUtils import ColorUtils
from ..helpers.XmlLoader import XmlLoader

from .Viewer import Viewer
from ..algorithms.process.analyze import Analyze

"""****Import Algorithms****"""
from ..algorithms.controllers.ColorMatch import ColorMatch
from ..algorithms.controllers.ColorAnomaly import ColorAnomaly
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
        #Adding slots for GUI elements
        self.identifierColorButton.clicked.connect(self.identifierButtonClicked)
        self.inputFolderButton.clicked.connect(self.inputFolderButtonClicked)
        self.outputFolderButton.clicked.connect(self.outputFolderButtonClicked)
        self.startButton.clicked.connect(self.startButtonClicked)
        self.viewResultsButton.clicked.connect(self.viewResultsButtonClicked)
        self.actionLoadFile.triggered.connect(self.loadFile)
        self.algorithmComboBox.currentTextChanged.connect(self.algorithmComboBoxChanged)
        self.algorithmComboBoxChanged()


    def identifierButtonClicked(self):
        currentColor = QColor(self.identifierColor[0],self.identifierColor[1],self.identifierColor[2])
        color = QColorDialog().getColor()
        if color.isValid():
            self.identifierColor = (color.red(),color.green(),color.blue())
            self.identifierColorButton.setStyleSheet("background-color: "+color.name()+";")

    def inputFolderButtonClicked(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory != "":
            self.inputFolderLine.setText(directory)

    def outputFolderButtonClicked(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory != "":
            self.outputFolderLine.setText(directory)

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
            self.startButton.setEnabled(False);
            self.addLogEntry("--- Starting image processing ---")

            options = self.algorithmWidget.getOptions()

            #Create instance of the analysis class with the selected algoritm (only ColorMatch for now)
            analyze = Analyze(1,str(self.algorithmComboBox.currentText()), self.inputFolderLine.text(),self.outputFolderLine.text(), self.identifierColor, self.minAreaSpinBox.value(), self.maxThreadsSpinBox.value(), options)

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

    def viewResultsButtonClicked(self):
        self.viewer = Viewer(self.outputFolderLine.text()+"/ADIAT_Results/", self.images)
        self.viewer.show()          

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
