# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MatchedFilter.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSlider, QSpacerItem,
    QVBoxLayout, QWidget)
from . import resources_rc

class Ui_MatchedFilter(object):
    def setupUi(self, MatchedFilter):
        if not MatchedFilter.objectName():
            MatchedFilter.setObjectName(u"MatchedFilter")
        MatchedFilter.resize(674, 94)
        self.verticalLayout = QVBoxLayout(MatchedFilter)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.ColorSelectionLayout = QHBoxLayout()
        self.ColorSelectionLayout.setObjectName(u"ColorSelectionLayout")
        self.colorButton = QPushButton(MatchedFilter)
        self.colorButton.setObjectName(u"colorButton")
        font = QFont()
        font.setPointSize(10)
        self.colorButton.setFont(font)
        icon = QIcon()
        icon.addFile(u":/icons/color.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.colorButton.setIcon(icon)

        self.ColorSelectionLayout.addWidget(self.colorButton)

        self.colorSample = QFrame(MatchedFilter)
        self.colorSample.setObjectName(u"colorSample")
        self.colorSample.setMinimumSize(QSize(50, 20))
        self.colorSample.setFrameShape(QFrame.StyledPanel)
        self.colorSample.setFrameShadow(QFrame.Raised)

        self.ColorSelectionLayout.addWidget(self.colorSample)

        self.SilderLayout = QHBoxLayout()
        self.SilderLayout.setObjectName(u"SilderLayout")
        self.thresholdLabel = QLabel(MatchedFilter)
        self.thresholdLabel.setObjectName(u"thresholdLabel")
        self.thresholdLabel.setFont(font)

        self.SilderLayout.addWidget(self.thresholdLabel)

        self.thresholdSlider = QSlider(MatchedFilter)
        self.thresholdSlider.setObjectName(u"thresholdSlider")
        self.thresholdSlider.setMinimum(1)
        self.thresholdSlider.setMaximum(10)
        self.thresholdSlider.setPageStep(1)
        self.thresholdSlider.setValue(3)
        self.thresholdSlider.setOrientation(Qt.Horizontal)
        self.thresholdSlider.setTickPosition(QSlider.TicksBelow)
        self.thresholdSlider.setTickInterval(1)

        self.SilderLayout.addWidget(self.thresholdSlider)

        self.thresholdValueLabel = QLabel(MatchedFilter)
        self.thresholdValueLabel.setObjectName(u"thresholdValueLabel")
        font1 = QFont()
        font1.setPointSize(10)
        font1.setBold(True)
        self.thresholdValueLabel.setFont(font1)

        self.SilderLayout.addWidget(self.thresholdValueLabel)


        self.ColorSelectionLayout.addLayout(self.SilderLayout)


        self.verticalLayout.addLayout(self.ColorSelectionLayout)

        self.RangeViewerLayout = QHBoxLayout()
        self.RangeViewerLayout.setObjectName(u"RangeViewerLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.RangeViewerLayout.addItem(self.horizontalSpacer)

        self.viewRangeButton = QPushButton(MatchedFilter)
        self.viewRangeButton.setObjectName(u"viewRangeButton")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.viewRangeButton.sizePolicy().hasHeightForWidth())
        self.viewRangeButton.setSizePolicy(sizePolicy)
        self.viewRangeButton.setFont(font)
        icon1 = QIcon()
        icon1.addFile(u":/icons/eye.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.viewRangeButton.setIcon(icon1)

        self.RangeViewerLayout.addWidget(self.viewRangeButton)


        self.verticalLayout.addLayout(self.RangeViewerLayout)


        self.retranslateUi(MatchedFilter)

        QMetaObject.connectSlotsByName(MatchedFilter)
    # setupUi

    def retranslateUi(self, MatchedFilter):
        MatchedFilter.setWindowTitle(QCoreApplication.translate("MatchedFilter", u"Form", None))
#if QT_CONFIG(tooltip)
        self.colorButton.setToolTip(QCoreApplication.translate("MatchedFilter", u"Select a target color signature for matched filter detection.\n"
"Opens a color picker to sample the spectral signature from an image.\n"
"The matched filter algorithm uses this color signature to find similar pixels.\n"
"Picks RGB values which are converted to a spectral signature for matching.\n"
"Best for detecting specific colored objects with consistent spectral properties.", None))
#endif // QT_CONFIG(tooltip)
        self.colorButton.setText(QCoreApplication.translate("MatchedFilter", u" Pick Color", None))
        self.colorButton.setProperty(u"iconName", QCoreApplication.translate("MatchedFilter", u"color.png", None))
#if QT_CONFIG(tooltip)
        self.colorSample.setToolTip(QCoreApplication.translate("MatchedFilter", u"Visual preview of the selected target color signature.\n"
"Shows the color that will be used for matched filter detection.\n"
"The algorithm finds pixels with similar spectral characteristics to this color.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.thresholdLabel.setToolTip(QCoreApplication.translate("MatchedFilter", u"Detection threshold for matched filter algorithm.\n"
"\u2022 Range: 0.1 to 1.0 (displayed as slider 1-10, divided by 10)\n"
"\u2022 Default: 0.3\n"
"Controls the correlation coefficient required for a pixel to match the target color signature:\n"
"\u2022 Lower values (0.1-0.3): INCREASE detections - more lenient matching, accepts less similar colors\n"
"\u2022 Higher values (0.7-1.0): DECREASE detections - strict matching, only very similar colors detected\n"
"Threshold represents how closely a pixel's spectral signature must match the target signature.", None))
#endif // QT_CONFIG(tooltip)
        self.thresholdLabel.setText(QCoreApplication.translate("MatchedFilter", u"Threshold:", None))
#if QT_CONFIG(tooltip)
        self.thresholdSlider.setToolTip(QCoreApplication.translate("MatchedFilter", u"Adjust the detection threshold for matched filter algorithm.\n"
"\u2022 Range: 0.1 to 1.0 (displayed as 1-10, divided by 10)\n"
"\u2022 Default: 0.3 (slider value 3)\n"
"The matched filter algorithm finds pixels with similar spectral signatures:\n"
"\u2022 Lower values (0.1-0.3): More lenient matching, more detections (may include dissimilar colors)\n"
"\u2022 Medium values (0.4-0.6): Balanced detection (recommended for most cases)\n"
"\u2022 Higher values (0.7-1.0): Strict matching, fewer detections (only very similar colors)\n"
"Threshold represents the correlation coefficient between target and pixel signatures.\n"
"Start with 0.3 and adjust based on detection results.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.thresholdValueLabel.setToolTip(QCoreApplication.translate("MatchedFilter", u"Current threshold value for matched filter detection.\n"
"Displays the slider value divided by 10 (e.g., slider 3 = threshold 0.3).\n"
"Represents the minimum correlation coefficient for detection.", None))
#endif // QT_CONFIG(tooltip)
        self.thresholdValueLabel.setText(QCoreApplication.translate("MatchedFilter", u".3", None))
#if QT_CONFIG(tooltip)
        self.viewRangeButton.setToolTip(QCoreApplication.translate("MatchedFilter", u"Opens the Range Viewer window to:\n"
"- See the range of colors that will be searched for in the image analysis.\n"
"Use this to see what colors are going to be detected and optimize the color ranges before processing.", None))
#endif // QT_CONFIG(tooltip)
        self.viewRangeButton.setText(QCoreApplication.translate("MatchedFilter", u"View Range", None))
        self.viewRangeButton.setProperty(u"iconName", QCoreApplication.translate("MatchedFilter", u"eye.png", None))
    # retranslateUi

