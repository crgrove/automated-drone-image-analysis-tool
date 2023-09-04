# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\xampp7\htdocs\ADIAT\resources/views/algorithms\ColorAnomaly.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ColorAnomaly(object):
    def setupUi(self, ColorAnomaly):
        ColorAnomaly.setObjectName("ColorAnomaly")
        ColorAnomaly.resize(674, 94)
        self.verticalLayout = QtWidgets.QVBoxLayout(ColorAnomaly)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.thresholdLabel = QtWidgets.QLabel(ColorAnomaly)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.thresholdLabel.setFont(font)
        self.thresholdLabel.setObjectName("thresholdLabel")
        self.horizontalLayout_3.addWidget(self.thresholdLabel)
        self.thresholdSlider = QtWidgets.QSlider(ColorAnomaly)
        self.thresholdSlider.setMaximum(1000)
        self.thresholdSlider.setSliderPosition(999)
        self.thresholdSlider.setOrientation(QtCore.Qt.Horizontal)
        self.thresholdSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.thresholdSlider.setObjectName("thresholdSlider")
        self.horizontalLayout_3.addWidget(self.thresholdSlider)
        self.thresholdValueLabel = QtWidgets.QLabel(ColorAnomaly)
        self.thresholdValueLabel.setMinimumSize(QtCore.QSize(50, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.thresholdValueLabel.setFont(font)
        self.thresholdValueLabel.setObjectName("thresholdValueLabel")
        self.horizontalLayout_3.addWidget(self.thresholdValueLabel)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)
        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.retranslateUi(ColorAnomaly)
        QtCore.QMetaObject.connectSlotsByName(ColorAnomaly)

    def retranslateUi(self, ColorAnomaly):
        _translate = QtCore.QCoreApplication.translate
        ColorAnomaly.setWindowTitle(_translate("ColorAnomaly", "Form"))
        self.thresholdLabel.setText(_translate("ColorAnomaly", "Threshold: "))
        self.thresholdValueLabel.setText(_translate("ColorAnomaly", ".999"))


