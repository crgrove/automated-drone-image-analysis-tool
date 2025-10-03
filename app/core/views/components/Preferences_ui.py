# -*- coding: utf-8 -*-

###############################################################################
# Form generated from reading UI file 'Preferences.ui'
#
# Created by: Qt User Interface Compiler version 6.9.2
#
# WARNING! All changes made in this file will be lost when recompiling UI file!
###############################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
        QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
        QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
        QDialogButtonBox, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_Preferences(object):
    def setupUi(self, Preferences):
        if not Preferences.objectName():
            Preferences.setObjectName(u"Preferences")
        Preferences.resize(431, 403)
        self.verticalLayout = QVBoxLayout(Preferences)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.mainWidget = QWidget(Preferences)
        self.mainWidget.setObjectName(u"mainWidget")
        self.verticalLayout_2 = QVBoxLayout(self.mainWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.themeWidget = QWidget(self.mainWidget)
        self.themeWidget.setObjectName(u"themeWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.themeWidget.sizePolicy().hasHeightForWidth())
        self.themeWidget.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(10)
        self.themeWidget.setFont(font)
        self.horizontalLayout_3 = QHBoxLayout(self.themeWidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label = QLabel(self.themeWidget)
        self.label.setObjectName(u"label")
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setFont(font)

        self.horizontalLayout_3.addWidget(self.label)

        self.themeComboBox = QComboBox(self.themeWidget)
        self.themeComboBox.addItem("")
        self.themeComboBox.addItem("")
        self.themeComboBox.setObjectName(u"themeComboBox")
        self.themeComboBox.setFont(font)

        self.horizontalLayout_3.addWidget(self.themeComboBox)


        self.verticalLayout_2.addWidget(self.themeWidget)

        self.maxAOIsWidget = QWidget(self.mainWidget)
        self.maxAOIsWidget.setObjectName(u"maxAOIsWidget")
        sizePolicy.setHeightForWidth(self.maxAOIsWidget.sizePolicy().hasHeightForWidth())
        self.maxAOIsWidget.setSizePolicy(sizePolicy)
        self.horizontalLayout_2 = QHBoxLayout(self.maxAOIsWidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.maxAOIsLabel = QLabel(self.maxAOIsWidget)
        self.maxAOIsLabel.setObjectName(u"maxAOIsLabel")
        sizePolicy.setHeightForWidth(self.maxAOIsLabel.sizePolicy().hasHeightForWidth())
        self.maxAOIsLabel.setSizePolicy(sizePolicy)
        self.maxAOIsLabel.setFont(font)

        self.horizontalLayout_2.addWidget(self.maxAOIsLabel)

        self.maxAOIsSpinBox = QSpinBox(self.maxAOIsWidget)
        self.maxAOIsSpinBox.setObjectName(u"maxAOIsSpinBox")
        self.maxAOIsSpinBox.setFont(font)
        self.maxAOIsSpinBox.setMaximum(1000)
        self.maxAOIsSpinBox.setValue(100)

        self.horizontalLayout_2.addWidget(self.maxAOIsSpinBox)


        self.verticalLayout_2.addWidget(self.maxAOIsWidget)

        self.radiuisWidget = QWidget(self.mainWidget)
        self.radiuisWidget.setObjectName(u"radiuisWidget")
        self.horizontalLayout = QHBoxLayout(self.radiuisWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.AOIRadiusLabel = QLabel(self.radiuisWidget)
        self.AOIRadiusLabel.setObjectName(u"AOIRadiusLabel")
        self.AOIRadiusLabel.setFont(font)

        self.horizontalLayout.addWidget(self.AOIRadiusLabel)

        self.AOIRadiusSpinBox = QSpinBox(self.radiuisWidget)
        self.AOIRadiusSpinBox.setObjectName(u"AOIRadiusSpinBox")
        self.AOIRadiusSpinBox.setFont(font)
        self.AOIRadiusSpinBox.setMaximum(100)
        self.AOIRadiusSpinBox.setValue(25)

        self.horizontalLayout.addWidget(self.AOIRadiusSpinBox)


        self.verticalLayout_2.addWidget(self.radiuisWidget)

        self.positionFormatWidget = QWidget(self.mainWidget)
        self.positionFormatWidget.setObjectName(u"positionFormatWidget")
        self.horizontalLayout_4 = QHBoxLayout(self.positionFormatWidget)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.positionFormatLabel = QLabel(self.positionFormatWidget)
        self.positionFormatLabel.setObjectName(u"positionFormatLabel")
        self.positionFormatLabel.setFont(font)

        self.horizontalLayout_4.addWidget(self.positionFormatLabel)

        self.positionFormatComboBox = QComboBox(self.positionFormatWidget)
        self.positionFormatComboBox.addItem("")
        self.positionFormatComboBox.addItem("")
        self.positionFormatComboBox.addItem("")
        self.positionFormatComboBox.setObjectName(u"positionFormatComboBox")
        self.positionFormatComboBox.setFont(font)

        self.horizontalLayout_4.addWidget(self.positionFormatComboBox)


        self.verticalLayout_2.addWidget(self.positionFormatWidget)

        self.TemperatureWidget = QWidget(self.mainWidget)
        self.TemperatureWidget.setObjectName(u"TemperatureWidget")
        self.horizontalLayout_5 = QHBoxLayout(self.TemperatureWidget)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.temperatureLabel = QLabel(self.TemperatureWidget)
        self.temperatureLabel.setObjectName(u"temperatureLabel")
        self.temperatureLabel.setFont(font)

        self.horizontalLayout_5.addWidget(self.temperatureLabel)

        self.temperatureComboBox = QComboBox(self.TemperatureWidget)
        self.temperatureComboBox.addItem("")
        self.temperatureComboBox.addItem("")
        self.temperatureComboBox.setObjectName(u"temperatureComboBox")
        self.temperatureComboBox.setFont(font)

        self.horizontalLayout_5.addWidget(self.temperatureComboBox)


        self.verticalLayout_2.addWidget(self.TemperatureWidget)

        self.distanceWidget = QWidget(self.mainWidget)
        self.distanceWidget.setObjectName(u"distanceWidget")
        self.horizontalLayout_7 = QHBoxLayout(self.distanceWidget)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.distanceLabel = QLabel(self.distanceWidget)
        self.distanceLabel.setObjectName(u"distanceLabel")
        self.distanceLabel.setFont(font)

        self.horizontalLayout_7.addWidget(self.distanceLabel)

        self.distanceComboBox = QComboBox(self.distanceWidget)
        self.distanceComboBox.addItem("")
        self.distanceComboBox.addItem("")
        self.distanceComboBox.setObjectName(u"distanceComboBox")
        self.distanceComboBox.setFont(font)

        self.horizontalLayout_7.addWidget(self.distanceComboBox)


        self.verticalLayout_2.addWidget(self.distanceWidget)

        self.droneSensorLabelsWidget = QHBoxLayout()
        self.droneSensorLabelsWidget.setObjectName(u"droneSensorLabelsWidget")
        self.droneSensorLabelsWidget.setContentsMargins(9, 9, 9, 9)
        self.droneSensorLabel = QLabel(self.mainWidget)
        self.droneSensorLabel.setObjectName(u"droneSensorLabel")
        self.droneSensorLabel.setFont(font)

        self.droneSensorLabelsWidget.addWidget(self.droneSensorLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.droneSensorLabelsWidget.addItem(self.horizontalSpacer)

        self.dronSensorVersionLabel = QLabel(self.mainWidget)
        self.dronSensorVersionLabel.setObjectName(u"dronSensorVersionLabel")
        self.dronSensorVersionLabel.setFont(font)

        self.droneSensorLabelsWidget.addWidget(self.dronSensorVersionLabel)

        self.horizontalSpacer_2 = QSpacerItem(10, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.droneSensorLabelsWidget.addItem(self.horizontalSpacer_2)

        self.droneSensorButton = QPushButton(self.mainWidget)
        self.droneSensorButton.setObjectName(u"droneSensorButton")
        self.droneSensorButton.setFont(font)
        self.droneSensorButton.setAutoDefault(False)

        self.droneSensorLabelsWidget.addWidget(self.droneSensorButton)


        self.verticalLayout_2.addLayout(self.droneSensorLabelsWidget)


        self.verticalLayout.addWidget(self.mainWidget, 0, Qt.AlignmentFlag.AlignTop)

        self.buttonBox = QDialogButtonBox(Preferences)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setFont(font)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Close)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(Preferences)
        self.buttonBox.rejected.connect(Preferences.reject)
        self.buttonBox.accepted.connect(Preferences.accept)

        QMetaObject.connectSlotsByName(Preferences)
    # setupUi

    def retranslateUi(self, Preferences):
        Preferences.setWindowTitle(QCoreApplication.translate("Preferences", u"Preferences", None))
        self.label.setText(QCoreApplication.translate("Preferences", u"Theme:", None))
        self.themeComboBox.setItemText(0, QCoreApplication.translate("Preferences", u"Light", None))
        self.themeComboBox.setItemText(1, QCoreApplication.translate("Preferences", u"Dark", None))

        self.maxAOIsLabel.setText(QCoreApplication.translate("Preferences", u"Max Areas of Interest: ", None))
        self.AOIRadiusLabel.setText(QCoreApplication.translate("Preferences", u"Area of Interest Circle Radius(px):", None))
        self.positionFormatLabel.setText(QCoreApplication.translate("Preferences", u"Coordinate System:", None))
        self.positionFormatComboBox.setItemText(0, QCoreApplication.translate("Preferences", u"Lat/Long - Decimal Degrees", None))
        self.positionFormatComboBox.setItemText(1, QCoreApplication.translate("Preferences", u"Lat/Long - Degrees, Minutes, Seconds", None))
        self.positionFormatComboBox.setItemText(2, QCoreApplication.translate("Preferences", u"UTM", None))

        self.temperatureLabel.setText(QCoreApplication.translate("Preferences", u"Temperature Unit:", None))
        self.temperatureComboBox.setItemText(0, QCoreApplication.translate("Preferences", u"Fahrenheit", None))
        self.temperatureComboBox.setItemText(1, QCoreApplication.translate("Preferences", u"Celsius", None))

        self.distanceLabel.setText(QCoreApplication.translate("Preferences", u"Distance Unit:", None))
        self.distanceComboBox.setItemText(0, QCoreApplication.translate("Preferences", u"Meters", None))
        self.distanceComboBox.setItemText(1, QCoreApplication.translate("Preferences", u"Feet", None))

        self.droneSensorLabel.setText(QCoreApplication.translate("Preferences", u"Drone Sensor File Version:", None))
        self.dronSensorVersionLabel.setText(QCoreApplication.translate("Preferences", u"TextLabel", None))
        self.droneSensorButton.setText(QCoreApplication.translate("Preferences", u"Replace", None))
    # retranslateUi

