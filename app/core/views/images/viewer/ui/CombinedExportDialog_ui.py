# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'CombinedExportDialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QFormLayout, QFrame,
    QLabel, QLineEdit, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_CombinedExportDialog(object):
    def setupUi(self, CombinedExportDialog):
        if not CombinedExportDialog.objectName():
            CombinedExportDialog.setObjectName(u"CombinedExportDialog")
        CombinedExportDialog.resize(460, 340)
        CombinedExportDialog.setMinimumSize(QSize(440, 0))
        CombinedExportDialog.setModal(True)
        self.verticalLayout = QVBoxLayout(CombinedExportDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.descriptionLabel = QLabel(CombinedExportDialog)
        self.descriptionLabel.setObjectName(u"descriptionLabel")
        self.descriptionLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.descriptionLabel)

        self.pdfCheckBox = QCheckBox(CombinedExportDialog)
        self.pdfCheckBox.setObjectName(u"pdfCheckBox")
        self.pdfCheckBox.setChecked(True)

        self.verticalLayout.addWidget(self.pdfCheckBox)

        self.pdfOptionsWidget = QWidget(CombinedExportDialog)
        self.pdfOptionsWidget.setObjectName(u"pdfOptionsWidget")
        self.pdfOptionsLayout = QFormLayout(self.pdfOptionsWidget)
        self.pdfOptionsLayout.setObjectName(u"pdfOptionsLayout")
        self.pdfOptionsLayout.setContentsMargins(24, 0, 0, 0)
        self.organizationLabel = QLabel(self.pdfOptionsWidget)
        self.organizationLabel.setObjectName(u"organizationLabel")

        self.pdfOptionsLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.organizationLabel)

        self.organizationLineEdit = QLineEdit(self.pdfOptionsWidget)
        self.organizationLineEdit.setObjectName(u"organizationLineEdit")

        self.pdfOptionsLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.organizationLineEdit)

        self.searchNameLabel = QLabel(self.pdfOptionsWidget)
        self.searchNameLabel.setObjectName(u"searchNameLabel")

        self.pdfOptionsLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.searchNameLabel)

        self.searchNameLineEdit = QLineEdit(self.pdfOptionsWidget)
        self.searchNameLineEdit.setObjectName(u"searchNameLineEdit")

        self.pdfOptionsLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.searchNameLineEdit)

        self.mapTilesLabel = QLabel(self.pdfOptionsWidget)
        self.mapTilesLabel.setObjectName(u"mapTilesLabel")

        self.pdfOptionsLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.mapTilesLabel)

        self.mapTilesComboBox = QComboBox(self.pdfOptionsWidget)
        self.mapTilesComboBox.setObjectName(u"mapTilesComboBox")

        self.pdfOptionsLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.mapTilesComboBox)


        self.verticalLayout.addWidget(self.pdfOptionsWidget)

        self.kmlCheckBox = QCheckBox(CombinedExportDialog)
        self.kmlCheckBox.setObjectName(u"kmlCheckBox")

        self.verticalLayout.addWidget(self.kmlCheckBox)

        self.caltopoCheckBox = QCheckBox(CombinedExportDialog)
        self.caltopoCheckBox.setObjectName(u"caltopoCheckBox")

        self.verticalLayout.addWidget(self.caltopoCheckBox)

        self.caltopoOptionsWidget = QWidget(CombinedExportDialog)
        self.caltopoOptionsWidget.setObjectName(u"caltopoOptionsWidget")
        self.caltopoOptionsLayout = QVBoxLayout(self.caltopoOptionsWidget)
        self.caltopoOptionsLayout.setObjectName(u"caltopoOptionsLayout")
        self.caltopoOptionsLayout.setContentsMargins(24, 0, 0, 0)
        self.caltopoPhotoCheckBox = QCheckBox(self.caltopoOptionsWidget)
        self.caltopoPhotoCheckBox.setObjectName(u"caltopoPhotoCheckBox")
        self.caltopoPhotoCheckBox.setChecked(True)

        self.caltopoOptionsLayout.addWidget(self.caltopoPhotoCheckBox)


        self.verticalLayout.addWidget(self.caltopoOptionsWidget)

        self.scopeSeparator = QFrame(CombinedExportDialog)
        self.scopeSeparator.setObjectName(u"scopeSeparator")
        self.scopeSeparator.setFrameShape(QFrame.Shape.HLine)
        self.scopeSeparator.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.scopeSeparator)

        self.includeImagesWithoutFlaggedAoisCheckBox = QCheckBox(CombinedExportDialog)
        self.includeImagesWithoutFlaggedAoisCheckBox.setObjectName(u"includeImagesWithoutFlaggedAoisCheckBox")

        self.verticalLayout.addWidget(self.includeImagesWithoutFlaggedAoisCheckBox)

        self.verticalSpacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.buttonBox = QDialogButtonBox(CombinedExportDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)

        QWidget.setTabOrder(self.pdfCheckBox, self.organizationLineEdit)
        QWidget.setTabOrder(self.organizationLineEdit, self.searchNameLineEdit)
        QWidget.setTabOrder(self.searchNameLineEdit, self.mapTilesComboBox)
        QWidget.setTabOrder(self.mapTilesComboBox, self.kmlCheckBox)
        QWidget.setTabOrder(self.kmlCheckBox, self.caltopoCheckBox)
        QWidget.setTabOrder(self.caltopoCheckBox, self.caltopoPhotoCheckBox)
        QWidget.setTabOrder(self.caltopoPhotoCheckBox, self.includeImagesWithoutFlaggedAoisCheckBox)

        self.retranslateUi(CombinedExportDialog)
        self.buttonBox.accepted.connect(CombinedExportDialog.accept)
        self.buttonBox.rejected.connect(CombinedExportDialog.reject)

        QMetaObject.connectSlotsByName(CombinedExportDialog)
    # setupUi

    def retranslateUi(self, CombinedExportDialog):
        CombinedExportDialog.setWindowTitle(QCoreApplication.translate("CombinedExportDialog", u"Export Combined Results", None))
        self.descriptionLabel.setText(QCoreApplication.translate("CombinedExportDialog", u"Choose what to make from the scanned results. Every output covers the same AOIs, numbered as in the PDF report.", None))
        self.pdfCheckBox.setText(QCoreApplication.translate("CombinedExportDialog", u"PDF report", None))
        self.organizationLabel.setText(QCoreApplication.translate("CombinedExportDialog", u"Organization:", None))
        self.organizationLineEdit.setPlaceholderText(QCoreApplication.translate("CombinedExportDialog", u"Enter organization name", None))
        self.searchNameLabel.setText(QCoreApplication.translate("CombinedExportDialog", u"Search Name:", None))
        self.searchNameLineEdit.setPlaceholderText(QCoreApplication.translate("CombinedExportDialog", u"Enter search name", None))
        self.mapTilesLabel.setText(QCoreApplication.translate("CombinedExportDialog", u"Map Tiles:", None))
#if QT_CONFIG(tooltip)
        self.mapTilesComboBox.setToolTip(QCoreApplication.translate("CombinedExportDialog", u"Choose the background tiles for the PDF overview map.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.kmlCheckBox.setToolTip(QCoreApplication.translate("CombinedExportDialog", u"One placemark per AOI, in a folder per result set, named as in the PDF report. Opens in Google Earth and imports into CalTopo or SARTopo.", None))
#endif // QT_CONFIG(tooltip)
        self.kmlCheckBox.setText(QCoreApplication.translate("CombinedExportDialog", u"KML file of detections", None))
#if QT_CONFIG(tooltip)
        self.caltopoCheckBox.setToolTip(QCoreApplication.translate("CombinedExportDialog", u"Add a marker for every AOI to a CalTopo map. You will choose how to sign in and which map next.", None))
#endif // QT_CONFIG(tooltip)
        self.caltopoCheckBox.setText(QCoreApplication.translate("CombinedExportDialog", u"Add detections to CalTopo", None))
#if QT_CONFIG(tooltip)
        self.caltopoPhotoCheckBox.setToolTip(QCoreApplication.translate("CombinedExportDialog", u"Upload each AOI's photo from the PDF report (the full image with zoomed insets) to its marker. Turn off on a slow connection.", None))
#endif // QT_CONFIG(tooltip)
        self.caltopoPhotoCheckBox.setText(QCoreApplication.translate("CombinedExportDialog", u"Attach the report photo to each marker", None))
#if QT_CONFIG(tooltip)
        self.includeImagesWithoutFlaggedAoisCheckBox.setToolTip(QCoreApplication.translate("CombinedExportDialog", u"Applies to every output. When unchecked, only flagged AOIs (and AOIs a reviewer commented on) are exported. When checked, images with no flagged AOIs are also exported, with all of their AOIs.", None))
#endif // QT_CONFIG(tooltip)
        self.includeImagesWithoutFlaggedAoisCheckBox.setText(QCoreApplication.translate("CombinedExportDialog", u"Include images without flagged AOIs", None))
    # retranslateUi

