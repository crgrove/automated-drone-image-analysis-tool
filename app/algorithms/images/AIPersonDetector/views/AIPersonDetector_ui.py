# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AIPersonDetector.ui'
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
    QSlider, QVBoxLayout, QWidget)
from . import resources_rc

class Ui_AIPersonDetector(object):
    def setupUi(self, AIPersonDetector):
        if not AIPersonDetector.objectName():
            AIPersonDetector.setObjectName(u"AIPersonDetector")
        AIPersonDetector.resize(674, 70)
        self.verticalLayout_4 = QVBoxLayout(AIPersonDetector)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.confidenceLabel = QLabel(AIPersonDetector)
        self.confidenceLabel.setObjectName(u"confidenceLabel")
        font = QFont()
        font.setPointSize(10)
        self.confidenceLabel.setFont(font)

        self.horizontalLayout.addWidget(self.confidenceLabel)

        self.confidenceSlider = QSlider(AIPersonDetector)
        self.confidenceSlider.setObjectName(u"confidenceSlider")
        self.confidenceSlider.setMinimum(-1)
        self.confidenceSlider.setMaximum(100)
        self.confidenceSlider.setPageStep(1)
        self.confidenceSlider.setValue(50)
        self.confidenceSlider.setOrientation(Qt.Horizontal)
        self.confidenceSlider.setTickPosition(QSlider.TicksBelow)
        self.confidenceSlider.setTickInterval(1)

        self.horizontalLayout.addWidget(self.confidenceSlider)

        self.confidenceValueLabel = QLabel(AIPersonDetector)
        self.confidenceValueLabel.setObjectName(u"confidenceValueLabel")
        font1 = QFont()
        font1.setPointSize(10)
        font1.setBold(True)
        self.confidenceValueLabel.setFont(font1)

        self.horizontalLayout.addWidget(self.confidenceValueLabel)


        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.GPULabel = QLabel(AIPersonDetector)
        self.GPULabel.setObjectName(u"GPULabel")
        font2 = QFont()
        font2.setPointSize(9)
        self.GPULabel.setFont(font2)

        self.verticalLayout_4.addWidget(self.GPULabel)


        self.retranslateUi(AIPersonDetector)

        QMetaObject.connectSlotsByName(AIPersonDetector)
    # setupUi

    def retranslateUi(self, AIPersonDetector):
        AIPersonDetector.setWindowTitle(QCoreApplication.translate("AIPersonDetector", u"Form", None))
#if QT_CONFIG(tooltip)
        self.confidenceLabel.setToolTip(QCoreApplication.translate("AIPersonDetector", u"Confidence threshold for AI person detection.\n"
"Controls the minimum confidence level required to report a person detection.", None))
#endif // QT_CONFIG(tooltip)
        self.confidenceLabel.setText(QCoreApplication.translate("AIPersonDetector", u"Confidence Threshold", None))
#if QT_CONFIG(tooltip)
        self.confidenceSlider.setToolTip(QCoreApplication.translate("AIPersonDetector", u"Adjust the confidence threshold for person detection.\n"
"\u2022 Range: 0% to 100% (slider -1 to 100, -1 displays as 0%)\n"
"\u2022 Default: 50%\n"
"The AI model assigns a confidence score to each person detection:\n"
"\u2022 Lower values (0-30%): Accept low-confidence detections (more detections, more false positives)\n"
"\u2022 Medium values (31-60%): Balanced detection (recommended for most cases)\n"
"\u2022 Higher values (61-100%): Only accept high-confidence detections (fewer detections, fewer false positives)\n"
"Confidence represents the AI model's certainty that a detected object is a person.\n"
"Start with 50% and adjust based on your accuracy requirements.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.confidenceValueLabel.setToolTip(QCoreApplication.translate("AIPersonDetector", u"Current confidence threshold percentage.\n"
"Displays the value selected on the confidence slider (0-100%).\n"
"Detections below this confidence level will be filtered out.", None))
#endif // QT_CONFIG(tooltip)
        self.confidenceValueLabel.setText(QCoreApplication.translate("AIPersonDetector", u"50", None))
#if QT_CONFIG(tooltip)
        self.GPULabel.setToolTip(QCoreApplication.translate("AIPersonDetector", u"GPU status and availability information.\n"
"Shows whether GPU acceleration is available for AI person detection.\n"
"\u2022 GPU Available: AI detection will use GPU for faster processing\n"
"\u2022 CPU Only: AI detection will use CPU (slower but still functional)\n"
"GPU acceleration significantly improves processing speed for AI models.", None))
#endif // QT_CONFIG(tooltip)
        self.GPULabel.setText(QCoreApplication.translate("AIPersonDetector", u"GPU Label", None))
    # retranslateUi


