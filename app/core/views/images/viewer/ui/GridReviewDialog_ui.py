# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'GridReviewDialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QFormLayout, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QSpinBox,
    QVBoxLayout, QWidget)

class Ui_GridReviewDialog(object):
    def setupUi(self, GridReviewDialog):
        if not GridReviewDialog.objectName():
            GridReviewDialog.setObjectName(u"GridReviewDialog")
        GridReviewDialog.resize(380, 260)
        self.verticalLayout = QVBoxLayout(GridReviewDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.descriptionLabel = QLabel(GridReviewDialog)
        self.descriptionLabel.setObjectName(u"descriptionLabel")
        self.descriptionLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.descriptionLabel)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.rowsLabel = QLabel(GridReviewDialog)
        self.rowsLabel.setObjectName(u"rowsLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.rowsLabel)

        self.rowsSpinBox = QSpinBox(GridReviewDialog)
        self.rowsSpinBox.setObjectName(u"rowsSpinBox")
        self.rowsSpinBox.setMinimum(1)
        self.rowsSpinBox.setMaximum(12)
        self.rowsSpinBox.setValue(4)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.rowsSpinBox)

        self.colsLabel = QLabel(GridReviewDialog)
        self.colsLabel.setObjectName(u"colsLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.colsLabel)

        self.colsSpinBox = QSpinBox(GridReviewDialog)
        self.colsSpinBox.setObjectName(u"colsSpinBox")
        self.colsSpinBox.setMinimum(1)
        self.colsSpinBox.setMaximum(12)
        self.colsSpinBox.setValue(4)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.colsSpinBox)


        self.verticalLayout.addLayout(self.formLayout)

        self.autoMarkCheckBox = QCheckBox(GridReviewDialog)
        self.autoMarkCheckBox.setObjectName(u"autoMarkCheckBox")
        self.autoMarkCheckBox.setChecked(True)

        self.verticalLayout.addWidget(self.autoMarkCheckBox)

        self.subGuideCheckBox = QCheckBox(GridReviewDialog)
        self.subGuideCheckBox.setObjectName(u"subGuideCheckBox")
        self.subGuideCheckBox.setChecked(True)

        self.verticalLayout.addWidget(self.subGuideCheckBox)

        self.applyAllCheckBox = QCheckBox(GridReviewDialog)
        self.applyAllCheckBox.setObjectName(u"applyAllCheckBox")

        self.verticalLayout.addWidget(self.applyAllCheckBox)

        self.suggestionLayout = QHBoxLayout()
        self.suggestionLayout.setObjectName(u"suggestionLayout")
        self.suggestionLabel = QLabel(GridReviewDialog)
        self.suggestionLabel.setObjectName(u"suggestionLabel")
        self.suggestionLabel.setWordWrap(True)

        self.suggestionLayout.addWidget(self.suggestionLabel)

        self.useSuggestionButton = QPushButton(GridReviewDialog)
        self.useSuggestionButton.setObjectName(u"useSuggestionButton")
        self.useSuggestionButton.setEnabled(False)

        self.suggestionLayout.addWidget(self.useSuggestionButton)


        self.verticalLayout.addLayout(self.suggestionLayout)

        self.verticalSpacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.buttonBox = QDialogButtonBox(GridReviewDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(GridReviewDialog)
        self.buttonBox.accepted.connect(GridReviewDialog.accept)
        self.buttonBox.rejected.connect(GridReviewDialog.reject)

        QMetaObject.connectSlotsByName(GridReviewDialog)
    # setupUi

    def retranslateUi(self, GridReviewDialog):
        GridReviewDialog.setWindowTitle(QCoreApplication.translate("GridReviewDialog", u"Grid Review Settings", None))
        self.descriptionLabel.setText(QCoreApplication.translate("GridReviewDialog", u"Choose how many cells the review grid divides each image into. Smaller cells mean a higher zoom per cell.", None))
        self.rowsLabel.setText(QCoreApplication.translate("GridReviewDialog", u"Rows", None))
        self.colsLabel.setText(QCoreApplication.translate("GridReviewDialog", u"Columns", None))
        self.autoMarkCheckBox.setText(QCoreApplication.translate("GridReviewDialog", u"Mark cells reviewed when advancing (Space)", None))
#if QT_CONFIG(tooltip)
        self.subGuideCheckBox.setToolTip(QCoreApplication.translate("GridReviewDialog", u"Draw a 3\u00d73 guide inside the active cell to focus your scan. Visual only \u2014 it does not change what gets reviewed.", None))
#endif // QT_CONFIG(tooltip)
        self.subGuideCheckBox.setText(QCoreApplication.translate("GridReviewDialog", u"Show 3\u00d73 focus guide inside each cell", None))
#if QT_CONFIG(tooltip)
        self.applyAllCheckBox.setToolTip(QCoreApplication.translate("GridReviewDialog", u"Apply the chosen rows and columns to every image in this dataset, not just the current one. Images you have already started reviewing keep their progress unless you confirm a reset.", None))
#endif // QT_CONFIG(tooltip)
        self.applyAllCheckBox.setText(QCoreApplication.translate("GridReviewDialog", u"Apply this grid size to all images", None))
        self.suggestionLabel.setText(QCoreApplication.translate("GridReviewDialog", u"No grid suggestion available (image GSD unknown).", None))
        self.useSuggestionButton.setText(QCoreApplication.translate("GridReviewDialog", u"Use Suggestion", None))
    # retranslateUi

