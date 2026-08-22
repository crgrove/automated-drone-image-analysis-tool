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


# ---------------------------------------------------------------------------
# Auto-zoom to a sub-visible reference person (high-altitude imagery)
# ---------------------------------------------------------------------------

import numpy as np
from types import SimpleNamespace

from core.views.images.viewer.dialogs.PersonReferenceDialog import (
    MIN_LEGIBLE_SCREEN_PX,
)


class _StubViewer:
    """Viewer stand-in: identity scene->screen mapping, records zooms."""

    def __init__(self):
        self.scene = MagicMock()
        self.zoom_calls = []

    def mapFromScene(self, rect):
        result = MagicMock()
        result.boundingRect.return_value = QtCore.QRect(
            0, 0, int(rect.width()), int(rect.height()))
        return result

    def zoomToRect(self, rect):
        self.zoom_calls.append(QtCore.QRectF(rect))


def _camera_image_service(agl_m):
    """Image service stub yielding a real CameraModel at the given AGL."""
    return SimpleNamespace(
        get_camera_intrinsics=lambda: {
            'focal_length_mm': 50.0,
            'sensor_width_mm': 36.0,
            'sensor_height_mm': 24.0,
        },
        get_relative_altitude=lambda unit: agl_m,
        get_camera_pitch=lambda: -90.0,
        get_camera_yaw=lambda: 0.0,
        img_array=np.zeros((579, 869, 3), dtype=np.uint8),
    )


def _make_projected_dialog(qtbot, agl_m):
    viewer = _StubViewer()
    dialog = PersonReferenceDialog(
        None, viewer, _camera_image_service(agl_m), 'does-not-exist.jpg', 'ft')
    qtbot.addWidget(dialog)
    return dialog, viewer


def test_auto_zooms_when_person_is_sub_visible(app, qtbot, isolated_settings):
    """High-altitude imagery (WALDO-style): the ~1px person gets framed."""
    dialog, viewer = _make_projected_dialog(qtbot, agl_m=1500.0)

    assert dialog.camera is not None
    assert len(viewer.zoom_calls) == 1
    target = viewer.zoom_calls[0]
    # The zoom target frames the silhouette bounds
    bounds = dialog._reference_bounds_scene()
    assert bounds is not None
    assert target.contains(bounds.center())
    assert target.width() >= 80.0


def test_no_auto_zoom_when_person_is_legible(app, qtbot, isolated_settings):
    """Drone-altitude imagery: the person is tens of pixels tall; no zoom."""
    dialog, viewer = _make_projected_dialog(qtbot, agl_m=40.0)

    assert dialog.camera is not None
    bounds = dialog._reference_bounds_scene()
    assert bounds is not None
    assert max(bounds.width(), bounds.height()) >= MIN_LEGIBLE_SCREEN_PX
    assert viewer.zoom_calls == []


def test_auto_zoom_failure_is_non_fatal(app, qtbot, isolated_settings):
    """A viewer without zoom support must not break the overlay."""
    viewer = _StubViewer()
    del viewer.zoom_calls
    viewer.zoomToRect = None  # not callable -> raises inside the guard

    dialog = PersonReferenceDialog(
        None, viewer, _camera_image_service(1500.0), 'does-not-exist.jpg', 'ft')
    qtbot.addWidget(dialog)

    assert dialog.camera is not None  # dialog still built the overlay
