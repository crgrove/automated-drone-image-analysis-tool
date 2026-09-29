"""
MapTileLoader - Downloads and caches XYZ map tiles for the map background.

Serves the base layers (street map, satellite, topo) and the transparent
overlay layers (roads, USFS MVUM, hiking trails) from one registry. Each
loader instance carries ONE source; the map view runs a loader per enabled
layer. Tiles are cached on disk keyed by source name, so cached layers keep
working in Offline Only mode.
"""

import os
import math
import hashlib
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QThread, QUrl, QTimer, Qt
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtGui import QPixmap, QImage, QColor, qGray
import tempfile

# Web Mercator (EPSG:3857) half-world extent in metres, for ArcGIS export
# endpoints that render a bbox instead of serving a tile pyramid.
WEB_MERCATOR_HALF_WORLD_M = 20037508.342789244

# Base (opaque) tile sources. 'url' is an XYZ template. Curated and
# hardcoded on purpose - matching the app's existing source handling.
BASE_SOURCES = {
    'map': {
        'url': "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        'max_zoom': 19,
    },
    'satellite': {
        'url': ("https://server.arcgisonline.com/ArcGIS/rest/services/"
                "World_Imagery/MapServer/tile/{z}/{y}/{x}"),
        'max_zoom': 20,
    },
    'topo': {
        # OpenTopoMap: global topographic rendering of OSM + SRTM contours.
        'url': "https://tile.opentopomap.org/{z}/{x}/{y}.png",
        'max_zoom': 17,
    },
}

# Transparent overlay sources drawn above a base layer. 'export' entries are
# ArcGIS MapServer export endpoints (dynamic services with no tile pyramid);
# the loader renders each XYZ tile via its EPSG:3857 bbox.
# NOTE: the USFS trails service name is EDW_TrailNFSPublish_01
# (EDW_TrailNFS_01 no longer exists).
OVERLAY_SOURCES = {
    'roads': {
        'url': ("https://server.arcgisonline.com/ArcGIS/rest/services/"
                "Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}"),
        'max_zoom': 19,
    },
    'mvum': {
        'export': ("https://apps.fs.usda.gov/arcx/rest/services/"
                   "EDW/EDW_MVUM_01/MapServer/export"),
        'max_zoom': 22,
    },
    'trails': {
        'url': "https://tile.waymarkedtrails.org/hiking/{z}/{x}/{y}.png",
        'max_zoom': 18,
    },
    'usfs_trails': {
        'export': ("https://apps.fs.usda.gov/arcx/rest/services/"
                   "EDW/EDW_TrailNFSPublish_01/MapServer/export"),
        'max_zoom': 22,
    },
}


class MapTileLoader(QObject):
    """
    Loads map tiles from OpenStreetMap for background display.

    Handles tile downloading, caching, and coordinate conversions.
    """

    # Signal emitted when a tile is loaded
    tile_loaded = Signal(int, int, int, QPixmap)  # x, y, zoom, pixmap
    # An overlay tile that is transparent because the FETCH failed (offline or
    # network error), not because the layer is legitimately empty there. Kept
    # distinct from tile_loaded so consumers never cache a failure as imagery
    # and can retry once conditions change.
    tile_placeholder = Signal(int, int, int, QPixmap)  # x, y, zoom, pixmap

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

        # Per-source maximum tile zoom (matches AlignImageView): Esri World
        # Imagery serves z20 (~0.15 m/px) across most SAR terrain, OSM tops
        # out at z19. Above the source's limit the view keeps scaling but
        # tiles stop sharpening.
        self.MAX_ZOOM_SATELLITE = 20
        self.MAX_ZOOM_MAP = 19

        # Ancestor fallback: when a tile is missing (404 / network error) or
        # is a "no imagery at this zoom" placeholder, serve an upscaled crop
        # of the nearest usable ancestor tile instead, so zooming past the
        # source's real coverage keeps showing the last good imagery rather
        # than a wall of gray/placeholder tiles. This is how far up the
        # pyramid we will climb (5 levels = a 32x upscale at worst).
        self.MAX_FALLBACK_LEVELS = 5
        # Placeholder detection: fraction of sampled pixels that must share
        # one luminance bucket for a tile to count as a "no imagery"
        # placeholder. Genuinely uniform imagery (open water) can trip this
        # too, but its ancestor crop shows the same pixels, so a false
        # positive is visually harmless.
        self.PLACEHOLDER_UNIFORM_FRACTION = 0.90

        # Pending fallback resolutions: (x, y, zoom, source) of an ancestor
        # download -> list of (x, y, zoom) descendant tiles waiting on it.
        self.fallback_waiters = {}
        # Ancestor downloads that errored this session; the fallback walk
        # climbs past them instead of re-requesting a dead tile forever.
        # Cleared with the error counter so a recovered network gets retried.
        self._fallback_failed = set()

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
            zoom: Zoom level (0 to the source's max, see max_zoom())

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
            source: A key of BASE_SOURCES or OVERLAY_SOURCES
                ('map', 'satellite', 'topo', 'roads', 'mvum', 'trails', ...).
        """
        self.tile_source = source

    @staticmethod
    def is_overlay(source):
        """True for transparent overlay sources (roads/MVUM/trails).

        Overlays skip the placeholder heuristic and the ancestor fallback: a
        fully transparent tile is a legitimate answer ("no trail here"), not
        missing imagery, and failures must yield transparency rather than a
        gray square that would blot out the base map.
        """
        return source in OVERLAY_SOURCES

    def _source_spec(self):
        """Registry entry for the current source (defaults to the street map)."""
        return (BASE_SOURCES.get(self.tile_source)
                or OVERLAY_SOURCES.get(self.tile_source)
                or BASE_SOURCES['map'])

    def tile_bounds_3857(self, x_tile, y_tile, zoom):
        """EPSG:3857 bounds of an XYZ tile, for ArcGIS export requests.

        Returns:
            tuple: (min_x, min_y, max_x, max_y) in metres.
        """
        n = 2.0 ** zoom
        size = 2.0 * WEB_MERCATOR_HALF_WORLD_M / n
        min_x = -WEB_MERCATOR_HALF_WORLD_M + x_tile * size
        max_y = WEB_MERCATOR_HALF_WORLD_M - y_tile * size
        return (min_x, max_y - size, min_x + size, max_y)

    def tile_url(self, x_tile, y_tile, zoom):
        """Server URL for one XYZ tile of the current source."""
        spec = self._source_spec()
        if 'export' in spec:
            min_x, min_y, max_x, max_y = self.tile_bounds_3857(x_tile, y_tile, zoom)
            return (f"{spec['export']}?bbox={min_x},{min_y},{max_x},{max_y}"
                    f"&bboxSR=3857&imageSR=3857&size={self.tile_size},{self.tile_size}"
                    f"&format=png32&transparent=true&f=image")
        return spec['url'].format(z=zoom, x=x_tile, y=y_tile)

    def max_zoom(self):
        """Maximum tile zoom the current source can serve."""
        return self._source_spec().get('max_zoom', self.MAX_ZOOM_MAP)

    def _transparent_tile(self):
        """A fully transparent tile: the overlay layers' 'nothing here'."""
        pixmap = QPixmap(self.tile_size, self.tile_size)
        pixmap.fill(Qt.transparent)
        return pixmap

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
        overlay = self.is_overlay(self.tile_source)

        if cache_path.exists():
            # Load from cache
            pixmap = QPixmap(str(cache_path))
            if not pixmap.isNull():
                # A cached "no imagery at this zoom" placeholder is worth
                # less than an upscaled crop of real imagery from a lower
                # zoom - prefer the ancestor when one is usable. Overlays are
                # exempt: their tiles are legitimately near-empty.
                if (not overlay and self._looks_unavailable(pixmap)
                        and self._emit_fallback_tile(x_tile, y_tile, zoom)):
                    return
                self.tile_loaded.emit(x_tile, y_tile, zoom, pixmap)
                return
        # If offline, don't attempt network: fall back to a cached ancestor
        # crop when possible, gray placeholder otherwise. Overlays go
        # transparent instead - a gray square would blot out the base map.
        if self.offline_only:
            if overlay:
                # A failure placeholder, NOT imagery: emitted on its own
                # channel so it is never cached as a successful (empty) tile.
                self.tile_placeholder.emit(x_tile, y_tile, zoom, self._transparent_tile())
                return
            if self._emit_fallback_tile(x_tile, y_tile, zoom):
                return
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
        url = self.tile_url(x_tile, y_tile, zoom)

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

        # Capture the source the request was made FOR. The completion callback
        # must never re-read self.tile_source: switching Map -> Satellite while
        # a request is in flight would otherwise save the street-map response
        # as a satellite tile (poisoning the on-disk cache across sessions),
        # emit it into the wrong layer, and strand the original download key.
        source = self.tile_source
        reply.finished.connect(
            lambda: self.on_tile_downloaded(reply, x_tile, y_tile, zoom, source))

    def on_tile_downloaded(self, reply, x_tile, y_tile, zoom, source=None):
        """
        Handle downloaded tile data.

        Args:
            reply: Network reply object
            x_tile: X tile coordinate
            y_tile: Y tile coordinate
            zoom: Zoom level
            source: Tile source the request was made for. Everything below
                (cache filename, bookkeeping keys, overlay behavior) uses it,
                never the source selected NOW. Defaults to the current source
                for direct callers.
        """
        if source is None:
            source = self.tile_source
        # A response for a source that is no longer selected is still worth
        # caching (under ITS OWN name), but must not be displayed.
        current = (source == self.tile_source)

        key = (x_tile, y_tile, zoom, source)
        if key in self.active_downloads:
            del self.active_downloads[key]

        if reply.error() == QNetworkReply.NetworkError.NoError:
            # Get data
            data = reply.readAll()

            # Save to cache (include source type in filename)
            cache_path = self.cache_dir / f"{source}_{zoom}_{x_tile}_{y_tile}.png"
            with open(cache_path, 'wb') as f:
                f.write(data.data())

            # Create pixmap
            pixmap = QPixmap()
            pixmap.loadFromData(data)

            if current and not pixmap.isNull():
                # Some servers answer 200 with a "no imagery at this zoom"
                # placeholder image; replace it with an upscaled ancestor
                # crop when one is available (or arriving). Overlays are
                # exempt (near-empty transparent tiles are legitimate).
                if (not self.is_overlay(source)
                        and self._looks_unavailable(pixmap)
                        and self._emit_fallback_tile(x_tile, y_tile, zoom)):
                    pass
                else:
                    self.tile_loaded.emit(x_tile, y_tile, zoom, pixmap)
            # Descendant tiles may be waiting on this download to build
            # their fallback crops.
            self._serve_fallback_waiters(x_tile, y_tile, zoom, source)
        else:
            # Handle error
            error_code = reply.error()
            error_string = reply.errorString()
            http_status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)

            # Check if we have a cached version from a previous session
            cache_path = self.cache_dir / f"{source}_{zoom}_{x_tile}_{y_tile}.png"
            if cache_path.exists():
                pixmap = QPixmap(str(cache_path))
                if not pixmap.isNull():
                    if current:
                        self.tile_loaded.emit(x_tile, y_tile, zoom, pixmap)
                    self._serve_fallback_waiters(x_tile, y_tile, zoom, source)
                    # Don't count as error if we have cache
                    return

            # Remember the failure so fallback walks climb past this tile
            # instead of re-requesting it in a loop while the network is down.
            self._fallback_failed.add((x_tile, y_tile, zoom, source))

            # Track errors and notify user if necessary
            self._handle_tile_error(error_code, error_string, http_status)

            if not current:
                pass  # never surface a tile for a deselected source
            elif self.is_overlay(source):
                # A failed overlay tile goes transparent so the base map stays
                # readable - but on the placeholder channel, so the miss is
                # retryable instead of cached as a successful empty tile.
                self.tile_placeholder.emit(x_tile, y_tile, zoom, self._transparent_tile())
            elif not self._emit_fallback_tile(x_tile, y_tile, zoom):
                # Prefer an upscaled ancestor crop over a blank gray tile so
                # the user keeps context of where they are in the imagery.
                pixmap = QPixmap(self.tile_size, self.tile_size)
                pixmap.fill(QColor(200, 200, 200))
                self.tile_loaded.emit(x_tile, y_tile, zoom, pixmap)

            # Resolve any descendants waiting on this (failed) ancestor: their
            # walk will now skip it and climb further up.
            self._serve_fallback_waiters(x_tile, y_tile, zoom, source)

        reply.deleteLater()

    def _looks_unavailable(self, pixmap):
        """
        Heuristic check for a "no imagery at this zoom" placeholder tile.

        Real placeholder tiles (e.g. Esri's "Map data not yet available")
        are a near-uniform background with at most a little text, so almost
        every sampled pixel shares one luminance bucket. Sampling uses
        FastTransformation (nearest pixel, no blending) so anti-aliased text
        does not smear into the background statistics.

        Args:
            pixmap: The tile QPixmap to inspect.

        Returns:
            bool: True when the tile is uniform enough to be a placeholder.
        """
        if pixmap.isNull():
            return True
        image = pixmap.toImage().scaled(
            24, 24,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.FastTransformation)
        counts = [0] * 16
        total = image.width() * image.height()
        if total <= 0:
            return True
        for y in range(image.height()):
            for x in range(image.width()):
                gray = qGray(image.pixel(x, y))
                counts[gray >> 4] += 1
        # Merge adjacent buckets so sensor noise straddling a bucket edge
        # doesn't hide a uniform tile.
        best = max(counts[i] + counts[i + 1] for i in range(15))
        return (best / total) >= self.PLACEHOLDER_UNIFORM_FRACTION

    def _crop_from_ancestor(self, ancestor_pixmap, x_tile, y_tile, dz):
        """
        Cut the region of an ancestor tile covering (x_tile, y_tile) and
        upscale it to a full tile.

        Args:
            ancestor_pixmap: Pixmap of the ancestor tile (dz levels up).
            x_tile, y_tile: Tile coordinates of the descendant being served.
            dz: Zoom level difference (>= 1).

        Returns:
            QPixmap: A tile_size x tile_size upscaled crop.
        """
        n = 1 << dz
        sub = self.tile_size / n
        sx = int((x_tile % n) * sub)
        sy = int((y_tile % n) * sub)
        side = max(1, int(sub))
        region = ancestor_pixmap.copy(sx, sy, side, side)
        return region.scaled(
            self.tile_size, self.tile_size,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation)

    def _emit_fallback_tile(self, x_tile, y_tile, zoom):
        """
        Serve (x_tile, y_tile, zoom) from the nearest usable ancestor tile.

        Walks up the pyramid: a cached, non-placeholder ancestor is cropped
        and emitted immediately. The first ancestor that is neither cached
        nor known-failed is downloaded (when online) and the tile is queued
        on it; the fallback then completes in on_tile_downloaded.

        Returns:
            bool: True when a crop was emitted or a download was scheduled;
                False when every ancestor up to MAX_FALLBACK_LEVELS is
                exhausted (caller should emit its own last-resort tile).
        """
        for dz in range(1, self.MAX_FALLBACK_LEVELS + 1):
            ancestor_zoom = zoom - dz
            if ancestor_zoom < 1:
                break
            ax = x_tile >> dz
            ay = y_tile >> dz
            cache_path = self.cache_dir / f"{self.tile_source}_{ancestor_zoom}_{ax}_{ay}.png"
            if cache_path.exists():
                pixmap = QPixmap(str(cache_path))
                if not pixmap.isNull() and not self._looks_unavailable(pixmap):
                    self.tile_loaded.emit(
                        x_tile, y_tile, zoom,
                        self._crop_from_ancestor(pixmap, x_tile, y_tile, dz))
                    return True
                continue  # cached but unusable - climb further
            key = (ax, ay, ancestor_zoom, self.tile_source)
            if self.offline_only or key in self._fallback_failed:
                continue  # can't/shouldn't fetch this one - climb further
            self.fallback_waiters.setdefault(key, []).append((x_tile, y_tile, zoom))
            self.download_tile(ax, ay, ancestor_zoom)
            return True
        return False

    def _serve_fallback_waiters(self, x_tile, y_tile, zoom, source=None):
        """
        Re-run the fallback walk for tiles queued on a finished download.

        Called from on_tile_downloaded for both outcomes: on success the
        walk finds the fresh cache entry and emits crops; on failure (or a
        placeholder) it climbs past this ancestor. Waiters whose walk is
        fully exhausted get their own cached tile back, or gray.

        Args:
            source: The source the finished download belonged to. Waiters for
                a source that is no longer selected are dropped - the view is
                not showing that layer, and switching back reloads its
                visible tiles from scratch anyway.
        """
        if source is None:
            source = self.tile_source
        key = (x_tile, y_tile, zoom, source)
        waiters = self.fallback_waiters.pop(key, None)
        if not waiters or source != self.tile_source:
            return
        for wx, wy, wz in waiters:
            if self._emit_fallback_tile(wx, wy, wz):
                continue
            # Exhausted: fall back to the tile's own cached content (the
            # placeholder we suppressed earlier) or a gray tile.
            own_cache = self.cache_dir / f"{self.tile_source}_{wz}_{wx}_{wy}.png"
            pixmap = QPixmap(str(own_cache)) if own_cache.exists() else QPixmap()
            if pixmap.isNull():
                pixmap = QPixmap(self.tile_size, self.tile_size)
                pixmap.fill(QColor(200, 200, 200))
            self.tile_loaded.emit(wx, wy, wz, pixmap)

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

        # Clamp to the source's max and leave one level of margin for
        # smooth fitting.
        return max(1, min(self.max_zoom(), int(zoom) - 1))

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
        # A quiet 30s means the network may have recovered - let fallback
        # walks retry ancestors that previously failed to download.
        self._fallback_failed.clear()
