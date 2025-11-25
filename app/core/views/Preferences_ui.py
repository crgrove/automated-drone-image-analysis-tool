# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Preferences.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QSpinBox,
    QVBoxLayout, QWidget)

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

        self.offlineWidget = QWidget(self.mainWidget)
        self.offlineWidget.setObjectName(u"offlineWidget")
        self.horizontalLayout_offline = QHBoxLayout(self.offlineWidget)
        self.horizontalLayout_offline.setObjectName(u"horizontalLayout_offline")
        self.offlineModeLabel = QLabel(self.offlineWidget)
        self.offlineModeLabel.setObjectName(u"offlineModeLabel")
        self.offlineModeLabel.setFont(font)

        self.horizontalLayout_offline.addWidget(self.offlineModeLabel)

        self.offlineOnlyCheckBox = QCheckBox(self.offlineWidget)
        self.offlineOnlyCheckBox.setObjectName(u"offlineOnlyCheckBox")
        self.offlineOnlyCheckBox.setFont(font)

        self.horizontalLayout_offline.addWidget(self.offlineOnlyCheckBox)


        self.verticalLayout_2.addWidget(self.offlineWidget)

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
#if QT_CONFIG(tooltip)
        self.label.setToolTip(QCoreApplication.translate("Preferences", u"Select the application theme appearance.\n"
"Changes the overall color scheme and visual style.", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("Preferences", u"Theme:", None))
        self.themeComboBox.setItemText(0, QCoreApplication.translate("Preferences", u"Light", None))
        self.themeComboBox.setItemText(1, QCoreApplication.translate("Preferences", u"Dark", None))

#if QT_CONFIG(tooltip)
        self.themeComboBox.setToolTip(QCoreApplication.translate("Preferences", u"Choose the application theme:\n"
"\u2022 Light: Bright theme with light backgrounds and dark text\n"
"\u2022 Dark: Dark theme with dark backgrounds and light text\n"
"Changes apply immediately to all windows.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.maxAOIsLabel.setToolTip(QCoreApplication.translate("Preferences", u"Warning threshold for total AOIs detected across all images.\n"
"Prompts user when this limit is reached during processing.", None))
#endif // QT_CONFIG(tooltip)
        self.maxAOIsLabel.setText(QCoreApplication.translate("Preferences", u"Max Areas of Interest: ", None))
#if QT_CONFIG(tooltip)
        self.maxAOIsSpinBox.setToolTip(QCoreApplication.translate("Preferences", u"Set the warning threshold for total AOIs detected during processing.\n"
"\u2022 Range: 0 to 1000\n"
"\u2022 Default: 100\n"
"When this number of AOIs is detected across all images:\n"
"\u2022 UI displays a warning message\n"
"\u2022 User can cancel processing, adjust settings, and rerun\n"
"\u2022 If no action taken, detection continues automatically\n"
"Use lower values to catch high detection counts early.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.AOIRadiusLabel.setToolTip(QCoreApplication.translate("Preferences", u"Radius for combining neighboring AOIs into single detections.\n"
"AOIs within this distance are merged together.", None))
#endif // QT_CONFIG(tooltip)
        self.AOIRadiusLabel.setText(QCoreApplication.translate("Preferences", u"Area of Interest Circle Radius(px):", None))
#if QT_CONFIG(tooltip)
        self.AOIRadiusSpinBox.setToolTip(QCoreApplication.translate("Preferences", u"Set the radius for combining nearby AOIs during detection.\n"
"\u2022 Range: 0 to 100 pixels\n"
"\u2022 Default: 25 pixels\n"
"When AOIs are within this radius of each other:\n"
"\u2022 They are combined into a single AOI\n"
"\u2022 Process repeats until no neighbors remain within radius\n"
"\u2022 Larger values: Combines more distant detections (fewer total AOIs)\n"
"\u2022 Smaller values: Keeps detections separate (more individual AOIs)\n"
"Use to consolidate clustered detections into single objects.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.positionFormatLabel.setToolTip(QCoreApplication.translate("Preferences", u"Format for displaying geographic coordinates throughout the application.\n"
"Affects how GPS locations are shown in the viewer and exports.", None))
#endif // QT_CONFIG(tooltip)
        self.positionFormatLabel.setText(QCoreApplication.translate("Preferences", u"Coordinate System:", None))
        self.positionFormatComboBox.setItemText(0, QCoreApplication.translate("Preferences", u"Lat/Long - Decimal Degrees", None))
        self.positionFormatComboBox.setItemText(1, QCoreApplication.translate("Preferences", u"Lat/Long - Degrees, Minutes, Seconds", None))
        self.positionFormatComboBox.setItemText(2, QCoreApplication.translate("Preferences", u"UTM", None))

#if QT_CONFIG(tooltip)
        self.positionFormatComboBox.setToolTip(QCoreApplication.translate("Preferences", u"Select the geographic coordinate display format:\n"
"\u2022 Lat/Long - Decimal Degrees: 34.123456, -118.987654 (most common, easy to use)\n"
"\u2022 Lat/Long - Degrees, Minutes, Seconds: 34\u00b0 7' 24.4416\" N, 118\u00b0 59' 15.5424\" W (traditional navigation)\n"
"\u2022 UTM: Universal Transverse Mercator grid system with zone, easting, northing (military, surveying)\n"
"This setting affects coordinate display in the viewer, exports, and overlays.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.temperatureLabel.setToolTip(QCoreApplication.translate("Preferences", u"Unit for displaying temperature measurements from thermal imagery.\n"
"Used when analyzing thermal images from thermal cameras.", None))
#endif // QT_CONFIG(tooltip)
        self.temperatureLabel.setText(QCoreApplication.translate("Preferences", u"Temperature Unit:", None))
        self.temperatureComboBox.setItemText(0, QCoreApplication.translate("Preferences", u"Fahrenheit", None))
        self.temperatureComboBox.setItemText(1, QCoreApplication.translate("Preferences", u"Celsius", None))

#if QT_CONFIG(tooltip)
        self.temperatureComboBox.setToolTip(QCoreApplication.translate("Preferences", u"Select the temperature unit for thermal image analysis:\n"
"\u2022 Fahrenheit (\u00b0F): Imperial temperature scale (US standard)\n"
"  - Water freezes at 32\u00b0F, boils at 212\u00b0F\n"
"\u2022 Celsius (\u00b0C): Metric temperature scale (international standard)\n"
"  - Water freezes at 0\u00b0C, boils at 100\u00b0C\n"
"Applies to thermal camera data display and analysis results.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.distanceLabel.setToolTip(QCoreApplication.translate("Preferences", u"Unit for displaying distance and altitude measurements.\n"
"Used for drone altitude, object distances, and spatial calculations.", None))
#endif // QT_CONFIG(tooltip)
        self.distanceLabel.setText(QCoreApplication.translate("Preferences", u"Distance Unit:", None))
        self.distanceComboBox.setItemText(0, QCoreApplication.translate("Preferences", u"Meters", None))
        self.distanceComboBox.setItemText(1, QCoreApplication.translate("Preferences", u"Feet", None))

#if QT_CONFIG(tooltip)
        self.distanceComboBox.setToolTip(QCoreApplication.translate("Preferences", u"Select the distance unit for measurements:\n"
"\u2022 Meters (m): Metric distance unit (international standard)\n"
"  - 1 meter = 3.281 feet\n"
"  - Used for altitude, GSD, and distance calculations\n"
"\u2022 Feet (ft): Imperial distance unit (US standard)\n"
"  - 1 foot = 0.3048 meters\n"
"  - Common in US aviation and surveying\n"
"Applies to altitude displays, GSD calculations, and distance measurements.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.offlineModeLabel.setToolTip(QCoreApplication.translate("Preferences", u"Toggle Offline Only mode.\n"
"When enabled, the app skips any network calls (map tiles, CalTopo exports) and works with cached data only.", None))
#endif // QT_CONFIG(tooltip)
        self.offlineModeLabel.setText(QCoreApplication.translate("Preferences", u"Offline Only Mode:", None))
#if QT_CONFIG(tooltip)
        self.offlineOnlyCheckBox.setToolTip(QCoreApplication.translate("Preferences", u"Disable online functionality (tile downloads, CalTopo integration) and work entirely offline.", None))
#endif // QT_CONFIG(tooltip)
        self.offlineOnlyCheckBox.setText(QCoreApplication.translate("Preferences", u"Enable", None))
#if QT_CONFIG(tooltip)
        self.droneSensorLabel.setToolTip(QCoreApplication.translate("Preferences", u"Version of the current drone sensor configuration file.\n"
"Contains camera specifications, sensor dimensions, and focal length data for different drone models.", None))
#endif // QT_CONFIG(tooltip)
        self.droneSensorLabel.setText(QCoreApplication.translate("Preferences", u"Drone Sensor File Version:", None))
#if QT_CONFIG(tooltip)
        self.dronSensorVersionLabel.setToolTip(QCoreApplication.translate("Preferences", u"Currently loaded drone sensor file version number.\n"
"The sensor file defines camera parameters for accurate GSD and AOI calculations.", None))
#endif // QT_CONFIG(tooltip)
        self.dronSensorVersionLabel.setText(QCoreApplication.translate("Preferences", u"TextLabel", None))
#if QT_CONFIG(tooltip)
        self.droneSensorButton.setToolTip(QCoreApplication.translate("Preferences", u"Replace the current drone sensor configuration file.\n"
"Allows updating to a newer version or custom sensor specifications.\n"
"Required file format: JSON with drone models, sensors, focal lengths, and dimensions.\n"
"Use this when:\n"
"\u2022 New drone models are available\n"
"\u2022 Sensor specifications need updating\n"
"\u2022 Custom camera configurations are needed\n"
"Backup existing file before replacing.", None))
#endif // QT_CONFIG(tooltip)
        self.droneSensorButton.setText(QCoreApplication.translate("Preferences", u"Replace", None))
#if QT_CONFIG(tooltip)
        self.buttonBox.setToolTip(QCoreApplication.translate("Preferences", u"Close the Preferences window.\n"
"All changes are saved automatically when modified.", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

