# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ColorDetectionWizard.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_ColorDetectionWizard(object):
    def setupUi(self, ColorDetectionWizard):
        if not ColorDetectionWizard.objectName():
            ColorDetectionWizard.setObjectName(u"ColorDetectionWizard")
        self.verticalLayout_root = QVBoxLayout(ColorDetectionWizard)
        self.verticalLayout_root.setObjectName(u"verticalLayout_root")
        self.verticalLayout_root.setContentsMargins(0, 5, 0, 0)
        self.widgetAddButton = QWidget(ColorDetectionWizard)
        self.widgetAddButton.setObjectName(u"widgetAddButton")
        self.horizontalLayout_add = QHBoxLayout(self.widgetAddButton)
        self.horizontalLayout_add.setSpacing(10)
        self.horizontalLayout_add.setObjectName(u"horizontalLayout_add")
        self.addColorButton = QPushButton(self.widgetAddButton)
        self.addColorButton.setObjectName(u"addColorButton")
        font = QFont()
        font.setPointSize(11)
        self.addColorButton.setFont(font)
        self.addColorButton.setMinimumSize(QSize(120, 32))

        self.horizontalLayout_add.addWidget(self.addColorButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_add.addItem(self.horizontalSpacer)


        self.verticalLayout_root.addWidget(self.widgetAddButton)

        self.colorsContainer = QWidget(ColorDetectionWizard)
        self.colorsContainer.setObjectName(u"colorsContainer")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.colorsContainer.sizePolicy().hasHeightForWidth())
        self.colorsContainer.setSizePolicy(sizePolicy)
        self.colorsLayout = QVBoxLayout(self.colorsContainer)
        self.colorsLayout.setSpacing(6)
        self.colorsLayout.setObjectName(u"colorsLayout")
        self.colorsLayout.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_root.addWidget(self.colorsContainer)

        self.verticalSpacer_bottom = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_root.addItem(self.verticalSpacer_bottom)


        self.retranslateUi(ColorDetectionWizard)

        QMetaObject.connectSlotsByName(ColorDetectionWizard)
    # setupUi

    def retranslateUi(self, ColorDetectionWizard):
        self.addColorButton.setText(QCoreApplication.translate("ColorDetectionWizard", u"Add Color", None))
        pass
    # retranslateUi

