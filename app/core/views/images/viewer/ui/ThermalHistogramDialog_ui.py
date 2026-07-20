# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ThermalHistogramDialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGroupBox, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_ThermalHistogramDialog(object):
    def setupUi(self, ThermalHistogramDialog):
        if not ThermalHistogramDialog.objectName():
            ThermalHistogramDialog.setObjectName(u"ThermalHistogramDialog")
        ThermalHistogramDialog.resize(720, 460)
        self.verticalLayout = QVBoxLayout(ThermalHistogramDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.descriptionLabel = QLabel(ThermalHistogramDialog)
        self.descriptionLabel.setObjectName(u"descriptionLabel")
        self.descriptionLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.descriptionLabel)

        self.zoomLayout = QHBoxLayout()
        self.zoomLayout.setObjectName(u"zoomLayout")
        self.zoomInfoLabel = QLabel(ThermalHistogramDialog)
        self.zoomInfoLabel.setObjectName(u"zoomInfoLabel")

        self.zoomLayout.addWidget(self.zoomInfoLabel)

        self.zoomSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.zoomLayout.addItem(self.zoomSpacer)

        self.resetZoomButton = QPushButton(ThermalHistogramDialog)
        self.resetZoomButton.setObjectName(u"resetZoomButton")

        self.zoomLayout.addWidget(self.resetZoomButton)


        self.verticalLayout.addLayout(self.zoomLayout)

        self.chartContainer = QWidget(ThermalHistogramDialog)
        self.chartContainer.setObjectName(u"chartContainer")

        self.verticalLayout.addWidget(self.chartContainer)

        self.rangeGroupBox = QGroupBox(ThermalHistogramDialog)
        self.rangeGroupBox.setObjectName(u"rangeGroupBox")
        self.verticalLayout_2 = QVBoxLayout(self.rangeGroupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.rangeSliderContainer = QWidget(self.rangeGroupBox)
        self.rangeSliderContainer.setObjectName(u"rangeSliderContainer")

        self.verticalLayout_2.addWidget(self.rangeSliderContainer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.minValueLabel = QLabel(self.rangeGroupBox)
        self.minValueLabel.setObjectName(u"minValueLabel")

        self.horizontalLayout.addWidget(self.minValueLabel)

        self.maxValueLabel = QLabel(self.rangeGroupBox)
        self.maxValueLabel.setObjectName(u"maxValueLabel")
        self.maxValueLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout.addWidget(self.maxValueLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.resetRangeButton = QPushButton(self.rangeGroupBox)
        self.resetRangeButton.setObjectName(u"resetRangeButton")

        self.horizontalLayout.addWidget(self.resetRangeButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.verticalLayout.addWidget(self.rangeGroupBox)

        self.hoverInfoLabel = QLabel(ThermalHistogramDialog)
        self.hoverInfoLabel.setObjectName(u"hoverInfoLabel")

        self.verticalLayout.addWidget(self.hoverInfoLabel)

        self.buttonBox = QDialogButtonBox(ThermalHistogramDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(ThermalHistogramDialog)

        QMetaObject.connectSlotsByName(ThermalHistogramDialog)
    # setupUi

    def retranslateUi(self, ThermalHistogramDialog):
        ThermalHistogramDialog.setWindowTitle(QCoreApplication.translate("ThermalHistogramDialog", u"Thermal Histogram", None))
        self.descriptionLabel.setText(QCoreApplication.translate("ThermalHistogramDialog", u"Gray bars show the full temperature distribution, orange bars mark AOI/anomaly bins, and hovering the chart highlights matching pixels in the image.", None))
        self.zoomInfoLabel.setText(QCoreApplication.translate("ThermalHistogramDialog", u"Drag on the histogram to zoom. Double-click or use Reset Zoom to return to the full range.", None))
        self.resetZoomButton.setText(QCoreApplication.translate("ThermalHistogramDialog", u"Reset Zoom", None))
        self.rangeGroupBox.setTitle(QCoreApplication.translate("ThermalHistogramDialog", u"Visible Temperature Range", None))
        self.minValueLabel.setText(QCoreApplication.translate("ThermalHistogramDialog", u"Minimum: --", None))
        self.maxValueLabel.setText(QCoreApplication.translate("ThermalHistogramDialog", u"Maximum: --", None))
        self.resetRangeButton.setText(QCoreApplication.translate("ThermalHistogramDialog", u"Reset Range", None))
        self.hoverInfoLabel.setText(QCoreApplication.translate("ThermalHistogramDialog", u"Hover over the histogram to inspect a temperature band.", None))
    # retranslateUi

