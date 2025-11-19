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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QSpacerItem, QSpinBox, QVBoxLayout, QWidget)

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


        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)


        self.verticalLayout.addLayout(self.horizontalLayout_4)


        self.retranslateUi(ThermalRange)

        QMetaObject.connectSlotsByName(ThermalRange)
    # setupUi

    def retranslateUi(self, ThermalRange):
        ThermalRange.setWindowTitle(QCoreApplication.translate("ThermalRange", u"Form", None))
#if QT_CONFIG(tooltip)
        self.minTempLabel.setToolTip(QCoreApplication.translate("ThermalRange", u"Minimum temperature threshold for detection in thermal images.\n"
"\u2022 Range: -30\u00b0C to 50\u00b0C\n"
"\u2022 Default: 35\u00b0C\n"
"Defines the lower bound of the temperature detection range:\n"
"\u2022 Lower values: INCREASE detections - accepts cooler objects\n"
"\u2022 Higher values: DECREASE detections - only warmer objects detected\n"
"Combined with Maximum Temp to create a detection range (e.g., 35-40\u00b0C for human body temperature).", None))
#endif // QT_CONFIG(tooltip)
        self.minTempLabel.setText(QCoreApplication.translate("ThermalRange", u"Minimum Temp (\u00b0C)", None))
#if QT_CONFIG(tooltip)
        self.minTempSpinBox.setToolTip(QCoreApplication.translate("ThermalRange", u"Set the minimum temperature for detection in Celsius.\n"
"\u2022 Range: -30\u00b0C to 50\u00b0C\n"
"\u2022 Default: 35\u00b0C\n"
"Pixels with temperatures at or above this threshold will be detected.\n"
"\u2022 Lower values: Detect cooler objects (more detections)\n"
"\u2022 Higher values: Only detect warmer objects (fewer detections)\n"
"Note: Temperature displayed in Celsius, converted based on Preferences setting.\n"
"Use for finding objects within a specific temperature range (e.g., people 35-40\u00b0C).", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.maxTempLabel.setToolTip(QCoreApplication.translate("ThermalRange", u"Maximum temperature threshold for detection in thermal images.\n"
"\u2022 Range: -30\u00b0C to 93\u00b0C\n"
"\u2022 Default: 40\u00b0C\n"
"Defines the upper bound of the temperature detection range:\n"
"\u2022 Lower values: DECREASE detections - only cooler objects detected\n"
"\u2022 Higher values: INCREASE detections - accepts warmer objects\n"
"Combined with Minimum Temp to create a detection range (e.g., 35-40\u00b0C for human body temperature).", None))
#endif // QT_CONFIG(tooltip)
        self.maxTempLabel.setText(QCoreApplication.translate("ThermalRange", u"Maximum Temp (\u00b0C)", None))
#if QT_CONFIG(tooltip)
        self.maxTempSpinBox.setToolTip(QCoreApplication.translate("ThermalRange", u"Set the maximum temperature for detection in Celsius.\n"
"\u2022 Range: -30\u00b0C to 93\u00b0C\n"
"\u2022 Default: 40\u00b0C\n"
"Pixels with temperatures at or below this threshold will be detected.\n"
"\u2022 Lower values: Only detect cooler objects (fewer detections)\n"
"\u2022 Higher values: Detect warmer objects (more detections)\n"
"Note: Temperature displayed in Celsius, converted based on Preferences setting.\n"
"Detection occurs for pixels between minimum and maximum temperatures (inclusive).", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

