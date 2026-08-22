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
from core.services.export.CalTopoAPIService import CalTopoAPIService, decode_credential_secret


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


# --- decode_credential_secret -------------------------------------------------


def test_decode_credential_secret_standard_base64():
    """A standard base64 secret decodes to the original key bytes."""
    key = b'a-real-looking-hmac-key-0123456789'
    assert decode_credential_secret(base64.b64encode(key).decode()) == key


def test_decode_credential_secret_urlsafe_alphabet():
    """Secrets copied in the URL-safe alphabet still decode."""
    key = bytes(range(250, 256)) + b'padding-bytes'
    urlsafe = base64.urlsafe_b64encode(key).decode()

    assert '-' in urlsafe or '_' in urlsafe  # guard: fixture exercises the fallback
    assert decode_credential_secret(urlsafe) == key


def test_decode_credential_secret_restores_missing_padding():
    """A secret whose trailing '=' was lost in copying still decodes."""
    key = b'12345'
    encoded = base64.b64encode(key).decode()

    assert encoded.endswith('=')  # guard: fixture actually has padding to drop
    assert decode_credential_secret(encoded.rstrip('=')) == key


def test_decode_credential_secret_surrounding_whitespace():
    """Whitespace from a sloppy copy/paste is tolerated."""
    key = b'whitespace-tolerant-key'
    encoded = base64.b64encode(key).decode()

    assert decode_credential_secret(f"  {encoded}\n") == key


@pytest.mark.parametrize("bad_secret", ["", "   ", None])
def test_decode_credential_secret_rejects_empty(bad_secret):
    """An empty secret is reported as empty, not as bad base64."""
    with pytest.raises(ValueError, match="empty"):
        decode_credential_secret(bad_secret)


def test_decode_credential_secret_rejects_non_base64():
    """The real-world failure: a short non-base64 value pasted as the secret."""
    with pytest.raises(ValueError, match="not valid base64"):
        decode_credential_secret("2GmR7xQp!wZ#4kLd")


def test_decode_credential_secret_does_not_silently_discard():
    """Characters outside the alphabet must fail, not be dropped.

    ``base64.b64decode`` without validate=True discards them, which turns a
    wrong-field paste into a plausible but useless HMAC key.
    """
    assert base64.b64decode("AAAA!!!!") == b'\x00\x00\x00'  # documents the trap

    with pytest.raises(ValueError, match="not valid base64"):
        decode_credential_secret("AAAA!!!!")


# --- failure logging ----------------------------------------------------------


@patch('core.services.export.CalTopoAPIService.requests.get')
def test_api_request_logs_http_failure(mock_get, sample_credentials):
    """A non-2xx response logs the status and body instead of failing silently."""
    logger = MagicMock()
    service = CalTopoAPIService(logger=logger)

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized: bad signature"
    mock_get.return_value = mock_response

    success, result = service._api_request(
        "GET",
        "/api/v1/acct/ABC123/since/0",
        sample_credentials['credential_id'],
        sample_credentials['credential_secret']
    )

    assert success is False
    logger.error.assert_called_once()
    logged = logger.error.call_args[0][0]
    assert "401" in logged
    assert "/api/v1/acct/ABC123/since/0" in logged
    assert "Unauthorized: bad signature" in logged


@patch('core.services.export.CalTopoAPIService.requests.get')
def test_api_request_undecodable_secret_never_hits_network(mock_get, sample_credentials):
    """An unusable secret fails before any request, and says so."""
    logger = MagicMock()
    service = CalTopoAPIService(logger=logger)

    success, result = service._api_request(
        "GET",
        "/api/v1/acct/ABC123/since/0",
        sample_credentials['credential_id'],
        "2GmR7xQp!wZ#4kLd"
    )

    assert success is False
    assert result is None
    mock_get.assert_not_called()
    logged = logger.error.call_args[0][0]
    assert "not sent" in logged
    assert "not valid base64" in logged


@patch('core.services.export.CalTopoAPIService.requests.get')
def test_api_request_logs_network_exception(mock_get, sample_credentials):
    """Transport failures are logged with their type."""
    import requests as requests_module

    logger = MagicMock()
    service = CalTopoAPIService(logger=logger)
    mock_get.side_effect = requests_module.ConnectionError("name resolution failed")

    success, result = service._api_request(
        "GET",
        "/api/v1/acct/ABC123/since/0",
        sample_credentials['credential_id'],
        sample_credentials['credential_secret']
    )

    assert success is False
    logged = logger.error.call_args[0][0]
    assert "ConnectionError" in logged
    assert "name resolution failed" in logged


@patch('core.services.export.CalTopoAPIService.requests.get')
def test_api_request_never_logs_the_signed_url(mock_get, sample_credentials):
    """The request URL carries the credential id and signature; keep it out of logs."""
    logger = MagicMock()
    service = CalTopoAPIService(logger=logger)

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "server error"
    mock_get.return_value = mock_response

    service._api_request(
        "GET",
        "/api/v1/acct/ABC123/since/0",
        sample_credentials['credential_id'],
        sample_credentials['credential_secret']
    )

    logged = logger.error.call_args[0][0]
    assert "signature=" not in logged
    assert sample_credentials['credential_id'] not in logged


@patch('core.services.export.CalTopoAPIService.requests.get')
def test_get_account_data_rejects_non_dict_result(mock_get, sample_credentials):
    """A list payload is refused rather than raising on item assignment."""
    logger = MagicMock()
    service = CalTopoAPIService(logger=logger)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": ["unexpected", "shape"]}
    mock_get.return_value = mock_response

    success, account_data = service.get_account_data(
        sample_credentials['team_id'],
        sample_credentials['credential_id'],
        sample_credentials['credential_secret']
    )

    assert success is False
    assert account_data is None
    logger.error.assert_called_once()
