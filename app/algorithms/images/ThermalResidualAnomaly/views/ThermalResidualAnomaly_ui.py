# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ThermalResidualAnomaly.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QSizePolicy, QSlider, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_ThermalResidualAnomaly(object):
    def setupUi(self, ThermalResidualAnomaly):
        if not ThermalResidualAnomaly.objectName():
            ThermalResidualAnomaly.setObjectName(u"ThermalResidualAnomaly")
        ThermalResidualAnomaly.resize(674, 94)
        self.verticalLayout = QVBoxLayout(ThermalResidualAnomaly)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.typeLabel = QLabel(ThermalResidualAnomaly)
        self.typeLabel.setObjectName(u"typeLabel")
        font = QFont()
        font.setPointSize(10)
        self.typeLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.typeLabel)

        self.anomalyTypeComboBox = QComboBox(ThermalResidualAnomaly)
        self.anomalyTypeComboBox.addItem("")
        self.anomalyTypeComboBox.addItem("")
        self.anomalyTypeComboBox.addItem("")
        self.anomalyTypeComboBox.setObjectName(u"anomalyTypeComboBox")
        self.anomalyTypeComboBox.setFont(font)

        self.horizontalLayout_3.addWidget(self.anomalyTypeComboBox)

        self.horizontalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.sensitivityLabel = QLabel(ThermalResidualAnomaly)
        self.sensitivityLabel.setObjectName(u"sensitivityLabel")
        self.sensitivityLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.sensitivityLabel)

        self.sensitivitySlider = QSlider(ThermalResidualAnomaly)
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

        self.sensitivityValueLabel = QLabel(ThermalResidualAnomaly)
        self.sensitivityValueLabel.setObjectName(u"sensitivityValueLabel")
        self.sensitivityValueLabel.setMinimumSize(QSize(50, 0))
        font1 = QFont()
        font1.setPointSize(10)
        font1.setBold(True)
        self.sensitivityValueLabel.setFont(font1)

        self.horizontalLayout_3.addWidget(self.sensitivityValueLabel)


        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)


        self.verticalLayout.addLayout(self.horizontalLayout_4)


        self.retranslateUi(ThermalResidualAnomaly)

        QMetaObject.connectSlotsByName(ThermalResidualAnomaly)
    # setupUi

    def retranslateUi(self, ThermalResidualAnomaly):
        ThermalResidualAnomaly.setWindowTitle(QCoreApplication.translate("ThermalResidualAnomaly", u"Form", None))
#if QT_CONFIG(tooltip)
        self.typeLabel.setToolTip(QCoreApplication.translate("ThermalResidualAnomaly", u"Type of local thermal residual anomaly to detect in radiometric imagery.\n"
"Determines whether to find warm anomalies, cool anomalies, or both.", None))
#endif // QT_CONFIG(tooltip)
        self.typeLabel.setText(QCoreApplication.translate("ThermalResidualAnomaly", u"Anomaly Type:", None))
        self.anomalyTypeComboBox.setItemText(0, QCoreApplication.translate("ThermalResidualAnomaly", u"Above or Below Mean", None))
        self.anomalyTypeComboBox.setItemText(1, QCoreApplication.translate("ThermalResidualAnomaly", u"Above Mean", None))
        self.anomalyTypeComboBox.setItemText(2, QCoreApplication.translate("ThermalResidualAnomaly", u"Below Mean", None))

#if QT_CONFIG(tooltip)
        self.anomalyTypeComboBox.setToolTip(QCoreApplication.translate("ThermalResidualAnomaly", u"Select the type of thermal residual anomaly to detect:\n"
"\u2022 Above or Below Mean: Detects both hot and cold anomalies (default)\n"
"\u2022 Above Mean: Only detects hot spots (temperatures above average)\n"
"\u2022 Below Mean: Only detects cold spots (temperatures below average)\n"
"The algorithm compares each pixel's temperature to its local background estimate.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.sensitivityLabel.setToolTip(QCoreApplication.translate("ThermalResidualAnomaly", u"Detection sensitivity for thermal residual anomalies.\n"
"\u2022 Range: 1 to 10\n"
"\u2022 Default: 5\n"
"Lower values are more conservative (fewer detections).\n"
"Higher values are more aggressive (more detections).", None))
#endif // QT_CONFIG(tooltip)
        self.sensitivityLabel.setText(QCoreApplication.translate("ThermalResidualAnomaly", u"Sensitivity:", None))
#if QT_CONFIG(tooltip)
        self.sensitivitySlider.setToolTip(QCoreApplication.translate("ThermalResidualAnomaly", u"Adjust detection sensitivity for local thermal residual anomalies.\n"
"\u2022 1-3: Conservative\n"
"\u2022 4-6: Moderate\n"
"\u2022 7-10: Aggressive", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.sensitivityValueLabel.setToolTip(QCoreApplication.translate("ThermalResidualAnomaly", u"Current sensitivity level for residual anomaly detection.", None))
#endif // QT_CONFIG(tooltip)
        self.sensitivityValueLabel.setText(QCoreApplication.translate("ThermalResidualAnomaly", u"5", None))
    # retranslateUi

