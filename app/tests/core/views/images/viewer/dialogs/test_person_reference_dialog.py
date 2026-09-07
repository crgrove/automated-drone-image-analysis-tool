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


def test_default_anchor_is_current_view_center(app, qtbot, isolated_settings):
    """The overlay opens where the user is looking, not at the image centre
    (field report: opening while zoomed to an AOI panned the view away)."""
    from types import SimpleNamespace as _NS
    from core.services.CameraModel import CameraModel

    dialog = _make_dialog(qtbot)
    dialog.camera = CameraModel(50.0, -90.0, 0.0, 8.38, 13.2, 8.8, 5472, 3078)
    dialog.image_viewer.viewport = lambda: _NS(
        rect=lambda: QtCore.QRect(0, 0, 400, 300))
    dialog.image_viewer.mapToScene = lambda p: QtCore.QPointF(1200.0, 800.0)
    point = dialog._default_anchor_scene()
    assert point.x() == pytest.approx(1200.0)
    assert point.y() == pytest.approx(800.0)


def test_default_anchor_falls_back_to_nadir(app, qtbot, isolated_settings):
    """With no usable view centre the overlay opens at the straight-down
    point (compact, upright silhouette at any camera angle)."""
    from core.services.CameraModel import CameraModel

    dialog = _make_dialog(qtbot)
    dialog.camera = CameraModel(50.0, -90.0, 0.0, 8.38, 13.2, 8.8, 5472, 3078)
    dialog.image_viewer.mapToScene = None  # not callable -> raises
    dialog.image_viewer.sceneRect = None   # fallback path raises too
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


def test_recenter_falls_back_to_nadir_without_a_view_center(app, qtbot,
                                                            isolated_settings):
    """When the viewport centre can't be determined at all, Recenter falls
    back to the default nadir placement instead of breaking."""
    from core.services.CameraModel import CameraModel
    from core.views.images.viewer.dialogs.PersonReferenceDialog import (
        _AnchorHandle,
    )

    dialog = _make_dialog(qtbot)
    dialog.camera = CameraModel(50.0, -90.0, 0.0, 8.38, 13.2, 8.8, 5472, 3078)
    dialog.image_viewer.mapToScene = None  # not callable -> raises
    dialog.image_viewer.sceneRect = None   # fallback path raises too
    dialog.anchor_item = _AnchorHandle(dialog)
    dialog.anchor_item.setPos(10.0, 10.0)  # simulate an off-nadir position

    dialog._recenter()

    assert dialog.anchor_item.pos().x() == pytest.approx(5472 / 2.0, abs=1.0)
    assert dialog.anchor_item.pos().y() == pytest.approx(3078 / 2.0, abs=1.0)


def test_recenter_moves_to_current_view_center(app, qtbot, isolated_settings):
    """Recenter pulls the person to where the user is currently looking
    (field request: it used to jump back to the full-image default)."""
    from types import SimpleNamespace as _NS
    from core.services.CameraModel import CameraModel
    from core.views.images.viewer.dialogs.PersonReferenceDialog import (
        _AnchorHandle,
    )

    dialog = _make_dialog(qtbot)
    dialog.camera = CameraModel(50.0, -90.0, 0.0, 8.38, 13.2, 8.8, 5472, 3078)
    # Simulate a zoomed/panned viewer whose viewport centre is (1200, 800).
    dialog.image_viewer.viewport = lambda: _NS(
        rect=lambda: QtCore.QRect(0, 0, 400, 300))
    dialog.image_viewer.mapToScene = lambda p: QtCore.QPointF(1200.0, 800.0)
    dialog.anchor_item = _AnchorHandle(dialog)
    dialog.anchor_item.setPos(10.0, 10.0)

    dialog._recenter()

    assert dialog.anchor_item.pos().x() == pytest.approx(1200.0)
    assert dialog.anchor_item.pos().y() == pytest.approx(800.0)


def test_recenter_clamps_to_image_bounds(app, qtbot, isolated_settings):
    """A viewport centre outside the image cannot fling the person off-frame."""
    from types import SimpleNamespace as _NS
    from core.services.CameraModel import CameraModel
    from core.views.images.viewer.dialogs.PersonReferenceDialog import (
        _AnchorHandle,
    )

    dialog = _make_dialog(qtbot)
    dialog.camera = CameraModel(50.0, -90.0, 0.0, 8.38, 13.2, 8.8, 5472, 3078)
    dialog.image_viewer.viewport = lambda: _NS(
        rect=lambda: QtCore.QRect(0, 0, 400, 300))
    dialog.image_viewer.mapToScene = lambda p: QtCore.QPointF(-500.0, 99999.0)
    dialog.anchor_item = _AnchorHandle(dialog)

    dialog._recenter()

    assert dialog.anchor_item.pos().x() == pytest.approx(0.0)
    assert dialog.anchor_item.pos().y() == pytest.approx(3078.0)


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


# ---------------------------------------------------------------------------
# Shadow trace -> time of day (the traced shadow drives the sun rendering)
# ---------------------------------------------------------------------------

import math
from datetime import datetime, timezone

_TRACE_LAT, _TRACE_LON = 36.8, -118.2


def _patch_sun_metadata(monkeypatch, claimed_utc):
    """Make the dialog resolve GPS + capture time without touching disk."""
    import core.views.images.viewer.dialogs.PersonReferenceDialog as dlg_mod
    monkeypatch.setattr(dlg_mod, 'MetaDataHelper', SimpleNamespace(
        get_exif_data_piexif=lambda path: {},
        get_xmp_data=lambda path, parse=True: None))
    monkeypatch.setattr(dlg_mod, 'LocationInfo', SimpleNamespace(
        get_gps=lambda exif_data: {'latitude': _TRACE_LAT,
                                   'longitude': _TRACE_LON}))
    monkeypatch.setattr(
        dlg_mod, 'resolve_capture_utc',
        lambda exif, xmp, lat=None, lon=None: (claimed_utc, 'gps'))


def _solved_trace_dialog(qtbot, monkeypatch, truth, claimed):
    """Dialog with a completed shadow trace built from the real sun at ``truth``."""
    from core.services.shadow.SolarPosition import get_solar_position

    _patch_sun_metadata(monkeypatch, claimed)
    dialog, _viewer = _make_projected_dialog(qtbot, agl_m=40.0)
    assert dialog.trace_shadow_button.isEnabled()

    # The camera is nadir with yaw 0, so image +u = east and +v = south.
    # Trace the shadow a real sun at ``truth`` would cast.
    _elev, sun_az = get_solar_position(_TRACE_LAT, _TRACE_LON, truth)
    shadow_rad = math.radians((sun_az + 180.0) % 360.0)
    base = (434.0, 289.0)  # ~image centre = ground nadir
    tip = (base[0] + 100.0 * math.sin(shadow_rad),
           base[1] - 100.0 * math.cos(shadow_rad))

    dialog._trace_active = True
    dialog._on_trace_click(*base)
    assert dialog._trace_override_utc is None  # one click is not enough
    dialog._on_trace_click(*tip)
    return dialog, sun_az


def test_shadow_trace_solves_and_applies_time(app, qtbot, isolated_settings,
                                              monkeypatch):
    truth = datetime(2026, 6, 15, 17, 0, tzinfo=timezone.utc)    # 10:00 PDT
    claimed = datetime(2026, 6, 15, 22, 0, tzinfo=timezone.utc)  # clock wrong
    dialog, sun_az = _solved_trace_dialog(qtbot, monkeypatch, truth, claimed)

    assert dialog._trace_override_utc is not None
    assert abs((dialog._trace_override_utc - truth).total_seconds()) < 300
    assert dialog.sun_time_source == 'shadow_trace'
    # The rendered sun now matches the traced moment, not the camera clock.
    assert dialog.sun_az == pytest.approx(sun_az, abs=2.0)
    assert dialog.trace_shadow_button.text() == 'Clear traced time'


def test_shadow_trace_clear_restores_clock_time(app, qtbot, isolated_settings,
                                                monkeypatch):
    truth = datetime(2026, 6, 15, 17, 0, tzinfo=timezone.utc)
    claimed = datetime(2026, 6, 15, 22, 0, tzinfo=timezone.utc)
    dialog, _sun_az = _solved_trace_dialog(qtbot, monkeypatch, truth, claimed)
    assert dialog.sun_time_source == 'shadow_trace'

    dialog._on_trace_shadow_clicked()  # "Clear traced time"

    assert dialog._trace_override_utc is None
    assert dialog.sun_time_source == 'gps'
    assert dialog.trace_shadow_button.text() == 'Trace shadow...'
    assert dialog._trace_items == []


def test_shadow_trace_disabled_without_camera(app, qtbot, isolated_settings,
                                              monkeypatch):
    """No camera model (missing metadata) -> the trace button stays off."""
    claimed = datetime(2026, 6, 15, 22, 0, tzinfo=timezone.utc)
    _patch_sun_metadata(monkeypatch, claimed)
    dialog = _make_dialog(qtbot)  # null-camera mock
    assert dialog.camera is None
    assert not dialog.trace_shadow_button.isEnabled()


def test_trace_toggles_viewer_point_capture(app, qtbot, isolated_settings,
                                            monkeypatch):
    """Arming the trace must put the image viewer in point-capture mode:
    on the main image the left button region-zooms, so without capture the
    trace clicks never reach the dialog (field-reported bug)."""
    claimed = datetime(2026, 6, 15, 22, 0, tzinfo=timezone.utc)
    _patch_sun_metadata(monkeypatch, claimed)
    dialog, viewer = _make_projected_dialog(qtbot, agl_m=40.0)
    calls = []
    viewer.leftMouseButtonPressed = MagicMock()  # connectable stand-in
    viewer.begin_point_capture = lambda: calls.append('begin')
    viewer.end_point_capture = lambda: calls.append('end')

    dialog._begin_trace()
    assert dialog._trace_active
    assert calls == ['begin']

    dialog._end_trace(cancelled=True)
    assert calls == ['begin', 'end']


def test_shadow_trace_reset_on_image_change(app, qtbot, isolated_settings,
                                            monkeypatch):
    """Switching images drops the traced time (it belongs to one frame)."""
    truth = datetime(2026, 6, 15, 17, 0, tzinfo=timezone.utc)
    claimed = datetime(2026, 6, 15, 22, 0, tzinfo=timezone.utc)
    dialog, _sun_az = _solved_trace_dialog(qtbot, monkeypatch, truth, claimed)
    assert dialog._trace_override_utc is not None

    dialog.update_for_image(_camera_image_service(40.0), 'other-image.jpg')
    dialog._apply_pending_image()  # flush the deferred rebuild

    assert dialog._trace_override_utc is None
    assert dialog.sun_time_source == 'gps'
    assert dialog.trace_shadow_button.text() == 'Trace shadow...'


# ---------------------------------------------------------------------------
# Anchor placement avoids the selected AOI (radius + 40 px clearance)
# ---------------------------------------------------------------------------

def _viewer_with_selected_aoi(center, radius, aoi_index=0):
    """Minimal parent-viewer stand-in exposing one selected AOI."""
    return SimpleNamespace(
        aoi_controller=SimpleNamespace(selected_aoi_index=aoi_index),
        images=[{'areas_of_interest': [{'center': center, 'radius': radius}]}],
        current_image=0,
    )


def _dialog_with_view_center(qtbot, view_center):
    from types import SimpleNamespace as _NS
    from core.services.CameraModel import CameraModel

    dialog = _make_dialog(qtbot)
    dialog.camera = CameraModel(50.0, -90.0, 0.0, 8.38, 13.2, 8.8, 5472, 3078)
    dialog.image_viewer.viewport = lambda: _NS(
        rect=lambda: QtCore.QRect(0, 0, 400, 300))
    dialog.image_viewer.mapToScene = lambda p: QtCore.QPointF(*view_center)
    return dialog


def test_anchor_shifts_left_of_a_centered_aoi(app, qtbot, isolated_settings):
    """View centred on the selected AOI: the person lands left of the AOI's
    radius + 40 px, level with it, instead of on top of it."""
    dialog = _dialog_with_view_center(qtbot, (1200.0, 800.0))
    dialog._parent_viewer = _viewer_with_selected_aoi((1200, 800), 30)

    point = dialog._default_anchor_scene()

    assert point.x() == pytest.approx(1200.0 - (30 + 40))
    assert point.y() == pytest.approx(800.0)


def test_anchor_shifts_right_when_left_is_off_image(app, qtbot,
                                                    isolated_settings):
    """An AOI near the left edge pushes the person to its right instead."""
    dialog = _dialog_with_view_center(qtbot, (50.0, 800.0))
    dialog._parent_viewer = _viewer_with_selected_aoi((50, 800), 30)

    point = dialog._default_anchor_scene()

    assert point.x() == pytest.approx(50.0 + (30 + 40))
    assert point.y() == pytest.approx(800.0)


def test_anchor_unmoved_when_view_is_not_on_the_aoi(app, qtbot,
                                                    isolated_settings):
    """A view centred far from the selected AOI keeps its own centre."""
    dialog = _dialog_with_view_center(qtbot, (2000.0, 1500.0))
    dialog._parent_viewer = _viewer_with_selected_aoi((1200, 800), 30)

    point = dialog._default_anchor_scene()

    assert point.x() == pytest.approx(2000.0)
    assert point.y() == pytest.approx(1500.0)


def test_anchor_unmoved_without_a_selected_aoi(app, qtbot, isolated_settings):
    dialog = _dialog_with_view_center(qtbot, (1200.0, 800.0))
    dialog._parent_viewer = _viewer_with_selected_aoi((1200, 800), 30,
                                                      aoi_index=-1)

    point = dialog._default_anchor_scene()

    assert point.x() == pytest.approx(1200.0)
    assert point.y() == pytest.approx(800.0)


# ---------------------------------------------------------------------------
# Image-change rebuilds defer so navigation (gallery zoom-to-AOI) wins
# ---------------------------------------------------------------------------

def test_image_change_rebuilds_immediately(app, qtbot, isolated_settings):
    """The rebuild runs inline, because the caller already arrived at the
    right moment.

    This used to be deferred 300 ms so an in-flight navigation could land
    first. The Viewer now calls in as the load pipeline's final step - after
    the zoom the navigation requested - so there is nothing left to wait
    for, and waiting a fixed 300 ms was only ever right on some machines.
    """
    dialog, _viewer = _make_projected_dialog(qtbot, agl_m=40.0)
    assert dialog.anchor_item is not None

    dialog.update_for_image(_camera_image_service(40.0), 'other-image.jpg')

    assert dialog._pending_image is None        # consumed, not queued
    assert dialog.anchor_item is not None       # rebuilt for the new image
    assert dialog.image_path == 'other-image.jpg'


def test_image_change_never_auto_zooms(app, qtbot, isolated_settings):
    """A gallery AOI click zooms the new image to the AOI; the dialog's
    legibility auto-zoom must not stomp it (field report). The auto-zoom
    belongs to the FIRST open only - once the dialog is up, an image
    change is the operator's own navigation and the view stays put."""
    dialog, viewer = _make_projected_dialog(qtbot, agl_m=1500.0)
    assert len(viewer.zoom_calls) == 1  # auto-zoomed once on open

    dialog.update_for_image(_camera_image_service(1500.0), 'other-image.jpg')
    dialog._apply_pending_image()

    assert len(viewer.zoom_calls) == 1  # no second auto-zoom, ever


def test_pending_image_change_dropped_on_close(app, qtbot, isolated_settings):
    """A rebuild must not run into a closed dialog.

    It would re-add overlay items nothing would ever remove. The request is
    still held between the two halves, so closing has to clear it - and a
    stray apply afterwards has to be a no-op.
    """
    dialog, _viewer = _make_projected_dialog(qtbot, agl_m=40.0)
    dialog._pending_image = (_camera_image_service(40.0), 'other-image.jpg', None)

    dialog.close()

    assert dialog._pending_image is None
    dialog._apply_pending_image()  # stray fire is a no-op
    assert dialog.anchor_item is None
