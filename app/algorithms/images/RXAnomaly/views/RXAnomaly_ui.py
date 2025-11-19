# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'RXAnomaly.ui'
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
    QSizePolicy, QSlider, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_RXAnomaly(object):
    def setupUi(self, RXAnomaly):
        if not RXAnomaly.objectName():
            RXAnomaly.setObjectName(u"RXAnomaly")
        RXAnomaly.resize(674, 94)
        self.verticalLayout = QVBoxLayout(RXAnomaly)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.segmentsLabel = QLabel(RXAnomaly)
        self.segmentsLabel.setObjectName(u"segmentsLabel")
        font = QFont()
        font.setPointSize(10)
        self.segmentsLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.segmentsLabel)

        self.segmentsComboBox = QComboBox(RXAnomaly)
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.setObjectName(u"segmentsComboBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.segmentsComboBox.sizePolicy().hasHeightForWidth())
        self.segmentsComboBox.setSizePolicy(sizePolicy)
        self.segmentsComboBox.setMinimumSize(QSize(30, 0))
        self.segmentsComboBox.setFont(font)

        self.horizontalLayout_3.addWidget(self.segmentsComboBox)

        self.horizontalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.sensitivityLabel = QLabel(RXAnomaly)
        self.sensitivityLabel.setObjectName(u"sensitivityLabel")
        self.sensitivityLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.sensitivityLabel)

        self.sensitivitySlider = QSlider(RXAnomaly)
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

        self.sensitivityValueLabel = QLabel(RXAnomaly)
        self.sensitivityValueLabel.setObjectName(u"sensitivityValueLabel")
        self.sensitivityValueLabel.setMinimumSize(QSize(50, 0))
        font1 = QFont()
        font1.setPointSize(10)
        font1.setBold(True)
        self.sensitivityValueLabel.setFont(font1)

        self.horizontalLayout_3.addWidget(self.sensitivityValueLabel)


        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)


        self.verticalLayout.addLayout(self.horizontalLayout_4)


        self.retranslateUi(RXAnomaly)

        QMetaObject.connectSlotsByName(RXAnomaly)
    # setupUi

    def retranslateUi(self, RXAnomaly):
        RXAnomaly.setWindowTitle(QCoreApplication.translate("RXAnomaly", u"Form", None))
#if QT_CONFIG(tooltip)
        self.segmentsLabel.setToolTip(QCoreApplication.translate("RXAnomaly", u"Number of segments to divide each image into for analysis.\n"
"The RX algorithm analyzes each segment independently to detect local anomalies.\n"
"Performance impact:\n"
"\u2022 Higher number of segments: INCREASES processing time (more segments to analyze)\n"
"\u2022 Lower number of segments: DECREASES processing time (fewer segments to analyze)\n"
"\u2022 1 segment: Fastest processing (analyzes whole image once)\n"
"Higher segment counts improve detection in images with varying backgrounds.", None))
#endif // QT_CONFIG(tooltip)
        self.segmentsLabel.setText(QCoreApplication.translate("RXAnomaly", u"Image Segments:", None))
        self.segmentsComboBox.setItemText(0, QCoreApplication.translate("RXAnomaly", u"1", None))
        self.segmentsComboBox.setItemText(1, QCoreApplication.translate("RXAnomaly", u"2", None))
        self.segmentsComboBox.setItemText(2, QCoreApplication.translate("RXAnomaly", u"4", None))
        self.segmentsComboBox.setItemText(3, QCoreApplication.translate("RXAnomaly", u"6", None))
        self.segmentsComboBox.setItemText(4, QCoreApplication.translate("RXAnomaly", u"9", None))
        self.segmentsComboBox.setItemText(5, QCoreApplication.translate("RXAnomaly", u"16", None))
        self.segmentsComboBox.setItemText(6, QCoreApplication.translate("RXAnomaly", u"25", None))
        self.segmentsComboBox.setItemText(7, QCoreApplication.translate("RXAnomaly", u"36", None))

#if QT_CONFIG(tooltip)
        self.segmentsComboBox.setToolTip(QCoreApplication.translate("RXAnomaly", u"Select the number of segments to divide each image into.\n"
"\u2022 Options: 1, 2, 4, 6, 9, 16, 25, 36 segments\n"
"\u2022 Default: 1 (analyze entire image as one segment)\n"
"The RX Anomaly algorithm uses statistical analysis to detect unusual pixels:\n"
"\u2022 1 segment: Analyzes the whole image at once (best for small images)\n"
"\u2022 More segments: Analyzes local regions independently (better for large images)\n"
"Higher segment counts improve detection in images with varying backgrounds.\n"
"Recommended: 4-9 segments for typical drone imagery.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.sensitivityLabel.setToolTip(QCoreApplication.translate("RXAnomaly", u"Detection sensitivity for anomaly detection.\n"
"\u2022 Range: 1 to 10\n"
"\u2022 Default: 5\n"
"Controls how statistically different a pixel must be from the background to be detected:\n"
"\u2022 Lower values (1-3): DECREASE detections - less sensitive, only detects strong anomalies\n"
"\u2022 Higher values (7-10): INCREASE detections - more sensitive, detects subtle anomalies\n"
"Higher sensitivity finds more potential targets but may include noise/false positives.", None))
#endif // QT_CONFIG(tooltip)
        self.sensitivityLabel.setText(QCoreApplication.translate("RXAnomaly", u"Sensitivity:", None))
#if QT_CONFIG(tooltip)
        self.sensitivitySlider.setToolTip(QCoreApplication.translate("RXAnomaly", u"Adjust the detection sensitivity for anomaly detection.\n"
"\u2022 Range: 1 to 10\n"
"\u2022 Default: 5\n"
"The RX algorithm uses statistical analysis to find pixels that differ from the background:\n"
"\u2022 Lower values (1-3): Less sensitive, only detects strong anomalies (fewer false positives)\n"
"\u2022 Medium values (4-6): Balanced detection (recommended for most cases)\n"
"\u2022 Higher values (7-10): More sensitive, detects subtle anomalies (more detections, may include noise)\n"
"Anomalies are pixels that are statistically different from the surrounding background.\n"
"Use lower sensitivity for clean images, higher for finding subtle targets.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.sensitivityValueLabel.setToolTip(QCoreApplication.translate("RXAnomaly", u"Current sensitivity level for anomaly detection.\n"
"Displays the value selected on the sensitivity slider (1-10).", None))
#endif // QT_CONFIG(tooltip)
        self.sensitivityValueLabel.setText(QCoreApplication.translate("RXAnomaly", u"5", None))
    # retranslateUi

