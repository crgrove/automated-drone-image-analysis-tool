import os
import shutil

from PySide6.QtWidgets import (
    QDialog, QFileDialog, QMessageBox, QComboBox, QHBoxLayout, QVBoxLayout, QLabel, QWidget,
    QPushButton, QLineEdit, QGroupBox
)
from core.views.Preferences_ui import Ui_Preferences
from core.services.LoggerService import LoggerService
from core.services.SettingsService import SettingsService
from core.services.terrain import (
    TerrainProviderFactory,
    PROVIDER_USGS_3DEP_LOCAL,
    DEFAULT_PROVIDER_ID,
)
from core.services.terrain.CanopyServiceFactory import (
    CanopyServiceFactory,
    CANOPY_KIND_NONE,
    DEFAULT_CANOPY_KIND,
)
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
        self._add_language_selection()
        self._add_terrain_provider_section()
        self._arrange_terrain_controls()
        # Canopy is added after the Terrain card so it sits at the bottom.
        self._add_canopy_source_section()
        self._load_settings()
        self._connect_signals()
        self._update_terrain_cache_display()

    def _add_language_selection(self):
        """Adds a language selection combo box to the UI dynamically."""
        # Create a new widget for language selection
        self.languageWidget = QWidget(self.mainWidget)
        self.languageLayout = QHBoxLayout(self.languageWidget)

        self.languageLabel = QLabel(self.tr("Language:"), self.languageWidget)
        font = self.label.font()
        self.languageLabel.setFont(font)

        self.languageComboBox = QComboBox(self.languageWidget)
        self.languageComboBox.setFont(font)
        self.languageComboBox.addItem("English", "en")
        self.languageComboBox.addItem("Italiano", "it")
        self.languageComboBox.addItem("Español", "es")
        self.languageComboBox.addItem("Nederlands", "nl")

        self.languageLayout.addWidget(self.languageLabel)
        self.languageLayout.addWidget(self.languageComboBox)

        # Insert it before the theme widget or at the top
        self.verticalLayout_2.insertWidget(0, self.languageWidget)

    def _add_terrain_provider_section(self):
        """Build the elevation-source controls (provider combo + 3DEP paths).

        This is a plain container with no border/title of its own; it is
        nested inside the "Terrain" card assembled by
        _arrange_terrain_controls, so the card's frame is the only border.
        """
        self.terrainProviderGroup = QWidget(self.mainWidget)
        layout = QVBoxLayout(self.terrainProviderGroup)
        layout.setContentsMargins(0, 0, 0, 0)

        # Baseline note: local 3DEP is an overlay on the always-available
        # online baseline, not an either/or replacement (TerrainService falls
        # back per-query outside local coverage).
        self.terrainBaselineLabel = QLabel(
            self.tr("AWS Terrain Tiles (online, ~30 m) is always available as the "
                    "baseline; local USGS 3DEP adds 1 m detail where downloaded."),
            self.terrainProviderGroup)
        self.terrainBaselineLabel.setWordWrap(True)
        self.terrainBaselineLabel.setStyleSheet("color: #909090;")
        layout.addWidget(self.terrainBaselineLabel)

        combo_row = QHBoxLayout()
        combo_label = QLabel(self.tr("Elevation Source:"), self.terrainProviderGroup)
        self.terrainProviderComboBox = QComboBox(self.terrainProviderGroup)
        for provider in TerrainProviderFactory.available_providers():
            self.terrainProviderComboBox.addItem(provider['label'], provider['id'])
        combo_row.addWidget(combo_label)
        combo_row.addWidget(self.terrainProviderComboBox, 1)
        layout.addLayout(combo_row)

        # 3DEP manifest path
        manifest_row = QHBoxLayout()
        self.terrain3DEPManifestLabel = QLabel(self.tr("Manifest CSV:"), self.terrainProviderGroup)
        self.terrain3DEPManifestEdit = QLineEdit(self.terrainProviderGroup)
        self.terrain3DEPManifestEdit.setPlaceholderText(self.tr("Path to dem_manifest.csv"))
        self.terrain3DEPManifestButton = QPushButton(self.tr("Browse..."), self.terrainProviderGroup)
        manifest_row.addWidget(self.terrain3DEPManifestLabel)
        manifest_row.addWidget(self.terrain3DEPManifestEdit, 1)
        manifest_row.addWidget(self.terrain3DEPManifestButton)
        layout.addLayout(manifest_row)

        # 3DEP tiles dir
        tiles_row = QHBoxLayout()
        self.terrain3DEPTilesLabel = QLabel(self.tr("Tiles directory:"), self.terrainProviderGroup)
        self.terrain3DEPTilesEdit = QLineEdit(self.terrainProviderGroup)
        self.terrain3DEPTilesEdit.setPlaceholderText(self.tr("Folder containing the GeoTIFF tiles"))
        self.terrain3DEPTilesButton = QPushButton(self.tr("Browse..."), self.terrainProviderGroup)
        tiles_row.addWidget(self.terrain3DEPTilesLabel)
        tiles_row.addWidget(self.terrain3DEPTilesEdit, 1)
        tiles_row.addWidget(self.terrain3DEPTilesButton)
        layout.addLayout(tiles_row)

        # Inline validation, mirroring the canopy section: a paths-requiring
        # provider with empty paths silently runs on the online baseline.
        self.terrain3DEPPathsWarningLabel = QLabel(
            self.tr("3DEP is inactive until both paths are set — the AWS Terrain "
                    "Tiles baseline is used. Use Download tiles… or Browse."),
            self.terrainProviderGroup)
        self.terrain3DEPPathsWarningLabel.setStyleSheet("color: #E6A700;")
        self.terrain3DEPPathsWarningLabel.setWordWrap(True)
        self.terrain3DEPPathsWarningLabel.setVisible(False)
        layout.addWidget(self.terrain3DEPPathsWarningLabel)

        # Placement is handled by _arrange_terrain_controls, which nests this
        # section inside the "Terrain" card with the toggle and cache rows.

    def _arrange_terrain_controls(self):
        """Collect the related terrain controls into a single "Terrain" card at
        the bottom of the dialog:

            Terrain  (QGroupBox card)
              Use Terrain Elevation   (terrainWidget, from the .ui)
              Elevation Source         (terrainProviderGroup, built in code)
              Terrain Cache            (terrainCacheWidget, from the .ui)

        The .ui-defined rows are detached from their default positions and
        re-parented into the card so the three settings read as one group.
        """
        layout = self.verticalLayout_2
        terrain_widget = getattr(self, 'terrainWidget', None)
        cache_widget = getattr(self, 'terrainCacheWidget', None)

        # Detach the .ui rows from their default positions (no-op if absent).
        for widget in (terrain_widget, cache_widget):
            if widget is not None:
                layout.removeWidget(widget)

        self.terrainCard = QGroupBox(self.tr("Terrain"), self.mainWidget)
        card_layout = QVBoxLayout(self.terrainCard)
        if terrain_widget is not None:
            card_layout.addWidget(terrain_widget)
        card_layout.addWidget(self.terrainProviderGroup)
        if cache_widget is not None:
            card_layout.addWidget(cache_widget)

        # Place the card at the bottom of the settings area.
        layout.addWidget(self.terrainCard)

    def _add_canopy_source_section(self):
        """Add a Canopy/vegetation source group: kind combo + manifest/tiles paths.

        Code-built to match the sibling terrain-provider section (also code-built,
        not in Preferences.ui); a documented CLAUDE.md 2.6 family exception.
        """
        self.canopySourceGroup = QGroupBox(self.tr("Canopy Data Source"), self.mainWidget)
        layout = QVBoxLayout(self.canopySourceGroup)

        combo_row = QHBoxLayout()
        combo_label = QLabel(self.tr("Source:"), self.canopySourceGroup)
        self.canopyKindComboBox = QComboBox(self.canopySourceGroup)
        for kind in CanopyServiceFactory.available_kinds():
            self.canopyKindComboBox.addItem(kind['label'], kind['id'])
        combo_row.addWidget(combo_label)
        combo_row.addWidget(self.canopyKindComboBox, 1)
        layout.addLayout(combo_row)

        manifest_row = QHBoxLayout()
        self.canopyManifestLabel = QLabel(self.tr("Manifest CSV:"), self.canopySourceGroup)
        self.canopyManifestEdit = QLineEdit(self.canopySourceGroup)
        self.canopyManifestEdit.setPlaceholderText(self.tr("Path to the canopy manifest CSV"))
        self.canopyManifestButton = QPushButton(self.tr("Browse..."), self.canopySourceGroup)
        manifest_row.addWidget(self.canopyManifestLabel)
        manifest_row.addWidget(self.canopyManifestEdit, 1)
        manifest_row.addWidget(self.canopyManifestButton)
        layout.addLayout(manifest_row)

        tiles_row = QHBoxLayout()
        self.canopyTilesLabel = QLabel(self.tr("Tiles directory:"), self.canopySourceGroup)
        self.canopyTilesEdit = QLineEdit(self.canopySourceGroup)
        self.canopyTilesEdit.setPlaceholderText(self.tr("Folder containing the GeoTIFF tiles"))
        self.canopyTilesButton = QPushButton(self.tr("Browse..."), self.canopySourceGroup)
        tiles_row.addWidget(self.canopyTilesLabel)
        tiles_row.addWidget(self.canopyTilesEdit, 1)
        tiles_row.addWidget(self.canopyTilesButton)
        layout.addLayout(tiles_row)

        # Inline validation: a paths-requiring kind with empty paths means
        # canopy is silently disabled at runtime -- say so right here.
        self.canopyPathsWarningLabel = QLabel(
            self.tr("Canopy is disabled until both paths are set — "
                    "use Download tiles… or Browse."),
            self.canopySourceGroup)
        self.canopyPathsWarningLabel.setStyleSheet("color: #E6A700;")
        self.canopyPathsWarningLabel.setWordWrap(True)
        self.canopyPathsWarningLabel.setVisible(False)
        layout.addWidget(self.canopyPathsWarningLabel)

        fetch_row = QHBoxLayout()
        fetch_row.addStretch()
        self.canopyFetchButton = QPushButton(self.tr("Download tiles..."), self.canopySourceGroup)
        self.canopyFetchButton.setToolTip(self.tr(
            "Download DEM and/or canopy tiles for an area of interest and register them here. "
            "Note: the canopy download uses Meta/WRI data and registers it as the canopy source."))
        fetch_row.addWidget(self.canopyFetchButton)
        layout.addLayout(fetch_row)

        # Append below the Terrain card (added by _arrange_terrain_controls) so
        # the Canopy Data Source group is the last section in the dialog.
        self.verticalLayout_2.addWidget(self.canopySourceGroup)

    def _load_settings(self):
        """Loads the settings from SettingsService and updates the UI accordingly."""
        lang = self.parent.settings_service.get_setting('Language', 'en')
        index = self.languageComboBox.findData(lang)
        if index >= 0:
            self.languageComboBox.setCurrentIndex(index)

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

        # Terrain provider selection + 3DEP paths
        provider_id = self.parent.settings_service.get_setting('TerrainProviderId', DEFAULT_PROVIDER_ID) or DEFAULT_PROVIDER_ID
        idx = self.terrainProviderComboBox.findData(provider_id)
        if idx >= 0:
            self.terrainProviderComboBox.setCurrentIndex(idx)
        manifest = self.parent.settings_service.get_setting('Terrain3DEPManifestPath', '') or ''
        tiles_dir = self.parent.settings_service.get_setting('Terrain3DEPTilesDir', '') or ''
        self.terrain3DEPManifestEdit.setText(manifest)
        self.terrain3DEPTilesEdit.setText(tiles_dir)
        self._refresh_terrain_provider_visibility()

        # Canopy source selection + paths
        canopy_kind = self.parent.settings_service.get_setting('CanopyKind', DEFAULT_CANOPY_KIND) or DEFAULT_CANOPY_KIND
        cidx = self.canopyKindComboBox.findData(canopy_kind)
        if cidx >= 0:
            self.canopyKindComboBox.setCurrentIndex(cidx)
        self.canopyManifestEdit.setText(self.parent.settings_service.get_setting('CanopyManifestPath', '') or '')
        self.canopyTilesEdit.setText(self.parent.settings_service.get_setting('CanopyTilesDir', '') or '')
        self._refresh_canopy_visibility()

        drone_sensor_version = PickleHelper.get_drone_sensor_file_version()
        self.dronSensorVersionLabel.setText(
            self.tr("{version}_{date}").format(
                version=drone_sensor_version['Version'],
                date=drone_sensor_version['Date']
            )
        )

    def _connect_signals(self):
        """Connects UI signals to the appropriate update methods."""
        self.languageComboBox.currentIndexChanged.connect(self._update_language)
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
        self.terrainProviderComboBox.currentIndexChanged.connect(self._update_terrain_provider)
        self.terrain3DEPManifestEdit.editingFinished.connect(self._update_terrain_3dep_manifest)
        self.terrain3DEPTilesEdit.editingFinished.connect(self._update_terrain_3dep_tiles)
        self.terrain3DEPManifestButton.clicked.connect(self._browse_terrain_3dep_manifest)
        self.terrain3DEPTilesButton.clicked.connect(self._browse_terrain_3dep_tiles)
        self.canopyKindComboBox.currentIndexChanged.connect(self._update_canopy_kind)
        self.canopyManifestEdit.editingFinished.connect(self._update_canopy_manifest)
        self.canopyTilesEdit.editingFinished.connect(self._update_canopy_tiles)
        self.canopyManifestButton.clicked.connect(self._browse_canopy_manifest)
        self.canopyTilesButton.clicked.connect(self._browse_canopy_tiles)
        self.canopyFetchButton.clicked.connect(self._open_tile_fetch_dialog)
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

    def _refresh_terrain_provider_visibility(self):
        """Show/hide the 3DEP path fields based on the active provider, and
        surface the inactive-until-configured warning when paths are missing."""
        is_local = self.terrainProviderComboBox.currentData() == PROVIDER_USGS_3DEP_LOCAL
        for w in (
            self.terrain3DEPManifestLabel, self.terrain3DEPManifestEdit, self.terrain3DEPManifestButton,
            self.terrain3DEPTilesLabel, self.terrain3DEPTilesEdit, self.terrain3DEPTilesButton,
        ):
            w.setVisible(is_local)
        if hasattr(self, 'terrain3DEPPathsWarningLabel'):
            manifest = self.terrain3DEPManifestEdit.text().strip()
            tiles = self.terrain3DEPTilesEdit.text().strip()
            if is_local and not (manifest and tiles):
                self.terrain3DEPPathsWarningLabel.setText(self.tr(
                    "3DEP is inactive until both paths are set — the AWS Terrain "
                    "Tiles baseline is used. Use Download tiles… or Browse."))
                self.terrain3DEPPathsWarningLabel.setVisible(True)
            elif is_local and not (os.path.isfile(manifest) and os.path.isdir(tiles)):
                # Registered but gone from disk (results folder moved/deleted).
                self.terrain3DEPPathsWarningLabel.setText(self.tr(
                    "The registered 3DEP files no longer exist on disk — the AWS "
                    "Terrain Tiles baseline is used. Re-download or fix the paths."))
                self.terrain3DEPPathsWarningLabel.setVisible(True)
            else:
                self.terrain3DEPPathsWarningLabel.setVisible(False)

    def _update_terrain_provider(self):
        """Persist the active terrain provider id and refresh dependent UI."""
        provider_id = self.terrainProviderComboBox.currentData() or DEFAULT_PROVIDER_ID
        self.parent.settings_service.set_setting('TerrainProviderId', provider_id)
        self._refresh_terrain_provider_visibility()
        # Force terrain service to rebuild on next access so the new provider is used.
        self._terrain_service = None

    def _update_terrain_3dep_manifest(self):
        self.parent.settings_service.set_setting(
            'Terrain3DEPManifestPath', self.terrain3DEPManifestEdit.text().strip()
        )
        self._terrain_service = None
        self._refresh_terrain_provider_visibility()

    def _update_terrain_3dep_tiles(self):
        self.parent.settings_service.set_setting(
            'Terrain3DEPTilesDir', self.terrain3DEPTilesEdit.text().strip()
        )
        self._terrain_service = None
        self._refresh_terrain_provider_visibility()

    def _browse_terrain_3dep_manifest(self):
        start_dir = self.terrain3DEPManifestEdit.text() or os.path.expanduser("~")
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select 3DEP manifest CSV"),
            start_dir,
            self.tr("CSV files (*.csv);;All files (*)"),
        )
        if filename:
            self.terrain3DEPManifestEdit.setText(filename)
            self._update_terrain_3dep_manifest()

    def _browse_terrain_3dep_tiles(self):
        start_dir = self.terrain3DEPTilesEdit.text() or os.path.expanduser("~")
        directory = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select 3DEP tiles directory"),
            start_dir,
        )
        if directory:
            self.terrain3DEPTilesEdit.setText(directory)
            self._update_terrain_3dep_tiles()

    # ---- Canopy source ----

    def _refresh_canopy_visibility(self):
        """Show/hide the canopy path fields based on the selected source kind,
        and surface the disabled-until-configured warning when paths are missing."""
        needs_paths = self.canopyKindComboBox.currentData() != CANOPY_KIND_NONE
        for w in (
            self.canopyManifestLabel, self.canopyManifestEdit, self.canopyManifestButton,
            self.canopyTilesLabel, self.canopyTilesEdit, self.canopyTilesButton,
        ):
            w.setVisible(needs_paths)
        if hasattr(self, 'canopyPathsWarningLabel'):
            manifest = self.canopyManifestEdit.text().strip()
            tiles = self.canopyTilesEdit.text().strip()
            if needs_paths and not (manifest and tiles):
                self.canopyPathsWarningLabel.setText(self.tr(
                    "Canopy is disabled until both paths are set — "
                    "use Download tiles… or Browse."))
                self.canopyPathsWarningLabel.setVisible(True)
            elif needs_paths and not (os.path.isfile(manifest) and os.path.isdir(tiles)):
                # Registered but gone from disk (results folder moved/deleted).
                self.canopyPathsWarningLabel.setText(self.tr(
                    "The registered canopy files no longer exist on disk — canopy "
                    "is disabled. Re-download or fix the paths."))
                self.canopyPathsWarningLabel.setVisible(True)
            else:
                self.canopyPathsWarningLabel.setVisible(False)

    def _update_canopy_kind(self):
        kind = self.canopyKindComboBox.currentData() or DEFAULT_CANOPY_KIND
        self.parent.settings_service.set_setting('CanopyKind', kind)
        self._refresh_canopy_visibility()

    def _update_canopy_manifest(self):
        self.parent.settings_service.set_setting(
            'CanopyManifestPath', self.canopyManifestEdit.text().strip())
        self._refresh_canopy_visibility()

    def _update_canopy_tiles(self):
        self.parent.settings_service.set_setting(
            'CanopyTilesDir', self.canopyTilesEdit.text().strip())
        self._refresh_canopy_visibility()

    def _browse_canopy_manifest(self):
        start_dir = self.canopyManifestEdit.text() or os.path.expanduser("~")
        filename, _ = QFileDialog.getOpenFileName(
            self, self.tr("Select canopy manifest CSV"), start_dir,
            self.tr("CSV files (*.csv);;All files (*)"))
        if filename:
            self.canopyManifestEdit.setText(filename)
            self._update_canopy_manifest()

    def _browse_canopy_tiles(self):
        start_dir = self.canopyTilesEdit.text() or os.path.expanduser("~")
        directory = QFileDialog.getExistingDirectory(
            self, self.tr("Select canopy tiles directory"), start_dir)
        if directory:
            self.canopyTilesEdit.setText(directory)
            self._update_canopy_tiles()

    def _open_tile_fetch_dialog(self):
        """Open the Download Tiles dialog and register any downloaded paths."""
        try:
            from core.controllers.images.viewer.exports.TileFetchController import TileFetchController
        except Exception as e:
            QMessageBox.information(
                self, self.tr("Download Tiles"),
                self.tr("The tile downloader is unavailable:\n{error}").format(error=str(e)))
            return
        # If a mission is loaded in the viewer, hand its images to the fetch
        # dialog so it can auto-fill the AOI (no manual coordinates needed).
        mission_images = None
        default_output_dir = None
        viewer = getattr(self.parent, 'viewer', None)
        if viewer is not None:
            mission_images = getattr(viewer, 'source_images', None) or getattr(viewer, 'images', None)
            # Default the download destination to the loaded results folder.
            # xml_path is a pathlib.Path (see MainWindow), so accept any path-like.
            xml_path = getattr(viewer, 'xml_path', None)
            if isinstance(xml_path, (str, os.PathLike)) and os.fspath(xml_path):
                default_output_dir = os.path.dirname(os.fspath(xml_path))

        controller = TileFetchController(self, self.parent.settings_service, logger=None)
        controller.run_fetch(mission_images=mission_images, default_output_dir=default_output_dir)
        # Reflect any settings the fetch registered back into the fields.
        self.canopyManifestEdit.setText(self.parent.settings_service.get_setting('CanopyManifestPath', '') or '')
        self.canopyTilesEdit.setText(self.parent.settings_service.get_setting('CanopyTilesDir', '') or '')
        canopy_kind = self.parent.settings_service.get_setting('CanopyKind', DEFAULT_CANOPY_KIND) or DEFAULT_CANOPY_KIND
        cidx = self.canopyKindComboBox.findData(canopy_kind)
        if cidx >= 0:
            self.canopyKindComboBox.setCurrentIndex(cidx)
        self._refresh_canopy_visibility()
        # Mirror the write-back for the DEM: a registered 3DEP download should
        # show up in the terrain fields immediately, not only after a reopen.
        if hasattr(self, 'terrain3DEPManifestEdit'):
            dem_manifest = self.parent.settings_service.get_setting('Terrain3DEPManifestPath', '') or ''
            dem_tiles = self.parent.settings_service.get_setting('Terrain3DEPTilesDir', '') or ''
            if dem_manifest:
                self.terrain3DEPManifestEdit.setText(dem_manifest)
            if dem_tiles:
                self.terrain3DEPTilesEdit.setText(dem_tiles)
            provider_id = self.parent.settings_service.get_setting('TerrainProviderId', '') or ''
            pidx = self.terrainProviderComboBox.findData(provider_id) if provider_id else -1
            if pidx >= 0:
                self.terrainProviderComboBox.setCurrentIndex(pidx)

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
            if not service:
                self.terrainCacheSizeLabel.setText(self.tr("Not available"))
                return
            info = service.get_service_info()
            cache_info = info.get('cache')
            if cache_info:
                tiles = cache_info.get('total_tiles', 0)
                size_mb = cache_info.get('total_size_mb', 0)
                self.terrainCacheSizeLabel.setText(
                    self.tr("{tiles} tiles ({size_mb:.1f} MB)").format(
                        tiles=tiles,
                        size_mb=size_mb
                    )
                )
            else:
                # Local-only providers (e.g. USGS 3DEP local GeoTIFFs) download
                # nothing, so there is no cache (get_service_info reports
                # cache=None). That's expected, not an error.
                self.terrainCacheSizeLabel.setText(self.tr("N/A (local tiles)"))
        except Exception as e:
            LoggerService().error(f"Preferences: terrain cache display failed: {e}")
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
        """Lets the user pick a replacement drones.csv and copies it into AppData."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select a Drone Sensor File"),
            "",
            self.tr("CSV Files (*.csv)")
        )
        if not filename:
            return

        dest_dir = PickleHelper._get_destination_path()
        dest_file = os.path.join(dest_dir, 'drones.csv')
        shutil.copy(filename, dest_file)
        PickleHelper.force_reload()
        drone_sensor_version = PickleHelper.get_drone_sensor_file_version()
        self.dronSensorVersionLabel.setText(
            self.tr("{version}_{date}").format(
                version=drone_sensor_version['Version'],
                date=drone_sensor_version['Date']
            )
        )

    def _update_language(self):
        """Updates the language setting and informs the user that a restart is required."""
        lang_code = self.languageComboBox.currentData()
        current_lang = self.parent.settings_service.get_setting('Language', 'en')

        if lang_code != current_lang:
            self.parent.settings_service.set_setting('Language', lang_code)
            QMessageBox.information(
                self,
                self.tr("Restart Required"),
                self.tr("Please restart the application for language changes to take effect.")
            )
