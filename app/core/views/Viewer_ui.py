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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QGraphicsView,
    QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QToolButton, QVBoxLayout,
    QWidget)
import resources_rc

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
        self.centralwidget = QWidget(Viewer)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, -1, -1, 9)
        self.TitleWidget = QWidget(self.centralwidget)
        self.TitleWidget.setObjectName(u"TitleWidget")
        self.horizontalLayout_2 = QHBoxLayout(self.TitleWidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 9, 0, -1)
        self.fileNameLabel = QLabel(self.TitleWidget)
        self.fileNameLabel.setObjectName(u"fileNameLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileNameLabel.sizePolicy().hasHeightForWidth())
        self.fileNameLabel.setSizePolicy(sizePolicy)
        self.fileNameLabel.setMinimumSize(QSize(10, 0))
        font = QFont()
        font.setPointSize(16)
        self.fileNameLabel.setFont(font)
        self.fileNameLabel.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByKeyboard|Qt.TextSelectableByMouse)

        self.horizontalLayout_2.addWidget(self.fileNameLabel)

        self.line_3 = QFrame(self.TitleWidget)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.VLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_2.addWidget(self.line_3)

        self.showOverlayCheckBox = QCheckBox(self.TitleWidget)
        self.showOverlayCheckBox.setObjectName(u"showOverlayCheckBox")

        self.horizontalLayout_2.addWidget(self.showOverlayCheckBox)

        self.highlightPixelsOfInterestCheckBox = QCheckBox(self.TitleWidget)
        self.highlightPixelsOfInterestCheckBox.setObjectName(u"highlightPixelsOfInterestCheckBox")

        self.horizontalLayout_2.addWidget(self.highlightPixelsOfInterestCheckBox)

        self.showAOIsCheckBox = QCheckBox(self.TitleWidget)
        self.showAOIsCheckBox.setObjectName(u"showAOIsCheckBox")
        font1 = QFont()
        font1.setPointSize(9)
        self.showAOIsCheckBox.setFont(font1)

        self.horizontalLayout_2.addWidget(self.showAOIsCheckBox)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.adjustmentsButton = QToolButton(self.TitleWidget)
        self.adjustmentsButton.setObjectName(u"adjustmentsButton")
        icon1 = QIcon()
        icon1.addFile(u":/icons/dark/adjustments.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.adjustmentsButton.setIcon(icon1)
        self.adjustmentsButton.setIconSize(QSize(25, 25))

        self.horizontalLayout_2.addWidget(self.adjustmentsButton)

        self.measureButton = QToolButton(self.TitleWidget)
        self.measureButton.setObjectName(u"measureButton")
        font2 = QFont()
        font2.setPointSize(10)
        self.measureButton.setFont(font2)
        icon2 = QIcon()
        icon2.addFile(u":/icons/ruler.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.measureButton.setIcon(icon2)
        self.measureButton.setIconSize(QSize(25, 25))

        self.horizontalLayout_2.addWidget(self.measureButton)

        self.magnifyButton = QToolButton(self.TitleWidget)
        self.magnifyButton.setObjectName(u"magnifyButton")
        icon3 = QIcon()
        icon3.addFile(u":/icons/dark/icons/dark_theme/magnify.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.magnifyButton.setIcon(icon3)
        self.magnifyButton.setIconSize(QSize(25, 25))

        self.horizontalLayout_2.addWidget(self.magnifyButton)

        self.line_4 = QFrame(self.TitleWidget)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.Shape.VLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_2.addWidget(self.line_4)

        self.kmlButton = QToolButton(self.TitleWidget)
        self.kmlButton.setObjectName(u"kmlButton")
        icon4 = QIcon()
        icon4.addFile(u":/icons/map.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.kmlButton.setIcon(icon4)
        self.kmlButton.setIconSize(QSize(25, 25))

        self.horizontalLayout_2.addWidget(self.kmlButton)

        self.pdfButton = QToolButton(self.TitleWidget)
        self.pdfButton.setObjectName(u"pdfButton")
        icon5 = QIcon()
        icon5.addFile(u":/icons/pdf.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pdfButton.setIcon(icon5)
        self.pdfButton.setIconSize(QSize(25, 25))

        self.horizontalLayout_2.addWidget(self.pdfButton)

        self.zipButton = QToolButton(self.TitleWidget)
        self.zipButton.setObjectName(u"zipButton")
        self.zipButton.setFont(font2)
        icon6 = QIcon()
        icon6.addFile(u":/icons/zip.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.zipButton.setIcon(icon6)
        self.zipButton.setIconSize(QSize(25, 25))

        self.horizontalLayout_2.addWidget(self.zipButton)

        self.caltopoButton = QToolButton(self.TitleWidget)
        self.caltopoButton.setObjectName(u"caltopoButton")
        icon7 = QIcon()
        icon7.addFile(u":/icons/caltopo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.caltopoButton.setIcon(icon7)
        self.caltopoButton.setIconSize(QSize(25, 25))

        self.horizontalLayout_2.addWidget(self.caltopoButton)

        self.line = QFrame(self.TitleWidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_2.addWidget(self.line)

        self.skipHidden = QCheckBox(self.TitleWidget)
        self.skipHidden.setObjectName(u"skipHidden")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.skipHidden.sizePolicy().hasHeightForWidth())
        self.skipHidden.setSizePolicy(sizePolicy1)
        font3 = QFont()
        font3.setPointSize(14)
        self.skipHidden.setFont(font3)

        self.horizontalLayout_2.addWidget(self.skipHidden)

        self.line_2 = QFrame(self.TitleWidget)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.VLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_2.addWidget(self.line_2)

        self.indexLabel = QLabel(self.TitleWidget)
        self.indexLabel.setObjectName(u"indexLabel")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.indexLabel.sizePolicy().hasHeightForWidth())
        self.indexLabel.setSizePolicy(sizePolicy2)
        self.indexLabel.setFont(font)
        self.indexLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.indexLabel)

        self.areaCountLabel = QLabel(self.TitleWidget)
        self.areaCountLabel.setObjectName(u"areaCountLabel")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.areaCountLabel.sizePolicy().hasHeightForWidth())
        self.areaCountLabel.setSizePolicy(sizePolicy3)
        self.areaCountLabel.setMinimumSize(QSize(250, 0))
        self.areaCountLabel.setMaximumSize(QSize(250, 16777215))
        self.areaCountLabel.setFont(font)
        self.areaCountLabel.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_2.addWidget(self.areaCountLabel)


        self.verticalLayout.addWidget(self.TitleWidget)

        self.ImageLayout = QHBoxLayout()
        self.ImageLayout.setObjectName(u"ImageLayout")
        self.placeholderImage = QGraphicsView(self.centralwidget)
        self.placeholderImage.setObjectName(u"placeholderImage")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.placeholderImage.sizePolicy().hasHeightForWidth())
        self.placeholderImage.setSizePolicy(sizePolicy4)
        self.placeholderImage.setMinimumSize(QSize(0, 0))
        self.placeholderImage.setFont(font1)

        self.ImageLayout.addWidget(self.placeholderImage)

        self.aoiListWidget = QListWidget(self.centralwidget)
        self.aoiListWidget.setObjectName(u"aoiListWidget")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.aoiListWidget.sizePolicy().hasHeightForWidth())
        self.aoiListWidget.setSizePolicy(sizePolicy5)
        self.aoiListWidget.setMinimumSize(QSize(250, 0))

        self.ImageLayout.addWidget(self.aoiListWidget)


        self.verticalLayout.addLayout(self.ImageLayout)

        self.ButtonLayout = QHBoxLayout()
        self.ButtonLayout.setSpacing(8)
        self.ButtonLayout.setObjectName(u"ButtonLayout")
        self.hideImageCheckbox = QCheckBox(self.centralwidget)
        self.hideImageCheckbox.setObjectName(u"hideImageCheckbox")

        self.ButtonLayout.addWidget(self.hideImageCheckbox)

        self.hideImageLabel = QLabel(self.centralwidget)
        self.hideImageLabel.setObjectName(u"hideImageLabel")
        self.hideImageLabel.setFont(font2)
        self.hideImageLabel.setFrameShadow(QFrame.Plain)
        self.hideImageLabel.setMargin(0)

        self.ButtonLayout.addWidget(self.hideImageLabel)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.ButtonLayout.addItem(self.horizontalSpacer_2)

        self.jumpToLabel = QLabel(self.centralwidget)
        self.jumpToLabel.setObjectName(u"jumpToLabel")
        self.jumpToLabel.setFont(font2)

        self.ButtonLayout.addWidget(self.jumpToLabel)

        self.jumpToLine = QLineEdit(self.centralwidget)
        self.jumpToLine.setObjectName(u"jumpToLine")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.jumpToLine.sizePolicy().hasHeightForWidth())
        self.jumpToLine.setSizePolicy(sizePolicy6)
        self.jumpToLine.setMinimumSize(QSize(50, 0))
        self.jumpToLine.setMaximumSize(QSize(50, 16777215))

        self.ButtonLayout.addWidget(self.jumpToLine)

        self.previousImageButton = QPushButton(self.centralwidget)
        self.previousImageButton.setObjectName(u"previousImageButton")
        self.previousImageButton.setFont(font2)
        icon8 = QIcon()
        icon8.addFile(u":/icons/previous.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.previousImageButton.setIcon(icon8)

        self.ButtonLayout.addWidget(self.previousImageButton)

        self.nextImageButton = QPushButton(self.centralwidget)
        self.nextImageButton.setObjectName(u"nextImageButton")
        self.nextImageButton.setFont(font2)
        self.nextImageButton.setLayoutDirection(Qt.RightToLeft)
        icon9 = QIcon()
        icon9.addFile(u":/icons/next.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.nextImageButton.setIcon(icon9)

        self.ButtonLayout.addWidget(self.nextImageButton)

        self.horizontalSpacer = QSpacerItem(260, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.ButtonLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.ButtonLayout)

        self.thumbnailScrollArea = QScrollArea(self.centralwidget)
        self.thumbnailScrollArea.setObjectName(u"thumbnailScrollArea")
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.thumbnailScrollArea.sizePolicy().hasHeightForWidth())
        self.thumbnailScrollArea.setSizePolicy(sizePolicy7)
        self.thumbnailScrollArea.setMinimumSize(QSize(0, 116))
        self.thumbnailScrollArea.setMaximumSize(QSize(16777215, 116))
        self.thumbnailScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.thumbnailScrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1532, 96))
        sizePolicy8 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy8)
        self.scrollAreaWidgetContents.setMinimumSize(QSize(0, 96))
        self.scrollAreaWidgetContents.setMaximumSize(QSize(16777215, 96))
        self.thumbnailLayout = QHBoxLayout(self.scrollAreaWidgetContents)
        self.thumbnailLayout.setObjectName(u"thumbnailLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")

        self.thumbnailLayout.addLayout(self.horizontalLayout)

        self.thumbnailScrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.thumbnailScrollArea)

        self.statusBarWidget = QWidget(self.centralwidget)
        self.statusBarWidget.setObjectName(u"statusBarWidget")
        self.horizontalLayout_4 = QHBoxLayout(self.statusBarWidget)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
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

        Viewer.setCentralWidget(self.centralwidget)

        self.retranslateUi(Viewer)

        QMetaObject.connectSlotsByName(Viewer)
    # setupUi

    def retranslateUi(self, Viewer):
        Viewer.setWindowTitle(QCoreApplication.translate("Viewer", u"Automated Drone Image Analysis Tool :: Viewer - Sponsored by TEXSAR", None))
        self.actionOpen.setText(QCoreApplication.translate("Viewer", u"Open", None))
        self.fileNameLabel.setText(QCoreApplication.translate("Viewer", u"TextLabel", None))
        self.showOverlayCheckBox.setText(QCoreApplication.translate("Viewer", u"Show Overlay", None))
        self.highlightPixelsOfInterestCheckBox.setText(QCoreApplication.translate("Viewer", u"Highlight Pixels of Interest", None))
        self.showAOIsCheckBox.setText(QCoreApplication.translate("Viewer", u"Show AOIs", None))
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
        self.kmlButton.setToolTip(QCoreApplication.translate("Viewer", u"Generate KML", None))
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
        self.caltopoButton.setToolTip(QCoreApplication.translate("Viewer", u"Export to CalTopo", None))
#endif // QT_CONFIG(tooltip)
        self.caltopoButton.setText(QCoreApplication.translate("Viewer", u"...", None))
        self.caltopoButton.setProperty(u"iconName", QCoreApplication.translate("Viewer", u"caltopo.png", None))
        self.skipHidden.setText(QCoreApplication.translate("Viewer", u"Skip Hidden", None))
        self.indexLabel.setText(QCoreApplication.translate("Viewer", u"TextLabel", None))
        self.areaCountLabel.setText(QCoreApplication.translate("Viewer", u"TextLabel", None))
        self.hideImageCheckbox.setText(QCoreApplication.translate("Viewer", u"Hide Image", None))
        self.hideImageLabel.setText(QCoreApplication.translate("Viewer", u"Hide Image", None))
        self.jumpToLabel.setText(QCoreApplication.translate("Viewer", u"Jump To:", None))
        self.previousImageButton.setText(QCoreApplication.translate("Viewer", u"Previous Image", None))
        self.previousImageButton.setProperty(u"iconName", QCoreApplication.translate("Viewer", u"previous.png", None))
        self.nextImageButton.setText(QCoreApplication.translate("Viewer", u"Next Image", None))
        self.nextImageButton.setProperty(u"iconName", QCoreApplication.translate("Viewer", u"next.png", None))
        self.statusBar.setText(QCoreApplication.translate("Viewer", u"TextLabel", None))
    # retranslateUi

