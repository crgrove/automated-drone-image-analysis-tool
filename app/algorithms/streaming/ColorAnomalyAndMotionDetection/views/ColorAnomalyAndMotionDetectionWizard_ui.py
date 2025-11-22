# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ColorAnomalyAndMotionDetectionWizard.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGroupBox, QHBoxLayout,
    QLabel, QRadioButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)
class Ui_ColorAnomalyAndMotionDetectionWizard(object):
    def setupUi(self, ColorAnomalyAndMotionDetectionWizard):
        if not ColorAnomalyAndMotionDetectionWizard.objectName():
            ColorAnomalyAndMotionDetectionWizard.setObjectName(u"ColorAnomalyAndMotionDetectionWizard")
        self.verticalLayout_root = QVBoxLayout(ColorAnomalyAndMotionDetectionWizard)
        self.verticalLayout_root.setObjectName(u"verticalLayout_root")
        self.verticalLayout_root.setContentsMargins(0, 5, 0, 0)
        self.groupBox_color = QGroupBox(ColorAnomalyAndMotionDetectionWizard)
        self.groupBox_color.setObjectName(u"groupBox_color")
        self.verticalLayout_color = QVBoxLayout(self.groupBox_color)
        self.verticalLayout_color.setObjectName(u"verticalLayout_color")
        self.enableColorCheckBox = QCheckBox(self.groupBox_color)
        self.enableColorCheckBox.setObjectName(u"enableColorCheckBox")
        self.enableColorCheckBox.setChecked(True)

        self.verticalLayout_color.addWidget(self.enableColorCheckBox)

        self.labelAggressiveness = QLabel(self.groupBox_color)
        self.labelAggressiveness.setObjectName(u"labelAggressiveness")
        font = QFont()
        font.setPointSize(12)
        self.labelAggressiveness.setFont(font)

        self.verticalLayout_color.addWidget(self.labelAggressiveness)

        self.labelNote = QLabel(self.groupBox_color)
        self.labelNote.setObjectName(u"labelNote")
        font1 = QFont()
        font1.setPointSize(11)
        font1.setItalic(True)
        self.labelNote.setFont(font1)

        self.verticalLayout_color.addWidget(self.labelNote)

        self.aggressivenessSliderPlaceholder = QWidget(self.groupBox_color)
        self.aggressivenessSliderPlaceholder.setObjectName(u"aggressivenessSliderPlaceholder")
        self.aggressivenessSliderPlaceholder.setMinimumSize(QSize(600, 60))

        self.verticalLayout_color.addWidget(self.aggressivenessSliderPlaceholder)


        self.verticalLayout_root.addWidget(self.groupBox_color)

        self.groupBox_motion = QGroupBox(ColorAnomalyAndMotionDetectionWizard)
        self.groupBox_motion.setObjectName(u"groupBox_motion")
        self.verticalLayout_motion = QVBoxLayout(self.groupBox_motion)
        self.verticalLayout_motion.setObjectName(u"verticalLayout_motion")
        self.labelMotionQuestion = QLabel(self.groupBox_motion)
        self.labelMotionQuestion.setObjectName(u"labelMotionQuestion")
        self.labelMotionQuestion.setFont(font)

        self.verticalLayout_motion.addWidget(self.labelMotionQuestion)

        self.widgetRadioButtons = QWidget(self.groupBox_motion)
        self.widgetRadioButtons.setObjectName(u"widgetRadioButtons")
        self.horizontalLayout_radio = QHBoxLayout(self.widgetRadioButtons)
        self.horizontalLayout_radio.setObjectName(u"horizontalLayout_radio")
        self.radioMotionNo = QRadioButton(self.widgetRadioButtons)
        self.radioMotionNo.setObjectName(u"radioMotionNo")
        self.radioMotionNo.setChecked(True)

        self.horizontalLayout_radio.addWidget(self.radioMotionNo)

        self.radioMotionYes = QRadioButton(self.widgetRadioButtons)
        self.radioMotionYes.setObjectName(u"radioMotionYes")

        self.horizontalLayout_radio.addWidget(self.radioMotionYes)

        self.horizontalSpacer_motion = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_radio.addItem(self.horizontalSpacer_motion)


        self.verticalLayout_motion.addWidget(self.widgetRadioButtons)


        self.verticalLayout_root.addWidget(self.groupBox_motion)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_root.addItem(self.verticalSpacer)


        self.retranslateUi(ColorAnomalyAndMotionDetectionWizard)

        QMetaObject.connectSlotsByName(ColorAnomalyAndMotionDetectionWizard)
    # setupUi

    def retranslateUi(self, ColorAnomalyAndMotionDetectionWizard):
        self.groupBox_color.setTitle(QCoreApplication.translate("ColorAnomalyAndMotionDetectionWizard", u"Color Anomaly Detection", None))
        self.enableColorCheckBox.setText(QCoreApplication.translate("ColorAnomalyAndMotionDetectionWizard", u"Enable Color Anomaly Detection", None))
        self.labelAggressiveness.setText(QCoreApplication.translate("ColorAnomalyAndMotionDetectionWizard", u"How aggressively should ADIAT be searching for anomalies?", None))
        self.labelNote.setText(QCoreApplication.translate("ColorAnomalyAndMotionDetectionWizard", u"Note: A higher setting will find more potential anomalies but may also increase false positives.", None))
        self.groupBox_motion.setTitle(QCoreApplication.translate("ColorAnomalyAndMotionDetectionWizard", u"Motion Detection", None))
        self.labelMotionQuestion.setText(QCoreApplication.translate("ColorAnomalyAndMotionDetectionWizard", u"Do you want to enable motion detection?", None))
        self.radioMotionNo.setText(QCoreApplication.translate("ColorAnomalyAndMotionDetectionWizard", u"No", None))
        self.radioMotionYes.setText(QCoreApplication.translate("ColorAnomalyAndMotionDetectionWizard", u"Yes", None))
        pass
    # retranslateUi

