"""Tests for run-wide AOI number rendering in the gallery view.

Covers AOIGalleryModel display/tooltip text and the AOIGalleryDelegate
number badge introduced by the AOI improvements feature.
"""

import pytest
from unittest.mock import MagicMock, patch

from PySide6.QtCore import QRect
from PySide6.QtGui import QPixmap, QPainter


@pytest.fixture
def gallery_model(app):
    """An AOIGalleryModel with the background thumbnail loader patched out."""
    with patch(
        "core.controllers.images.viewer.gallery.AOIGalleryModel.ThumbnailLoader"
    ):
        from core.controllers.images.viewer.gallery.AOIGalleryModel import AOIGalleryModel
        model = AOIGalleryModel()
    viewer = MagicMock()
    viewer.images = [{'name': 'DJI_0001.JPG'}, {'name': 'DJI_0002.JPG'}]
    model.viewer = viewer
    yield model
    # AOIGalleryModel is a QObject; the patched ThumbnailLoader mock records
    # the bound-method slots connected to it, forming a reference cycle.
    # Break it on teardown so the model is freed while QApplication is alive.
    model.thumbnail_loader = None
    model.viewer = None


# ---------------------------------------------------------------------------
# AOIGalleryModel display / tooltip text
# ---------------------------------------------------------------------------

def test_display_text_uses_aoi_number(gallery_model):
    """The gallery display text shows the run-wide AOI number."""
    text = gallery_model._get_display_text(0, 3, {'number': 42})
    assert 'AOI #42' in text
    assert 'DJI_0001.JPG' in text


def test_display_text_falls_back_without_number(gallery_model):
    """Display text falls back to the AOI index when no number is present."""
    text = gallery_model._get_display_text(0, 3, {})
    assert 'AOI 3' in text


def test_display_text_keeps_confidence(gallery_model):
    """Display text keeps the confidence readout alongside the number."""
    text = gallery_model._get_display_text(1, 0, {'number': 7, 'confidence': 0.5})
    assert 'AOI #7' in text
    assert '%' in text


def test_tooltip_text_uses_aoi_number(gallery_model):
    """The gallery tooltip shows the run-wide AOI number."""
    text = gallery_model._get_tooltip_text(0, 3, {'number': 42, 'center': (10, 20)})
    assert 'AOI #42' in text


def test_tooltip_text_falls_back_without_number(gallery_model):
    """Tooltip falls back to the AOI index when no number is present."""
    text = gallery_model._get_tooltip_text(0, 3, {'center': (10, 20)})
    assert 'AOI Index: 3' in text


# ---------------------------------------------------------------------------
# AOIGalleryDelegate number badge
# ---------------------------------------------------------------------------

def test_delegate_draws_number_badge(app):
    """The gallery delegate's number badge renders without error."""
    from core.controllers.images.viewer.gallery.GalleryUIComponent import AOIGalleryDelegate

    # Bypass __init__ (which loads qtawesome icons) — the badge helper only
    # needs a painter, a rect and a number, so this keeps the test
    # independent of qtawesome font state and test ordering.
    delegate = AOIGalleryDelegate.__new__(AOIGalleryDelegate)
    pixmap = QPixmap(200, 200)
    painter = QPainter(pixmap)
    try:
        delegate._draw_number_badge(painter, QRect(0, 0, 180, 180), 123)
    finally:
        painter.end()
