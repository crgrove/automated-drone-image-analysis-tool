"""Freeze regression: transient viewChanged 'zoom_when_ready' handlers.

Both GalleryController.on_aoi_clicked and
AOINeighborTrackingController._on_gallery_image_clicked connect a one-shot
closure to main_image.viewChanged *before* loading, so a zoom fires once the
new image is ready. If the load fails or returns early (missing file, viewer
destroyed) the old code left the closure connected forever; every later
viewChanged — including those from wheel zooming — then re-ran it, re-entering
zoomToArea against a stale AOI. load_image() is synchronous, so the handler
must be unconditionally disconnected once it returns.
"""

import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtCore import QObject
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

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
    """Load an image and reset zoom so a later viewChanged would satisfy the
    handler's guard conditions (has image, empty zoom stack)."""
    pm = QPixmap(80, 80)
    pm.fill(Qt.black)
    viewer.setImage(pm)


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


def test_gallery_handler_disconnected_after_failed_load(app):
    viewer = _sized_viewer()
    parent = MagicMock()
    parent.main_image = viewer
    parent.current_image = 0
    parent._load_image = lambda: None  # failed load: never sets an image

    gc = _gallery_controller(parent)
    gc._zoom_to_aoi = MagicMock()

    # Click an AOI on a different image -> needs_load path connects the handler.
    gc.on_aoi_clicked(1, 0, {'center': (10, 20)})

    # The failed load never zoomed.
    assert gc._zoom_to_aoi.call_count == 0

    # Later the user has an image loaded with a cleared zoom stack; a wheel
    # zoom emits viewChanged. A leaked handler would zoom here.
    _give_image(viewer)
    gc._zoom_to_aoi.reset_mock()
    viewer.viewChanged.emit()

    assert gc._zoom_to_aoi.call_count == 0


def test_gallery_handler_still_zooms_then_disconnects_on_success(app):
    viewer = _sized_viewer()
    parent = MagicMock()
    parent.main_image = viewer
    parent.current_image = 0
    # Successful load: sets an image and resets zoom (emits viewChanged).
    parent._load_image = lambda: (_give_image(viewer), viewer.resetZoom())

    gc = _gallery_controller(parent)
    gc._zoom_to_aoi = MagicMock()

    gc.on_aoi_clicked(1, 0, {'center': (10, 20)})

    # The normal path still zooms exactly once.
    assert gc._zoom_to_aoi.call_count == 1

    # And the handler is gone: a later viewChanged does not re-zoom.
    viewer.viewChanged.emit()
    assert gc._zoom_to_aoi.call_count == 1


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


def test_neighbor_handler_disconnected_after_failed_load(app):
    viewer = _sized_viewer()
    parent = QObject()          # QObject: controller passes it to super().__init__
    parent.main_image = viewer
    parent.current_image = 0
    parent._load_image = lambda: None  # failed load

    ctrl = _neighbor_controller(parent)
    ctrl._neighbor_results = [{'image_idx': 1, 'pixel_x': 10, 'pixel_y': 20}]

    ctrl._on_gallery_image_clicked(1)

    # Later: image present, zoom stack clear, wheel zoom emits viewChanged.
    _give_image(viewer)
    viewer.zoomToArea = MagicMock()
    viewer.viewChanged.emit()

    assert viewer.zoomToArea.call_count == 0
