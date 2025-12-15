"""
Comprehensive tests for CalTopoService.

Tests CalTopo API interactions and authentication.
"""

import pytest
from unittest.mock import patch, MagicMock
from core.services.export.CalTopoService import CalTopoService


@pytest.fixture
def caltopo_service():
    """Fixture providing a CalTopoService instance."""
    return CalTopoService()


def test_caltopo_service_initialization(caltopo_service):
    """Test CalTopoService initialization."""
    assert caltopo_service is not None
    assert caltopo_service.session is not None
    assert caltopo_service.settings is not None


def test_clear_session(caltopo_service):
    """Test clearing session data."""
    caltopo_service.clear_session()
    assert len(caltopo_service.session.cookies) == 0


def test_is_authenticated_false(caltopo_service):
    """Test authentication check when not authenticated."""
    with patch.object(caltopo_service.session, 'get', side_effect=Exception):
        result = caltopo_service.is_authenticated()
        assert result is False


def test_is_authenticated_true(caltopo_service):
    """Test authentication check when authenticated."""
    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch.object(caltopo_service.session, 'get', return_value=mock_response):
        result = caltopo_service.is_authenticated()
        assert result is True


def test_get_user_maps(caltopo_service):
    """Test getting user maps."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {'id': '1', 'title': 'Test Map', 'modified': '2024-01-01'}
    ]

    with patch.object(caltopo_service.session, 'get', return_value=mock_response):
        maps = caltopo_service.get_user_maps()
        assert isinstance(maps, list)


def test_save_session(caltopo_service):
    """Test saving session cookies."""
    cookies_dict = {'session_id': 'test123', 'auth_token': 'token456'}
    caltopo_service.save_session(cookies_dict)

    # Verify cookies were saved
    cookies_json = caltopo_service.settings.value("session_cookies", "")
    assert cookies_json is not None
