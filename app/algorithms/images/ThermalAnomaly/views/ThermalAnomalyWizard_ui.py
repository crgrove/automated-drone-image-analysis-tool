# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ThermalAnomalyWizard.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QRadioButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_ThermalAnomalyWizard(object):
    def setupUi(self, ThermalAnomalyWizard):
        if not ThermalAnomalyWizard.objectName():
            ThermalAnomalyWizard.setObjectName(u"ThermalAnomalyWizard")
        ThermalAnomalyWizard.resize(800, 296)
        self.verticalLayout_root = QVBoxLayout(ThermalAnomalyWizard)
        self.verticalLayout_root.setObjectName(u"verticalLayout_root")
        self.verticalLayout_root.setContentsMargins(0, 5, 0, 0)
        self.widgetComplex = QWidget(ThermalAnomalyWizard)
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

        self.widgetType = QWidget(ThermalAnomalyWizard)
        self.widgetType.setObjectName(u"widgetType")
        self.verticalLayout_type = QVBoxLayout(self.widgetType)
        self.verticalLayout_type.setObjectName(u"verticalLayout_type")
        self.labelAnomalyType = QLabel(self.widgetType)
        self.labelAnomalyType.setObjectName(u"labelAnomalyType")
        self.labelAnomalyType.setFont(font)

        self.verticalLayout_type.addWidget(self.labelAnomalyType)

        self.horizontalLayout_type = QHBoxLayout()
        self.horizontalLayout_type.setSpacing(20)
        self.horizontalLayout_type.setObjectName(u"horizontalLayout_type")
        self.radioTypeHot = QRadioButton(self.widgetType)
        self.radioTypeHot.setObjectName(u"radioTypeHot")
        self.radioTypeHot.setFont(font1)

        self.horizontalLayout_type.addWidget(self.radioTypeHot)

        self.radioTypeCold = QRadioButton(self.widgetType)
        self.radioTypeCold.setObjectName(u"radioTypeCold")
        self.radioTypeCold.setFont(font1)

        self.horizontalLayout_type.addWidget(self.radioTypeCold)

        self.radioTypeBoth = QRadioButton(self.widgetType)
        self.radioTypeBoth.setObjectName(u"radioTypeBoth")
        self.radioTypeBoth.setFont(font1)
        self.radioTypeBoth.setChecked(True)

        self.horizontalLayout_type.addWidget(self.radioTypeBoth)

        self.horizontalSpacer_type = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_type.addItem(self.horizontalSpacer_type)


        self.verticalLayout_type.addLayout(self.horizontalLayout_type)


        self.verticalLayout_root.addWidget(self.widgetType)

        self.widgetAggressiveness = QWidget(ThermalAnomalyWizard)
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
        font2.setPointSize(10)
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


        self.retranslateUi(ThermalAnomalyWizard)

        QMetaObject.connectSlotsByName(ThermalAnomalyWizard)
    # setupUi

    def retranslateUi(self, ThermalAnomalyWizard):
        self.labelComplexScenes.setText(QCoreApplication.translate("ThermalAnomalyWizard", u"Do your images contain complex scenes with buildings, vehicles, or mixed manmade ground cover?", None))
        self.radioComplexNo.setText(QCoreApplication.translate("ThermalAnomalyWizard", u"No", None))
        self.radioComplexYes.setText(QCoreApplication.translate("ThermalAnomalyWizard", u"Yes", None))
        self.labelAnomalyType.setText(QCoreApplication.translate("ThermalAnomalyWizard", u"What type of anomalies are you looking for?", None))
        self.radioTypeHot.setText(QCoreApplication.translate("ThermalAnomalyWizard", u"Warmer than surroundings", None))
        self.radioTypeCold.setText(QCoreApplication.translate("ThermalAnomalyWizard", u"Cooler than surroundings", None))
        self.radioTypeBoth.setText(QCoreApplication.translate("ThermalAnomalyWizard", u"Both", None))
        self.labelAggressiveness.setText(QCoreApplication.translate("ThermalAnomalyWizard", u"How aggressively should ADIAT be searching for anomalies?", None))
        self.labelNote.setText(QCoreApplication.translate("ThermalAnomalyWizard", u"Note: A higher setting will find more potential anomalies but may also increase false positives.", None))
        pass
    # retranslateUi


