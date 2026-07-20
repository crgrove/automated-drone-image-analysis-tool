# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'telemetry_hud.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_TelemetryHud(object):
    def setupUi(self, TelemetryHud):
        if not TelemetryHud.objectName():
            TelemetryHud.setObjectName(u"TelemetryHud")
        TelemetryHud.resize(640, 56)
        TelemetryHud.setStyleSheet(u"QWidget { background-color: rgba(0, 0, 0, 160); color: #e8e8e8; }\n"
"QLabel { font-family: \"Consolas\", \"Courier New\", monospace; font-size: 11px; }\n"
"QLabel#staleBadge { color: #ff8080; font-weight: bold; }\n"
"QLabel#batteryChip { padding-left: 4px; padding-right: 4px; border-radius: 2px; }")
        self.hudLayout = QVBoxLayout(TelemetryHud)
        self.hudLayout.setSpacing(1)
        self.hudLayout.setObjectName(u"hudLayout")
        self.hudLayout.setContentsMargins(6, 2, 6, 2)
        self.row1Layout = QHBoxLayout()
        self.row1Layout.setSpacing(12)
        self.row1Layout.setObjectName(u"row1Layout")
        self.latLabel = QLabel(TelemetryHud)
        self.latLabel.setObjectName(u"latLabel")

        self.row1Layout.addWidget(self.latLabel)

        self.lonLabel = QLabel(TelemetryHud)
        self.lonLabel.setObjectName(u"lonLabel")

        self.row1Layout.addWidget(self.lonLabel)

        self.altLabel = QLabel(TelemetryHud)
        self.altLabel.setObjectName(u"altLabel")

        self.row1Layout.addWidget(self.altLabel)

        self.row1Spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.row1Layout.addItem(self.row1Spacer)

        self.staleBadge = QLabel(TelemetryHud)
        self.staleBadge.setObjectName(u"staleBadge")

        self.row1Layout.addWidget(self.staleBadge)


        self.hudLayout.addLayout(self.row1Layout)

        self.row2Layout = QHBoxLayout()
        self.row2Layout.setSpacing(12)
        self.row2Layout.setObjectName(u"row2Layout")
        self.headingLabel = QLabel(TelemetryHud)
        self.headingLabel.setObjectName(u"headingLabel")

        self.row2Layout.addWidget(self.headingLabel)

        self.speedLabel = QLabel(TelemetryHud)
        self.speedLabel.setObjectName(u"speedLabel")

        self.row2Layout.addWidget(self.speedLabel)

        self.verticalSpeedLabel = QLabel(TelemetryHud)
        self.verticalSpeedLabel.setObjectName(u"verticalSpeedLabel")

        self.row2Layout.addWidget(self.verticalSpeedLabel)

        self.batteryLabel = QLabel(TelemetryHud)
        self.batteryLabel.setObjectName(u"batteryLabel")

        self.row2Layout.addWidget(self.batteryLabel)

        self.batteryChip = QLabel(TelemetryHud)
        self.batteryChip.setObjectName(u"batteryChip")

        self.row2Layout.addWidget(self.batteryChip)

        self.flightModeLabel = QLabel(TelemetryHud)
        self.flightModeLabel.setObjectName(u"flightModeLabel")

        self.row2Layout.addWidget(self.flightModeLabel)

        self.row2Spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.row2Layout.addItem(self.row2Spacer)


        self.hudLayout.addLayout(self.row2Layout)


        self.retranslateUi(TelemetryHud)

        QMetaObject.connectSlotsByName(TelemetryHud)
    # setupUi

    def retranslateUi(self, TelemetryHud):
        self.latLabel.setText(QCoreApplication.translate("TelemetryHud", u"LAT \u2014", None))
        self.lonLabel.setText(QCoreApplication.translate("TelemetryHud", u"LON \u2014", None))
        self.altLabel.setText(QCoreApplication.translate("TelemetryHud", u"ALT \u2014", None))
        self.staleBadge.setText("")
        self.headingLabel.setText(QCoreApplication.translate("TelemetryHud", u"HDG \u2014", None))
        self.speedLabel.setText(QCoreApplication.translate("TelemetryHud", u"SPD \u2014", None))
        self.verticalSpeedLabel.setText(QCoreApplication.translate("TelemetryHud", u"\u2195 \u2014", None))
        self.batteryLabel.setText(QCoreApplication.translate("TelemetryHud", u"BAT", None))
        self.batteryChip.setText(QCoreApplication.translate("TelemetryHud", u"\u2014", None))
        self.flightModeLabel.setText(QCoreApplication.translate("TelemetryHud", u"\u2014", None))
        pass
    # retranslateUi

