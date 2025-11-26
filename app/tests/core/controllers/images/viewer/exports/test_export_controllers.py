"""
Comprehensive tests for export controllers.

Tests PDF, Zip, KML, CalTopo, and Coverage Extent export controllers.
"""

import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication


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
            'name': 'test1.jpg',
            'areas_of_interest': [
                {'center': (100, 100), 'radius': 20, 'flagged': True}
            ],
            'hidden': False
        }
    ]
    viewer.xml_path = 'test.xml'
    viewer.settings = {'thermal': 'False'}
    return viewer


def test_pdf_export_controller_initialization(app, mock_viewer):
    """Test PDFExportController initialization."""
    from core.controllers.images.viewer.exports.PDFExportController import PDFExportController

    controller = PDFExportController(mock_viewer)
    assert controller.parent == mock_viewer


def test_zip_export_controller_initialization(app, mock_viewer):
    """Test ZipExportController initialization."""
    from core.controllers.images.viewer.exports.ZipExportController import ZipExportController

    controller = ZipExportController(mock_viewer)
    assert controller.parent == mock_viewer


def test_unified_map_export_controller_initialization(app, mock_viewer):
    """Test UnifiedMapExportController initialization."""
    import pytest
    try:
        from core.controllers.images.viewer.exports.UnifiedMapExportController import UnifiedMapExportController
    except ImportError as e:
        pytest.skip(f"Dependencies not available: {e}")

    controller = UnifiedMapExportController(mock_viewer)
    assert controller.parent == mock_viewer


def test_coverage_extent_export_controller_initialization(app, mock_viewer):
    """Test CoverageExtentExportController initialization."""
    import pytest
    try:
        from core.controllers.images.viewer.exports.CoverageExtentExportController import CoverageExtentExportController
    except ImportError as e:
        pytest.skip(f"Dependencies not available: {e}")

    controller = CoverageExtentExportController(mock_viewer)
    assert controller.parent == mock_viewer


def test_caltopo_export_controller_initialization(app, mock_viewer):
    """Test CalTopoExportController initialization."""
    from core.controllers.images.viewer.exports.CalTopoExportController import CalTopoExportController

    controller = CalTopoExportController(mock_viewer)
    assert controller.parent == mock_viewer
