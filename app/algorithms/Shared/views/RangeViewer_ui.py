# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\charl\source\repos\crgrove\adiat_ai\resources/views/algorithms/RangeViewer.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ColorRangeViewer(object):
    def setupUi(self, ColorRangeViewer):
        ColorRangeViewer.setObjectName("ColorRangeViewer")
        ColorRangeViewer.resize(1200, 700)
        self.verticalLayout = QtWidgets.QVBoxLayout(ColorRangeViewer)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.selectedWidget = QtWidgets.QWidget(ColorRangeViewer)
        self.selectedWidget.setObjectName("selectedWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.selectedWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.selectedLabel = QtWidgets.QLabel(self.selectedWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.selectedLabel.sizePolicy().hasHeightForWidth())
        self.selectedLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.selectedLabel.setFont(font)
        self.selectedLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.selectedLabel.setObjectName("selectedLabel")
        self.verticalLayout_2.addWidget(self.selectedLabel)
        self.selectedLayout = QtWidgets.QHBoxLayout()
        self.selectedLayout.setSpacing(0)
        self.selectedLayout.setObjectName("selectedLayout")
        self.verticalLayout_2.addLayout(self.selectedLayout)
        self.verticalLayout.addWidget(self.selectedWidget)
        self.widget = QtWidgets.QWidget(ColorRangeViewer)
        self.widget.setObjectName("widget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtWidgets.QLabel(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.unselectedLayout = QtWidgets.QHBoxLayout()
        self.unselectedLayout.setSpacing(0)
        self.unselectedLayout.setObjectName("unselectedLayout")
        self.verticalLayout_3.addLayout(self.unselectedLayout)
        self.verticalLayout.addWidget(self.widget)

        self.retranslateUi(ColorRangeViewer)
        QtCore.QMetaObject.connectSlotsByName(ColorRangeViewer)

    def retranslateUi(self, ColorRangeViewer):
        _translate = QtCore.QCoreApplication.translate
        ColorRangeViewer.setWindowTitle(_translate("ColorRangeViewer", "Color Range Viewer"))
        self.selectedLabel.setText(_translate("ColorRangeViewer", "Selected"))
        self.label.setText(_translate("ColorRangeViewer", "Unselected"))
