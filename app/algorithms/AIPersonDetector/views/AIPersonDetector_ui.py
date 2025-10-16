# -*- coding: utf-8 -*-

###############################################################################
# Form generated from reading UI file 'AIPersonDetector.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
        QSlider, QVBoxLayout, QWidget)
from . import resources_rc

class Ui_AIPersonDetector(object):
    def setupUi(self, AIPersonDetector):
        if not AIPersonDetector.objectName():
            AIPersonDetector.setObjectName(u"AIPersonDetector")
        AIPersonDetector.resize(674, 70)
        self.verticalLayout_4 = QVBoxLayout(AIPersonDetector)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.confidenceLabel = QLabel(AIPersonDetector)
        self.confidenceLabel.setObjectName(u"confidenceLabel")
        font = QFont()
        font.setPointSize(10)
        self.confidenceLabel.setFont(font)

        self.horizontalLayout.addWidget(self.confidenceLabel)

        self.confidenceSlider = QSlider(AIPersonDetector)
        self.confidenceSlider.setObjectName(u"confidenceSlider")
        self.confidenceSlider.setMinimum(-1)
        self.confidenceSlider.setMaximum(100)
        self.confidenceSlider.setPageStep(1)
        self.confidenceSlider.setValue(50)
        self.confidenceSlider.setOrientation(Qt.Horizontal)
        self.confidenceSlider.setTickPosition(QSlider.TicksBelow)
        self.confidenceSlider.setTickInterval(1)

        self.horizontalLayout.addWidget(self.confidenceSlider)

        self.confidenceValueLabel = QLabel(AIPersonDetector)
        self.confidenceValueLabel.setObjectName(u"confidenceValueLabel")
        font1 = QFont()
        font1.setPointSize(10)
        font1.setBold(True)
        self.confidenceValueLabel.setFont(font1)

        self.horizontalLayout.addWidget(self.confidenceValueLabel)


        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.GPULabel = QLabel(AIPersonDetector)
        self.GPULabel.setObjectName(u"GPULabel")
        font2 = QFont()
        font2.setPointSize(9)
        self.GPULabel.setFont(font2)

        self.verticalLayout_4.addWidget(self.GPULabel)


        self.retranslateUi(AIPersonDetector)

        QMetaObject.connectSlotsByName(AIPersonDetector)
    # setupUi

    def retranslateUi(self, AIPersonDetector):
        AIPersonDetector.setWindowTitle(QCoreApplication.translate("AIPersonDetector", u"Form", None))
        self.confidenceLabel.setText(QCoreApplication.translate("AIPersonDetector", u"Confidence Threshold", None))
        self.confidenceValueLabel.setText(QCoreApplication.translate("AIPersonDetector", u"50", None))
        self.GPULabel.setText(QCoreApplication.translate("AIPersonDetector", u"GPU Label", None))
    # retranslateUi

