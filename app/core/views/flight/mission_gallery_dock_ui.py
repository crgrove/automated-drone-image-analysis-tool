# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mission_gallery_dock.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_MissionGalleryContents(object):
    def setupUi(self, MissionGalleryContents):
        if not MissionGalleryContents.objectName():
            MissionGalleryContents.setObjectName(u"MissionGalleryContents")
        MissionGalleryContents.resize(380, 540)
        self.missionLayout = QVBoxLayout(MissionGalleryContents)
        self.missionLayout.setSpacing(4)
        self.missionLayout.setObjectName(u"missionLayout")
        self.missionLayout.setContentsMargins(4, 4, 4, 4)
        self.filterGroup = QGroupBox(MissionGalleryContents)
        self.filterGroup.setObjectName(u"filterGroup")
        self.filterGrid = QGridLayout(self.filterGroup)
        self.filterGrid.setObjectName(u"filterGrid")
        self.feedFilterLabel = QLabel(self.filterGroup)
        self.feedFilterLabel.setObjectName(u"feedFilterLabel")

        self.filterGrid.addWidget(self.feedFilterLabel, 0, 0, 1, 1)

        self.feedFilterCombo = QComboBox(self.filterGroup)
        self.feedFilterCombo.setObjectName(u"feedFilterCombo")

        self.filterGrid.addWidget(self.feedFilterCombo, 0, 1, 1, 1)

        self.detectorFilterLabel = QLabel(self.filterGroup)
        self.detectorFilterLabel.setObjectName(u"detectorFilterLabel")

        self.filterGrid.addWidget(self.detectorFilterLabel, 1, 0, 1, 1)

        self.detectorFilterCombo = QComboBox(self.filterGroup)
        self.detectorFilterCombo.setObjectName(u"detectorFilterCombo")

        self.filterGrid.addWidget(self.detectorFilterCombo, 1, 1, 1, 1)

        self.minScoreLabel = QLabel(self.filterGroup)
        self.minScoreLabel.setObjectName(u"minScoreLabel")

        self.filterGrid.addWidget(self.minScoreLabel, 2, 0, 1, 1)

        self.minScoreSpin = QDoubleSpinBox(self.filterGroup)
        self.minScoreSpin.setObjectName(u"minScoreSpin")
        self.minScoreSpin.setDecimals(2)
        self.minScoreSpin.setMinimum(0.000000000000000)
        self.minScoreSpin.setMaximum(1.000000000000000)
        self.minScoreSpin.setSingleStep(0.050000000000000)

        self.filterGrid.addWidget(self.minScoreSpin, 2, 1, 1, 1)


        self.missionLayout.addWidget(self.filterGroup)

        self.missionList = QListWidget(MissionGalleryContents)
        self.missionList.setObjectName(u"missionList")
        self.missionList.setAlternatingRowColors(True)
        self.missionList.setIconSize(QSize(128, 96))

        self.missionLayout.addWidget(self.missionList)

        self.exportRow = QHBoxLayout()
        self.exportRow.setObjectName(u"exportRow")
        self.rowCountLabel = QLabel(MissionGalleryContents)
        self.rowCountLabel.setObjectName(u"rowCountLabel")

        self.exportRow.addWidget(self.rowCountLabel)

        self.exportSpacer = QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.exportRow.addItem(self.exportSpacer)

        self.exportButton = QPushButton(MissionGalleryContents)
        self.exportButton.setObjectName(u"exportButton")

        self.exportRow.addWidget(self.exportButton)


        self.missionLayout.addLayout(self.exportRow)


        self.retranslateUi(MissionGalleryContents)

        QMetaObject.connectSlotsByName(MissionGalleryContents)
    # setupUi

    def retranslateUi(self, MissionGalleryContents):
        self.filterGroup.setTitle(QCoreApplication.translate("MissionGalleryContents", u"Filters", None))
        self.feedFilterLabel.setText(QCoreApplication.translate("MissionGalleryContents", u"Feed", None))
        self.detectorFilterLabel.setText(QCoreApplication.translate("MissionGalleryContents", u"Detector", None))
        self.minScoreLabel.setText(QCoreApplication.translate("MissionGalleryContents", u"Min score", None))
        self.rowCountLabel.setText(QCoreApplication.translate("MissionGalleryContents", u"0 detections", None))
        self.exportButton.setText(QCoreApplication.translate("MissionGalleryContents", u"Export", None))
#if QT_CONFIG(tooltip)
        self.exportButton.setToolTip(QCoreApplication.translate("MissionGalleryContents", u"Export filtered detections to the standard ADIAT image-mode gallery format.", None))
#endif // QT_CONFIG(tooltip)
        pass
    # retranslateUi

