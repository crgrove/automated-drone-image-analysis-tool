# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'StreamingGuide.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSlider,
    QSpacerItem, QSpinBox, QStackedWidget, QTextEdit,
    QToolButton, QVBoxLayout, QWidget)

class Ui_StreamingGuide(object):
    def setupUi(self, StreamingGuide):
        if not StreamingGuide.objectName():
            StreamingGuide.setObjectName(u"StreamingGuide")
        StreamingGuide.resize(760, 560)
        self.verticalLayout = QVBoxLayout(StreamingGuide)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.stackedWidget = QStackedWidget(StreamingGuide)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.pageSource = QWidget()
        self.pageSource.setObjectName(u"pageSource")
        self.verticalLayout_source = QVBoxLayout(self.pageSource)
        self.verticalLayout_source.setSpacing(10)
        self.verticalLayout_source.setObjectName(u"verticalLayout_source")
        self.verticalLayout_source.setContentsMargins(-1, 5, -1, -1)
        self.labelPageSourceTitle = QLabel(self.pageSource)
        self.labelPageSourceTitle.setObjectName(u"labelPageSourceTitle")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.labelPageSourceTitle.setFont(font)

        self.verticalLayout_source.addWidget(self.labelPageSourceTitle)

        self.line_source = QFrame(self.pageSource)
        self.line_source.setObjectName(u"line_source")
        self.line_source.setFrameShape(QFrame.Shape.HLine)
        self.line_source.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_source.addWidget(self.line_source)

        self.verticalLayout_streamSelection = QVBoxLayout()
        self.verticalLayout_streamSelection.setSpacing(15)
        self.verticalLayout_streamSelection.setObjectName(u"verticalLayout_streamSelection")
        self.streamTypeButtonWidget = QWidget(self.pageSource)
        self.streamTypeButtonWidget.setObjectName(u"streamTypeButtonWidget")
        self.horizontalLayout_streamButtons = QHBoxLayout(self.streamTypeButtonWidget)
        self.horizontalLayout_streamButtons.setSpacing(24)
        self.horizontalLayout_streamButtons.setObjectName(u"horizontalLayout_streamButtons")
        self.horizontalLayout_streamButtons.setContentsMargins(0, -1, 0, -1)
        self.streamButtonsLeftSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_streamButtons.addItem(self.streamButtonsLeftSpacer)

        self.fileButton = QToolButton(self.streamTypeButtonWidget)
        self.fileButton.setObjectName(u"fileButton")
        self.fileButton.setMinimumSize(QSize(150, 150))
        self.fileButton.setMaximumSize(QSize(180, 180))
        font1 = QFont()
        font1.setPointSize(12)
        self.fileButton.setFont(font1)
        self.fileButton.setStyleSheet(u"QToolButton { border: 3px solid palette(mid); border-radius: 12px; padding: 10px; }\n"
"QToolButton:checked { border-color: #4CAF50; background-color: #1b2d44; }")
        self.fileButton.setIconSize(QSize(72, 72))
        self.fileButton.setCheckable(True)
        self.fileButton.setChecked(True)
        self.fileButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.horizontalLayout_streamButtons.addWidget(self.fileButton)

        self.hdmiButton = QToolButton(self.streamTypeButtonWidget)
        self.hdmiButton.setObjectName(u"hdmiButton")
        self.hdmiButton.setMinimumSize(QSize(150, 150))
        self.hdmiButton.setMaximumSize(QSize(180, 180))
        self.hdmiButton.setFont(font1)
        self.hdmiButton.setStyleSheet(u"QToolButton { border: 3px solid palette(mid); border-radius: 12px; padding: 10px; }\n"
"QToolButton:checked { border-color: #4CAF50; background-color: #1b2d44; }")
        self.hdmiButton.setIconSize(QSize(72, 72))
        self.hdmiButton.setCheckable(True)
        self.hdmiButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.horizontalLayout_streamButtons.addWidget(self.hdmiButton)

        self.rtmpButton = QToolButton(self.streamTypeButtonWidget)
        self.rtmpButton.setObjectName(u"rtmpButton")
        self.rtmpButton.setMinimumSize(QSize(150, 150))
        self.rtmpButton.setMaximumSize(QSize(180, 180))
        self.rtmpButton.setFont(font1)
        self.rtmpButton.setStyleSheet(u"QToolButton { border: 3px solid palette(mid); border-radius: 12px; padding: 10px; }\n"
"QToolButton:checked { border-color: #4CAF50; background-color: #1b2d44; }")
        self.rtmpButton.setIconSize(QSize(72, 72))
        self.rtmpButton.setCheckable(True)
        self.rtmpButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.horizontalLayout_streamButtons.addWidget(self.rtmpButton)

        self.streamButtonsRightSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_streamButtons.addItem(self.streamButtonsRightSpacer)


        self.verticalLayout_streamSelection.addWidget(self.streamTypeButtonWidget)

        self.labelFileDescription = QLabel(self.pageSource)
        self.labelFileDescription.setObjectName(u"labelFileDescription")
        font2 = QFont()
        font2.setPointSize(11)
        self.labelFileDescription.setFont(font2)
        self.labelFileDescription.setWordWrap(True)

        self.verticalLayout_streamSelection.addWidget(self.labelFileDescription)

        self.labelHdmiDescription = QLabel(self.pageSource)
        self.labelHdmiDescription.setObjectName(u"labelHdmiDescription")
        self.labelHdmiDescription.setFont(font2)
        self.labelHdmiDescription.setWordWrap(True)

        self.verticalLayout_streamSelection.addWidget(self.labelHdmiDescription)

        self.labelRtmpDescription = QLabel(self.pageSource)
        self.labelRtmpDescription.setObjectName(u"labelRtmpDescription")
        self.labelRtmpDescription.setFont(font2)
        self.labelRtmpDescription.setWordWrap(True)

        self.verticalLayout_streamSelection.addWidget(self.labelRtmpDescription)

        self.verticalSpacer_source = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_streamSelection.addItem(self.verticalSpacer_source)


        self.verticalLayout_source.addLayout(self.verticalLayout_streamSelection)

        self.stackedWidget.addWidget(self.pageSource)
        self.pageConnection = QWidget()
        self.pageConnection.setObjectName(u"pageConnection")
        self.verticalLayout_connection = QVBoxLayout(self.pageConnection)
        self.verticalLayout_connection.setSpacing(10)
        self.verticalLayout_connection.setObjectName(u"verticalLayout_connection")
        self.verticalLayout_connection.setContentsMargins(-1, 5, -1, -1)
        self.labelPageConnectionTitle = QLabel(self.pageConnection)
        self.labelPageConnectionTitle.setObjectName(u"labelPageConnectionTitle")
        self.labelPageConnectionTitle.setFont(font)

        self.verticalLayout_connection.addWidget(self.labelPageConnectionTitle)

        self.line_connection = QFrame(self.pageConnection)
        self.line_connection.setObjectName(u"line_connection")
        self.line_connection.setFrameShape(QFrame.Shape.HLine)
        self.line_connection.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_connection.addWidget(self.line_connection)

        self.labelConnectionInstructions = QLabel(self.pageConnection)
        self.labelConnectionInstructions.setObjectName(u"labelConnectionInstructions")
        self.labelConnectionInstructions.setFont(font1)
        self.labelConnectionInstructions.setWordWrap(True)

        self.verticalLayout_connection.addWidget(self.labelConnectionInstructions)

        self.gridLayout_connection = QGridLayout()
        self.gridLayout_connection.setObjectName(u"gridLayout_connection")
        self.labelStreamUrl = QLabel(self.pageConnection)
        self.labelStreamUrl.setObjectName(u"labelStreamUrl")
        self.labelStreamUrl.setFont(font1)

        self.gridLayout_connection.addWidget(self.labelStreamUrl, 0, 0, 1, 1)

        self.horizontalLayout_url = QHBoxLayout()
        self.horizontalLayout_url.setObjectName(u"horizontalLayout_url")
        self.streamUrlLineEdit = QLineEdit(self.pageConnection)
        self.streamUrlLineEdit.setObjectName(u"streamUrlLineEdit")

        self.horizontalLayout_url.addWidget(self.streamUrlLineEdit)

        self.browseButton = QPushButton(self.pageConnection)
        self.browseButton.setObjectName(u"browseButton")
        self.browseButton.setFont(font2)

        self.horizontalLayout_url.addWidget(self.browseButton)


        self.gridLayout_connection.addLayout(self.horizontalLayout_url, 0, 1, 1, 1)

        self.labelAutoConnect = QLabel(self.pageConnection)
        self.labelAutoConnect.setObjectName(u"labelAutoConnect")
        self.labelAutoConnect.setFont(font1)

        self.gridLayout_connection.addWidget(self.labelAutoConnect, 1, 0, 1, 1)

        self.autoConnectCheckBox = QCheckBox(self.pageConnection)
        self.autoConnectCheckBox.setObjectName(u"autoConnectCheckBox")
        self.autoConnectCheckBox.setFont(font2)

        self.gridLayout_connection.addWidget(self.autoConnectCheckBox, 1, 1, 1, 1)

        self.labelHdmiDevices = QLabel(self.pageConnection)
        self.labelHdmiDevices.setObjectName(u"labelHdmiDevices")
        self.labelHdmiDevices.setFont(font1)

        self.gridLayout_connection.addWidget(self.labelHdmiDevices, 2, 0, 1, 1)

        self.horizontalLayout_hdmiDevices = QHBoxLayout()
        self.horizontalLayout_hdmiDevices.setObjectName(u"horizontalLayout_hdmiDevices")
        self.deviceComboBox = QComboBox(self.pageConnection)
        self.deviceComboBox.setObjectName(u"deviceComboBox")
        self.deviceComboBox.setEnabled(True)

        self.horizontalLayout_hdmiDevices.addWidget(self.deviceComboBox)

        self.scanDevicesButton = QPushButton(self.pageConnection)
        self.scanDevicesButton.setObjectName(u"scanDevicesButton")
        self.scanDevicesButton.setFont(font2)

        self.horizontalLayout_hdmiDevices.addWidget(self.scanDevicesButton)


        self.gridLayout_connection.addLayout(self.horizontalLayout_hdmiDevices, 2, 1, 1, 1)

        self.verticalSpacer_resolution = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_connection.addItem(self.verticalSpacer_resolution, 3, 0, 1, 1)

        self.verticalSpacer_resolution2 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_connection.addItem(self.verticalSpacer_resolution2, 3, 1, 1, 1)

        self.labelProcessingResolution = QLabel(self.pageConnection)
        self.labelProcessingResolution.setObjectName(u"labelProcessingResolution")
        self.labelProcessingResolution.setFont(font1)

        self.gridLayout_connection.addWidget(self.labelProcessingResolution, 4, 0, 1, 1)

        self.resolutionSliderWidget = QWidget(self.pageConnection)
        self.resolutionSliderWidget.setObjectName(u"resolutionSliderWidget")
        self.resolutionSliderWidget.setMinimumSize(QSize(400, 60))

        self.gridLayout_connection.addWidget(self.resolutionSliderWidget, 4, 1, 1, 1)


        self.verticalLayout_connection.addLayout(self.gridLayout_connection)

        self.verticalSpacer_connection = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_connection.addItem(self.verticalSpacer_connection)

        self.stackedWidget.addWidget(self.pageConnection)
        self.pageCapture = QWidget()
        self.pageCapture.setObjectName(u"pageCapture")
        self.verticalLayout_capture = QVBoxLayout(self.pageCapture)
        self.verticalLayout_capture.setObjectName(u"verticalLayout_capture")
        self.verticalLayout_capture.setContentsMargins(-1, 5, -1, -1)
        self.labelPageCaptureTitle = QLabel(self.pageCapture)
        self.labelPageCaptureTitle.setObjectName(u"labelPageCaptureTitle")
        self.labelPageCaptureTitle.setFont(font)

        self.verticalLayout_capture.addWidget(self.labelPageCaptureTitle)

        self.line_capture = QFrame(self.pageCapture)
        self.line_capture.setObjectName(u"line_capture")
        self.line_capture.setFrameShape(QFrame.Shape.HLine)
        self.line_capture.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_capture.addWidget(self.line_capture)

        self.widgetDrone = QWidget(self.pageCapture)
        self.widgetDrone.setObjectName(u"widgetDrone")
        self.verticalLayout_drone = QVBoxLayout(self.widgetDrone)
        self.verticalLayout_drone.setObjectName(u"verticalLayout_drone")
        self.labelDrone = QLabel(self.widgetDrone)
        self.labelDrone.setObjectName(u"labelDrone")
        self.labelDrone.setFont(font1)

        self.verticalLayout_drone.addWidget(self.labelDrone)

        self.droneComboBox = QComboBox(self.widgetDrone)
        self.droneComboBox.setObjectName(u"droneComboBox")
        self.droneComboBox.setFont(font2)
        self.droneComboBox.setEditable(False)

        self.verticalLayout_drone.addWidget(self.droneComboBox)


        self.verticalLayout_capture.addWidget(self.widgetDrone)

        self.widgetAltitude = QWidget(self.pageCapture)
        self.widgetAltitude.setObjectName(u"widgetAltitude")
        self.verticalLayout_altitude = QVBoxLayout(self.widgetAltitude)
        self.verticalLayout_altitude.setObjectName(u"verticalLayout_altitude")
        self.labelAltitude = QLabel(self.widgetAltitude)
        self.labelAltitude.setObjectName(u"labelAltitude")
        self.labelAltitude.setFont(font1)

        self.verticalLayout_altitude.addWidget(self.labelAltitude)

        self.horizontalLayout_altitude = QHBoxLayout()
        self.horizontalLayout_altitude.setObjectName(u"horizontalLayout_altitude")
        self.altitudeSlider = QSlider(self.widgetAltitude)
        self.altitudeSlider.setObjectName(u"altitudeSlider")
        self.altitudeSlider.setLayoutDirection(Qt.LeftToRight)
        self.altitudeSlider.setMinimum(0)
        self.altitudeSlider.setMaximum(600)
        self.altitudeSlider.setValue(100)
        self.altitudeSlider.setOrientation(Qt.Horizontal)

        self.horizontalLayout_altitude.addWidget(self.altitudeSlider)

        self.altitudeSpinBox = QSpinBox(self.widgetAltitude)
        self.altitudeSpinBox.setObjectName(u"altitudeSpinBox")
        self.altitudeSpinBox.setFont(font2)
        self.altitudeSpinBox.setMinimum(0)
        self.altitudeSpinBox.setMaximum(1000)
        self.altitudeSpinBox.setValue(100)

        self.horizontalLayout_altitude.addWidget(self.altitudeSpinBox)

        self.altitudeUnitComboBox = QComboBox(self.widgetAltitude)
        self.altitudeUnitComboBox.addItem("")
        self.altitudeUnitComboBox.addItem("")
        self.altitudeUnitComboBox.setObjectName(u"altitudeUnitComboBox")
        self.altitudeUnitComboBox.setFont(font2)

        self.horizontalLayout_altitude.addWidget(self.altitudeUnitComboBox)


        self.verticalLayout_altitude.addLayout(self.horizontalLayout_altitude)


        self.verticalLayout_capture.addWidget(self.widgetAltitude)

        self.verticalSpacer_capture1 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_capture.addItem(self.verticalSpacer_capture1)

        self.gsdWidget = QWidget(self.pageCapture)
        self.gsdWidget.setObjectName(u"gsdWidget")
        self.verticalLayout_gsd = QVBoxLayout(self.gsdWidget)
        self.verticalLayout_gsd.setObjectName(u"verticalLayout_gsd")
        self.labelGSDTitle = QLabel(self.gsdWidget)
        self.labelGSDTitle.setObjectName(u"labelGSDTitle")
        font3 = QFont()
        font3.setPointSize(12)
        font3.setBold(True)
        self.labelGSDTitle.setFont(font3)

        self.verticalLayout_gsd.addWidget(self.labelGSDTitle)

        self.gsdTextEdit = QTextEdit(self.gsdWidget)
        self.gsdTextEdit.setObjectName(u"gsdTextEdit")
        self.gsdTextEdit.setMaximumSize(QSize(16777215, 100))
        self.gsdTextEdit.setFont(font2)
        self.gsdTextEdit.setReadOnly(True)

        self.verticalLayout_gsd.addWidget(self.gsdTextEdit)


        self.verticalLayout_capture.addWidget(self.gsdWidget)

        self.verticalSpacer_capture2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_capture.addItem(self.verticalSpacer_capture2)

        self.stackedWidget.addWidget(self.pageCapture)
        self.pageTargetSize = QWidget()
        self.pageTargetSize.setObjectName(u"pageTargetSize")
        self.verticalLayout_targetSize = QVBoxLayout(self.pageTargetSize)
        self.verticalLayout_targetSize.setObjectName(u"verticalLayout_targetSize")
        self.verticalLayout_targetSize.setContentsMargins(-1, 5, -1, -1)
        self.labelPageTargetSizeTitle = QLabel(self.pageTargetSize)
        self.labelPageTargetSizeTitle.setObjectName(u"labelPageTargetSizeTitle")
        self.labelPageTargetSizeTitle.setFont(font)
        self.labelPageTargetSizeTitle.setWordWrap(True)

        self.verticalLayout_targetSize.addWidget(self.labelPageTargetSizeTitle)

        self.line_targetSize = QFrame(self.pageTargetSize)
        self.line_targetSize.setObjectName(u"line_targetSize")
        self.line_targetSize.setFrameShape(QFrame.Shape.HLine)
        self.line_targetSize.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_targetSize.addWidget(self.line_targetSize)

        self.widgetObjectSize = QWidget(self.pageTargetSize)
        self.widgetObjectSize.setObjectName(u"widgetObjectSize")
        self.verticalLayout_objectSize = QVBoxLayout(self.widgetObjectSize)
        self.verticalLayout_objectSize.setObjectName(u"verticalLayout_objectSize")
        self.labelObjectSize = QLabel(self.widgetObjectSize)
        self.labelObjectSize.setObjectName(u"labelObjectSize")
        self.labelObjectSize.setFont(font1)

        self.verticalLayout_objectSize.addWidget(self.labelObjectSize)

        self.objectSizeRangeSliderWidget = QWidget(self.widgetObjectSize)
        self.objectSizeRangeSliderWidget.setObjectName(u"objectSizeRangeSliderWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.objectSizeRangeSliderWidget.sizePolicy().hasHeightForWidth())
        self.objectSizeRangeSliderWidget.setSizePolicy(sizePolicy)
        self.objectSizeRangeSliderWidget.setMinimumSize(QSize(800, 150))

        self.verticalLayout_objectSize.addWidget(self.objectSizeRangeSliderWidget)


        self.verticalLayout_targetSize.addWidget(self.widgetObjectSize)

        self.labelExamples = QLabel(self.pageTargetSize)
        self.labelExamples.setObjectName(u"labelExamples")
        self.labelExamples.setFont(font1)
        self.labelExamples.setWordWrap(True)

        self.verticalLayout_targetSize.addWidget(self.labelExamples)

        self.verticalSpacer_targetSize = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_targetSize.addItem(self.verticalSpacer_targetSize)

        self.stackedWidget.addWidget(self.pageTargetSize)
        self.pageAlgorithm = QWidget()
        self.pageAlgorithm.setObjectName(u"pageAlgorithm")
        self.verticalLayout_algorithm = QVBoxLayout(self.pageAlgorithm)
        self.verticalLayout_algorithm.setSpacing(10)
        self.verticalLayout_algorithm.setObjectName(u"verticalLayout_algorithm")
        self.verticalLayout_algorithm.setContentsMargins(-1, 5, -1, -1)
        self.labelPageAlgorithmTitle = QLabel(self.pageAlgorithm)
        self.labelPageAlgorithmTitle.setObjectName(u"labelPageAlgorithmTitle")
        self.labelPageAlgorithmTitle.setFont(font)

        self.verticalLayout_algorithm.addWidget(self.labelPageAlgorithmTitle)

        self.line_algorithm = QFrame(self.pageAlgorithm)
        self.line_algorithm.setObjectName(u"line_algorithm")
        self.line_algorithm.setFrameShape(QFrame.Shape.HLine)
        self.line_algorithm.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_algorithm.addWidget(self.line_algorithm)

        self.algorithmWidget = QWidget(self.pageAlgorithm)
        self.algorithmWidget.setObjectName(u"algorithmWidget")
        self.verticalLayout_algorithmDecision = QVBoxLayout(self.algorithmWidget)
        self.verticalLayout_algorithmDecision.setObjectName(u"verticalLayout_algorithmDecision")
        self.labelCurrentQuestion = QLabel(self.algorithmWidget)
        self.labelCurrentQuestion.setObjectName(u"labelCurrentQuestion")
        font4 = QFont()
        font4.setPointSize(14)
        self.labelCurrentQuestion.setFont(font4)
        self.labelCurrentQuestion.setAlignment(Qt.AlignCenter)

        self.verticalLayout_algorithmDecision.addWidget(self.labelCurrentQuestion)

        self.horizontalLayout_algorithmButtons = QHBoxLayout()
        self.horizontalLayout_algorithmButtons.setObjectName(u"horizontalLayout_algorithmButtons")
        self.horizontalLayout_algorithmButtons.setContentsMargins(-1, 10, -1, 10)
        self.horizontalSpacer_algorithm = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_algorithmButtons.addItem(self.horizontalSpacer_algorithm)

        self.buttonYes = QPushButton(self.algorithmWidget)
        self.buttonYes.setObjectName(u"buttonYes")
        self.buttonYes.setMinimumSize(QSize(100, 40))
        self.buttonYes.setFont(font1)

        self.horizontalLayout_algorithmButtons.addWidget(self.buttonYes)

        self.horizontalSpacer_algorithm2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_algorithmButtons.addItem(self.horizontalSpacer_algorithm2)

        self.buttonNo = QPushButton(self.algorithmWidget)
        self.buttonNo.setObjectName(u"buttonNo")
        self.buttonNo.setMinimumSize(QSize(100, 40))
        self.buttonNo.setFont(font1)

        self.horizontalLayout_algorithmButtons.addWidget(self.buttonNo)

        self.horizontalSpacer_algorithm3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_algorithmButtons.addItem(self.horizontalSpacer_algorithm3)


        self.verticalLayout_algorithmDecision.addLayout(self.horizontalLayout_algorithmButtons)

        self.labelAlgorithmResult = QLabel(self.algorithmWidget)
        self.labelAlgorithmResult.setObjectName(u"labelAlgorithmResult")
        font5 = QFont()
        font5.setPointSize(14)
        font5.setBold(True)
        self.labelAlgorithmResult.setFont(font5)
        self.labelAlgorithmResult.setVisible(False)
        self.labelAlgorithmResult.setAlignment(Qt.AlignCenter)

        self.verticalLayout_algorithmDecision.addWidget(self.labelAlgorithmResult)

        self.horizontalLayout_reset = QHBoxLayout()
        self.horizontalLayout_reset.setObjectName(u"horizontalLayout_reset")
        self.horizontalLayout_reset.setContentsMargins(-1, 25, -1, 9)
        self.horizontalSpacer_reset = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_reset.addItem(self.horizontalSpacer_reset)

        self.resetAlgorithmButton = QPushButton(self.algorithmWidget)
        self.resetAlgorithmButton.setObjectName(u"resetAlgorithmButton")
        self.resetAlgorithmButton.setFont(font2)

        self.horizontalLayout_reset.addWidget(self.resetAlgorithmButton)

        self.horizontalSpacer_reset2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_reset.addItem(self.horizontalSpacer_reset2)


        self.verticalLayout_algorithmDecision.addLayout(self.horizontalLayout_reset)

        self.verticalSpacer_algorithmDecision = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_algorithmDecision.addItem(self.verticalSpacer_algorithmDecision)


        self.verticalLayout_algorithm.addWidget(self.algorithmWidget)

        self.verticalSpacer_algorithm = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_algorithm.addItem(self.verticalSpacer_algorithm)

        self.stackedWidget.addWidget(self.pageAlgorithm)
        self.pageAlgorithmParameters = QWidget()
        self.pageAlgorithmParameters.setObjectName(u"pageAlgorithmParameters")
        self.verticalLayout_algorithmParameters = QVBoxLayout(self.pageAlgorithmParameters)
        self.verticalLayout_algorithmParameters.setObjectName(u"verticalLayout_algorithmParameters")
        self.verticalLayout_algorithmParameters.setContentsMargins(-1, 5, -1, -1)
        self.labelPageAlgorithmParametersTitle = QLabel(self.pageAlgorithmParameters)
        self.labelPageAlgorithmParametersTitle.setObjectName(u"labelPageAlgorithmParametersTitle")
        self.labelPageAlgorithmParametersTitle.setFont(font)

        self.verticalLayout_algorithmParameters.addWidget(self.labelPageAlgorithmParametersTitle)

        self.line_algorithmParameters = QFrame(self.pageAlgorithmParameters)
        self.line_algorithmParameters.setObjectName(u"line_algorithmParameters")
        self.line_algorithmParameters.setFrameShape(QFrame.Shape.HLine)
        self.line_algorithmParameters.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_algorithmParameters.addWidget(self.line_algorithmParameters)

        self.algorithmParametersContainer = QWidget(self.pageAlgorithmParameters)
        self.algorithmParametersContainer.setObjectName(u"algorithmParametersContainer")

        self.verticalLayout_algorithmParameters.addWidget(self.algorithmParametersContainer)

        self.stackedWidget.addWidget(self.pageAlgorithmParameters)

        self.verticalLayout.addWidget(self.stackedWidget)

        self.buttonWidget = QWidget(StreamingGuide)
        self.buttonWidget.setObjectName(u"buttonWidget")
        self.buttonWidget.setMinimumSize(QSize(0, 50))
        self.horizontalLayout_buttons = QHBoxLayout(self.buttonWidget)
        self.horizontalLayout_buttons.setObjectName(u"horizontalLayout_buttons")
        self.cancelButton = QPushButton(self.buttonWidget)
        self.cancelButton.setObjectName(u"cancelButton")
        self.cancelButton.setFont(font2)

        self.horizontalLayout_buttons.addWidget(self.cancelButton)

        self.skipGuideCheckBox = QCheckBox(self.buttonWidget)
        self.skipGuideCheckBox.setObjectName(u"skipGuideCheckBox")
        font6 = QFont()
        font6.setPointSize(10)
        self.skipGuideCheckBox.setFont(font6)

        self.horizontalLayout_buttons.addWidget(self.skipGuideCheckBox)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_buttons.addItem(self.horizontalSpacer)

        self.backButton = QPushButton(self.buttonWidget)
        self.backButton.setObjectName(u"backButton")
        self.backButton.setFont(font2)

        self.horizontalLayout_buttons.addWidget(self.backButton)

        self.continueButton = QPushButton(self.buttonWidget)
        self.continueButton.setObjectName(u"continueButton")
        self.continueButton.setFont(font2)

        self.horizontalLayout_buttons.addWidget(self.continueButton)


        self.verticalLayout.addWidget(self.buttonWidget)


        self.retranslateUi(StreamingGuide)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(StreamingGuide)
    # setupUi

    def retranslateUi(self, StreamingGuide):
        StreamingGuide.setWindowTitle(QCoreApplication.translate("StreamingGuide", u"Streaming Setup Guide", None))
        self.labelPageSourceTitle.setText(QCoreApplication.translate("StreamingGuide", u"Connect to Your Stream", None))
#if QT_CONFIG(tooltip)
        self.fileButton.setToolTip(QCoreApplication.translate("StreamingGuide", u"Pre-recorded video file with playback controls", None))
#endif // QT_CONFIG(tooltip)
        self.fileButton.setText(QCoreApplication.translate("StreamingGuide", u"File", None))
#if QT_CONFIG(tooltip)
        self.hdmiButton.setToolTip(QCoreApplication.translate("StreamingGuide", u"Live HDMI capture device (enter device index)", None))
#endif // QT_CONFIG(tooltip)
        self.hdmiButton.setText(QCoreApplication.translate("StreamingGuide", u"HDMI", None))
#if QT_CONFIG(tooltip)
        self.rtmpButton.setToolTip(QCoreApplication.translate("StreamingGuide", u"Network stream via RTMP URL", None))
#endif // QT_CONFIG(tooltip)
        self.rtmpButton.setText(QCoreApplication.translate("StreamingGuide", u"RTMP", None))
        self.labelFileDescription.setText(QCoreApplication.translate("StreamingGuide", u"File: Use local video files (MP4, MOV, etc.) with timeline controls.", None))
        self.labelHdmiDescription.setText(QCoreApplication.translate("StreamingGuide", u"HDMI: Connect to a live HDMI capture device.", None))
        self.labelRtmpDescription.setText(QCoreApplication.translate("StreamingGuide", u"RTMP: Connect to a live network stream (rtmp://server:port/app/key).", None))
        self.labelPageConnectionTitle.setText(QCoreApplication.translate("StreamingGuide", u"Connection Details", None))
        self.labelConnectionInstructions.setText(QCoreApplication.translate("StreamingGuide", u"Provide the path or URL for your selected stream type. You can optionally auto-connect when the guide is finished.", None))
        self.labelStreamUrl.setText(QCoreApplication.translate("StreamingGuide", u"Stream URL / Path:", None))
        self.streamUrlLineEdit.setPlaceholderText(QCoreApplication.translate("StreamingGuide", u"Click Browse to select a file or enter a URL...", None))
        self.browseButton.setText(QCoreApplication.translate("StreamingGuide", u"Browse...", None))
        self.labelAutoConnect.setText(QCoreApplication.translate("StreamingGuide", u"Auto Connect:", None))
        self.autoConnectCheckBox.setText(QCoreApplication.translate("StreamingGuide", u"Connect as soon as the guide finishes", None))
        self.labelHdmiDevices.setText(QCoreApplication.translate("StreamingGuide", u"Capture Devices:", None))
        self.scanDevicesButton.setText(QCoreApplication.translate("StreamingGuide", u"Scan...", None))
        self.labelProcessingResolution.setText(QCoreApplication.translate("StreamingGuide", u"Processing Resolution:", None))
        self.labelPageCaptureTitle.setText(QCoreApplication.translate("StreamingGuide", u"Image Capture Information", None))
        self.labelDrone.setText(QCoreApplication.translate("StreamingGuide", u"What drone/camera was used to capture images?", None))
        self.labelAltitude.setText(QCoreApplication.translate("StreamingGuide", u"At what above ground level (AGL) altitude was the drone flying?", None))
        self.altitudeUnitComboBox.setItemText(0, QCoreApplication.translate("StreamingGuide", u"ft", None))
        self.altitudeUnitComboBox.setItemText(1, QCoreApplication.translate("StreamingGuide", u"m", None))

        self.labelGSDTitle.setText(QCoreApplication.translate("StreamingGuide", u"Estimated Ground Sampling Distance (GSD):", None))
        self.gsdTextEdit.setHtml(QCoreApplication.translate("StreamingGuide", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'MS Shell Dlg 2'; font-size:9pt;\"><br /></p></body></html>", None))
        self.gsdTextEdit.setPlaceholderText(QCoreApplication.translate("StreamingGuide", u"--", None))
        self.labelPageTargetSizeTitle.setText(QCoreApplication.translate("StreamingGuide", u"Search Target Size", None))
        self.labelObjectSize.setText(QCoreApplication.translate("StreamingGuide", u"Approximately how large are the objects you're wanting to identify?", None))
        self.labelExamples.setText(QCoreApplication.translate("StreamingGuide", u"<html><head/><body><p><span style=\" font-weight:700;\">More Examples:</span></p><ul><li>&nbsp;&nbsp;1 sqft \u2013 Hat, Helmet, Plastic Bag </li><li>&nbsp;&nbsp;3 sqft \u2013 Cat, Daypack </li><li>&nbsp;&nbsp;6 sqft \u2013 Large Pack, Medium Dog </li><li>&nbsp;&nbsp;12 sqft \u2013 Sleeping Bag, Large Dog </li><li>&nbsp;&nbsp;50 sqft \u2013 Small Boat, 2-Person Tent </li><li>&nbsp;&nbsp;200 sqft \u2013 Car/SUV, Small Pickup Truck, Large Tent </li><li>&nbsp;&nbsp;1000 sqft \u2013 House </li></ul></body></html>", None))
        self.labelPageAlgorithmTitle.setText(QCoreApplication.translate("StreamingGuide", u"Detection & Processing", None))
        self.labelCurrentQuestion.setText(QCoreApplication.translate("StreamingGuide", u"Are you looking for specific colors?", None))
        self.buttonYes.setText(QCoreApplication.translate("StreamingGuide", u"Yes", None))
        self.buttonNo.setText(QCoreApplication.translate("StreamingGuide", u"No", None))
        self.labelAlgorithmResult.setText("")
        self.resetAlgorithmButton.setText(QCoreApplication.translate("StreamingGuide", u"Reset", None))
        self.labelPageAlgorithmParametersTitle.setText(QCoreApplication.translate("StreamingGuide", u"Algorithm Parameters", None))
        self.cancelButton.setText(QCoreApplication.translate("StreamingGuide", u"Close", None))
        self.skipGuideCheckBox.setText(QCoreApplication.translate("StreamingGuide", u"Skip this streaming guide next time", None))
        self.backButton.setText(QCoreApplication.translate("StreamingGuide", u"Back", None))
        self.continueButton.setText(QCoreApplication.translate("StreamingGuide", u"Continue", None))
    # retranslateUi

