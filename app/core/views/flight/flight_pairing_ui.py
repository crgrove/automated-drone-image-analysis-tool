# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'flight_pairing.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
    QLineEdit, QProgressBar, QPushButton, QSizePolicy,
    QSpacerItem, QStackedWidget, QVBoxLayout, QWidget)

class Ui_FlightPairingDialog(object):
    def setupUi(self, FlightPairingDialog):
        if not FlightPairingDialog.objectName():
            FlightPairingDialog.setObjectName(u"FlightPairingDialog")
        FlightPairingDialog.resize(460, 260)
        self.pairingLayout = QVBoxLayout(FlightPairingDialog)
        self.pairingLayout.setObjectName(u"pairingLayout")
        self.stateStack = QStackedWidget(FlightPairingDialog)
        self.stateStack.setObjectName(u"stateStack")
        self.codeEntryPage = QWidget()
        self.codeEntryPage.setObjectName(u"codeEntryPage")
        self.codePageLayout = QVBoxLayout(self.codeEntryPage)
        self.codePageLayout.setObjectName(u"codePageLayout")
        self.codeInstructions = QLabel(self.codeEntryPage)
        self.codeInstructions.setObjectName(u"codeInstructions")
        self.codeInstructions.setWordWrap(True)

        self.codePageLayout.addWidget(self.codeInstructions)

        self.codeEdit = QLineEdit(self.codeEntryPage)
        self.codeEdit.setObjectName(u"codeEdit")
        self.codeEdit.setMaxLength(9)
        font = QFont()
        font.setPointSize(14)
        self.codeEdit.setFont(font)
        self.codeEdit.setAlignment(Qt.AlignCenter)

        self.codePageLayout.addWidget(self.codeEdit)

        self.codeErrorLabel = QLabel(self.codeEntryPage)
        self.codeErrorLabel.setObjectName(u"codeErrorLabel")
        self.codeErrorLabel.setWordWrap(True)
        self.codeErrorLabel.setStyleSheet(u"QLabel { color: #c0392b; }")

        self.codePageLayout.addWidget(self.codeErrorLabel)

        self.codePageSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.codePageLayout.addItem(self.codePageSpacer)

        self.stateStack.addWidget(self.codeEntryPage)
        self.negotiatingPage = QWidget()
        self.negotiatingPage.setObjectName(u"negotiatingPage")
        self.negotiatingLayout = QVBoxLayout(self.negotiatingPage)
        self.negotiatingLayout.setObjectName(u"negotiatingLayout")
        self.negotiatingHeader = QLabel(self.negotiatingPage)
        self.negotiatingHeader.setObjectName(u"negotiatingHeader")
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(True)
        self.negotiatingHeader.setFont(font1)

        self.negotiatingLayout.addWidget(self.negotiatingHeader)

        self.negotiatingDetail = QLabel(self.negotiatingPage)
        self.negotiatingDetail.setObjectName(u"negotiatingDetail")
        self.negotiatingDetail.setWordWrap(True)

        self.negotiatingLayout.addWidget(self.negotiatingDetail)

        self.negotiatingProgress = QProgressBar(self.negotiatingPage)
        self.negotiatingProgress.setObjectName(u"negotiatingProgress")
        self.negotiatingProgress.setMaximum(0)
        self.negotiatingProgress.setValue(0)

        self.negotiatingLayout.addWidget(self.negotiatingProgress)

        self.negotiatingSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.negotiatingLayout.addItem(self.negotiatingSpacer)

        self.stateStack.addWidget(self.negotiatingPage)
        self.failedPage = QWidget()
        self.failedPage.setObjectName(u"failedPage")
        self.failedLayout = QVBoxLayout(self.failedPage)
        self.failedLayout.setObjectName(u"failedLayout")
        self.failedHeader = QLabel(self.failedPage)
        self.failedHeader.setObjectName(u"failedHeader")
        self.failedHeader.setFont(font1)

        self.failedLayout.addWidget(self.failedHeader)

        self.failedDetail = QLabel(self.failedPage)
        self.failedDetail.setObjectName(u"failedDetail")
        self.failedDetail.setWordWrap(True)

        self.failedLayout.addWidget(self.failedDetail)

        self.failedSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.failedLayout.addItem(self.failedSpacer)

        self.stateStack.addWidget(self.failedPage)

        self.pairingLayout.addWidget(self.stateStack)

        self.footerRow = QHBoxLayout()
        self.footerRow.setObjectName(u"footerRow")
        self.capHintLabel = QLabel(FlightPairingDialog)
        self.capHintLabel.setObjectName(u"capHintLabel")
        self.capHintLabel.setStyleSheet(u"QLabel { color: palette(mid); }")

        self.footerRow.addWidget(self.capHintLabel)

        self.footerSpacer = QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.footerRow.addItem(self.footerSpacer)

        self.cancelButton = QPushButton(FlightPairingDialog)
        self.cancelButton.setObjectName(u"cancelButton")

        self.footerRow.addWidget(self.cancelButton)

        self.connectButton = QPushButton(FlightPairingDialog)
        self.connectButton.setObjectName(u"connectButton")

        self.footerRow.addWidget(self.connectButton)


        self.pairingLayout.addLayout(self.footerRow)


        self.retranslateUi(FlightPairingDialog)

        self.stateStack.setCurrentIndex(0)
        self.connectButton.setDefault(True)


        QMetaObject.connectSlotsByName(FlightPairingDialog)
    # setupUi

    def retranslateUi(self, FlightPairingDialog):
        FlightPairingDialog.setWindowTitle(QCoreApplication.translate("FlightPairingDialog", u"Add Flight Feed", None))
        self.codeInstructions.setText(QCoreApplication.translate("FlightPairingDialog", u"Ask the drone operator to read out the 6-character pairing code shown on their controller.", None))
        self.codeEdit.setPlaceholderText(QCoreApplication.translate("FlightPairingDialog", u"e.g. K3F7PM", None))
        self.codeErrorLabel.setText("")
        self.negotiatingHeader.setText(QCoreApplication.translate("FlightPairingDialog", u"Pairing\u2026", None))
        self.negotiatingDetail.setText(QCoreApplication.translate("FlightPairingDialog", u"Looking up code, exchanging keys, gathering ICE candidates.", None))
        self.failedHeader.setText(QCoreApplication.translate("FlightPairingDialog", u"Pairing failed", None))
        self.failedDetail.setText("")
        self.capHintLabel.setText("")
        self.cancelButton.setText(QCoreApplication.translate("FlightPairingDialog", u"Cancel", None))
        self.connectButton.setText(QCoreApplication.translate("FlightPairingDialog", u"Connect", None))
    # retranslateUi

