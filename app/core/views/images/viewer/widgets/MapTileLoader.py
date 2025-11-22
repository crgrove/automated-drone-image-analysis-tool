"""
MapTileLoader - Downloads and caches OpenStreetMap tiles for map background.

This module handles fetching map tiles from OpenStreetMap and caching them locally.
"""

import os
import math
import hashlib
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QThread, QUrl, QTimer
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtGui import QPixmap, QImage, QColor
import tempfile


class MapTileLoader(QObject):
    """
    Loads map tiles from OpenStreetMap for background display.

    Handles tile downloading, caching, and coordinate conversions.
    """

    # Signal emitted when a tile is loaded
    tile_loaded = Signal(int, int, int, QPixmap)  # x, y, zoom, pixmap

    # Signal emitted when there's an error loading tiles
    tile_error = Signal(str)  # error message

    def __init__(self, offline_only=False):
        """Initialize the tile loader."""
        super().__init__()
        self.offline_only = offline_only

        # Tile cache directory
        self.cache_dir = Path(tempfile.gettempdir()) / "adiat_map_cache"
        self.cache_dir.mkdir(exist_ok=True)

        # Network manager for downloading tiles
        self.network_manager = QNetworkAccessManager()

        # Tile size (OpenStreetMap uses 256x256)
        self.tile_size = 256

        # Current downloads
        self.active_downloads = {}

        # Tile source type ('map' or 'satellite')
        self.tile_source = 'map'

        # Error tracking
        self.error_count = 0
        self.max_errors_before_notify = 3
        self.last_error_message = None
        self.error_reset_timer = QTimer()
        self.error_reset_timer.setSingleShot(True)
        self.error_reset_timer.timeout.connect(self.reset_error_count)

    def lat_lon_to_tile(self, lat, lon, zoom):
        """
        Convert latitude/longitude to tile coordinates.

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees
            zoom: Zoom level (0-19)

        Returns:
            tuple: (x_tile, y_tile) coordinates
        """
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        x_tile = int((lon + 180.0) / 360.0 * n)
        y_tile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return x_tile, y_tile

    def tile_to_lat_lon(self, x_tile, y_tile, zoom):
        """
        Convert tile coordinates to latitude/longitude (northwest corner).

        Args:
            x_tile: X tile coordinate
            y_tile: Y tile coordinate
            zoom: Zoom level

        Returns:
            tuple: (lat, lon) in degrees
        """
        n = 2.0 ** zoom
        lon = x_tile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y_tile / n)))
        lat = math.degrees(lat_rad)
        return lat, lon

    def get_tile_bounds(self, x_tile, y_tile, zoom):
        """
        Get the geographic bounds of a tile.

        Args:
            x_tile: X tile coordinate
            y_tile: Y tile coordinate
            zoom: Zoom level

        Returns:
            tuple: (north, south, east, west) bounds in degrees
        """
        north_west = self.tile_to_lat_lon(x_tile, y_tile, zoom)
        south_east = self.tile_to_lat_lon(x_tile + 1, y_tile + 1, zoom)
        return north_west[0], south_east[0], south_east[1], north_west[1]

    def set_tile_source(self, source):
        """
        Set the tile source type.

        Args:
            source: 'map' or 'satellite'
        """
        self.tile_source = source

    def set_offline_only(self, offline_only: bool):
        """Enable/disable offline-only mode (no new tile downloads)."""
        self.offline_only = bool(offline_only)

    def load_tile(self, x_tile, y_tile, zoom):
        """
        Load a map tile (from cache or download).

        Args:
            x_tile: X tile coordinate
            y_tile: Y tile coordinate
            zoom: Zoom level
        """
        # Check cache first (include source type in cache filename)
        cache_path = self.cache_dir / f"{self.tile_source}_{zoom}_{x_tile}_{y_tile}.png"

        if cache_path.exists():
            # Load from cache
            pixmap = QPixmap(str(cache_path))
            if not pixmap.isNull():
                self.tile_loaded.emit(x_tile, y_tile, zoom, pixmap)
                return
        # If offline, don't attempt network and show placeholder/error
        if self.offline_only:
            self.tile_error.emit("Offline mode: map tiles unavailable")
            pixmap = QPixmap(self.tile_size, self.tile_size)
            pixmap.fill(QColor(200, 200, 200))
            self.tile_loaded.emit(x_tile, y_tile, zoom, pixmap)
            return

        # Download tile when online
        self.download_tile(x_tile, y_tile, zoom)

    def download_tile(self, x_tile, y_tile, zoom):
        """
        Download a tile from the tile server.

        Args:
            x_tile: X tile coordinate
            y_tile: Y tile coordinate
            zoom: Zoom level
        """
        # Select tile server based on source type
        if self.tile_source == 'satellite':
            # Use ESRI World Imagery tiles
            url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{y_tile}/{x_tile}"
        else:
            # Use OpenStreetMap tiles
            url = f"https://tile.openstreetmap.org/{zoom}/{x_tile}/{y_tile}.png"

        # Check if already downloading
        key = (x_tile, y_tile, zoom, self.tile_source)
        if key in self.active_downloads:
            return

        # Create network request
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader(b"User-Agent", b"ADIAT/1.0")

        # Start download
        reply = self.network_manager.get(request)
        self.active_downloads[key] = reply

        # Connect signals
        reply.finished.connect(lambda: self.on_tile_downloaded(reply, x_tile, y_tile, zoom))

    def on_tile_downloaded(self, reply, x_tile, y_tile, zoom):
        """
        Handle downloaded tile data.

        Args:
            reply: Network reply object
            x_tile: X tile coordinate
            y_tile: Y tile coordinate
            zoom: Zoom level
        """
        key = (x_tile, y_tile, zoom, self.tile_source)
        if key in self.active_downloads:
            del self.active_downloads[key]

        if reply.error() == QNetworkReply.NetworkError.NoError:
            # Get data
            data = reply.readAll()

            # Save to cache (include source type in filename)
            cache_path = self.cache_dir / f"{self.tile_source}_{zoom}_{x_tile}_{y_tile}.png"
            with open(cache_path, 'wb') as f:
                f.write(data.data())

            # Create pixmap
            pixmap = QPixmap()
            pixmap.loadFromData(data)

            if not pixmap.isNull():
                self.tile_loaded.emit(x_tile, y_tile, zoom, pixmap)
        else:
            # Handle error
            error_code = reply.error()
            error_string = reply.errorString()
            http_status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)

            # Check if we have a cached version from a previous session
            cache_path = self.cache_dir / f"{self.tile_source}_{zoom}_{x_tile}_{y_tile}.png"
            if cache_path.exists():
                pixmap = QPixmap(str(cache_path))
                if not pixmap.isNull():
                    self.tile_loaded.emit(x_tile, y_tile, zoom, pixmap)
                    # Don't count as error if we have cache
                    return

            # Track errors and notify user if necessary
            self._handle_tile_error(error_code, error_string, http_status)

            # Only show gray tile if no cache exists
            pixmap = QPixmap(self.tile_size, self.tile_size)
            pixmap.fill(QColor(200, 200, 200))
            self.tile_loaded.emit(x_tile, y_tile, zoom, pixmap)

        reply.deleteLater()

    def calculate_zoom_for_bounds(self, min_lat, max_lat, min_lon, max_lon, map_width, map_height):
        """
        Calculate appropriate zoom level for given bounds.

        Args:
            min_lat, max_lat, min_lon, max_lon: Geographic bounds
            map_width, map_height: Map display size in pixels

        Returns:
            int: Appropriate zoom level
        """
        # Calculate zoom to fit bounds
        lat_diff = max_lat - min_lat
        lon_diff = max_lon - min_lon

        # Prevent division by zero
        if lat_diff == 0:
            lat_diff = 0.001
        if lon_diff == 0:
            lon_diff = 0.001

        # Calculate zoom for width and height
        zoom_x = math.log2(360 / lon_diff * map_width / self.tile_size)
        zoom_y = math.log2(180 / lat_diff * map_height / self.tile_size)

        # Use minimum zoom to ensure all points fit
        zoom = min(zoom_x, zoom_y)

        # Clamp to valid range (0-19) and leave some margin
        return max(1, min(18, int(zoom) - 1))

    def _handle_tile_error(self, error_code, error_string, http_status):
        """
        Handle tile download errors and notify user if necessary.

        Args:
            error_code: QNetworkReply error code
            error_string: Error description string
            http_status: HTTP status code if available
        """
        self.error_count += 1

        # Reset error count after 30 seconds of no errors
        self.error_reset_timer.stop()
        self.error_reset_timer.start(30000)

        # Determine error message based on status
        if http_status == 429:
            # Too Many Requests - rate limiting
            error_msg = "Map tile service rate limit exceeded. Please wait a moment before zooming/panning."
        elif http_status == 403:
            # Forbidden - possible usage policy violation
            error_msg = "Map tile access denied. This may be due to excessive usage or policy restrictions."
        elif http_status == 503:
            # Service Unavailable
            error_msg = "Map tile service is temporarily unavailable. Using cached tiles where available."
        elif error_code == QNetworkReply.NetworkError.HostNotFoundError:
            error_msg = "Cannot connect to map tile server. Please check your internet connection."
        elif error_code == QNetworkReply.NetworkError.TimeoutError:
            error_msg = "Map tile request timed out. The server may be slow or your connection may be unstable."
        elif error_code == QNetworkReply.NetworkError.ConnectionRefusedError:
            error_msg = "Connection to map tile server was refused."
        else:
            # Generic error
            error_msg = "Failed to load some map tiles. Using cached tiles where available."

        # Only emit error signal if we've hit the threshold and it's a different message
        if self.error_count >= self.max_errors_before_notify:
            if error_msg != self.last_error_message:
                self.last_error_message = error_msg
                self.tile_error.emit(error_msg)
                # Reset count after notifying to avoid spam
                self.error_count = 0

    def reset_error_count(self):
        """Reset the error count after a period of successful operations."""
        self.error_count = 0
        self.last_error_message = None
