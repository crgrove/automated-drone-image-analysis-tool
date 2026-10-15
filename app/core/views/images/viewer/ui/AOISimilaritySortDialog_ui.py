# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AOISimilaritySortDialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QDoubleSpinBox, QFormLayout, QLabel, QSizePolicy,
    QSpacerItem, QSpinBox, QVBoxLayout, QWidget)

class Ui_AOISimilaritySortDialog(object):
    def setupUi(self, AOISimilaritySortDialog):
        if not AOISimilaritySortDialog.objectName():
            AOISimilaritySortDialog.setObjectName(u"AOISimilaritySortDialog")
        AOISimilaritySortDialog.resize(420, 200)
        AOISimilaritySortDialog.setMinimumSize(QSize(420, 0))
        AOISimilaritySortDialog.setModal(True)
        self.verticalLayout = QVBoxLayout(AOISimilaritySortDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.descriptionLabel = QLabel(AOISimilaritySortDialog)
        self.descriptionLabel.setObjectName(u"descriptionLabel")
        self.descriptionLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.descriptionLabel)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.distanceLabel = QLabel(AOISimilaritySortDialog)
        self.distanceLabel.setObjectName(u"distanceLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.distanceLabel)

        self.distanceSpinBox = QDoubleSpinBox(AOISimilaritySortDialog)
        self.distanceSpinBox.setObjectName(u"distanceSpinBox")
        self.distanceSpinBox.setDecimals(1)
        self.distanceSpinBox.setSingleStep(5.000000000000000)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.distanceSpinBox)

        self.similarityLabel = QLabel(AOISimilaritySortDialog)
        self.similarityLabel.setObjectName(u"similarityLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.similarityLabel)

        self.similaritySpinBox = QSpinBox(AOISimilaritySortDialog)
        self.similaritySpinBox.setObjectName(u"similaritySpinBox")
        self.similaritySpinBox.setMinimum(1)
        self.similaritySpinBox.setMaximum(100)
        self.similaritySpinBox.setValue(70)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.similaritySpinBox)


        self.verticalLayout.addLayout(self.formLayout)

        self.verticalSpacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.buttonBox = QDialogButtonBox(AOISimilaritySortDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(AOISimilaritySortDialog)
        self.buttonBox.accepted.connect(AOISimilaritySortDialog.accept)
        self.buttonBox.rejected.connect(AOISimilaritySortDialog.reject)

        QMetaObject.connectSlotsByName(AOISimilaritySortDialog)
    # setupUi

    def retranslateUi(self, AOISimilaritySortDialog):
        AOISimilaritySortDialog.setWindowTitle(QCoreApplication.translate("AOISimilaritySortDialog", u"Sort: Similar & Nearby", None))
        self.descriptionLabel.setText(QCoreApplication.translate("AOISimilaritySortDialog", u"Places AOIs that look alike (the same score as Find Similar AOIs, Shift+Z) and are close together on the ground next to each other. The largest groups come first; AOIs without a match follow in their usual order.", None))
        self.distanceLabel.setText(QCoreApplication.translate("AOISimilaritySortDialog", u"Max distance apart:", None))
#if QT_CONFIG(tooltip)
        self.distanceSpinBox.setToolTip(QCoreApplication.translate("AOISimilaritySortDialog", u"Largest ground distance between two AOIs in the same group, from their estimated GPS positions.", None))
#endif // QT_CONFIG(tooltip)
        self.similarityLabel.setText(QCoreApplication.translate("AOISimilaritySortDialog", u"Min similarity:", None))
#if QT_CONFIG(tooltip)
        self.similaritySpinBox.setToolTip(QCoreApplication.translate("AOISimilaritySortDialog", u"Smallest visual similarity between two AOIs in the same group.", None))
#endif // QT_CONFIG(tooltip)
        self.similaritySpinBox.setSuffix(QCoreApplication.translate("AOISimilaritySortDialog", u"%", None))
    # retranslateUi

