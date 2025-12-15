# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ImageAnalysisGuide.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
    QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QRadioButton, QSizePolicy, QSlider,
    QSpacerItem, QSpinBox, QStackedWidget, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_ImageAnalysisGuide(object):
    def setupUi(self, ImageAnalysisGuide):
        if not ImageAnalysisGuide.objectName():
            ImageAnalysisGuide.setObjectName(u"ImageAnalysisGuide")
        ImageAnalysisGuide.resize(854, 600)
        self.verticalLayout = QVBoxLayout(ImageAnalysisGuide)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, 0, -1, -1)
        self.stackedWidget = QStackedWidget(ImageAnalysisGuide)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.pageReviewOrNew = QWidget()
        self.pageReviewOrNew.setObjectName(u"pageReviewOrNew")
        self.verticalLayout_reviewOrNew = QVBoxLayout(self.pageReviewOrNew)
        self.verticalLayout_reviewOrNew.setObjectName(u"verticalLayout_reviewOrNew")
        self.verticalLayout_reviewOrNew.setContentsMargins(-1, 5, -1, -1)
        self.labelPageReviewOrNewTitle = QLabel(self.pageReviewOrNew)
        self.labelPageReviewOrNewTitle.setObjectName(u"labelPageReviewOrNewTitle")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.labelPageReviewOrNewTitle.setFont(font)

        self.verticalLayout_reviewOrNew.addWidget(self.labelPageReviewOrNewTitle)

        self.line_reviewOrNew = QFrame(self.pageReviewOrNew)
        self.line_reviewOrNew.setObjectName(u"line_reviewOrNew")
        self.line_reviewOrNew.setFrameShape(QFrame.Shape.HLine)
        self.line_reviewOrNew.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_reviewOrNew.addWidget(self.line_reviewOrNew)

        self.fileSelectorWidget = QWidget(self.pageReviewOrNew)
        self.fileSelectorWidget.setObjectName(u"fileSelectorWidget")
        self.fileSelectorWidget.setVisible(False)
        self.verticalLayout_fileSelector = QVBoxLayout(self.fileSelectorWidget)
        self.verticalLayout_fileSelector.setObjectName(u"verticalLayout_fileSelector")
        self.verticalLayout_fileSelector.setContentsMargins(-1, 0, -1, -1)
        self.labelFileInstructions = QLabel(self.fileSelectorWidget)
        self.labelFileInstructions.setObjectName(u"labelFileInstructions")
        font1 = QFont()
        font1.setPointSize(12)
        self.labelFileInstructions.setFont(font1)
        self.labelFileInstructions.setWordWrap(True)

        self.verticalLayout_fileSelector.addWidget(self.labelFileInstructions)

        self.horizontalLayout_fileSelector = QHBoxLayout()
        self.horizontalLayout_fileSelector.setObjectName(u"horizontalLayout_fileSelector")
        self.filePathLabel = QLabel(self.fileSelectorWidget)
        self.filePathLabel.setObjectName(u"filePathLabel")
        self.filePathLabel.setWordWrap(True)

        self.horizontalLayout_fileSelector.addWidget(self.filePathLabel)

        self.browseFileButton = QPushButton(self.fileSelectorWidget)
        self.browseFileButton.setObjectName(u"browseFileButton")
        font2 = QFont()
        font2.setPointSize(11)
        self.browseFileButton.setFont(font2)
        self.browseFileButton.setMinimumSize(QSize(80, 0))
        self.browseFileButton.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_fileSelector.addWidget(self.browseFileButton)


        self.verticalLayout_fileSelector.addLayout(self.horizontalLayout_fileSelector)


        self.verticalLayout_reviewOrNew.addWidget(self.fileSelectorWidget)

        self.labelInstructions = QLabel(self.pageReviewOrNew)
        self.labelInstructions.setObjectName(u"labelInstructions")
        self.labelInstructions.setFont(font1)
        self.labelInstructions.setWordWrap(True)

        self.verticalLayout_reviewOrNew.addWidget(self.labelInstructions)

        self.verticalSpacer_reviewOrNew1 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_reviewOrNew.addItem(self.verticalSpacer_reviewOrNew1)

        self.buttonContainer = QWidget(self.pageReviewOrNew)
        self.buttonContainer.setObjectName(u"buttonContainer")
        self.verticalLayout_buttonContainer = QVBoxLayout(self.buttonContainer)
        self.verticalLayout_buttonContainer.setSpacing(15)
        self.verticalLayout_buttonContainer.setObjectName(u"verticalLayout_buttonContainer")
        self.newAnalysisButton = QPushButton(self.buttonContainer)
        self.newAnalysisButton.setObjectName(u"newAnalysisButton")
        self.newAnalysisButton.setFont(font2)
        self.newAnalysisButton.setMinimumSize(QSize(0, 50))

        self.verticalLayout_buttonContainer.addWidget(self.newAnalysisButton)

        self.reviewButton = QPushButton(self.buttonContainer)
        self.reviewButton.setObjectName(u"reviewButton")
        self.reviewButton.setFont(font2)
        self.reviewButton.setMinimumSize(QSize(0, 50))

        self.verticalLayout_buttonContainer.addWidget(self.reviewButton)


        self.verticalLayout_reviewOrNew.addWidget(self.buttonContainer)

        self.verticalSpacer_reviewOrNew2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_reviewOrNew.addItem(self.verticalSpacer_reviewOrNew2)

        self.stackedWidget.addWidget(self.pageReviewOrNew)
        self.pageDirectories = QWidget()
        self.pageDirectories.setObjectName(u"pageDirectories")
        self.verticalLayout_directories = QVBoxLayout(self.pageDirectories)
        self.verticalLayout_directories.setObjectName(u"verticalLayout_directories")
        self.verticalLayout_directories.setContentsMargins(-1, 5, -1, -1)
        self.labelPage0Title = QLabel(self.pageDirectories)
        self.labelPage0Title.setObjectName(u"labelPage0Title")
        self.labelPage0Title.setFont(font)

        self.verticalLayout_directories.addWidget(self.labelPage0Title)

        self.line = QFrame(self.pageDirectories)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_directories.addWidget(self.line)

        self.widgetInputDirectory = QWidget(self.pageDirectories)
        self.widgetInputDirectory.setObjectName(u"widgetInputDirectory")
        self.verticalLayout_inputDir = QVBoxLayout(self.widgetInputDirectory)
        self.verticalLayout_inputDir.setObjectName(u"verticalLayout_inputDir")
        self.labelInputDirectory = QLabel(self.widgetInputDirectory)
        self.labelInputDirectory.setObjectName(u"labelInputDirectory")
        self.labelInputDirectory.setFont(font1)

        self.verticalLayout_inputDir.addWidget(self.labelInputDirectory)

        self.horizontalLayout_inputDir = QHBoxLayout()
        self.horizontalLayout_inputDir.setObjectName(u"horizontalLayout_inputDir")
        self.inputDirectoryLineEdit = QLineEdit(self.widgetInputDirectory)
        self.inputDirectoryLineEdit.setObjectName(u"inputDirectoryLineEdit")
        self.inputDirectoryLineEdit.setReadOnly(True)

        self.horizontalLayout_inputDir.addWidget(self.inputDirectoryLineEdit)

        self.inputDirectoryButton = QPushButton(self.widgetInputDirectory)
        self.inputDirectoryButton.setObjectName(u"inputDirectoryButton")
        self.inputDirectoryButton.setFont(font2)

        self.horizontalLayout_inputDir.addWidget(self.inputDirectoryButton)


        self.verticalLayout_inputDir.addLayout(self.horizontalLayout_inputDir)


        self.verticalLayout_directories.addWidget(self.widgetInputDirectory)

        self.widgetOutputDirectory = QWidget(self.pageDirectories)
        self.widgetOutputDirectory.setObjectName(u"widgetOutputDirectory")
        self.verticalLayout_outputDir = QVBoxLayout(self.widgetOutputDirectory)
        self.verticalLayout_outputDir.setObjectName(u"verticalLayout_outputDir")
        self.labelOutputDirectory = QLabel(self.widgetOutputDirectory)
        self.labelOutputDirectory.setObjectName(u"labelOutputDirectory")
        self.labelOutputDirectory.setFont(font1)

        self.verticalLayout_outputDir.addWidget(self.labelOutputDirectory)

        self.horizontalLayout_outputDir = QHBoxLayout()
        self.horizontalLayout_outputDir.setObjectName(u"horizontalLayout_outputDir")
        self.outputDirectoryLineEdit = QLineEdit(self.widgetOutputDirectory)
        self.outputDirectoryLineEdit.setObjectName(u"outputDirectoryLineEdit")
        self.outputDirectoryLineEdit.setReadOnly(True)

        self.horizontalLayout_outputDir.addWidget(self.outputDirectoryLineEdit)

        self.outputDirectoryButton = QPushButton(self.widgetOutputDirectory)
        self.outputDirectoryButton.setObjectName(u"outputDirectoryButton")
        self.outputDirectoryButton.setFont(font2)

        self.horizontalLayout_outputDir.addWidget(self.outputDirectoryButton)


        self.verticalLayout_outputDir.addLayout(self.horizontalLayout_outputDir)


        self.verticalLayout_directories.addWidget(self.widgetOutputDirectory)

        self.verticalSpacer_dir2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_directories.addItem(self.verticalSpacer_dir2)

        self.stackedWidget.addWidget(self.pageDirectories)
        self.pageCapture = QWidget()
        self.pageCapture.setObjectName(u"pageCapture")
        self.verticalLayout_2 = QVBoxLayout(self.pageCapture)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, 5, -1, -1)
        self.labelPage2Title = QLabel(self.pageCapture)
        self.labelPage2Title.setObjectName(u"labelPage2Title")
        self.labelPage2Title.setFont(font)

        self.verticalLayout_2.addWidget(self.labelPage2Title)

        self.line_2 = QFrame(self.pageCapture)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line_2)

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


        self.verticalLayout_2.addWidget(self.widgetDrone)

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


        self.verticalLayout_2.addWidget(self.widgetAltitude)

        self.verticalSpacer_4 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_2.addItem(self.verticalSpacer_4)

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


        self.verticalLayout_2.addWidget(self.gsdWidget)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_5)

        self.stackedWidget.addWidget(self.pageCapture)
        self.pageTargetSize = QWidget()
        self.pageTargetSize.setObjectName(u"pageTargetSize")
        self.verticalLayout_3 = QVBoxLayout(self.pageTargetSize)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(-1, 5, -1, -1)
        self.labelPage3Title_TargetSize = QLabel(self.pageTargetSize)
        self.labelPage3Title_TargetSize.setObjectName(u"labelPage3Title_TargetSize")
        self.labelPage3Title_TargetSize.setFont(font)
        self.labelPage3Title_TargetSize.setWordWrap(True)

        self.verticalLayout_3.addWidget(self.labelPage3Title_TargetSize)

        self.line_3 = QFrame(self.pageTargetSize)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_3.addWidget(self.line_3)

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


        self.verticalLayout_3.addWidget(self.widgetObjectSize)

        self.labelExamples = QLabel(self.pageTargetSize)
        self.labelExamples.setObjectName(u"labelExamples")
        self.labelExamples.setFont(font1)
        self.labelExamples.setWordWrap(True)

        self.verticalLayout_3.addWidget(self.labelExamples)

        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_8)

        self.stackedWidget.addWidget(self.pageTargetSize)
        self.pageAlgorithm = QWidget()
        self.pageAlgorithm.setObjectName(u"pageAlgorithm")
        self.verticalLayout_4 = QVBoxLayout(self.pageAlgorithm)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(-1, 5, -1, -1)
        self.labelPage4Title = QLabel(self.pageAlgorithm)
        self.labelPage4Title.setObjectName(u"labelPage4Title")
        self.labelPage4Title.setFont(font)

        self.verticalLayout_4.addWidget(self.labelPage4Title)

        self.line_4 = QFrame(self.pageAlgorithm)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_4.addWidget(self.line_4)

        self.algorithmWidget = QWidget(self.pageAlgorithm)
        self.algorithmWidget.setObjectName(u"algorithmWidget")
        self.verticalLayout_algorithm = QVBoxLayout(self.algorithmWidget)
        self.verticalLayout_algorithm.setObjectName(u"verticalLayout_algorithm")
        self.labelCurrentQuestion = QLabel(self.algorithmWidget)
        self.labelCurrentQuestion.setObjectName(u"labelCurrentQuestion")
        font4 = QFont()
        font4.setPointSize(14)
        self.labelCurrentQuestion.setFont(font4)
        self.labelCurrentQuestion.setAlignment(Qt.AlignCenter)

        self.verticalLayout_algorithm.addWidget(self.labelCurrentQuestion)

        self.horizontalLayout_buttons = QHBoxLayout()
        self.horizontalLayout_buttons.setObjectName(u"horizontalLayout_buttons")
        self.horizontalLayout_buttons.setContentsMargins(-1, 10, -1, 10)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_buttons.addItem(self.horizontalSpacer)

        self.buttonYes = QPushButton(self.algorithmWidget)
        self.buttonYes.setObjectName(u"buttonYes")
        self.buttonYes.setMinimumSize(QSize(100, 40))
        self.buttonYes.setFont(font1)

        self.horizontalLayout_buttons.addWidget(self.buttonYes)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_buttons.addItem(self.horizontalSpacer_2)

        self.buttonNo = QPushButton(self.algorithmWidget)
        self.buttonNo.setObjectName(u"buttonNo")
        self.buttonNo.setMinimumSize(QSize(100, 40))
        self.buttonNo.setFont(font1)

        self.horizontalLayout_buttons.addWidget(self.buttonNo)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_buttons.addItem(self.horizontalSpacer_3)


        self.verticalLayout_algorithm.addLayout(self.horizontalLayout_buttons)

        self.labelAlgorithmResult = QLabel(self.algorithmWidget)
        self.labelAlgorithmResult.setObjectName(u"labelAlgorithmResult")
        font5 = QFont()
        font5.setPointSize(14)
        font5.setBold(True)
        self.labelAlgorithmResult.setFont(font5)
        self.labelAlgorithmResult.setVisible(False)
        self.labelAlgorithmResult.setAlignment(Qt.AlignCenter)

        self.verticalLayout_algorithm.addWidget(self.labelAlgorithmResult)

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


        self.verticalLayout_algorithm.addLayout(self.horizontalLayout_reset)

        self.verticalSpacer_11 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_algorithm.addItem(self.verticalSpacer_11)


        self.verticalLayout_4.addWidget(self.algorithmWidget)

        self.stackedWidget.addWidget(self.pageAlgorithm)
        self.pageAlgorithmParameters = QWidget()
        self.pageAlgorithmParameters.setObjectName(u"pageAlgorithmParameters")
        self.verticalLayout_algorithmParameters = QVBoxLayout(self.pageAlgorithmParameters)
        self.verticalLayout_algorithmParameters.setObjectName(u"verticalLayout_algorithmParameters")
        self.verticalLayout_algorithmParameters.setContentsMargins(-1, 5, -1, -1)
        self.labelPage5Title_AlgorithmParameters = QLabel(self.pageAlgorithmParameters)
        self.labelPage5Title_AlgorithmParameters.setObjectName(u"labelPage5Title_AlgorithmParameters")
        self.labelPage5Title_AlgorithmParameters.setFont(font)

        self.verticalLayout_algorithmParameters.addWidget(self.labelPage5Title_AlgorithmParameters)

        self.line_algorithmParameters = QFrame(self.pageAlgorithmParameters)
        self.line_algorithmParameters.setObjectName(u"line_algorithmParameters")
        self.line_algorithmParameters.setFrameShape(QFrame.Shape.HLine)
        self.line_algorithmParameters.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_algorithmParameters.addWidget(self.line_algorithmParameters)

        self.algorithmParametersContainer = QWidget(self.pageAlgorithmParameters)
        self.algorithmParametersContainer.setObjectName(u"algorithmParametersContainer")

        self.verticalLayout_algorithmParameters.addWidget(self.algorithmParametersContainer)

        self.stackedWidget.addWidget(self.pageAlgorithmParameters)
        self.pageSettings = QWidget()
        self.pageSettings.setObjectName(u"pageSettings")
        self.verticalLayout_5 = QVBoxLayout(self.pageSettings)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(-1, 5, -1, -1)
        self.labelPage4Title_Settings = QLabel(self.pageSettings)
        self.labelPage4Title_Settings.setObjectName(u"labelPage4Title_Settings")
        self.labelPage4Title_Settings.setFont(font)

        self.verticalLayout_5.addWidget(self.labelPage4Title_Settings)

        self.line_5 = QFrame(self.pageSettings)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShape(QFrame.Shape.HLine)
        self.line_5.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_5.addWidget(self.line_5)

        self.widgetIdentifierColor = QWidget(self.pageSettings)
        self.widgetIdentifierColor.setObjectName(u"widgetIdentifierColor")
        self.verticalLayout_color = QVBoxLayout(self.widgetIdentifierColor)
        self.verticalLayout_color.setObjectName(u"verticalLayout_color")
        self.labelIdentifierColor = QLabel(self.widgetIdentifierColor)
        self.labelIdentifierColor.setObjectName(u"labelIdentifierColor")
        self.labelIdentifierColor.setFont(font1)

        self.verticalLayout_color.addWidget(self.labelIdentifierColor)

        self.horizontalLayout_color = QHBoxLayout()
        self.horizontalLayout_color.setObjectName(u"horizontalLayout_color")
        self.colorPickerButton = QPushButton(self.widgetIdentifierColor)
        self.colorPickerButton.setObjectName(u"colorPickerButton")
        self.colorPickerButton.setMinimumSize(QSize(150, 30))
        self.colorPickerButton.setFont(font2)

        self.horizontalLayout_color.addWidget(self.colorPickerButton)

        self.labelColorPreview = QLabel(self.widgetIdentifierColor)
        self.labelColorPreview.setObjectName(u"labelColorPreview")
        self.labelColorPreview.setMinimumSize(QSize(50, 30))
        self.labelColorPreview.setStyleSheet(u"background-color: red; border: 1px solid black;")

        self.horizontalLayout_color.addWidget(self.labelColorPreview)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_color.addItem(self.horizontalSpacer_6)


        self.verticalLayout_color.addLayout(self.horizontalLayout_color)


        self.verticalLayout_5.addWidget(self.widgetIdentifierColor)

        self.widgetMaxProcesses = QWidget(self.pageSettings)
        self.widgetMaxProcesses.setObjectName(u"widgetMaxProcesses")
        self.verticalLayout_maxProcesses = QVBoxLayout(self.widgetMaxProcesses)
        self.verticalLayout_maxProcesses.setObjectName(u"verticalLayout_maxProcesses")
        self.labelMaxProcesses = QLabel(self.widgetMaxProcesses)
        self.labelMaxProcesses.setObjectName(u"labelMaxProcesses")
        self.labelMaxProcesses.setFont(font1)

        self.verticalLayout_maxProcesses.addWidget(self.labelMaxProcesses)

        self.horizontalLayout_processes = QHBoxLayout()
        self.horizontalLayout_processes.setObjectName(u"horizontalLayout_processes")
        self.maxProcessesSliderWidget = QWidget(self.widgetMaxProcesses)
        self.maxProcessesSliderWidget.setObjectName(u"maxProcessesSliderWidget")
        self.maxProcessesSliderWidget.setMinimumSize(QSize(600, 60))

        self.horizontalLayout_processes.addWidget(self.maxProcessesSliderWidget)

        self.benchmarkButton = QPushButton(self.widgetMaxProcesses)
        self.benchmarkButton.setObjectName(u"benchmarkButton")
        self.benchmarkButton.setFont(font2)

        self.horizontalLayout_processes.addWidget(self.benchmarkButton)


        self.verticalLayout_maxProcesses.addLayout(self.horizontalLayout_processes)


        self.verticalLayout_5.addWidget(self.widgetMaxProcesses)

        self.widgetProcessingResolution = QWidget(self.pageSettings)
        self.widgetProcessingResolution.setObjectName(u"widgetProcessingResolution")
        self.verticalLayout_processingResolution = QVBoxLayout(self.widgetProcessingResolution)
        self.verticalLayout_processingResolution.setSpacing(0)
        self.verticalLayout_processingResolution.setObjectName(u"verticalLayout_processingResolution")
        self.labelProcessingResolution = QLabel(self.widgetProcessingResolution)
        self.labelProcessingResolution.setObjectName(u"labelProcessingResolution")
        self.labelProcessingResolution.setFont(font1)

        self.verticalLayout_processingResolution.addWidget(self.labelProcessingResolution)

        self.processingResolutionSliderWidget = QWidget(self.widgetProcessingResolution)
        self.processingResolutionSliderWidget.setObjectName(u"processingResolutionSliderWidget")
        self.processingResolutionSliderWidget.setMinimumSize(QSize(600, 60))

        self.verticalLayout_processingResolution.addWidget(self.processingResolutionSliderWidget)


        self.verticalLayout_5.addWidget(self.widgetProcessingResolution)

        self.widgetNormalizeHistogram = QWidget(self.pageSettings)
        self.widgetNormalizeHistogram.setObjectName(u"widgetNormalizeHistogram")
        self.verticalLayout_normalize = QVBoxLayout(self.widgetNormalizeHistogram)
        self.verticalLayout_normalize.setObjectName(u"verticalLayout_normalize")
        self.labelNormalizeHistogram = QLabel(self.widgetNormalizeHistogram)
        self.labelNormalizeHistogram.setObjectName(u"labelNormalizeHistogram")
        self.labelNormalizeHistogram.setFont(font1)

        self.verticalLayout_normalize.addWidget(self.labelNormalizeHistogram)

        self.widgetRadioButtons = QWidget(self.widgetNormalizeHistogram)
        self.widgetRadioButtons.setObjectName(u"widgetRadioButtons")
        self.horizontalLayout_radio = QHBoxLayout(self.widgetRadioButtons)
        self.horizontalLayout_radio.setObjectName(u"horizontalLayout_radio")
        self.radioNormalizeNo = QRadioButton(self.widgetRadioButtons)
        self.radioNormalizeNo.setObjectName(u"radioNormalizeNo")
        self.radioNormalizeNo.setFont(font2)
        self.radioNormalizeNo.setChecked(True)

        self.horizontalLayout_radio.addWidget(self.radioNormalizeNo)

        self.radioNormalizeYes = QRadioButton(self.widgetRadioButtons)
        self.radioNormalizeYes.setObjectName(u"radioNormalizeYes")
        self.radioNormalizeYes.setFont(font2)

        self.horizontalLayout_radio.addWidget(self.radioNormalizeYes)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_radio.addItem(self.horizontalSpacer_4)


        self.verticalLayout_normalize.addWidget(self.widgetRadioButtons)


        self.verticalLayout_5.addWidget(self.widgetNormalizeHistogram)

        self.verticalSpacer_15 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_15)

        self.stackedWidget.addWidget(self.pageSettings)

        self.verticalLayout.addWidget(self.stackedWidget)

        self.buttonWidget = QWidget(ImageAnalysisGuide)
        self.buttonWidget.setObjectName(u"buttonWidget")
        self.buttonWidget.setMinimumSize(QSize(0, 50))
        self.horizontalLayout_buttons_main = QHBoxLayout(self.buttonWidget)
        self.horizontalLayout_buttons_main.setObjectName(u"horizontalLayout_buttons_main")
        self.cancelButton = QPushButton(self.buttonWidget)
        self.cancelButton.setObjectName(u"cancelButton")
        self.cancelButton.setFont(font2)

        self.horizontalLayout_buttons_main.addWidget(self.cancelButton)

        self.skipCheckBox = QCheckBox(self.buttonWidget)
        self.skipCheckBox.setObjectName(u"skipCheckBox")
        font6 = QFont()
        font6.setPointSize(10)
        self.skipCheckBox.setFont(font6)

        self.horizontalLayout_buttons_main.addWidget(self.skipCheckBox)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_buttons_main.addItem(self.horizontalSpacer_5)

        self.backButton = QPushButton(self.buttonWidget)
        self.backButton.setObjectName(u"backButton")
        self.backButton.setFont(font2)

        self.horizontalLayout_buttons_main.addWidget(self.backButton)

        self.continueButton = QPushButton(self.buttonWidget)
        self.continueButton.setObjectName(u"continueButton")
        self.continueButton.setFont(font2)

        self.horizontalLayout_buttons_main.addWidget(self.continueButton)


        self.verticalLayout.addWidget(self.buttonWidget)


        self.retranslateUi(ImageAnalysisGuide)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(ImageAnalysisGuide)
    # setupUi

    def retranslateUi(self, ImageAnalysisGuide):
        ImageAnalysisGuide.setWindowTitle(QCoreApplication.translate("ImageAnalysisGuide", u"Image Analysis Guide", None))
        self.labelPageReviewOrNewTitle.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Welcome to ADIAT", None))
        self.labelFileInstructions.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Please select the ADIAT_Data.xml file from previous analysis:", None))
        self.filePathLabel.setText(QCoreApplication.translate("ImageAnalysisGuide", u"No file selected", None))
        self.browseFileButton.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Browse...", None))
        self.labelInstructions.setText(QCoreApplication.translate("ImageAnalysisGuide", u"What would you like to do?", None))
        self.newAnalysisButton.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Start New Image Analysis", None))
        self.reviewButton.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Review Existing Image Analysis", None))
        self.labelPage0Title.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Select Directories", None))
        self.labelInputDirectory.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Where are the images you want to analyze?", None))
        self.inputDirectoryButton.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Browse...", None))
        self.labelOutputDirectory.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Where do you want ADIAT to store the output files?", None))
        self.outputDirectoryButton.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Browse...", None))
        self.labelPage2Title.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Image Capture Information", None))
        self.labelDrone.setText(QCoreApplication.translate("ImageAnalysisGuide", u"What drone/camera was used to capture images?", None))
        self.labelAltitude.setText(QCoreApplication.translate("ImageAnalysisGuide", u"At what above ground level (AGL) altitude was the drone flying?", None))
        self.altitudeUnitComboBox.setItemText(0, QCoreApplication.translate("ImageAnalysisGuide", u"ft", None))
        self.altitudeUnitComboBox.setItemText(1, QCoreApplication.translate("ImageAnalysisGuide", u"m", None))

        self.labelGSDTitle.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Estimated Ground Sampling Distance (GSD):", None))
        self.gsdTextEdit.setHtml(QCoreApplication.translate("ImageAnalysisGuide", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'MS Shell Dlg 2'; font-size:9pt;\"><br /></p></body></html>", None))
        self.gsdTextEdit.setPlaceholderText(QCoreApplication.translate("ImageAnalysisGuide", u"--", None))
        self.labelPage3Title_TargetSize.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Search Target Size", None))
        self.labelObjectSize.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Approximately how large are the objects you're wanting to identify?", None))
        self.labelExamples.setText(QCoreApplication.translate("ImageAnalysisGuide", u"<html><head/><body><p><span style=\" font-weight:700;\">More Examples:</span></p><ul><li>&nbsp;&nbsp;1 sqft \u2013 Hat, Helmet, Plastic Bag </li><li>&nbsp;&nbsp;3 sqft \u2013 Cat, Daypack </li><li>&nbsp;&nbsp;6 sqft \u2013 Large Pack, Medium Dog </li><li>&nbsp;&nbsp;12 sqft \u2013 Sleeping Bag, Large Dog </li><li>&nbsp;&nbsp;50 sqft \u2013 Small Boat, 2-Person Tent </li><li>&nbsp;&nbsp;200 sqft \u2013 Car/SUV, Small Pickup Truck, Large Tent </li><li>&nbsp;&nbsp;1000 sqft \u2013 House </li></ul></body></html>", None))
        self.labelPage4Title.setText(QCoreApplication.translate("ImageAnalysisGuide", u"ALGORITHM SELECTION GUIDE", None))
        self.labelCurrentQuestion.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Are you using thermal images?", None))
        self.buttonYes.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Yes", None))
        self.buttonNo.setText(QCoreApplication.translate("ImageAnalysisGuide", u"No", None))
        self.labelAlgorithmResult.setText("")
        self.resetAlgorithmButton.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Reset", None))
        self.labelPage5Title_AlgorithmParameters.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Algorithm Parameters", None))
        self.labelPage4Title_Settings.setText(QCoreApplication.translate("ImageAnalysisGuide", u"General Settings", None))
        self.labelIdentifierColor.setText(QCoreApplication.translate("ImageAnalysisGuide", u"What color should be used to highlight Areas of Interest (AOIs)?", None))
        self.colorPickerButton.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Select Color", None))
        self.labelColorPreview.setText("")
        self.labelMaxProcesses.setText(QCoreApplication.translate("ImageAnalysisGuide", u"How many images should be processed at the same time?", None))
        self.benchmarkButton.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Run Benchmark", None))
        self.labelProcessingResolution.setText(QCoreApplication.translate("ImageAnalysisGuide", u"What resolution should images be processed at?", None))
        self.labelNormalizeHistogram.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Were the images captured in different lighting conditions?", None))
        self.radioNormalizeNo.setText(QCoreApplication.translate("ImageAnalysisGuide", u"No", None))
        self.radioNormalizeYes.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Yes", None))
        self.cancelButton.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Close", None))
        self.skipCheckBox.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Skip this wizard in the future", None))
        self.backButton.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Back", None))
        self.continueButton.setText(QCoreApplication.translate("ImageAnalysisGuide", u"Continue", None))
    # retranslateUi

