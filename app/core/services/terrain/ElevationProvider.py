"""
ElevationProvider - Providers for fetching elevation data from online services.

Supports:
- AWS Terrain Tiles (Terrarium format) - Primary provider
- Nextzen Terrain Tiles - Backup provider
"""

import math
import struct
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from PIL import Image
import io
import requests

from core.services.LoggerService import LoggerService


class ElevationProvider(ABC):
    """Abstract base class for elevation data providers.

    Two provider kinds are supported:

    * `'tiled_web'` — implements `get_tile_url` + `decode_elevation` (the
      existing TerrainService cache path drives this).
    * `'local_geotiff'` — implements `sample_elevation(lat, lon)` and is
      consulted directly by TerrainService without a tile cache.
    """

    def get_provider_kind(self) -> str:
        """Return the provider category used by TerrainService to dispatch.

        Defaults to 'tiled_web' so existing subclasses (TerrariumProvider)
        keep their original behaviour without an explicit override.
        """
        return 'tiled_web'

    def warmup(self) -> None:
        """Eagerly load any heavy state (manifests, indices) that would
        otherwise stall the first sample call. Default no-op; tile-based
        providers don't have anything to load up-front."""
        return None

    def covers(self, bounds_wgs84) -> str:
        """How much of ``bounds_wgs84`` (min_lon, min_lat, max_lon, max_lat)
        this provider can serve: ``'full' | 'partial' | 'none'``.

        Tiled-web providers are global, so the default reports 'full';
        local providers override with a manifest-driven answer.
        """
        return 'full' if self.get_provider_kind() == 'tiled_web' else 'none'

    # Upper bound on cells the slow (per-point) grid fallback will sample before
    # refusing, so a mis-sized bbox can't spin for an hour of point queries.
    SLOW_GRID_CELL_LIMIT = 250_000

    def sample_elevation(self, lat: float, lon: float) -> Optional[float]:
        """Return orthometric elevation in meters at lat/lon, or None if unavailable.

        Default raises NotImplementedError; required for `local_geotiff` providers.
        Tile-based providers should leave this as the default and rely on the
        TerrainService tile-cache path.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} did not override sample_elevation; "
            "this is required for non-tile providers."
        )

    def sample_grid(self, bounds_wgs84: Tuple[float, float, float, float],
                    resolution_m: float):
        """Return an elevation grid covering ``bounds_wgs84`` at ~``resolution_m``.

        Convenience wrapper: derives a lattice-snapped EPSG:3857 ``GridSpec`` and
        delegates to :meth:`sample_grid_spec`. ``bounds_wgs84`` is
        (min_lon, min_lat, max_lon, max_lat).
        """
        from .grid import spec_for_bounds_wgs84
        return self.sample_grid_spec(spec_for_bounds_wgs84(bounds_wgs84, resolution_m))

    def sample_grid_spec(self, spec):
        """Return a ``GridSample`` for ``spec``, or None if unavailable.

        Default slow path: loop :meth:`sample_elevation` over cell centers. Works
        for any provider that implements ``sample_elevation``; providers with a
        fast windowed path (e.g. local GeoTIFF) override this. Returns None when
        ``sample_elevation`` is unimplemented (tile-based providers — their fast
        path lives on ``TerrainService``) or when the grid exceeds
        ``SLOW_GRID_CELL_LIMIT``.
        """
        import numpy as np
        from .grid import GridSample, mercator_to_lonlat

        n_cells = spec.width * spec.height
        if n_cells > self.SLOW_GRID_CELL_LIMIT:
            logger = getattr(self, 'logger', None)
            if logger is not None:
                logger.warning(
                    f"{self.__class__.__name__}: grid {spec.width}x{spec.height} exceeds "
                    f"slow-path limit {self.SLOW_GRID_CELL_LIMIT}; refusing."
                )
            return None

        xs, ys = spec.cell_centers()
        data = np.full((spec.height, spec.width), np.nan, dtype=np.float32)
        try:
            for i, y in enumerate(ys):
                for j, x in enumerate(xs):
                    lon, lat = mercator_to_lonlat(float(x), float(y))
                    value = self.sample_elevation(lat, lon)
                    if value is not None:
                        data[i, j] = value
        except NotImplementedError:
            return None

        datum = self.get_datum_info()
        datum_note = f"{datum.get('type', '')} {datum.get('name', '')}".strip()
        return GridSample(data=data, transform=spec.transform, crs=spec.crs,
                          datum_note=datum_note)

    def get_tile_url(self, z: int, x: int, y: int) -> str:
        """Get the URL for a specific tile (tile-based providers only)."""
        raise NotImplementedError(
            f"{self.__class__.__name__} is not a tile-based provider."
        )

    def decode_elevation(self, image: Image.Image, pixel_x: int, pixel_y: int) -> float:
        """Decode elevation from a pixel (tile-based providers only)."""
        raise NotImplementedError(
            f"{self.__class__.__name__} is not a tile-based provider."
        )

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of this provider."""
        pass

    @abstractmethod
    def get_datum_info(self) -> dict:
        """Get information about the vertical datum used by this provider.

        Returns:
            dict with 'name', 'type' ('orthometric' or 'ellipsoidal'), 'geoid_model'
        """
        pass


class TerrariumProvider(ElevationProvider):
    """
    AWS Terrain Tiles provider using Mapzen Terrarium format.

    Terrarium format encodes elevation in RGB values:
    elevation = (R * 256 + G + B / 256) - 32768

    Data source: SRTM + ASTER GDEM
    Resolution: ~30m at zoom 10-14
    Coverage: Global (except poles)
    Vertical datum: Orthometric (EGM96)
    """

    # AWS S3 public bucket - no API key required
    BASE_URL = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium"

    # Alternative URLs for fallback
    FALLBACK_URLS = [
        "https://tile.nextzen.org/tilezen/terrain/v1/256/terrarium",
    ]

    # Recommended zoom level for ~30m resolution
    DEFAULT_ZOOM = 12

    def __init__(self, timeout: float = 10.0):
        """Initialize the Terrarium provider.

        Args:
            timeout: Request timeout in seconds
        """
        self.logger = LoggerService()
        self.timeout = timeout
        self._session = None

    @property
    def session(self) -> requests.Session:
        """Lazy-initialized requests session for connection pooling."""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({
                'User-Agent': 'ADIAT/1.0 (Drone Image Analysis Tool)'
            })
        return self._session

    def get_tile_url(self, z: int, x: int, y: int) -> str:
        """Get the URL for a specific tile."""
        return f"{self.BASE_URL}/{z}/{x}/{y}.png"

    def get_fallback_urls(self, z: int, x: int, y: int) -> list:
        """Get fallback URLs for a tile."""
        urls = []
        for base in self.FALLBACK_URLS:
            urls.append(f"{base}/{z}/{x}/{y}.png")
        return urls

    def decode_elevation(self, image: Image.Image, pixel_x: int, pixel_y: int) -> float:
        """
        Decode elevation from Terrarium format.

        Formula: elevation = (R * 256 + G + B / 256) - 32768
        """
        # Ensure we're working with RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Clamp coordinates to valid range
        pixel_x = max(0, min(pixel_x, image.width - 1))
        pixel_y = max(0, min(pixel_y, image.height - 1))

        r, g, b = image.getpixel((pixel_x, pixel_y))

        # Terrarium encoding formula
        elevation = (r * 256 + g + b / 256) - 32768

        return elevation

    def decode_elevation_bilinear(self, image: Image.Image, pixel_x: float, pixel_y: float) -> float:
        """
        Decode elevation with bilinear interpolation for sub-pixel accuracy.

        Args:
            image: PIL Image of the tile
            pixel_x: X coordinate (can be fractional)
            pixel_y: Y coordinate (can be fractional)

        Returns:
            Interpolated elevation in meters
        """
        # Get integer and fractional parts
        x0 = int(pixel_x)
        y0 = int(pixel_y)
        x1 = min(x0 + 1, image.width - 1)
        y1 = min(y0 + 1, image.height - 1)

        fx = pixel_x - x0
        fy = pixel_y - y0

        # Get elevations at four corners
        e00 = self.decode_elevation(image, x0, y0)
        e10 = self.decode_elevation(image, x1, y0)
        e01 = self.decode_elevation(image, x0, y1)
        e11 = self.decode_elevation(image, x1, y1)

        # Bilinear interpolation
        e0 = e00 * (1 - fx) + e10 * fx
        e1 = e01 * (1 - fx) + e11 * fx
        elevation = e0 * (1 - fy) + e1 * fy

        return elevation

    def get_provider_name(self) -> str:
        return "AWS Terrain Tiles"

    def get_datum_info(self) -> dict:
        return {
            'name': 'EGM96',
            'type': 'orthometric',
            'geoid_model': 'EGM96',
            'source': 'SRTM + ASTER GDEM',
            'resolution_m': 30
        }

    def download_tile(self, z: int, x: int, y: int) -> Optional[bytes]:
        """
        Download a tile from the server.

        Args:
            z: Zoom level
            x: Tile X coordinate
            y: Tile Y coordinate

        Returns:
            PNG image bytes or None if download failed
        """
        # Try primary URL first
        url = self.get_tile_url(z, x, y)
        urls_to_try = [url] + self.get_fallback_urls(z, x, y)

        for try_url in urls_to_try:
            try:
                response = self.session.get(try_url, timeout=self.timeout)
                if response.status_code == 200:
                    # Validate it's a valid PNG
                    try:
                        img = Image.open(io.BytesIO(response.content))
                        img.verify()
                        return response.content
                    except Exception:
                        self.logger.warning(f"Invalid image from {try_url}")
                        continue
                elif response.status_code == 404:
                    # Tile doesn't exist (e.g., ocean areas)
                    return None
                else:
                    self.logger.warning(f"HTTP {response.status_code} from {try_url}")
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed for {try_url}: {e}")
                continue

        return None

    @staticmethod
    def lat_lon_to_tile(lat: float, lon: float, zoom: int) -> Tuple[int, int]:
        """
        Convert latitude/longitude to tile coordinates.

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees
            zoom: Zoom level

        Returns:
            Tuple of (tile_x, tile_y)
        """
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        x = int((lon + 180.0) / 360.0 * n)
        y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)

        # Clamp to valid range
        x = max(0, min(x, int(n) - 1))
        y = max(0, min(y, int(n) - 1))

        return x, y

    @staticmethod
    def lat_lon_to_pixel_in_tile(lat: float, lon: float, zoom: int, tile_size: int = 256) -> Tuple[float, float]:
        """
        Convert latitude/longitude to pixel coordinates within a tile.

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees
            zoom: Zoom level
            tile_size: Size of tile in pixels (default 256)

        Returns:
            Tuple of (pixel_x, pixel_y) as floats for sub-pixel accuracy
        """
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom

        # Get global pixel coordinates
        global_x = (lon + 180.0) / 360.0 * n * tile_size
        global_y = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n * tile_size

        # Get tile coordinates
        tile_x = int(global_x / tile_size)
        tile_y = int(global_y / tile_size)

        # Get pixel within tile
        pixel_x = global_x - tile_x * tile_size
        pixel_y = global_y - tile_y * tile_size

        return pixel_x, pixel_y

    def close(self):
        """Close the requests session."""
        if self._session is not None:
            self._session.close()
            self._session = None
