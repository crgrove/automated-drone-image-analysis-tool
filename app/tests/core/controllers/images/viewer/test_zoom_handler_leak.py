"""Regression: zoom-after-load must not leave anything armed behind it.

Cross-image navigation with a framing intent (a gallery AOI click, a
neighbor-tracking result click) used to connect a transient viewChanged
closure before loading and repair missed zooms with settle-window timers.
Both could leak: a leaked closure re-entered zoomToArea against a stale
target on any later viewChanged (wheel zoom), and a stale timer could zoom
after the user had moved on.

The mechanism is now Viewer.load_image_with_zoom: one entry point that
arms the viewer's single pending-zoom slot, loads, and always disarms -
the load pipeline consumes the slot as its final step. These tests pin
the contract: the requester's zoom fires exactly once through the
pipeline, a failed load leaves nothing armed, no later viewChanged
emission can ever re-zoom, and geometry events delegate to reprojectView
instead of discarding a held zoom.
"""

import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtCore import QObject
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from core.controllers.images.viewer.Viewer import Viewer
from core.views.images.viewer.widgets.QtImageViewer import QtImageViewer


@pytest.fixture(scope='session')
def app():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


def _sized_viewer():
    """A real viewer (real viewChanged signal), no image yet."""
    viewer = QtImageViewer(MagicMock())
    viewer.resize(100, 100)
    return viewer


def _give_image(viewer):
    """Load an image so a later viewChanged would have satisfied the old
    handler's guard conditions (has image, empty zoom stack)."""
    pm = QPixmap(80, 80)
    pm.fill(Qt.black)
    viewer.setImage(pm)


# --------------------------------------------------------------------------- #
#  Viewer pending-zoom slot semantics (unbound methods on a bare stand-in)    #
# --------------------------------------------------------------------------- #

class _Slot:
    _pending_view_zoom = None
    current_image = 0

    def __init__(self):
        self.logger = MagicMock()  # the bound Viewer methods log

    def _load_image(self):
        pass


def test_load_with_zoom_slot_consumed_by_matching_load():
    slot = _Slot()
    applied = []

    def pipeline_load():
        cb = Viewer.take_pending_view_zoom(slot, slot.current_image)
        if cb is not None:
            cb()
    slot._load_image = pipeline_load

    Viewer.load_image_with_zoom(slot, 2, lambda: applied.append(2))

    assert applied == [2]
    assert slot.current_image == 2
    assert slot._pending_view_zoom is None


def test_arming_and_consuming_logs_nothing():
    """No log traffic on the normal path: this runs on every gallery AOI click.

    The armed/applied pair existed only to prove the mechanism fired on an
    unreproducible field machine. It did - the fault was relink drift in the
    results file - so the instrumentation came out before the prod build.
    """
    slot = _Slot()
    slot._load_image = lambda: Viewer.take_pending_view_zoom(slot, slot.current_image)

    Viewer.load_image_with_zoom(slot, 7, MagicMock())

    slot.logger.warning.assert_not_called()
    slot.logger.debug.assert_not_called()
    slot.logger.info.assert_not_called()


def test_unconsumed_request_is_disarmed_silently():
    """A load that never consumes still leaves nothing armed behind it."""
    slot = _Slot()
    slot._load_image = lambda: None  # never consumes the armed request

    Viewer.load_image_with_zoom(slot, 7, MagicMock())

    assert slot._pending_view_zoom is None
    slot.logger.warning.assert_not_called()


def test_take_for_mismatched_image_drops_request():
    slot = _Slot()
    slot._pending_view_zoom = (1, MagicMock())

    assert Viewer.take_pending_view_zoom(slot, 5) is None
    # Dropped, not left armed for a later load of image 1.
    assert slot._pending_view_zoom is None


def test_take_when_empty_is_none():
    slot = _Slot()
    assert Viewer.take_pending_view_zoom(slot, 0) is None


def test_load_with_zoom_disarms_even_when_load_raises():
    slot = _Slot()

    def exploding_load():
        raise RuntimeError("load blew up")
    slot._load_image = exploding_load

    with pytest.raises(RuntimeError):
        Viewer.load_image_with_zoom(slot, 3, MagicMock())

    # The finally disarmed the slot: nothing stale survives the failure.
    assert slot._pending_view_zoom is None


# --------------------------------------------------------------------------- #
#  Geometry events delegate to reprojectView (never discard a held zoom)      #
# --------------------------------------------------------------------------- #

def test_splitter_resize_delegates_to_reprojectview():
    viewer_self = MagicMock()
    viewer_self.main_image._is_destroyed = False

    Viewer._resize_main_image_and_reposition_overlay(viewer_self)

    viewer_self.main_image.reprojectView.assert_called_once_with()
    # And no direct wipe primitives were reached for.
    viewer_self.main_image.clearZoom.assert_not_called()
    viewer_self.main_image.resetZoom.assert_not_called()


# --------------------------------------------------------------------------- #
#  GalleryController.on_aoi_clicked                                           #
# --------------------------------------------------------------------------- #

def _gallery_controller(parent):
    with patch(
        "core.controllers.images.viewer.gallery.GalleryController.GalleryUIComponent"
    ), patch(
        "core.controllers.images.viewer.gallery.GalleryController.AOIGalleryModel"
    ):
        from core.controllers.images.viewer.gallery.GalleryController import GalleryController
        return GalleryController(parent)


def test_gallery_failed_load_arms_nothing(app, wire_pending_zoom):
    viewer = _sized_viewer()
    parent = MagicMock()
    parent.main_image = viewer
    parent.current_image = 0
    wire_pending_zoom(parent, loaded_idx=None)

    gc = _gallery_controller(parent)
    gc._zoom_to_aoi = MagicMock()

    gc.on_aoi_clicked(1, 0, {'center': (10, 20)})

    # The failed load never zoomed, and the slot was disarmed.
    assert gc._zoom_to_aoi.call_count == 0
    assert parent._pending_view_zoom is None

    # Later the user has an image loaded with a cleared zoom stack; a wheel
    # zoom emits viewChanged. Nothing may zoom in response.
    _give_image(viewer)
    gc._zoom_to_aoi.reset_mock()
    viewer.viewChanged.emit()

    assert gc._zoom_to_aoi.call_count == 0


def test_gallery_click_zooms_once_through_the_pipeline(app, wire_pending_zoom):
    viewer = _sized_viewer()
    parent = MagicMock()
    parent.main_image = viewer
    parent.current_image = 0
    wire_pending_zoom(parent, loaded_idx=1)

    gc = _gallery_controller(parent)
    gc._zoom_to_aoi = MagicMock()

    gc.on_aoi_clicked(1, 0, {'center': (10, 20)})

    # The pipeline applied the requested zoom exactly once.
    assert gc._zoom_to_aoi.call_count == 1

    # And nothing is armed: a later viewChanged does not re-zoom.
    _give_image(viewer)
    viewer.viewChanged.emit()
    assert gc._zoom_to_aoi.call_count == 1
    assert parent._pending_view_zoom is None


# --------------------------------------------------------------------------- #
#  AOINeighborTrackingController._on_gallery_image_clicked                    #
# --------------------------------------------------------------------------- #

def _neighbor_controller(parent):
    with patch(
        "core.controllers.images.viewer.neighbor.AOINeighborTrackingController.AOINeighborService"
    ):
        from core.controllers.images.viewer.neighbor.AOINeighborTrackingController import (
            AOINeighborTrackingController,
        )
        return AOINeighborTrackingController(parent)


def test_neighbor_failed_load_arms_nothing(app, wire_pending_zoom):
    viewer = _sized_viewer()
    parent = QObject()          # QObject: controller passes it to super().__init__
    parent.main_image = viewer
    parent.current_image = 0
    parent.images = [{}, {}]    # legacy index path: viewer_idx = image_idx
    wire_pending_zoom(parent, loaded_idx=None)

    ctrl = _neighbor_controller(parent)
    ctrl._neighbor_results = [{'image_idx': 1, 'pixel_x': 10, 'pixel_y': 20}]

    ctrl._on_gallery_image_clicked(1)

    # The failed load never zoomed, and the slot was disarmed.
    assert parent._pending_view_zoom is None

    # Later: image present, zoom stack clear, wheel zoom emits viewChanged.
    _give_image(viewer)
    viewer.zoomToArea = MagicMock()
    viewer.viewChanged.emit()

    assert viewer.zoomToArea.call_count == 0


def test_neighbor_click_zooms_once_through_the_pipeline(app, wire_pending_zoom):
    viewer = _sized_viewer()
    parent = QObject()
    parent.main_image = viewer
    parent.current_image = 0
    parent.images = [{}, {}]
    _give_image(viewer)
    wire_pending_zoom(parent, loaded_idx=1)

    ctrl = _neighbor_controller(parent)
    ctrl._neighbor_results = [{'image_idx': 1, 'pixel_x': 10, 'pixel_y': 20}]
    viewer.zoomToArea = MagicMock()

    ctrl._on_gallery_image_clicked(1)

    viewer.zoomToArea.assert_called_once_with((10, 20), 6)
    assert parent._pending_view_zoom is None

    # No re-zoom on later emissions.
    viewer.viewChanged.emit()
    assert viewer.zoomToArea.call_count == 1
