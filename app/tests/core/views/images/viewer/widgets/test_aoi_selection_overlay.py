"""Tests for the selected-AOI on-image overlay (number badge + ruler)."""

import pytest
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtWidgets import QStyleOptionGraphicsItem

from core.views.images.viewer.widgets.AOISelectionOverlay import (
    AOISelectionOverlay, build_ruler_model, compute_ruler_ticks,
    ruler_angle_from_drag,
)


# ---------------------------------------------------------------------------
# compute_ruler_ticks
# ---------------------------------------------------------------------------

def test_compute_ruler_ticks_empty_for_non_positive_width():
    assert compute_ruler_ticks(0) == []
    assert compute_ruler_ticks(-1) == []
    assert compute_ruler_ticks(None) == []


def test_compute_ruler_ticks_classifies_one_unit():
    """A 1-unit ruler has major ends, a medium centre and minor quarters."""
    assert compute_ruler_ticks(1.0) == [
        (0.0, 'major'),
        (0.25, 'minor'),
        (0.5, 'medium'),
        (0.75, 'minor'),
        (1.0, 'major'),
    ]


def test_compute_ruler_ticks_stops_at_width():
    """Ticks never run past the ruler's end."""
    positions = [pos for pos, _ in compute_ruler_ticks(2.6)]
    assert max(positions) == 2.5
    assert all(pos <= 2.6 for pos in positions)


def test_compute_ruler_ticks_major_on_whole_units():
    ticks = dict(compute_ruler_ticks(3.0))
    assert ticks[0.0] == 'major'
    assert ticks[1.0] == 'major'
    assert ticks[2.0] == 'major'
    assert ticks[3.0] == 'major'
    assert ticks[1.5] == 'medium'
    assert ticks[2.25] == 'minor'


# ---------------------------------------------------------------------------
# build_ruler_model
# ---------------------------------------------------------------------------

def test_build_ruler_model_none_without_gsd():
    """No ground sample distance means the ruler cannot be built."""
    assert build_ruler_model(100, None, 'Feet') is None
    assert build_ruler_model(100, 0, 'Feet') is None


def test_build_ruler_model_none_without_radius():
    assert build_ruler_model(0, 2.5, 'Feet') is None


def test_build_ruler_model_feet():
    """A 100 px radius at 2 cm/px is a 4 m (~13.12 ft) wide AOI."""
    model = build_ruler_model(100, 2.0, 'Feet')
    assert model['unit_label'] == 'ft'
    assert model['width_units'] == pytest.approx(13.123, abs=0.01)
    # 0.3048 m per foot / 0.02 m per px == 15.24 px per foot.
    assert model['pixels_per_unit'] == pytest.approx(15.24, abs=0.01)
    assert model['width_text'] == '13.12 ft'
    assert model['ticks'][0] == (0.0, 'major')


def test_build_ruler_model_meters():
    """The same AOI is 4.00 m wide when the preference is metric."""
    model = build_ruler_model(100, 2.0, 'Meters')
    assert model['unit_label'] == 'm'
    assert model['width_units'] == pytest.approx(4.0, abs=1e-6)
    assert model['pixels_per_unit'] == pytest.approx(50.0, abs=1e-6)
    assert model['width_text'] == '4.00 m'


def test_build_ruler_model_accepts_legacy_unit_strings():
    """Legacy 'ft'/'m' unit strings work like 'Feet'/'Meters'."""
    assert build_ruler_model(100, 2.0, 'ft')['unit_label'] == 'ft'
    assert build_ruler_model(100, 2.0, 'm')['unit_label'] == 'm'


def test_build_ruler_model_ruler_spans_the_diameter():
    """width_units * pixels_per_unit equals the AOI diameter in pixels."""
    model = build_ruler_model(80, 3.3, 'Feet')
    diameter_px = model['width_units'] * model['pixels_per_unit']
    assert diameter_px == pytest.approx(160.0, abs=1e-6)


# ---------------------------------------------------------------------------
# AOISelectionOverlay graphics item
# ---------------------------------------------------------------------------

def test_overlay_item_hidden_until_configured(app):
    item = AOISelectionOverlay()
    assert not item.isVisible()
    assert item.boundingRect().isEmpty()


def test_overlay_item_paints_number_and_ruler(app):
    """A configured overlay paints without error and has a bounding rect."""
    item = AOISelectionOverlay()
    item.configure((100.0, 120.0), 80, 7, build_ruler_model(80, 2.5, 'Feet'))

    assert item.boundingRect().width() > 0
    assert item.pos().x() == 100.0 and item.pos().y() == 120.0

    pixmap = QPixmap(400, 400)
    painter = QPainter(pixmap)
    try:
        item.paint(painter, QStyleOptionGraphicsItem(), None)
    finally:
        painter.end()


def test_overlay_item_paints_number_only_without_ruler(app):
    """With no ruler model the overlay still paints the number badge."""
    item = AOISelectionOverlay()
    item.configure((50.0, 50.0), 40, 12, None)

    pixmap = QPixmap(200, 200)
    painter = QPainter(pixmap)
    try:
        item.paint(painter, QStyleOptionGraphicsItem(), None)
    finally:
        painter.end()


# ---------------------------------------------------------------------------
# ruler_angle_from_drag
# ---------------------------------------------------------------------------

def test_ruler_angle_from_drag_zero_below_centre():
    """A cursor straight below the AOI keeps the ruler horizontal."""
    assert ruler_angle_from_drag(0.0, 10.0) == pytest.approx(0.0)


def test_ruler_angle_from_drag_clamps_to_90():
    """Dragging far to either side clamps the ruler to +/- 90 degrees."""
    assert ruler_angle_from_drag(10.0, 0.0) == pytest.approx(-90.0)
    assert ruler_angle_from_drag(-10.0, 0.0) == pytest.approx(90.0)


def test_ruler_angle_from_drag_respects_grab_offset():
    """The grab offset keeps the ruler from jumping when the handle is seized."""
    # Offset equal to the cursor angle -> the ruler holds at 0.
    assert ruler_angle_from_drag(10.0, 10.0, offset=45.0) == pytest.approx(0.0)


def test_ruler_angle_from_drag_handles_zero_vector():
    assert ruler_angle_from_drag(0.0, 0.0) == 0.0


# ---------------------------------------------------------------------------
# AOISelectionOverlay ruler rotation
# ---------------------------------------------------------------------------

def test_overlay_item_set_ruler_angle_clamps(app):
    item = AOISelectionOverlay()
    item.set_ruler_angle(45.0)
    assert item.ruler_angle() == 45.0
    item.set_ruler_angle(200.0)
    assert item.ruler_angle() == 90.0
    item.set_ruler_angle(-200.0)
    assert item.ruler_angle() == -90.0
    item.reset_ruler_angle()
    assert item.ruler_angle() == 0.0


def test_overlay_item_configure_keeps_ruler_angle(app):
    """A refresh (configure) must not undo the user's rotation."""
    item = AOISelectionOverlay()
    item.set_ruler_angle(30.0)
    item.configure((10.0, 10.0), 50, 1, build_ruler_model(50, 2.0, 'Feet'))
    assert item.ruler_angle() == 30.0


def test_overlay_item_handle_moves_with_angle(app):
    """The grab handle's scene position changes as the ruler is rotated."""
    item = AOISelectionOverlay()
    item.configure((100.0, 100.0), 70, 4, build_ruler_model(70, 3.0, 'Meters'))

    item.set_ruler_angle(0.0)
    handle_flat = item.handle_scene_pos()
    item.set_ruler_angle(90.0)
    handle_rotated = item.handle_scene_pos()
    assert handle_flat != handle_rotated


def test_overlay_item_paints_rotated_ruler(app):
    """A rotated ruler paints without error."""
    item = AOISelectionOverlay()
    item.configure((100.0, 100.0), 70, 4, build_ruler_model(70, 3.0, 'Meters'))
    item.set_ruler_angle(60.0)
    item.set_dragging(True)

    pixmap = QPixmap(400, 400)
    painter = QPainter(pixmap)
    try:
        item.paint(painter, QStyleOptionGraphicsItem(), None)
    finally:
        painter.end()
