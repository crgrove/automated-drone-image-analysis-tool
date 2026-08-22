"""
Comprehensive tests for CalTopoService.

Tests CalTopo API interactions and authentication.
"""

import base64
import json
import pytest
import requests
from unittest.mock import patch, MagicMock
from core.services.export.CalTopoService import CalTopoService


@pytest.fixture
def caltopo_service(isolated_qsettings):
    """A CalTopoService backed by throwaway settings.

    save_session() writes cookies; against the real store that would overwrite
    the user's actual logged-in CalTopo browser session.
    """
    return CalTopoService(settings=isolated_qsettings)


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


def test_save_session_refuses_a_capture_without_the_session_cookie(caltopo_service):
    """A capture missing SESSION authenticates as nobody and must be refused.

    CalTopo's SESSION cookie is HttpOnly, so a capture can easily come back
    holding only the incidental cookies. Storing that would overwrite a
    working session and turn every subsequent write into a silent 401.
    """
    good = [{'name': 'SESSION', 'value': 'real-session', 'domain': 'caltopo.com', 'path': '/'}]
    caltopo_service.save_session(good)
    stored_before = caltopo_service.settings.value("session_cookies", "")
    assert 'real-session' in stored_before

    caltopo_service.logger = MagicMock()
    caltopo_service.save_session([{'name': '_ssid', 'value': 'incidental',
                                   'domain': 'caltopo.com', 'path': '/'}])

    assert caltopo_service.settings.value("session_cookies", "") == stored_before
    assert caltopo_service.logger.warning.called


def test_save_session_accepts_a_capture_with_the_session_cookie(caltopo_service):
    """A real capture still replaces the stored session."""
    caltopo_service.save_session([
        {'name': 'SESSION', 'value': 'first', 'domain': 'caltopo.com', 'path': '/'}
    ])
    caltopo_service.save_session([
        {'name': 'SESSION', 'value': 'second', 'domain': 'caltopo.com', 'path': '/'}
    ])

    assert 'second' in caltopo_service.settings.value("session_cookies", "")


def test_csrf_lookup_does_not_touch_the_network(caltopo_service):
    """Probing for a token must not issue a request on the export session.

    Presenting an unrecognised session makes CalTopo hand back a fresh
    anonymous one, which requests writes straight over the captured cookie -
    silently downgrading a real login.
    """
    with patch.object(caltopo_service.session, 'get') as mock_get:
        caltopo_service._get_csrf_token('MAP1')

    mock_get.assert_not_called()


def test_post_feature_rejects_an_error_status_in_a_200_body(caltopo_service):
    """A 200 carrying status "error" is a failure, not a success."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {'status': 'error', 'message': 'nope'}
    response.text = '{"status": "error"}'

    caltopo_service.logger = MagicMock()

    with patch.object(caltopo_service.session, 'post', return_value=response):
        success, object_id = caltopo_service.add_marker_to_map(
            'MAP1', {'lat': 1.0, 'lon': 2.0, 'title': 't'}
        )

    assert (success, object_id) == (False, None)
    assert caltopo_service.logger.error.called


def test_post_feature_rejects_a_non_json_body(caltopo_service):
    """An unparseable body must not be reported as success."""
    response = MagicMock()
    response.status_code = 200
    response.json.side_effect = ValueError("no json")
    response.text = '<html>maintenance</html>'

    caltopo_service.logger = MagicMock()

    with patch.object(caltopo_service.session, 'post', return_value=response):
        success, object_id = caltopo_service.add_marker_to_map(
            'MAP1', {'lat': 1.0, 'lon': 2.0, 'title': 't'}
        )

    assert (success, object_id) == (False, None)


def test_media_is_attributed_to_the_signed_in_account(caltopo_service, tmp_path):
    """Media must carry the real account id, not an invented literal."""
    photo = tmp_path / "p.jpg"
    photo.write_bytes(b'bytes')

    caltopo_service.set_account_id('ACCT123')

    responses = [_ok_response({'result': {'id': 'media-1'}}),
                 _ok_response({'result': {}}),
                 _ok_response({'result': {'id': 'obj-1'}})]

    with patch.object(caltopo_service.session, 'post', side_effect=responses) as mock_post:
        caltopo_service.upload_photo_for_marker('MAP1', 'm1', str(photo), 1.0, 2.0)

    metadata = json.loads(mock_post.call_args_list[0].kwargs['data']['json'])
    assert metadata['properties']['creator'] == 'ACCT123'


def test_session_storage_is_isolated_from_real_user_settings(caltopo_service):
    """Fixture cookies must not overwrite the user's real CalTopo login."""
    assert "adiat-test-qsettings-" in caltopo_service.settings.fileName()


# --- HTTP writes --------------------------------------------------------------


@pytest.fixture
def posting_service(caltopo_service):
    """Service with CSRF/creator lookups stubbed so POSTs can be inspected."""
    caltopo_service._csrf_tokens['MAP1'] = 'csrf-token'
    caltopo_service._creator_ids['MAP1'] = 'creator-1'
    return caltopo_service


def _ok_response(payload=None):
    """Build a 200 response returning the given JSON body."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = payload if payload is not None else {}
    response.text = '{}'
    return response


def test_add_marker_posts_form_encoded_json_with_browser_headers(posting_service):
    """CalTopo wants form-encoded data in a field named 'json', plus Referer/Origin.

    A raw application/json body is rejected, and without Referer/Origin/CSRF the
    session is treated as cross-site.
    """
    response = _ok_response({'result': {'id': 'marker-1'}})

    with patch.object(posting_service.session, 'post', return_value=response) as mock_post:
        success, marker_id = posting_service.add_marker_to_map(
            'MAP1', {'lat': 30.65, 'lon': -97.95, 'title': 'AOI 1', 'description': 'd'}
        )

    assert (success, marker_id) == (True, 'marker-1')

    args, kwargs = mock_post.call_args
    assert args[0] == 'https://caltopo.com/api/v1/map/MAP1/Marker'
    assert set(kwargs['data']) == {'json'}          # form field, not a JSON body
    assert kwargs['headers']['Referer'] == 'https://caltopo.com/m/MAP1'
    assert kwargs['headers']['Origin'] == 'https://caltopo.com'
    assert kwargs['headers']['X-CSRFToken'] == 'csrf-token'
    assert kwargs['headers']['X-XSRF-TOKEN'] == 'csrf-token'

    payload = json.loads(kwargs['data']['json'])
    assert payload['geometry']['coordinates'] == [-97.95, 30.65]  # GeoJSON is lon,lat
    assert payload['properties']['title'] == 'AOI 1'


def test_add_marker_converts_rgb_to_hex(posting_service):
    """AOI colour comes through as an RGB tuple and must reach CalTopo as hex."""
    response = _ok_response({'result': {'id': 'marker-1'}})

    with patch.object(posting_service.session, 'post', return_value=response) as mock_post:
        posting_service.add_marker_to_map(
            'MAP1', {'lat': 1.0, 'lon': 2.0, 'title': 't', 'rgb': (255, 0, 57)}
        )

    payload = json.loads(mock_post.call_args.kwargs['data']['json'])
    assert payload['properties']['marker-color'] == 'FF0039'


def test_add_marker_reports_http_failure(posting_service):
    """A rejected write is reported and logged, not silently swallowed."""
    response = MagicMock()
    response.status_code = 403
    response.text = 'Forbidden'

    posting_service.logger = MagicMock()

    with patch.object(posting_service.session, 'post', return_value=response):
        success, marker_id = posting_service.add_marker_to_map(
            'MAP1', {'lat': 1.0, 'lon': 2.0, 'title': 't'}
        )

    assert (success, marker_id) == (False, None)
    logged = posting_service.logger.error.call_args[0][0]
    assert '403' in logged and 'Forbidden' in logged


def test_add_shape_closes_the_polygon_ring(posting_service):
    """GeoJSON polygons must be explicitly closed."""
    response = _ok_response({'result': {'id': 'shape-1'}})

    with patch.object(posting_service.session, 'post', return_value=response) as mock_post:
        success, shape_id = posting_service.add_shape_to_map(
            'MAP1',
            {'coordinates': [(1.0, 2.0), (1.0, 3.0), (2.0, 3.0)],
             'title': 'Coverage', 'description': 'd'}
        )

    assert (success, shape_id) == (True, 'shape-1')
    payload = json.loads(mock_post.call_args.kwargs['data']['json'])
    ring = payload['geometry']['coordinates'][0]
    assert ring[0] == ring[-1]
    assert ring[0] == [2.0, 1.0]  # lon, lat


def test_upload_photo_runs_the_three_step_media_flow(posting_service, tmp_path):
    """Photos need media create -> data -> attach, in that order."""
    photo = tmp_path / "DJI_0021.JPG"
    photo.write_bytes(b'\xff\xd8\xff\xe0 fake jpeg bytes')

    responses = [
        _ok_response({'result': {'id': 'media-1'}}),
        _ok_response({'result': {}}),
        _ok_response({'result': {'id': 'mediaobject-1'}}),
    ]

    with patch.object(posting_service.session, 'post', side_effect=responses) as mock_post:
        success, media_object_id = posting_service.upload_photo_for_marker(
            'MAP1', 'marker-1', str(photo), 30.65, -97.95, title='AOI 1', description='d'
        )

    assert (success, media_object_id) == (True, 'mediaobject-1')
    assert mock_post.call_count == 3

    urls = [call.args[0] for call in mock_post.call_args_list]
    assert '/api/v1/media/' in urls[0]
    assert urls[1].endswith('/data')
    assert urls[2] == 'https://caltopo.com/api/v1/map/MAP1/MapMediaObject'

    # The image goes out as an ordinary form field, not embedded in a script.
    data_payload = json.loads(mock_post.call_args_list[1].kwargs['data']['json'])
    assert data_payload['data'] == base64.b64encode(photo.read_bytes()).decode()

    attach_payload = json.loads(mock_post.call_args_list[2].kwargs['data']['json'])
    assert attach_payload['properties']['parentId'] == 'Marker:marker-1'
    assert attach_payload['properties']['backendMediaId']


def test_upload_photo_uses_a_long_timeout_for_image_data(posting_service, tmp_path):
    """Drone stills are large; the data step must not use the short timeout."""
    photo = tmp_path / "big.jpg"
    photo.write_bytes(b'x' * 2048)

    responses = [_ok_response({'result': {'id': 'media-1'}}),
                 _ok_response({'result': {}}),
                 _ok_response({'result': {'id': 'obj-1'}})]

    with patch.object(posting_service.session, 'post', side_effect=responses) as mock_post:
        posting_service.upload_photo_for_marker('MAP1', 'm1', str(photo), 1.0, 2.0)

    assert mock_post.call_args_list[1].kwargs['timeout'] == CalTopoService.UPLOAD_TIMEOUT
    assert mock_post.call_args_list[0].kwargs['timeout'] == CalTopoService.DEFAULT_TIMEOUT


def test_upload_photo_stops_when_a_step_fails(posting_service, tmp_path):
    """A failed metadata step must not go on to send megabytes of data."""
    photo = tmp_path / "photo.jpg"
    photo.write_bytes(b'bytes')

    failure = MagicMock()
    failure.status_code = 500
    failure.text = 'boom'

    posting_service.logger = MagicMock()

    with patch.object(posting_service.session, 'post', return_value=failure) as mock_post:
        success, media_object_id = posting_service.upload_photo_for_marker(
            'MAP1', 'm1', str(photo), 1.0, 2.0
        )

    assert (success, media_object_id) == (False, None)
    assert mock_post.call_count == 1
    assert posting_service.logger.error.called


def test_upload_photo_handles_unreadable_file(posting_service):
    """A missing image is reported, not raised."""
    posting_service.logger = MagicMock()

    success, media_object_id = posting_service.upload_photo_for_marker(
        'MAP1', 'm1', 'does_not_exist.jpg', 1.0, 2.0
    )

    assert (success, media_object_id) == (False, None)
    assert posting_service.logger.error.called


def test_csrf_token_is_read_from_the_captured_session(caltopo_service):
    """The token comes from the cookies we already hold, and is cached."""
    with patch.object(caltopo_service.session.cookies, 'get',
                      side_effect=lambda name: 'abc123' if name == 'csrftoken' else None) as mock_get:
        first = caltopo_service._get_csrf_token('MAP1')
        second = caltopo_service._get_csrf_token('MAP1')

    assert first == second == 'abc123'
    # Cached: the second call does not re-read the jar.
    assert mock_get.call_count == 1


def test_csrf_headers_are_omitted_when_no_token_exists(caltopo_service):
    """CalTopo does not always issue a CSRF cookie; sending nothing is correct."""
    response = _ok_response({'result': {'id': 'm1'}})

    with patch.object(caltopo_service.session.cookies, 'get', return_value=None):
        with patch.object(caltopo_service.session, 'post', return_value=response) as mock_post:
            caltopo_service.add_marker_to_map('MAP1', {'lat': 1.0, 'lon': 2.0, 'title': 't'})

    headers = mock_post.call_args.kwargs['headers']
    assert 'X-CSRFToken' not in headers
    assert headers['Referer'] == 'https://caltopo.com/m/MAP1'


def test_post_feature_survives_network_error(posting_service):
    """A transport failure is logged and reported, not raised at the caller."""
    posting_service.logger = MagicMock()

    with patch.object(posting_service.session, 'post',
                      side_effect=requests.ConnectionError('no route to host')):
        success, object_id = posting_service.add_marker_to_map(
            'MAP1', {'lat': 1.0, 'lon': 2.0, 'title': 't'}
        )

    assert (success, object_id) == (False, None)
    logged = posting_service.logger.error.call_args[0][0]
    assert 'ConnectionError' in logged
