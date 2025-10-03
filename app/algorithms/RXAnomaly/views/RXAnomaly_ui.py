# -*- coding: utf-8 -*-

###############################################################################
# Form generated from reading UI file 'RXAnomaly.ui'
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
        QSizePolicy, QSlider, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_RXAnomaly(object):
    def setupUi(self, RXAnomaly):
        if not RXAnomaly.objectName():
            RXAnomaly.setObjectName(u"RXAnomaly")
        RXAnomaly.resize(674, 94)
        self.verticalLayout = QVBoxLayout(RXAnomaly)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.segmentsLabel = QLabel(RXAnomaly)
        self.segmentsLabel.setObjectName(u"segmentsLabel")
        font = QFont()
        font.setPointSize(10)
        self.segmentsLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.segmentsLabel)

        self.segmentsComboBox = QComboBox(RXAnomaly)
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.setObjectName(u"segmentsComboBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.segmentsComboBox.sizePolicy().hasHeightForWidth())
        self.segmentsComboBox.setSizePolicy(sizePolicy)
        self.segmentsComboBox.setMinimumSize(QSize(30, 0))
        self.segmentsComboBox.setFont(font)

        self.horizontalLayout_3.addWidget(self.segmentsComboBox)

        self.horizontalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.sensitivityLabel = QLabel(RXAnomaly)
        self.sensitivityLabel.setObjectName(u"sensitivityLabel")
        self.sensitivityLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.sensitivityLabel)

        self.sensitivitySlider = QSlider(RXAnomaly)
        self.sensitivitySlider.setObjectName(u"sensitivitySlider")
        self.sensitivitySlider.setMinimum(1)
        self.sensitivitySlider.setMaximum(10)
        self.sensitivitySlider.setPageStep(1)
        self.sensitivitySlider.setValue(5)
        self.sensitivitySlider.setSliderPosition(5)
        self.sensitivitySlider.setOrientation(Qt.Horizontal)
        self.sensitivitySlider.setTickPosition(QSlider.TicksBelow)
        self.sensitivitySlider.setTickInterval(1)

        self.horizontalLayout_3.addWidget(self.sensitivitySlider)

        self.sensitivityValueLabel = QLabel(RXAnomaly)
        self.sensitivityValueLabel.setObjectName(u"sensitivityValueLabel")
        self.sensitivityValueLabel.setMinimumSize(QSize(50, 0))
        font1 = QFont()
        font1.setPointSize(10)
        font1.setBold(True)
        self.sensitivityValueLabel.setFont(font1)

        self.horizontalLayout_3.addWidget(self.sensitivityValueLabel)


        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)


        self.verticalLayout.addLayout(self.horizontalLayout_4)


        self.retranslateUi(RXAnomaly)

        QMetaObject.connectSlotsByName(RXAnomaly)
    # setupUi

    def retranslateUi(self, RXAnomaly):
        RXAnomaly.setWindowTitle(QCoreApplication.translate("RXAnomaly", u"Form", None))
        self.segmentsLabel.setText(QCoreApplication.translate("RXAnomaly", u"Image Segments:", None))
        self.segmentsComboBox.setItemText(0, QCoreApplication.translate("RXAnomaly", u"1", None))
        self.segmentsComboBox.setItemText(1, QCoreApplication.translate("RXAnomaly", u"2", None))
        self.segmentsComboBox.setItemText(2, QCoreApplication.translate("RXAnomaly", u"4", None))
        self.segmentsComboBox.setItemText(3, QCoreApplication.translate("RXAnomaly", u"6", None))
        self.segmentsComboBox.setItemText(4, QCoreApplication.translate("RXAnomaly", u"9", None))
        self.segmentsComboBox.setItemText(5, QCoreApplication.translate("RXAnomaly", u"16", None))
        self.segmentsComboBox.setItemText(6, QCoreApplication.translate("RXAnomaly", u"25", None))
        self.segmentsComboBox.setItemText(7, QCoreApplication.translate("RXAnomaly", u"36", None))

        self.sensitivityLabel.setText(QCoreApplication.translate("RXAnomaly", u"Sensitivity:", None))
        self.sensitivityValueLabel.setText(QCoreApplication.translate("RXAnomaly", u"5", None))
    # retranslateUi

