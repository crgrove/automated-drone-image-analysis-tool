import os
import shutil

from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox
from core.views.Preferences_ui import Ui_Preferences
from core.services.SettingsService import SettingsService
from helpers.PickleHelper import PickleHelper
from helpers.TranslationMixin import TranslationMixin


class Preferences(TranslationMixin, QDialog, Ui_Preferences):
    """Controller for the Preferences dialog box.

    This class manages user preferences for the application, including settings such as
    maximum areas of interest, theme, area of interest radius, position format, and temperature unit.
    """

    def __init__(self, parent):
        """Initializes the Preferences dialog.

        Args:
            parent (MainWindow): The parent window for the dialog.
        """
        super().__init__()
        self.parent = parent
        self.setupUi(self)

        # Set custom tooltip styling - light blue background with black text
        self.setStyleSheet("""
            QToolTip {
                background-color: lightblue;
                color: black;
                border: 1px solid #333333;
                padding: 4px;
                font-size: 11px;
            }
        """)

        self._terrain_service = None
        self._load_settings()
        self._connect_signals()
        self._update_terrain_cache_display()

    def _load_settings(self):
        """Loads the settings from SettingsService and updates the UI accordingly."""
        self.maxAOIsSpinBox.setValue(self.parent.settings_service.get_setting('MaxAOIs'))
        self.themeComboBox.setCurrentText(self.parent.settings_service.get_setting('Theme'))
        self.AOIRadiusSpinBox.setValue(self.parent.settings_service.get_setting('AOIRadius'))
        self.positionFormatComboBox.setCurrentText(self.parent.settings_service.get_setting('PositionFormat'))
        self.temperatureComboBox.setCurrentText(self.parent.settings_service.get_setting('TemperatureUnit'))
        # Load distance unit with default of 'Feet' if not set
        # Also handle legacy 'ft'/'m' values and convert to 'Feet'/'Meters'
        distance_unit = self.parent.settings_service.get_setting('DistanceUnit', 'Feet')
        if distance_unit == 'ft':
            distance_unit = 'Feet'
            self.parent.settings_service.set_setting('DistanceUnit', 'Feet')  # Migrate to new format
        elif distance_unit == 'm':
            distance_unit = 'Meters'
            self.parent.settings_service.set_setting('DistanceUnit', 'Meters')  # Migrate to new format
        self.distanceComboBox.setCurrentText(distance_unit)
        offline_only = self.parent.settings_service.get_bool_setting('OfflineOnly', False)
        if hasattr(self, 'offlineOnlyCheckBox'):
            self.offlineOnlyCheckBox.setChecked(offline_only)

        # Load terrain elevation setting (default: enabled)
        terrain_enabled = self.parent.settings_service.get_bool_setting('UseTerrainElevation', True)
        if hasattr(self, 'terrainElevationCheckBox'):
            self.terrainElevationCheckBox.setChecked(terrain_enabled)

        drone_sensor_version = PickleHelper.get_drone_sensor_file_version()
        self.dronSensorVersionLabel.setText(
            self.tr("{version}_{date}").format(
                version=drone_sensor_version['Version'],
                date=drone_sensor_version['Date']
            )
        )

    def _connect_signals(self):
        """Connects UI signals to the appropriate update methods."""
        self.maxAOIsSpinBox.valueChanged.connect(self._update_max_aois)
        self.AOIRadiusSpinBox.valueChanged.connect(self._update_aoi_radius)
        self.themeComboBox.currentTextChanged.connect(self._update_theme)
        self.positionFormatComboBox.currentTextChanged.connect(self._update_position_format)
        self.temperatureComboBox.currentTextChanged.connect(self._update_temperature_unit)
        self.distanceComboBox.currentTextChanged.connect(self._update_distance_unit)
        if hasattr(self, 'offlineOnlyCheckBox'):
            self.offlineOnlyCheckBox.toggled.connect(self._update_offline_only)
        if hasattr(self, 'terrainElevationCheckBox'):
            self.terrainElevationCheckBox.toggled.connect(self._update_terrain_elevation)
        if hasattr(self, 'clearTerrainCacheButton'):
            self.clearTerrainCacheButton.clicked.connect(self._clear_terrain_cache)
        self.droneSensorButton.clicked.connect(self._droneSensorButton_clicked)

    def _update_max_aois(self):
        """Updates the maximum areas of interest setting based on the spinbox value."""
        self.parent.settings_service.set_setting('MaxAOIs', self.maxAOIsSpinBox.value())

    def _update_aoi_radius(self):
        """Updates the area of interest radius setting based on the spinbox value."""
        self.parent.settings_service.set_setting('AOIRadius', self.AOIRadiusSpinBox.value())

    def _update_theme(self):
        """Updates the theme setting based on the selected combobox value and applies it."""
        theme = self.themeComboBox.currentText()
        self.parent.settings_service.set_setting('Theme', theme)
        self.parent.update_theme(theme)

    def _update_position_format(self):
        """Updates the position format setting based on the selected combobox value."""
        self.parent.settings_service.set_setting('PositionFormat', self.positionFormatComboBox.currentText())

    def _update_temperature_unit(self):
        """Updates the temperature unit setting based on the selected combobox value."""
        self.parent.settings_service.set_setting('TemperatureUnit', self.temperatureComboBox.currentText())

    def _update_distance_unit(self):
        """Updates the distance unit setting based on the selected combobox value."""
        self.parent.settings_service.set_setting('DistanceUnit', self.distanceComboBox.currentText())

    def _update_offline_only(self, checked: bool):
        """Update whether the app should run without online map/CalTopo access."""
        self.parent.settings_service.set_setting('OfflineOnly', bool(checked))

    def _update_terrain_elevation(self, checked: bool):
        """Update whether terrain elevation data should be used for AOI positioning."""
        self.parent.settings_service.set_setting('UseTerrainElevation', bool(checked))

        # Update terrain service if available
        if self._terrain_service:
            self._terrain_service.enabled = checked

    def _get_terrain_service(self):
        """Lazy-load terrain service."""
        if self._terrain_service is None:
            try:
                from core.services.terrain import TerrainService
                self._terrain_service = TerrainService()
            except Exception:
                pass
        return self._terrain_service

    def _update_terrain_cache_display(self):
        """Update the terrain cache size display."""
        if not hasattr(self, 'terrainCacheSizeLabel'):
            return

        try:
            service = self._get_terrain_service()
            if service:
                info = service.get_service_info()
                cache_info = info.get('cache', {})
                tiles = cache_info.get('total_tiles', 0)
                size_mb = cache_info.get('total_size_mb', 0)
                self.terrainCacheSizeLabel.setText(
                    self.tr("{tiles} tiles ({size_mb:.1f} MB)").format(
                        tiles=tiles,
                        size_mb=size_mb
                    )
                )
            else:
                self.terrainCacheSizeLabel.setText(self.tr("Not available"))
        except Exception:
            self.terrainCacheSizeLabel.setText(self.tr("Error"))

    def _clear_terrain_cache(self):
        """Clear the terrain elevation cache."""
        service = self._get_terrain_service()
        if not service:
            QMessageBox.warning(
                self,
                self.tr("Error"),
                self.tr("Terrain service not available.")
            )
            return

        reply = QMessageBox.question(
            self,
            self.tr("Clear Terrain Cache"),
            self.tr(
                "Are you sure you want to clear all cached terrain elevation data?\n\n"
                "This will require re-downloading tiles when terrain elevation is used."
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                count = service.clear_cache()
                self._update_terrain_cache_display()
                QMessageBox.information(
                    self,
                    self.tr("Cache Cleared"),
                    self.tr("Cleared {count} cached terrain tiles.").format(count=count)
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    self.tr("Error"),
                    self.tr("Failed to clear cache: {error}").format(error=e)
                )

    def _droneSensorButton_clicked(self):
        """
        Opens a file dialog for the user to select a .pkl file and copies it to the app's destination directory.
        """
        # Only allow .pkl files
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select a Drone Sensor File"),
            "",
            self.tr("Pickle Files (*.pkl)")
        )
        if not filename:
            return  # User cancelled

        # Destination path (change as needed)
        dest_dir = PickleHelper._get_destination_path()
        dest_file = os.path.join(dest_dir, 'drones.pkl')
        shutil.copy(filename, dest_file)
        PickleHelper.force_reload()
        drone_sensor_version = PickleHelper.get_drone_sensor_file_version()
        self.dronSensorVersionLabel.setText(
            self.tr("{version}_{date}").format(
                version=drone_sensor_version['Version'],
                date=drone_sensor_version['Date']
            )
        )
