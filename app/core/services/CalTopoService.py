"""
CalTopoService - Handles CalTopo authentication and API interactions.

This service manages session authentication, map retrieval, and marker/waypoint
creation on CalTopo maps.
"""

import json
import requests
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
        """Initialize the CalTopo service."""
        self.session = requests.Session()
        self.settings = QSettings("ADIAT", "CalTopo")
        self._load_session()

    def _load_session(self):
        """Load saved session cookies from settings."""
        cookies_json = self.settings.value("session_cookies", "")
        if cookies_json:
            try:
                cookies = json.loads(cookies_json)
                for cookie in cookies:
                    self.session.cookies.set(**cookie)
            except json.JSONDecodeError:
                pass

    def save_session(self, cookies_dict):
        """Save session cookies to settings.

        Args:
            cookies_dict: Dictionary of cookies from the web view
        """
        # Convert cookies to serializable format
        cookies_list = []
        for name, value in cookies_dict.items():
            cookies_list.append({
                'name': name,
                'value': value,
                'domain': '.caltopo.com'
            })

        print(f"DEBUG CalTopo: Saving {len(cookies_list)} cookies")
        self.settings.setValue("session_cookies", json.dumps(cookies_list))
        self._load_session()
        print(f"DEBUG CalTopo: Session cookies loaded. Current cookies: {list(self.session.cookies.keys())}")

    def clear_session(self):
        """Clear stored session data."""
        self.settings.remove("session_cookies")
        self.session.cookies.clear()

    def is_authenticated(self):
        """Check if user has valid session.

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
        """Retrieve list of user's CalTopo maps.

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
        except Exception as e:
            print(f"Error fetching maps: {e}")
            return []

    def _get_csrf_token(self, map_id):
        """Try to get CSRF token from CalTopo map page.

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
                print(f"DEBUG CalTopo: Found CSRF token: {csrf_token[:20]}...")
                return csrf_token

            # Try to parse from page content
            import re
            csrf_match = re.search(r'csrf[_-]?token["\']?\s*[:=]\s*["\']([^"\']+)', response.text, re.IGNORECASE)
            if csrf_match:
                token = csrf_match.group(1)
                print(f"DEBUG CalTopo: Extracted CSRF token from page: {token[:20]}...")
                return token

            print("DEBUG CalTopo: No CSRF token found")
            return None
        except Exception as e:
            print(f"DEBUG CalTopo: Error getting CSRF token: {e}")
            return None

    def add_marker_to_map(self, map_id, marker_data):
        """Add a marker/waypoint to a CalTopo map.

        Args:
            map_id (str): CalTopo map ID
            marker_data (dict): Marker data with 'lat', 'lon', 'title', 'description'

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # CalTopo marker format (GeoJSON Feature)
            # Based on actual network traffic capture from CalTopo web interface
            marker_payload = {
                'type': 'Feature',
                'class': None,  # Required by CalTopo
                'geometry': {
                    'type': 'Point',
                    'coordinates': [marker_data['lon'], marker_data['lat']]
                },
                'properties': {
                    'title': marker_data.get('title', ''),
                    'description': marker_data.get('description', ''),
                    'marker-size': '1',
                    'marker-symbol': 'a:4',  # CalTopo's default marker symbol
                    'marker-color': 'FF0000',
                    'marker-rotation': 0
                }
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

            print(f"DEBUG CalTopo: Posting marker to {url}")
            print(f"DEBUG CalTopo: Payload: {marker_payload}")
            print(f"DEBUG CalTopo: Form data: {form_data}")
            print(f"DEBUG CalTopo: Cookies: {list(self.session.cookies.keys())}")
            print(f"DEBUG CalTopo: Headers: {headers}")

            response = self.session.post(
                url,
                data=form_data,  # Use 'data' for form encoding, not 'json'
                headers=headers,
                timeout=10
            )

            print(f"DEBUG CalTopo: Response status: {response.status_code}")
            print(f"DEBUG CalTopo: Response headers: {dict(response.headers)}")
            print(f"DEBUG CalTopo: Response text: {response.text[:500] if response.text else '(empty)'}")

            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error adding marker: {e}")
            import traceback
            traceback.print_exc()
            return False

    def add_markers_batch(self, map_id, markers):
        """Add multiple markers to a CalTopo map.

        Args:
            map_id (str): CalTopo map ID
            markers (list): List of marker data dictionaries

        Returns:
            tuple: (success_count, total_count)
        """
        success_count = 0
        total_count = len(markers)

        for marker in markers:
            if self.add_marker_to_map(map_id, marker):
                success_count += 1

        return success_count, total_count

    def upload_photo_waypoint(self, map_id, photo_data):
        """Upload a photo waypoint to a CalTopo map.

        Args:
            map_id (str): CalTopo map ID
            photo_data (dict): Photo data with 'lat', 'lon', 'title', 'image_path'

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # First create the marker
            marker_payload = {
                'type': 'Marker',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [photo_data['lon'], photo_data['lat']]
                },
                'properties': {
                    'title': photo_data.get('title', ''),
                    'description': photo_data.get('description', ''),
                    'class': 'Marker'
                }
            }

            # TODO: Implement photo upload once CalTopo photo API is confirmed
            # This may require multipart form data with image file

            response = self.session.post(
                f"{self.CALTOPO_API_BASE}/map/{map_id}/Marker",
                json=marker_payload,
                timeout=10
            )

            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error uploading photo waypoint: {e}")
            return False
