# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'detection_row.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_DetectionRowWidget(object):
    def setupUi(self, DetectionRowWidget):
        if not DetectionRowWidget.objectName():
            DetectionRowWidget.setObjectName(u"DetectionRowWidget")
        DetectionRowWidget.resize(360, 104)
        self.rowLayout = QHBoxLayout(DetectionRowWidget)
        self.rowLayout.setSpacing(6)
        self.rowLayout.setObjectName(u"rowLayout")
        self.rowLayout.setContentsMargins(4, 4, 4, 4)
        self.thumbnailLabel = QLabel(DetectionRowWidget)
        self.thumbnailLabel.setObjectName(u"thumbnailLabel")
        self.thumbnailLabel.setMinimumSize(QSize(128, 96))
        self.thumbnailLabel.setMaximumSize(QSize(128, 96))
        self.thumbnailLabel.setAlignment(Qt.AlignCenter)
        self.thumbnailLabel.setStyleSheet(u"QLabel { background-color: #222; border: 1px solid #444; }")

        self.rowLayout.addWidget(self.thumbnailLabel)

        self.metaLayout = QVBoxLayout()
        self.metaLayout.setSpacing(2)
        self.metaLayout.setObjectName(u"metaLayout")
        self.classLabel = QLabel(DetectionRowWidget)
        self.classLabel.setObjectName(u"classLabel")
        font = QFont()
        font.setBold(True)
        self.classLabel.setFont(font)

        self.metaLayout.addWidget(self.classLabel)

        self.confidenceLabel = QLabel(DetectionRowWidget)
        self.confidenceLabel.setObjectName(u"confidenceLabel")

        self.metaLayout.addWidget(self.confidenceLabel)

        self.locationLabel = QLabel(DetectionRowWidget)
        self.locationLabel.setObjectName(u"locationLabel")

        self.metaLayout.addWidget(self.locationLabel)

        self.timestampLabel = QLabel(DetectionRowWidget)
        self.timestampLabel.setObjectName(u"timestampLabel")

        self.metaLayout.addWidget(self.timestampLabel)

        self.feedLabel = QLabel(DetectionRowWidget)
        self.feedLabel.setObjectName(u"feedLabel")
        self.feedLabel.setStyleSheet(u"QLabel { color: palette(mid); font-size: 10px; }")

        self.metaLayout.addWidget(self.feedLabel)


        self.rowLayout.addLayout(self.metaLayout)

        self.actionsLayout = QVBoxLayout()
        self.actionsLayout.setObjectName(u"actionsLayout")
        self.viewButton = QPushButton(DetectionRowWidget)
        self.viewButton.setObjectName(u"viewButton")

        self.actionsLayout.addWidget(self.viewButton)

        self.copyCoordsButton = QPushButton(DetectionRowWidget)
        self.copyCoordsButton.setObjectName(u"copyCoordsButton")

        self.actionsLayout.addWidget(self.copyCoordsButton)


        self.rowLayout.addLayout(self.actionsLayout)


        self.retranslateUi(DetectionRowWidget)

        QMetaObject.connectSlotsByName(DetectionRowWidget)
    # setupUi

    def retranslateUi(self, DetectionRowWidget):
        self.thumbnailLabel.setText("")
        self.classLabel.setText(QCoreApplication.translate("DetectionRowWidget", u"CLASS", None))
        self.confidenceLabel.setText(QCoreApplication.translate("DetectionRowWidget", u"--%", None))
        self.locationLabel.setText(QCoreApplication.translate("DetectionRowWidget", u"--, --", None))
        self.timestampLabel.setText(QCoreApplication.translate("DetectionRowWidget", u"--:--:--", None))
        self.feedLabel.setText(QCoreApplication.translate("DetectionRowWidget", u"Feed: --", None))
        self.viewButton.setText(QCoreApplication.translate("DetectionRowWidget", u"View", None))
#if QT_CONFIG(tooltip)
        self.viewButton.setToolTip(QCoreApplication.translate("DetectionRowWidget", u"Open the full-size thumbnail and metadata.", None))
#endif // QT_CONFIG(tooltip)
        self.copyCoordsButton.setText(QCoreApplication.translate("DetectionRowWidget", u"Copy GPS", None))
#if QT_CONFIG(tooltip)
        self.copyCoordsButton.setToolTip(QCoreApplication.translate("DetectionRowWidget", u"Copy the detection's coordinates to the clipboard in the operator-preferred format.", None))
#endif // QT_CONFIG(tooltip)
        pass
    # retranslateUi

