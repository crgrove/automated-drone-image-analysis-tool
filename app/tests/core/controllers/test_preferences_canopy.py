"""Smoke tests for the code-built canopy source section in Preferences."""

import pytest
from unittest.mock import MagicMock

from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def prefs(app, monkeypatch):
    monkeypatch.setattr(
        "helpers.PickleHelper.PickleHelper.get_drone_sensor_file_version",
        staticmethod(lambda: {"Version": "1", "Date": "2020-01-01"}),
    )
    settings = {
        "Language": "en", "MaxAOIs": 100, "Theme": "Dark", "AOIRadius": 5,
        "PositionFormat": "Lat/Long - Decimal Degrees", "TemperatureUnit": "Fahrenheit",
        "DistanceUnit": "Feet",
    }
    parent = MagicMock()
    parent.settings_service.get_setting.side_effect = lambda k, d=None: settings.get(k, d)
    parent.settings_service.get_bool_setting.side_effect = lambda k, d=False: settings.get(k, d)
    parent.settings_service.set_setting.side_effect = lambda k, v: settings.__setitem__(k, v)

    from core.controllers.Preferences import Preferences
    dialog = Preferences(parent)
    return dialog, settings


def test_canopy_section_built(prefs):
    dialog, _ = prefs
    assert dialog.canopyKindComboBox.count() == 3
    ids = [dialog.canopyKindComboBox.itemData(i) for i in range(3)]
    assert ids == ["none", "landfire", "meta"]


def test_default_kind_none_hides_paths(prefs):
    dialog, _ = prefs
    # Default kind is 'none' -> path fields hidden.
    assert dialog.canopyKindComboBox.currentData() == "none"
    assert dialog.canopyManifestEdit.isVisible() is False


def test_changing_kind_persists_and_shows_paths(prefs):
    dialog, settings = prefs
    idx = dialog.canopyKindComboBox.findData("meta")
    dialog.canopyKindComboBox.setCurrentIndex(idx)
    assert settings["CanopyKind"] == "meta"
    # Path fields become relevant (widgets exist; visibility toggles on show).
    dialog.show()
    dialog._refresh_canopy_visibility()
    assert dialog.canopyManifestEdit.isVisibleTo(dialog.canopySourceGroup)
    dialog.hide()


def test_manifest_edit_persists(prefs):
    dialog, settings = prefs
    dialog.canopyManifestEdit.setText("C:/data/canopy.csv")
    dialog._update_canopy_manifest()
    assert settings["CanopyManifestPath"] == "C:/data/canopy.csv"


def test_load_settings_reads_back_persisted_canopy(app, qtbot, monkeypatch, tmp_path):
    """Back-compat READ path (CLAUDE.md 2.5): a settings store already populated
    with canopy keys must be reflected in the UI on construction via
    _load_settings -> combo currentData, edits set, path fields visible."""
    monkeypatch.setattr(
        "helpers.PickleHelper.PickleHelper.get_drone_sensor_file_version",
        staticmethod(lambda: {"Version": "1", "Date": "2020-01-01"}),
    )

    manifest_path = str(tmp_path / "canopy_manifest.csv")
    tiles_dir = str(tmp_path / "canopy_tiles")

    settings = {
        "Language": "en", "MaxAOIs": 100, "Theme": "Dark", "AOIRadius": 5,
        "PositionFormat": "Lat/Long - Decimal Degrees", "TemperatureUnit": "Fahrenheit",
        "DistanceUnit": "Feet",
        # Pre-populated canopy settings that must be read back on load.
        "CanopyKind": "meta",
        "CanopyManifestPath": manifest_path,
        "CanopyTilesDir": tiles_dir,
    }
    parent = MagicMock()
    parent.settings_service.get_setting.side_effect = lambda k, d=None: settings.get(k, d)
    parent.settings_service.get_bool_setting.side_effect = lambda k, d=False: settings.get(k, d)
    parent.settings_service.set_setting.side_effect = lambda k, v: settings.__setitem__(k, v)

    from core.controllers.Preferences import Preferences
    dialog = Preferences(parent)
    qtbot.addWidget(dialog)

    # Combo reflects the persisted kind.
    assert dialog.canopyKindComboBox.currentData() == "meta"
    # Path edits reflect the persisted values.
    assert dialog.canopyManifestEdit.text() == manifest_path
    assert dialog.canopyTilesEdit.text() == tiles_dir
    # A non-'none' kind means the path fields are shown (set by
    # _refresh_canopy_visibility during _load_settings).
    assert dialog.canopyManifestEdit.isVisibleTo(dialog.canopySourceGroup)
    assert dialog.canopyTilesEdit.isVisibleTo(dialog.canopySourceGroup)
