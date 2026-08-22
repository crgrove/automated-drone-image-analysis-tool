"""
CalTopoAPIService - Handles CalTopo Team API interactions.

This service manages API-based authentication and operations using
service account credentials (Team ID, Credential ID, Credential Secret).
"""

import json
import base64
import binascii
import hmac
import time
import uuid
import os
import requests
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode

from core.services.LoggerService import LoggerService
from core.services.export.PhotoPayload import encode_photo

# CalTopo hands out the credential secret as base64. Some consoles/clients hand
# it back in the URL-safe alphabet, so accept that too rather than failing on a
# secret that is genuinely correct.
_URLSAFE_TO_STANDARD = str.maketrans("-_", "+/")


def decode_credential_secret(credential_secret: str) -> bytes:
    """Decode a CalTopo credential secret into the raw HMAC key bytes.

    Accepts the standard and URL-safe base64 alphabets, and restores padding
    that was dropped when the value was copied. Decoding is strict about the
    alphabet on purpose: ``base64.b64decode`` silently *discards* characters
    outside the alphabet, which turns a wrong-field paste into a plausible but
    useless key instead of a clear error.

    Args:
        credential_secret (str): Secret exactly as issued by CalTopo.

    Returns:
        bytes: The decoded HMAC key.

    Raises:
        ValueError: If the value cannot be a CalTopo credential secret. The
            message is written for the user, not the developer, because it is
            surfaced in the credential dialog.
    """
    if not credential_secret or not credential_secret.strip():
        raise ValueError("The CalTopo credential secret is empty.")

    text = credential_secret.strip()
    padded = text + "=" * (-len(text) % 4)

    for candidate in (padded, padded.translate(_URLSAFE_TO_STANDARD)):
        try:
            return base64.b64decode(candidate, validate=True)
        except (binascii.Error, ValueError):
            continue

    raise ValueError(
        f"The CalTopo credential secret is not valid base64 ({len(text)} characters). "
        "Copy the Credential Secret exactly as shown on the CalTopo Team Admin "
        "page under Service Accounts - it is a long base64 string, not the "
        "Credential ID or the Team ID."
    )


class CalTopoAPIService:
    """
    Service for interacting with CalTopo Team API.

    Handles signed requests, account data retrieval, and map object creation
    using service account credentials.
    """

    CALTOPO_BASE_URL = "https://caltopo.com"
    DEFAULT_TIMEOUT_MS = 2 * 60 * 1000  # 2 minutes

    def __init__(self, logger=None):
        """
        Initialize the CalTopo API service.

        Sets up the service for making authenticated API requests to CalTopo.

        Args:
            logger: Optional LoggerService instance. Failures are logged rather
                than swallowed so "check the console for details" is truthful.
        """
        self.logger = logger or LoggerService()

    def _sign_request(self, method: str, url: str, expires: int, payload_string: str, credential_secret: str) -> str:
        """Generate an HMAC signature for API request authentication.

        Args:
            method (str): HTTP method (e.g., "GET", "POST")
            url (str): API endpoint URL
            expires (int): Expiration time in milliseconds
            payload_string (str): JSON payload as a string
            credential_secret (str): Credential Secret (base64-encoded)

        Returns:
            str: Base64-encoded signature

        Raises:
            ValueError: If credential_secret is not decodable base64.
        """
        message = f"{method} {url}\n{expires}\n{payload_string}"
        secret = decode_credential_secret(credential_secret)
        signature = hmac.new(secret, message.encode(), "sha256").digest()
        return base64.b64encode(signature).decode()

    def _api_request(self, method: str, endpoint: str, credential_id: str, credential_secret: str,
                     payload: Optional[Dict] = None, timeout: int = 30) -> Tuple[bool, Optional[Dict]]:
        """Make an authenticated API request to CalTopo Team API.

        Args:
            method (str): HTTP method (e.g., "GET", "POST", "DELETE")
            endpoint (str): API endpoint (e.g., "/api/v1/acct/{team_id}/CollaborativeMap/{map_id}")
            credential_id (str): Credential ID
            credential_secret (str): Credential Secret (base64-encoded)
            payload (dict, optional): Request payload
            timeout (int): Request timeout in seconds

        Returns:
            tuple: (success: bool, result: dict or None)
        """
        try:
            payload_string = json.dumps(payload) if payload else ""
            expires = int(time.time() * 1000) + self.DEFAULT_TIMEOUT_MS
            try:
                signature = self._sign_request(method, endpoint, expires, payload_string, credential_secret)
            except ValueError as e:
                # An undecodable secret fails here instantly, with no network
                # call at all. Say so, or the caller reports a "connection"
                # failure that never involved a connection.
                self.logger.error(f"CalTopo API {method} {endpoint} not sent - {e}")
                return False, None

            parameters = {
                "id": credential_id,
                "expires": expires,
                "signature": signature,
            }

            # For POST requests with payload, include json in parameters and use empty query string
            if method.upper() == "POST" and payload is not None:
                parameters["json"] = payload_string
                query_string = ""
            else:
                query_string = f"?{urlencode(parameters)}"

            url = f"{self.CALTOPO_BASE_URL}{endpoint}{query_string}"

            if method.upper() == "POST":
                # POST requests: body contains form-encoded parameters (including json)
                body = (
                    urlencode(parameters).encode()
                    if payload is not None
                    else None
                )
                headers = {}
                if body is not None:
                    headers["Content-Type"] = "application/x-www-form-urlencoded"
                    headers["Content-Length"] = str(len(body))
                response = requests.post(url, data=body, headers=headers, timeout=timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, timeout=timeout)
            else:  # GET
                response = requests.get(url, timeout=timeout)

            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    return True, data.get("result")
                except json.JSONDecodeError:
                    return True, None
            else:
                self.logger.error(
                    f"CalTopo API {method} {endpoint} failed: HTTP {response.status_code} "
                    f"- {self._response_snippet(response)}"
                )
                return False, None

        except requests.RequestException as e:
            self.logger.error(f"CalTopo API {method} {endpoint} failed: {type(e).__name__}: {e}")
            return False, None
        except Exception as e:
            self.logger.error(f"CalTopo API {method} {endpoint} failed: {type(e).__name__}: {e}")
            return False, None

    @staticmethod
    def _response_snippet(response, limit: int = 500) -> str:
        """Return a short, safe excerpt of a response body for logging.

        The request URL is deliberately never logged: it carries the credential
        id and signature as query parameters.

        Args:
            response: The requests Response object.
            limit (int): Maximum number of characters to include.

        Returns:
            str: Body excerpt, or a placeholder when the body is unreadable.
        """
        try:
            body = str(response.text or "").strip()
        except Exception:
            return "<response body unavailable>"
        if not body:
            return "<empty response body>"
        return body[:limit] + ("..." if len(body) > limit else "")

    def get_account_data(self, team_id: str, credential_id: str, credential_secret: str,
                         timestamp: int = 0) -> Tuple[bool, Optional[Dict]]:
        """Get account data from CalTopo API.

        Args:
            team_id (str): Team ID
            credential_id (str): Credential ID
            credential_secret (str): Credential Secret (base64-encoded)
            timestamp (int): Unix timestamp in milliseconds (0 for all data)

        Returns:
            tuple: (success: bool, account_data: dict or None)
        """
        endpoint = f"/api/v1/acct/{team_id}/since/{timestamp}"
        success, result = self._api_request("GET", endpoint, credential_id, credential_secret)
        if success and result:
            if not isinstance(result, dict):
                self.logger.error(
                    f"CalTopo API returned an unexpected account payload of type "
                    f"{type(result).__name__} for team {team_id}; expected an object."
                )
                return False, None
            result['team_id'] = team_id  # Store team_id for later use
        return success, result

    def add_marker_via_api(self, map_id: str, team_id: str, credential_id: str, credential_secret: str,
                           marker_data: Dict) -> Tuple[bool, Optional[str]]:
        """Add a marker to a map using the API.

        Args:
            map_id (str): Map ID
            team_id (str): Team ID
            credential_id (str): Credential ID
            credential_secret (str): Credential Secret (base64-encoded)
            marker_data (dict): Marker data with 'lat', 'lon', 'title', 'description', etc.

        Returns:
            tuple: (success: bool, marker_id: str or None)
        """
        # Determine marker color
        marker_color = marker_data.get('marker_color')
        if not marker_color and marker_data.get('rgb'):
            try:
                r, g, b = marker_data['rgb']
                marker_color = f"{r:02X}{g:02X}{b:02X}"
            except Exception:
                marker_color = "FF0000"
        if not marker_color:
            marker_color = "FF0000"

        marker_payload = {
            "type": "Feature",
            "id": None,
            "geometry": {
                "type": "Point",
                "coordinates": [marker_data["lon"], marker_data["lat"]],
            },
            "properties": {
                "title": marker_data.get("title", ""),
                "description": marker_data.get("description", ""),
                "folderId": None,
                "marker-size": str(marker_data.get("marker_size", "1")),
                "marker-symbol": marker_data.get("marker_symbol", "a:4"),
                "marker-color": marker_color,
                "marker-rotation": marker_data.get("marker_rotation", 0),
            },
        }

        endpoint = f"/api/v1/map/{map_id}/Marker"
        success, result = self._api_request("POST", endpoint, credential_id, credential_secret, marker_payload)

        if success and result and result.get("id"):
            return True, result["id"]
        return False, None

    def add_polygon_via_api(self, map_id: str, team_id: str, credential_id: str, credential_secret: str,
                            polygon_data: Dict) -> Tuple[bool, Optional[str]]:
        """Add a polygon to a map using the API.

        Args:
            map_id (str): Map ID
            team_id (str): Team ID
            credential_id (str): Credential ID
            credential_secret (str): Credential Secret (base64-encoded)
            polygon_data (dict): Polygon data with 'coordinates', 'title', 'description'

        Returns:
            tuple: (success: bool, polygon_id: str or None)
        """
        coords = polygon_data.get('coordinates', [])
        if not coords:
            return False, None

        # Ensure polygon is closed
        if coords[0] != coords[-1]:
            coords.append(coords[0])

        # Convert to GeoJSON format: (lon, lat) arrays
        geojson_coords = [[lon, lat] for lat, lon in coords]

        shape_payload = {
            "properties": {
                "title": polygon_data.get("title", ""),
                "description": polygon_data.get("description", ""),
                "folderId": None,
                "stroke-width": 2,
                "stroke-opacity": 1,
                "stroke": "#FF0000",
                "fill-opacity": 0.1,
                "fill": "#FF0000"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [geojson_coords]  # GeoJSON Polygon requires array of rings
            }
        }

        endpoint = f"/api/v1/map/{map_id}/Shape"
        success, result = self._api_request("POST", endpoint, credential_id, credential_secret, shape_payload)

        if success and result and result.get("id"):
            return True, result["id"]
        return False, None

    def upload_photo_via_api(self, map_id: str, team_id: str, credential_id: str, credential_secret: str,
                             photo_path: str, lat: float, lon: float, title: str = None,
                             description: str = "", marker_id: str = None) -> Tuple[bool, Optional[str]]:
        """Upload a photo to a map using the API.

        Args:
            map_id (str): Map ID
            team_id (str): Team ID
            credential_id (str): Credential ID
            credential_secret (str): Credential Secret (base64-encoded)
            photo_path (str): Path to photo file
            lat (float): Latitude
            lon (float): Longitude
            title (str, optional): Photo title
            description (str): Photo description
            marker_id (str, optional): Marker ID to attach photo to

        Returns:
            tuple: (success: bool, media_object_id: str or None)
        """
        try:
            # Read and encode image, capping camera-sized originals (see
            # PhotoPayload: base64 plus form-encoding inflates a file by ~43%).
            base64_data, filename = encode_photo(photo_path, logger=self.logger)

            # Generate media ID
            media_id = str(uuid.uuid4())

            # Step 1: Create media metadata
            media_metadata_payload = {
                "properties": {
                    "creator": team_id,
                    "filename": filename
                }
            }
            endpoint = f"/api/v1/media/{media_id}"
            success, _ = self._api_request("POST", endpoint, credential_id, credential_secret, media_metadata_payload)
            if not success:
                return False, None

            # Step 2: Upload media data
            media_data_payload = {"data": base64_data}
            endpoint = f"/api/v1/media/{media_id}/data"
            success, _ = self._api_request("POST", endpoint, credential_id, credential_secret, media_data_payload)
            if not success:
                return False, None

            # Step 3: Attach media to map
            media_object_payload = {
                "type": "Feature",
                "id": None,
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "parentId": f"Marker:{marker_id}" if marker_id else "",
                    "backendMediaId": media_id,
                    "title": title or filename,
                    "heading": None,
                    "description": description,
                    "marker-symbol": "aperture",
                    "marker-color": "#FFFFFF",
                    "marker-size": 1,
                }
            }
            endpoint = f"/api/v1/map/{map_id}/MapMediaObject"
            success, result = self._api_request("POST", endpoint, credential_id, credential_secret, media_object_payload)

            if success and result and result.get("id"):
                return True, result["id"]
            return False, None

        except Exception as e:
            self.logger.error(f"CalTopo photo upload failed for {photo_path}: {type(e).__name__}: {e}")
            return False, None
