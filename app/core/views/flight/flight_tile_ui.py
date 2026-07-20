# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'flight_tile.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_FlightTileContents(object):
    def setupUi(self, FlightTileContents):
        if not FlightTileContents.objectName():
            FlightTileContents.setObjectName(u"FlightTileContents")
        FlightTileContents.resize(640, 480)
        self.tileLayout = QVBoxLayout(FlightTileContents)
        self.tileLayout.setSpacing(2)
        self.tileLayout.setObjectName(u"tileLayout")
        self.tileLayout.setContentsMargins(2, 2, 2, 2)
        self.videoLabel = QLabel(FlightTileContents)
        self.videoLabel.setObjectName(u"videoLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.videoLabel.sizePolicy().hasHeightForWidth())
        self.videoLabel.setSizePolicy(sizePolicy)
        self.videoLabel.setMinimumSize(QSize(0, 0))
        self.videoLabel.setAlignment(Qt.AlignCenter)
        self.videoLabel.setStyleSheet(u"QLabel { background-color: black; color: #888; }")

        self.tileLayout.addWidget(self.videoLabel)

        self.statusStrip = QFrame(FlightTileContents)
        self.statusStrip.setObjectName(u"statusStrip")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.statusStrip.sizePolicy().hasHeightForWidth())
        self.statusStrip.setSizePolicy(sizePolicy1)
        self.statusStrip.setMaximumSize(QSize(16777215, 22))
        self.statusStrip.setFrameShape(QFrame.NoFrame)
        self.statusLayout = QHBoxLayout(self.statusStrip)
        self.statusLayout.setSpacing(10)
        self.statusLayout.setObjectName(u"statusLayout")
        self.statusLayout.setContentsMargins(6, 0, 6, 0)
        self.iceStateLabel = QLabel(self.statusStrip)
        self.iceStateLabel.setObjectName(u"iceStateLabel")

        self.statusLayout.addWidget(self.iceStateLabel)

        self.resolutionLabel = QLabel(self.statusStrip)
        self.resolutionLabel.setObjectName(u"resolutionLabel")

        self.statusLayout.addWidget(self.resolutionLabel)

        self.fpsLabel = QLabel(self.statusStrip)
        self.fpsLabel.setObjectName(u"fpsLabel")

        self.statusLayout.addWidget(self.fpsLabel)

        self.bitrateLabel = QLabel(self.statusStrip)
        self.bitrateLabel.setObjectName(u"bitrateLabel")

        self.statusLayout.addWidget(self.bitrateLabel)

        self.latencyLabel = QLabel(self.statusStrip)
        self.latencyLabel.setObjectName(u"latencyLabel")

        self.statusLayout.addWidget(self.latencyLabel)

        self.statusSpacer = QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.statusLayout.addItem(self.statusSpacer)

        self.statusBadgeLabel = QLabel(self.statusStrip)
        self.statusBadgeLabel.setObjectName(u"statusBadgeLabel")

        self.statusLayout.addWidget(self.statusBadgeLabel)


        self.tileLayout.addWidget(self.statusStrip)


        self.retranslateUi(FlightTileContents)

        QMetaObject.connectSlotsByName(FlightTileContents)
    # setupUi

    def retranslateUi(self, FlightTileContents):
        self.videoLabel.setText(QCoreApplication.translate("FlightTileContents", u"Waiting for video\u2026", None))
        self.iceStateLabel.setText(QCoreApplication.translate("FlightTileContents", u"Network: new", None))
        self.resolutionLabel.setText(QCoreApplication.translate("FlightTileContents", u"0x0", None))
        self.fpsLabel.setText(QCoreApplication.translate("FlightTileContents", u"0 fps", None))
        self.bitrateLabel.setText(QCoreApplication.translate("FlightTileContents", u"0 kbps", None))
        self.latencyLabel.setText(QCoreApplication.translate("FlightTileContents", u"latency: --", None))
        self.statusBadgeLabel.setText("")
        pass
    # retranslateUi

