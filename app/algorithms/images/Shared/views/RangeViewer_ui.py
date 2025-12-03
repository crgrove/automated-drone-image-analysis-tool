# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'RangeViewer.ui'
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
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_ColorRangeViewer(object):
    def setupUi(self, ColorRangeViewer):
        if not ColorRangeViewer.objectName():
            ColorRangeViewer.setObjectName(u"ColorRangeViewer")
        ColorRangeViewer.resize(1200, 700)
        self.verticalLayout = QVBoxLayout(ColorRangeViewer)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.selectedWidget = QWidget(ColorRangeViewer)
        self.selectedWidget.setObjectName(u"selectedWidget")
        self.verticalLayout_2 = QVBoxLayout(self.selectedWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.selectedLabel = QLabel(self.selectedWidget)
        self.selectedLabel.setObjectName(u"selectedLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.selectedLabel.sizePolicy().hasHeightForWidth())
        self.selectedLabel.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(16)
        self.selectedLabel.setFont(font)
        self.selectedLabel.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.selectedLabel)

        self.selectedLayout = QHBoxLayout()
        self.selectedLayout.setSpacing(0)
        self.selectedLayout.setObjectName(u"selectedLayout")

        self.verticalLayout_2.addLayout(self.selectedLayout)


        self.verticalLayout.addWidget(self.selectedWidget)

        self.widget = QWidget(ColorRangeViewer)
        self.widget.setObjectName(u"widget")
        self.verticalLayout_3 = QVBoxLayout(self.widget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.label)

        self.unselectedLayout = QHBoxLayout()
        self.unselectedLayout.setSpacing(0)
        self.unselectedLayout.setObjectName(u"unselectedLayout")

        self.verticalLayout_3.addLayout(self.unselectedLayout)


        self.verticalLayout.addWidget(self.widget)


        self.retranslateUi(ColorRangeViewer)

        QMetaObject.connectSlotsByName(ColorRangeViewer)
    # setupUi

    def retranslateUi(self, ColorRangeViewer):
        ColorRangeViewer.setWindowTitle(QCoreApplication.translate("ColorRangeViewer", u"Color Range Viewer", None))
#if QT_CONFIG(tooltip)
        self.selectedLabel.setToolTip(QCoreApplication.translate("ColorRangeViewer", u"Selected images for viewing.\n"
"Shows images that you've chosen to view in the range viewer.\n"
"Click on images below to add or remove them from this section.", None))
#endif // QT_CONFIG(tooltip)
        self.selectedLabel.setText(QCoreApplication.translate("ColorRangeViewer", u"Selected", None))
#if QT_CONFIG(tooltip)
        self.label.setToolTip(QCoreApplication.translate("ColorRangeViewer", u"Available images for viewing.\n"
"Shows all images from the input folder that are available to select.\n"
"Click on images to move them to the Selected section above.", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("ColorRangeViewer", u"Unselected", None))
    # retranslateUi

