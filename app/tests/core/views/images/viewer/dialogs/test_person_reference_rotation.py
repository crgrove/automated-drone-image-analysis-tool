"""Tests for the person-size tool's drag-to-rotate handle."""

from unittest.mock import MagicMock

import pytest
from PySide6 import QtCore

from core.services.CameraModel import CameraModel
from core.views.images.viewer.dialogs.PersonReferenceDialog import (
    PersonReferenceDialog,
    _AnchorHandle,
    _RotationHandle,
    person_rotation_from_ground_vector,
)


def _make_dialog(qtbot):
    """Dialog with a real nadir camera and a real anchor at image centre."""
    image_service = MagicMock()
    image_service.get_camera_intrinsics.return_value = None
    viewer = MagicMock()
    dialog = PersonReferenceDialog(
        None, viewer, image_service, 'does-not-exist.jpg', 'ft')
    qtbot.addWidget(dialog)

    dialog.camera = CameraModel(50.0, -90.0, 0.0, 8.38, 13.2, 8.8, 5472, 3078)
    dialog.anchor_item = _AnchorHandle(dialog)
    dialog.anchor_item.setPos(QtCore.QPointF(2736.0, 1539.0))
    dialog.rotation_handle_item = _RotationHandle(dialog)
    return dialog


# ---------------------------------------------------------------------------
# Pure helper
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("d_north,d_east,expected", [
    (1.0, 0.0, 0.0),      # due north
    (0.0, 1.0, 90.0),     # due east
    (-1.0, 0.0, 180.0),   # due south
    (0.0, -1.0, 270.0),   # due west
])
def test_ground_vector_headings(d_north, d_east, expected):
    assert person_rotation_from_ground_vector(d_north, d_east) == pytest.approx(expected)


def test_ground_vector_offset_wraps_through_zero():
    # Heading 10 with a grab offset of 30 wraps to 340, not -20.
    assert person_rotation_from_ground_vector(
        1.0, 0.17632698, offset_deg=40.0) == pytest.approx(330.0, abs=0.5)


# ---------------------------------------------------------------------------
# Orbit geometry: dragging to where the handle already sits keeps the angle
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("rotation", [0, 45, 137, 270, 359])
def test_orbit_position_round_trips_through_heading(app, qtbot, rotation):
    dialog = _make_dialog(qtbot)
    dialog.rotation_deg = rotation

    orbit = dialog._rotation_handle_orbit_pos()
    assert orbit is not None
    heading = dialog._heading_at_scene_pos(orbit)
    assert heading == pytest.approx(rotation, abs=0.6)


def test_drag_to_new_bearing_updates_rotation_and_spinbox(app, qtbot):
    dialog = _make_dialog(qtbot)
    dialog.rotation_deg = 0
    dialog.rotation_spin.setValue(0)

    # Target: where the orbit sits when the rotation is 90 degrees.
    dialog.rotation_deg = 90
    target = dialog._rotation_handle_orbit_pos()
    dialog.rotation_deg = 0

    fired = []
    dialog.rotation_spin.valueChanged.connect(fired.append)
    constrained = dialog._on_rotation_handle_dragged(target, 0.0)

    assert dialog.rotation_deg == 90
    assert dialog.rotation_spin.value() == 90
    assert fired == [], "spinbox sync must not re-trigger the change handler"
    assert constrained is not None
    assert constrained.x() == pytest.approx(target.x(), abs=1.0)
    assert constrained.y() == pytest.approx(target.y(), abs=1.0)


def test_grab_offset_prevents_jump(app, qtbot):
    dialog = _make_dialog(qtbot)
    dialog.rotation_deg = 30

    # Dragging back onto the 30-degree orbit with the matching grab offset
    # of 0 keeps the rotation identical (no snap at drag start).
    orbit = dialog._rotation_handle_orbit_pos()
    dialog._on_rotation_handle_dragged(orbit, 0.0)
    assert dialog.rotation_deg == 30


def test_unresolvable_drag_keeps_previous_rotation(app, qtbot):
    dialog = _make_dialog(qtbot)
    dialog.rotation_deg = 42
    dialog.camera = None  # heading can no longer be computed

    constrained = dialog._on_rotation_handle_dragged(QtCore.QPointF(0, 0), 0.0)
    assert dialog.rotation_deg == 42
    assert constrained is None  # no orbit either; move left unconstrained


def test_spinbox_change_reseats_handle(app, qtbot):
    dialog = _make_dialog(qtbot)
    dialog.pose_items = {}
    dialog.shadow_item = None

    dialog._on_rotation_changed(0)
    pos_at_0 = dialog.rotation_handle_item.pos()
    dialog._on_rotation_changed(180)
    pos_at_180 = dialog.rotation_handle_item.pos()

    assert (pos_at_0 - pos_at_180).manhattanLength() > 1.0


def test_handle_hidden_without_camera(app, qtbot):
    dialog = _make_dialog(qtbot)
    dialog.camera = None
    dialog._position_rotation_handle()
    assert not dialog.rotation_handle_item.isVisible()


def test_clear_items_removes_rotation_handle(app, qtbot):
    dialog = _make_dialog(qtbot)
    dialog._clear_items()
    assert dialog.rotation_handle_item is None
