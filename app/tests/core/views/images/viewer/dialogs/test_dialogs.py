"""
Comprehensive tests for viewer dialogs.

Tests all dialogs used in the viewer.
"""

import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication

from core.views.images.viewer.dialogs.AOICommentDialog import AOICommentDialog
from core.views.images.viewer.dialogs.AOICreationDialog import AOICreationDialog
from core.views.images.viewer.dialogs.AOIFilterDialog import AOIFilterDialog
from core.views.images.viewer.dialogs.BearingRecoveryDialog import BearingRecoveryDialog
from core.views.images.viewer.dialogs.CacheLocationDialog import CacheLocationDialog
from core.views.images.viewer.dialogs.CalTopoAuthDialog import CalTopoAuthDialog
from core.views.images.viewer.dialogs.CalTopoMapDialog import CalTopoMapDialog
from core.views.images.viewer.dialogs.ExportProgressDialog import ExportProgressDialog
from core.views.images.viewer.dialogs.GPSMapDialog import GPSMapDialog
from core.views.images.viewer.dialogs.HelpDialog import HelpDialog
from core.views.images.viewer.dialogs.ImageAdjustmentDialog import ImageAdjustmentDialog
from core.views.images.viewer.dialogs.LoadingDialog import LoadingDialog
from core.views.images.viewer.dialogs.MapExportDialog import MapExportDialog
from core.views.images.viewer.dialogs.MeasureDialog import MeasureDialog
from core.views.images.viewer.dialogs.PDFExportDialog import PDFExportDialog
from core.views.images.viewer.dialogs.ReviewerNameDialog import ReviewerNameDialog
from core.views.images.viewer.dialogs.UpscaleDialog import UpscaleDialog
from core.views.images.viewer.dialogs.ZipExportDialog import ZipExportDialog


@pytest.fixture(scope='session')
def app():
    """Create QApplication for widget tests."""
    return QApplication.instance() or QApplication([])


def test_aoi_comment_dialog_initialization(app):
    """Test AOICommentDialog initialization."""
    dialog = AOICommentDialog(None, "Test comment")
    assert dialog is not None


def test_aoi_creation_dialog_initialization(app):
    """Test AOICreationDialog initialization."""
    dialog = AOICreationDialog(None)
    assert dialog is not None


def test_aoi_filter_dialog_initialization(app):
    """Test AOIFilterDialog initialization."""
    dialog = AOIFilterDialog(None)
    assert dialog is not None


def test_bearing_recovery_dialog_initialization(app):
    """Test BearingRecoveryDialog initialization."""
    # Mock QMessageBox to avoid showing dialog during test
    with patch('core.views.images.viewer.dialogs.BearingRecoveryDialog.QMessageBox'):
        # Mock QTimer to prevent automatic skip
        with patch('core.views.images.viewer.dialogs.BearingRecoveryDialog.QTimer'):
            dialog = BearingRecoveryDialog(None, [])
            assert dialog is not None


def test_cache_location_dialog_initialization(app):
    """Test CacheLocationDialog initialization."""
    dialog = CacheLocationDialog(None, "default_path")
    assert dialog is not None


def test_caltopo_auth_dialog_initialization(app):
    """Test CalTopoAuthDialog initialization."""
    dialog = CalTopoAuthDialog(None)
    assert dialog is not None


def test_caltopo_map_dialog_initialization(app):
    """Test CalTopoMapDialog initialization."""
    dialog = CalTopoMapDialog(None)
    assert dialog is not None


def test_export_progress_dialog_initialization(app):
    """Test ExportProgressDialog initialization."""
    dialog = ExportProgressDialog(None, "Test Export", 100)
    assert dialog is not None


def test_gps_map_dialog_initialization(app):
    """Test GPSMapDialog initialization."""
    # GPSMapDialog requires gps_data (list) and current_image_index
    # GPS data must have 'latitude', 'longitude', and 'index' keys
    gps_data = [
        {'latitude': 37.7749, 'longitude': -122.4194, 'name': 'Image 1', 'index': 0},
        {'latitude': 37.7750, 'longitude': -122.4195, 'name': 'Image 2', 'index': 1}
    ]
    dialog = GPSMapDialog(None, gps_data, 0)
    assert dialog is not None


def test_help_dialog_initialization(app):
    """Test HelpDialog initialization."""
    dialog = HelpDialog(None)
    assert dialog is not None


def test_image_adjustment_dialog_initialization(app):
    """Test ImageAdjustmentDialog initialization."""
    dialog = ImageAdjustmentDialog(None)
    assert dialog is not None


def test_loading_dialog_initialization(app):
    """Test LoadingDialog initialization."""
    # LoadingDialog only takes parent, not a message
    dialog = LoadingDialog(None)
    assert dialog is not None


def test_map_export_dialog_initialization(app):
    """Test MapExportDialog initialization."""
    dialog = MapExportDialog(None)
    assert dialog is not None


def test_measure_dialog_initialization(app):
    """Test MeasureDialog initialization."""
    # MeasureDialog requires image_viewer, current_gsd, and distance_unit
    mock_image_viewer = MagicMock()
    mock_image_viewer.canZoom = True
    mock_image_viewer.canPan = True
    mock_image_viewer.regionZoomButton = MagicMock()

    dialog = MeasureDialog(None, mock_image_viewer, 5.0, 'm')
    assert dialog is not None


def test_pdf_export_dialog_initialization(app):
    """Test PDFExportDialog initialization."""
    dialog = PDFExportDialog(None)
    assert dialog is not None


def test_reviewer_name_dialog_initialization(app):
    """Test ReviewerNameDialog initialization."""
    dialog = ReviewerNameDialog(None)
    assert dialog is not None


def test_upscale_dialog_initialization(app):
    """Test UpscaleDialog initialization."""
    dialog = UpscaleDialog(None)
    assert dialog is not None


def test_zip_export_dialog_initialization(app):
    """Test ZipExportDialog initialization."""
    dialog = ZipExportDialog(None)
    assert dialog is not None
