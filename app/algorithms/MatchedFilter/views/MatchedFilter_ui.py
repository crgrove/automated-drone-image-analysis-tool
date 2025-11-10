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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)
from . import resources_rc

class Ui_MatchedFilter(object):
    def setupUi(self, MatchedFilter):
        if not MatchedFilter.objectName():
            MatchedFilter.setObjectName(u"MatchedFilter")
        MatchedFilter.resize(800, 400)
        self.verticalLayout = QVBoxLayout(MatchedFilter)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName(u"buttonLayout")
        self.addColorButton = QPushButton(MatchedFilter)
        self.addColorButton.setObjectName(u"addColorButton")
        font = QFont()
        font.setPointSize(10)
        self.addColorButton.setFont(font)
        icon = QIcon()
        icon.addFile(u":/icons/color.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.addColorButton.setIcon(icon)

        self.buttonLayout.addWidget(self.addColorButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonLayout.addItem(self.horizontalSpacer)

        self.viewRangeButton = QPushButton(MatchedFilter)
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

        self.buttonLayout.addWidget(self.viewRangeButton)


        self.verticalLayout.addLayout(self.buttonLayout)

        self.scrollArea = QScrollArea(MatchedFilter)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 798, 350))
        self.colorsLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.colorsLayout.setSpacing(6)
        self.colorsLayout.setObjectName(u"colorsLayout")
        self.colorsLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(MatchedFilter)

        QMetaObject.connectSlotsByName(MatchedFilter)
    # setupUi

    def retranslateUi(self, MatchedFilter):
        MatchedFilter.setWindowTitle(QCoreApplication.translate("MatchedFilter", u"Form", None))
#if QT_CONFIG(tooltip)
        self.addColorButton.setToolTip(QCoreApplication.translate("MatchedFilter", u"Add a new color signature for matched filter detection. Each color can have its own threshold value.", None))
#endif // QT_CONFIG(tooltip)
        self.addColorButton.setText(QCoreApplication.translate("MatchedFilter", u"Add Color", None))
        self.addColorButton.setProperty(u"iconName", QCoreApplication.translate("MatchedFilter", u"color.png", None))
#if QT_CONFIG(tooltip)
        self.viewRangeButton.setToolTip(QCoreApplication.translate("MatchedFilter", u"Opens the Range Viewer window to:\n"
"- See the range of colors that will be searched for in the image analysis.\n"
"Use this to see what colors are going to be detected and optimize the thresholds before processing.", None))
#endif // QT_CONFIG(tooltip)
        self.viewRangeButton.setText(QCoreApplication.translate("MatchedFilter", u"View Range", None))
        self.viewRangeButton.setProperty(u"iconName", QCoreApplication.translate("MatchedFilter", u"eye.png", None))
    # retranslateUi

