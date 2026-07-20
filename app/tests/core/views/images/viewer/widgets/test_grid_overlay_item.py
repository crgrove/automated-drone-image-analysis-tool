"""Tests for the grid review on-image overlay and cell zoom."""

from unittest.mock import MagicMock

from PySide6.QtCore import QRectF
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtWidgets import QGraphicsScene, QStyleOptionGraphicsItem

from core.views.images.viewer.widgets.GridOverlayItem import GridOverlayItem
from core.views.images.viewer.widgets.QtImageViewer import QtImageViewer


# ---------------------------------------------------------------------------
# GridOverlayItem
# ---------------------------------------------------------------------------

def test_grid_overlay_hidden_until_configured(app):
    item = GridOverlayItem()
    assert not item.isVisible()
    assert item.boundingRect().isEmpty()


def test_grid_overlay_bounding_rect_matches_image(app):
    item = GridOverlayItem()
    item.configure(8000, 6000, 4, 4, set(), None)
    assert item.boundingRect() == QRectF(0, 0, 8000, 6000)


def test_grid_overlay_cell_rect_lookup(app):
    item = GridOverlayItem()
    item.configure(100, 100, 2, 2, set(), None)
    assert item.cell_rect(0) == (0, 0, 50, 50)
    assert item.cell_rect(3) == (50, 50, 50, 50)
    assert item.cell_rect(4) is None
    assert item.cell_rect(None) is None
    assert item.cell_rect(-1) is None


def test_grid_overlay_lives_in_a_scene(app):
    scene = QGraphicsScene()
    item = GridOverlayItem()
    scene.addItem(item)
    item.configure(640, 480, 3, 3, {0, 4}, 5)
    assert item.scene() is scene


def test_grid_overlay_paint_smoke(app):
    """Configured overlay paints reviewed + current cells without error."""
    item = GridOverlayItem()
    item.configure(400, 300, 4, 4, {0, 1, 5}, 6)

    pixmap = QPixmap(400, 300)
    painter = QPainter(pixmap)
    try:
        item.paint(painter, QStyleOptionGraphicsItem(), None)
    finally:
        painter.end()


def test_grid_overlay_focus_guide_defaults_and_paints(app):
    """The 3x3 focus guide defaults on and paints inside the active cell."""
    item = GridOverlayItem()
    item.configure(400, 300, 4, 4, set(), 5)
    assert item._subdivisions == 3

    pixmap = QPixmap(400, 300)
    painter = QPainter(pixmap)
    try:
        item.paint(painter, QStyleOptionGraphicsItem(), None)
    finally:
        painter.end()


def test_grid_overlay_focus_guide_can_be_disabled(app):
    """subdivisions=1 disables the guide; painting still succeeds."""
    item = GridOverlayItem()
    item.configure(400, 300, 4, 4, set(), 5, subdivisions=1)
    assert item._subdivisions == 1
    item.set_subdivisions(3)
    assert item._subdivisions == 3
    # Clamps degenerate values up to 1.
    item.set_subdivisions(0)
    assert item._subdivisions == 1

    pixmap = QPixmap(400, 300)
    painter = QPainter(pixmap)
    try:
        item.paint(painter, QStyleOptionGraphicsItem(), None)
    finally:
        painter.end()


def test_grid_overlay_paint_unconfigured_is_noop(app):
    item = GridOverlayItem()
    pixmap = QPixmap(50, 50)
    painter = QPainter(pixmap)
    try:
        item.paint(painter, QStyleOptionGraphicsItem(), None)
    finally:
        painter.end()


def test_grid_overlay_partial_updates(app):
    item = GridOverlayItem()
    item.configure(100, 100, 2, 2, set(), 0)
    item.set_reviewed({0, 1})
    item.set_current_index(2)
    assert item._reviewed == {0, 1}
    assert item._current_index == 2


def test_grid_overlay_reconfigure_for_new_image(app):
    """Reconfiguring for a different image replaces geometry and state."""
    item = GridOverlayItem()
    item.configure(100, 100, 2, 2, {0}, 1)
    item.configure(200, 100, 1, 2, {1}, 0)
    assert item.boundingRect() == QRectF(0, 0, 200, 100)
    assert item.cell_rect(0) == (0, 0, 100, 100)
    assert item.cell_rect(2) is None


# ---------------------------------------------------------------------------
# QtImageViewer.zoomToRect
# ---------------------------------------------------------------------------

def _viewer_with_image(width=800, height=600):
    viewer = QtImageViewer(MagicMock())
    viewer.resize(400, 300)
    viewer.setImage(QPixmap(width, height))
    return viewer


def test_zoom_to_rect_replaces_zoom_stack(app):
    viewer = _viewer_with_image()
    viewer.zoomStack = [QRectF(0, 0, 800, 600), QRectF(10, 10, 100, 100)]

    viewer.zoomToRect(QRectF(200, 150, 400, 300))

    assert len(viewer.zoomStack) == 1
    assert viewer.zoomStack[0] == QRectF(200, 150, 400, 300)


def test_zoom_to_rect_clips_to_scene(app):
    viewer = _viewer_with_image()
    viewer.zoomToRect(QRectF(600, 400, 400, 400))

    assert len(viewer.zoomStack) == 1
    assert viewer.zoomStack[0] == QRectF(600, 400, 200, 200)


def test_zoom_to_rect_rejects_degenerate_rect(app):
    viewer = _viewer_with_image()
    viewer.zoomToRect(QRectF(0, 0, 2, 2))
    assert viewer.zoomStack == []
    viewer.zoomToRect(QRectF())
    assert viewer.zoomStack == []


def test_zoom_to_rect_without_image_is_noop(app):
    viewer = QtImageViewer(MagicMock())
    viewer.zoomToRect(QRectF(0, 0, 100, 100))
    assert viewer.zoomStack == []
