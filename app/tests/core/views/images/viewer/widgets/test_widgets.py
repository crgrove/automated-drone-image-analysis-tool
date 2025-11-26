"""
Comprehensive tests for viewer widgets.

Tests QtImageViewer, OverlayWidget, ScaleBarWidget, GPSMapView, etc.
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF


@pytest.fixture(scope='session')
def app():
    """Create QApplication for widget tests."""
    return QApplication.instance() or QApplication([])


def test_qt_image_viewer_initialization(app):
    """Test QtImageViewer initialization."""
    from core.views.images.viewer.widgets.QtImageViewer import QtImageViewer

    # QtImageViewer requires window parameter
    mock_window = MagicMock()
    viewer = QtImageViewer(mock_window)
    assert viewer is not None


def test_overlay_widget_initialization(app):
    """Test OverlayWidget initialization."""
    from core.views.images.viewer.widgets.OverlayWidget import OverlayWidget
    from core.views.images.viewer.widgets.QtImageViewer import QtImageViewer
    from core.views.images.viewer.widgets.ScaleBarWidget import ScaleBarWidget

    # OverlayWidget requires main_image_widget, scale_bar_widget, and theme
    mock_window = MagicMock()
    main_image_widget = QtImageViewer(mock_window)
    scale_bar_widget = ScaleBarWidget()
    widget = OverlayWidget(main_image_widget, scale_bar_widget, 'Dark')
    assert widget is not None


def test_scale_bar_widget_initialization(app):
    """Test ScaleBarWidget initialization."""
    from core.views.images.viewer.widgets.ScaleBarWidget import ScaleBarWidget

    widget = ScaleBarWidget()
    assert widget is not None


def test_scale_bar_widget_update(app):
    """Test ScaleBarWidget update functionality."""
    from core.views.images.viewer.widgets.ScaleBarWidget import ScaleBarWidget

    widget = ScaleBarWidget()

    # ScaleBarWidget uses setLabel() method, not update_scale_bar
    widget.setLabel("5.0 m")
    assert widget is not None


def test_gps_map_view_initialization(app):
    """Test GPSMapView initialization."""
    from core.views.images.viewer.widgets.GPSMapView import GPSMapView

    view = GPSMapView()
    assert view is not None


def test_map_tile_loader_initialization(app):
    """Test MapTileLoader initialization."""
    from core.views.images.viewer.widgets.MapTileLoader import MapTileLoader

    loader = MapTileLoader()
    assert loader is not None
