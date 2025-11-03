# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Viewer.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGraphicsView, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMainWindow, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QSplitter,
    QToolButton, QVBoxLayout, QWidget)
from . import resources_rc

class Ui_Viewer(object):
    def setupUi(self, Viewer):
        if not Viewer.objectName():
            Viewer.setObjectName(u"Viewer")
        Viewer.resize(1552, 951)
        icon = QIcon()
        icon.addFile(u":/ADIAT.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        Viewer.setWindowIcon(icon)
        self.actionOpen = QAction(Viewer)
        self.actionOpen.setObjectName(u"actionOpen")
        self.outerWidget = QWidget(Viewer)
        self.outerWidget.setObjectName(u"outerWidget")
        self.verticalLayout = QVBoxLayout(self.outerWidget)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, -1, -1, 9)
        self.mainWidget = QWidget(self.outerWidget)
        self.mainWidget.setObjectName(u"mainWidget")
        self.horizontalLayout_6 = QHBoxLayout(self.mainWidget)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(-1, -1, -1, 0)
        self.mainSplitter = QSplitter(self.mainWidget)
        self.mainSplitter.setObjectName(u"mainSplitter")
        self.mainSplitter.setOrientation(Qt.Horizontal)
        self.mainSplitter.setChildrenCollapsible(False)
        self.imageWidget = QWidget(self.mainSplitter)
        self.imageWidget.setObjectName(u"imageWidget")
        self.verticalLayout_3 = QVBoxLayout(self.imageWidget)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.mainHeaderWidget = QWidget(self.imageWidget)
        self.mainHeaderWidget.setObjectName(u"mainHeaderWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainHeaderWidget.sizePolicy().hasHeightForWidth())
        self.mainHeaderWidget.setSizePolicy(sizePolicy)
        self.mainHeaderWidget.setMinimumSize(QSize(0, 50))
        self.mainHeaderWidget.setMaximumSize(QSize(16777215, 50))
        self.horizontalLayout_5 = QHBoxLayout(self.mainHeaderWidget)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 5, 0, 5)
        self.fileNameLabel = QLabel(self.mainHeaderWidget)
        self.fileNameLabel.setObjectName(u"fileNameLabel")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.fileNameLabel.sizePolicy().hasHeightForWidth())
        self.fileNameLabel.setSizePolicy(sizePolicy1)
        self.fileNameLabel.setMinimumSize(QSize(10, 0))
        font = QFont()
        font.setPointSize(16)
        self.fileNameLabel.setFont(font)
        self.fileNameLabel.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByKeyboard|Qt.TextSelectableByMouse)

        self.horizontalLayout_5.addWidget(self.fileNameLabel)

        self.indexLabel = QLabel(self.mainHeaderWidget)
        self.indexLabel.setObjectName(u"indexLabel")
        sizePolicy1.setHeightForWidth(self.indexLabel.sizePolicy().hasHeightForWidth())
        self.indexLabel.setSizePolicy(sizePolicy1)
        self.indexLabel.setFont(font)
        self.indexLabel.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.indexLabel)

        self.helpButton = QToolButton(self.mainHeaderWidget)
        self.helpButton.setObjectName(u"helpButton")
        self.helpButton.setMinimumSize(QSize(30, 30))
        self.helpButton.setMaximumSize(QSize(30, 30))
        font1 = QFont()
        font1.setPointSize(16)
        font1.setBold(True)
        self.helpButton.setFont(font1)
        self.helpButton.setStyleSheet(u"QToolButton {\n"
"    background-color: #2196F3;\n"
"    color: white;\n"
"    border: 2px solid #1976D2;\n"
"    border-radius: 15px;\n"
"    font-weight: bold;\n"
"}\n"
"QToolButton:hover {\n"
"    background-color: #1976D2;\n"
"}\n"
"QToolButton:pressed {\n"
"    background-color: #0D47A1;\n"
"}")
        self.helpButton.setIconSize(QSize(25, 25))

        self.horizontalLayout_5.addWidget(self.helpButton)

        self.line_3 = QFrame(self.mainHeaderWidget)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.VLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_5.addWidget(self.line_3)

        self.showOverlayCheckBox = QCheckBox(self.mainHeaderWidget)
        self.showOverlayCheckBox.setObjectName(u"showOverlayCheckBox")

        self.horizontalLayout_5.addWidget(self.showOverlayCheckBox)

        self.horizontalSpacer_3 = QSpacerItem(224, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_3)

        self.showPOIsButton = QToolButton(self.mainHeaderWidget)
        self.showPOIsButton.setObjectName(u"showPOIsButton")
        self.showPOIsButton.setIconSize(QSize(25, 25))
        self.showPOIsButton.setCheckable(True)
        self.showPOIsButton.setChecked(False)

        self.horizontalLayout_5.addWidget(self.showPOIsButton)

        self.showAOIsButton = QToolButton(self.mainHeaderWidget)
        self.showAOIsButton.setObjectName(u"showAOIsButton")
        self.showAOIsButton.setIconSize(QSize(25, 25))
        self.showAOIsButton.setCheckable(True)
        self.showAOIsButton.setChecked(True)

        self.horizontalLayout_5.addWidget(self.showAOIsButton)

        self.line_7 = QFrame(self.mainHeaderWidget)
        self.line_7.setObjectName(u"line_7")
        self.line_7.setFrameShape(QFrame.Shape.VLine)
        self.line_7.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_5.addWidget(self.line_7)

        self.GPSMapButton = QToolButton(self.mainHeaderWidget)
        self.GPSMapButton.setObjectName(u"GPSMapButton")
        self.GPSMapButton.setIconSize(QSize(25, 25))

        self.horizontalLayout_5.addWidget(self.GPSMapButton)

        self.rotateImageButton = QToolButton(self.mainHeaderWidget)
        self.rotateImageButton.setObjectName(u"rotateImageButton")
        self.rotateImageButton.setIconSize(QSize(25, 25))

        self.horizontalLayout_5.addWidget(self.rotateImageButton)

        self.adjustmentsButton = QToolButton(self.mainHeaderWidget)
        self.adjustmentsButton.setObjectName(u"adjustmentsButton")
        icon1 = QIcon()
        icon1.addFile(u":/icons/dark/adjustments.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.adjustmentsButton.setIcon(icon1)
        self.adjustmentsButton.setIconSize(QSize(25, 25))

        self.horizontalLayout_5.addWidget(self.adjustmentsButton)

        self.measureButton = QToolButton(self.mainHeaderWidget)
        self.measureButton.setObjectName(u"measureButton")
        font2 = QFont()
        font2.setPointSize(10)
        self.measureButton.setFont(font2)
        icon2 = QIcon()
        icon2.addFile(u":/icons/ruler.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.measureButton.setIcon(icon2)
        self.measureButton.setIconSize(QSize(25, 25))

        self.horizontalLayout_5.addWidget(self.measureButton)

        self.magnifyButton = QToolButton(self.mainHeaderWidget)
        self.magnifyButton.setObjectName(u"magnifyButton")
        self.magnifyButton.setStyleSheet(u"QToolButton {\n"
"    border: 1px solid transparent;\n"
"    border-radius: 4px;\n"
"    padding: 2px;\n"
"}\n"
"QToolButton:hover {\n"
"    border: 1px solid #888;\n"
"    background-color: rgba(136, 136, 136, 0.1);\n"
"}\n"
"QToolButton:pressed {\n"
"    background-color: rgba(136, 136, 136, 0.2);\n"
"}")
        icon3 = QIcon()
        icon3.addFile(u":/icons/dark/icons/dark_theme/magnify.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.magnifyButton.setIcon(icon3)
        self.magnifyButton.setIconSize(QSize(25, 25))

        self.horizontalLayout_5.addWidget(self.magnifyButton)

        self.line_4 = QFrame(self.mainHeaderWidget)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.Shape.VLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_5.addWidget(self.line_4)

        self.kmlButton = QToolButton(self.mainHeaderWidget)
        self.kmlButton.setObjectName(u"kmlButton")
        self.kmlButton.setStyleSheet(u"QToolButton {\n"
"    border: 1px solid transparent;\n"
"    border-radius: 4px;\n"
"    padding: 2px;\n"
"}\n"
"QToolButton:hover {\n"
"    border: 1px solid #888;\n"
"    background-color: rgba(136, 136, 136, 0.1);\n"
"}\n"
"QToolButton:pressed {\n"
"    background-color: rgba(136, 136, 136, 0.2);\n"
"}")
        icon4 = QIcon()
        icon4.addFile(u":/icons/map.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.kmlButton.setIcon(icon4)
        self.kmlButton.setIconSize(QSize(25, 25))

        self.horizontalLayout_5.addWidget(self.kmlButton)

        self.pdfButton = QToolButton(self.mainHeaderWidget)
        self.pdfButton.setObjectName(u"pdfButton")
        self.pdfButton.setStyleSheet(u"QToolButton {\n"
"    border: 1px solid transparent;\n"
"    border-radius: 4px;\n"
"    padding: 2px;\n"
"}\n"
"QToolButton:hover {\n"
"    border: 1px solid #888;\n"
"    background-color: rgba(136, 136, 136, 0.1);\n"
"}\n"
"QToolButton:pressed {\n"
"    background-color: rgba(136, 136, 136, 0.2);\n"
"}")
        icon5 = QIcon()
        icon5.addFile(u":/icons/pdf.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pdfButton.setIcon(icon5)
        self.pdfButton.setIconSize(QSize(25, 25))

        self.horizontalLayout_5.addWidget(self.pdfButton)

        self.zipButton = QToolButton(self.mainHeaderWidget)
        self.zipButton.setObjectName(u"zipButton")
        self.zipButton.setFont(font2)
        self.zipButton.setStyleSheet(u"QToolButton {\n"
"    border: 1px solid transparent;\n"
"    border-radius: 4px;\n"
"    padding: 2px;\n"
"}\n"
"QToolButton:hover {\n"
"    border: 1px solid #888;\n"
"    background-color: rgba(136, 136, 136, 0.1);\n"
"}\n"
"QToolButton:pressed {\n"
"    background-color: rgba(136, 136, 136, 0.2);\n"
"}")
        icon6 = QIcon()
        icon6.addFile(u":/icons/zip.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.zipButton.setIcon(icon6)
        self.zipButton.setIconSize(QSize(25, 25))

        self.horizontalLayout_5.addWidget(self.zipButton)

        self.line = QFrame(self.mainHeaderWidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_5.addWidget(self.line)

        self.skipHidden = QCheckBox(self.mainHeaderWidget)
        self.skipHidden.setObjectName(u"skipHidden")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.skipHidden.sizePolicy().hasHeightForWidth())
        self.skipHidden.setSizePolicy(sizePolicy2)
        font3 = QFont()
        font3.setPointSize(14)
        self.skipHidden.setFont(font3)

        self.horizontalLayout_5.addWidget(self.skipHidden)


        self.verticalLayout_3.addWidget(self.mainHeaderWidget)

        self.placeholderImage = QGraphicsView(self.imageWidget)
        self.placeholderImage.setObjectName(u"placeholderImage")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.placeholderImage.sizePolicy().hasHeightForWidth())
        self.placeholderImage.setSizePolicy(sizePolicy3)
        self.placeholderImage.setMinimumSize(QSize(0, 0))
        font4 = QFont()
        font4.setPointSize(9)
        self.placeholderImage.setFont(font4)

        self.verticalLayout_3.addWidget(self.placeholderImage)

        self.ButtonLayout = QHBoxLayout()
        self.ButtonLayout.setSpacing(8)
        self.ButtonLayout.setObjectName(u"ButtonLayout")
        self.ButtonLayout.setContentsMargins(-1, -1, 10, -1)
        self.hideImageCheckbox = QCheckBox(self.imageWidget)
        self.hideImageCheckbox.setObjectName(u"hideImageCheckbox")

        self.ButtonLayout.addWidget(self.hideImageCheckbox)

        self.hideImageLabel = QLabel(self.imageWidget)
        self.hideImageLabel.setObjectName(u"hideImageLabel")
        self.hideImageLabel.setFont(font2)
        self.hideImageLabel.setFrameShadow(QFrame.Plain)
        self.hideImageLabel.setMargin(0)

        self.ButtonLayout.addWidget(self.hideImageLabel)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.ButtonLayout.addItem(self.horizontalSpacer_2)

        self.jumpToLabel = QLabel(self.imageWidget)
        self.jumpToLabel.setObjectName(u"jumpToLabel")
        self.jumpToLabel.setFont(font2)

        self.ButtonLayout.addWidget(self.jumpToLabel)

        self.jumpToLine = QLineEdit(self.imageWidget)
        self.jumpToLine.setObjectName(u"jumpToLine")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.jumpToLine.sizePolicy().hasHeightForWidth())
        self.jumpToLine.setSizePolicy(sizePolicy4)
        self.jumpToLine.setMinimumSize(QSize(50, 0))
        self.jumpToLine.setMaximumSize(QSize(50, 16777215))

        self.ButtonLayout.addWidget(self.jumpToLine)

        self.previousImageButton = QPushButton(self.imageWidget)
        self.previousImageButton.setObjectName(u"previousImageButton")
        self.previousImageButton.setFont(font2)
        icon7 = QIcon()
        icon7.addFile(u":/icons/previous.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.previousImageButton.setIcon(icon7)

        self.ButtonLayout.addWidget(self.previousImageButton)

        self.nextImageButton = QPushButton(self.imageWidget)
        self.nextImageButton.setObjectName(u"nextImageButton")
        self.nextImageButton.setFont(font2)
        self.nextImageButton.setLayoutDirection(Qt.RightToLeft)
        icon8 = QIcon()
        icon8.addFile(u":/icons/next.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.nextImageButton.setIcon(icon8)

        self.ButtonLayout.addWidget(self.nextImageButton)


        self.verticalLayout_3.addLayout(self.ButtonLayout)

        self.thumbnailScrollArea = QScrollArea(self.imageWidget)
        self.thumbnailScrollArea.setObjectName(u"thumbnailScrollArea")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.thumbnailScrollArea.sizePolicy().hasHeightForWidth())
        self.thumbnailScrollArea.setSizePolicy(sizePolicy5)
        self.thumbnailScrollArea.setMinimumSize(QSize(0, 116))
        self.thumbnailScrollArea.setMaximumSize(QSize(16777215, 116))
        self.thumbnailScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.thumbnailScrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1222, 96))
        sizePolicy.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.scrollAreaWidgetContents.setMinimumSize(QSize(0, 96))
        self.scrollAreaWidgetContents.setMaximumSize(QSize(16777215, 96))
        self.thumbnailLayout = QHBoxLayout(self.scrollAreaWidgetContents)
        self.thumbnailLayout.setObjectName(u"thumbnailLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")

        self.thumbnailLayout.addLayout(self.horizontalLayout)

        self.thumbnailScrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_3.addWidget(self.thumbnailScrollArea)

        self.mainSplitter.addWidget(self.imageWidget)
        self.aoiWidget = QWidget(self.mainSplitter)
        self.aoiWidget.setObjectName(u"aoiWidget")
        self.verticalLayout_4 = QVBoxLayout(self.aoiWidget)
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.aoiHeaderWidget = QWidget(self.aoiWidget)
        self.aoiHeaderWidget.setObjectName(u"aoiHeaderWidget")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.aoiHeaderWidget.sizePolicy().hasHeightForWidth())
        self.aoiHeaderWidget.setSizePolicy(sizePolicy6)
        self.aoiHeaderWidget.setMinimumSize(QSize(250, 50))
        self.aoiHeaderWidget.setMaximumSize(QSize(294, 50))
        self.horizontalLayout_3 = QHBoxLayout(self.aoiHeaderWidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 5, 0, 5)
        self.aoiHeaderLeftSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.aoiHeaderLeftSpacer)

        self.areaCountLabel = QLabel(self.aoiHeaderWidget)
        self.areaCountLabel.setObjectName(u"areaCountLabel")
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.areaCountLabel.sizePolicy().hasHeightForWidth())
        self.areaCountLabel.setSizePolicy(sizePolicy7)
        self.areaCountLabel.setFont(font)
        self.areaCountLabel.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_3.addWidget(self.areaCountLabel)

        self.filterButton = QToolButton(self.aoiHeaderWidget)
        self.filterButton.setObjectName(u"filterButton")
        self.filterButton.setStyleSheet(u"QToolButton {\n"
"    border: 1px solid transparent;\n"
"    border-radius: 4px;\n"
"    padding: 2px;\n"
"}\n"
"QToolButton:hover {\n"
"    border: 1px solid #888;\n"
"    background-color: rgba(136, 136, 136, 0.1);\n"
"}\n"
"QToolButton:pressed {\n"
"    background-color: rgba(136, 136, 136, 0.2);\n"
"}")
        self.filterButton.setIconSize(QSize(25, 25))

        self.horizontalLayout_3.addWidget(self.filterButton)

        self.aoiHeaderRightSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.aoiHeaderRightSpacer)


        self.verticalLayout_4.addWidget(self.aoiHeaderWidget)

        self.aoiFrame = QFrame(self.aoiWidget)
        self.aoiFrame.setObjectName(u"aoiFrame")
        self.aoiFrame.setFrameShape(QFrame.StyledPanel)
        self.aoiFrame.setFrameShadow(QFrame.Sunken)
        self.verticalLayout_2 = QVBoxLayout(self.aoiFrame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.aoiSortLabel = QLabel(self.aoiFrame)
        self.aoiSortLabel.setObjectName(u"aoiSortLabel")
        self.aoiSortLabel.setFont(font2)

        self.verticalLayout_2.addWidget(self.aoiSortLabel)

        self.aoiSortComboBox = QComboBox(self.aoiFrame)
        self.aoiSortComboBox.setObjectName(u"aoiSortComboBox")
        self.aoiSortComboBox.setFont(font2)

        self.verticalLayout_2.addWidget(self.aoiSortComboBox)

        self.aoiListWidget = QListWidget(self.aoiFrame)
        self.aoiListWidget.setObjectName(u"aoiListWidget")
        sizePolicy8 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(self.aoiListWidget.sizePolicy().hasHeightForWidth())
        self.aoiListWidget.setSizePolicy(sizePolicy8)
        self.aoiListWidget.setMinimumSize(QSize(250, 0))
        self.aoiListWidget.setFrameShape(QFrame.NoFrame)

        self.verticalLayout_2.addWidget(self.aoiListWidget)


        self.verticalLayout_4.addWidget(self.aoiFrame)

        self.mainSplitter.addWidget(self.aoiWidget)

        self.horizontalLayout_6.addWidget(self.mainSplitter)


        self.verticalLayout.addWidget(self.mainWidget)

        self.statusBarWidget = QWidget(self.outerWidget)
        self.statusBarWidget.setObjectName(u"statusBarWidget")
        self.statusBarWidget.setMaximumSize(QSize(16777215, 40))
        self.horizontalLayout_4 = QHBoxLayout(self.statusBarWidget)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.statusBar = QLabel(self.statusBarWidget)
        self.statusBar.setObjectName(u"statusBar")
        sizePolicy9 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy9.setHorizontalStretch(0)
        sizePolicy9.setVerticalStretch(0)
        sizePolicy9.setHeightForWidth(self.statusBar.sizePolicy().hasHeightForWidth())
        self.statusBar.setSizePolicy(sizePolicy9)
        self.statusBar.setFont(font2)

        self.horizontalLayout_4.addWidget(self.statusBar)


        self.verticalLayout.addWidget(self.statusBarWidget)

        Viewer.setCentralWidget(self.outerWidget)

        self.retranslateUi(Viewer)

        QMetaObject.connectSlotsByName(Viewer)
    # setupUi

    def retranslateUi(self, Viewer):
        Viewer.setWindowTitle(QCoreApplication.translate("Viewer", u"Automated Drone Image Analysis Tool :: Viewer - Sponsored by TEXSAR", None))
        self.actionOpen.setText(QCoreApplication.translate("Viewer", u"Open", None))
        self.fileNameLabel.setText(QCoreApplication.translate("Viewer", u"TextLabel", None))
        self.indexLabel.setText(QCoreApplication.translate("Viewer", u"TextLabel", None))
#if QT_CONFIG(tooltip)
        self.helpButton.setToolTip(QCoreApplication.translate("Viewer", u"View keyboard shortcuts and help", None))
#endif // QT_CONFIG(tooltip)
        self.helpButton.setText("")
#if QT_CONFIG(tooltip)
        self.showOverlayCheckBox.setToolTip(QCoreApplication.translate("Viewer", u"Toggle the detection overlay on the image.\n"
"When enabled, shows processed image with detected objects highlighted.\n"
"When disabled, shows the original unprocessed image.\n"
"Use to compare original image with detection results.", None))
#endif // QT_CONFIG(tooltip)
        self.showOverlayCheckBox.setText(QCoreApplication.translate("Viewer", u"Show Overlay", None))
#if QT_CONFIG(tooltip)
        self.showPOIsButton.setToolTip(QCoreApplication.translate("Viewer", u"Highlight Pixels of Interest(H)", None))
#endif // QT_CONFIG(tooltip)
        self.showPOIsButton.setText("")
#if QT_CONFIG(tooltip)
        self.showAOIsButton.setToolTip(QCoreApplication.translate("Viewer", u"Show AOIs", None))
#endif // QT_CONFIG(tooltip)
        self.showAOIsButton.setText("")
#if QT_CONFIG(tooltip)
        self.GPSMapButton.setToolTip(QCoreApplication.translate("Viewer", u"Map with Image Locations (M)", None))
#endif // QT_CONFIG(tooltip)
        self.GPSMapButton.setText("")
#if QT_CONFIG(tooltip)
        self.rotateImageButton.setToolTip(QCoreApplication.translate("Viewer", u"North-Oriented View of Image (R)", None))
#endif // QT_CONFIG(tooltip)
        self.rotateImageButton.setText("")
#if QT_CONFIG(tooltip)
        self.adjustmentsButton.setToolTip(QCoreApplication.translate("Viewer", u"Adjust Image (Ctrl+H)", None))
#endif // QT_CONFIG(tooltip)
        self.adjustmentsButton.setText(QCoreApplication.translate("Viewer", u"...", None))
        self.adjustmentsButton.setProperty(u"iconName", QCoreApplication.translate("Viewer", u"adjustments.png", None))
#if QT_CONFIG(tooltip)
        self.measureButton.setToolTip(QCoreApplication.translate("Viewer", u"Measure Distance (Ctrl+M)", None))
#endif // QT_CONFIG(tooltip)
        self.measureButton.setText(QCoreApplication.translate("Viewer", u"...", None))
        self.measureButton.setProperty(u"iconName", QCoreApplication.translate("Viewer", u"ruler.png", None))
#if QT_CONFIG(tooltip)
        self.magnifyButton.setToolTip(QCoreApplication.translate("Viewer", u"Toggle Magnifying Glass (Middle Mouse)", None))
#endif // QT_CONFIG(tooltip)
        self.magnifyButton.setText(QCoreApplication.translate("Viewer", u"...", None))
        self.magnifyButton.setProperty(u"iconName", QCoreApplication.translate("Viewer", u"magnify.png", None))
#if QT_CONFIG(tooltip)
        self.kmlButton.setToolTip(QCoreApplication.translate("Viewer", u"Map Export (KML / CalTopo)", None))
#endif // QT_CONFIG(tooltip)
        self.kmlButton.setText(QCoreApplication.translate("Viewer", u"...", None))
        self.kmlButton.setProperty(u"iconName", QCoreApplication.translate("Viewer", u"map.png", None))
#if QT_CONFIG(tooltip)
        self.pdfButton.setToolTip(QCoreApplication.translate("Viewer", u"Generate PDF Report", None))
#endif // QT_CONFIG(tooltip)
        self.pdfButton.setText(QCoreApplication.translate("Viewer", u"...", None))
        self.pdfButton.setProperty(u"iconName", QCoreApplication.translate("Viewer", u"pdf.png", None))
#if QT_CONFIG(tooltip)
        self.zipButton.setToolTip(QCoreApplication.translate("Viewer", u"Generate Zip Bundle", None))
#endif // QT_CONFIG(tooltip)
        self.zipButton.setText(QCoreApplication.translate("Viewer", u"...", None))
        self.zipButton.setProperty(u"iconName", QCoreApplication.translate("Viewer", u"zip.png", None))
#if QT_CONFIG(tooltip)
        self.skipHidden.setToolTip(QCoreApplication.translate("Viewer", u"Skip hidden images when navigating.\n"
"When enabled, Previous/Next buttons will skip over images marked as hidden.\n"
"Use to focus on images that haven't been reviewed or marked for exclusion.\n"
"Keyboard shortcut: H to hide/unhide current image", None))
#endif // QT_CONFIG(tooltip)
        self.skipHidden.setText(QCoreApplication.translate("Viewer", u"Skip Hidden", None))
#if QT_CONFIG(tooltip)
        self.hideImageCheckbox.setToolTip(QCoreApplication.translate("Viewer", u"Mark current image as hidden.\n"
"Hidden images can be excluded from reports, exports, and navigation.\n"
"Use to remove images with false positives or no relevant detections.\n"
"When \"Skip Hidden\" is enabled, hidden images are skipped during navigation.\n"
"Keyboard shortcut: H", None))
#endif // QT_CONFIG(tooltip)
        self.hideImageCheckbox.setText(QCoreApplication.translate("Viewer", u"Hide Image", None))
#if QT_CONFIG(tooltip)
        self.hideImageLabel.setToolTip(QCoreApplication.translate("Viewer", u"Displays the name of the currently hidden image.\n"
"When an image is marked as hidden, its filename appears here.\n"
"Hidden images are excluded from navigation when \"Skip Hidden\" is enabled.", None))
#endif // QT_CONFIG(tooltip)
        self.hideImageLabel.setText(QCoreApplication.translate("Viewer", u"Hide Image", None))
#if QT_CONFIG(tooltip)
        self.jumpToLabel.setToolTip(QCoreApplication.translate("Viewer", u"Jump directly to a specific image number.\n"
"Enter an image number and press Enter to navigate instantly.\n"
"Useful for reviewing specific images or returning to a noted location.", None))
#endif // QT_CONFIG(tooltip)
        self.jumpToLabel.setText(QCoreApplication.translate("Viewer", u"Jump To:", None))
#if QT_CONFIG(tooltip)
        self.jumpToLine.setToolTip(QCoreApplication.translate("Viewer", u"Enter an image number (1 to total) and press Enter.\n"
"Quickly navigate to any image in the analysis results.\n"
"Example: Type \"25\" and press Enter to jump to image #25", None))
#endif // QT_CONFIG(tooltip)
        self.previousImageButton.setText(QCoreApplication.translate("Viewer", u"Previous Image", None))
        self.previousImageButton.setProperty(u"iconName", QCoreApplication.translate("Viewer", u"previous.png", None))
        self.nextImageButton.setText(QCoreApplication.translate("Viewer", u"Next Image", None))
        self.nextImageButton.setProperty(u"iconName", QCoreApplication.translate("Viewer", u"next.png", None))
        self.areaCountLabel.setText(QCoreApplication.translate("Viewer", u"TextLabel", None))
#if QT_CONFIG(tooltip)
        self.filterButton.setToolTip(QCoreApplication.translate("Viewer", u"Filter AOIs by color and pixel area", None))
#endif // QT_CONFIG(tooltip)
        self.filterButton.setText("")
        self.aoiSortLabel.setText(QCoreApplication.translate("Viewer", u"Sort By", None))
#if QT_CONFIG(tooltip)
        self.aoiSortComboBox.setToolTip(QCoreApplication.translate("Viewer", u"Sort Areas of Interest (AOIs) in the list.\n"
"Choose how to order the detected objects:\n"
"\u2022 Pixel Area: Sort by size (largest to smallest)\n"
"\u2022 Distance: Sort by distance from image center or reference point\n"
"\u2022 Color: Group by similar colors\n"
"\u2022 Detection Order: Original order from analysis\n"
"Sorting helps prioritize review of larger or closer objects.", None))
#endif // QT_CONFIG(tooltip)
        self.aoiSortComboBox.setCurrentText("")
        self.statusBar.setText(QCoreApplication.translate("Viewer", u"TextLabel", None))
    # retranslateUi

