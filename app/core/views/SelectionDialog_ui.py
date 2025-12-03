# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SelectionDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
    QSizePolicy, QSpacerItem, QToolButton, QVBoxLayout,
    QWidget)

class Ui_MediaSelector(object):
    def setupUi(self, MediaSelector):
        if not MediaSelector.objectName():
            MediaSelector.setObjectName(u"MediaSelector")
        MediaSelector.resize(425, 265)
        self.verticalLayout_3 = QVBoxLayout(MediaSelector)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label = QLabel(MediaSelector)
        self.label.setObjectName(u"label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(16)
        self.label.setFont(font)

        self.verticalLayout_3.addWidget(self.label)

        self.selectionWidget = QWidget(MediaSelector)
        self.selectionWidget.setObjectName(u"selectionWidget")
        self.horizontalLayout_2 = QHBoxLayout(self.selectionWidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.imageWidget = QWidget(self.selectionWidget)
        self.imageWidget.setObjectName(u"imageWidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.imageWidget.sizePolicy().hasHeightForWidth())
        self.imageWidget.setSizePolicy(sizePolicy1)
        self.verticalLayout = QVBoxLayout(self.imageWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer_top = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_top)

        self.imageButton = QToolButton(self.imageWidget)
        self.imageButton.setObjectName(u"imageButton")
        self.imageButton.setMinimumSize(QSize(150, 150))
        self.imageButton.setMaximumSize(QSize(150, 150))
        font1 = QFont()
        font1.setPointSize(12)
        self.imageButton.setFont(font1)
        self.imageButton.setStyleSheet(u"QToolButton { border: 3px solid palette(mid); border-radius: 8px; }")
        self.imageButton.setIconSize(QSize(100, 100))
        self.imageButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.verticalLayout.addWidget(self.imageButton, 0, Qt.AlignHCenter)

        self.verticalSpacer_bottom = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_bottom)


        self.horizontalLayout_2.addWidget(self.imageWidget)

        self.streamWidget = QWidget(self.selectionWidget)
        self.streamWidget.setObjectName(u"streamWidget")
        sizePolicy1.setHeightForWidth(self.streamWidget.sizePolicy().hasHeightForWidth())
        self.streamWidget.setSizePolicy(sizePolicy1)
        self.verticalLayout_2 = QVBoxLayout(self.streamWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalSpacer_top_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_top_2)

        self.streamButton = QToolButton(self.streamWidget)
        self.streamButton.setObjectName(u"streamButton")
        self.streamButton.setMinimumSize(QSize(150, 150))
        self.streamButton.setMaximumSize(QSize(150, 150))
        self.streamButton.setFont(font1)
        self.streamButton.setStyleSheet(u"QToolButton { border: 3px solid palette(mid); border-radius: 8px; }")
        self.streamButton.setIconSize(QSize(100, 100))
        self.streamButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.verticalLayout_2.addWidget(self.streamButton, 0, Qt.AlignHCenter)

        self.verticalSpacer_bottom_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_bottom_2)


        self.horizontalLayout_2.addWidget(self.streamWidget)


        self.verticalLayout_3.addWidget(self.selectionWidget)


        self.retranslateUi(MediaSelector)

        QMetaObject.connectSlotsByName(MediaSelector)
    # setupUi

    def retranslateUi(self, MediaSelector):
        MediaSelector.setWindowTitle(QCoreApplication.translate("MediaSelector", u"Automated Drone Image Analysis Tool (ADIAT)", None))
        self.label.setText(QCoreApplication.translate("MediaSelector", u"What type of media are you working with?", None))
        self.imageButton.setText(QCoreApplication.translate("MediaSelector", u"Images", None))
#if QT_CONFIG(tooltip)
        self.streamButton.setToolTip(QCoreApplication.translate("MediaSelector", u"RTMP, Video Files, HDMI Capture", None))
#endif // QT_CONFIG(tooltip)
        self.streamButton.setText(QCoreApplication.translate("MediaSelector", u"Streaming", None))
    # retranslateUi

