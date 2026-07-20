"""Tests for AlignImageView's initial seed geometry.

The Align Image dialog seeds its FOV quad from the drone photo itself so the
four corner handles start exactly on their colour-matched corner squares. These
tests lock in that behaviour (and the Reset that restores it) so the quad can
never regress to the mirrored/rotated placement the metadata estimate produced.
"""

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap, QColor

from core.views.images.viewer.widgets.AlignImageView import AlignImageView
from helpers.PhotogrammetryHelper import local_enu_to_gps, corners_are_mirrored


_LAT, _LON = 40.0, -105.0


@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def make_view(app):
    """Create AlignImageViews and tear them down deterministically.

    The view arms debounced tile QTimers and connects to its tile loader; left
    alive they fire in a later test's event loop and raise. Stop and disconnect
    them so tests stay isolated.
    """
    views = []

    def _make():
        view = AlignImageView(offline_only=True)
        views.append(view)
        return view

    yield _make

    for view in views:
        view._tile_timer.stop()
        view._zoom_timer.stop()
        try:
            view.tile_loader.tile_loaded.disconnect()
        except (RuntimeError, TypeError):
            pass
        view.deleteLater()
    QApplication.processEvents()


def _make_drone_image(tmp_path, w=400, h=300):
    """Write a real PNG so QPixmap(path) loads a known-size drone image."""
    pixmap = QPixmap(w, h)
    pixmap.fill(QColor("gray"))
    path = str(tmp_path / "drone.png")
    assert pixmap.save(path, "PNG")
    return path


def _estimated_corners(half_w_m=40.0, half_h_m=30.0):
    """A rectangular metadata footprint estimate (TL, TR, BR, BL)."""
    return [
        local_enu_to_gps(-half_w_m, half_h_m, _LAT, _LON),   # TL
        local_enu_to_gps(half_w_m, half_h_m, _LAT, _LON),    # TR
        local_enu_to_gps(half_w_m, -half_h_m, _LAT, _LON),   # BR
        local_enu_to_gps(-half_w_m, -half_h_m, _LAT, _LON),  # BL
    ]


def _assert_handles_on_markers(view, tol=1e-6):
    assert len(view.corner_handles) == 4
    assert len(view.corner_markers) == 4
    for handle, marker in zip(view.corner_handles, view.corner_markers):
        assert handle.pos().x() == pytest.approx(marker.pos().x(), abs=tol)
        assert handle.pos().y() == pytest.approx(marker.pos().y(), abs=tol)


def test_estimate_seed_places_handles_on_photo_corners(make_view, tmp_path):
    """A fresh estimate seeds each handle exactly on its photo corner square."""
    view = make_view()
    view.load(_make_drone_image(tmp_path), _estimated_corners(), bearing=90.0)

    # The whole point of the fix: handles coincide with the colour-matched
    # corner squares instead of starting mirrored/rotated away from them.
    _assert_handles_on_markers(view)


def test_estimate_seed_is_not_mirrored(make_view, tmp_path):
    """The seeded quad has a correct (orientation-preserving) winding."""
    view = make_view()
    view.load(_make_drone_image(tmp_path), _estimated_corners(), bearing=90.0)

    # Seeding from the photo (not the reverse-wound metadata corners) means the
    # accept-time mirror warning does not fire on an untouched estimate.
    assert not corners_are_mirrored(view.get_corner_gps())


def test_estimate_seed_uses_camera_heading_for_rotation(make_view, tmp_path):
    """The passed camera heading orients the photo (and thus the quad)."""
    view = make_view()
    view.load(_make_drone_image(tmp_path), _estimated_corners(), bearing=123.0)

    assert view.get_rotation() == pytest.approx(123.0)


def test_reset_restores_estimate_seed(make_view, tmp_path):
    """Reset re-seeds the handles on the photo corners and restores rotation."""
    view = make_view()
    view.load(_make_drone_image(tmp_path), _estimated_corners(), bearing=45.0)

    # Drag a corner handle well away and rotate the image.
    moved = view.corner_handles[0]
    moved.setPos(moved.pos().x() + 5000.0, moved.pos().y() + 5000.0)
    view.set_image_rotation(200.0)
    assert view.get_rotation() == pytest.approx(200.0)

    view.reset_to_estimate()

    assert view.get_rotation() == pytest.approx(45.0)
    _assert_handles_on_markers(view)


def test_reset_clears_tie_points(make_view, tmp_path):
    """Reset drops any tie points, matching a fresh estimate."""
    view = make_view()
    view.load(_make_drone_image(tmp_path), _estimated_corners(), bearing=0.0)

    view.add_tie_point()
    assert len(view.tie_points) == 1

    view.reset_to_estimate()
    assert view.tie_points == []


def test_saved_alignment_keeps_placed_corners(make_view, tmp_path):
    """Resuming a saved alignment restores its corners verbatim, not the photo."""
    saved_corners = _estimated_corners(half_w_m=60.0, half_h_m=20.0)
    saved = {'corners': saved_corners, 'tie_points': [], 'rotation': 33.0}

    view = make_view()
    view.load(_make_drone_image(tmp_path), _estimated_corners(), bearing=90.0,
              saved_alignment=saved)

    assert view.get_rotation() == pytest.approx(33.0)
    # Handles sit on the saved corner GPS, not re-derived from the photo.
    got = view.get_corner_gps()
    for (glat, glon), (slat, slon) in zip(got, saved_corners):
        assert glat == pytest.approx(slat, abs=1e-6)
        assert glon == pytest.approx(slon, abs=1e-6)
