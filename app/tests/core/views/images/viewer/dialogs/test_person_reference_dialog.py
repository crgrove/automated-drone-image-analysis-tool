"""Tests for PersonReferenceDialog settings persistence.

The dialog is constructed with a null-camera mock so no perspective
projection or scene rendering happens; only the settings-restore/persist
behaviour is exercised. QSettings is redirected to a temp INI file so the
test never touches the real user settings.
"""

from unittest.mock import MagicMock

import pytest
from PySide6 import QtCore

from core.services.SettingsService import SettingsService
from core.views.images.viewer.dialogs.PersonReferenceDialog import (
    PersonReferenceDialog,
    SETTING_SIZE_KEY,
    SETTING_SHOW_STANDING,
    SETTING_SHOW_RECUMBENT,
    SETTING_SHOW_SITTING,
    SETTING_SHOW_SHADOWS,
    SETTING_USE_TERRAIN,
)


@pytest.fixture
def isolated_settings(tmp_path, monkeypatch):
    """Redirect every SettingsService in this test to a temp INI file."""
    ini = str(tmp_path / "settings.ini")
    real_qsettings = QtCore.QSettings  # capture before patching

    def factory(*args, **kwargs):
        return real_qsettings(ini, real_qsettings.IniFormat)

    monkeypatch.setattr(
        'core.services.SettingsService.QtCore.QSettings', factory)
    return SettingsService()


def _make_dialog(qtbot):
    """Build the dialog with a mock image service that yields no camera."""
    image_service = MagicMock()
    image_service.get_camera_intrinsics.return_value = None  # -> camera is None
    viewer = MagicMock()
    dialog = PersonReferenceDialog(
        None, viewer, image_service, 'does-not-exist.jpg', 'ft')
    qtbot.addWidget(dialog)
    return dialog


def test_restores_saved_settings(app, qtbot, isolated_settings):
    isolated_settings.set_setting(SETTING_SIZE_KEY, 'child')
    isolated_settings.set_setting(SETTING_SHOW_STANDING, False)
    isolated_settings.set_setting(SETTING_SHOW_RECUMBENT, False)
    isolated_settings.set_setting(SETTING_SHOW_SITTING, True)
    isolated_settings.set_setting(SETTING_SHOW_SHADOWS, False)
    isolated_settings.set_setting(SETTING_USE_TERRAIN, False)

    dialog = _make_dialog(qtbot)

    assert dialog.size_combo.currentData() == 'child'
    assert dialog.standing_check.isChecked() is False
    assert dialog.recumbent_check.isChecked() is False
    assert dialog.sitting_check.isChecked() is True
    assert dialog.shadow_check.isChecked() is False
    assert dialog.terrain_check.isChecked() is False


def test_defaults_when_nothing_saved(app, qtbot, isolated_settings):
    dialog = _make_dialog(qtbot)
    # Matches the historical widget defaults.
    assert dialog.size_combo.currentData() == 'average_adult'
    assert dialog.standing_check.isChecked() is True
    assert dialog.recumbent_check.isChecked() is True
    assert dialog.sitting_check.isChecked() is False
    assert dialog.shadow_check.isChecked() is True
    assert dialog.terrain_check.isChecked() is True


def test_default_anchor_is_nadir(app, qtbot, isolated_settings):
    """The overlay opens at the straight-down point, not the zoomed view centre."""
    from core.services.CameraModel import CameraModel

    dialog = _make_dialog(qtbot)
    dialog.camera = CameraModel(50.0, -90.0, 0.0, 8.38, 13.2, 8.8, 5472, 3078)
    point = dialog._default_anchor_scene()
    assert point.x() == pytest.approx(5472 / 2.0, abs=1.0)
    assert point.y() == pytest.approx(3078 / 2.0, abs=1.0)


def test_is_near_nadir_gates_on_pitch(app, qtbot, isolated_settings):
    from core.services.CameraModel import CameraModel

    dialog = _make_dialog(qtbot)
    dialog.camera = CameraModel(50.0, -89.0, 0.0, 8.38, 13.2, 8.8, 5472, 3078)
    assert dialog._is_near_nadir() is True
    dialog.camera = CameraModel(50.0, -45.0, 0.0, 8.38, 13.2, 8.8, 5472, 3078)
    assert dialog._is_near_nadir() is False


def test_recenter_returns_to_nadir(app, qtbot, isolated_settings):
    """Recenter must snap back to the nadir, not the zoomed viewport centre."""
    from core.services.CameraModel import CameraModel
    from core.views.images.viewer.dialogs.PersonReferenceDialog import (
        _AnchorHandle,
    )

    dialog = _make_dialog(qtbot)
    dialog.camera = CameraModel(50.0, -90.0, 0.0, 8.38, 13.2, 8.8, 5472, 3078)
    dialog.anchor_item = _AnchorHandle(dialog)
    dialog.anchor_item.setPos(10.0, 10.0)  # simulate an off-nadir position

    dialog._recenter()

    assert dialog.anchor_item.pos().x() == pytest.approx(5472 / 2.0, abs=1.0)
    assert dialog.anchor_item.pos().y() == pytest.approx(3078 / 2.0, abs=1.0)


def test_persists_on_change(app, qtbot, isolated_settings):
    dialog = _make_dialog(qtbot)

    dialog.sitting_check.setChecked(True)
    dialog.standing_check.setChecked(False)
    dialog.shadow_check.setChecked(False)
    dialog.size_combo.setCurrentIndex(
        dialog.size_combo.findData('small_child'))

    # A fresh service reads the values back from the temp INI.
    reread = SettingsService()
    assert reread.get_bool_setting(SETTING_SHOW_SITTING) is True
    assert reread.get_bool_setting(SETTING_SHOW_STANDING) is False
    assert reread.get_bool_setting(SETTING_SHOW_SHADOWS) is False
    assert reread.get_setting(SETTING_SIZE_KEY) == 'small_child'
