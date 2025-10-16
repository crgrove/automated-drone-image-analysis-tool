# -*- coding: utf-8 -*-

###############################################################################
# Form generated from reading UI file 'ThermalAnomaly.ui'
#
# Created by: Qt User Interface Compiler version 6.9.2
#
# WARNING! All changes made in this file will be lost when recompiling UI file!
###############################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
        QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
        QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
        QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_ThermalAnomaly(object):
    def setupUi(self, ThermalAnomaly):
        if not ThermalAnomaly.objectName():
            ThermalAnomaly.setObjectName(u"ThermalAnomaly")
        ThermalAnomaly.resize(674, 94)
        self.verticalLayout = QVBoxLayout(ThermalAnomaly)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.typeLabel = QLabel(ThermalAnomaly)
        self.typeLabel.setObjectName(u"typeLabel")
        font = QFont()
        font.setPointSize(10)
        self.typeLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.typeLabel)

        self.anomalyTypeComboBox = QComboBox(ThermalAnomaly)
        self.anomalyTypeComboBox.addItem("")
        self.anomalyTypeComboBox.addItem("")
        self.anomalyTypeComboBox.addItem("")
        self.anomalyTypeComboBox.setObjectName(u"anomalyTypeComboBox")
        self.anomalyTypeComboBox.setFont(font)

        self.horizontalLayout_3.addWidget(self.anomalyTypeComboBox)

        self.thersholdLabel = QLabel(ThermalAnomaly)
        self.thersholdLabel.setObjectName(u"thersholdLabel")
        self.thersholdLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.thersholdLabel)

        self.anomalySpinBox = QSpinBox(ThermalAnomaly)
        self.anomalySpinBox.setObjectName(u"anomalySpinBox")
        self.anomalySpinBox.setMaximum(7)
        self.anomalySpinBox.setValue(4)

        self.horizontalLayout_3.addWidget(self.anomalySpinBox)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.colorMapLabel = QLabel(ThermalAnomaly)
        self.colorMapLabel.setObjectName(u"colorMapLabel")
        self.colorMapLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.colorMapLabel)

        self.colorMapComboBox = QComboBox(ThermalAnomaly)
        self.colorMapComboBox.addItem("")
        self.colorMapComboBox.addItem("")
        self.colorMapComboBox.addItem("")
        self.colorMapComboBox.addItem("")
        self.colorMapComboBox.addItem("")
        self.colorMapComboBox.setObjectName(u"colorMapComboBox")
        self.colorMapComboBox.setFont(font)

        self.horizontalLayout_3.addWidget(self.colorMapComboBox)


        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.segmentsLabel = QLabel(ThermalAnomaly)
        self.segmentsLabel.setObjectName(u"segmentsLabel")
        self.segmentsLabel.setFont(font)

        self.horizontalLayout.addWidget(self.segmentsLabel)

        self.segmentsComboBox = QComboBox(ThermalAnomaly)
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.setObjectName(u"segmentsComboBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.segmentsComboBox.sizePolicy().hasHeightForWidth())
        self.segmentsComboBox.setSizePolicy(sizePolicy)
        self.segmentsComboBox.setMinimumSize(QSize(30, 0))
        self.segmentsComboBox.setFont(font)

        self.horizontalLayout.addWidget(self.segmentsComboBox)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(ThermalAnomaly)

        QMetaObject.connectSlotsByName(ThermalAnomaly)
    # setupUi

    def retranslateUi(self, ThermalAnomaly):
        ThermalAnomaly.setWindowTitle(QCoreApplication.translate("ThermalAnomaly", u"Form", None))
        self.typeLabel.setText(QCoreApplication.translate("ThermalAnomaly", u"Anomaly Type:", None))
        self.anomalyTypeComboBox.setItemText(0, QCoreApplication.translate("ThermalAnomaly", u"Above or Below Mean", None))
        self.anomalyTypeComboBox.setItemText(1, QCoreApplication.translate("ThermalAnomaly", u"Above Mean", None))
        self.anomalyTypeComboBox.setItemText(2, QCoreApplication.translate("ThermalAnomaly", u"Below Mean", None))

        self.thersholdLabel.setText(QCoreApplication.translate("ThermalAnomaly", u"Anomaly Threshold:", None))
        self.colorMapLabel.setText(QCoreApplication.translate("ThermalAnomaly", u"Color Map: ", None))
        self.colorMapComboBox.setItemText(0, QCoreApplication.translate("ThermalAnomaly", u"White Hot", None))
        self.colorMapComboBox.setItemText(1, QCoreApplication.translate("ThermalAnomaly", u"Black Hot", None))
        self.colorMapComboBox.setItemText(2, QCoreApplication.translate("ThermalAnomaly", u"Inferno (Iron Red)", None))
        self.colorMapComboBox.setItemText(3, QCoreApplication.translate("ThermalAnomaly", u"Hot (Fulgurite)", None))
        self.colorMapComboBox.setItemText(4, QCoreApplication.translate("ThermalAnomaly", u"Jet (Rainbow2)", None))

        self.segmentsLabel.setText(QCoreApplication.translate("ThermalAnomaly", u"Image Segments:", None))
        self.segmentsComboBox.setItemText(0, QCoreApplication.translate("ThermalAnomaly", u"1", None))
        self.segmentsComboBox.setItemText(1, QCoreApplication.translate("ThermalAnomaly", u"2", None))
        self.segmentsComboBox.setItemText(2, QCoreApplication.translate("ThermalAnomaly", u"4", None))
        self.segmentsComboBox.setItemText(3, QCoreApplication.translate("ThermalAnomaly", u"6", None))
        self.segmentsComboBox.setItemText(4, QCoreApplication.translate("ThermalAnomaly", u"9", None))
        self.segmentsComboBox.setItemText(5, QCoreApplication.translate("ThermalAnomaly", u"16", None))
        self.segmentsComboBox.setItemText(6, QCoreApplication.translate("ThermalAnomaly", u"25", None))
        self.segmentsComboBox.setItemText(7, QCoreApplication.translate("ThermalAnomaly", u"36", None))

    # retranslateUi

