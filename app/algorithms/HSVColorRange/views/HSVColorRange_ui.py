# -*- coding: utf-8 -*-

###############################################################################
# Form generated from reading UI file 'HSVColorRange.ui'
#
# Created by: Qt User Interface Compiler version 6.9.2
#
# WARNING! All changes made in this file will be lost when recompiling UI file!
###############################################################################

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

class Ui_HSVColorRange(object):
    def setupUi(self, HSVColorRange):
        if not HSVColorRange.objectName():
            HSVColorRange.setObjectName(u"HSVColorRange")
        HSVColorRange.resize(674, 94)
        self.verticalLayout = QVBoxLayout(HSVColorRange)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.ColorSelectionLayout = QHBoxLayout()
        self.ColorSelectionLayout.setObjectName(u"ColorSelectionLayout")
        self.colorButton = QPushButton(HSVColorRange)
        self.colorButton.setObjectName(u"colorButton")
        font = QFont()
        font.setPointSize(10)
        self.colorButton.setFont(font)
        icon = QIcon()
        icon.addFile(u":/icons/color.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.colorButton.setIcon(icon)

        self.ColorSelectionLayout.addWidget(self.colorButton)

        self.colorSample = QFrame(HSVColorRange)
        self.colorSample.setObjectName(u"colorSample")
        self.colorSample.setMinimumSize(QSize(50, 20))
        self.colorSample.setFrameShape(QFrame.StyledPanel)
        self.colorSample.setFrameShadow(QFrame.Raised)

        self.ColorSelectionLayout.addWidget(self.colorSample)

        self.horizontalSpacer_4 = QSpacerItem(18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.ColorSelectionLayout.addItem(self.horizontalSpacer_4)

        self.SpinBoxLayout = QHBoxLayout()
        self.SpinBoxLayout.setObjectName(u"SpinBoxLayout")
        self.hueSensitivityLabel = QLabel(HSVColorRange)
        self.hueSensitivityLabel.setObjectName(u"hueSensitivityLabel")
        self.hueSensitivityLabel.setFont(font)

        self.SpinBoxLayout.addWidget(self.hueSensitivityLabel)

        self.hueMinusLabel = QLabel(HSVColorRange)
        self.hueMinusLabel.setObjectName(u"hueMinusLabel")
        font1 = QFont()
        font1.setPointSize(8)
        self.hueMinusLabel.setFont(font1)

        self.SpinBoxLayout.addWidget(self.hueMinusLabel)

        self.hueMinusSpinBox = QSpinBox(HSVColorRange)
        self.hueMinusSpinBox.setObjectName(u"hueMinusSpinBox")
        self.hueMinusSpinBox.setFont(font)
        self.hueMinusSpinBox.setMinimum(0)
        self.hueMinusSpinBox.setMaximum(179)
        self.hueMinusSpinBox.setValue(20)

        self.SpinBoxLayout.addWidget(self.hueMinusSpinBox)

        self.huePlusLabel = QLabel(HSVColorRange)
        self.huePlusLabel.setObjectName(u"huePlusLabel")
        self.huePlusLabel.setFont(font1)

        self.SpinBoxLayout.addWidget(self.huePlusLabel)

        self.huePlusSpinBox = QSpinBox(HSVColorRange)
        self.huePlusSpinBox.setObjectName(u"huePlusSpinBox")
        self.huePlusSpinBox.setFont(font)
        self.huePlusSpinBox.setMinimum(0)
        self.huePlusSpinBox.setMaximum(179)
        self.huePlusSpinBox.setValue(20)

        self.SpinBoxLayout.addWidget(self.huePlusSpinBox)

        self.horizontalSpacer = QSpacerItem(18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.SpinBoxLayout.addItem(self.horizontalSpacer)

        self.saturationSensitivityLabel = QLabel(HSVColorRange)
        self.saturationSensitivityLabel.setObjectName(u"saturationSensitivityLabel")
        self.saturationSensitivityLabel.setFont(font)

        self.SpinBoxLayout.addWidget(self.saturationSensitivityLabel)

        self.saturationMinusLabel = QLabel(HSVColorRange)
        self.saturationMinusLabel.setObjectName(u"saturationMinusLabel")
        self.saturationMinusLabel.setFont(font1)

        self.SpinBoxLayout.addWidget(self.saturationMinusLabel)

        self.saturationMinusSpinBox = QSpinBox(HSVColorRange)
        self.saturationMinusSpinBox.setObjectName(u"saturationMinusSpinBox")
        self.saturationMinusSpinBox.setFont(font)
        self.saturationMinusSpinBox.setMaximum(255)
        self.saturationMinusSpinBox.setValue(50)

        self.SpinBoxLayout.addWidget(self.saturationMinusSpinBox)

        self.saturationPlusLabel = QLabel(HSVColorRange)
        self.saturationPlusLabel.setObjectName(u"saturationPlusLabel")
        self.saturationPlusLabel.setFont(font1)

        self.SpinBoxLayout.addWidget(self.saturationPlusLabel)

        self.saturationPlusSpinBox = QSpinBox(HSVColorRange)
        self.saturationPlusSpinBox.setObjectName(u"saturationPlusSpinBox")
        self.saturationPlusSpinBox.setFont(font)
        self.saturationPlusSpinBox.setMaximum(255)
        self.saturationPlusSpinBox.setValue(50)

        self.SpinBoxLayout.addWidget(self.saturationPlusSpinBox)

        self.horizontalSpacer_2 = QSpacerItem(18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.SpinBoxLayout.addItem(self.horizontalSpacer_2)

        self.valueSensitivityLabel = QLabel(HSVColorRange)
        self.valueSensitivityLabel.setObjectName(u"valueSensitivityLabel")
        self.valueSensitivityLabel.setFont(font)

        self.SpinBoxLayout.addWidget(self.valueSensitivityLabel)

        self.valueMinusLabel = QLabel(HSVColorRange)
        self.valueMinusLabel.setObjectName(u"valueMinusLabel")
        self.valueMinusLabel.setFont(font1)

        self.SpinBoxLayout.addWidget(self.valueMinusLabel)

        self.valueMinusSpinBox = QSpinBox(HSVColorRange)
        self.valueMinusSpinBox.setObjectName(u"valueMinusSpinBox")
        self.valueMinusSpinBox.setFont(font)
        self.valueMinusSpinBox.setMaximum(255)
        self.valueMinusSpinBox.setValue(50)

        self.SpinBoxLayout.addWidget(self.valueMinusSpinBox)

        self.valuePlusLabel = QLabel(HSVColorRange)
        self.valuePlusLabel.setObjectName(u"valuePlusLabel")
        self.valuePlusLabel.setFont(font1)

        self.SpinBoxLayout.addWidget(self.valuePlusLabel)

        self.valuePlusSpinBox = QSpinBox(HSVColorRange)
        self.valuePlusSpinBox.setObjectName(u"valuePlusSpinBox")
        self.valuePlusSpinBox.setFont(font)
        self.valuePlusSpinBox.setMaximum(255)
        self.valuePlusSpinBox.setValue(50)

        self.SpinBoxLayout.addWidget(self.valuePlusSpinBox)


        self.ColorSelectionLayout.addLayout(self.SpinBoxLayout)


        self.verticalLayout.addLayout(self.ColorSelectionLayout)

        self.ColorRangeLayout = QHBoxLayout()
        self.ColorRangeLayout.setObjectName(u"ColorRangeLayout")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.ColorRangeLayout.addItem(self.horizontalSpacer_3)

        self.viewRangeButton = QPushButton(HSVColorRange)
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


        self.retranslateUi(HSVColorRange)

        QMetaObject.connectSlotsByName(HSVColorRange)
    # setupUi

    def retranslateUi(self, HSVColorRange):
        HSVColorRange.setWindowTitle(QCoreApplication.translate("HSVColorRange", u"Form", None))
        self.colorButton.setText(QCoreApplication.translate("HSVColorRange", u" Pick Color", None))
        self.colorButton.setProperty(u"iconName", QCoreApplication.translate("HSVColorRange", u"color.png", None))
        self.hueSensitivityLabel.setText(QCoreApplication.translate("HSVColorRange", u"Hue Range", None))
        self.hueMinusLabel.setText(QCoreApplication.translate("HSVColorRange", u"-", None))
        self.huePlusLabel.setText(QCoreApplication.translate("HSVColorRange", u"+", None))
        self.saturationSensitivityLabel.setText(QCoreApplication.translate("HSVColorRange", u"Saturation Range", None))
        self.saturationMinusLabel.setText(QCoreApplication.translate("HSVColorRange", u"-", None))
        self.saturationPlusLabel.setText(QCoreApplication.translate("HSVColorRange", u"+", None))
        self.valueSensitivityLabel.setText(QCoreApplication.translate("HSVColorRange", u"Value Range", None))
        self.valueMinusLabel.setText(QCoreApplication.translate("HSVColorRange", u"-", None))
        self.valuePlusLabel.setText(QCoreApplication.translate("HSVColorRange", u"+", None))
        self.viewRangeButton.setText(QCoreApplication.translate("HSVColorRange", u"View Range", None))
        self.viewRangeButton.setProperty(u"iconName", QCoreApplication.translate("HSVColorRange", u"eye.png", None))
    # retranslateUi

