# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ColorRange.ui'
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
    QPushButton, QSizePolicy, QSpacerItem, QSpinBox,
    QVBoxLayout, QWidget)
from . import resources_rc

class Ui_ColorRange(object):
    def setupUi(self, ColorRange):
        if not ColorRange.objectName():
            ColorRange.setObjectName(u"ColorRange")
        ColorRange.resize(674, 94)
        self.verticalLayout = QVBoxLayout(ColorRange)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.ColorSelectionLayout = QHBoxLayout()
        self.ColorSelectionLayout.setObjectName(u"ColorSelectionLayout")
        self.colorButton = QPushButton(ColorRange)
        self.colorButton.setObjectName(u"colorButton")
        font = QFont()
        font.setPointSize(10)
        self.colorButton.setFont(font)
        icon = QIcon()
        icon.addFile(u":/icons/color.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.colorButton.setIcon(icon)

        self.ColorSelectionLayout.addWidget(self.colorButton)

        self.horizontalSpacer_4 = QSpacerItem(18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.ColorSelectionLayout.addItem(self.horizontalSpacer_4)

        self.SpinBoxLayout = QHBoxLayout()
        self.SpinBoxLayout.setObjectName(u"SpinBoxLayout")
        self.rSensitivityLabel = QLabel(ColorRange)
        self.rSensitivityLabel.setObjectName(u"rSensitivityLabel")
        self.rSensitivityLabel.setFont(font)

        self.SpinBoxLayout.addWidget(self.rSensitivityLabel)

        self.rRangeSpinBox = QSpinBox(ColorRange)
        self.rRangeSpinBox.setObjectName(u"rRangeSpinBox")
        self.rRangeSpinBox.setFont(font)
        self.rRangeSpinBox.setMaximum(255)
        self.rRangeSpinBox.setValue(50)

        self.SpinBoxLayout.addWidget(self.rRangeSpinBox)

        self.horizontalSpacer = QSpacerItem(18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.SpinBoxLayout.addItem(self.horizontalSpacer)

        self.gSensitivityLabel = QLabel(ColorRange)
        self.gSensitivityLabel.setObjectName(u"gSensitivityLabel")
        self.gSensitivityLabel.setFont(font)

        self.SpinBoxLayout.addWidget(self.gSensitivityLabel)

        self.gRangeSpinBox = QSpinBox(ColorRange)
        self.gRangeSpinBox.setObjectName(u"gRangeSpinBox")
        self.gRangeSpinBox.setFont(font)
        self.gRangeSpinBox.setMaximum(255)
        self.gRangeSpinBox.setValue(50)

        self.SpinBoxLayout.addWidget(self.gRangeSpinBox)

        self.horizontalSpacer_2 = QSpacerItem(18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.SpinBoxLayout.addItem(self.horizontalSpacer_2)

        self.bSensitivityLabel = QLabel(ColorRange)
        self.bSensitivityLabel.setObjectName(u"bSensitivityLabel")
        self.bSensitivityLabel.setFont(font)

        self.SpinBoxLayout.addWidget(self.bSensitivityLabel)

        self.bRangeSpinBox = QSpinBox(ColorRange)
        self.bRangeSpinBox.setObjectName(u"bRangeSpinBox")
        self.bRangeSpinBox.setFont(font)
        self.bRangeSpinBox.setMaximum(255)
        self.bRangeSpinBox.setValue(50)

        self.SpinBoxLayout.addWidget(self.bRangeSpinBox)


        self.ColorSelectionLayout.addLayout(self.SpinBoxLayout)


        self.verticalLayout.addLayout(self.ColorSelectionLayout)

        self.ColorRangeLayout = QHBoxLayout()
        self.ColorRangeLayout.setObjectName(u"ColorRangeLayout")
        self.colorRangeLabel = QLabel(ColorRange)
        self.colorRangeLabel.setObjectName(u"colorRangeLabel")
        self.colorRangeLabel.setFont(font)

        self.ColorRangeLayout.addWidget(self.colorRangeLabel)

        self.minColor = QFrame(ColorRange)
        self.minColor.setObjectName(u"minColor")
        self.minColor.setFrameShape(QFrame.StyledPanel)
        self.minColor.setFrameShadow(QFrame.Raised)

        self.ColorRangeLayout.addWidget(self.minColor)

        self.midColor = QFrame(ColorRange)
        self.midColor.setObjectName(u"midColor")
        self.midColor.setFrameShape(QFrame.StyledPanel)
        self.midColor.setFrameShadow(QFrame.Raised)

        self.ColorRangeLayout.addWidget(self.midColor)

        self.maxColor = QFrame(ColorRange)
        self.maxColor.setObjectName(u"maxColor")
        self.maxColor.setFrameShape(QFrame.StyledPanel)
        self.maxColor.setFrameShadow(QFrame.Raised)

        self.ColorRangeLayout.addWidget(self.maxColor)

        self.viewRangeButton = QPushButton(ColorRange)
        self.viewRangeButton.setObjectName(u"viewRangeButton")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.viewRangeButton.sizePolicy().hasHeightForWidth())
        self.viewRangeButton.setSizePolicy(sizePolicy)
        self.viewRangeButton.setFont(font)
        icon1 = QIcon()
        icon1.addFile(u":/icons/eye.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.viewRangeButton.setIcon(icon1)

        self.ColorRangeLayout.addWidget(self.viewRangeButton)


        self.verticalLayout.addLayout(self.ColorRangeLayout)


        self.retranslateUi(ColorRange)

        QMetaObject.connectSlotsByName(ColorRange)
    # setupUi

    def retranslateUi(self, ColorRange):
        ColorRange.setWindowTitle(QCoreApplication.translate("ColorRange", u"Form", None))
#if QT_CONFIG(tooltip)
        self.colorButton.setToolTip(QCoreApplication.translate("ColorRange", u"Select a target color from an image to detect using RGB color space.\n"
"Opens a color picker that allows you to:\n"
"\u2022 Load an image from the input folder\n"
"\u2022 Click on pixels to sample colors\n"
"\u2022 Automatically calculates RGB values\n"
"\u2022 Sets Red, Green, and Blue range tolerances\n"
"The selected color becomes the center of your RGB detection range.\n"
"Adjust the +/- range values to capture color variations.", None))
#endif // QT_CONFIG(tooltip)
        self.colorButton.setText(QCoreApplication.translate("ColorRange", u" Pick Color", None))
        self.colorButton.setProperty(u"iconName", QCoreApplication.translate("ColorRange", u"color.png", None))
#if QT_CONFIG(tooltip)
        self.rSensitivityLabel.setToolTip(QCoreApplication.translate("ColorRange", u"Red channel tolerance for RGB color detection.\n"
"Defines how much variation in the red channel value is acceptable.\n"
"Adjust to allow more or less red color variation.", None))
#endif // QT_CONFIG(tooltip)
        self.rSensitivityLabel.setText(QCoreApplication.translate("ColorRange", u"Red Range +/-", None))
#if QT_CONFIG(tooltip)
        self.rRangeSpinBox.setToolTip(QCoreApplication.translate("ColorRange", u"Red channel range tolerance (+/-).\n"
"\u2022 Range: 0 to 255\n"
"\u2022 Default: 50\n"
"Creates a range around the target red value by adding and subtracting this amount.\n"
"\u2022 Lower values: Strict red matching (narrow range)\n"
"\u2022 Higher values: Loose red matching (wide range)\n"
"Example: Target red 150, range 50 = detects red values from 100-200.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.gSensitivityLabel.setToolTip(QCoreApplication.translate("ColorRange", u"Green channel tolerance for RGB color detection.\n"
"Defines how much variation in the green channel value is acceptable.\n"
"Adjust to allow more or less green color variation.", None))
#endif // QT_CONFIG(tooltip)
        self.gSensitivityLabel.setText(QCoreApplication.translate("ColorRange", u"Green Range +/-", None))
#if QT_CONFIG(tooltip)
        self.gRangeSpinBox.setToolTip(QCoreApplication.translate("ColorRange", u"Green channel range tolerance (+/-).\n"
"\u2022 Range: 0 to 255\n"
"\u2022 Default: 50\n"
"Creates a range around the target green value by adding and subtracting this amount.\n"
"\u2022 Lower values: Strict green matching (narrow range)\n"
"\u2022 Higher values: Loose green matching (wide range)\n"
"Example: Target green 100, range 50 = detects green values from 50-150.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.bSensitivityLabel.setToolTip(QCoreApplication.translate("ColorRange", u"Blue channel tolerance for RGB color detection.\n"
"Defines how much variation in the blue channel value is acceptable.\n"
"Adjust to allow more or less blue color variation.", None))
#endif // QT_CONFIG(tooltip)
        self.bSensitivityLabel.setText(QCoreApplication.translate("ColorRange", u"Blue Range +/-", None))
#if QT_CONFIG(tooltip)
        self.bRangeSpinBox.setToolTip(QCoreApplication.translate("ColorRange", u"Blue channel range tolerance (+/-).\n"
"\u2022 Range: 0 to 255\n"
"\u2022 Default: 50\n"
"Creates a range around the target blue value by adding and subtracting this amount.\n"
"\u2022 Lower values: Strict blue matching (narrow range)\n"
"\u2022 Higher values: Loose blue matching (wide range)\n"
"Example: Target blue 80, range 50 = detects blue values from 30-130.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.colorRangeLabel.setToolTip(QCoreApplication.translate("ColorRange", u"Visual preview of the RGB color detection range.\n"
"Shows the minimum, center, and maximum colors that will be detected.", None))
#endif // QT_CONFIG(tooltip)
        self.colorRangeLabel.setText(QCoreApplication.translate("ColorRange", u"Color Range:", None))
#if QT_CONFIG(whatsthis)
        self.minColor.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
#if QT_CONFIG(tooltip)
        self.minColor.setToolTip(QCoreApplication.translate("ColorRange", u"Minimum color in the detection range.\n"
"Shows the darkest/lowest RGB values that will be detected.\n"
"Calculated by subtracting the range values from the target color.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.midColor.setToolTip(QCoreApplication.translate("ColorRange", u"Center/target color for detection.\n"
"Shows the exact RGB color that was selected.\n"
"This is the middle of your detection range.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.maxColor.setToolTip(QCoreApplication.translate("ColorRange", u"Maximum color in the detection range.\n"
"Shows the brightest/highest RGB values that will be detected.\n"
"Calculated by adding the range values to the target color.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.viewRangeButton.setToolTip(QCoreApplication.translate("ColorRange", u"Opens the Range Viewer window to:\n"
"- See the range of colors that will be searched for in the image analysis.\n"
"Use this to see what colors are going to be detected and optimize the color ranges before processing.", None))
#endif // QT_CONFIG(tooltip)
        self.viewRangeButton.setText(QCoreApplication.translate("ColorRange", u"View Range", None))
        self.viewRangeButton.setProperty(u"iconName", QCoreApplication.translate("ColorRange", u"eye.png", None))
    # retranslateUi

