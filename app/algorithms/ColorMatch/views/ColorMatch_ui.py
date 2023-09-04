# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\xampp7\htdocs\ADIAT\resources/views/algorithms\ColorMatchWidget.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ColorMatch(object):
    def setupUi(self, ColorMatch):
        ColorMatch.setObjectName("ColorMatch")
        ColorMatch.resize(674, 94)
        self.verticalLayout = QtWidgets.QVBoxLayout(ColorMatch)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.colorButton = QtWidgets.QPushButton(ColorMatch)
        self.colorButton.setObjectName("colorButton")
        self.horizontalLayout_4.addWidget(self.colorButton)
        spacerItem = QtWidgets.QSpacerItem(18, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.hSensitivityLabel = QtWidgets.QLabel(ColorMatch)
        self.hSensitivityLabel.setObjectName("hSensitivityLabel")
        self.horizontalLayout_3.addWidget(self.hSensitivityLabel)
        self.rRangeSpinBox = QtWidgets.QSpinBox(ColorMatch)
        self.rRangeSpinBox.setMaximum(255)
        self.rRangeSpinBox.setProperty("value", 75)
        self.rRangeSpinBox.setObjectName("rRangeSpinBox")
        self.horizontalLayout_3.addWidget(self.rRangeSpinBox)
        spacerItem1 = QtWidgets.QSpacerItem(18, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.sSensitivityLabel = QtWidgets.QLabel(ColorMatch)
        self.sSensitivityLabel.setObjectName("sSensitivityLabel")
        self.horizontalLayout_3.addWidget(self.sSensitivityLabel)
        self.gRangeSpinBox = QtWidgets.QSpinBox(ColorMatch)
        self.gRangeSpinBox.setMaximum(255)
        self.gRangeSpinBox.setProperty("value", 75)
        self.gRangeSpinBox.setObjectName("gRangeSpinBox")
        self.horizontalLayout_3.addWidget(self.gRangeSpinBox)
        spacerItem2 = QtWidgets.QSpacerItem(18, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.vSensitivityLabel = QtWidgets.QLabel(ColorMatch)
        self.vSensitivityLabel.setObjectName("vSensitivityLabel")
        self.horizontalLayout_3.addWidget(self.vSensitivityLabel)
        self.bRangeSpinBox = QtWidgets.QSpinBox(ColorMatch)
        self.bRangeSpinBox.setMaximum(255)
        self.bRangeSpinBox.setProperty("value", 75)
        self.bRangeSpinBox.setObjectName("bRangeSpinBox")
        self.horizontalLayout_3.addWidget(self.bRangeSpinBox)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.colorRangeLabel = QtWidgets.QLabel(ColorMatch)
        self.colorRangeLabel.setObjectName("colorRangeLabel")
        self.horizontalLayout_6.addWidget(self.colorRangeLabel)
        self.min_color = QtWidgets.QFrame(ColorMatch)
        self.min_color.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.min_color.setFrameShadow(QtWidgets.QFrame.Raised)
        self.min_color.setObjectName("min_color")
        self.horizontalLayout_6.addWidget(self.min_color)
        self.mid_color = QtWidgets.QFrame(ColorMatch)
        self.mid_color.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.mid_color.setFrameShadow(QtWidgets.QFrame.Raised)
        self.mid_color.setObjectName("mid_color")
        self.horizontalLayout_6.addWidget(self.mid_color)
        self.max_color = QtWidgets.QFrame(ColorMatch)
        self.max_color.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.max_color.setFrameShadow(QtWidgets.QFrame.Raised)
        self.max_color.setObjectName("max_color")
        self.horizontalLayout_6.addWidget(self.max_color)
        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.retranslateUi(ColorMatch)
        QtCore.QMetaObject.connectSlotsByName(ColorMatch)

    def retranslateUi(self, ColorMatch):
        _translate = QtCore.QCoreApplication.translate
        ColorMatch.setWindowTitle(_translate("ColorMatch", "Form"))
        self.colorButton.setText(_translate("ColorMatch", "Pick Color"))
        self.hSensitivityLabel.setText(_translate("ColorMatch", "Red Range +/-"))
        self.sSensitivityLabel.setText(_translate("ColorMatch", "Green Range +/-"))
        self.vSensitivityLabel.setText(_translate("ColorMatch", "Blue Range +/-"))
        self.colorRangeLabel.setText(_translate("ColorMatch", "Color Range:"))


