"""
CalTopoService - Handles CalTopo authentication and API interactions.

This service manages session authentication, map retrieval, and marker/waypoint
creation on CalTopo maps.
"""

import base64
import json
import os
import requests
import time
import uuid
from http.cookiejar import Cookie
from typing import Any, Dict, List, Union
from PySide6.QtCore import QSettings

from core.services.LoggerService import LoggerService
from core.services.export.PhotoPayload import encode_photo


class CalTopoService:
    """
    Service for interacting with CalTopo using a captured browser session.

    Handles session management, map retrieval, and creation of markers,
    shapes and photo attachments.

    All writes go out over plain HTTP with the cookies harvested from the
    embedded browser. Driving them from JavaScript inside the page instead
    means megabyte-sized image payloads have to be interpolated into script
    source, and completion can only be observed through a callback channel that
    proved unreliable - so uploads were abandoned mid-flight when the browser
    was torn down. Requests carry the same Referer/Origin/CSRF headers a real
    browser would send.
    """

    CALTOPO_BASE_URL = "https://caltopo.com"
    CALTOPO_API_BASE = "https://caltopo.com/api/v1"

    # Photo payloads are base64 drone stills; they need far longer than a
    # normal API call.
    UPLOAD_TIMEOUT = 120
    DEFAULT_TIMEOUT = 30

    def __init__(self, logger=None, settings=None):
        """
        Initialize the CalTopo service.

        Sets up the HTTP session and loads any previously saved session cookies.

        Args:
            logger: Optional LoggerService for diagnostics.
            settings: Optional QSettings backing store. Tests must pass an
                isolated one - saving fixture cookies into the shared store
                destroys the user's real logged-in CalTopo session.
        """
        self.session = requests.Session()
        self.settings = settings if settings is not None else QSettings("ADIAT", "CalTopo")
        self.logger = logger or LoggerService()
        self._csrf_tokens = {}
        self._creator_ids = {}
        self._account_id = None
        self._load_session()

    def _serialize_cookies(self):
        """
        Convert the current cookie jar into a JSON-serializable list.

        Returns:
            list: List of dictionaries containing cookie attributes.
        """
        serialized = []
        for cookie in self.session.cookies:
            serialized.append({
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'secure': cookie.secure,
                'expires': cookie.expires,
                'rest': cookie._rest,
                'version': cookie.version,
                'port': cookie.port,
                'port_specified': cookie.port_specified,
                'domain_initial_dot': cookie.domain_initial_dot,
                'domain_specified': cookie.domain_specified,
                'path_specified': cookie.path_specified,
                'discard': cookie.discard,
                'comment': cookie.comment,
                'comment_url': cookie.comment_url
            })
        return serialized

    def _deserialize_cookies(self, serialized):
        """
        Populate the session cookie jar from serialized data.

        Args:
            serialized: List of cookie dictionaries to deserialize.
        """
        self.session.cookies.clear()
        if not serialized:
            return

        for cookie_data in serialized:
            try:
                # Ensure we have required fields
                if 'name' not in cookie_data or 'value' not in cookie_data:
                    continue

                # Normalize domain - ensure it works with requests
                domain = cookie_data.get('domain', '.caltopo.com')
                # Remove leading dot if present for requests library compatibility
                if domain.startswith('.'):
                    domain = domain[1:]

                cookie = Cookie(
                    version=cookie_data.get('version', 0),
                    name=cookie_data['name'],
                    value=cookie_data['value'],
                    port=cookie_data.get('port'),
                    port_specified=cookie_data.get('port_specified', False),
                    domain=domain,
                    domain_specified=cookie_data.get('domain_specified', bool(domain)),
                    domain_initial_dot=cookie_data.get('domain_initial_dot', False),
                    path=cookie_data.get('path', '/'),
                    path_specified=cookie_data.get('path_specified', bool(cookie_data.get('path'))),
                    secure=cookie_data.get('secure', False),
                    expires=cookie_data.get('expires'),
                    discard=cookie_data.get('discard', False),
                    comment=cookie_data.get('comment'),
                    comment_url=cookie_data.get('comment_url'),
                    rest=cookie_data.get('rest') or {},
                    rfc2109=False
                )
                self.session.cookies.set_cookie(cookie)
            except (KeyError, Exception):
                continue

    def _persist_session_cookies(self):
        """
        Persist the current cookie jar to settings.

        Saves the serialized cookies to QSettings for later retrieval.
        """
        serialized = self._serialize_cookies()
        self.settings.setValue("session_cookies", json.dumps(serialized))

    def _load_session(self):
        """
        Load saved session cookies from settings.

        Attempts to restore previously saved session cookies from QSettings.
        """
        cookies_json = self.settings.value("session_cookies", "")
        if cookies_json:
            try:
                cookies = json.loads(cookies_json)
                self._deserialize_cookies(cookies)
            except json.JSONDecodeError:
                pass

    def _normalize_cookies(self, cookies_payload: Union[Dict[str, Any], List[Dict[str, Any]]]):
        """
        Normalize cookies from various formats into a list of cookie dicts.

        Args:
            cookies_payload: Cookies in various formats (list, dict, or nested dict).

        Returns:
            list: Normalized list of cookie dictionaries.
        """
        if not cookies_payload:
            return []

        if isinstance(cookies_payload, list):
            return cookies_payload

        # Support structures like {'cookies': [...]}
        if isinstance(cookies_payload, dict):
            if 'cookies' in cookies_payload and isinstance(cookies_payload['cookies'], list):
                return cookies_payload['cookies']

            # Legacy dict of name -> value
            normalized = []
            for name, value in cookies_payload.items():
                if name.startswith('__'):
                    continue
                normalized.append({
                    'name': name,
                    'value': value,
                    'domain': 'caltopo.com',  # No leading dot for requests compatibility
                    'path': '/',
                    'secure': True,
                    'expires': None,
                    'rest': {},
                    'discard': True,
                    'version': 0,
                    'port': None,
                    'port_specified': False,
                    'domain_initial_dot': False,
                    'domain_specified': True,
                    'path_specified': True,
                    'comment': None,
                    'comment_url': None
                })
            return normalized

        return []

    SESSION_COOKIE_NAME = "SESSION"

    def save_session(self, cookies_payload: Union[Dict[str, Any], List[Dict[str, Any]]]):
        """Persist cookies captured from the CalTopo web view.

        A capture that lacks the session cookie authenticates as nobody, so it
        is refused rather than written over a session that still works.

        Args:
            cookies_payload: List or dict containing cookie metadata
        """
        cookies_list = self._normalize_cookies(cookies_payload)
        if not cookies_list:
            return

        if not any(cookie.get('name') == self.SESSION_COOKIE_NAME for cookie in cookies_list):
            self.logger.warning(
                f"Refusing to store a CalTopo session with no "
                f"'{self.SESSION_COOKIE_NAME}' cookie; keeping the existing one."
            )
            return

        # Load cookies into the current session so new requests use them immediately
        self._deserialize_cookies(cookies_list)
        self._persist_session_cookies()

    def set_account_id(self, account_id):
        """Record the signed-in CalTopo account, used to attribute media.

        Args:
            account_id (str): Account id read from the page, or None.
        """
        if account_id:
            self._account_id = account_id

    def clear_session(self):
        """
        Clear stored session data.

        Removes saved cookies from settings and clears the current session.
        """
        self.settings.remove("session_cookies")
        self.session.cookies.clear()

    def is_authenticated(self):
        """
        Check if user has valid session.

        Returns:
            bool: True if session appears valid, False otherwise
        """
        # Simple check - try to access user data endpoint
        try:
            response = self.session.get(
                f"{self.CALTOPO_API_BASE}/account/maps",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    def get_user_maps(self):
        """
        Retrieve list of user's CalTopo maps.

        Returns:
            list: List of map dictionaries with 'id', 'title', 'modified' keys
                  Returns empty list on error
        """
        try:
            response = self.session.get(
                f"{self.CALTOPO_API_BASE}/account/maps",
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                # Parse the response to extract map information
                maps = []
                if isinstance(data, list):
                    for map_data in data:
                        maps.append({
                            'id': map_data.get('id', ''),
                            'title': map_data.get('title', 'Untitled Map'),
                            'modified': map_data.get('modified', '')
                        })
                return maps
            return []
        except Exception:
            return []

    def _get_csrf_token(self, map_id):
        """
        Get the CSRF token for a map, caching it for the session.

        Args:
            map_id (str): CalTopo map ID

        Returns:
            str: CSRF token if found, None otherwise
        """
        if map_id in self._csrf_tokens:
            return self._csrf_tokens[map_id]

        # Read only what the captured session already carries. Fetching the map
        # page to hunt for a token used to run on self.session, and presenting
        # an unrecognised session makes CalTopo hand back a fresh anonymous one
        # that requests writes straight over the captured cookie - quietly
        # downgrading a real login to an anonymous session.
        token = self.session.cookies.get('csrftoken') or self.session.cookies.get('XSRF-TOKEN')

        self._csrf_tokens[map_id] = token
        return token

    def _response_snippet(self, response, limit=500):
        """Short excerpt of a response body for logging.

        Args:
            response: requests Response object.
            limit (int): Maximum characters to include.

        Returns:
            str: Body excerpt or a placeholder.
        """
        try:
            body = str(response.text or "").strip()
        except Exception:
            return "<response body unavailable>"
        if not body:
            return "<empty response body>"
        return body[:limit] + ("..." if len(body) > limit else "")

    def _post_feature(self, map_id, endpoint, payload, timeout=None):
        """POST a JSON payload the way the CalTopo web app does.

        CalTopo expects form-urlencoded data with the JSON in a field named
        ``json`` - not a raw application/json body. Referer/Origin are sent
        explicitly because a real browser supplies them for free.

        Args:
            map_id (str): Map the request relates to (used for Referer/CSRF).
            endpoint (str): Path below the API base, e.g. "/map/ABC/Marker".
            payload (dict): Feature payload.
            timeout (int): Request timeout; defaults to DEFAULT_TIMEOUT.

        Returns:
            tuple: (success: bool, object_id: str or None)
        """
        url = f"{self.CALTOPO_API_BASE}{endpoint}"
        headers = {
            'Referer': f'{self.CALTOPO_BASE_URL}/m/{map_id}',
            'Origin': self.CALTOPO_BASE_URL,
        }

        csrf_token = self._get_csrf_token(map_id)
        if csrf_token:
            headers['X-CSRFToken'] = csrf_token
            headers['X-XSRF-TOKEN'] = csrf_token

        try:
            response = self.session.post(
                url,
                data={'json': json.dumps(payload)},
                headers=headers,
                timeout=timeout or self.DEFAULT_TIMEOUT
            )
        except requests.RequestException as e:
            self.logger.error(f"CalTopo POST {endpoint} failed: {type(e).__name__}: {e}")
            return False, None

        if response.status_code not in (200, 201):
            self.logger.error(
                f"CalTopo POST {endpoint} failed: HTTP {response.status_code} "
                f"- {self._response_snippet(response)}"
            )
            return False, None

        try:
            body = response.json()
        except ValueError:
            self.logger.error(
                f"CalTopo POST {endpoint} returned a non-JSON body: "
                f"{self._response_snippet(response)}"
            )
            return False, None

        if not isinstance(body, dict):
            self.logger.error(f"CalTopo POST {endpoint} returned an unexpected payload shape")
            return False, None

        # A 200 with status "error" is still a failure.
        if str(body.get('status', 'ok')).lower() == 'error':
            self.logger.error(
                f"CalTopo POST {endpoint} rejected: {self._response_snippet(response)}"
            )
            return False, None

        result = body.get('result')
        if isinstance(result, dict):
            return True, result.get('id')
        return True, None

    def add_marker_to_map(self, map_id, marker_data):
        """
        Add a marker/waypoint to a CalTopo map.

        Args:
            map_id (str): CalTopo map ID
            marker_data (dict): Marker data with 'lat', 'lon', 'title',
                'description', and optionally 'rgb' or 'marker_color'.

        Returns:
            tuple: (success: bool, marker_id: str or None)
        """
        marker_color = marker_data.get('marker_color')
        if not marker_color and marker_data.get('rgb'):
            try:
                r, g, b = marker_data['rgb']
                marker_color = f"{r:02X}{g:02X}{b:02X}"
            except Exception:
                marker_color = None
        if not marker_color:
            marker_color = 'FF0000'

        # Field shapes follow the known-working ADIAT Flight client: a null
        # top-level 'id', and a numeric marker-size.
        marker_payload = {
            'type': 'Feature',
            'id': None,
            'geometry': {
                'type': 'Point',
                'coordinates': [marker_data['lon'], marker_data['lat']]
            },
            'properties': {
                'title': marker_data.get('title', ''),
                'description': marker_data.get('description', ''),
                'marker-size': marker_data.get('marker_size', 1),
                'marker-symbol': marker_data.get('marker_symbol', 'a:4'),
                'marker-color': marker_color,
                'marker-rotation': marker_data.get('marker_rotation', 0)
            }
        }

        return self._post_feature(map_id, f"/map/{map_id}/Marker", marker_payload)

    def add_shape_to_map(self, map_id, polygon_data):
        """
        Add a polygon shape to a CalTopo map.

        Args:
            map_id (str): CalTopo map ID
            polygon_data (dict): Polygon with 'coordinates' as (lat, lon)
                tuples, plus 'title' and 'description'.

        Returns:
            tuple: (success: bool, shape_id: str or None)
        """
        coords = list(polygon_data.get('coordinates') or [])
        if not coords:
            return False, None

        # GeoJSON rings must be closed.
        if coords[0] != coords[-1]:
            coords.append(coords[0])

        shape_payload = {
            'type': 'Feature',
            'properties': {
                'title': polygon_data.get('title', ''),
                'description': polygon_data.get('description', ''),
                'folderId': None,
                'stroke-width': 2,
                'stroke-opacity': 1,
                'stroke': '#FF0000',
                'fill-opacity': 0.1,
                'fill': '#FF0000'
            },
            'geometry': {
                'type': 'Polygon',
                'coordinates': [[[lon, lat] for lat, lon in coords]]
            }
        }

        return self._post_feature(map_id, f"/map/{map_id}/Shape", shape_payload)

    def _get_creator_id(self, map_id):
        """Best-effort creator id for media objects, cached per map.

        Mirrors what the web app attributes uploads to; falls back to a literal
        when the map has no features to learn from.

        Args:
            map_id (str): CalTopo map ID

        Returns:
            str: Creator identifier.
        """
        # The account read from the signed-in page is authoritative; media
        # attributed to an invented literal is registered against an account
        # that does not exist.
        if self._account_id:
            return self._account_id

        if map_id in self._creator_ids:
            return self._creator_ids[map_id]

        creator = 'ADIAT_User'
        try:
            response = self.session.get(
                f"{self.CALTOPO_API_BASE}/map/{map_id}/since/0", timeout=self.DEFAULT_TIMEOUT
            )
            if response.status_code in (200, 201):
                state = (response.json().get('result') or {}).get('state') or {}
                for feature in state.get('features') or []:
                    found = (feature.get('properties') or {}).get('creator')
                    if found:
                        creator = found
                        break
        except (requests.RequestException, ValueError, AttributeError) as e:
            self.logger.warning(f"Could not determine CalTopo creator id for map {map_id}: {e}")

        self._creator_ids[map_id] = creator
        return creator

    def upload_photo_for_marker(self, map_id, marker_id, photo_path, lat, lon,
                                title=None, description=""):
        """
        Attach a photo to a marker using CalTopo's three-step media flow.

        Args:
            map_id (str): CalTopo map ID
            marker_id (str): Marker to attach the photo to
            photo_path (str): Path to the image file
            lat (float): Latitude for the media object
            lon (float): Longitude for the media object
            title (str, optional): Media title; defaults to the file name
            description (str): Media description

        Returns:
            tuple: (success: bool, media_object_id: str or None)
        """
        try:
            base64_data, filename = encode_photo(photo_path, logger=self.logger)
        except OSError as e:
            self.logger.error(f"Could not read photo {photo_path}: {e}")
            return False, None

        media_id = str(uuid.uuid4())

        # Step 1: register the media object.
        success, _ = self._post_feature(
            map_id,
            f"/media/{media_id}",
            {'properties': {'creator': self._get_creator_id(map_id), 'filename': filename}}
        )
        if not success:
            self.logger.error(f"CalTopo photo upload failed at metadata step for {filename}")
            return False, None

        # Step 2: send the image bytes.
        success, _ = self._post_feature(
            map_id,
            f"/media/{media_id}/data",
            {'data': base64_data},
            timeout=self.UPLOAD_TIMEOUT
        )
        if not success:
            self.logger.error(f"CalTopo photo upload failed while sending data for {filename}")
            return False, None

        # Step 3: attach it to the marker.
        success, media_object_id = self._post_feature(
            map_id,
            f"/map/{map_id}/MapMediaObject",
            {
                'type': 'Feature',
                'geometry': {'type': 'Point', 'coordinates': [lon, lat]},
                'properties': {
                    'parentId': f'Marker:{marker_id}',
                    'backendMediaId': media_id,
                    'created': int(time.time() * 1000),
                    'title': title or filename,
                    'heading': None,
                    'description': description,
                    'marker-symbol': 'aperture',
                    'marker-color': '#FFFFFF',
                    'marker-size': 1
                }
            }
        )
        if not success:
            self.logger.error(f"CalTopo photo upload failed while attaching {filename} to marker {marker_id}")
            return False, None

        return True, media_object_id
