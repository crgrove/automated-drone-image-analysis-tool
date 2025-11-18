# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MatchedFilterWizard.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_MatchedFilterWizard(object):
    def setupUi(self, MatchedFilterWizard):
        if not MatchedFilterWizard.objectName():
            MatchedFilterWizard.setObjectName(u"MatchedFilterWizard")
        self.verticalLayout_root = QVBoxLayout(MatchedFilterWizard)
        self.verticalLayout_root.setObjectName(u"verticalLayout_root")
        self.verticalLayout_root.setContentsMargins(0, 5, 0, 0)
        self.widgetAddButton = QWidget(MatchedFilterWizard)
        self.widgetAddButton.setObjectName(u"widgetAddButton")
        self.horizontalLayout_add = QHBoxLayout(self.widgetAddButton)
        self.horizontalLayout_add.setSpacing(10)
        self.horizontalLayout_add.setObjectName(u"horizontalLayout_add")
        self.addTargetButton = QPushButton(self.widgetAddButton)
        self.addTargetButton.setObjectName(u"addTargetButton")
        font = QFont()
        font.setPointSize(11)
        self.addTargetButton.setFont(font)
        self.addTargetButton.setMinimumSize(QSize(120, 32))

        self.horizontalLayout_add.addWidget(self.addTargetButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_add.addItem(self.horizontalSpacer)


        self.verticalLayout_root.addWidget(self.widgetAddButton)

        self.targetsContainer = QWidget(MatchedFilterWizard)
        self.targetsContainer.setObjectName(u"targetsContainer")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.targetsContainer.sizePolicy().hasHeightForWidth())
        self.targetsContainer.setSizePolicy(sizePolicy)
        self.targetsLayout = QVBoxLayout(self.targetsContainer)
        self.targetsLayout.setSpacing(6)
        self.targetsLayout.setObjectName(u"targetsLayout")
        self.targetsLayout.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_root.addWidget(self.targetsContainer)

        self.verticalSpacer_bottom = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_root.addItem(self.verticalSpacer_bottom)


        self.retranslateUi(MatchedFilterWizard)

        QMetaObject.connectSlotsByName(MatchedFilterWizard)
    # setupUi

    def retranslateUi(self, MatchedFilterWizard):
        self.addTargetButton.setText(QCoreApplication.translate("MatchedFilterWizard", u"Add Color", None))
        pass
    # retranslateUi


