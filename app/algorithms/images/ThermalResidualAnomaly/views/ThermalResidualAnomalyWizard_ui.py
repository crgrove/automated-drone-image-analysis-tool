# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ThermalResidualAnomalyWizard.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
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

class Ui_ThermalResidualAnomalyWizard(object):
    def setupUi(self, ThermalResidualAnomalyWizard):
        if not ThermalResidualAnomalyWizard.objectName():
            ThermalResidualAnomalyWizard.setObjectName(u"ThermalResidualAnomalyWizard")
        ThermalResidualAnomalyWizard.resize(618, 300)
        self.verticalLayout_root = QVBoxLayout(ThermalResidualAnomalyWizard)
        self.verticalLayout_root.setObjectName(u"verticalLayout_root")
        self.verticalLayout_root.setContentsMargins(0, 5, 0, 0)
        self.widgetType = QWidget(ThermalResidualAnomalyWizard)
        self.widgetType.setObjectName(u"widgetType")
        self.verticalLayout_type = QVBoxLayout(self.widgetType)
        self.verticalLayout_type.setObjectName(u"verticalLayout_type")
        self.labelAnomalyType = QLabel(self.widgetType)
        self.labelAnomalyType.setObjectName(u"labelAnomalyType")
        font = QFont()
        font.setPointSize(12)
        self.labelAnomalyType.setFont(font)

        self.verticalLayout_type.addWidget(self.labelAnomalyType)

        self.horizontalLayout_type = QHBoxLayout()
        self.horizontalLayout_type.setSpacing(20)
        self.horizontalLayout_type.setObjectName(u"horizontalLayout_type")
        self.radioTypeHot = QRadioButton(self.widgetType)
        self.radioTypeHot.setObjectName(u"radioTypeHot")
        font1 = QFont()
        font1.setPointSize(11)
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

        self.widgetAggressiveness = QWidget(ThermalResidualAnomalyWizard)
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


        self.retranslateUi(ThermalResidualAnomalyWizard)

        QMetaObject.connectSlotsByName(ThermalResidualAnomalyWizard)
    # setupUi

    def retranslateUi(self, ThermalResidualAnomalyWizard):
        self.labelAnomalyType.setText(QCoreApplication.translate("ThermalResidualAnomalyWizard", u"What type of anomalies are you looking for?", None))
        self.radioTypeHot.setText(QCoreApplication.translate("ThermalResidualAnomalyWizard", u"Warmer than surroundings", None))
        self.radioTypeCold.setText(QCoreApplication.translate("ThermalResidualAnomalyWizard", u"Cooler than surroundings", None))
        self.radioTypeBoth.setText(QCoreApplication.translate("ThermalResidualAnomalyWizard", u"Both", None))
        self.labelAggressiveness.setText(QCoreApplication.translate("ThermalResidualAnomalyWizard", u"How aggressively should ADIAT be searching for anomalies?", None))
        self.labelNote.setText(QCoreApplication.translate("ThermalResidualAnomalyWizard", u"Note: A higher setting will find more potential anomalies but may also increase false positives.", None))
        pass
    # retranslateUi

