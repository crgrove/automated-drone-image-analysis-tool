# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ThermalAnomaly.ui'
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
    QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_ThermalAnomaly(object):
    def setupUi(self, ThermalAnomaly):
        if not ThermalAnomaly.objectName():
            ThermalAnomaly.setObjectName(u"ThermalAnomaly")
        ThermalAnomaly.resize(674, 94)
        self.verticalLayout = QVBoxLayout(ThermalAnomaly)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.typeLabel = QLabel(ThermalAnomaly)
        self.typeLabel.setObjectName(u"typeLabel")
        font = QFont()
        font.setPointSize(10)
        self.typeLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.typeLabel)

        self.anomalyTypeComboBox = QComboBox(ThermalAnomaly)
        self.anomalyTypeComboBox.addItem("")
        self.anomalyTypeComboBox.addItem("")
        self.anomalyTypeComboBox.addItem("")
        self.anomalyTypeComboBox.setObjectName(u"anomalyTypeComboBox")
        self.anomalyTypeComboBox.setFont(font)

        self.horizontalLayout_3.addWidget(self.anomalyTypeComboBox)

        self.thersholdLabel = QLabel(ThermalAnomaly)
        self.thersholdLabel.setObjectName(u"thersholdLabel")
        self.thersholdLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.thersholdLabel)

        self.anomalySpinBox = QSpinBox(ThermalAnomaly)
        self.anomalySpinBox.setObjectName(u"anomalySpinBox")
        self.anomalySpinBox.setMaximum(7)
        self.anomalySpinBox.setValue(4)

        self.horizontalLayout_3.addWidget(self.anomalySpinBox)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)


        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.segmentsLabel = QLabel(ThermalAnomaly)
        self.segmentsLabel.setObjectName(u"segmentsLabel")
        self.segmentsLabel.setFont(font)

        self.horizontalLayout.addWidget(self.segmentsLabel)

        self.segmentsComboBox = QComboBox(ThermalAnomaly)
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.setObjectName(u"segmentsComboBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.segmentsComboBox.sizePolicy().hasHeightForWidth())
        self.segmentsComboBox.setSizePolicy(sizePolicy)
        self.segmentsComboBox.setMinimumSize(QSize(30, 0))
        self.segmentsComboBox.setFont(font)

        self.horizontalLayout.addWidget(self.segmentsComboBox)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(ThermalAnomaly)

        QMetaObject.connectSlotsByName(ThermalAnomaly)
    # setupUi

    def retranslateUi(self, ThermalAnomaly):
        ThermalAnomaly.setWindowTitle(QCoreApplication.translate("ThermalAnomaly", u"Form", None))
#if QT_CONFIG(tooltip)
        self.typeLabel.setToolTip(QCoreApplication.translate("ThermalAnomaly", u"Type of thermal anomaly to detect in thermal imagery.\n"
"Determines whether to find hot spots, cold spots, or both.", None))
#endif // QT_CONFIG(tooltip)
        self.typeLabel.setText(QCoreApplication.translate("ThermalAnomaly", u"Anomaly Type:", None))
        self.anomalyTypeComboBox.setItemText(0, QCoreApplication.translate("ThermalAnomaly", u"Above or Below Mean", None))
        self.anomalyTypeComboBox.setItemText(1, QCoreApplication.translate("ThermalAnomaly", u"Above Mean", None))
        self.anomalyTypeComboBox.setItemText(2, QCoreApplication.translate("ThermalAnomaly", u"Below Mean", None))

#if QT_CONFIG(tooltip)
        self.anomalyTypeComboBox.setToolTip(QCoreApplication.translate("ThermalAnomaly", u"Select the type of thermal anomaly to detect:\n"
"\u2022 Above or Below Mean: Detects both hot and cold anomalies (default)\n"
"\u2022 Above Mean: Only detects hot spots (temperatures above average)\n"
"\u2022 Below Mean: Only detects cold spots (temperatures below average)\n"
"The algorithm compares each pixel's temperature to the mean temperature of its segment.\n"
"Use \"Above Mean\" for finding heat sources, \"Below Mean\" for cold objects.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.thersholdLabel.setToolTip(QCoreApplication.translate("ThermalAnomaly", u"Temperature threshold for detecting thermal anomalies.\n"
"Measured in standard deviations from the mean temperature.", None))
#endif // QT_CONFIG(tooltip)
        self.thersholdLabel.setText(QCoreApplication.translate("ThermalAnomaly", u"Anomaly Threshold:", None))
#if QT_CONFIG(tooltip)
        self.anomalySpinBox.setToolTip(QCoreApplication.translate("ThermalAnomaly", u"Set the anomaly detection threshold in standard deviations.\n"
"\u2022 Range: 0 to 7 standard deviations\n"
"\u2022 Default: 4\n"
"Defines how different a temperature must be from the mean to be detected:\n"
"\u2022 Lower values (1-2): Very sensitive, detects subtle temperature differences (more detections)\n"
"\u2022 Medium values (3-5): Balanced detection (recommended for most cases)\n"
"\u2022 Higher values (6-7): Only detects extreme temperature differences (fewer detections)\n"
"Example: Value of 4 detects pixels 4 standard deviations above/below mean temperature.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.segmentsLabel.setToolTip(QCoreApplication.translate("ThermalAnomaly", u"Number of segments to divide each thermal image into for analysis.\n"
"Each segment is analyzed independently for local thermal anomalies.\n"
"Performance impact:\n"
"\u2022 Higher number of segments: INCREASES processing time (more segments to analyze)\n"
"\u2022 Lower number of segments: DECREASES processing time (fewer segments to analyze)\n"
"\u2022 1 segment: Fastest processing (analyzes whole image once)\n"
"Higher segment counts improve detection in scenes with temperature gradients.", None))
#endif // QT_CONFIG(tooltip)
        self.segmentsLabel.setText(QCoreApplication.translate("ThermalAnomaly", u"Image Segments:", None))
        self.segmentsComboBox.setItemText(0, QCoreApplication.translate("ThermalAnomaly", u"1", None))
        self.segmentsComboBox.setItemText(1, QCoreApplication.translate("ThermalAnomaly", u"2", None))
        self.segmentsComboBox.setItemText(2, QCoreApplication.translate("ThermalAnomaly", u"4", None))
        self.segmentsComboBox.setItemText(3, QCoreApplication.translate("ThermalAnomaly", u"6", None))
        self.segmentsComboBox.setItemText(4, QCoreApplication.translate("ThermalAnomaly", u"9", None))
        self.segmentsComboBox.setItemText(5, QCoreApplication.translate("ThermalAnomaly", u"16", None))
        self.segmentsComboBox.setItemText(6, QCoreApplication.translate("ThermalAnomaly", u"25", None))
        self.segmentsComboBox.setItemText(7, QCoreApplication.translate("ThermalAnomaly", u"36", None))

#if QT_CONFIG(tooltip)
        self.segmentsComboBox.setToolTip(QCoreApplication.translate("ThermalAnomaly", u"Select the number of segments to divide each thermal image into.\n"
"\u2022 Options: 1, 2, 4, 6, 9, 16, 25, 36 segments\n"
"\u2022 Default: 1 (analyze entire image as one segment)\n"
"The algorithm calculates mean temperature for each segment independently:\n"
"\u2022 1 segment: Global temperature analysis (best for uniform scenes)\n"
"\u2022 More segments: Local temperature analysis (better for varying backgrounds)\n"
"Higher segment counts improve detection in scenes with temperature gradients.\n"
"Recommended: 4-9 segments for typical thermal drone imagery.", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

