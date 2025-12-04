"""
CalTopoService - Handles CalTopo authentication and API interactions.

This service manages session authentication, map retrieval, and marker/waypoint
creation on CalTopo maps.
"""

import json
import requests
import re
from http.cookiejar import Cookie
from typing import Any, Dict, List, Union
from PySide6.QtCore import QSettings


class CalTopoService:
    """
    Service for interacting with CalTopo API.

    Handles authentication, session management, map retrieval,
    and marker/waypoint creation.
    """

    CALTOPO_BASE_URL = "https://caltopo.com"
    CALTOPO_API_BASE = "https://caltopo.com/api/v1"

    def __init__(self):
        """
        Initialize the CalTopo service.

        Sets up the HTTP session and loads any previously saved session cookies.
        """
        self.session = requests.Session()
        self.settings = QSettings("ADIAT", "CalTopo")
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

    def save_session(self, cookies_payload: Union[Dict[str, Any], List[Dict[str, Any]]]):
        """Persist cookies captured from the CalTopo web view.

        Args:
            cookies_payload: List or dict containing cookie metadata
        """
        cookies_list = self._normalize_cookies(cookies_payload)
        if not cookies_list:
            return

        # Load cookies into the current session so new requests use them immediately
        self._deserialize_cookies(cookies_list)
        self._persist_session_cookies()

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
        Try to get CSRF token from CalTopo map page.

        Args:
            map_id (str): CalTopo map ID

        Returns:
            str: CSRF token if found, None otherwise
        """
        try:
            # Try to get CSRF token from the map page
            response = self.session.get(
                f"{self.CALTOPO_BASE_URL}/m/{map_id}",
                timeout=5
            )

            # Look for CSRF token in cookies
            csrf_token = self.session.cookies.get('csrftoken') or self.session.cookies.get('XSRF-TOKEN')
            if csrf_token:
                return csrf_token

            # Try to parse from page content
            csrf_match = re.search(r'csrf[_-]?token["\']?\s*[:=]\s*["\']([^"\']+)', response.text, re.IGNORECASE)
            if csrf_match:
                return csrf_match.group(1)

            return None
        except Exception:
            return None

    def add_marker_to_map(self, map_id, marker_data):
        """
        Add a marker/waypoint to a CalTopo map.

        Args:
            map_id (str): CalTopo map ID
            marker_data (dict): Marker data with 'lat', 'lon', 'title', 'description'

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # CalTopo marker format (GeoJSON Feature)
            # Based on actual network traffic capture from CalTopo web interface
            marker_properties = {
                'title': marker_data.get('title', ''),
                'description': marker_data.get('description', ''),
                'marker-size': marker_data.get('marker_size', '1'),
                'marker-symbol': marker_data.get('marker_symbol', 'a:4'),
                'marker-color': marker_data.get('marker_color', 'FF0000'),
                'marker-rotation': marker_data.get('marker_rotation', 0)
            }

            marker_payload = {
                'type': 'Feature',
                'class': None,  # Required by CalTopo
                'geometry': {
                    'type': 'Point',
                    'coordinates': [marker_data['lon'], marker_data['lat']]
                },
                'properties': marker_properties
            }

            url = f"{self.CALTOPO_API_BASE}/map/{map_id}/Marker"

            # Try to get CSRF token
            csrf_token = self._get_csrf_token(map_id)

            # Prepare headers
            headers = {
                'Referer': f'{self.CALTOPO_BASE_URL}/m/{map_id}',
                'Origin': self.CALTOPO_BASE_URL
            }

            if csrf_token:
                headers['X-CSRFToken'] = csrf_token
                headers['X-XSRF-TOKEN'] = csrf_token

            # IMPORTANT: CalTopo expects form-urlencoded data, NOT raw JSON!
            # The JSON must be sent as a form parameter named 'json'
            form_data = {
                'json': json.dumps(marker_payload)
            }

            response = self.session.post(
                url,
                data=form_data,  # Use 'data' for form encoding, not 'json'
                headers=headers,
                timeout=10
            )

            return response.status_code in [200, 201]
        except Exception:
            return False

    def upload_photo_waypoint(self, map_id, photo_data, team_id, marker_id):
        """
        Upload a photo waypoint to a CalTopo map.

        NOTE: This method is deprecated and not currently used.
        Photo uploads should be done via JavaScript in the authenticated browser session,
        similar to marker uploads. This method remains for reference but the requests-based
        approach doesn't work reliably due to session/authentication issues.

        Args:
            map_id (str): CalTopo map ID
            photo_data (dict): Photo data with 'lat', 'lon', 'title', 'image_path'
            team_id (str): Team ID for service account permissions
            marker_id (str): Marker ID to attach the photo to

        Returns:
            bool: Always returns False as this method is deprecated
        """
        return False
