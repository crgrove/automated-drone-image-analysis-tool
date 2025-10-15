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
import resources_rc

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
        self.maxAreaSpinBox.setMaximum(1999)
        self.maxAreaSpinBox.setSingleStep(1)
        self.maxAreaSpinBox.setValue(0)

        self.GeneralLayout.addWidget(self.maxAreaSpinBox)

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
        MainWindow.setMenuBar(self.mainBar)

        self.mainBar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionLoadFile)
        self.menuFile.addAction(self.actionPreferences)
        self.menuFile.addAction(self.actionVideoParser)
        self.menuFile.addAction(self.actionRTMPDetection)
        self.menuFile.addAction(self.actionIntegratedDetection)

        self.retranslateUi(MainWindow)

        self.startButton.setDefault(False)
        self.viewResultsButton.setDefault(False)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Automated Drone Image Analysis Tool  v1.2 - Sponsored by TEXSAR", None))
        self.actionLoadFile.setText(QCoreApplication.translate("MainWindow", u"Load Results File", None))
        self.actionPreferences.setText(QCoreApplication.translate("MainWindow", u"Preferences", None))
        self.actionVideoParser.setText(QCoreApplication.translate("MainWindow", u"Video Parser", None))
        self.actionRTMPDetection.setText(QCoreApplication.translate("MainWindow", u"Real-Time Color Detection", None))
        self.actionIntegratedDetection.setText(QCoreApplication.translate("MainWindow", u"Real-Time Integrated Detection", None))
        self.outputFolderButton.setText(QCoreApplication.translate("MainWindow", u" Select", None))
        self.outputFolderButton.setProperty(u"iconName", QCoreApplication.translate("MainWindow", u"folder.png", None))
        self.inputFolderLabel.setText(QCoreApplication.translate("MainWindow", u"Input Folder:", None))
        self.outputFolderLabel.setText(QCoreApplication.translate("MainWindow", u"Output Folder:", None))
        self.inputFolderButton.setText(QCoreApplication.translate("MainWindow", u" Select", None))
        self.inputFolderButton.setProperty(u"iconName", QCoreApplication.translate("MainWindow", u"folder.png", None))
        self.minAreaLabel.setText(QCoreApplication.translate("MainWindow", u"Min Object Area (px):", None))
        self.maxAreaLabel.setText(QCoreApplication.translate("MainWindow", u"Max Object Area (px):", None))
        self.maxAreaSpinBox.setSpecialValueText(QCoreApplication.translate("MainWindow", u"None", None))
        self.identifierColor.setText(QCoreApplication.translate("MainWindow", u"Object Identifer Color:", None))
        self.identifierColorButton.setText("")
        self.maxProcessesLabel.setText(QCoreApplication.translate("MainWindow", u"Max Processes: ", None))
        self.kMeansCheckbox.setText(QCoreApplication.translate("MainWindow", u"Use K-Means Clustering", None))
        self.clustersLabel.setText(QCoreApplication.translate("MainWindow", u"Number of Clusters (Colors)", None))
        self.histogramCheckbox.setText(QCoreApplication.translate("MainWindow", u"Normalize Histograms", None))
        self.histogramReferenceImageLabel.setText(QCoreApplication.translate("MainWindow", u"Reference Image:", None))
        self.histogramButton.setText(QCoreApplication.translate("MainWindow", u" Select", None))
        self.histogramButton.setProperty(u"iconName", QCoreApplication.translate("MainWindow", u"image.png", None))
        self.algorithmLabel.setText(QCoreApplication.translate("MainWindow", u"Algorithm:", None))
        self.startButton.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.cancelButton.setText(QCoreApplication.translate("MainWindow", u" Cancel", None))
        self.cancelButton.setProperty(u"iconName", QCoreApplication.translate("MainWindow", u"cancel.png", None))
        self.viewResultsButton.setText(QCoreApplication.translate("MainWindow", u" View Results", None))
        self.viewResultsButton.setProperty(u"iconName", QCoreApplication.translate("MainWindow", u"search", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"Menu", None))
    # retranslateUi

