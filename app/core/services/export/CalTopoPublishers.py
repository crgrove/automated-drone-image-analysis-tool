"""
CalTopoPublishers - Uniform write interface over the two CalTopo auth modes.

Both the Team API (service-account credentials, HMAC-signed) and the browser
session (cookies harvested from the embedded login) create the same objects on
the same endpoints; only the transport and authentication differ. Wrapping each
in a publisher lets one export worker drive either, instead of maintaining two
copies of the marker/polygon/photo loop.
"""


class CalTopoApiPublisher:
    """Publishes to CalTopo through the Team API using service credentials."""

    def __init__(self, api_service, map_id, team_id, credential_id, credential_secret):
        """
        Initialize the API publisher.

        Args:
            api_service: CalTopoAPIService instance.
            map_id (str): Target map ID.
            team_id (str): Team ID.
            credential_id (str): Credential ID.
            credential_secret (str): Credential Secret.
        """
        self.api_service = api_service
        self.map_id = map_id
        self.team_id = team_id
        self.credential_id = credential_id
        self.credential_secret = credential_secret

    def add_marker(self, marker):
        """Create a marker.

        Args:
            marker (dict): Marker data.

        Returns:
            tuple: (success: bool, marker_id: str or None)
        """
        return self.api_service.add_marker_via_api(
            self.map_id, self.team_id, self.credential_id, self.credential_secret, marker
        )

    def add_polygon(self, polygon):
        """Create a polygon.

        Args:
            polygon (dict): Polygon data.

        Returns:
            tuple: (success: bool, shape_id: str or None)
        """
        return self.api_service.add_polygon_via_api(
            self.map_id, self.team_id, self.credential_id, self.credential_secret, polygon
        )

    def upload_photo(self, marker, marker_id, photo_path=None, title=None):
        """Attach a photo to a marker.

        Args:
            marker (dict): Marker data; 'image_path' is the fallback photo.
            marker_id (str): Marker the photo belongs to.
            photo_path (str, optional): Specific photo file to upload; falls back
                to the marker's 'image_path' when omitted.
            title (str, optional): Title for this photo; falls back to the
                marker title.

        Returns:
            tuple: (success: bool, media_object_id: str or None)
        """
        return self.api_service.upload_photo_via_api(
            self.map_id, self.team_id, self.credential_id, self.credential_secret,
            photo_path or marker['image_path'], marker['lat'], marker['lon'],
            title=title or marker.get('title'),
            description=marker.get('description', ''),
            marker_id=marker_id
        )


class CalTopoBrowserPublisher:
    """Publishes to CalTopo using the session captured from the embedded browser."""

    def __init__(self, caltopo_service, map_id):
        """
        Initialize the browser publisher.

        Args:
            caltopo_service: CalTopoService holding the authenticated session.
            map_id (str): Target map ID.
        """
        self.caltopo_service = caltopo_service
        self.map_id = map_id

    def add_marker(self, marker):
        """Create a marker.

        Args:
            marker (dict): Marker data.

        Returns:
            tuple: (success: bool, marker_id: str or None)
        """
        return self.caltopo_service.add_marker_to_map(self.map_id, marker)

    def add_polygon(self, polygon):
        """Create a polygon.

        Args:
            polygon (dict): Polygon data.

        Returns:
            tuple: (success: bool, shape_id: str or None)
        """
        return self.caltopo_service.add_shape_to_map(self.map_id, polygon)

    def upload_photo(self, marker, marker_id, photo_path=None, title=None):
        """Attach a photo to a marker.

        Args:
            marker (dict): Marker data; 'image_path' is the fallback photo.
            marker_id (str): Marker the photo belongs to.
            photo_path (str, optional): Specific photo file to upload; falls back
                to the marker's 'image_path' when omitted.
            title (str, optional): Title for this photo; falls back to the
                marker title.

        Returns:
            tuple: (success: bool, media_object_id: str or None)
        """
        return self.caltopo_service.upload_photo_for_marker(
            self.map_id, marker_id, photo_path or marker['image_path'],
            marker['lat'], marker['lon'],
            title=title or marker.get('title'),
            description=marker.get('description', '')
        )
