# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMenu, QMenuBar, QPlainTextEdit,
    QPushButton, QSizePolicy, QSpacerItem, QSpinBox,
    QStatusBar, QVBoxLayout, QWidget)
from . import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(897, 835)
        font = QFont()
        font.setPointSize(10)
        MainWindow.setFont(font)
        icon = QIcon()
        icon.addFile(u":/ADIAT.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        self.actionLoadFile = QAction(MainWindow)
        self.actionLoadFile.setObjectName(u"actionLoadFile")
        self.actionLoadFile.setFont(font)
        self.actionPreferences = QAction(MainWindow)
        self.actionPreferences.setObjectName(u"actionPreferences")
        self.actionPreferences.setFont(font)
        self.actionVideoParser = QAction(MainWindow)
        self.actionVideoParser.setObjectName(u"actionVideoParser")
        self.actionVideoParser.setFont(font)
        self.actionRTMPDetection = QAction(MainWindow)
        self.actionRTMPDetection.setObjectName(u"actionRTMPDetection")
        self.actionRTMPDetection.setFont(font)
        self.actionIntegratedDetection = QAction(MainWindow)
        self.actionIntegratedDetection.setObjectName(u"actionIntegratedDetection")
        self.actionIntegratedDetection.setFont(font)
        self.actionCoordinator = QAction(MainWindow)
        self.actionCoordinator.setObjectName(u"actionCoordinator")
        self.actionCoordinator.setFont(font)
        self.actionHelp = QAction(MainWindow)
        self.actionHelp.setObjectName(u"actionHelp")
        self.actionHelp.setFont(font)
        self.actionCommunityHelp = QAction(MainWindow)
        self.actionCommunityHelp.setObjectName(u"actionCommunityHelp")
        self.actionCommunityHelp.setFont(font)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.verticalLayout_3 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.setupFrame = QFrame(self.centralwidget)
        self.setupFrame.setObjectName(u"setupFrame")
        self.setupFrame.setFrameShape(QFrame.StyledPanel)
        self.setupFrame.setFrameShadow(QFrame.Plain)
        self.setupFrame.setLineWidth(3)
        self.verticalLayout_4 = QVBoxLayout(self.setupFrame)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.directoriesLayout = QGridLayout()
        self.directoriesLayout.setSpacing(6)
        self.directoriesLayout.setObjectName(u"directoriesLayout")
        self.outputFolderButton = QPushButton(self.setupFrame)
        self.outputFolderButton.setObjectName(u"outputFolderButton")
        self.outputFolderButton.setFont(font)
        icon1 = QIcon()
        icon1.addFile(u":/icons/folder.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.outputFolderButton.setIcon(icon1)

        self.directoriesLayout.addWidget(self.outputFolderButton, 1, 2, 1, 1)

        self.outputFolderLine = QLineEdit(self.setupFrame)
        self.outputFolderLine.setObjectName(u"outputFolderLine")
        self.outputFolderLine.setFont(font)
        self.outputFolderLine.setReadOnly(True)

        self.directoriesLayout.addWidget(self.outputFolderLine, 1, 1, 1, 1)

        self.inputFolderLabel = QLabel(self.setupFrame)
        self.inputFolderLabel.setObjectName(u"inputFolderLabel")
        self.inputFolderLabel.setFont(font)

        self.directoriesLayout.addWidget(self.inputFolderLabel, 0, 0, 1, 1)

        self.outputFolderLabel = QLabel(self.setupFrame)
        self.outputFolderLabel.setObjectName(u"outputFolderLabel")
        self.outputFolderLabel.setFont(font)

        self.directoriesLayout.addWidget(self.outputFolderLabel, 1, 0, 1, 1)

        self.inputFolderButton = QPushButton(self.setupFrame)
        self.inputFolderButton.setObjectName(u"inputFolderButton")
        self.inputFolderButton.setFont(font)
        self.inputFolderButton.setIcon(icon1)

        self.directoriesLayout.addWidget(self.inputFolderButton, 0, 2, 1, 1)

        self.inputFolderLine = QLineEdit(self.setupFrame)
        self.inputFolderLine.setObjectName(u"inputFolderLine")
        self.inputFolderLine.setFont(font)
        self.inputFolderLine.setReadOnly(True)

        self.directoriesLayout.addWidget(self.inputFolderLine, 0, 1, 1, 1)


        self.verticalLayout_4.addLayout(self.directoriesLayout)

        self.GlobalOptionsFrame = QFrame(self.setupFrame)
        self.GlobalOptionsFrame.setObjectName(u"GlobalOptionsFrame")
        self.GlobalOptionsFrame.setFrameShape(QFrame.StyledPanel)
        self.GlobalOptionsFrame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.GlobalOptionsFrame)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.GeneralLayout = QHBoxLayout()
        self.GeneralLayout.setObjectName(u"GeneralLayout")
        self.minAreaLabel = QLabel(self.GlobalOptionsFrame)
        self.minAreaLabel.setObjectName(u"minAreaLabel")
        self.minAreaLabel.setFont(font)

        self.GeneralLayout.addWidget(self.minAreaLabel)

        self.minAreaSpinBox = QSpinBox(self.GlobalOptionsFrame)
        self.minAreaSpinBox.setObjectName(u"minAreaSpinBox")
        self.minAreaSpinBox.setFont(font)
        self.minAreaSpinBox.setMinimum(1)
        self.minAreaSpinBox.setMaximum(999)
        self.minAreaSpinBox.setValue(10)

        self.GeneralLayout.addWidget(self.minAreaSpinBox)

        self.maxAreaLabel = QLabel(self.GlobalOptionsFrame)
        self.maxAreaLabel.setObjectName(u"maxAreaLabel")
        font1 = QFont()
        font1.setPointSize(10)
        font1.setBold(False)
        self.maxAreaLabel.setFont(font1)

        self.GeneralLayout.addWidget(self.maxAreaLabel)

        self.maxAreaSpinBox = QSpinBox(self.GlobalOptionsFrame)
        self.maxAreaSpinBox.setObjectName(u"maxAreaSpinBox")
        self.maxAreaSpinBox.setFont(font)
        self.maxAreaSpinBox.setMinimum(0)
        self.maxAreaSpinBox.setMaximum(99999)
        self.maxAreaSpinBox.setSingleStep(1)
        self.maxAreaSpinBox.setValue(0)

        self.GeneralLayout.addWidget(self.maxAreaSpinBox)

        self.processingResolutionLabel = QLabel(self.GlobalOptionsFrame)
        self.processingResolutionLabel.setObjectName(u"processingResolutionLabel")
        self.processingResolutionLabel.setFont(font)

        self.GeneralLayout.addWidget(self.processingResolutionLabel)

        self.processingResolutionCombo = QComboBox(self.GlobalOptionsFrame)
        self.processingResolutionCombo.setObjectName(u"processingResolutionCombo")
        self.processingResolutionCombo.setFont(font)

        self.GeneralLayout.addWidget(self.processingResolutionCombo)

        self.generalHorizontalSpacer1 = QSpacerItem(48, 43, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.GeneralLayout.addItem(self.generalHorizontalSpacer1)

        self.identifierColor = QLabel(self.GlobalOptionsFrame)
        self.identifierColor.setObjectName(u"identifierColor")
        self.identifierColor.setFont(font)

        self.GeneralLayout.addWidget(self.identifierColor)

        self.identifierColorButton = QPushButton(self.GlobalOptionsFrame)
        self.identifierColorButton.setObjectName(u"identifierColorButton")
        self.identifierColorButton.setStyleSheet(u"background-color: rgb(0, 255, 0);")

        self.GeneralLayout.addWidget(self.identifierColorButton)

        self.generalHorizontalSpacer2 = QSpacerItem(40, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.GeneralLayout.addItem(self.generalHorizontalSpacer2)

        self.maxProcessesLabel = QLabel(self.GlobalOptionsFrame)
        self.maxProcessesLabel.setObjectName(u"maxProcessesLabel")
        self.maxProcessesLabel.setFont(font)

        self.GeneralLayout.addWidget(self.maxProcessesLabel)

        self.maxProcessesSpinBox = QSpinBox(self.GlobalOptionsFrame)
        self.maxProcessesSpinBox.setObjectName(u"maxProcessesSpinBox")
        self.maxProcessesSpinBox.setFont(font)
        self.maxProcessesSpinBox.setMinimum(1)
        self.maxProcessesSpinBox.setMaximum(20)
        self.maxProcessesSpinBox.setValue(10)

        self.GeneralLayout.addWidget(self.maxProcessesSpinBox)


        self.verticalLayout_6.addLayout(self.GeneralLayout)

        self.AdvancedFeaturesWidget = QWidget(self.GlobalOptionsFrame)
        self.AdvancedFeaturesWidget.setObjectName(u"AdvancedFeaturesWidget")
        self.verticalLayout = QVBoxLayout(self.AdvancedFeaturesWidget)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.KMeansLayout = QHBoxLayout()
        self.KMeansLayout.setObjectName(u"KMeansLayout")
        self.kMeansCheckbox = QCheckBox(self.AdvancedFeaturesWidget)
        self.kMeansCheckbox.setObjectName(u"kMeansCheckbox")
        self.kMeansCheckbox.setMaximumSize(QSize(16777215, 16777215))
        self.kMeansCheckbox.setFont(font)

        self.KMeansLayout.addWidget(self.kMeansCheckbox)

        self.KMeansWidget = QWidget(self.AdvancedFeaturesWidget)
        self.KMeansWidget.setObjectName(u"KMeansWidget")
        self.horizontalLayout = QHBoxLayout(self.KMeansWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.clustersLabel = QLabel(self.KMeansWidget)
        self.clustersLabel.setObjectName(u"clustersLabel")
        self.clustersLabel.setFont(font)

        self.horizontalLayout.addWidget(self.clustersLabel)

        self.clustersSpinBox = QSpinBox(self.KMeansWidget)
        self.clustersSpinBox.setObjectName(u"clustersSpinBox")
        self.clustersSpinBox.setFont(font)
        self.clustersSpinBox.setMinimum(2)
        self.clustersSpinBox.setMaximum(100)
        self.clustersSpinBox.setValue(10)

        self.horizontalLayout.addWidget(self.clustersSpinBox)


        self.KMeansLayout.addWidget(self.KMeansWidget)


        self.verticalLayout.addLayout(self.KMeansLayout)

        self.HistogramLayout = QHBoxLayout()
        self.HistogramLayout.setObjectName(u"HistogramLayout")
        self.histogramCheckbox = QCheckBox(self.AdvancedFeaturesWidget)
        self.histogramCheckbox.setObjectName(u"histogramCheckbox")
        self.histogramCheckbox.setFont(font)

        self.HistogramLayout.addWidget(self.histogramCheckbox)

        self.HistogramImgWidget = QWidget(self.AdvancedFeaturesWidget)
        self.HistogramImgWidget.setObjectName(u"HistogramImgWidget")
        self.horizontalLayout_3 = QHBoxLayout(self.HistogramImgWidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.histogramReferenceImageLabel = QLabel(self.HistogramImgWidget)
        self.histogramReferenceImageLabel.setObjectName(u"histogramReferenceImageLabel")
        self.histogramReferenceImageLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.histogramReferenceImageLabel)

        self.histogramLine = QLineEdit(self.HistogramImgWidget)
        self.histogramLine.setObjectName(u"histogramLine")
        self.histogramLine.setFont(font)
        self.histogramLine.setReadOnly(True)

        self.horizontalLayout_3.addWidget(self.histogramLine)

        self.histogramButton = QPushButton(self.HistogramImgWidget)
        self.histogramButton.setObjectName(u"histogramButton")
        self.histogramButton.setFont(font)
        icon2 = QIcon()
        icon2.addFile(u":/icons/image.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.histogramButton.setIcon(icon2)

        self.horizontalLayout_3.addWidget(self.histogramButton)


        self.HistogramLayout.addWidget(self.HistogramImgWidget)


        self.verticalLayout.addLayout(self.HistogramLayout)


        self.verticalLayout_6.addWidget(self.AdvancedFeaturesWidget)


        self.verticalLayout_4.addWidget(self.GlobalOptionsFrame)

        self.line = QFrame(self.setupFrame)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_4.addWidget(self.line)

        self.algorithmSelectorlLayout = QHBoxLayout()
        self.algorithmSelectorlLayout.setObjectName(u"algorithmSelectorlLayout")
        self.algorithmLabel = QLabel(self.setupFrame)
        self.algorithmLabel.setObjectName(u"algorithmLabel")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.algorithmLabel.sizePolicy().hasHeightForWidth())
        self.algorithmLabel.setSizePolicy(sizePolicy1)
        self.algorithmLabel.setFont(font)

        self.algorithmSelectorlLayout.addWidget(self.algorithmLabel)

        self.tempAlgorithmComboBox = QComboBox(self.setupFrame)
        self.tempAlgorithmComboBox.setObjectName(u"tempAlgorithmComboBox")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.tempAlgorithmComboBox.sizePolicy().hasHeightForWidth())
        self.tempAlgorithmComboBox.setSizePolicy(sizePolicy2)
        self.tempAlgorithmComboBox.setMinimumSize(QSize(300, 0))
        self.tempAlgorithmComboBox.setFont(font)

        self.algorithmSelectorlLayout.addWidget(self.tempAlgorithmComboBox)

        self.algorithmHorizontalSpacer = QSpacerItem(400, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.algorithmSelectorlLayout.addItem(self.algorithmHorizontalSpacer)


        self.verticalLayout_4.addLayout(self.algorithmSelectorlLayout)

        self.algorithmFrame = QFrame(self.setupFrame)
        self.algorithmFrame.setObjectName(u"algorithmFrame")
        self.algorithmFrame.setFrameShape(QFrame.StyledPanel)
        self.algorithmFrame.setFrameShadow(QFrame.Plain)
        self.algorithmFrame.setLineWidth(3)
        self.algorithmFrame.setMidLineWidth(0)
        self.verticalLayout_2 = QVBoxLayout(self.algorithmFrame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")

        self.verticalLayout_4.addWidget(self.algorithmFrame)


        self.verticalLayout_3.addWidget(self.setupFrame)

        self.mainButtons = QHBoxLayout()
        self.mainButtons.setObjectName(u"mainButtons")
        self.startButton = QPushButton(self.centralwidget)
        self.startButton.setObjectName(u"startButton")
        self.startButton.setEnabled(True)
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.startButton.sizePolicy().hasHeightForWidth())
        self.startButton.setSizePolicy(sizePolicy3)
        self.startButton.setMinimumSize(QSize(150, 0))
        font2 = QFont()
        font2.setPointSize(10)
        font2.setBold(True)
        self.startButton.setFont(font2)
        self.startButton.setLayoutDirection(Qt.LeftToRight)
        self.startButton.setAutoFillBackground(False)
        self.startButton.setStyleSheet(u"background-color: rgb(0, 136, 0);\n"
"color: rgb(228, 231, 235);")

        self.mainButtons.addWidget(self.startButton)

        self.cancelButton = QPushButton(self.centralwidget)
        self.cancelButton.setObjectName(u"cancelButton")
        self.cancelButton.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.cancelButton.sizePolicy().hasHeightForWidth())
        self.cancelButton.setSizePolicy(sizePolicy3)
        self.cancelButton.setMinimumSize(QSize(150, 0))
        self.cancelButton.setFont(font2)
        self.cancelButton.setStyleSheet(u"")
        icon3 = QIcon()
        icon3.addFile(u":/icons/cancel.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.cancelButton.setIcon(icon3)

        self.mainButtons.addWidget(self.cancelButton)

        self.viewResultsButton = QPushButton(self.centralwidget)
        self.viewResultsButton.setObjectName(u"viewResultsButton")
        self.viewResultsButton.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.viewResultsButton.sizePolicy().hasHeightForWidth())
        self.viewResultsButton.setSizePolicy(sizePolicy3)
        self.viewResultsButton.setMinimumSize(QSize(150, 0))
        self.viewResultsButton.setFont(font2)
        self.viewResultsButton.setAutoFillBackground(False)
        self.viewResultsButton.setStyleSheet(u"")
        icon4 = QIcon()
        icon4.addFile(u":/icons/search.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.viewResultsButton.setIcon(icon4)

        self.mainButtons.addWidget(self.viewResultsButton)

        self.buttonsSpacer = QSpacerItem(400, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.mainButtons.addItem(self.buttonsSpacer)


        self.verticalLayout_3.addLayout(self.mainButtons)

        self.outputWindow = QPlainTextEdit(self.centralwidget)
        self.outputWindow.setObjectName(u"outputWindow")
        self.outputWindow.setEnabled(True)
        font3 = QFont()
        font3.setPointSize(12)
        self.outputWindow.setFont(font3)
        self.outputWindow.setReadOnly(True)
        self.outputWindow.setCenterOnScroll(True)

        self.verticalLayout_3.addWidget(self.outputWindow)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.mainBar = QMenuBar(MainWindow)
        self.mainBar.setObjectName(u"mainBar")
        self.mainBar.setGeometry(QRect(0, 0, 897, 23))
        self.menuFile = QMenu(self.mainBar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuHelp = QMenu(self.mainBar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.mainBar)

        self.mainBar.addAction(self.menuFile.menuAction())
        self.mainBar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionLoadFile)
        self.menuFile.addAction(self.actionPreferences)
        self.menuFile.addAction(self.actionVideoParser)
        self.menuFile.addAction(self.actionRTMPDetection)
        self.menuFile.addAction(self.actionIntegratedDetection)
        self.menuFile.addAction(self.actionCoordinator)
        self.menuHelp.addAction(self.actionHelp)
        self.menuHelp.addAction(self.actionCommunityHelp)

        self.retranslateUi(MainWindow)

        self.startButton.setDefault(False)
        self.viewResultsButton.setDefault(False)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Automated Drone Image Analysis Tool  v1.2 - Sponsored by TEXSAR", None))
        self.actionLoadFile.setText(QCoreApplication.translate("MainWindow", u"Load Results File", None))
#if QT_CONFIG(tooltip)
        self.actionLoadFile.setToolTip(QCoreApplication.translate("MainWindow", u"Load a previously saved results file for viewing.\n"
"Opens a file dialog to select a results file (.pkl format).\n"
"Loads the analysis results and opens the Results Viewer.\n"
"Use this to review results from previous analysis sessions without reprocessing.", None))
#endif // QT_CONFIG(tooltip)
        self.actionPreferences.setText(QCoreApplication.translate("MainWindow", u"Preferences", None))
#if QT_CONFIG(tooltip)
        self.actionPreferences.setToolTip(QCoreApplication.translate("MainWindow", u"Open the Preferences dialog to configure application settings.\n"
"Adjust global settings including:\n"
"\u2022 Application theme (Light/Dark)\n"
"\u2022 Max AOI warning threshold\n"
"\u2022 AOI circle radius for clustering\n"
"\u2022 Coordinate system format (Lat/Long, UTM)\n"
"\u2022 Temperature unit (Fahrenheit/Celsius)\n"
"\u2022 Distance unit (Meters/Feet)\n"
"\u2022 Drone sensor configuration file\n"
"All changes are saved automatically.", None))
#endif // QT_CONFIG(tooltip)
        self.actionVideoParser.setText(QCoreApplication.translate("MainWindow", u"Video Parser", None))
#if QT_CONFIG(tooltip)
        self.actionVideoParser.setToolTip(QCoreApplication.translate("MainWindow", u"Open the Video Parser utility to extract frames from video files.\n"
"Convert video footage into individual frame images for analysis.\n"
"Features:\n"
"\u2022 Extract frames at specified time intervals\n"
"\u2022 Optional SRT file support for GPS metadata\n"
"\u2022 Supports common video formats (MP4, AVI, MOV, etc.)\n"
"\u2022 Embeds location data into extracted frames\n"
"Use to prepare video footage for image-based analysis.", None))
#endif // QT_CONFIG(tooltip)
        self.actionRTMPDetection.setText(QCoreApplication.translate("MainWindow", u"Real-Time Color Detection", None))
#if QT_CONFIG(tooltip)
        self.actionRTMPDetection.setToolTip(QCoreApplication.translate("MainWindow", u"Open the Real-Time Color Detection window for live video analysis.\n"
"Perform HSV color-based detection on live video streams.\n"
"Features:\n"
"\u2022 Connect to RTMP/RTSP video streams or local cameras\n"
"\u2022 Real-time color detection with adjustable HSV ranges\n"
"\u2022 Interactive HSV range tuning with live preview\n"
"\u2022 Adjustable processing resolution for performance\n"
"\u2022 Frame capture and saving capabilities\n"
"\u2022 Detection statistics and performance metrics\n"
"Ideal for live drone feeds and real-time monitoring applications.", None))
#endif // QT_CONFIG(tooltip)
        self.actionIntegratedDetection.setText(QCoreApplication.translate("MainWindow", u"Real-Time Anomaly Detection", None))
#if QT_CONFIG(tooltip)
        self.actionIntegratedDetection.setToolTip(QCoreApplication.translate("MainWindow", u"Open the Real-Time Anomaly Detection window for advanced live analysis.\n"
"Combines multiple detection algorithms for comprehensive real-time anomaly detection.\n"
"Features:\n"
"\u2022 Motion detection with background subtraction\n"
"\u2022 Color quantization anomaly detection\n"
"\u2022 Advanced streaming video processing\n"
"\u2022 Detection fusion and temporal filtering\n"
"\u2022 Real-time performance optimization\n"
"\u2022 Multi-threaded processing for better performance\n"
"\u2022 Enhanced detection accuracy through algorithm combination\n"
"Designed for detecting unusual objects, movement, and colors in real-time video streams.", None))
#endif // QT_CONFIG(tooltip)
        self.actionCoordinator.setText(QCoreApplication.translate("MainWindow", u"Search Coordinator", None))
#if QT_CONFIG(tooltip)
        self.actionCoordinator.setToolTip(QCoreApplication.translate("MainWindow", u"Open the Search Coordinator window for managing multi-batch review projects.\n"
"Features:\n"
"\u2022 Create and manage search projects with multiple batches\n"
"\u2022 Track reviewer progress across multiple image sets\n"
"\u2022 Consolidate review results from multiple reviewers\n"
"\u2022 View dashboard with search status and metrics\n"
"\u2022 Export consolidated results\n"
"\u2022 Manage batch assignments and reviewer coordination\n"
"Ideal for large-scale searches with multiple reviewers and image batches.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.actionCoordinator.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Shift+C", None))
#endif // QT_CONFIG(shortcut)
        self.actionHelp.setText(QCoreApplication.translate("MainWindow", u"Manual", None))
#if QT_CONFIG(tooltip)
        self.actionHelp.setToolTip(QCoreApplication.translate("MainWindow", u"Open the online help documentation in your web browser.\n"
"Access comprehensive documentation, tutorials, and user guides.\n"
"Provides detailed information on all features and algorithms.", None))
#endif // QT_CONFIG(tooltip)
        self.actionCommunityHelp.setText(QCoreApplication.translate("MainWindow", u"Community Forum", None))
#if QT_CONFIG(tooltip)
        self.actionCommunityHelp.setToolTip(QCoreApplication.translate("MainWindow", u"Join the community Discord server for support and discussions.\n"
"Connect with other users, share experiences, and get help.\n"
"Ask questions, report issues, and suggest new features.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.outputFolderButton.setToolTip(QCoreApplication.translate("MainWindow", u"Browse for the output folder to save analysis results.\n"
"Opens a folder selection dialog.\n"
"Choose an empty folder or create a new one to avoid overwriting existing files.", None))
#endif // QT_CONFIG(tooltip)
        self.outputFolderButton.setText(QCoreApplication.translate("MainWindow", u" Select", None))
        self.outputFolderButton.setProperty(u"iconName", QCoreApplication.translate("MainWindow", u"folder.png", None))
#if QT_CONFIG(tooltip)
        self.outputFolderLine.setToolTip(QCoreApplication.translate("MainWindow", u"Path to the output folder for saving analysis results.\n"
"Click the Select button to browse for a destination folder.\n"
"Results include:\n"
"\u2022 Processed images with detected objects marked\n"
"\u2022 CSV file with detection coordinates and metadata\n"
"\u2022 KML file for viewing results in mapping applications\n"
"\u2022 Additional algorithm-specific output files", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.inputFolderLabel.setToolTip(QCoreApplication.translate("MainWindow", u"Select the folder containing images to analyze.\n"
"Supported formats: JPG, PNG, TIFF, and other common image formats.", None))
#endif // QT_CONFIG(tooltip)
        self.inputFolderLabel.setText(QCoreApplication.translate("MainWindow", u"Input Folder:", None))
#if QT_CONFIG(tooltip)
        self.outputFolderLabel.setToolTip(QCoreApplication.translate("MainWindow", u"Select the destination folder for analysis results.\n"
"Output includes processed images with marked detections and CSV data files.", None))
#endif // QT_CONFIG(tooltip)
        self.outputFolderLabel.setText(QCoreApplication.translate("MainWindow", u"Output Folder:", None))
#if QT_CONFIG(tooltip)
        self.inputFolderButton.setToolTip(QCoreApplication.translate("MainWindow", u"Browse for the input folder containing images to analyze.\n"
"Opens a folder selection dialog.", None))
#endif // QT_CONFIG(tooltip)
        self.inputFolderButton.setText(QCoreApplication.translate("MainWindow", u" Select", None))
        self.inputFolderButton.setProperty(u"iconName", QCoreApplication.translate("MainWindow", u"folder.png", None))
#if QT_CONFIG(tooltip)
        self.inputFolderLine.setToolTip(QCoreApplication.translate("MainWindow", u"Path to the input folder containing images for analysis.\n"
"Click the Select button to browse for a folder.\n"
"All supported image files in this folder will be processed.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.minAreaLabel.setToolTip(QCoreApplication.translate("MainWindow", u"Minimum object size in pixels for detection filtering.\n"
"Objects smaller than this will be ignored.", None))
#endif // QT_CONFIG(tooltip)
        self.minAreaLabel.setText(QCoreApplication.translate("MainWindow", u"Min Object Area (px):", None))
#if QT_CONFIG(tooltip)
        self.minAreaSpinBox.setToolTip(QCoreApplication.translate("MainWindow", u"Set the minimum object area in pixels for detection filtering.\n"
"\u2022 Range: 1 to 999 pixels\n"
"\u2022 Default: 10 pixels\n"
"Objects smaller than this threshold will be filtered out and not detected.\n"
"\u2022 Lower values: Detect smaller objects (may increase false positives)\n"
"\u2022 Higher values: Only detect larger objects (reduces noise)\n"
"Use to filter out small artifacts and noise in detection results.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.maxAreaLabel.setToolTip(QCoreApplication.translate("MainWindow", u"Maximum object size in pixels for detection filtering.\n"
"Objects larger than this will be ignored.", None))
#endif // QT_CONFIG(tooltip)
        self.maxAreaLabel.setText(QCoreApplication.translate("MainWindow", u"Max Object Area (px):", None))
#if QT_CONFIG(tooltip)
        self.maxAreaSpinBox.setToolTip(QCoreApplication.translate("MainWindow", u"Set the maximum object area in pixels for detection filtering.\n"
"\u2022 Range: 0 to 99999 pixels\n"
"\u2022 Default: 0 (None - no maximum filter applied)\n"
"\u2022 Special value: 0 displays as \"None\"\n"
"Objects larger than this threshold will be filtered out and not detected.\n"
"\u2022 Lower values: Only detect smaller objects\n"
"\u2022 Higher values: Allow detection of larger objects\n"
"\u2022 Set to 0 (None): No maximum size filtering\n"
"Use to exclude very large false positive detections like shadows or terrain features.", None))
#endif // QT_CONFIG(tooltip)
        self.maxAreaSpinBox.setSpecialValueText(QCoreApplication.translate("MainWindow", u"None", None))
#if QT_CONFIG(tooltip)
        self.processingResolutionLabel.setToolTip(QCoreApplication.translate("MainWindow", u"Resolution at which images are processed.\n"
"Lower resolutions = faster processing but may miss small objects.", None))
#endif // QT_CONFIG(tooltip)
        self.processingResolutionLabel.setText(QCoreApplication.translate("MainWindow", u"Processing Resolution:", None))
#if QT_CONFIG(tooltip)
        self.processingResolutionCombo.setToolTip(QCoreApplication.translate("MainWindow", u"Select processing resolution as percentage of original image size:\n"
"\u2022 100%: Original resolution (no scaling, highest quality, slowest)\n"
"\u2022 75%: High quality (~56% of pixels, ~1.8x faster)\n"
"\u2022 50%: Balanced quality (25% of pixels, ~4x faster) - RECOMMENDED\n"
"\u2022 33%: Fast processing (~11% of pixels, ~9x faster)\n"
"\u2022 25%: Very fast (6% of pixels, ~16x faster)\n"
"\u2022 10%: Ultra fast (1% of pixels, ~100x faster)\n"
"\n"
"Percentage scaling preserves original aspect ratio.\n"
"Works with any image size, orientation, or aspect ratio.\n"
"\n"
"Min/Max Area values are always specified in original resolution.\n"
"All results are returned in original resolution coordinates.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.identifierColor.setToolTip(QCoreApplication.translate("MainWindow", u"Color used to mark and identify detected objects in output images.\n"
"Click the color button to select a different color.", None))
#endif // QT_CONFIG(tooltip)
        self.identifierColor.setText(QCoreApplication.translate("MainWindow", u"Object Identifer Color:", None))
#if QT_CONFIG(tooltip)
        self.identifierColorButton.setToolTip(QCoreApplication.translate("MainWindow", u"Select the color used to mark detected objects in output images.\n"
"\u2022 Default: Green (RGB: 0, 255, 0)\n"
"Click to open a color picker dialog and choose a different marker color.\n"
"The selected color will be used for:\n"
"\u2022 Drawing circles/rectangles around detected objects\n"
"\u2022 Highlighting AOI locations on output images\n"
"\u2022 Creating visual markers in the results viewer\n"
"Choose a color that contrasts well with your image content for best visibility.", None))
#endif // QT_CONFIG(tooltip)
        self.identifierColorButton.setText("")
#if QT_CONFIG(tooltip)
        self.maxProcessesLabel.setToolTip(QCoreApplication.translate("MainWindow", u"Maximum number of parallel processes to use for image analysis.\n"
"More processes = faster processing but higher CPU/memory usage.", None))
#endif // QT_CONFIG(tooltip)
        self.maxProcessesLabel.setText(QCoreApplication.translate("MainWindow", u"Max Processes: ", None))
#if QT_CONFIG(tooltip)
        self.maxProcessesSpinBox.setToolTip(QCoreApplication.translate("MainWindow", u"Set the maximum number of parallel processes for image analysis.\n"
"\u2022 Range: 1 to 20 processes\n"
"\u2022 Default: 10 processes\n"
"The application uses multiprocessing to analyze multiple images simultaneously:\n"
"\u2022 Higher values: Faster processing (uses more CPU cores and memory)\n"
"\u2022 Lower values: Slower processing (uses fewer system resources)\n"
"\u2022 Recommended: Set to number of CPU cores or slightly higher\n"
"\u2022 For systems with limited RAM, reduce this value to prevent memory issues\n"
"Each process analyzes one image at a time, so more processes = more parallel image processing.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.kMeansCheckbox.setToolTip(QCoreApplication.translate("MainWindow", u"Enable K-Means clustering preprocessing on images before detection.\n"
"K-Means clustering reduces image colors to a specified number of dominant colors:\n"
"\u2022 Simplifies image complexity for better detection\n"
"\u2022 Groups similar pixels into clusters\n"
"\u2022 Can improve detection of specific colored objects\n"
"\u2022 Reduces noise and color variations\n"
"When enabled, specify the number of color clusters to use.\n"
"Useful for images with complex color patterns or when targeting specific colors.", None))
#endif // QT_CONFIG(tooltip)
        self.kMeansCheckbox.setText(QCoreApplication.translate("MainWindow", u"Use K-Means Clustering", None))
#if QT_CONFIG(tooltip)
        self.clustersLabel.setToolTip(QCoreApplication.translate("MainWindow", u"Number of color clusters to use in K-Means preprocessing.\n"
"Determines how many dominant colors the image is reduced to.", None))
#endif // QT_CONFIG(tooltip)
        self.clustersLabel.setText(QCoreApplication.translate("MainWindow", u"Number of Clusters (Colors)", None))
#if QT_CONFIG(tooltip)
        self.clustersSpinBox.setToolTip(QCoreApplication.translate("MainWindow", u"Set the number of color clusters for K-Means preprocessing.\n"
"\u2022 Range: 2 to 100 clusters\n"
"\u2022 Default: 10 clusters\n"
"The image will be reduced to this many dominant colors:\n"
"\u2022 Lower values (2-5): Aggressive color reduction, simpler images\n"
"\u2022 Medium values (6-15): Balanced reduction, good for most cases\n"
"\u2022 Higher values (16-100): Subtle reduction, preserves more color detail\n"
"Start with 10 and adjust based on your image complexity and detection needs.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.histogramCheckbox.setToolTip(QCoreApplication.translate("MainWindow", u"Enable histogram normalization preprocessing on images before detection.\n"
"Histogram normalization adjusts image colors to match a reference image:\n"
"\u2022 Equalizes lighting and color differences across images\n"
"\u2022 Corrects for varying sun angles, shadows, and atmospheric conditions\n"
"\u2022 Standardizes color appearance across image set\n"
"\u2022 Improves consistency of detection results\n"
"When enabled, select a reference image with ideal lighting/color conditions.\n"
"Useful when processing images taken at different times or under varying conditions.", None))
#endif // QT_CONFIG(tooltip)
        self.histogramCheckbox.setText(QCoreApplication.translate("MainWindow", u"Normalize Histograms", None))
#if QT_CONFIG(tooltip)
        self.histogramReferenceImageLabel.setToolTip(QCoreApplication.translate("MainWindow", u"Select the reference image for histogram normalization.\n"
"All images will be adjusted to match this image's color distribution.", None))
#endif // QT_CONFIG(tooltip)
        self.histogramReferenceImageLabel.setText(QCoreApplication.translate("MainWindow", u"Reference Image:", None))
#if QT_CONFIG(tooltip)
        self.histogramLine.setToolTip(QCoreApplication.translate("MainWindow", u"Path to the reference image for histogram normalization.\n"
"Click the Select button to choose an image.\n"
"Choose an image with ideal lighting and color conditions:\n"
"\u2022 Clear, well-lit image from your dataset\n"
"\u2022 Representative of the desired appearance\n"
"\u2022 Typical lighting conditions for your mission\n"
"All other images will be color-adjusted to match this reference.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.histogramButton.setToolTip(QCoreApplication.translate("MainWindow", u"Browse for a reference image for histogram normalization.\n"
"Opens an image file selection dialog.\n"
"Select a representative image with good lighting and typical color conditions.", None))
#endif // QT_CONFIG(tooltip)
        self.histogramButton.setText(QCoreApplication.translate("MainWindow", u" Select", None))
        self.histogramButton.setProperty(u"iconName", QCoreApplication.translate("MainWindow", u"image.png", None))
#if QT_CONFIG(tooltip)
        self.algorithmLabel.setToolTip(QCoreApplication.translate("MainWindow", u"Select the detection algorithm to use for image analysis.\n"
"\n"
"Each algorithm has specific strengths and use cases:\n"
"\n"
"\u2022 HSV Color Range: Best for detecting specific colored objects\n"
"\u2022 Color Range (RGB): Alternative color detection using RGB color space\n"
"\u2022 RX Anomaly: Statistical detection for unusual/anomalous objects\n"
"\u2022 Thermal Anomaly: Detects temperature anomalies in thermal imagery\n"
"\u2022 Thermal Range: Temperature-based detection in thermal images\n"
"\u2022 Matched Filter: Target-based detection using spectral matching\n"
"\u2022 MR Map: Multi-resolution feature detection at various scales\n"
"\u2022 AI Person Detector: Machine learning for detecting people\n"
"\n"
"Hover over the algorithm dropdown for detailed descriptions of each algorithm.", None))
#endif // QT_CONFIG(tooltip)
        self.algorithmLabel.setText(QCoreApplication.translate("MainWindow", u"Algorithm:", None))
#if QT_CONFIG(tooltip)
        self.tempAlgorithmComboBox.setToolTip(QCoreApplication.translate("MainWindow", u"Select the detection algorithm for your image analysis task.\n"
"Each algorithm has unique strengths and optimal use cases:\n"
"\n"
"\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\n"
"HSV COLOR RANGE\n"
"\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\n"
"What it does: Detects objects by specific color ranges using HSV color space\n"
"Strengths:\n"
"\u2022 Best for detecting brightly colored objects (orange, yellow, red clothing)\n"
"\u2022 Robust to lighting variations (HSV separates color from brigh"
                        "tness)\n"
"\u2022 Highly customizable with per-channel ranges\n"
"\u2022 Interactive color selection tools available\n"
"Weaknesses:\n"
"\u2022 Requires careful color range tuning for optimal results\n"
"\u2022 May struggle with color variations in shadows\n"
"\u2022 Not effective for colorless or camouflaged objects\n"
"Best for: Search & Rescue (colored clothing, equipment), colored vehicles, tents, colored tarps\n"
"\n"
"\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\n"
"COLOR RANGE (RGB)\n"
"\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550"
                        "\u2550\u2550\u2550\u2550\u2550\u2550\u2550\n"
"What it does: Detects objects by RGB color ranges\n"
"Strengths:\n"
"\u2022 Simple and intuitive RGB color specification\n"
"\u2022 Fast processing speed\n"
"\u2022 Good for basic color-based detection\n"
"Weaknesses:\n"
"\u2022 More sensitive to lighting changes than HSV\n"
"\u2022 RGB channels mix color and brightness information\n"
"\u2022 Less flexible than HSV for complex color variations\n"
"Best for: Controlled lighting situations, quick basic color detection, simple scenarios\n"
"\n"
"\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\n"
"RX ANOMALY\n"
"\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550"
                        "\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\n"
"What it does: Statistical anomaly detection - finds pixels that are unusual compared to background\n"
"Strengths:\n"
"\u2022 Detects objects that don't match the background (no target sample needed)\n"
"\u2022 Excellent for finding camouflaged or partially hidden objects\n"
"\u2022 Works across all image types (RGB, thermal, multispectral)\n"
"\u2022 Automatically adapts to scene characteristics\n"
"\u2022 Good for detecting subtle differences\n"
"Weaknesses:\n"
"\u2022 May detect natural anomalies (rocks, vegetation changes)\n"
"\u2022 Requires tuning sensitivity to balance detection vs false positives\n"
"\u2022 Higher segment counts significantly increase processing time\n"
"\u2022 Less effective in highly varied/cluttered backgrounds\n"
"Best for: Missing person searches (human among vegetation), camouflaged objects, unknown targets, anything unusual in "
                        "the scene\n"
"\n"
"\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\n"
"THERMAL ANOMALY\n"
"\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\n"
"What it does: Detects temperature anomalies in thermal imagery (hot/cold spots)\n"
"Strengths:\n"
"\u2022 Finds temperature outliers automatically (no specific temp needed)\n"
"\u2022 Excellent for detecting heat sources (people, animals, fires)\n"
"\u2022 Works day or night with thermal cameras\n"
"\u2022 Detects through light vegetation\n"
"\u2022 Adjustable f"
                        "or hot, cold, or both types of anomalies\n"
"Weaknesses:\n"
"\u2022 Requires thermal (FLIR) imagery\n"
"\u2022 May detect sun-heated objects (rocks, vehicles)\n"
"\u2022 Temperature gradients can cause false positives\n"
"\u2022 Affected by ambient temperature and weather\n"
"Best for: Night searches, detecting people/animals by body heat, finding heat sources, cold spot detection\n"
"\n"
"\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\n"
"THERMAL RANGE\n"
"\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550"
                        "\n"
"What it does: Temperature-based detection within a specific temperature range\n"
"Strengths:\n"
"\u2022 Precise temperature-based detection\n"
"\u2022 Excellent for finding humans (body temp ~35-40\u00b0C / 95-104\u00b0F)\n"
"\u2022 Filters out non-target temperatures effectively\n"
"\u2022 Works day or night with thermal cameras\n"
"\u2022 Very reliable when target temperature is known\n"
"Weaknesses:\n"
"\u2022 Requires thermal (FLIR) imagery with temperature data\n"
"\u2022 Must know target temperature range in advance\n"
"\u2022 Ambient conditions affect target temperature\n"
"\u2022 May miss targets in extreme weather (hypothermia cases)\n"
"Best for: Human detection (known body temp), specific temperature targets, fire detection (high temp range)\n"
"\n"
"\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550"
                        "\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\n"
"MATCHED FILTER\n"
"\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\n"
"What it does: Target-based detection using spectral signature matching\n"
"Strengths:\n"
"\u2022 Very precise when you have a target sample\n"
"\u2022 Uses spectral/color \"signature\" of target for matching\n"
"\u2022 Reduces false positives by matching known target characteristics\n"
"\u2022 Good for detecting specific object types\n"
"Weaknesses:\n"
"\u2022 Requires a reference image or color sample of the target\n"
"\u2022 Less effective if target appearance varies significantly\n"
"\u2022 Lighting differences can affect matching accuracy\n"
"\u2022 Not suitable for unknown targets\n"
"Best for: Finding specific known object"
                        "s (specific vehicle color, specific clothing), when you have a target sample to match\n"
"\n"
"\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\n"
"MR MAP (Multi-Resolution Map)\n"
"\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\n"
"What it does: Multi-resolution feature detection at various spatial scales\n"
"Strengths:\n"
"\u2022 Detects features at multiple scales simultaneously\n"
"\u2022 Good for finding objects of varying sizes\n"
"\u2022 Effective for complex scene analysis\n"
"\u2022 Can detect"
                        " both large and small features in one pass\n"
"Weaknesses:\n"
"\u2022 More computationally intensive\n"
"\u2022 Requires careful parameter tuning\n"
"\u2022 Higher segment counts significantly increase processing time\n"
"\u2022 May produce more false positives requiring filtering\n"
"Best for: Complex scenes with varying object sizes, when target size is unknown, general feature mapping\n"
"\n"
"\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\n"
"AI PERSON DETECTOR\n"
"\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550"
                        "\u2550\u2550\n"
"What it does: Deep learning AI model trained specifically to detect people\n"
"Strengths:\n"
"\u2022 Extremely accurate for detecting people in various poses\n"
"\u2022 Works with partial visibility and varied clothing\n"
"\u2022 No color/temperature requirements - works on regular RGB images\n"
"\u2022 Trained on millions of images for robust detection\n"
"\u2022 Detects people in complex backgrounds\n"
"\u2022 Minimal parameter tuning needed\n"
"Weaknesses:\n"
"\u2022 Only detects people (not vehicles, equipment, etc.)\n"
"\u2022 Computationally intensive - slower processing\n"
"\u2022 Requires adequate image resolution\n"
"\u2022 May struggle with very distant/small people\n"
"\u2022 Less effective with heavy occlusion\n"
"Best for: Search & Rescue operations (missing persons), people counting, situations where only human detection is needed\n"
"\n"
"\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550"
                        "\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\n"
"ALGORITHM SELECTION GUIDE\n"
"\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\n"
"\u2022 For colorful objects (bright clothing, gear): HSV Color Range\n"
"\u2022 For thermal cameras searching people: Thermal Range or Thermal Anomaly\n"
"\u2022 For camouflaged or hidden subjects: RX Anomaly\n"
"\u2022 For detecting people specifically: AI Person Detector\n"
"\u2022 When you have a target sample: Matched Filter\n"
"\u2022 For unknown targets that stand out: RX Anomaly or Thermal Anomaly\n"
"\u2022 For fastest processing: Color Range (RGB) or HSV Color Range\n"
"\u2022 For most accurate people d"
                        "etection: AI Person Detector", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.startButton.setToolTip(QCoreApplication.translate("MainWindow", u"Start processing images with the selected algorithm.\n"
"Requirements before starting:\n"
"\u2022 Input folder must be selected with valid images\n"
"\u2022 Output folder must be selected\n"
"\u2022 Algorithm must be selected\n"
"\u2022 All required algorithm parameters must be configured\n"
"Processing will:\n"
"\u2022 Analyze all images in the input folder using the selected algorithm\n"
"\u2022 Apply global filters (min/max area, K-Means, histogram normalization)\n"
"\u2022 Save results to output folder (marked images, CSV, KML files)\n"
"\u2022 Display progress and results in the output window\n"
"Click Cancel during processing to stop the analysis.", None))
#endif // QT_CONFIG(tooltip)
        self.startButton.setText(QCoreApplication.translate("MainWindow", u"Start", None))
#if QT_CONFIG(tooltip)
        self.cancelButton.setToolTip(QCoreApplication.translate("MainWindow", u"Cancel the currently running image analysis process.\n"
"Stops processing immediately and safely terminates all worker processes.\n"
"Effects of canceling:\n"
"\u2022 All running analysis processes are stopped\n"
"\u2022 Partial results are saved up to the cancellation point\n"
"\u2022 Images already processed will have output files in the output folder\n"
"\u2022 Processing can be restarted after cancellation\n"
"\u2022 Returns to the ready state\n"
"Use when you need to stop processing to adjust settings or fix issues.", None))
#endif // QT_CONFIG(tooltip)
        self.cancelButton.setText(QCoreApplication.translate("MainWindow", u" Cancel", None))
        self.cancelButton.setProperty(u"iconName", QCoreApplication.translate("MainWindow", u"cancel.png", None))
#if QT_CONFIG(tooltip)
        self.viewResultsButton.setToolTip(QCoreApplication.translate("MainWindow", u"Open the Results Viewer to review detection results.\n"
"Available after processing completes successfully.\n"
"The Results Viewer provides:\n"
"\u2022 Interactive image browsing with detected objects highlighted\n"
"\u2022 Side-by-side comparison of original and processed images\n"
"\u2022 Navigation through all processed images\n"
"\u2022 AOI (Area of Interest) details and metadata\n"
"\u2022 GPS coordinates for detected objects\n"
"\u2022 Export options for selected detections\n"
"\u2022 Zoom and pan capabilities\n"
"\u2022 Filtering and sorting of detection results\n"
"Use to review, verify, and export analysis results.", None))
#endif // QT_CONFIG(tooltip)
        self.viewResultsButton.setText(QCoreApplication.translate("MainWindow", u" View Results", None))
        self.viewResultsButton.setProperty(u"iconName", QCoreApplication.translate("MainWindow", u"search", None))
#if QT_CONFIG(tooltip)
        self.outputWindow.setToolTip(QCoreApplication.translate("MainWindow", u"Processing status and output log window.\n"
"Displays real-time information during image analysis:\n"
"\u2022 Current processing status and progress\n"
"\u2022 Images being analyzed with filenames\n"
"\u2022 Detection counts per image\n"
"\u2022 Processing errors and warnings\n"
"\u2022 Completion status and summary statistics\n"
"\u2022 Total processing time and performance metrics\n"
"\u2022 File save locations and output paths\n"
"The window auto-scrolls to show the latest output.\n"
"Use to monitor processing progress and troubleshoot issues.", None))
#endif // QT_CONFIG(tooltip)
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"Menu", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi

