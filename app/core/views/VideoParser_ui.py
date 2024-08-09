# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\charl\source\repos\crgrove\automated-drone-image-analysis-tool\resources/views\VideoParser.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_VideoParser(object):
    def setupUi(self, VideoParser):
        VideoParser.setObjectName("VideoParser")
        VideoParser.resize(732, 490)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(VideoParser)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.setupFrame = QtWidgets.QFrame(VideoParser)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.setupFrame.sizePolicy().hasHeightForWidth())
        self.setupFrame.setSizePolicy(sizePolicy)
        self.setupFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setupFrame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.setupFrame.setLineWidth(3)
        self.setupFrame.setObjectName("setupFrame")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.setupFrame)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.selectorsGrid = QtWidgets.QGridLayout()
        self.selectorsGrid.setObjectName("selectorsGrid")
        self.videoSelectLine = QtWidgets.QLineEdit(self.setupFrame)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.videoSelectLine.setFont(font)
        self.videoSelectLine.setReadOnly(True)
        self.videoSelectLine.setObjectName("videoSelectLine")
        self.selectorsGrid.addWidget(self.videoSelectLine, 0, 1, 1, 1)
        self.srtSelectLabel = QtWidgets.QLabel(self.setupFrame)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.srtSelectLabel.setFont(font)
        self.srtSelectLabel.setToolTip("")
        self.srtSelectLabel.setObjectName("srtSelectLabel")
        self.selectorsGrid.addWidget(self.srtSelectLabel, 1, 0, 1, 1)
        self.outputLabel = QtWidgets.QLabel(self.setupFrame)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.outputLabel.setFont(font)
        self.outputLabel.setObjectName("outputLabel")
        self.selectorsGrid.addWidget(self.outputLabel, 2, 0, 1, 1)
        self.outputLine = QtWidgets.QLineEdit(self.setupFrame)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.outputLine.setFont(font)
        self.outputLine.setReadOnly(True)
        self.outputLine.setObjectName("outputLine")
        self.selectorsGrid.addWidget(self.outputLine, 2, 1, 1, 1)
        self.outputSelectButton = QtWidgets.QPushButton(self.setupFrame)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.outputSelectButton.setFont(font)
        self.outputSelectButton.setAutoDefault(False)
        self.outputSelectButton.setObjectName("outputSelectButton")
        self.selectorsGrid.addWidget(self.outputSelectButton, 2, 2, 1, 1)
        self.videoSelectLabel = QtWidgets.QLabel(self.setupFrame)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.videoSelectLabel.setFont(font)
        self.videoSelectLabel.setObjectName("videoSelectLabel")
        self.selectorsGrid.addWidget(self.videoSelectLabel, 0, 0, 1, 1)
        self.videoSelectButton = QtWidgets.QPushButton(self.setupFrame)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.videoSelectButton.setFont(font)
        self.videoSelectButton.setAutoDefault(False)
        self.videoSelectButton.setObjectName("videoSelectButton")
        self.selectorsGrid.addWidget(self.videoSelectButton, 0, 2, 1, 1)
        self.srtSelectLine = QtWidgets.QLineEdit(self.setupFrame)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.srtSelectLine.setFont(font)
        self.srtSelectLine.setReadOnly(True)
        self.srtSelectLine.setObjectName("srtSelectLine")
        self.selectorsGrid.addWidget(self.srtSelectLine, 1, 1, 1, 1)
        self.srtSelectButton = QtWidgets.QPushButton(self.setupFrame)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.srtSelectButton.setFont(font)
        self.srtSelectButton.setAutoDefault(False)
        self.srtSelectButton.setObjectName("srtSelectButton")
        self.selectorsGrid.addWidget(self.srtSelectButton, 1, 2, 1, 1)
        self.verticalLayout_3.addLayout(self.selectorsGrid)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.timeLabel = QtWidgets.QLabel(self.setupFrame)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.timeLabel.setFont(font)
        self.timeLabel.setObjectName("timeLabel")
        self.horizontalLayout.addWidget(self.timeLabel)
        self.timespinBox = QtWidgets.QSpinBox(self.setupFrame)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.timespinBox.setFont(font)
        self.timespinBox.setMinimum(1)
        self.timespinBox.setProperty("value", 5)
        self.timespinBox.setObjectName("timespinBox")
        self.horizontalLayout.addWidget(self.timespinBox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addWidget(self.setupFrame)
        self.mainButtons = QtWidgets.QHBoxLayout()
        self.mainButtons.setObjectName("mainButtons")
        self.startButton = QtWidgets.QPushButton(VideoParser)
        self.startButton.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.startButton.sizePolicy().hasHeightForWidth())
        self.startButton.setSizePolicy(sizePolicy)
        self.startButton.setMinimumSize(QtCore.QSize(150, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.startButton.setFont(font)
        self.startButton.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.startButton.setAutoFillBackground(False)
        self.startButton.setStyleSheet("background-color: rgb(0, 136, 0);\n"
"color: rgb(228, 231, 235);")
        self.startButton.setDefault(False)
        self.startButton.setObjectName("startButton")
        self.mainButtons.addWidget(self.startButton)
        self.cancelButton = QtWidgets.QPushButton(VideoParser)
        self.cancelButton.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cancelButton.sizePolicy().hasHeightForWidth())
        self.cancelButton.setSizePolicy(sizePolicy)
        self.cancelButton.setMinimumSize(QtCore.QSize(150, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.cancelButton.setFont(font)
        self.cancelButton.setStyleSheet("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.cancelButton.setIcon(icon)
        self.cancelButton.setObjectName("cancelButton")
        self.mainButtons.addWidget(self.cancelButton)
        spacerItem1 = QtWidgets.QSpacerItem(400, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.mainButtons.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.mainButtons)
        self.outputWindow = QtWidgets.QPlainTextEdit(VideoParser)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.outputWindow.setFont(font)
        self.outputWindow.setReadOnly(True)
        self.outputWindow.setObjectName("outputWindow")
        self.verticalLayout_2.addWidget(self.outputWindow)

        self.retranslateUi(VideoParser)
        QtCore.QMetaObject.connectSlotsByName(VideoParser)

    def retranslateUi(self, VideoParser):
        _translate = QtCore.QCoreApplication.translate
        VideoParser.setWindowTitle(_translate("VideoParser", "Video Parser"))
        self.srtSelectLabel.setWhatsThis(_translate("VideoParser", "The SRT file contains timestamped information about the video file.  It is optional, but without it output images won\'t include location information."))
        self.srtSelectLabel.setText(_translate("VideoParser", "SRT File (optional): "))
        self.outputLabel.setText(_translate("VideoParser", "Output Folder:"))
        self.outputSelectButton.setText(_translate("VideoParser", "Select"))
        self.videoSelectLabel.setText(_translate("VideoParser", "Video File:"))
        self.videoSelectButton.setText(_translate("VideoParser", "Select"))
        self.srtSelectButton.setText(_translate("VideoParser", "Select"))
        self.timeLabel.setText(_translate("VideoParser", "Time Interval (seconds):"))
        self.startButton.setText(_translate("VideoParser", "Start"))
        self.cancelButton.setText(_translate("VideoParser", " Cancel"))
from . import resources_rc