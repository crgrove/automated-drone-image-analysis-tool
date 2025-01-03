from core.views.components.GroupedComboBox import GroupedComboBox
import pathlib
import os
import platform
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import QThread, pyqtSlot, QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QColorDialog, QFileDialog, QMessageBox, QSizePolicy

from core.views.MainWindow_ui import Ui_MainWindow

from helpers.ColorUtils import ColorUtils

from core.controllers.Viewer import Viewer
from core.controllers.Perferences import Preferences
from core.controllers.VideoParser import VideoParser

from core.services.LoggerService import LoggerService
from core.services.AnalyzeService import AnalyzeService
from core.services.SettingsService import SettingsService
from core.services.XmlService import XmlService
from core.services.ConfigService import ConfigService

"""****Import Algorithm Controllers****"""
from algorithms.ColorRange.controllers.ColorRangeController import ColorRangeController
from algorithms.RXAnomaly.controllers.RXAnomalyController import RXAnomalyController
from algorithms.MatchedFilter.controllers.MatchedFilterController import MatchedFilterController
from algorithms.ThermalRange.controllers.ThermalRangeController import ThermalRangeController
from algorithms.ThermalAnomaly.controllers.ThermalAnomalyController import ThermalAnomalyController
"""****End Algorithm Import****"""


class MainWindow(QMainWindow, Ui_MainWindow):
    """Controller for the Main Window (QMainWindow)."""

    def __init__(self, theme, version):
        """
        Initializes the ADIAT Main Window.

        Args:
            theme (qdarktheme): Instance of qdarktheme to toggle light/dark mode.
            version (str): App version to display in the main window title bar.
        """
        self.logger = LoggerService()
        QMainWindow.__init__(self)
        self.theme = theme
        self.setupUi(self)
        self.__threads = []
        self.images = None
        self.algorithmWidget = None
        self.identifierColor = (0, 255, 0)
        self.HistogramImgWidget.setVisible(False)
        self.KMeansWidget.setVisible(False)
        self.setWindowTitle(f"Automated Drone Image Analysis Tool v{version} - Sponsored by TEXSAR")
        self.loadAlgorithms()

        # Setting up GUI element connections
        self.identifierColorButton.clicked.connect(self.identifierButtonClicked)
        self.inputFolderButton.clicked.connect(self.inputFolderButtonClicked)
        self.outputFolderButton.clicked.connect(self.outputFolderButtonClicked)
        self.startButton.clicked.connect(self.startButtonClicked)
        self.cancelButton.clicked.connect(self.cancelButtonClicked)
        self.viewResultsButton.clicked.connect(self.viewResultsButtonClicked)
        self.actionLoadFile.triggered.connect(self.openLoadFile)
        self.actionPreferences.triggered.connect(self.openPreferences)
        self.actionVideoParser.triggered.connect(self.openVideoParser)
        self.algorithmComboBox.currentTextChanged.connect(self.algorithmComboBoxChanged)
        self.algorithmComboBoxChanged()
        self.minAreaSpinBox.valueChanged.connect(self.minAreaSpinBoxChange)
        self.maxAreaSpinBox.valueChanged.connect(self.maxAreaSpinBoxChange)
        self.histogramCheckbox.stateChanged.connect(self.histogramCheckboxChange)
        self.histogramButton.clicked.connect(self.histogramButtonClicked)
        self.kMeansCheckbox.stateChanged.connect(self.kMeansCheckboxChange)

        self.results_path = ''
        self.settings_service = SettingsService()
        self.setDefaults()

        # Store previous valid values
        self._previous_min_area = self.minAreaSpinBox.value()
        self._previous_max_area = self.maxAreaSpinBox.value()

        # Connect spinbox signals
        self.minAreaSpinBox.editingFinished.connect(self.minAreaEditingFinished)
        self.maxAreaSpinBox.editingFinished.connect(self.maxAreaEditingFinished)

    def loadAlgorithms(self):
        """
        Loads and categorizes algorithms for selection in the algorithm combobox.
        """
        system = platform.system()
        configService = ConfigService(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'algorithms.conf'))
        self.algorithms = configService.getAlgorithms()
        algorithm_list = {}
        for algorithm in self.algorithms:
            if system in algorithm['platforms']:
                if algorithm['type'] not in algorithm_list:
                    algorithm_list[algorithm['type']] = []
                algorithm_list[algorithm['type']].append(algorithm['label'])

        self.replaceAlgorithmComboBox()
        for key, algos in algorithm_list.items():
            self.algorithmComboBox.addGroup(key, algos)
        self.algorithmComboBox.setCurrentIndex(1)

    def replaceAlgorithmComboBox(self):
        """
        Replaces the standard combobox with a grouped version to allow algorithm grouping.
        """
        self.tempAlgorithmComboBox.deleteLater()
        self.algorithmComboBox = GroupedComboBox(self.setupFrame)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy.setHeightForWidth(self.algorithmComboBox.sizePolicy().hasHeightForWidth())
        self.algorithmComboBox.setSizePolicy(sizePolicy)
        self.algorithmComboBox.setMinimumSize(QSize(300, 0))
        font = QFont()
        font.setPointSize(10)
        self.algorithmComboBox.setFont(font)
        self.algorithmSelectorlLayout.replaceWidget(self.tempAlgorithmComboBox, self.algorithmComboBox)

    def identifierButtonClicked(self):
        """
        Opens a color selector dialog for setting the object identifier color.
        """
        color = QColorDialog().getColor()
        if color.isValid():
            self.identifierColor = (color.red(), color.green(), color.blue())
            self.identifierColorButton.setStyleSheet("background-color: " + color.name() + ";")

    def inputFolderButtonClicked(self):
        """
        Opens a directory dialog to select an input folder for analysis.
        """
        dir = self.inputFolderLine.text() or self.settings_service.getSetting('InputFolder')
        dir = dir if isinstance(dir, str) else ""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", dir, QFileDialog.ShowDirsOnly)
        if directory:
            self.inputFolderLine.setText(directory)
            self.settings_service.setSetting('InputFolder', pathlib.Path(directory).parent.__str__())

    def outputFolderButtonClicked(self):
        """
        Opens a directory dialog to select an output folder for analysis results.
        """
        dir = self.outputFolderLine.text() or self.settings_service.getSetting('OutputFolder')
        dir = dir if isinstance(dir, str) else ""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", dir, QFileDialog.ShowDirsOnly)
        if directory:
            self.outputFolderLine.setText(directory)
            self.settings_service.setSetting('OutputFolder', pathlib.Path(directory).parent.__str__())

    def histogramButtonClicked(self):
        """
        Opens a file dialog to select a reference image for histogram-based analysis.
        """
        dir = self.inputFolderLine.text() or self.settings_service.getSetting('InputFolder')
        filename, _ = QFileDialog.getOpenFileName(self, "Select a Reference Image", dir, "Images (*.png *.jpg)")
        if filename:
            self.histogramLine.setText(filename)

    def algorithmComboBoxChanged(self):
        """
        Loads the selected algorithm's widget and sets UI elements based on the algorithm's requirements.
        """
        if self.algorithmWidget:
            self.verticalLayout_2.removeWidget(self.algorithmWidget)
            self.algorithmWidget.deleteLater()

        self.activeAlgorithm = next(x for x in self.algorithms if x['label'] == self.algorithmComboBox.currentText())
        cls = globals()[self.activeAlgorithm['controller']]
        self.algorithmWidget = cls()
        self.verticalLayout_2.addWidget(self.algorithmWidget)
        self.AdvancedFeaturesWidget.setVisible(not self.algorithmWidget.is_thermal)

    def histogramCheckboxChange(self):
        """
        Shows or hides the histogram reference image selector based on checkbox state.
        """
        self.HistogramImgWidget.setVisible(self.histogramCheckbox.isChecked())

    def minAreaSpinBoxChange(self):
        """
        Verifies that the min area spinbox value is still smaller than the max spinbox value and, if not, updates the max spinbox value
        """
        if self.minAreaSpinBox.value() >= self.maxAreaSpinBox.value():
            self.maxAreaSpinBox.setValue(self.minAreaSpinBox.value()+1)

    def maxAreaSpinBoxChange(self):
        """
        Verifies that the max area spinbox value is still larger than the min spinbox value and, if not, updates the min spinbox value
        """
        if self.minAreaSpinBox.value() >= self.maxAreaSpinBox.value():
            self.minAreaSpinBox.setValue(self.maxAreaSpinBox.value()-1)

    def kMeansCheckboxChange(self):
        """
        Shows or hides the number of clusters spinbox for kMeans Clustering based on checkbox state.
        """
        self.KMeansWidget.setVisible(self.kMeansCheckbox.isChecked())

    def startButtonClicked(self):
        """
        Starts the image analysis process.
        """
        try:
            alg_validation = self.algorithmWidget.validate()
            if alg_validation:
                self.showError(alg_validation)
                return

            if not (self.inputFolderLine.text() and self.outputFolderLine.text()):
                self.showError("Please set the input and output directories.")
                return

            self.setStartButton(False)
            self.setViewResultsButton(False)
            self.addLogEntry("--- Starting image processing ---")

            options = self.algorithmWidget.getOptions()
            hist_ref_path = self.histogramLine.text() if self.histogramCheckbox.isChecked() else None
            kmeans_clusters = self.clustersSpinBox.value() if self.kMeansCheckbox.isChecked() else None

            self.settings_service.setSetting('MinObjectArea', self.minAreaSpinBox.value())
            self.settings_service.setSetting('MaxObjectArea', self.maxAreaSpinBox.value())
            self.settings_service.setSetting('IdentifierColor', self.identifierColor)
            self.settings_service.setSetting('MaxProcesses', self.maxProcessesSpinBox.value())

            max_aois = self.settings_service.getSetting('MaxAOIs')
            aoi_radius = self.settings_service.getSetting('AOIRadius')

            self.analyzeService = AnalyzeService(
                1, self.activeAlgorithm, self.inputFolderLine.text(), self.outputFolderLine.text(),
                self.identifierColor, self.minAreaSpinBox.value(), self.maxProcessesSpinBox.value(),
                max_aois, aoi_radius, hist_ref_path, kmeans_clusters, self.algorithmWidget.is_thermal, options,
                self.maxAreaSpinBox.value()
            )

            thread = QThread()
            self.__threads.append((thread, self.analyzeService))
            self.analyzeService.moveToThread(thread)

            self.analyzeService.sig_msg.connect(self.onWorkerMsg)
            self.analyzeService.sig_aois.connect(self.showAOIsLimitWarning)
            self.analyzeService.sig_done.connect(self.onWorkerDone)

            thread.started.connect(self.analyzeService.processFiles)
            thread.start()

            self.results_path = self.outputFolderLine.text()
            self.setCancelButton(True)
        except Exception as e:
            self.logger.error(e)

    def cancelButtonClicked(self):
        """
        Cancels the in-progress analysis.
        """
        self.analyzeService.processCancel()
        self.setCancelButton(False)

    def viewResultsButtonClicked(self):
        """
        Launches the image viewer to display analysis results.
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        output_folder = os.path.join(self.results_path, "ADIAT_Results")
        file = pathlib.Path(output_folder, "ADIAT_Data.xml")
        if file.is_file():
            position_format = self.settings_service.getSetting('PositionFormat')
            temperature_unit = self.settings_service.getSetting('TemperatureUnit')
            self.viewer = Viewer(file, position_format, temperature_unit, False)
            self.viewer.show()
        else:
            self.showError("Could not parse XML file. Check file paths in \"ADIAT_Data.xml\"")
        QApplication.restoreOverrideCursor()

    def addLogEntry(self, text):
        """
        Adds a log entry to the output window.

        Args:
            text (str): The text to add to the output window.
        """
        self.outputWindow.appendPlainText(text)

    @pyqtSlot()
    def showAOIsLimitWarning(self):
        """
        Displays a warning that the maximum number of areas of interest has been exceeded.
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText(f"Area of Interest Limit ({self.settings_service.getSetting('MaxAOIs')}) exceeded. Continue?")
        msg.setWindowTitle("Area of Interest Limit Exceeded")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if msg.exec_() == QMessageBox.No:
            self.cancelButtonClicked()

    @pyqtSlot(str)
    def onWorkerMsg(self, text):
        """
        Logs a message from the worker thread.

        Args:
            text (str): The message text.
        """
        self.addLogEntry(text)

    @pyqtSlot(int, int)
    def onWorkerDone(self, id, images_with_aois):
        """
        Finalizes the UI upon completion of the analysis process.

        Args:
            id (int): ID of the calling object.
            images_with_aois (int): Count of images with areas of interest.
        """
        self.addLogEntry("--- Image Processing Completed ---")
        if images_with_aois > 0:
            self.addLogEntry(f"{images_with_aois} images with areas of interest identified")
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
        Displays an error message.

        Args:
            text (str): The error message text.
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle("Error Starting Processing")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def openLoadFile(self):
        """
        Opens a file dialog to select a file to load.
        """
        try:
            file, _ = QFileDialog.getOpenFileName(self, "Select File")
            if file:
                self.processXmlFile(file)
        except Exception as e:
            self.logger.error(e)

    def processXmlFile(self, full_path):
        """
        Processes an XML file selected in the Load File dialog.

        Args:
            full_path (str): Path to the XML file.
        """
        try:
            image_count = self.getSettingsFromXml(full_path)
            if image_count > 0:
                self.setViewResultsButton(True)
            self.AdvancedFeaturesWidget.setVisible(not self.algorithmWidget.is_thermal)
        except Exception as e:
            self.logger.error(e)

    def getSettingsFromXml(self, full_path):
        """
        Populates the UI with data from a previously executed analysis.

        Args:
            full_path (str): Path to the XML file.

        Returns:
            int: Number of images with areas of interest.
        """
        xmlLoader = XmlService(full_path)
        settings, image_count = xmlLoader.getSettings()
        if 'output_dir' in settings:
            self.outputFolderLine.setText(settings['output_dir'])
            self.results_path = settings['output_dir']
        if 'input_dir' in settings:
            self.inputFolderLine.setText(settings['input_dir'])
        if 'identifier_color' in settings:
            self.identifierColor = settings['identifier_color']
            color = QColor(*self.identifierColor)
            self.identifierColorButton.setStyleSheet("background-color: " + color.name() + ";")
        if 'num_processes' in settings:
            self.maxProcessesSpinBox.setValue(settings['num_processes'])
        if 'min_area' in settings:
            self.minAreaSpinBox.setValue(int(settings['min_area']))
        if 'max_area' in settings:
            self.maxAreaSpinBox.setValue(int(settings['max_area']))
        if 'hist_ref_path' in settings:
            self.histogramCheckbox.setChecked(True)
            self.histogramLine.setText(settings['hist_ref_path'])
        if 'kmeans_clusters' in settings:
            self.kMeansCheckbox.setChecked(True)
            self.clustersSpinBox.setValue(settings['kmeans_clusters'])
        if 'algorithm' in settings:
            self.activeAlgorithm = next(x for x in self.algorithms if x['name'] == settings['algorithm'])
            self.algorithmComboBox.setCurrentText(self.activeAlgorithm['label'])
            self.algorithmWidget.loadOptions(settings['options'])
        if 'thermal' in settings:
            self.algorithmWidget.is_thermal = (settings['thermal'] == 'True')
        return image_count

    def openPreferences(self):
        """
        Opens the Preferences dialog.
        """
        pref = Preferences(self)
        pref.exec()

    def openVideoParser(self):
        """
        Opens the Video Parser dialog.
        """
        parser = VideoParser()
        parser.exec_()

    def closeEvent(self, event):
        """
        Closes all top-level windows when the main window is closed.
        """
        for window in QApplication.topLevelWidgets():
            window.close()

    def setStartButton(self, enabled):
        """
        Enables or disables the start button.

        Args:
            enabled (bool): True to enable, False to disable.
        """
        if enabled:
            self.startButton.setStyleSheet("background-color: rgb(0, 136, 0); color: rgb(228, 231, 235);")
            self.startButton.setEnabled(True)
        else:
            self.startButton.setStyleSheet("")
            self.startButton.setEnabled(False)

    def setCancelButton(self, enabled):
        """
        Enables or disables the cancel button.

        Args:
            enabled (bool): True to enable, False to disable.
        """
        if enabled:
            self.cancelButton.setStyleSheet("background-color: rgb(136, 0, 0); color: rgb(228, 231, 235);")
            self.cancelButton.setEnabled(True)
        else:
            self.cancelButton.setStyleSheet("")
            self.cancelButton.setEnabled(False)

    def setViewResultsButton(self, enabled):
        """
        Enables or disables the view results button.

        Args:
            enabled (bool): True to enable, False to disable.
        """
        if enabled:
            self.viewResultsButton.setStyleSheet("background-color: rgb(0, 0, 136); color: rgb(228, 231, 235);")
            self.viewResultsButton.setEnabled(True)
        else:
            self.viewResultsButton.setStyleSheet("")
            self.viewResultsButton.setEnabled(False)

    def setDefaults(self):
        """
        Sets default values for UI elements based on persistent settings and initializes settings if not previously set.
        """
        min_area = self.settings_service.getSetting('MinObjectArea')
        if isinstance(min_area, int):
            self.minAreaSpinBox.setValue(min_area)

        max_area = self.settings_service.getSetting('MaxObjectArea')
        if isinstance(max_area, int):
            self.maxAreaSpinBox.setValue(max_area)

        max_processes = self.settings_service.getSetting('MaxProcesses')
        if isinstance(max_processes, int):
            self.maxProcessesSpinBox.setValue(max_processes)

        id_color = self.settings_service.getSetting('IdentifierColor')
        if isinstance(id_color, tuple):
            self.identifierColor = id_color
            color = QColor(*self.identifierColor)
            self.identifierColorButton.setStyleSheet("background-color: " + color.name() + ";")

        max_aois = self.settings_service.getSetting('MaxAOIs')
        if not isinstance(max_aois, int):
            self.settings_service.setSetting('MaxAOIs', 100)

        aoi_radius = self.settings_service.getSetting('AOIRadius')
        if not isinstance(aoi_radius, int):
            self.settings_service.setSetting('AOIRadius', 15)

        position_format = self.settings_service.getSetting('PositionFormat')
        if not isinstance(position_format, str):
            self.settings_service.setSetting('PositionFormat', 'Lat/Long - Decimal Degrees')

        temperature_unit = self.settings_service.getSetting('TemperatureUnit')
        if not isinstance(temperature_unit, str):
            self.settings_service.setSetting('TemperatureUnit', 'Fahrenheit')

        theme = self.settings_service.getSetting('Theme')
        if theme is None:
            self.settings_service.setSetting('Theme', 'Dark')
            theme = 'Dark'
        self.updateTheme(theme)

    def updateTheme(self, theme):
        """
        Updates the application theme.

        Args:
            theme (str): 'Light' or 'Dark'
        """
        self.theme.setup_theme("light" if theme == 'Light' else "dark")

    def minAreaEditingFinished(self):
        """
        Validates the minimum area value after manual entry is complete.
        """
        new_value = self.minAreaSpinBox.value()
        if new_value >= self.maxAreaSpinBox.value():
            self.minAreaSpinBox.setValue(self._previous_min_area)
            self.showAreaValidationError("The min object area (px) value must be less than the max object area (px) value")
        else:
            self._previous_min_area = new_value

    def maxAreaEditingFinished(self):
        """
        Validates the maximum area value after manual entry is complete.
        """
        new_value = self.maxAreaSpinBox.value()
        if new_value <= self.minAreaSpinBox.value():
            self.maxAreaSpinBox.setValue(self._previous_max_area)
            self.showAreaValidationError("The max object area (px) value must be greater than the min object area (px) value")
        else:
            self._previous_max_area = new_value

    def showAreaValidationError(self, message):
        """
        Displays an error message for area validation.

        Args:
            message (str): The error message to display.
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Invalid Value")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
