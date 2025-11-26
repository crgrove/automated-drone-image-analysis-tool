"""
Comprehensive tests for viewer controllers.

Tests the various controllers used in the Viewer window.
"""

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QPoint
from unittest.mock import patch, MagicMock
import tempfile
import os


@pytest.fixture(scope='session')
def app():
    """Create QApplication for widget tests."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def mock_viewer():
    """Create a mock viewer instance."""
    viewer = MagicMock()
    viewer.images = [
        {
            'path': 'test1.jpg',
            'areas_of_interest': [
                {'center': (100, 100), 'radius': 20, 'area': 400}
            ]
        },
        {
            'path': 'test2.jpg',
            'areas_of_interest': [
                {'center': (200, 200), 'radius': 30, 'area': 600}
            ]
        }
    ]
    viewer.current_image_index = 0
    viewer.xml_service = MagicMock()
    viewer.settings = {'thermal': 'False'}
    viewer.is_thermal = False
    return viewer


def test_aoi_controller_initialization(app, mock_viewer):
    """Test AOIController initialization."""
    import pytest
    try:
        from core.controllers.images.viewer.aoi.AOIController import AOIController
    except ImportError as e:
        pytest.skip(f"Dependencies not available: {e}")

    controller = AOIController(mock_viewer)

    assert controller.parent == mock_viewer
    assert controller.ui_component is not None


def test_gallery_controller_initialization(app, mock_viewer):
    """Test GalleryController initialization."""
    import pytest
    try:
        from core.controllers.images.viewer.gallery.GalleryController import GalleryController
    except ImportError as e:
        pytest.skip(f"Dependencies not available: {e}")

    controller = GalleryController(mock_viewer)

    assert controller.parent == mock_viewer
    assert controller.model is not None
    assert controller.ui_component is not None


def test_coordinate_controller_initialization(app, mock_viewer):
    """Test CoordinateController initialization."""
    from core.controllers.images.viewer.CoordinateController import CoordinateController

    controller = CoordinateController(mock_viewer)

    assert controller.parent == mock_viewer


def test_status_controller_initialization(app, mock_viewer):
    """Test StatusController initialization."""
    from core.controllers.images.viewer.status.StatusController import StatusController

    controller = StatusController(mock_viewer)

    assert controller.parent == mock_viewer


def test_gps_map_controller_initialization(app, mock_viewer):
    """Test GPSMapController initialization."""
    from core.controllers.images.viewer.GPSMapController import GPSMapController

    controller = GPSMapController(mock_viewer)

    assert controller.parent == mock_viewer


def test_thumbnail_controller_initialization(app, mock_viewer):
    """Test ThumbnailController initialization."""
    from core.controllers.images.viewer.thumbnails.ThumbnailController import ThumbnailController

    controller = ThumbnailController(mock_viewer)

    assert controller.parent == mock_viewer


def test_thermal_data_controller_initialization(app, mock_viewer):
    """Test ThermalDataController initialization."""
    from core.controllers.images.viewer.ThermalDataController import ThermalDataController

    controller = ThermalDataController(mock_viewer)

    assert controller.parent == mock_viewer


def test_pixel_info_controller_initialization(app, mock_viewer):
    """Test PixelInfoController initialization."""
    from core.controllers.images.viewer.PixelInfoController import PixelInfoController

    controller = PixelInfoController(mock_viewer)

    assert controller.parent == mock_viewer


def test_altitude_controller_initialization(app, mock_viewer):
    """Test AltitudeController initialization."""
    from core.controllers.images.viewer.AltitudeController import AltitudeController

    controller = AltitudeController(mock_viewer)

    assert controller.parent == mock_viewer
