# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AOIDuplicatePickerDialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QDialog,
    QDialogButtonBox, QFrame, QHBoxLayout, QLabel,
    QListView, QListWidget, QListWidgetItem, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_AOIDuplicatePickerDialog(object):
    def setupUi(self, AOIDuplicatePickerDialog):
        if not AOIDuplicatePickerDialog.objectName():
            AOIDuplicatePickerDialog.setObjectName(u"AOIDuplicatePickerDialog")
        AOIDuplicatePickerDialog.resize(820, 400)
        AOIDuplicatePickerDialog.setMinimumSize(QSize(560, 360))
        AOIDuplicatePickerDialog.setModal(True)
        self.verticalLayout = QVBoxLayout(AOIDuplicatePickerDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.instructionLabel = QLabel(AOIDuplicatePickerDialog)
        self.instructionLabel.setObjectName(u"instructionLabel")
        self.instructionLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.instructionLabel)

        self.contentLayout = QHBoxLayout()
        self.contentLayout.setObjectName(u"contentLayout")
        self.sourceLayout = QVBoxLayout()
        self.sourceLayout.setObjectName(u"sourceLayout")
        self.sourceTitleLabel = QLabel(AOIDuplicatePickerDialog)
        self.sourceTitleLabel.setObjectName(u"sourceTitleLabel")
        self.sourceTitleLabel.setAlignment(Qt.AlignCenter)

        self.sourceLayout.addWidget(self.sourceTitleLabel)

        self.sourceThumbnailLabel = QLabel(AOIDuplicatePickerDialog)
        self.sourceThumbnailLabel.setObjectName(u"sourceThumbnailLabel")
        self.sourceThumbnailLabel.setMinimumSize(QSize(150, 150))
        self.sourceThumbnailLabel.setMaximumSize(QSize(150, 150))
        self.sourceThumbnailLabel.setFrameShape(QFrame.StyledPanel)
        self.sourceThumbnailLabel.setAlignment(Qt.AlignCenter)

        self.sourceLayout.addWidget(self.sourceThumbnailLabel)

        self.sourceCaptionLabel = QLabel(AOIDuplicatePickerDialog)
        self.sourceCaptionLabel.setObjectName(u"sourceCaptionLabel")
        self.sourceCaptionLabel.setAlignment(Qt.AlignCenter)
        self.sourceCaptionLabel.setWordWrap(True)

        self.sourceLayout.addWidget(self.sourceCaptionLabel)

        self.sourceSpacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.sourceLayout.addItem(self.sourceSpacer)


        self.contentLayout.addLayout(self.sourceLayout)

        self.separatorLine = QFrame(AOIDuplicatePickerDialog)
        self.separatorLine.setObjectName(u"separatorLine")
        self.separatorLine.setFrameShape(QFrame.Shape.VLine)
        self.separatorLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.contentLayout.addWidget(self.separatorLine)

        self.candidatesLayout = QVBoxLayout()
        self.candidatesLayout.setObjectName(u"candidatesLayout")
        self.candidatesTitleLabel = QLabel(AOIDuplicatePickerDialog)
        self.candidatesTitleLabel.setObjectName(u"candidatesTitleLabel")

        self.candidatesLayout.addWidget(self.candidatesTitleLabel)

        self.candidateList = QListWidget(AOIDuplicatePickerDialog)
        self.candidateList.setObjectName(u"candidateList")
        self.candidateList.setMinimumSize(QSize(360, 220))
        self.candidateList.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.candidateList.setIconSize(QSize(150, 150))
        self.candidateList.setMovement(QListView.Static)
        self.candidateList.setFlow(QListView.LeftToRight)
        self.candidateList.setProperty(u"isWrapping", False)
        self.candidateList.setResizeMode(QListView.Adjust)
        self.candidateList.setSpacing(6)
        self.candidateList.setGridSize(QSize(172, 200))
        self.candidateList.setViewMode(QListView.IconMode)
        self.candidateList.setUniformItemSizes(True)
        self.candidateList.setTextElideMode(Qt.ElideMiddle)
        self.candidateList.setWordWrap(True)

        self.candidatesLayout.addWidget(self.candidateList)


        self.contentLayout.addLayout(self.candidatesLayout)


        self.verticalLayout.addLayout(self.contentLayout)

        self.buttonBox = QDialogButtonBox(AOIDuplicatePickerDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(AOIDuplicatePickerDialog)
        self.buttonBox.accepted.connect(AOIDuplicatePickerDialog.accept)
        self.buttonBox.rejected.connect(AOIDuplicatePickerDialog.reject)

        QMetaObject.connectSlotsByName(AOIDuplicatePickerDialog)
    # setupUi

    def retranslateUi(self, AOIDuplicatePickerDialog):
        AOIDuplicatePickerDialog.setWindowTitle(QCoreApplication.translate("AOIDuplicatePickerDialog", u"Mark as Duplicate", None))
        self.instructionLabel.setText(QCoreApplication.translate("AOIDuplicatePickerDialog", u"Pick the AOI this one is another sighting of. Reports show that AOI once, at its position, and list this image and AOI number under it. The best match (closest and most alike) is selected - press Enter to confirm.", None))
        self.sourceTitleLabel.setText(QCoreApplication.translate("AOIDuplicatePickerDialog", u"This AOI", None))
        self.candidatesTitleLabel.setText(QCoreApplication.translate("AOIDuplicatePickerDialog", u"Is a duplicate of", None))
#if QT_CONFIG(tooltip)
        self.candidateList.setToolTip(QCoreApplication.translate("AOIDuplicatePickerDialog", u"Flagged AOIs and AOIs that already have duplicates, best match first. Double-click to choose one.", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

