# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ThermalRangeWizard.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_ThermalRangeWizard(object):
    def setupUi(self, ThermalRangeWizard):
        if not ThermalRangeWizard.objectName():
            ThermalRangeWizard.setObjectName(u"ThermalRangeWizard")
        ThermalRangeWizard.resize(407, 165)
        self.verticalLayout_root = QVBoxLayout(ThermalRangeWizard)
        self.verticalLayout_root.setObjectName(u"verticalLayout_root")
        self.verticalLayout_root.setContentsMargins(0, 5, 0, 0)
        self.labelQuestion = QLabel(ThermalRangeWizard)
        self.labelQuestion.setObjectName(u"labelQuestion")
        font = QFont()
        font.setPointSize(12)
        self.labelQuestion.setFont(font)
        self.labelQuestion.setWordWrap(True)

        self.verticalLayout_root.addWidget(self.labelQuestion)

        self.rangeSliderPlaceholder = QWidget(ThermalRangeWizard)
        self.rangeSliderPlaceholder.setObjectName(u"rangeSliderPlaceholder")
        self.rangeSliderPlaceholder.setMinimumSize(QSize(800, 120))

        self.verticalLayout_root.addWidget(self.rangeSliderPlaceholder)

        self.verticalSpacer_bottom = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_root.addItem(self.verticalSpacer_bottom)


        self.retranslateUi(ThermalRangeWizard)

        QMetaObject.connectSlotsByName(ThermalRangeWizard)
    # setupUi

    def retranslateUi(self, ThermalRangeWizard):
        self.labelQuestion.setText(QCoreApplication.translate("ThermalRangeWizard", u"What range of temperatures should ADIAT look for?", None))
        pass
    # retranslateUi

