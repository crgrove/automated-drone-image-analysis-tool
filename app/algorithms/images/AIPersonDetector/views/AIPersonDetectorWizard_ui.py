# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AIPersonDetectorWizard.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
from PySide6.QtWidgets import (QApplication, QLabel, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_AIPersonDetectorWizard(object):
    def setupUi(self, AIPersonDetectorWizard):
        if not AIPersonDetectorWizard.objectName():
            AIPersonDetectorWizard.setObjectName(u"AIPersonDetectorWizard")
        AIPersonDetectorWizard.resize(618, 176)
        self.verticalLayout_root = QVBoxLayout(AIPersonDetectorWizard)
        self.verticalLayout_root.setObjectName(u"verticalLayout_root")
        self.verticalLayout_root.setContentsMargins(0, 5, 0, 0)
        self.widgetConfidence = QWidget(AIPersonDetectorWizard)
        self.widgetConfidence.setObjectName(u"widgetConfidence")
        self.verticalLayout_confidence = QVBoxLayout(self.widgetConfidence)
        self.verticalLayout_confidence.setSpacing(3)
        self.verticalLayout_confidence.setObjectName(u"verticalLayout_confidence")
        self.labelConfidence = QLabel(self.widgetConfidence)
        self.labelConfidence.setObjectName(u"labelConfidence")
        font = QFont()
        font.setPointSize(12)
        self.labelConfidence.setFont(font)
        self.labelConfidence.setWordWrap(True)

        self.verticalLayout_confidence.addWidget(self.labelConfidence)

        self.labelNote = QLabel(self.widgetConfidence)
        self.labelNote.setObjectName(u"labelNote")
        font1 = QFont()
        font1.setPointSize(10)
        font1.setItalic(True)
        self.labelNote.setFont(font1)
        self.labelNote.setWordWrap(True)

        self.verticalLayout_confidence.addWidget(self.labelNote)

        self.confidenceSliderPlaceholder = QWidget(self.widgetConfidence)
        self.confidenceSliderPlaceholder.setObjectName(u"confidenceSliderPlaceholder")
        self.confidenceSliderPlaceholder.setMinimumSize(QSize(600, 60))

        self.verticalLayout_confidence.addWidget(self.confidenceSliderPlaceholder)


        self.verticalLayout_root.addWidget(self.widgetConfidence)

        self.verticalSpacer_bottom = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_root.addItem(self.verticalSpacer_bottom)


        self.retranslateUi(AIPersonDetectorWizard)

        QMetaObject.connectSlotsByName(AIPersonDetectorWizard)
    # setupUi

    def retranslateUi(self, AIPersonDetectorWizard):
        self.labelConfidence.setText(QCoreApplication.translate("AIPersonDetectorWizard", u"How confident should ADIAT be before marking something as a person?", None))
        self.labelNote.setText(QCoreApplication.translate("AIPersonDetectorWizard", u"Note: A higher setting may increase false positives.", None))
        pass
    # retranslateUi

