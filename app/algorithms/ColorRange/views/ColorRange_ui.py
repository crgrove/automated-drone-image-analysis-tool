# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\charl\source\repos\crgrove\adiat_ai\resources/views/algorithms/ColorRange.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ColorRange(object):
    def setupUi(self, ColorRange):
        ColorRange.setObjectName("ColorRange")
        ColorRange.resize(674, 94)
        self.verticalLayout = QtWidgets.QVBoxLayout(ColorRange)
        self.verticalLayout.setObjectName("verticalLayout")
        self.ColorSelectionLayout = QtWidgets.QHBoxLayout()
        self.ColorSelectionLayout.setObjectName("ColorSelectionLayout")
        self.colorButton = QtWidgets.QPushButton(ColorRange)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.colorButton.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/color.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.colorButton.setIcon(icon)
        self.colorButton.setObjectName("colorButton")
        self.ColorSelectionLayout.addWidget(self.colorButton)
        spacerItem = QtWidgets.QSpacerItem(18, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.ColorSelectionLayout.addItem(spacerItem)
        self.SpinBoxLayout = QtWidgets.QHBoxLayout()
        self.SpinBoxLayout.setObjectName("SpinBoxLayout")
        self.rSensitivityLabel = QtWidgets.QLabel(ColorRange)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rSensitivityLabel.setFont(font)
        self.rSensitivityLabel.setObjectName("rSensitivityLabel")
        self.SpinBoxLayout.addWidget(self.rSensitivityLabel)
        self.rRangeSpinBox = QtWidgets.QSpinBox(ColorRange)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rRangeSpinBox.setFont(font)
        self.rRangeSpinBox.setMaximum(255)
        self.rRangeSpinBox.setProperty("value", 50)
        self.rRangeSpinBox.setObjectName("rRangeSpinBox")
        self.SpinBoxLayout.addWidget(self.rRangeSpinBox)
        spacerItem1 = QtWidgets.QSpacerItem(18, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.SpinBoxLayout.addItem(spacerItem1)
        self.gSensitivityLabel = QtWidgets.QLabel(ColorRange)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.gSensitivityLabel.setFont(font)
        self.gSensitivityLabel.setObjectName("gSensitivityLabel")
        self.SpinBoxLayout.addWidget(self.gSensitivityLabel)
        self.gRangeSpinBox = QtWidgets.QSpinBox(ColorRange)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.gRangeSpinBox.setFont(font)
        self.gRangeSpinBox.setMaximum(255)
        self.gRangeSpinBox.setProperty("value", 50)
        self.gRangeSpinBox.setObjectName("gRangeSpinBox")
        self.SpinBoxLayout.addWidget(self.gRangeSpinBox)
        spacerItem2 = QtWidgets.QSpacerItem(18, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.SpinBoxLayout.addItem(spacerItem2)
        self.bSensitivityLabel = QtWidgets.QLabel(ColorRange)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.bSensitivityLabel.setFont(font)
        self.bSensitivityLabel.setObjectName("bSensitivityLabel")
        self.SpinBoxLayout.addWidget(self.bSensitivityLabel)
        self.bRangeSpinBox = QtWidgets.QSpinBox(ColorRange)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.bRangeSpinBox.setFont(font)
        self.bRangeSpinBox.setMaximum(255)
        self.bRangeSpinBox.setProperty("value", 50)
        self.bRangeSpinBox.setObjectName("bRangeSpinBox")
        self.SpinBoxLayout.addWidget(self.bRangeSpinBox)
        self.ColorSelectionLayout.addLayout(self.SpinBoxLayout)
        self.verticalLayout.addLayout(self.ColorSelectionLayout)
        self.ColorRangeLayout = QtWidgets.QHBoxLayout()
        self.ColorRangeLayout.setObjectName("ColorRangeLayout")
        self.colorRangeLabel = QtWidgets.QLabel(ColorRange)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.colorRangeLabel.setFont(font)
        self.colorRangeLabel.setObjectName("colorRangeLabel")
        self.ColorRangeLayout.addWidget(self.colorRangeLabel)
        self.minColor = QtWidgets.QFrame(ColorRange)
        self.minColor.setWhatsThis("")
        self.minColor.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.minColor.setFrameShadow(QtWidgets.QFrame.Raised)
        self.minColor.setObjectName("minColor")
        self.ColorRangeLayout.addWidget(self.minColor)
        self.midColor = QtWidgets.QFrame(ColorRange)
        self.midColor.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.midColor.setFrameShadow(QtWidgets.QFrame.Raised)
        self.midColor.setObjectName("midColor")
        self.ColorRangeLayout.addWidget(self.midColor)
        self.maxColor = QtWidgets.QFrame(ColorRange)
        self.maxColor.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.maxColor.setFrameShadow(QtWidgets.QFrame.Raised)
        self.maxColor.setObjectName("maxColor")
        self.ColorRangeLayout.addWidget(self.maxColor)
        self.viewRangeButton = QtWidgets.QPushButton(ColorRange)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.viewRangeButton.sizePolicy().hasHeightForWidth())
        self.viewRangeButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.viewRangeButton.setFont(font)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/eye.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.viewRangeButton.setIcon(icon1)
        self.viewRangeButton.setObjectName("viewRangeButton")
        self.ColorRangeLayout.addWidget(self.viewRangeButton)
        self.verticalLayout.addLayout(self.ColorRangeLayout)

        self.retranslateUi(ColorRange)
        QtCore.QMetaObject.connectSlotsByName(ColorRange)

    def retranslateUi(self, ColorRange):
        _translate = QtCore.QCoreApplication.translate
        ColorRange.setWindowTitle(_translate("ColorRange", "Form"))
        self.colorButton.setText(_translate("ColorRange", " Pick Color"))
        self.colorButton.setProperty("iconName", _translate("ColorRange", "color.png"))
        self.rSensitivityLabel.setText(_translate("ColorRange", "Red Range +/-"))
        self.gSensitivityLabel.setText(_translate("ColorRange", "Green Range +/-"))
        self.bSensitivityLabel.setText(_translate("ColorRange", "Blue Range +/-"))
        self.colorRangeLabel.setText(_translate("ColorRange", "Color Range:"))
        self.viewRangeButton.setText(_translate("ColorRange", "View Range"))
        self.viewRangeButton.setProperty("iconName", _translate("ColorRange", "eye.png"))
from . import resources_rc
