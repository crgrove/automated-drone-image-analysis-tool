# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MotionDetectionWizard.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox, QHBoxLayout,
    QLabel, QSizePolicy, QSlider, QSpacerItem,
    QSpinBox, QVBoxLayout, QWidget)
class Ui_MotionDetectionWizard(object):
    def setupUi(self, MotionDetectionWizard):
        if not MotionDetectionWizard.objectName():
            MotionDetectionWizard.setObjectName(u"MotionDetectionWizard")
        self.verticalLayout_root = QVBoxLayout(MotionDetectionWizard)
        self.verticalLayout_root.setObjectName(u"verticalLayout_root")
        self.verticalLayout_root.setContentsMargins(0, 5, 0, 0)
        self.groupBox_mode = QGroupBox(MotionDetectionWizard)
        self.groupBox_mode.setObjectName(u"groupBox_mode")
        self.verticalLayout_mode = QVBoxLayout(self.groupBox_mode)
        self.verticalLayout_mode.setObjectName(u"verticalLayout_mode")
        self.labelMode = QLabel(self.groupBox_mode)
        self.labelMode.setObjectName(u"labelMode")

        self.verticalLayout_mode.addWidget(self.labelMode)

        self.modeComboBox = QComboBox(self.groupBox_mode)
        self.modeComboBox.addItem("")
        self.modeComboBox.addItem("")
        self.modeComboBox.addItem("")
        self.modeComboBox.setObjectName(u"modeComboBox")

        self.verticalLayout_mode.addWidget(self.modeComboBox)


        self.verticalLayout_root.addWidget(self.groupBox_mode)

        self.groupBox_algorithm = QGroupBox(MotionDetectionWizard)
        self.groupBox_algorithm.setObjectName(u"groupBox_algorithm")
        self.verticalLayout_algorithm = QVBoxLayout(self.groupBox_algorithm)
        self.verticalLayout_algorithm.setObjectName(u"verticalLayout_algorithm")
        self.labelAlgorithm = QLabel(self.groupBox_algorithm)
        self.labelAlgorithm.setObjectName(u"labelAlgorithm")

        self.verticalLayout_algorithm.addWidget(self.labelAlgorithm)

        self.algorithmComboBox = QComboBox(self.groupBox_algorithm)
        self.algorithmComboBox.addItem("")
        self.algorithmComboBox.addItem("")
        self.algorithmComboBox.addItem("")
        self.algorithmComboBox.addItem("")
        self.algorithmComboBox.addItem("")
        self.algorithmComboBox.setObjectName(u"algorithmComboBox")

        self.verticalLayout_algorithm.addWidget(self.algorithmComboBox)


        self.verticalLayout_root.addWidget(self.groupBox_algorithm)

        self.groupBox_parameters = QGroupBox(MotionDetectionWizard)
        self.groupBox_parameters.setObjectName(u"groupBox_parameters")
        self.verticalLayout_parameters = QVBoxLayout(self.groupBox_parameters)
        self.verticalLayout_parameters.setObjectName(u"verticalLayout_parameters")
        self.labelSensitivity = QLabel(self.groupBox_parameters)
        self.labelSensitivity.setObjectName(u"labelSensitivity")

        self.verticalLayout_parameters.addWidget(self.labelSensitivity)

        self.sensitivitySlider = QSlider(self.groupBox_parameters)
        self.sensitivitySlider.setObjectName(u"sensitivitySlider")
        self.sensitivitySlider.setOrientation(Qt.Horizontal)
        self.sensitivitySlider.setMinimum(0)
        self.sensitivitySlider.setMaximum(100)
        self.sensitivitySlider.setValue(50)

        self.verticalLayout_parameters.addWidget(self.sensitivitySlider)

        self.horizontalLayout_minArea = QHBoxLayout()
        self.horizontalLayout_minArea.setObjectName(u"horizontalLayout_minArea")
        self.labelMinArea = QLabel(self.groupBox_parameters)
        self.labelMinArea.setObjectName(u"labelMinArea")

        self.horizontalLayout_minArea.addWidget(self.labelMinArea)

        self.minAreaSpinBox = QSpinBox(self.groupBox_parameters)
        self.minAreaSpinBox.setObjectName(u"minAreaSpinBox")
        self.minAreaSpinBox.setMinimum(10)
        self.minAreaSpinBox.setMaximum(50000)
        self.minAreaSpinBox.setValue(500)

        self.horizontalLayout_minArea.addWidget(self.minAreaSpinBox)


        self.verticalLayout_parameters.addLayout(self.horizontalLayout_minArea)

        self.horizontalLayout_maxArea = QHBoxLayout()
        self.horizontalLayout_maxArea.setObjectName(u"horizontalLayout_maxArea")
        self.labelMaxArea = QLabel(self.groupBox_parameters)
        self.labelMaxArea.setObjectName(u"labelMaxArea")

        self.horizontalLayout_maxArea.addWidget(self.labelMaxArea)

        self.maxAreaSpinBox = QSpinBox(self.groupBox_parameters)
        self.maxAreaSpinBox.setObjectName(u"maxAreaSpinBox")
        self.maxAreaSpinBox.setMinimum(100)
        self.maxAreaSpinBox.setMaximum(500000)
        self.maxAreaSpinBox.setValue(100000)

        self.horizontalLayout_maxArea.addWidget(self.maxAreaSpinBox)


        self.verticalLayout_parameters.addLayout(self.horizontalLayout_maxArea)


        self.verticalLayout_root.addWidget(self.groupBox_parameters)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_root.addItem(self.verticalSpacer)


        self.retranslateUi(MotionDetectionWizard)

        QMetaObject.connectSlotsByName(MotionDetectionWizard)
    # setupUi

    def retranslateUi(self, MotionDetectionWizard):
        self.groupBox_mode.setTitle(QCoreApplication.translate("MotionDetectionWizard", u"Detection Mode", None))
        self.labelMode.setText(QCoreApplication.translate("MotionDetectionWizard", u"Mode:", None))
        self.modeComboBox.setItemText(0, QCoreApplication.translate("MotionDetectionWizard", u"Auto", None))
        self.modeComboBox.setItemText(1, QCoreApplication.translate("MotionDetectionWizard", u"Static Camera", None))
        self.modeComboBox.setItemText(2, QCoreApplication.translate("MotionDetectionWizard", u"Moving Camera", None))

        self.groupBox_algorithm.setTitle(QCoreApplication.translate("MotionDetectionWizard", u"Algorithm", None))
        self.labelAlgorithm.setText(QCoreApplication.translate("MotionDetectionWizard", u"Algorithm:", None))
        self.algorithmComboBox.setItemText(0, QCoreApplication.translate("MotionDetectionWizard", u"Frame Difference", None))
        self.algorithmComboBox.setItemText(1, QCoreApplication.translate("MotionDetectionWizard", u"MOG2 Background", None))
        self.algorithmComboBox.setItemText(2, QCoreApplication.translate("MotionDetectionWizard", u"KNN Background", None))
        self.algorithmComboBox.setItemText(3, QCoreApplication.translate("MotionDetectionWizard", u"Optical Flow", None))
        self.algorithmComboBox.setItemText(4, QCoreApplication.translate("MotionDetectionWizard", u"Feature Matching", None))

        self.groupBox_parameters.setTitle(QCoreApplication.translate("MotionDetectionWizard", u"Detection Parameters", None))
        self.labelSensitivity.setText(QCoreApplication.translate("MotionDetectionWizard", u"Sensitivity: 50%", None))
        self.labelMinArea.setText(QCoreApplication.translate("MotionDetectionWizard", u"Min Area:", None))
        self.labelMaxArea.setText(QCoreApplication.translate("MotionDetectionWizard", u"Max Area:", None))
        pass
    # retranslateUi

