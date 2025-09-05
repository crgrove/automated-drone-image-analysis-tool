# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MRMap.ui'
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
    QSizePolicy, QSlider, QSpacerItem, QSpinBox,
    QVBoxLayout, QWidget)

class Ui_MRMap(object):
    def setupUi(self, MRMap):
        if not MRMap.objectName():
            MRMap.setObjectName(u"MRMap")
        MRMap.resize(674, 94)
        self.verticalLayout = QVBoxLayout(MRMap)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.segmentsLabel = QLabel(MRMap)
        self.segmentsLabel.setObjectName(u"segmentsLabel")
        font = QFont()
        font.setPointSize(10)
        self.segmentsLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.segmentsLabel)

        self.segmentsComboBox = QComboBox(MRMap)
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.setObjectName(u"segmentsComboBox")
        self.segmentsComboBox.setMinimumSize(QSize(30, 0))
        self.segmentsComboBox.setFont(font)

        self.horizontalLayout_3.addWidget(self.segmentsComboBox)

        self.horizontalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.windowLabel = QLabel(MRMap)
        self.windowLabel.setObjectName(u"windowLabel")
        self.windowLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.windowLabel)

        self.windowSpinBox = QSpinBox(MRMap)
        self.windowSpinBox.setObjectName(u"windowSpinBox")
        self.windowSpinBox.setMinimum(1)
        self.windowSpinBox.setMaximum(10)
        self.windowSpinBox.setValue(5)

        self.horizontalLayout_3.addWidget(self.windowSpinBox)

        self.horizontalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.thresholdLabel = QLabel(MRMap)
        self.thresholdLabel.setObjectName(u"thresholdLabel")
        self.thresholdLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.thresholdLabel)

        self.thresholdSlider = QSlider(MRMap)
        self.thresholdSlider.setObjectName(u"thresholdSlider")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.thresholdSlider.sizePolicy().hasHeightForWidth())
        self.thresholdSlider.setSizePolicy(sizePolicy)
        self.thresholdSlider.setMinimum(1)
        self.thresholdSlider.setMaximum(200)
        self.thresholdSlider.setPageStep(1)
        self.thresholdSlider.setValue(100)
        self.thresholdSlider.setSliderPosition(100)
        self.thresholdSlider.setOrientation(Qt.Horizontal)
        self.thresholdSlider.setInvertedAppearance(True)
        self.thresholdSlider.setTickPosition(QSlider.TicksBelow)
        self.thresholdSlider.setTickInterval(1)

        self.horizontalLayout_3.addWidget(self.thresholdSlider)

        self.thresholdValueLabel = QLabel(MRMap)
        self.thresholdValueLabel.setObjectName(u"thresholdValueLabel")
        self.thresholdValueLabel.setMinimumSize(QSize(50, 0))
        font1 = QFont()
        font1.setPointSize(10)
        font1.setBold(True)
        self.thresholdValueLabel.setFont(font1)

        self.horizontalLayout_3.addWidget(self.thresholdValueLabel)


        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)


        self.verticalLayout.addLayout(self.horizontalLayout_4)


        self.retranslateUi(MRMap)

        QMetaObject.connectSlotsByName(MRMap)
    # setupUi

    def retranslateUi(self, MRMap):
        MRMap.setWindowTitle(QCoreApplication.translate("MRMap", u"Form", None))
        self.segmentsLabel.setText(QCoreApplication.translate("MRMap", u"Image Segments:", None))
        self.segmentsComboBox.setItemText(0, QCoreApplication.translate("MRMap", u"1", None))
        self.segmentsComboBox.setItemText(1, QCoreApplication.translate("MRMap", u"2", None))
        self.segmentsComboBox.setItemText(2, QCoreApplication.translate("MRMap", u"4", None))
        self.segmentsComboBox.setItemText(3, QCoreApplication.translate("MRMap", u"6", None))
        self.segmentsComboBox.setItemText(4, QCoreApplication.translate("MRMap", u"9", None))
        self.segmentsComboBox.setItemText(5, QCoreApplication.translate("MRMap", u"16", None))
        self.segmentsComboBox.setItemText(6, QCoreApplication.translate("MRMap", u"25", None))
        self.segmentsComboBox.setItemText(7, QCoreApplication.translate("MRMap", u"36", None))

        self.windowLabel.setText(QCoreApplication.translate("MRMap", u"Window Size:", None))
        self.thresholdLabel.setText(QCoreApplication.translate("MRMap", u"Threshold:", None))
        self.thresholdValueLabel.setText(QCoreApplication.translate("MRMap", u"100", None))
    # retranslateUi

