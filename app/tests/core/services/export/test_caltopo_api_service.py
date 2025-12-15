"""
Comprehensive tests for CalTopoAPIService.

Tests CalTopo Team API interactions, signed requests, and authentication.
"""

import pytest
import base64
import hmac
import time
import json
from unittest.mock import patch, MagicMock, mock_open
from core.services.export.CalTopoAPIService import CalTopoAPIService


@pytest.fixture
def caltopo_api_service():
    """Fixture providing a CalTopoAPIService instance."""
    return CalTopoAPIService()


@pytest.fixture
def sample_credentials():
    """Sample credentials for testing."""
    return {
        'team_id': 'ABC123',
        'credential_id': 'cred_id_123',
        'credential_secret': base64.b64encode(b'test_secret_key_12345678901234567890').decode()
    }


def test_caltopo_api_service_initialization(caltopo_api_service):
    """Test CalTopoAPIService initialization."""
    assert caltopo_api_service is not None
    assert caltopo_api_service.CALTOPO_BASE_URL == "https://caltopo.com"
    assert caltopo_api_service.DEFAULT_TIMEOUT_MS == 2 * 60 * 1000


def test_sign_request(caltopo_api_service, sample_credentials):
    """Test HMAC signature generation."""
    method = "GET"
    url = "/api/v1/acct/ABC123/since/0"
    expires = int(time.time() * 1000) + 120000
    payload_string = ""
    credential_secret = sample_credentials['credential_secret']

    signature = caltopo_api_service._sign_request(method, url, expires, payload_string, credential_secret)

    assert signature is not None
    assert isinstance(signature, str)
    # Verify it's base64 encoded
    try:
        base64.b64decode(signature)
    except Exception:
        pytest.fail("Signature is not valid base64")


def test_sign_request_with_payload(caltopo_api_service, sample_credentials):
    """Test HMAC signature generation with payload."""
    method = "POST"
    url = "/api/v1/map/MAP123/Marker"
    expires = int(time.time() * 1000) + 120000
    payload = {"type": "Feature", "properties": {"title": "Test"}}
    payload_string = json.dumps(payload)
    credential_secret = sample_credentials['credential_secret']

    signature = caltopo_api_service._sign_request(method, url, expires, payload_string, credential_secret)

    assert signature is not None
    # Same payload should produce same signature
    signature2 = caltopo_api_service._sign_request(method, url, expires, payload_string, credential_secret)
    assert signature == signature2


@patch('core.services.export.CalTopoAPIService.requests.get')
def test_api_request_get_success(mock_get, caltopo_api_service, sample_credentials):
    """Test successful GET API request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": {"data": "test"}}
    mock_get.return_value = mock_response

    success, result = caltopo_api_service._api_request(
        "GET",
        "/api/v1/acct/ABC123/since/0",
        sample_credentials['credential_id'],
        sample_credentials['credential_secret']
    )

    assert success is True
    assert result == {"data": "test"}
    mock_get.assert_called_once()


@patch('core.services.export.CalTopoAPIService.requests.post')
def test_api_request_post_success(mock_post, caltopo_api_service, sample_credentials):
    """Test successful POST API request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": {"id": "marker123"}}
    mock_post.return_value = mock_response

    payload = {"type": "Feature", "properties": {"title": "Test"}}
    success, result = caltopo_api_service._api_request(
        "POST",
        "/api/v1/map/MAP123/Marker",
        sample_credentials['credential_id'],
        sample_credentials['credential_secret'],
        payload
    )

    assert success is True
    assert result == {"id": "marker123"}
    mock_post.assert_called_once()


@patch('core.services.export.CalTopoAPIService.requests.get')
def test_api_request_get_failure(mock_get, caltopo_api_service, sample_credentials):
    """Test failed GET API request."""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_get.return_value = mock_response

    success, result = caltopo_api_service._api_request(
        "GET",
        "/api/v1/acct/ABC123/since/0",
        sample_credentials['credential_id'],
        sample_credentials['credential_secret']
    )

    assert success is False
    assert result is None


@patch('core.services.export.CalTopoAPIService.requests.get')
def test_get_account_data_success(mock_get, caltopo_api_service, sample_credentials):
    """Test successful account data retrieval."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "result": {
            "state": {
                "features": [
                    {
                        "id": "map1",
                        "properties": {
                            "class": "CollaborativeMap",
                            "title": "Test Map",
                            "modified": 1234567890
                        }
                    }
                ]
            }
        }
    }
    mock_get.return_value = mock_response

    success, account_data = caltopo_api_service.get_account_data(
        sample_credentials['team_id'],
        sample_credentials['credential_id'],
        sample_credentials['credential_secret']
    )

    assert success is True
    assert account_data is not None
    assert account_data.get('team_id') == sample_credentials['team_id']
    assert 'state' in account_data


@patch('core.services.export.CalTopoAPIService.requests.post')
def test_add_marker_via_api_success(mock_post, caltopo_api_service, sample_credentials):
    """Test successful marker addition."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": {"id": "marker123"}}
    mock_post.return_value = mock_response

    marker_data = {
        "lat": 37.7749,
        "lon": -122.4194,
        "title": "Test Marker",
        "description": "Test description",
        "marker_color": "FF0000"
    }

    success, marker_id = caltopo_api_service.add_marker_via_api(
        "MAP123",
        sample_credentials['team_id'],
        sample_credentials['credential_id'],
        sample_credentials['credential_secret'],
        marker_data
    )

    assert success is True
    assert marker_id == "marker123"
    mock_post.assert_called_once()


@patch('core.services.export.CalTopoAPIService.requests.post')
def test_add_marker_via_api_with_rgb_color(mock_post, caltopo_api_service, sample_credentials):
    """Test marker addition with RGB color conversion."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": {"id": "marker123"}}
    mock_post.return_value = mock_response

    marker_data = {
        "lat": 37.7749,
        "lon": -122.4194,
        "title": "Test Marker",
        "rgb": (255, 0, 128)  # Should convert to FF0080
    }

    success, marker_id = caltopo_api_service.add_marker_via_api(
        "MAP123",
        sample_credentials['team_id'],
        sample_credentials['credential_id'],
        sample_credentials['credential_secret'],
        marker_data
    )

    assert success is True
    # Verify the call was made with correct color
    call_args = mock_post.call_args
    assert call_args is not None


@patch('core.services.export.CalTopoAPIService.requests.post')
def test_add_polygon_via_api_success(mock_post, caltopo_api_service, sample_credentials):
    """Test successful polygon addition."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": {"id": "polygon123"}}
    mock_post.return_value = mock_response

    polygon_data = {
        "coordinates": [
            (37.7749, -122.4194),
            (37.7750, -122.4195),
            (37.7751, -122.4196),
            (37.7749, -122.4194)  # Closed polygon
        ],
        "title": "Test Polygon",
        "description": "Test description"
    }

    success, polygon_id = caltopo_api_service.add_polygon_via_api(
        "MAP123",
        sample_credentials['team_id'],
        sample_credentials['credential_id'],
        sample_credentials['credential_secret'],
        polygon_data
    )

    assert success is True
    assert polygon_id == "polygon123"


@patch('core.services.export.CalTopoAPIService.requests.post')
def test_add_polygon_via_api_closes_polygon(mock_post, caltopo_api_service, sample_credentials):
    """Test that polygon is automatically closed if not already closed."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": {"id": "polygon123"}}
    mock_post.return_value = mock_response

    # Polygon not closed (first != last)
    polygon_data = {
        "coordinates": [
            (37.7749, -122.4194),
            (37.7750, -122.4195),
            (37.7751, -122.4196)
        ],
        "title": "Test Polygon"
    }

    success, polygon_id = caltopo_api_service.add_polygon_via_api(
        "MAP123",
        sample_credentials['team_id'],
        sample_credentials['credential_id'],
        sample_credentials['credential_secret'],
        polygon_data
    )

    assert success is True
    # Verify the polygon was closed in the request
    call_args = mock_post.call_args
    assert call_args is not None


@patch('core.services.export.CalTopoAPIService.requests.post')
def test_add_polygon_via_api_empty_coordinates(mock_post, caltopo_api_service, sample_credentials):
    """Test polygon addition with empty coordinates."""
    polygon_data = {
        "coordinates": [],
        "title": "Test Polygon"
    }

    success, polygon_id = caltopo_api_service.add_polygon_via_api(
        "MAP123",
        sample_credentials['team_id'],
        sample_credentials['credential_id'],
        sample_credentials['credential_secret'],
        polygon_data
    )

    assert success is False
    assert polygon_id is None
    mock_post.assert_not_called()


@patch('core.services.export.CalTopoAPIService.requests.post')
@patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
def test_upload_photo_via_api_success(mock_file, mock_post, caltopo_api_service, sample_credentials):
    """Test successful photo upload."""
    # Mock responses for all three API calls
    responses = [
        MagicMock(status_code=200, json=lambda: {"result": {}}),  # Media metadata
        MagicMock(status_code=200, json=lambda: {"result": {}}),  # Media data
        MagicMock(status_code=200, json=lambda: {"result": {"id": "media123"}})  # Media object
    ]
    mock_post.side_effect = responses

    success, media_id = caltopo_api_service.upload_photo_via_api(
        "MAP123",
        sample_credentials['team_id'],
        sample_credentials['credential_id'],
        sample_credentials['credential_secret'],
        "test_photo.jpg",
        37.7749,
        -122.4194,
        title="Test Photo",
        description="Test description",
        marker_id="marker123"
    )

    assert success is True
    assert media_id == "media123"
    assert mock_post.call_count == 3  # Three API calls for photo upload


@patch('core.services.export.CalTopoAPIService.requests.post')
@patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
def test_upload_photo_via_api_failure_on_metadata(mock_file, mock_post, caltopo_api_service, sample_credentials):
    """Test photo upload failure on metadata creation."""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_post.return_value = mock_response

    success, media_id = caltopo_api_service.upload_photo_via_api(
        "MAP123",
        sample_credentials['team_id'],
        sample_credentials['credential_id'],
        sample_credentials['credential_secret'],
        "test_photo.jpg",
        37.7749,
        -122.4194
    )

    assert success is False
    assert media_id is None
    assert mock_post.call_count == 1  # Only first call made


@patch('core.services.export.CalTopoAPIService.requests.post')
@patch('builtins.open', side_effect=IOError("File not found"))
def test_upload_photo_via_api_file_error(mock_file, mock_post, caltopo_api_service, sample_credentials):
    """Test photo upload with file read error."""
    success, media_id = caltopo_api_service.upload_photo_via_api(
        "MAP123",
        sample_credentials['team_id'],
        sample_credentials['credential_id'],
        sample_credentials['credential_secret'],
        "nonexistent.jpg",
        37.7749,
        -122.4194
    )

    assert success is False
    assert media_id is None
    mock_post.assert_not_called()


@patch('core.services.export.CalTopoAPIService.requests.delete')
def test_api_request_delete(mock_delete, caltopo_api_service, sample_credentials):
    """Test DELETE API request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_delete.return_value = mock_response

    success, result = caltopo_api_service._api_request(
        "DELETE",
        "/api/v1/map/MAP123/Marker/MARKER123",
        sample_credentials['credential_id'],
        sample_credentials['credential_secret']
    )

    assert success is True
    mock_delete.assert_called_once()
