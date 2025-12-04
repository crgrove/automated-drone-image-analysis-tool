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
    assert controller.caltopo_service is not None
    assert controller.caltopo_api_service is not None
    assert controller.credential_helper is not None


@patch('core.controllers.images.viewer.exports.CalTopoExportController.QMessageBox')
def test_caltopo_export_controller_offline_mode(app, mock_viewer, mock_messagebox):
    """Test CalTopo export with offline mode enabled."""
    from core.controllers.images.viewer.exports.CalTopoExportController import CalTopoExportController
    
    # Mock offline mode
    mock_viewer.settings_service = MagicMock()
    mock_viewer.settings_service.get_bool_setting.return_value = True
    
    controller = CalTopoExportController(mock_viewer)
    
    result = controller.export_to_caltopo_via_api(
        [],
        {},
        include_flagged_aois=True
    )
    
    assert result is False
    mock_messagebox.information.assert_called_once()


@patch('core.controllers.images.viewer.exports.CalTopoExportController.CalTopoCredentialDialog')
@patch('core.controllers.images.viewer.exports.CalTopoExportController.CalTopoAPIMapDialog')
@patch('core.services.export.CalTopoAPIService.CalTopoAPIService')
def test_caltopo_export_via_api_success(mock_api_service, mock_map_dialog, mock_cred_dialog, app, mock_viewer):
    """Test successful CalTopo API export."""
    from core.controllers.images.viewer.exports.CalTopoExportController import CalTopoExportController
    
    # Setup mocks
    mock_viewer.settings_service = MagicMock()
    mock_viewer.settings_service.get_bool_setting.return_value = False
    
    # Mock credential dialog
    mock_cred_instance = MagicMock()
    mock_cred_instance.exec.return_value = 1  # Accepted
    mock_cred_instance.get_credentials.return_value = ('TEAM123', 'CRED123', 'SECRET123')
    mock_cred_dialog.return_value = mock_cred_instance
    
    # Mock API service
    mock_api_instance = MagicMock()
    mock_api_instance.get_account_data.return_value = (True, {
        'team_id': 'TEAM123',
        'state': {
            'features': [
                {
                    'id': 'map1',
                    'properties': {
                        'class': 'CollaborativeMap',
                        'title': 'Test Map',
                        'modified': 1234567890
                    }
                }
            ]
        }
    })
    mock_api_instance.add_marker_via_api.return_value = (True, 'marker123')
    mock_api_instance.add_polygon_via_api.return_value = (True, 'polygon123')
    mock_api_service.return_value = mock_api_instance
    
    # Mock map dialog
    mock_map_instance = MagicMock()
    mock_map_instance.exec.return_value = 1  # Accepted
    mock_map_instance.selected_map = {
        'type': 'map',
        'id': 'map1',
        'title': 'Test Map',
        'team_id': 'TEAM123'
    }
    mock_map_dialog.return_value = mock_map_instance
    
    # Mock credential helper
    with patch.object(CalTopoExportController, 'credential_helper') as mock_helper:
        mock_helper.has_credentials.return_value = False
        mock_helper.get_credentials.return_value = (None, None, None)
        
        controller = CalTopoExportController(mock_viewer)
        controller.caltopo_api_service = mock_api_instance
        
        # Mock image data
        images = [
            {
                'path': 'test1.jpg',
                'name': 'test1.jpg',
                'areas_of_interest': [
                    {
                        'center': [100, 100],
                        'area': 1000,
                        'user_comment': 'Test AOI'
                    }
                ],
                'hidden': False
            }
        ]
        flagged_aois = {0: {0}}
        
        # Mock the marker preparation methods
        with patch.object(controller, '_prepare_markers') as mock_prep_markers, \
             patch.object(controller, '_export_markers_via_api') as mock_export_markers, \
             patch.object(controller, '_export_polygons_via_api') as mock_export_polygons:
            
            mock_prep_markers.return_value = [
                {
                    'lat': 37.7749,
                    'lon': -122.4194,
                    'title': 'Test Marker',
                    'description': 'Test'
                }
            ]
            mock_export_markers.return_value = (1, False)  # 1 success, not cancelled
            mock_export_polygons.return_value = (0, False)
            
            result = controller.export_to_caltopo_via_api(
                images,
                flagged_aois,
                include_flagged_aois=True
            )
            
            # Should complete successfully
            assert mock_cred_instance.exec.called
            assert mock_map_instance.exec.called


@patch('core.controllers.images.viewer.exports.CalTopoExportController.QMessageBox')
def test_caltopo_export_via_api_no_data_selected(app, mock_viewer, mock_messagebox):
    """Test CalTopo API export with no data types selected."""
    from core.controllers.images.viewer.exports.CalTopoExportController import CalTopoExportController
    
    mock_viewer.settings_service = MagicMock()
    mock_viewer.settings_service.get_bool_setting.return_value = False
    
    controller = CalTopoExportController(mock_viewer)
    
    result = controller.export_to_caltopo_via_api(
        [],
        {},
        include_flagged_aois=False,
        include_locations=False,
        include_coverage_area=False
    )
    
    assert result is False
    mock_messagebox.information.assert_called_once()


@patch('core.controllers.images.viewer.exports.CalTopoExportController.CalTopoCredentialDialog')
def test_caltopo_export_via_api_credentials_cancelled(app, mock_viewer, mock_cred_dialog):
    """Test CalTopo API export when user cancels credential entry."""
    from core.controllers.images.viewer.exports.CalTopoExportController import CalTopoExportController
    
    mock_viewer.settings_service = MagicMock()
    mock_viewer.settings_service.get_bool_setting.return_value = False
    
    # Mock credential dialog - user cancels
    mock_cred_instance = MagicMock()
    mock_cred_instance.exec.return_value = 0  # Rejected
    mock_cred_dialog.return_value = mock_cred_instance
    
    controller = CalTopoExportController(mock_viewer)
    
    with patch.object(controller.credential_helper, 'has_credentials', return_value=False):
        result = controller.export_to_caltopo_via_api(
            [],
            {},
            include_flagged_aois=True
        )
        
        assert result is False
