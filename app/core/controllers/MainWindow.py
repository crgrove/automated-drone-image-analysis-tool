# Set environment variable to avoid numpy._core issues - MUST be first
import os
os.environ['NUMPY_EXPERIMENTAL_DTYPE_API'] = '0'

from core.views.components.GroupedComboBox import GroupedComboBox
import pathlib
import platform
import qtawesome as qta
from PySide6.QtGui import QColor, QFont, QIcon, QDesktopServices
from PySide6.QtCore import QThread, Slot, QSize, Qt, QUrl
from PySide6.QtWidgets import (QApplication, QMainWindow, QColorDialog, QFileDialog,
                               QMessageBox, QSizePolicy, QAbstractButton)
from core.views.MainWindow_ui import Ui_MainWindow

from helpers.PickleHelper import PickleHelper

from core.controllers.viewer.Viewer import Viewer
from core.controllers.Perferences import Preferences
from core.controllers.VideoParser import VideoParser
from core.controllers.RTMPColorDetectionViewer import RTMPColorDetectionViewer
from core.controllers.RTMPMotionDetectionViewer import RTMPMotionDetectionViewer
from core.controllers.IntegratedDetectionViewer import IntegratedDetectionViewer

from core.services.LoggerService import LoggerService
from core.services.AnalyzeService import AnalyzeService
from core.services.SettingsService import SettingsService
from core.services.XmlService import XmlService
from core.services.ConfigService import ConfigService

"""****Import Algorithm Controllers****"""
from algorithms.ColorRange.controllers.ColorRangeController import ColorRangeController
from algorithms.RXAnomaly.controllers.RXAnomalyController import RXAnomalyController
from algorithms.MatchedFilter.controllers.MatchedFilterController import MatchedFilterController
from algorithms.MRMap.controllers.MRMapController import MRMapController
from algorithms.AIPersonDetector.controllers.AIPersonDetectorController import AIPersonDetectorController
from algorithms.HSVColorRange.controllers.HSVColorRangeController import HSVColorRangeController
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

        # Set custom tooltip styling - light blue background with black text
        self.setStyleSheet("""
            QToolTip {
                background-color: lightblue;
                color: black;
                border: 1px solid #333333;
                padding: 4px;
                font-size: 11px;
            }
        """)

        self.__threads = []
        self.images = None
        self.algorithmWidget = None
        self.identifierColor = (0, 255, 0)
        self.HistogramImgWidget.setVisible(False)
        self.KMeansWidget.setVisible(False)
        self.setWindowTitle(f"Automated Drone Image Analysis Tool v{version} - Sponsored by TEXSAR")
        self._load_algorithms()

        self.results_path = ''
        self.settings_service = SettingsService()
        self._set_defaults(version)

        # Setting up GUI element connections
        self.identifierColorButton.clicked.connect(self._identifierButton_clicked)
        self.inputFolderButton.clicked.connect(self._inputFolderButton_clicked)
        self.outputFolderButton.clicked.connect(self._outputFolderButton_clicked)
        self.startButton.clicked.connect(self._startButton_clicked)
        self.cancelButton.clicked.connect(self._cancelButton_clicked)
        self.viewResultsButton.clicked.connect(self._viewResultsButton_clicked)
        self.actionLoadFile.triggered.connect(self._open_load_file)
        self.actionPreferences.triggered.connect(self._open_preferences)
        self.actionVideoParser.triggered.connect(self._open_video_parser)

        # Add RTMP Color Detection functionality
        self.rtmp_viewer = None
        if hasattr(self, 'actionRTMPDetection'):
            self.actionRTMPDetection.triggered.connect(self._open_rtmp_detection)

        # Add RTMP Motion Detection functionality
        self.rtmp_motion_viewer = None
        if hasattr(self, 'actionRTMPMotionDetection'):
            self.actionRTMPMotionDetection.triggered.connect(self._open_rtmp_motion_detection)

        # Add Integrated Detection functionality
        self.integrated_viewer = None
        if hasattr(self, 'actionIntegratedDetection'):
            self.actionIntegratedDetection.triggered.connect(self._open_integrated_detection)

        # Add Help menu items
        if hasattr(self, 'actionHelp'):
            self.actionHelp.triggered.connect(self._open_help)
        if hasattr(self, 'actionCommunityHelp'):
            self.actionCommunityHelp.triggered.connect(self._open_community_help)

        self.algorithmComboBox.currentTextChanged.connect(self._algorithmComboBox_changed)
        self._algorithmComboBox_changed()
        # Connect to editingFinished instead of valueChanged for deferred validation
        self.minAreaSpinBox.editingFinished.connect(self._minAreaSpinBox_editingFinished)
        self.maxAreaSpinBox.editingFinished.connect(self._maxAreaSpinBox_editingFinished)
        # Store original values to detect actual changes
        self._minAreaOriginal = self.minAreaSpinBox.value()
        self._maxAreaOriginal = self.maxAreaSpinBox.value()
        self.histogramCheckbox.stateChanged.connect(self._histogramCheckbox_change)
        self.histogramButton.clicked.connect(self._histogramButton_clicked)
        self.kMeansCheckbox.stateChanged.connect(self._kMeansCheckbox_change)

        # Store previous valid values
        self._previous_min_area = self.minAreaSpinBox.value()
        self._previous_max_area = self.maxAreaSpinBox.value()

    def _load_algorithms(self):
        """
        Loads and categorizes algorithms for selection in the algorithm combobox.
        """
        system = platform.system()
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                   'algorithms.conf')
        configService = ConfigService(config_path)
        self.algorithms = configService.get_algorithms()
        algorithm_list = {}
        for algorithm in self.algorithms:
            if system in algorithm['platforms']:
                if algorithm['type'] not in algorithm_list:
                    algorithm_list[algorithm['type']] = []
                algorithm_list[algorithm['type']].append(algorithm['label'])

        self._replace_algorithmComboBox()
        for key, algos in algorithm_list.items():
            self.algorithmComboBox.add_group(key, algos)
        self.algorithmComboBox.setCurrentIndex(1)

    def _replace_algorithmComboBox(self):
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

        # Set comprehensive tooltip for algorithm selection
        self.algorithmComboBox.setToolTip(
            "Select the detection algorithm for your image analysis task:\n"
            "\n"
            "HSV COLOR RANGE: Detects brightly colored objects (clothing, vehicles, tents)\n"
            "  • Best for: Colored objects in varying lighting conditions\n"
            "  • Limitation: Requires color tuning, not for camouflaged objects\n"
            "\n"
            "COLOR RANGE (RGB): Simple RGB color detection, fast processing\n"
            "  • Best for: Basic color detection in controlled lighting\n"
            "  • Limitation: Sensitive to lighting changes\n"
            "\n"
            "RX ANOMALY: Finds objects that don't match background (no sample needed)\n"
            "  • Best for: Camouflaged/hidden subjects, unknown targets\n"
            "  • Limitation: May detect natural anomalies, slower with more segments\n"
            "\n"
            "THERMAL ANOMALY: Detects hot/cold spots in thermal imagery\n"
            "  • Best for: Night searches, detecting people/animals by body heat\n"
            "  • Limitation: Requires thermal camera, may detect sun-heated objects\n"
            "\n"
            "THERMAL RANGE: Temperature-based detection (e.g., 35-40°C for humans)\n"
            "  • Best for: Human detection with thermal camera (known body temp)\n"
            "  • Limitation: Requires thermal camera, must know target temperature\n"
            "\n"
            "MATCHED FILTER: Matches targets using color signature from sample\n"
            "  • Best for: Specific known objects when you have a target sample\n"
            "  • Limitation: Requires reference image, not for unknown targets\n"
            "\n"
            "MR MAP: Multi-resolution detection for objects of varying sizes\n"
            "  • Best for: Complex scenes with unknown target sizes\n"
            "  • Limitation: Slower processing, more false positives\n"
            "\n"
            "AI PERSON DETECTOR: Deep learning model for accurate people detection\n"
            "  • Best for: Search & Rescue, finding people in any clothing/pose\n"
            "  • Limitation: Only detects people, slower processing"
        )

        self.algorithmSelectorlLayout.replaceWidget(self.tempAlgorithmComboBox, self.algorithmComboBox)

    def _identifierButton_clicked(self):
        """
        Opens a color selector dialog for setting the object identifier color.
        """
        color = QColorDialog().getColor()
        if color.isValid():
            self.identifierColor = (color.red(), color.green(), color.blue())
            self.identifierColorButton.setStyleSheet("background-color: " + color.name() + ";")

    def _inputFolderButton_clicked(self):
        """
        Opens a directory dialog to select an input folder for analysis.
        """
        dir = self.inputFolderLine.text() or self.settings_service.get_setting('InputFolder')
        dir = dir if isinstance(dir, str) else ""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", dir, QFileDialog.ShowDirsOnly)
        if directory:
            self.inputFolderLine.setText(directory)
            if os.name == 'nt':
                self.inputFolderLine.setText(directory.replace('/', '\\'))
            self.settings_service.set_setting('InputFolder', pathlib.Path(directory).parent.__str__())

    def _outputFolderButton_clicked(self):
        """
        Opens a directory dialog to select an output folder for analysis results.
        """
        dir = self.outputFolderLine.text() or self.settings_service.get_setting('OutputFolder')
        dir = dir if isinstance(dir, str) else ""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", dir, QFileDialog.ShowDirsOnly)
        if directory:
            self.outputFolderLine.setText(directory)
            if os.name == 'nt':
                self.outputFolderLine.setText(directory.replace('/', '\\'))
            self.settings_service.set_setting('OutputFolder', pathlib.Path(directory).parent.__str__())

    def _histogramButton_clicked(self):
        """
        Opens a file dialog to select a reference image for histogram-based analysis.
        """
        dir = self.inputFolderLine.text() or self.settings_service.get_setting('InputFolder')
        filename, _ = QFileDialog.getOpenFileName(self, "Select a Reference Image", dir, "Images (*.png *.jpg)")
        if filename:
            self.histogramLine.setText(filename)
            if os.name == 'nt':
                self.histogramLine.setText(filename.replace('/', '\\'))

    def _algorithmComboBox_changed(self):
        """
        Loads the selected algorithm's widget and sets UI elements based on the algorithm's requirements.
        """
        if self.algorithmWidget:
            self.verticalLayout_2.removeWidget(self.algorithmWidget)
            self.algorithmWidget.deleteLater()

        self.activeAlgorithm = next(x for x in self.algorithms if x['label'] == self.algorithmComboBox.currentText())
        cls = globals()[self.activeAlgorithm['controller']]
        self.algorithmWidget = cls(self.activeAlgorithm, self.settings_service.get_setting('Theme'))
        self.verticalLayout_2.addWidget(self.algorithmWidget)
        self.AdvancedFeaturesWidget.setVisible(not self.algorithmWidget.is_thermal)

    def _histogramCheckbox_change(self):
        """
        Shows or hides the histogram reference image selector based on checkbox state.
        """
        self.HistogramImgWidget.setVisible(self.histogramCheckbox.isChecked())

    def _minAreaSpinBox_editingFinished(self):
        """
        Validates min area when user finishes editing (loses focus or presses Enter).
        Shows a notification if the max area needs to be adjusted.
        """
        min_val = self.minAreaSpinBox.value()
        max_val = self.maxAreaSpinBox.value()

        # Only validate if value actually changed
        if min_val == self._minAreaOriginal:
            return

        # Check if min is greater than or equal to max
        if min_val >= max_val and max_val > 0:
            new_max = min_val + 1
            self.maxAreaSpinBox.setValue(new_max)
            self._maxAreaOriginal = new_max  # Update the stored max value

            # Notify user of the change
            QMessageBox.information(
                self,
                "Value Adjusted",
                f"Maximum area has been adjusted to {new_max} pixels to maintain valid range.\n"
                f"(Minimum area must be less than maximum area)",
                QMessageBox.Ok
            )

        # Update stored original value
        self._minAreaOriginal = min_val

    def _maxAreaSpinBox_editingFinished(self):
        """
        Validates max area when user finishes editing (loses focus or presses Enter).
        Shows a notification if the min area needs to be adjusted.
        """
        min_val = self.minAreaSpinBox.value()
        max_val = self.maxAreaSpinBox.value()

        # Only validate if value actually changed
        if max_val == self._maxAreaOriginal:
            return

        # Check if max is less than or equal to min
        if max_val <= min_val and max_val > 0:
            new_min = max(0, max_val - 1)  # Ensure min doesn't go below 0
            self.minAreaSpinBox.setValue(new_min)
            self._minAreaOriginal = new_min  # Update the stored min value

            # Notify user of the change
            QMessageBox.information(
                self,
                "Value Adjusted",
                f"Minimum area has been adjusted to {new_min} pixels to maintain valid range.\n"
                f"(Maximum area must be greater than minimum area)",
                QMessageBox.Ok
            )

        # Update stored original value
        self._maxAreaOriginal = max_val

    def _kMeansCheckbox_change(self):
        """
        Shows or hides the number of clusters spinbox for kMeans Clustering based on checkbox state.
        """
        self.KMeansWidget.setVisible(self.kMeansCheckbox.isChecked())

    def _startButton_clicked(self):
        """
        Starts the image analysis process.
        """
        try:
            alg_validation = self.algorithmWidget.validate()
            if alg_validation:
                self._show_error(alg_validation)
                return

            if not (self.inputFolderLine.text() and self.outputFolderLine.text()):
                self._show_error("Please set the input and output directories.")
                return

            self._set_StartButton(False)
            self._set_ViewResultsButton(False)
            self._add_log_entry("--- Starting image processing ---")

            options = self.algorithmWidget.get_options()
            hist_ref_path = self.histogramLine.text() if self.histogramCheckbox.isChecked() else None
            kmeans_clusters = self.clustersSpinBox.value() if self.kMeansCheckbox.isChecked() else None

            self.settings_service.set_setting('MinObjectArea', self.minAreaSpinBox.value())
            self.settings_service.set_setting('MaxObjectArea', self.maxAreaSpinBox.value())
            self.settings_service.set_setting('IdentifierColor', self.identifierColor)
            self.settings_service.set_setting('MaxProcesses', self.maxProcessesSpinBox.value())

            max_aois = self.settings_service.get_setting('MaxAOIs')
            aoi_radius = self.settings_service.get_setting('AOIRadius')

            self.analyzeService = AnalyzeService(
                1, self.activeAlgorithm, self.inputFolderLine.text(), self.outputFolderLine.text(),
                self.identifierColor, self.minAreaSpinBox.value(), self.maxProcessesSpinBox.value(),
                max_aois, aoi_radius, hist_ref_path, kmeans_clusters, options,
                self.maxAreaSpinBox.value()
            )

            thread = QThread()
            self.__threads.append((thread, self.analyzeService))
            self.analyzeService.moveToThread(thread)

            self.analyzeService.sig_msg.connect(self._on_worker_msg)
            self.analyzeService.sig_aois.connect(self._show_aois_limit_warning)
            self.analyzeService.sig_done.connect(self._on_worker_done)

            thread.started.connect(self.analyzeService.process_files)
            thread.start()

            self._set_CancelButton(True)
        except Exception as e:
            self.logger.error(e)

    def _cancelButton_clicked(self):
        """
        Cancels the in-progress analysis.
        """
        self.analyzeService.process_cancel()
        self._set_CancelButton(False)

    def _viewResultsButton_clicked(self):
        """
        Launches the image viewer to display analysis results.
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        file = pathlib.Path(self.results_path)
        if file.is_file():
            position_format = self.settings_service.get_setting('PositionFormat')
            temperature_unit = self.settings_service.get_setting('TemperatureUnit')
            distance_unit = self.settings_service.get_setting('DistanceUnit')
            self.viewer = Viewer(file, position_format, temperature_unit, distance_unit, False,
                                 self.settings_service.get_setting('Theme'))
            self.viewer.show()
        else:
            self._show_error("Could not parse XML file. Check file paths in \"ADIAT_Data.xml\"")
        QApplication.restoreOverrideCursor()

    def _add_log_entry(self, text):
        """
        Adds a log entry to the output window.

        Args:
            text (str): The text to add to the output window.
        """
        self.outputWindow.appendPlainText(text)

    @Slot()
    def _show_aois_limit_warning(self):
        """
        Displays a warning that the maximum number of areas of interest has been exceeded.
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText(f"Area of Interest Limit ({self.settings_service.get_setting('MaxAOIs')}) exceeded. Continue?")
        msg.setWindowTitle("Area of Interest Limit Exceeded")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if msg.exec() == QMessageBox.No:
            self._cancelButton_clicked()

    @Slot(str)
    def _on_worker_msg(self, text):
        """
        Logs a message from the worker thread.

        Args:
            text (str): The message text.
        """
        self._add_log_entry(text)

    @Slot(int, int, str)
    def _on_worker_done(self, id, images_with_aois, xml_path):
        """
        Finalizes the UI upon completion of the analysis process.

        Args:
            id (int): ID of the calling object.
            images_with_aois (int): Count of images with areas of interest.
        """
        self._add_log_entry("--- Image Processing Completed ---")
        if images_with_aois > 0:
            self._add_log_entry(f"{images_with_aois} images with areas of interest identified")
            self._set_ViewResultsButton(True)
        else:
            self._add_log_entry("No areas of interest identified")
            self._set_ViewResultsButton(False)

        self.results_path = xml_path
        self._set_StartButton(True)
        self._set_CancelButton(False)
        for thread, analyze in self.__threads:
            thread.quit()

    def _show_error(self, text):
        """
        Displays an error message.

        Args:
            text (str): The error message text.
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    def _open_load_file(self):
        """
        Opens a file dialog to select a file to load.
        """
        try:
            file, _ = QFileDialog.getOpenFileName(self, "Select File")
            if file:
                self._process_xml_file(file)
        except Exception as e:
            self.logger.error(e)

    def _process_xml_file(self, full_path):
        """
        Processes an XML file selected in the Load File dialog.

        Args:
            full_path (str): Path to the XML file.
        """
        try:
            image_count = self._get_settings_from_xml(full_path)
            if image_count > 0:
                self._set_ViewResultsButton(True)
            self.AdvancedFeaturesWidget.setVisible(not self.algorithmWidget.is_thermal)
        except Exception as e:
            self.logger.error(e)

    def _get_settings_from_xml(self, full_path):
        """
        Populates the UI with data from a previously executed analysis.

        Args:
            full_path (str): Path to the XML file.

        Returns:
            int: Number of images with areas of interest.
        """
        xmlLoader = XmlService(full_path)
        settings, image_count = xmlLoader.get_settings()
        if 'output_dir' in settings:
            self.outputFolderLine.setText(settings['output_dir'])
            self.results_path = full_path
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
            self._minAreaOriginal = int(settings['min_area'])
        if 'max_area' in settings:
            self.maxAreaSpinBox.setValue(int(settings['max_area']))
            self._maxAreaOriginal = int(settings['max_area'])
        if 'hist_ref_path' in settings:
            if settings['hist_ref_path'] != "":
                self.histogramCheckbox.setChecked(True)
                self.histogramLine.setText(settings['hist_ref_path'])
        if 'kmeans_clusters' in settings:
            if settings['kmeans_clusters'] != 0:
                self.kMeansCheckbox.setChecked(True)
                self.clustersSpinBox.setValue(settings['kmeans_clusters'])
        if 'algorithm' in settings:
            self.activeAlgorithm = next(x for x in self.algorithms if x['name'] == settings['algorithm'])
            self.algorithmComboBox.setCurrentText(self.activeAlgorithm['label'])
            self.algorithmWidget.load_options(settings['options'])
        if 'thermal' in settings:
            self.algorithmWidget.is_thermal = (settings['thermal'] == 'True')
        return image_count

    def _open_preferences(self):
        """
        Opens the Preferences dialog.
        """
        pref = Preferences(self)
        pref.exec()

    def _open_video_parser(self):
        """
        Opens the Video Parser dialog.
        """
        parser = VideoParser(self.settings_service.get_setting('Theme'))
        parser.exec()

    def _open_rtmp_detection(self):
        """
        Opens the Real-Time RTMP Color Detection viewer.
        """
        try:
            if self.rtmp_viewer is None or not self.rtmp_viewer.isVisible():
                self.rtmp_viewer = RTMPColorDetectionViewer(self)
                self.rtmp_viewer.show()
                self.logger.info("RTMP Color Detection viewer opened")
            else:
                # Bring existing viewer to front
                self.rtmp_viewer.raise_()
                self.rtmp_viewer.activateWindow()
        except Exception as e:
            self.logger.error(f"Error opening RTMP viewer: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open RTMP Color Detection viewer:\n{str(e)}")

    def _open_rtmp_motion_detection(self):
        """
        Opens the Real-Time RTMP Motion Detection viewer with dual-mode support.
        """
        try:
            if self.rtmp_motion_viewer is None or not self.rtmp_motion_viewer.isVisible():
                self.rtmp_motion_viewer = RTMPMotionDetectionViewer(self)
                self.rtmp_motion_viewer.show()
                self.logger.info("RTMP Motion Detection viewer opened")
            else:
                # Bring existing viewer to front
                self.rtmp_motion_viewer.raise_()
                self.rtmp_motion_viewer.activateWindow()
        except Exception as e:
            self.logger.error(f"Error opening RTMP motion viewer: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open RTMP Motion Detection viewer:\n{str(e)}")

    def _open_integrated_detection(self):
        """
        Opens the Real-Time Integrated Detection viewer.
        """
        try:
            if self.integrated_viewer is None or not self.integrated_viewer.isVisible():
                self.integrated_viewer = IntegratedDetectionViewer(self)
                self.integrated_viewer.show()
                self.logger.info("Integrated Detection viewer opened")
            else:
                # Bring existing viewer to front
                self.integrated_viewer.raise_()
                self.integrated_viewer.activateWindow()
        except Exception as e:
            self.logger.error(f"Error opening Integrated Detection viewer: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open Integrated Detection viewer:\n{str(e)}")

    def _open_help(self):
        """
        Opens the Help documentation URL in the default browser.
        """
        try:
            url = QUrl("https://www.texsar.org/automated-drone-image-analysis-tool/")
            QDesktopServices.openUrl(url)
            self.logger.info("Help documentation opened")
        except Exception as e:
            self.logger.error(f"Error opening Help URL: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open Help documentation:\n{str(e)}")

    def _open_community_help(self):
        """
        Opens the Community Help Discord URL in the default browser.
        """
        try:
            url = QUrl("https://discord.gg/UWxu9Dk8")
            QDesktopServices.openUrl(url)
            self.logger.info("Community Help Discord opened")
        except Exception as e:
            self.logger.error(f"Error opening Community Help URL: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open Community Help:\n{str(e)}")

    def closeEvent(self, event):
        """
        Closes all top-level windows when the main window is closed.
        """
        for window in QApplication.topLevelWidgets():
            window.close()

    def _set_StartButton(self, enabled):
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

    def _set_CancelButton(self, enabled):
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

    def _set_ViewResultsButton(self, enabled):
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

    def _set_defaults(self, version):
        """
        Sets default values for UI elements based on persistent settings and initializes settings if not previously set.
        """
        min_area = self.settings_service.get_setting('MinObjectArea')
        if isinstance(min_area, int):
            self.minAreaSpinBox.setValue(min_area)
            self._minAreaOriginal = min_area

        max_area = self.settings_service.get_setting('MaxObjectArea')
        if isinstance(max_area, int):
            self.maxAreaSpinBox.setValue(max_area)
            self._maxAreaOriginal = max_area

        max_processes = self.settings_service.get_setting('MaxProcesses')
        if isinstance(max_processes, int):
            self.maxProcessesSpinBox.setValue(max_processes)

        id_color = self.settings_service.get_setting('IdentifierColor')
        if isinstance(id_color, tuple):
            self.identifierColor = id_color
            color = QColor(*self.identifierColor)
            self.identifierColorButton.setStyleSheet("background-color: " + color.name() + ";")

        max_aois = self.settings_service.get_setting('MaxAOIs')
        if not isinstance(max_aois, int):
            self.settings_service.set_setting('MaxAOIs', 100)

        aoi_radius = self.settings_service.get_setting('AOIRadius')
        if not isinstance(aoi_radius, int):
            self.settings_service.set_setting('AOIRadius', 15)

        position_format = self.settings_service.get_setting('PositionFormat')
        if not isinstance(position_format, str):
            self.settings_service.set_setting('PositionFormat', 'Lat/Long - Decimal Degrees')

        temperature_unit = self.settings_service.get_setting('TemperatureUnit')
        if not isinstance(temperature_unit, str):
            self.settings_service.set_setting('TemperatureUnit', 'Fahrenheit')

        distance_unit = self.settings_service.get_setting('DistanceUnit')
        if not isinstance(distance_unit, str):
            self.settings_service.set_setting('DistanceUnit', 'Meters')

        theme = self.settings_service.get_setting('Theme')
        if theme is None:
            self.settings_service.set_setting('Theme', 'Dark')
            theme = 'Dark'
        self.update_theme(theme)
        try:
            current_version = self.settings_service.get_setting('app_version')
            if current_version is None or PickleHelper.get_drone_sensor_file_version() is None:
                self.settings_service.set_setting('app_version', version)
                PickleHelper.copy_pickle('drones.pkl')
            else:
                current_version_int = PickleHelper.version_to_int(current_version)
                new_version_int = PickleHelper.version_to_int(version)
                if new_version_int > current_version_int:
                    self.settings_service.set_setting('app_version', version)
                    PickleHelper.copy_pickle('drones.pkl')
            if PickleHelper.get_xmp_mapping() is None:
                PickleHelper.copy_pickle('xmp.pkl')
        except Exception as e:
            self.logger.error(e)

    def update_theme(self, theme):
        """
        Updates the application theme.

        Args:
            theme (str): 'Light' or 'Dark'
        """
        if theme == 'Light':
            self.theme.setup_theme("light")
            self._apply_icons("Light")
        else:
            self.theme.setup_theme()
            self._apply_icons("Dark")

    def _show_area_validation_error(self, message):
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
        msg.exec()

    def _apply_icons(self, theme):
        """
        Loads icon assets based on the currently selected theme.

        Args:
            theme (str): Name of the active theme used to resolve icon paths.
        """
        from helpers.IconHelper import IconHelper
        
        self.inputFolderButton.setIcon(IconHelper.create_icon('fa6.folder-open', theme))
        self.outputFolderButton.setIcon(IconHelper.create_icon('fa6.folder-open', theme))
        self.startButton.setIcon(IconHelper.create_icon('fa6s.play', theme))
        self.cancelButton.setIcon(IconHelper.create_icon('mdi.close-circle', theme))
        self.viewResultsButton.setIcon(IconHelper.create_icon('fa6.images', theme))
        self.histogramButton.setIcon(IconHelper.create_icon('fa6.image', theme))
        