# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'RXAnomalyWizard.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QRadioButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_RXAnomalyWizard(object):
    def setupUi(self, RXAnomalyWizard):
        if not RXAnomalyWizard.objectName():
            RXAnomalyWizard.setObjectName(u"RXAnomalyWizard")
        self.verticalLayout_root = QVBoxLayout(RXAnomalyWizard)
        self.verticalLayout_root.setObjectName(u"verticalLayout_root")
        self.verticalLayout_root.setContentsMargins(0, 5, 0, 0)
        self.widgetComplex = QWidget(RXAnomalyWizard)
        self.widgetComplex.setObjectName(u"widgetComplex")
        self.verticalLayout_complex = QVBoxLayout(self.widgetComplex)
        self.verticalLayout_complex.setObjectName(u"verticalLayout_complex")
        self.labelComplexScenes = QLabel(self.widgetComplex)
        self.labelComplexScenes.setObjectName(u"labelComplexScenes")
        font = QFont()
        font.setPointSize(12)
        self.labelComplexScenes.setFont(font)
        self.labelComplexScenes.setWordWrap(True)

        self.verticalLayout_complex.addWidget(self.labelComplexScenes)

        self.horizontalLayout_complex = QHBoxLayout()
        self.horizontalLayout_complex.setSpacing(20)
        self.horizontalLayout_complex.setObjectName(u"horizontalLayout_complex")
        self.radioComplexNo = QRadioButton(self.widgetComplex)
        self.radioComplexNo.setObjectName(u"radioComplexNo")
        font1 = QFont()
        font1.setPointSize(11)
        self.radioComplexNo.setFont(font1)
        self.radioComplexNo.setChecked(True)

        self.horizontalLayout_complex.addWidget(self.radioComplexNo)

        self.radioComplexYes = QRadioButton(self.widgetComplex)
        self.radioComplexYes.setObjectName(u"radioComplexYes")
        self.radioComplexYes.setFont(font1)

        self.horizontalLayout_complex.addWidget(self.radioComplexYes)

        self.horizontalSpacer_complex = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_complex.addItem(self.horizontalSpacer_complex)


        self.verticalLayout_complex.addLayout(self.horizontalLayout_complex)


        self.verticalLayout_root.addWidget(self.widgetComplex)

        self.widgetAggressiveness = QWidget(RXAnomalyWizard)
        self.widgetAggressiveness.setObjectName(u"widgetAggressiveness")
        self.verticalLayout_aggr = QVBoxLayout(self.widgetAggressiveness)
        self.verticalLayout_aggr.setSpacing(3)
        self.verticalLayout_aggr.setObjectName(u"verticalLayout_aggr")
        self.labelAggressiveness = QLabel(self.widgetAggressiveness)
        self.labelAggressiveness.setObjectName(u"labelAggressiveness")
        self.labelAggressiveness.setFont(font)

        self.verticalLayout_aggr.addWidget(self.labelAggressiveness)

        self.labelNote = QLabel(self.widgetAggressiveness)
        self.labelNote.setObjectName(u"labelNote")
        font2 = QFont()
        font2.setPointSize(11)
        font2.setItalic(True)
        self.labelNote.setFont(font2)
        self.labelNote.setWordWrap(True)

        self.verticalLayout_aggr.addWidget(self.labelNote)

        self.aggressivenessSliderPlaceholder = QWidget(self.widgetAggressiveness)
        self.aggressivenessSliderPlaceholder.setObjectName(u"aggressivenessSliderPlaceholder")
        self.aggressivenessSliderPlaceholder.setMinimumSize(QSize(600, 60))

        self.verticalLayout_aggr.addWidget(self.aggressivenessSliderPlaceholder)


        self.verticalLayout_root.addWidget(self.widgetAggressiveness)

        self.verticalSpacer_bottom = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_root.addItem(self.verticalSpacer_bottom)


        self.retranslateUi(RXAnomalyWizard)

        QMetaObject.connectSlotsByName(RXAnomalyWizard)
    # setupUi

    def retranslateUi(self, RXAnomalyWizard):
        self.labelComplexScenes.setText(QCoreApplication.translate("RXAnomalyWizard", u"Do your images contain complex scenes with buildings, vehicles, or mixed manmade ground cover?", None))
        self.radioComplexNo.setText(QCoreApplication.translate("RXAnomalyWizard", u"No", None))
        self.radioComplexYes.setText(QCoreApplication.translate("RXAnomalyWizard", u"Yes", None))
        self.labelAggressiveness.setText(QCoreApplication.translate("RXAnomalyWizard", u"How aggressively should ADIAT be searching for anomalies?", None))
        self.labelNote.setText(QCoreApplication.translate("RXAnomalyWizard", u"Note: A higher setting will find more potential anomalies but may also increase false positives.", None))
        pass
    # retranslateUi

