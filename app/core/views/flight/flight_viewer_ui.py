# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'flight_viewer.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
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
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QMenu,
    QMenuBar, QSizePolicy, QStatusBar, QToolBar,
    QVBoxLayout, QWidget)

class Ui_FlightViewerWindow(object):
    def setupUi(self, FlightViewerWindow):
        if not FlightViewerWindow.objectName():
            FlightViewerWindow.setObjectName(u"FlightViewerWindow")
        FlightViewerWindow.resize(1200, 800)
        self.actionAddFeed = QAction(FlightViewerWindow)
        self.actionAddFeed.setObjectName(u"actionAddFeed")
        self.actionToggleGallery = QAction(FlightViewerWindow)
        self.actionToggleGallery.setObjectName(u"actionToggleGallery")
        self.actionToggleGallery.setCheckable(True)
        self.actionToggleGallery.setChecked(True)
        self.actionSaveLayout = QAction(FlightViewerWindow)
        self.actionSaveLayout.setObjectName(u"actionSaveLayout")
        self.actionRestoreLayout = QAction(FlightViewerWindow)
        self.actionRestoreLayout.setObjectName(u"actionRestoreLayout")
        self.actionClose = QAction(FlightViewerWindow)
        self.actionClose.setObjectName(u"actionClose")
        self.actionToggleMap = QAction(FlightViewerWindow)
        self.actionToggleMap.setObjectName(u"actionToggleMap")
        self.actionToggleMap.setCheckable(True)
        self.actionToggleMap.setChecked(False)
        self.actionOpenImageAnalysis = QAction(FlightViewerWindow)
        self.actionOpenImageAnalysis.setObjectName(u"actionOpenImageAnalysis")
        self.actionOpenStreamingDetector = QAction(FlightViewerWindow)
        self.actionOpenStreamingDetector.setObjectName(u"actionOpenStreamingDetector")
        self.actionHelp = QAction(FlightViewerWindow)
        self.actionHelp.setObjectName(u"actionHelp")
        self.centralwidget = QWidget(FlightViewerWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralLayout = QVBoxLayout(self.centralwidget)
        self.centralLayout.setObjectName(u"centralLayout")
        self.placeholderLabel = QLabel(self.centralwidget)
        self.placeholderLabel.setObjectName(u"placeholderLabel")
        self.placeholderLabel.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        self.placeholderLabel.setFont(font)
        self.placeholderLabel.setStyleSheet(u"QLabel { color: palette(mid); }")

        self.centralLayout.addWidget(self.placeholderLabel)

        FlightViewerWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(FlightViewerWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1200, 22))
        self.menuMain = QMenu(self.menubar)
        self.menuMain.setObjectName(u"menuMain")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        FlightViewerWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(FlightViewerWindow)
        self.statusbar.setObjectName(u"statusbar")
        FlightViewerWindow.setStatusBar(self.statusbar)
        self.mainToolBar = QToolBar(FlightViewerWindow)
        self.mainToolBar.setObjectName(u"mainToolBar")
        self.mainToolBar.setMovable(False)
        self.mainToolBar.setFloatable(False)
        FlightViewerWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.mainToolBar)

        self.menubar.addAction(self.menuMain.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuMain.addAction(self.actionAddFeed)
        self.menuMain.addSeparator()
        self.menuMain.addAction(self.actionToggleGallery)
        self.menuMain.addAction(self.actionToggleMap)
        self.menuMain.addSeparator()
        self.menuMain.addAction(self.actionSaveLayout)
        self.menuMain.addAction(self.actionRestoreLayout)
        self.menuMain.addSeparator()
        self.menuMain.addAction(self.actionOpenImageAnalysis)
        self.menuMain.addAction(self.actionOpenStreamingDetector)
        self.menuMain.addSeparator()
        self.menuMain.addAction(self.actionClose)
        self.menuHelp.addAction(self.actionHelp)
        self.mainToolBar.addAction(self.actionAddFeed)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.actionSaveLayout)
        self.mainToolBar.addAction(self.actionRestoreLayout)

        self.retranslateUi(FlightViewerWindow)

        QMetaObject.connectSlotsByName(FlightViewerWindow)
    # setupUi

    def retranslateUi(self, FlightViewerWindow):
        FlightViewerWindow.setWindowTitle(QCoreApplication.translate("FlightViewerWindow", u"ADIAT Flight Viewer", None))
        self.actionAddFeed.setText(QCoreApplication.translate("FlightViewerWindow", u"+ Add Feed", None))
#if QT_CONFIG(tooltip)
        self.actionAddFeed.setToolTip(QCoreApplication.translate("FlightViewerWindow", u"Pair with an ADIAT Mobile drone controller using a 6-character code.", None))
#endif // QT_CONFIG(tooltip)
        self.actionToggleGallery.setText(QCoreApplication.translate("FlightViewerWindow", u"Mission Gallery", None))
#if QT_CONFIG(tooltip)
        self.actionToggleGallery.setToolTip(QCoreApplication.translate("FlightViewerWindow", u"Show or hide the aggregate Mission Gallery panel.", None))
#endif // QT_CONFIG(tooltip)
        self.actionSaveLayout.setText(QCoreApplication.translate("FlightViewerWindow", u"Save Layout", None))
#if QT_CONFIG(tooltip)
        self.actionSaveLayout.setToolTip(QCoreApplication.translate("FlightViewerWindow", u"Save the current dock arrangement for next session.", None))
#endif // QT_CONFIG(tooltip)
        self.actionRestoreLayout.setText(QCoreApplication.translate("FlightViewerWindow", u"Restore Layout", None))
#if QT_CONFIG(tooltip)
        self.actionRestoreLayout.setToolTip(QCoreApplication.translate("FlightViewerWindow", u"Apply the last saved dock arrangement.", None))
#endif // QT_CONFIG(tooltip)
        self.actionClose.setText(QCoreApplication.translate("FlightViewerWindow", u"Close Viewer", None))
        self.actionToggleMap.setText(QCoreApplication.translate("FlightViewerWindow", u"Map", None))
#if QT_CONFIG(tooltip)
        self.actionToggleMap.setToolTip(QCoreApplication.translate("FlightViewerWindow", u"Show or hide the detection map dock.", None))
#endif // QT_CONFIG(tooltip)
        self.actionOpenImageAnalysis.setText(QCoreApplication.translate("FlightViewerWindow", u"Open Image Analysis", None))
#if QT_CONFIG(tooltip)
        self.actionOpenImageAnalysis.setToolTip(QCoreApplication.translate("FlightViewerWindow", u"Switch to the Image Analysis window for post-flight image review.", None))
#endif // QT_CONFIG(tooltip)
        self.actionOpenStreamingDetector.setText(QCoreApplication.translate("FlightViewerWindow", u"Open Streaming Detector", None))
#if QT_CONFIG(tooltip)
        self.actionOpenStreamingDetector.setToolTip(QCoreApplication.translate("FlightViewerWindow", u"Switch to the Streaming Detector window for RTMP / HDMI capture sessions.", None))
#endif // QT_CONFIG(tooltip)
        self.actionHelp.setText(QCoreApplication.translate("FlightViewerWindow", u"ADIAT Help", None))
#if QT_CONFIG(tooltip)
        self.actionHelp.setToolTip(QCoreApplication.translate("FlightViewerWindow", u"Open the ADIAT documentation in your browser.", None))
#endif // QT_CONFIG(tooltip)
        self.placeholderLabel.setText(QCoreApplication.translate("FlightViewerWindow", u"Add a feed to begin.  Use Add Feed in the toolbar.", None))
        self.menuMain.setTitle(QCoreApplication.translate("FlightViewerWindow", u"Menu", None))
        self.menuHelp.setTitle(QCoreApplication.translate("FlightViewerWindow", u"Help", None))
        self.mainToolBar.setWindowTitle(QCoreApplication.translate("FlightViewerWindow", u"Main Toolbar", None))
    # retranslateUi

