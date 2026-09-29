"""Tests for QtImageViewer's control schemes and context-menu signal.

classic  - left-drag = box zoom, right-drag = pan (unchanged default)
standard - left-drag = pan, Shift+left-drag = box zoom, right-click = menu
Both schemes: a right click WITHOUT a drag emits contextMenuRequested.
"""

import pytest
from PySide6.QtCore import QEvent, QPointF, QRectF, Qt
from PySide6.QtGui import QImage, QMouseEvent
from PySide6.QtWidgets import QApplication, QGraphicsEllipseItem, QGraphicsItem

from core.views.images.viewer.widgets.QtImageViewer import QtImageViewer


@pytest.fixture(scope='session')
def app():
    return QApplication.instance() or QApplication([])


class _StubWindow:
    """Minimal viewer stand-in; MagicMock would fake aoi_creation_mode truthy."""
    aoi_creation_mode = False


def _viewer(app, scheme='classic', thumbnail=False):
    viewer = QtImageViewer(_StubWindow(), thumbnail=thumbnail)
    image = QImage(800, 600, QImage.Format_RGB32)
    image.fill(Qt.gray)
    viewer.setImage(image)
    viewer.resize(400, 300)
    viewer.set_control_scheme(scheme)
    return viewer


def _mouse_event(event_type, pos, button, buttons=None, modifiers=Qt.KeyboardModifier.NoModifier):
    return QMouseEvent(
        event_type, QPointF(pos[0], pos[1]), QPointF(pos[0], pos[1]),
        button, buttons if buttons is not None else button, modifiers)


def _press(viewer, pos, button, modifiers=Qt.KeyboardModifier.NoModifier):
    viewer.mousePressEvent(_mouse_event(QEvent.Type.MouseButtonPress, pos, button, modifiers=modifiers))


def _move(viewer, pos, button):
    viewer.mouseMoveEvent(_mouse_event(QEvent.Type.MouseMove, pos, Qt.MouseButton.NoButton, buttons=button))


def _release(viewer, pos, button, modifiers=Qt.KeyboardModifier.NoModifier):
    viewer.mouseReleaseEvent(_mouse_event(QEvent.Type.MouseButtonRelease, pos, button, modifiers=modifiers))


# ---------------------------------------------------------------------------
# Scheme mapping
# ---------------------------------------------------------------------------

def test_classic_scheme_button_mapping(app):
    viewer = _viewer(app, 'classic')
    assert viewer.regionZoomButton == Qt.LeftButton
    assert viewer.panButton == Qt.RightButton


def test_standard_scheme_button_mapping(app):
    viewer = _viewer(app, 'standard')
    assert viewer.regionZoomButton is None
    assert viewer.panButton == Qt.LeftButton


def test_scheme_can_swap_back_live(app):
    viewer = _viewer(app, 'standard')
    viewer.set_control_scheme('classic')
    assert viewer.regionZoomButton == Qt.LeftButton
    assert viewer.panButton == Qt.RightButton


def test_thumbnail_viewers_ignore_scheme(app):
    viewer = QtImageViewer(_StubWindow(), thumbnail=True)
    viewer.set_control_scheme('standard')
    assert viewer.regionZoomButton == Qt.LeftButton
    assert viewer.panButton == Qt.RightButton


# ---------------------------------------------------------------------------
# Standard scheme: left-drag pans, Shift+left-drag box zooms
# ---------------------------------------------------------------------------

def test_standard_left_drag_pans_the_zoom_rect(app):
    viewer = _viewer(app, 'standard')
    viewer.zoomStack = [QRectF(200, 150, 200, 150)]
    viewer.updateViewer()
    before = QRectF(viewer.zoomStack[-1])

    _press(viewer, (100, 100), Qt.MouseButton.LeftButton)
    assert viewer._isPanning
    _move(viewer, (140, 120), Qt.MouseButton.LeftButton)
    _release(viewer, (140, 120), Qt.MouseButton.LeftButton)

    after = viewer.zoomStack[-1]
    assert not viewer._isPanning
    assert (after.x(), after.y()) != (before.x(), before.y())


def test_standard_shift_left_drag_starts_region_zoom(app):
    viewer = _viewer(app, 'standard')
    _press(viewer, (100, 100), Qt.MouseButton.LeftButton,
           modifiers=Qt.KeyboardModifier.ShiftModifier)
    assert viewer._isZooming
    assert viewer._zoomStartButton == Qt.MouseButton.LeftButton
    # Finishes even while Shift is still held
    _release(viewer, (160, 160), Qt.MouseButton.LeftButton,
             modifiers=Qt.KeyboardModifier.ShiftModifier)
    assert not viewer._isZooming


def test_classic_left_drag_still_starts_region_zoom(app):
    viewer = _viewer(app, 'classic')
    _press(viewer, (100, 100), Qt.MouseButton.LeftButton)
    assert viewer._isZooming
    _release(viewer, (160, 160), Qt.MouseButton.LeftButton)
    assert not viewer._isZooming


def test_standard_left_click_without_drag_emits_click_signals(app):
    viewer = _viewer(app, 'standard')
    viewer.zoomStack = [QRectF(200, 150, 200, 150)]
    pressed, released = [], []
    viewer.leftMouseButtonPressed.connect(lambda x, y, v: pressed.append((x, y)))
    viewer.leftMouseButtonReleased.connect(lambda x, y: released.append((x, y)))

    _press(viewer, (100, 100), Qt.MouseButton.LeftButton)
    _release(viewer, (101, 100), Qt.MouseButton.LeftButton)

    assert len(pressed) == 1
    assert len(released) == 1


# ---------------------------------------------------------------------------
# Context menu: right click without drag, both schemes
# ---------------------------------------------------------------------------

def test_classic_right_click_without_drag_requests_menu(app):
    viewer = _viewer(app, 'classic')
    requests = []
    viewer.contextMenuRequested.connect(lambda scene, gp: requests.append(scene))

    _press(viewer, (100, 100), Qt.MouseButton.RightButton)
    assert viewer._isPanning, "classic right press should arm the pan"
    _release(viewer, (101, 101), Qt.MouseButton.RightButton)

    assert len(requests) == 1


def test_classic_right_drag_does_not_request_menu(app):
    viewer = _viewer(app, 'classic')
    viewer.zoomStack = [QRectF(200, 150, 200, 150)]
    requests = []
    viewer.contextMenuRequested.connect(lambda scene, gp: requests.append(scene))

    _press(viewer, (100, 100), Qt.MouseButton.RightButton)
    _move(viewer, (150, 130), Qt.MouseButton.RightButton)
    _release(viewer, (150, 130), Qt.MouseButton.RightButton)

    assert requests == []


def test_standard_right_click_requests_menu(app):
    viewer = _viewer(app, 'standard')
    requests = []
    viewer.contextMenuRequested.connect(lambda scene, gp: requests.append(scene))

    _press(viewer, (100, 100), Qt.MouseButton.RightButton)
    assert not viewer._isPanning, "standard right press must not pan"
    _release(viewer, (100, 100), Qt.MouseButton.RightButton)

    assert len(requests) == 1


def test_standard_right_drag_does_not_request_menu(app):
    viewer = _viewer(app, 'standard')
    requests = []
    viewer.contextMenuRequested.connect(lambda scene, gp: requests.append(scene))

    _press(viewer, (100, 100), Qt.MouseButton.RightButton)
    _release(viewer, (150, 140), Qt.MouseButton.RightButton)

    assert requests == []


def test_context_menu_event_is_swallowed(app):
    """Windows-synthesized context-menu events must not double-fire the menu."""
    viewer = _viewer(app, 'classic')

    class _FakeCtxEvent:
        accepted = False

        def accept(self):
            self.accepted = True

    ev = _FakeCtxEvent()
    viewer.contextMenuEvent(ev)
    assert ev.accepted


# ---------------------------------------------------------------------------
# Standard scheme: presses on movable items belong to the item, not the pan
# ---------------------------------------------------------------------------

def test_standard_press_on_movable_item_does_not_pan(app):
    viewer = _viewer(app, 'standard')
    handle = QGraphicsEllipseItem(-10, -10, 20, 20)
    handle.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
    handle.setZValue(100)
    viewer.scene.addItem(handle)
    # Park the handle at the scene point under view pos (50, 50)
    handle.setPos(viewer.mapToScene(50, 50))

    _press(viewer, (50, 50), Qt.MouseButton.LeftButton)
    assert not viewer._isPanning

    viewer.scene.removeItem(handle)


def test_standard_press_on_plain_image_still_pans(app):
    viewer = _viewer(app, 'standard')
    _press(viewer, (50, 50), Qt.MouseButton.LeftButton)
    assert viewer._isPanning
    _release(viewer, (50, 50), Qt.MouseButton.LeftButton)
