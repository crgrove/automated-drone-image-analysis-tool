# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'VideoParser.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QDoubleSpinBox, QFrame,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QPlainTextEdit, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)
from . import resources_rc

class Ui_VideoParser(object):
    def setupUi(self, VideoParser):
        if not VideoParser.objectName():
            VideoParser.setObjectName(u"VideoParser")
        VideoParser.resize(732, 490)
        self.verticalLayout_2 = QVBoxLayout(VideoParser)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.setupFrame = QFrame(VideoParser)
        self.setupFrame.setObjectName(u"setupFrame")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.setupFrame.sizePolicy().hasHeightForWidth())
        self.setupFrame.setSizePolicy(sizePolicy)
        self.setupFrame.setFrameShape(QFrame.StyledPanel)
        self.setupFrame.setFrameShadow(QFrame.Plain)
        self.setupFrame.setLineWidth(3)
        self.verticalLayout_3 = QVBoxLayout(self.setupFrame)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.selectorsGrid = QGridLayout()
        self.selectorsGrid.setObjectName(u"selectorsGrid")
        self.videoSelectLine = QLineEdit(self.setupFrame)
        self.videoSelectLine.setObjectName(u"videoSelectLine")
        font = QFont()
        font.setPointSize(9)
        self.videoSelectLine.setFont(font)
        self.videoSelectLine.setReadOnly(True)

        self.selectorsGrid.addWidget(self.videoSelectLine, 0, 1, 1, 1)

        self.srtSelectLabel = QLabel(self.setupFrame)
        self.srtSelectLabel.setObjectName(u"srtSelectLabel")
        font1 = QFont()
        font1.setPointSize(10)
        self.srtSelectLabel.setFont(font1)

        self.selectorsGrid.addWidget(self.srtSelectLabel, 1, 0, 1, 1)

        self.outputLabel = QLabel(self.setupFrame)
        self.outputLabel.setObjectName(u"outputLabel")
        self.outputLabel.setFont(font1)

        self.selectorsGrid.addWidget(self.outputLabel, 2, 0, 1, 1)

        self.outputLine = QLineEdit(self.setupFrame)
        self.outputLine.setObjectName(u"outputLine")
        self.outputLine.setFont(font1)
        self.outputLine.setReadOnly(True)

        self.selectorsGrid.addWidget(self.outputLine, 2, 1, 1, 1)

        self.outputSelectButton = QPushButton(self.setupFrame)
        self.outputSelectButton.setObjectName(u"outputSelectButton")
        self.outputSelectButton.setFont(font1)
        icon = QIcon()
        icon.addFile(u":/icons/folder.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.outputSelectButton.setIcon(icon)
        self.outputSelectButton.setAutoDefault(False)

        self.selectorsGrid.addWidget(self.outputSelectButton, 2, 2, 1, 1)

        self.videoSelectLabel = QLabel(self.setupFrame)
        self.videoSelectLabel.setObjectName(u"videoSelectLabel")
        self.videoSelectLabel.setFont(font1)

        self.selectorsGrid.addWidget(self.videoSelectLabel, 0, 0, 1, 1)

        self.videoSelectButton = QPushButton(self.setupFrame)
        self.videoSelectButton.setObjectName(u"videoSelectButton")
        self.videoSelectButton.setFont(font1)
        self.videoSelectButton.setAutoDefault(False)

        self.selectorsGrid.addWidget(self.videoSelectButton, 0, 2, 1, 1)

        self.srtSelectLine = QLineEdit(self.setupFrame)
        self.srtSelectLine.setObjectName(u"srtSelectLine")
        self.srtSelectLine.setFont(font1)
        self.srtSelectLine.setReadOnly(True)

        self.selectorsGrid.addWidget(self.srtSelectLine, 1, 1, 1, 1)

        self.srtSelectButton = QPushButton(self.setupFrame)
        self.srtSelectButton.setObjectName(u"srtSelectButton")
        self.srtSelectButton.setFont(font1)
        self.srtSelectButton.setAutoDefault(False)

        self.selectorsGrid.addWidget(self.srtSelectButton, 1, 2, 1, 1)


        self.verticalLayout_3.addLayout(self.selectorsGrid)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.timeLabel = QLabel(self.setupFrame)
        self.timeLabel.setObjectName(u"timeLabel")
        self.timeLabel.setFont(font1)

        self.horizontalLayout.addWidget(self.timeLabel)

        self.timespinBox = QDoubleSpinBox(self.setupFrame)
        self.timespinBox.setObjectName(u"timespinBox")
        self.timespinBox.setFont(font1)
        self.timespinBox.setDecimals(1)
        self.timespinBox.setMinimum(0.100000000000000)
        self.timespinBox.setSingleStep(0.500000000000000)
        self.timespinBox.setValue(5.000000000000000)

        self.horizontalLayout.addWidget(self.timespinBox)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_3.addLayout(self.horizontalLayout)


        self.verticalLayout_2.addWidget(self.setupFrame)

        self.mainButtons = QHBoxLayout()
        self.mainButtons.setObjectName(u"mainButtons")
        self.startButton = QPushButton(VideoParser)
        self.startButton.setObjectName(u"startButton")
        self.startButton.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.startButton.sizePolicy().hasHeightForWidth())
        self.startButton.setSizePolicy(sizePolicy1)
        self.startButton.setMinimumSize(QSize(150, 0))
        font2 = QFont()
        font2.setPointSize(10)
        font2.setBold(True)
        self.startButton.setFont(font2)
        self.startButton.setLayoutDirection(Qt.LeftToRight)
        self.startButton.setAutoFillBackground(False)
        self.startButton.setStyleSheet(u"background-color: rgb(0, 136, 0);\n"
"color: rgb(228, 231, 235);")

        self.mainButtons.addWidget(self.startButton)

        self.cancelButton = QPushButton(VideoParser)
        self.cancelButton.setObjectName(u"cancelButton")
        self.cancelButton.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.cancelButton.sizePolicy().hasHeightForWidth())
        self.cancelButton.setSizePolicy(sizePolicy1)
        self.cancelButton.setMinimumSize(QSize(150, 0))
        self.cancelButton.setFont(font2)
        self.cancelButton.setStyleSheet(u"")
        icon1 = QIcon()
        icon1.addFile(u":/icons/cancel.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.cancelButton.setIcon(icon1)

        self.mainButtons.addWidget(self.cancelButton)

        self.buttonsSpacer = QSpacerItem(400, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.mainButtons.addItem(self.buttonsSpacer)


        self.verticalLayout_2.addLayout(self.mainButtons)

        self.outputWindow = QPlainTextEdit(VideoParser)
        self.outputWindow.setObjectName(u"outputWindow")
        font3 = QFont()
        font3.setPointSize(12)
        self.outputWindow.setFont(font3)
        self.outputWindow.setReadOnly(True)

        self.verticalLayout_2.addWidget(self.outputWindow)


        self.retranslateUi(VideoParser)

        self.startButton.setDefault(False)


        QMetaObject.connectSlotsByName(VideoParser)
    # setupUi

    def retranslateUi(self, VideoParser):
        VideoParser.setWindowTitle(QCoreApplication.translate("VideoParser", u"Video Parser", None))
#if QT_CONFIG(tooltip)
        self.videoSelectLine.setToolTip(QCoreApplication.translate("VideoParser", u"Path to the video file to extract frames from.\n"
"Supported formats: MP4, AVI, MOV, MKV, and other common video formats.\n"
"Click the Select button to browse for a video file.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.srtSelectLabel.setToolTip(QCoreApplication.translate("VideoParser", u"SRT subtitle file containing GPS telemetry and timestamp data.\n"
"Optional: Provides location information for extracted frames.\n"
"Without SRT file, frames will have no GPS metadata.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.srtSelectLabel.setWhatsThis(QCoreApplication.translate("VideoParser", u"The SRT file contains timestamped information about the video file.  It is optional, but without it output images won't include location information.", None))
#endif // QT_CONFIG(whatsthis)
        self.srtSelectLabel.setText(QCoreApplication.translate("VideoParser", u"SRT File (optional): ", None))
#if QT_CONFIG(tooltip)
        self.outputLabel.setToolTip(QCoreApplication.translate("VideoParser", u"Destination folder where extracted frame images will be saved.\n"
"Each frame is saved as a separate image file with timestamp information.", None))
#endif // QT_CONFIG(tooltip)
        self.outputLabel.setText(QCoreApplication.translate("VideoParser", u"Output Folder:", None))
#if QT_CONFIG(tooltip)
        self.outputLine.setToolTip(QCoreApplication.translate("VideoParser", u"Path to the output folder for extracted frame images.\n"
"All frames will be saved in this directory with sequential naming.\n"
"Click the Select button to choose a different folder.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.outputSelectButton.setToolTip(QCoreApplication.translate("VideoParser", u"Browse for output folder to save extracted frames.\n"
"Opens a folder selection dialog.", None))
#endif // QT_CONFIG(tooltip)
        self.outputSelectButton.setText(QCoreApplication.translate("VideoParser", u"Select", None))
        self.outputSelectButton.setProperty(u"iconName", QCoreApplication.translate("VideoParser", u"folder.png", None))
#if QT_CONFIG(tooltip)
        self.videoSelectLabel.setToolTip(QCoreApplication.translate("VideoParser", u"Select the source video file to parse.\n"
"Video will be split into individual frame images.", None))
#endif // QT_CONFIG(tooltip)
        self.videoSelectLabel.setText(QCoreApplication.translate("VideoParser", u"Video File:", None))
#if QT_CONFIG(tooltip)
        self.videoSelectButton.setToolTip(QCoreApplication.translate("VideoParser", u"Browse for video file to extract frames from.\n"
"Opens a file selection dialog for video files (MP4, AVI, MOV, etc.).", None))
#endif // QT_CONFIG(tooltip)
        self.videoSelectButton.setText(QCoreApplication.translate("VideoParser", u"Select", None))
#if QT_CONFIG(tooltip)
        self.srtSelectLine.setToolTip(QCoreApplication.translate("VideoParser", u"Path to the optional SRT subtitle file with GPS telemetry data.\n"
"SRT files contain timestamp and location information for video frames.\n"
"If provided, extracted frames will include GPS metadata (latitude, longitude, altitude).\n"
"Can be left empty if location data is not needed.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.srtSelectButton.setToolTip(QCoreApplication.translate("VideoParser", u"Browse for optional SRT subtitle file containing GPS telemetry.\n"
"SRT files are commonly created by DJI drones and other video recording devices.\n"
"Opens a file selection dialog for SRT files.", None))
#endif // QT_CONFIG(tooltip)
        self.srtSelectButton.setText(QCoreApplication.translate("VideoParser", u"Select", None))
#if QT_CONFIG(tooltip)
        self.timeLabel.setToolTip(QCoreApplication.translate("VideoParser", u"Time interval between extracted frames.\n"
"Determines how frequently frames are captured from the video.\n"
"Smaller intervals = More frames extracted (larger output)", None))
#endif // QT_CONFIG(tooltip)
        self.timeLabel.setText(QCoreApplication.translate("VideoParser", u"Time Interval (seconds):", None))
#if QT_CONFIG(tooltip)
        self.timespinBox.setToolTip(QCoreApplication.translate("VideoParser", u"Set the time interval in seconds between frame extractions.\n"
"\u2022 Range: 0.1 to unlimited seconds\n"
"\u2022 Default: 5.0 seconds (extracts 1 frame every 5 seconds)\n"
"\u2022 Lower values: More frames extracted (e.g., 0.5s = 2 frames per second)\n"
"\u2022 Higher values: Fewer frames extracted (e.g., 10s = 1 frame every 10 seconds)\n"
"Recommendation: 3-5 seconds for most drone footage analysis", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.startButton.setToolTip(QCoreApplication.translate("VideoParser", u"Start extracting frames from the video file.\n"
"Requirements:\n"
"\u2022 Video file must be selected\n"
"\u2022 Output folder must be selected\n"
"\u2022 Time interval must be set (default: 5 seconds)\n"
"The process will extract frames at the specified interval and save them as images.\n"
"If SRT file is provided, GPS metadata will be embedded in the extracted frames.", None))
#endif // QT_CONFIG(tooltip)
        self.startButton.setText(QCoreApplication.translate("VideoParser", u"Start", None))
#if QT_CONFIG(tooltip)
        self.cancelButton.setToolTip(QCoreApplication.translate("VideoParser", u"Cancel the frame extraction process.\n"
"Stops the operation immediately and returns to the ready state.\n"
"Any frames already extracted will be saved in the output folder.\n"
"Click to abort the current parsing operation.", None))
#endif // QT_CONFIG(tooltip)
        self.cancelButton.setText(QCoreApplication.translate("VideoParser", u" Cancel", None))
        self.cancelButton.setProperty(u"iconName", QCoreApplication.translate("VideoParser", u"cancel.png", None))
#if QT_CONFIG(tooltip)
        self.outputWindow.setToolTip(QCoreApplication.translate("VideoParser", u"Progress and status output window.\n"
"Displays real-time information during frame extraction:\n"
"\u2022 Current frame being processed\n"
"\u2022 Frame timestamps and numbers\n"
"\u2022 GPS coordinates (if SRT file is provided)\n"
"\u2022 Progress percentage and completion status\n"
"\u2022 Any errors or warnings encountered\n"
"Shows total frames extracted when complete.", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

