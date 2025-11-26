"""
Comprehensive tests for viewer dialogs.

Tests all dialogs used in the viewer.
"""

import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope='session')
def app():
    """Create QApplication for widget tests."""
    return QApplication.instance() or QApplication([])


def test_aoi_comment_dialog_initialization(app):
    """Test AOICommentDialog initialization."""
    from core.views.images.viewer.dialogs.AOICommentDialog import AOICommentDialog

    dialog = AOICommentDialog(None, "Test comment")
    assert dialog is not None


def test_aoi_creation_dialog_initialization(app):
    """Test AOICreationDialog initialization."""
    from core.views.images.viewer.dialogs.AOICreationDialog import AOICreationDialog

    dialog = AOICreationDialog(None)
    assert dialog is not None


def test_aoi_filter_dialog_initialization(app):
    """Test AOIFilterDialog initialization."""
    from core.views.images.viewer.dialogs.AOIFilterDialog import AOIFilterDialog

    dialog = AOIFilterDialog(None)
    assert dialog is not None


def test_bearing_recovery_dialog_initialization(app):
    """Test BearingRecoveryDialog initialization."""
    from core.views.images.viewer.dialogs.BearingRecoveryDialog import BearingRecoveryDialog

    dialog = BearingRecoveryDialog(None, [])
    assert dialog is not None


def test_cache_location_dialog_initialization(app):
    """Test CacheLocationDialog initialization."""
    from core.views.images.viewer.dialogs.CacheLocationDialog import CacheLocationDialog

    dialog = CacheLocationDialog(None, "default_path")
    assert dialog is not None


def test_caltopo_auth_dialog_initialization(app):
    """Test CalTopoAuthDialog initialization."""
    from core.views.images.viewer.dialogs.CalTopoAuthDialog import CalTopoAuthDialog

    dialog = CalTopoAuthDialog(None)
    assert dialog is not None


def test_caltopo_map_dialog_initialization(app):
    """Test CalTopoMapDialog initialization."""
    from core.views.images.viewer.dialogs.CalTopoMapDialog import CalTopoMapDialog

    dialog = CalTopoMapDialog(None)
    assert dialog is not None


def test_export_progress_dialog_initialization(app):
    """Test ExportProgressDialog initialization."""
    from core.views.images.viewer.dialogs.ExportProgressDialog import ExportProgressDialog

    dialog = ExportProgressDialog(None, "Test Export", 100)
    assert dialog is not None


def test_gps_map_dialog_initialization(app):
    """Test GPSMapDialog initialization."""
    from core.views.images.viewer.dialogs.GPSMapDialog import GPSMapDialog

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
    from core.views.images.viewer.dialogs.HelpDialog import HelpDialog

    dialog = HelpDialog(None)
    assert dialog is not None


def test_image_adjustment_dialog_initialization(app):
    """Test ImageAdjustmentDialog initialization."""
    from core.views.images.viewer.dialogs.ImageAdjustmentDialog import ImageAdjustmentDialog

    dialog = ImageAdjustmentDialog(None)
    assert dialog is not None


def test_loading_dialog_initialization(app):
    """Test LoadingDialog initialization."""
    from core.views.images.viewer.dialogs.LoadingDialog import LoadingDialog

    # LoadingDialog only takes parent, not a message
    dialog = LoadingDialog(None)
    assert dialog is not None


def test_map_export_dialog_initialization(app):
    """Test MapExportDialog initialization."""
    from core.views.images.viewer.dialogs.MapExportDialog import MapExportDialog

    dialog = MapExportDialog(None)
    assert dialog is not None


def test_measure_dialog_initialization(app):
    """Test MeasureDialog initialization."""
    from core.views.images.viewer.dialogs.MeasureDialog import MeasureDialog

    # MeasureDialog requires image_viewer, current_gsd, and distance_unit
    mock_image_viewer = MagicMock()
    mock_image_viewer.canZoom = True
    mock_image_viewer.canPan = True
    mock_image_viewer.regionZoomButton = MagicMock()

    dialog = MeasureDialog(None, mock_image_viewer, 5.0, 'm')
    assert dialog is not None


def test_pdf_export_dialog_initialization(app):
    """Test PDFExportDialog initialization."""
    from core.views.images.viewer.dialogs.PDFExportDialog import PDFExportDialog

    dialog = PDFExportDialog(None)
    assert dialog is not None


def test_reviewer_name_dialog_initialization(app):
    """Test ReviewerNameDialog initialization."""
    from core.views.images.viewer.dialogs.ReviewerNameDialog import ReviewerNameDialog

    dialog = ReviewerNameDialog(None)
    assert dialog is not None


def test_upscale_dialog_initialization(app):
    """Test UpscaleDialog initialization."""
    from core.views.images.viewer.dialogs.UpscaleDialog import UpscaleDialog

    dialog = UpscaleDialog(None)
    assert dialog is not None


def test_zip_export_dialog_initialization(app):
    """Test ZipExportDialog initialization."""
    from core.views.images.viewer.dialogs.ZipExportDialog import ZipExportDialog

    dialog = ZipExportDialog(None)
    assert dialog is not None
