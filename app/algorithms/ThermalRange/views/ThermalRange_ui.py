# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ThermalRange.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_ThermalRange(object):
    def setupUi(self, ThermalRange):
        if not ThermalRange.objectName():
            ThermalRange.setObjectName(u"ThermalRange")
        ThermalRange.resize(674, 94)
        self.verticalLayout = QVBoxLayout(ThermalRange)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.minTempLabel = QLabel(ThermalRange)
        self.minTempLabel.setObjectName(u"minTempLabel")
        font = QFont()
        font.setPointSize(10)
        self.minTempLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.minTempLabel)

        self.minTempSpinBox = QSpinBox(ThermalRange)
        self.minTempSpinBox.setObjectName(u"minTempSpinBox")
        self.minTempSpinBox.setFont(font)
        self.minTempSpinBox.setMinimum(-30)
        self.minTempSpinBox.setMaximum(50)
        self.minTempSpinBox.setValue(35)

        self.horizontalLayout_3.addWidget(self.minTempSpinBox)

        self.horizontalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.maxTempLabel = QLabel(ThermalRange)
        self.maxTempLabel.setObjectName(u"maxTempLabel")
        self.maxTempLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.maxTempLabel)

        self.maxTempSpinBox = QSpinBox(ThermalRange)
        self.maxTempSpinBox.setObjectName(u"maxTempSpinBox")
        self.maxTempSpinBox.setFont(font)
        self.maxTempSpinBox.setMinimum(-30)
        self.maxTempSpinBox.setMaximum(93)
        self.maxTempSpinBox.setValue(40)

        self.horizontalLayout_3.addWidget(self.maxTempSpinBox)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.colorMapLabel = QLabel(ThermalRange)
        self.colorMapLabel.setObjectName(u"colorMapLabel")
        self.colorMapLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.colorMapLabel)

        self.colorMapComboBox = QComboBox(ThermalRange)
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


        self.retranslateUi(ThermalRange)

        QMetaObject.connectSlotsByName(ThermalRange)
    # setupUi

    def retranslateUi(self, ThermalRange):
        ThermalRange.setWindowTitle(QCoreApplication.translate("ThermalRange", u"Form", None))
        self.minTempLabel.setText(QCoreApplication.translate("ThermalRange", u"Minimum Temp (\u00b0C)", None))
        self.maxTempLabel.setText(QCoreApplication.translate("ThermalRange", u"Maximum Temp (\u00b0C)", None))
        self.colorMapLabel.setText(QCoreApplication.translate("ThermalRange", u"Color Map: ", None))
        self.colorMapComboBox.setItemText(0, QCoreApplication.translate("ThermalRange", u"White Hot", None))
        self.colorMapComboBox.setItemText(1, QCoreApplication.translate("ThermalRange", u"Black Hot", None))
        self.colorMapComboBox.setItemText(2, QCoreApplication.translate("ThermalRange", u"Inferno (Iron Red)", None))
        self.colorMapComboBox.setItemText(3, QCoreApplication.translate("ThermalRange", u"Hot (Fulgurite)", None))
        self.colorMapComboBox.setItemText(4, QCoreApplication.translate("ThermalRange", u"Jet (Rainbow2)", None))

    # retranslateUi

