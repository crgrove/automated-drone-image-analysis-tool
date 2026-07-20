"""Tests for the Preferences dialog terrain-card arrangement."""

from unittest.mock import MagicMock

import pytest

from core.controllers.Preferences import Preferences


def _make_parent():
    parent = MagicMock()

    def get_setting(key, default=None):
        values = {
            'Language': 'en',
            'MaxAOIs': 200,
            'Theme': 'Dark',
            'AOIRadius': 15,
            'PositionFormat': 'Lat/Long - Decimal Degrees',
            'TemperatureUnit': 'Fahrenheit',
            'DistanceUnit': 'Feet',
            'TerrainProviderId': 'terrarium',
        }
        return values.get(key, default if default is not None else '')

    parent.settings_service.get_setting.side_effect = get_setting
    parent.settings_service.get_bool_setting.side_effect = lambda k, d=False: {
        'OfflineOnly': False,
        'UseTerrainElevation': True,
    }.get(k, d)
    return parent


@pytest.fixture
def preferences(qtbot):
    dialog = Preferences(_make_parent())
    qtbot.addWidget(dialog)
    return dialog


def _card_children(card):
    layout = card.layout()
    return [layout.itemAt(i).widget() for i in range(layout.count())]


# ---------------------------------------------------------------------------
# Terrain cache display
# ---------------------------------------------------------------------------

def test_terrain_cache_local_provider_shows_na_not_error(preferences):
    """A local-only provider (USGS 3DEP GeoTIFFs) has no download cache, so
    get_service_info() reports cache=None. That must read 'N/A (local tiles)',
    NOT 'Error' (regression: info.get('cache', {}) returned None and
    None.get(...) blew up into the swallowed 'Error')."""
    service = MagicMock()
    service.get_service_info.return_value = {
        'provider': 'USGS 3DEP 1m (Local GeoTIFF)', 'cache': None}
    preferences._get_terrain_service = MagicMock(return_value=service)

    preferences._update_terrain_cache_display()

    assert preferences.terrainCacheSizeLabel.text() == "N/A (local tiles)"


def test_terrain_cache_online_provider_shows_tiles_and_size(preferences):
    """A caching provider (Terrain Tiles) reports tile count and size."""
    service = MagicMock()
    service.get_service_info.return_value = {
        'provider': 'AWS Terrain Tiles', 'cache': {'total_tiles': 12, 'total_size_mb': 3.5}}
    preferences._get_terrain_service = MagicMock(return_value=service)

    preferences._update_terrain_cache_display()

    assert preferences.terrainCacheSizeLabel.text() == "12 tiles (3.5 MB)"


def test_terrain_cache_no_service_shows_not_available(preferences):
    preferences._get_terrain_service = MagicMock(return_value=None)
    preferences._update_terrain_cache_display()
    assert preferences.terrainCacheSizeLabel.text() == "Not available"


def test_terrain_card_groups_all_three_controls(preferences):
    """The three related terrain controls live inside one Terrain card, in
    order: Use Terrain Elevation, Elevation Source, Terrain Cache."""
    assert hasattr(preferences, 'terrainCard')
    children = _card_children(preferences.terrainCard)

    assert children == [
        preferences.terrainWidget,
        preferences.terrainProviderGroup,
        preferences.terrainCacheWidget,
    ]


def test_canopy_group_is_at_the_bottom_below_terrain(preferences):
    """The Canopy Data Source group is the last item, directly below the
    Terrain card."""
    layout = preferences.verticalLayout_2
    last = layout.itemAt(layout.count() - 1).widget()
    second_last = layout.itemAt(layout.count() - 2).widget()
    assert last is preferences.canopySourceGroup
    assert second_last is preferences.terrainCard


def test_preferences_use_scroll_area(preferences):
    """All settings live inside a scroll area so the dialog can stay compact."""
    assert hasattr(preferences, 'scrollArea')
    assert preferences.scrollArea.widgetResizable()
    assert preferences.scrollArea.widget() is preferences.mainWidget


def test_terrain_controls_not_left_in_top_level_layout(preferences):
    """The card's controls were moved out of the main layout (no duplicates)."""
    layout = preferences.verticalLayout_2
    top_level = {layout.itemAt(i).widget() for i in range(layout.count())}

    assert preferences.terrainWidget not in top_level
    assert preferences.terrainCacheWidget not in top_level
    assert preferences.terrainProviderGroup not in top_level
    # Only the card itself represents them at the top level.
    assert preferences.terrainCard in top_level


# ---------------------------------------------------------------------------
# 3DEP inactive-until-configured warning + baseline note
# ---------------------------------------------------------------------------

def test_baseline_note_present(preferences):
    """The card states the overlay semantics: AWS baseline always available,
    3DEP adds local detail."""
    assert "baseline" in preferences.terrainBaselineLabel.text()
    assert not preferences.terrainBaselineLabel.isHidden()


def test_3dep_warning_hidden_for_online_provider(preferences):
    # Fixture provider is terrarium -> fields and warning hidden.
    assert preferences.terrain3DEPPathsWarningLabel.isHidden()


def test_3dep_warning_shown_when_local_selected_without_paths(preferences):
    idx = preferences.terrainProviderComboBox.findData('usgs_3dep_local')
    preferences.terrainProviderComboBox.setCurrentIndex(idx)
    assert not preferences.terrain3DEPPathsWarningLabel.isHidden()
    assert "inactive" in preferences.terrain3DEPPathsWarningLabel.text()


def test_3dep_warning_clears_once_both_paths_set(preferences, tmp_path):
    manifest = tmp_path / "dem_manifest.csv"
    manifest.write_text("filename,minX,minY,maxX,maxY\n")
    idx = preferences.terrainProviderComboBox.findData('usgs_3dep_local')
    preferences.terrainProviderComboBox.setCurrentIndex(idx)
    preferences.terrain3DEPManifestEdit.setText(str(manifest))
    preferences._update_terrain_3dep_manifest()
    assert not preferences.terrain3DEPPathsWarningLabel.isHidden()  # tiles still missing
    preferences.terrain3DEPTilesEdit.setText(str(tmp_path))
    preferences._update_terrain_3dep_tiles()
    assert preferences.terrain3DEPPathsWarningLabel.isHidden()


def test_3dep_warning_flags_missing_files(preferences, tmp_path):
    """Paths set but gone from disk (moved/deleted results folder) show the
    dangling-registration message, not the paths-unset one."""
    idx = preferences.terrainProviderComboBox.findData('usgs_3dep_local')
    preferences.terrainProviderComboBox.setCurrentIndex(idx)
    preferences.terrain3DEPManifestEdit.setText(str(tmp_path / "gone" / "m.csv"))
    preferences.terrain3DEPTilesEdit.setText(str(tmp_path / "gone"))
    preferences._refresh_terrain_provider_visibility()
    assert not preferences.terrain3DEPPathsWarningLabel.isHidden()
    assert "no longer exist" in preferences.terrain3DEPPathsWarningLabel.text()


def test_3dep_warning_hidden_when_files_exist(preferences, tmp_path):
    manifest = tmp_path / "dem_manifest.csv"
    manifest.write_text("filename,minX,minY,maxX,maxY\n")
    idx = preferences.terrainProviderComboBox.findData('usgs_3dep_local')
    preferences.terrainProviderComboBox.setCurrentIndex(idx)
    preferences.terrain3DEPManifestEdit.setText(str(manifest))
    preferences.terrain3DEPTilesEdit.setText(str(tmp_path))
    preferences._refresh_terrain_provider_visibility()
    assert preferences.terrain3DEPPathsWarningLabel.isHidden()


def test_canopy_warning_flags_missing_files(preferences, tmp_path):
    cidx = preferences.canopyKindComboBox.findData('meta')
    preferences.canopyKindComboBox.setCurrentIndex(cidx)
    preferences.canopyManifestEdit.setText(str(tmp_path / "gone" / "chm_manifest.csv"))
    preferences.canopyTilesEdit.setText(str(tmp_path / "gone"))
    preferences._refresh_canopy_visibility()
    assert not preferences.canopyPathsWarningLabel.isHidden()
    assert "no longer exist" in preferences.canopyPathsWarningLabel.text()
