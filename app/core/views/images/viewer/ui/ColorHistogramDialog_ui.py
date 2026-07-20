# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ColorHistogramDialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_ColorHistogramDialog(object):
    def setupUi(self, ColorHistogramDialog):
        if not ColorHistogramDialog.objectName():
            ColorHistogramDialog.setObjectName(u"ColorHistogramDialog")
        ColorHistogramDialog.resize(760, 520)
        self.verticalLayout = QVBoxLayout(ColorHistogramDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.descriptionLabel = QLabel(ColorHistogramDialog)
        self.descriptionLabel.setObjectName(u"descriptionLabel")
        self.descriptionLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.descriptionLabel)

        self.selectionLayout = QHBoxLayout()
        self.selectionLayout.setObjectName(u"selectionLayout")
        self.showAoiOnlyCheckBox = QCheckBox(ColorHistogramDialog)
        self.showAoiOnlyCheckBox.setObjectName(u"showAoiOnlyCheckBox")

        self.selectionLayout.addWidget(self.showAoiOnlyCheckBox)

        self.selectionSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.selectionLayout.addItem(self.selectionSpacer)

        self.resetZoomButton = QPushButton(ColorHistogramDialog)
        self.resetZoomButton.setObjectName(u"resetZoomButton")

        self.selectionLayout.addWidget(self.resetZoomButton)


        self.verticalLayout.addLayout(self.selectionLayout)

        self.zoomInfoLabel = QLabel(ColorHistogramDialog)
        self.zoomInfoLabel.setObjectName(u"zoomInfoLabel")
        self.zoomInfoLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.zoomInfoLabel)

        self.chartContainer = QWidget(ColorHistogramDialog)
        self.chartContainer.setObjectName(u"chartContainer")

        self.verticalLayout.addWidget(self.chartContainer)

        self.rangeGroupBox = QGroupBox(ColorHistogramDialog)
        self.rangeGroupBox.setObjectName(u"rangeGroupBox")
        self.rangeLayout = QVBoxLayout(self.rangeGroupBox)
        self.rangeLayout.setObjectName(u"rangeLayout")
        self.rangeSliderContainer = QWidget(self.rangeGroupBox)
        self.rangeSliderContainer.setObjectName(u"rangeSliderContainer")

        self.rangeLayout.addWidget(self.rangeSliderContainer)

        self.rangeValueLayout = QHBoxLayout()
        self.rangeValueLayout.setObjectName(u"rangeValueLayout")
        self.minValueLabel = QLabel(self.rangeGroupBox)
        self.minValueLabel.setObjectName(u"minValueLabel")

        self.rangeValueLayout.addWidget(self.minValueLabel)

        self.maxValueLabel = QLabel(self.rangeGroupBox)
        self.maxValueLabel.setObjectName(u"maxValueLabel")
        self.maxValueLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.rangeValueLayout.addWidget(self.maxValueLabel)

        self.rangeSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.rangeValueLayout.addItem(self.rangeSpacer)

        self.resetRangeButton = QPushButton(self.rangeGroupBox)
        self.resetRangeButton.setObjectName(u"resetRangeButton")

        self.rangeValueLayout.addWidget(self.resetRangeButton)


        self.rangeLayout.addLayout(self.rangeValueLayout)


        self.verticalLayout.addWidget(self.rangeGroupBox)

        self.hoverInfoLabel = QLabel(ColorHistogramDialog)
        self.hoverInfoLabel.setObjectName(u"hoverInfoLabel")

        self.verticalLayout.addWidget(self.hoverInfoLabel)

        self.buttonBox = QDialogButtonBox(ColorHistogramDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(ColorHistogramDialog)

        QMetaObject.connectSlotsByName(ColorHistogramDialog)
    # setupUi

    def retranslateUi(self, ColorHistogramDialog):
        ColorHistogramDialog.setWindowTitle(QCoreApplication.translate("ColorHistogramDialog", u"Hue Histogram", None))
        self.descriptionLabel.setText(QCoreApplication.translate("ColorHistogramDialog", u"Hue distribution of all pixels vs. AOI pixels. Hovering the chart highlights matching pixels in the image.", None))
        self.showAoiOnlyCheckBox.setText(QCoreApplication.translate("ColorHistogramDialog", u"AOIs Only", None))
        self.resetZoomButton.setText(QCoreApplication.translate("ColorHistogramDialog", u"Reset Zoom", None))
        self.zoomInfoLabel.setText(QCoreApplication.translate("ColorHistogramDialog", u"Drag on the histogram or use the mouse wheel to zoom. Double-click or use Reset Zoom to return to the full range.", None))
        self.rangeGroupBox.setTitle(QCoreApplication.translate("ColorHistogramDialog", u"Visible Hue Range", None))
        self.minValueLabel.setText(QCoreApplication.translate("ColorHistogramDialog", u"Minimum: --", None))
        self.maxValueLabel.setText(QCoreApplication.translate("ColorHistogramDialog", u"Maximum: --", None))
        self.resetRangeButton.setText(QCoreApplication.translate("ColorHistogramDialog", u"Reset Range", None))
        self.hoverInfoLabel.setText(QCoreApplication.translate("ColorHistogramDialog", u"Hover over the histogram to inspect a hue band.", None))
    # retranslateUi

