# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MRMap.ui'
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
    QSizePolicy, QSlider, QSpacerItem, QSpinBox,
    QVBoxLayout, QWidget)

class Ui_MRMap(object):
    def setupUi(self, MRMap):
        if not MRMap.objectName():
            MRMap.setObjectName(u"MRMap")
        MRMap.resize(674, 94)
        self.verticalLayout = QVBoxLayout(MRMap)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.segmentsLabel = QLabel(MRMap)
        self.segmentsLabel.setObjectName(u"segmentsLabel")
        font = QFont()
        font.setPointSize(10)
        self.segmentsLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.segmentsLabel)

        self.segmentsComboBox = QComboBox(MRMap)
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.addItem("")
        self.segmentsComboBox.setObjectName(u"segmentsComboBox")
        self.segmentsComboBox.setMinimumSize(QSize(30, 0))
        self.segmentsComboBox.setFont(font)

        self.horizontalLayout_3.addWidget(self.segmentsComboBox)

        self.horizontalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.colorspaceLabel = QLabel(MRMap)
        self.colorspaceLabel.setObjectName(u"colorspaceLabel")
        self.colorspaceLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.colorspaceLabel)

        self.colorspaceComboBox = QComboBox(MRMap)
        self.colorspaceComboBox.addItem("")
        self.colorspaceComboBox.addItem("")
        self.colorspaceComboBox.addItem("")
        self.colorspaceComboBox.setObjectName(u"colorspaceComboBox")
        self.colorspaceComboBox.setMinimumSize(QSize(60, 0))
        self.colorspaceComboBox.setFont(font)

        self.horizontalLayout_3.addWidget(self.colorspaceComboBox)

        self.horizontalSpacer_3 = QSpacerItem(20, 20, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.windowLabel = QLabel(MRMap)
        self.windowLabel.setObjectName(u"windowLabel")
        self.windowLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.windowLabel)

        self.windowSpinBox = QSpinBox(MRMap)
        self.windowSpinBox.setObjectName(u"windowSpinBox")
        self.windowSpinBox.setMinimum(1)
        self.windowSpinBox.setMaximum(10)
        self.windowSpinBox.setValue(5)

        self.horizontalLayout_3.addWidget(self.windowSpinBox)

        self.horizontalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.thresholdLabel = QLabel(MRMap)
        self.thresholdLabel.setObjectName(u"thresholdLabel")
        self.thresholdLabel.setFont(font)

        self.horizontalLayout_3.addWidget(self.thresholdLabel)

        self.thresholdSlider = QSlider(MRMap)
        self.thresholdSlider.setObjectName(u"thresholdSlider")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.thresholdSlider.sizePolicy().hasHeightForWidth())
        self.thresholdSlider.setSizePolicy(sizePolicy)
        self.thresholdSlider.setMinimum(1)
        self.thresholdSlider.setMaximum(200)
        self.thresholdSlider.setPageStep(1)
        self.thresholdSlider.setValue(100)
        self.thresholdSlider.setSliderPosition(100)
        self.thresholdSlider.setOrientation(Qt.Horizontal)
        self.thresholdSlider.setInvertedAppearance(True)
        self.thresholdSlider.setTickPosition(QSlider.TicksBelow)
        self.thresholdSlider.setTickInterval(1)

        self.horizontalLayout_3.addWidget(self.thresholdSlider)

        self.thresholdValueLabel = QLabel(MRMap)
        self.thresholdValueLabel.setObjectName(u"thresholdValueLabel")
        self.thresholdValueLabel.setMinimumSize(QSize(50, 0))
        font1 = QFont()
        font1.setPointSize(10)
        font1.setBold(True)
        self.thresholdValueLabel.setFont(font1)

        self.horizontalLayout_3.addWidget(self.thresholdValueLabel)


        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)


        self.verticalLayout.addLayout(self.horizontalLayout_4)


        self.retranslateUi(MRMap)

        QMetaObject.connectSlotsByName(MRMap)
    # setupUi

    def retranslateUi(self, MRMap):
        MRMap.setWindowTitle(QCoreApplication.translate("MRMap", u"Form", None))
#if QT_CONFIG(tooltip)
        self.segmentsLabel.setToolTip(QCoreApplication.translate("MRMap", u"Number of segments to divide each image into for MR Map analysis.\n"
"Each segment is processed independently for multi-resolution feature detection.\n"
"Performance impact:\n"
"\u2022 Higher number of segments: INCREASES processing time (more segments to analyze)\n"
"\u2022 Lower number of segments: DECREASES processing time (fewer segments to analyze)\n"
"\u2022 1 segment: Fastest processing (analyzes whole image once)\n"
"Higher segment counts improve detection in images with varying features.", None))
#endif // QT_CONFIG(tooltip)
        self.segmentsLabel.setText(QCoreApplication.translate("MRMap", u"Image Segments:", None))
        self.segmentsComboBox.setItemText(0, QCoreApplication.translate("MRMap", u"1", None))
        self.segmentsComboBox.setItemText(1, QCoreApplication.translate("MRMap", u"2", None))
        self.segmentsComboBox.setItemText(2, QCoreApplication.translate("MRMap", u"4", None))
        self.segmentsComboBox.setItemText(3, QCoreApplication.translate("MRMap", u"6", None))
        self.segmentsComboBox.setItemText(4, QCoreApplication.translate("MRMap", u"9", None))
        self.segmentsComboBox.setItemText(5, QCoreApplication.translate("MRMap", u"16", None))
        self.segmentsComboBox.setItemText(6, QCoreApplication.translate("MRMap", u"25", None))
        self.segmentsComboBox.setItemText(7, QCoreApplication.translate("MRMap", u"36", None))

#if QT_CONFIG(tooltip)
        self.segmentsComboBox.setToolTip(QCoreApplication.translate("MRMap", u"Select the number of segments to divide each image into.\n"
"\u2022 Options: 1, 2, 4, 6, 9, 16, 25, 36 segments\n"
"\u2022 Default: 1 (analyze entire image as one segment)\n"
"The MR Map (Multi-Resolution Map) algorithm analyzes features at multiple scales:\n"
"\u2022 1 segment: Process whole image (best for small images or uniform content)\n"
"\u2022 More segments: Analyze local regions independently (better for large images)\n"
"Higher segment counts improve detection in images with varying features across the scene.\n"
"Recommended: 4-9 segments for typical drone imagery.", None))
#endif // QT_CONFIG(tooltip)
        self.colorspaceLabel.setText(QCoreApplication.translate("MRMap", u"Colorspace:", None))
        self.colorspaceComboBox.setItemText(0, QCoreApplication.translate("MRMap", u"RGB", None))
        self.colorspaceComboBox.setItemText(1, QCoreApplication.translate("MRMap", u"HSV", None))
        self.colorspaceComboBox.setItemText(2, QCoreApplication.translate("MRMap", u"LAB", None))
#if QT_CONFIG(tooltip)
        self.windowLabel.setToolTip(QCoreApplication.translate("MRMap", u"Window size for multi-resolution analysis.\n"
"Determines the spatial scale of features to detect.", None))
#endif // QT_CONFIG(tooltip)
        self.windowLabel.setText(QCoreApplication.translate("MRMap", u"Window Size:", None))
#if QT_CONFIG(tooltip)
        self.windowSpinBox.setToolTip(QCoreApplication.translate("MRMap", u"Set the window size for multi-resolution analysis.\n"
"\u2022 Range: 1 to 10\n"
"\u2022 Default: 5\n"
"The MR Map algorithm analyzes features at multiple spatial scales using sliding windows:\n"
"\u2022 Smaller values (1-3): Detect fine details and small features\n"
"\u2022 Medium values (4-6): Balanced detection (recommended for most cases)\n"
"\u2022 Larger values (7-10): Detect larger features and patterns\n"
"Window size affects the spatial resolution of feature detection.\n"
"Larger windows provide more context but may miss small objects.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.thresholdLabel.setToolTip(QCoreApplication.translate("MRMap", u"Detection threshold for MR Map feature detection.\n"
"Controls the sensitivity of feature detection across multiple resolutions.", None))
#endif // QT_CONFIG(tooltip)
        self.thresholdLabel.setText(QCoreApplication.translate("MRMap", u"Threshold:", None))
#if QT_CONFIG(tooltip)
        self.thresholdSlider.setToolTip(QCoreApplication.translate("MRMap", u"Adjust the detection threshold for MR Map algorithm.\n"
"\u2022 Range: 1 to 200\n"
"\u2022 Default: 100\n"
"\u2022 Slider is inverted: LEFT = higher threshold, RIGHT = lower threshold\n"
"The MR Map algorithm detects features at multiple spatial resolutions:\n"
"\u2022 Lower values (1-50): Very sensitive, detects many features (may include noise)\n"
"\u2022 Medium values (51-150): Balanced detection (recommended for most cases)\n"
"\u2022 Higher values (151-200): Less sensitive, only detects prominent features\n"
"Threshold controls how distinct a feature must be to be detected.\n"
"Note: Slider appearance is inverted - move left for stricter, right for more lenient.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.thresholdValueLabel.setToolTip(QCoreApplication.translate("MRMap", u"Current threshold value for MR Map feature detection.\n"
"Displays the value selected on the threshold slider (1-200).\n"
"Lower values = more sensitive detection.", None))
#endif // QT_CONFIG(tooltip)
        self.thresholdValueLabel.setText(QCoreApplication.translate("MRMap", u"100", None))
    # retranslateUi

