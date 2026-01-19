"""
TerrainService - Main facade for terrain elevation data.

Provides:
- Elevation lookup at any latitude/longitude
- Automatic caching and offline support
- Geoid correction for height datum conversions
- Fallback handling when data is unavailable
"""

import math
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any
from PIL import Image

from core.services.LoggerService import LoggerService
from .TerrainCacheService import TerrainCacheService
from .GeoidService import GeoidService
from .ElevationProvider import TerrariumProvider


@dataclass
class ElevationResult:
    """Result of an elevation query."""
    elevation_m: Optional[float]  # Elevation in meters (orthometric)
    source: str  # 'terrain', 'flat', 'error'
    geoid_undulation_m: Optional[float]  # Geoid undulation at location
    provider: Optional[str]  # Provider name if terrain was used
    zoom_level: Optional[int]  # Zoom level used for query
    resolution_m: Optional[float]  # Approximate resolution in meters
    from_cache: bool  # Whether data came from cache

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'elevation_m': self.elevation_m,
            'source': self.source,
            'geoid_undulation_m': self.geoid_undulation_m,
            'provider': self.provider,
            'zoom_level': self.zoom_level,
            'resolution_m': self.resolution_m,
            'from_cache': self.from_cache
        }


class TerrainService:
    """
    Main service for terrain elevation data.

    Usage:
        service = TerrainService()
        result = service.get_elevation(lat, lon)
        if result.source == 'terrain':
            print(f"Terrain elevation: {result.elevation_m}m")
        else:
            print("Using flat terrain assumption")
    """

    # Zoom level to use for queries (affects resolution)
    # Zoom 12 gives ~38m resolution, good balance of accuracy and data size
    DEFAULT_ZOOM = 12

    # Approximate resolution in meters at different zoom levels
    ZOOM_RESOLUTION = {
        10: 152,  # ~152m
        11: 76,   # ~76m
        12: 38,   # ~38m
        13: 19,   # ~19m
        14: 9.5,  # ~9.5m
    }

    def __init__(self, cache_dir: Optional[str] = None, enable_geoid: bool = True):
        """
        Initialize the TerrainService.

        Args:
            cache_dir: Custom cache directory
            enable_geoid: Whether to load geoid data for height conversions
        """
        self.logger = LoggerService()
        self.zoom = self.DEFAULT_ZOOM

        # Initialize sub-services
        self.provider = TerrariumProvider()
        self.cache = TerrainCacheService(cache_dir=cache_dir, provider=self.provider)

        self._geoid: Optional[GeoidService] = None
        if enable_geoid:
            try:
                self._geoid = GeoidService(
                    cache_dir=str(self.cache.cache_dir / 'geoid') if cache_dir else None
                )
            except Exception as e:
                self.logger.warning(f"Failed to initialize geoid service: {e}")

        self._enabled = True

    @property
    def enabled(self) -> bool:
        """Whether terrain lookup is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        """Enable or disable terrain lookup."""
        self._enabled = value

    def get_elevation(self, lat: float, lon: float, offline_only: bool = False) -> ElevationResult:
        """
        Get terrain elevation at a location.

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees
            offline_only: If True, only use cached data

        Returns:
            ElevationResult with elevation data
        """
        if not self._enabled:
            return self._create_flat_result(lat, lon)

        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            self.logger.warning(f"Invalid coordinates: {lat}, {lon}")
            return self._create_error_result("Invalid coordinates")

        # Get tile coordinates
        tile_x, tile_y = self.provider.lat_lon_to_tile(lat, lon, self.zoom)
        pixel_x, pixel_y = self.provider.lat_lon_to_pixel_in_tile(lat, lon, self.zoom)

        # Get tile from cache or download
        if offline_only:
            tile = self.cache.get_tile_if_cached(self.zoom, tile_x, tile_y)
            from_cache = True
        else:
            tile = self.cache.get_tile(self.zoom, tile_x, tile_y)
            from_cache = self.cache.is_tile_cached(self.zoom, tile_x, tile_y)

        if tile is None:
            return self._create_flat_result(lat, lon)

        # Decode elevation
        try:
            elevation = self.provider.decode_elevation_bilinear(tile, pixel_x, pixel_y)
        except Exception as e:
            self.logger.error(f"Failed to decode elevation: {e}")
            return self._create_error_result(str(e))

        # Get geoid undulation
        geoid_undulation = None
        if self._geoid:
            geoid_undulation = self._geoid.get_undulation(lat, lon)

        return ElevationResult(
            elevation_m=elevation,
            source='terrain',
            geoid_undulation_m=geoid_undulation,
            provider=self.provider.get_provider_name(),
            zoom_level=self.zoom,
            resolution_m=self.ZOOM_RESOLUTION.get(self.zoom, 38),
            from_cache=from_cache
        )

    def get_elevation_batch(self, locations: list, offline_only: bool = False) -> list:
        """
        Get elevation for multiple locations efficiently.

        Args:
            locations: List of (lat, lon) tuples
            offline_only: If True, only use cached data

        Returns:
            List of ElevationResult objects
        """
        results = []
        for lat, lon in locations:
            results.append(self.get_elevation(lat, lon, offline_only))
        return results

    def get_effective_altitude_agl(
        self,
        drone_lat: float,
        drone_lon: float,
        takeoff_elevation_m: Optional[float],
        relative_altitude_m: float,
        target_lat: float,
        target_lon: float,
        offline_only: bool = False
    ) -> Tuple[float, str]:
        """
        Calculate effective AGL (Above Ground Level) at a target location.

        This handles the case where terrain varies between takeoff and target.

        Args:
            drone_lat: Drone GPS latitude
            drone_lon: Drone GPS longitude
            takeoff_elevation_m: Takeoff point elevation (orthometric), or None to lookup
            relative_altitude_m: Drone's reported AGL from takeoff point
            target_lat: Target location latitude
            target_lon: Target location longitude
            offline_only: If True, only use cached data

        Returns:
            Tuple of (effective_agl_m, source) where source is 'terrain' or 'flat'
        """
        if not self._enabled:
            return relative_altitude_m, 'flat'

        # Get terrain elevation at target
        target_result = self.get_elevation(target_lat, target_lon, offline_only)

        if target_result.source != 'terrain' or target_result.elevation_m is None:
            return relative_altitude_m, 'flat'

        # If we don't have takeoff elevation, try to get it from drone position
        if takeoff_elevation_m is None:
            # Estimate takeoff elevation from drone position
            # Drone's true elevation = takeoff_elevation + relative_altitude
            # We can't determine this without external data, so fall back
            # to using the target terrain elevation directly

            # Assume drone elevation (orthometric) = target_terrain + relative_altitude
            # This is an approximation that works when terrain is relatively flat
            drone_elevation_orthometric = target_result.elevation_m + relative_altitude_m

            # AGL at target = drone_elevation - target_terrain
            effective_agl = drone_elevation_orthometric - target_result.elevation_m
            return effective_agl, 'terrain'

        else:
            # We have takeoff elevation
            # Drone elevation (orthometric) = takeoff_elevation + relative_altitude
            drone_elevation_orthometric = takeoff_elevation_m + relative_altitude_m

            # AGL at target = drone_elevation - target_terrain
            effective_agl = drone_elevation_orthometric - target_result.elevation_m

            # Clamp to positive value (can't be below ground)
            effective_agl = max(1.0, effective_agl)

            return effective_agl, 'terrain'

    def convert_ellipsoidal_to_orthometric(self, lat: float, lon: float, h_ellipsoidal: float) -> Optional[float]:
        """
        Convert ellipsoidal (GPS) height to orthometric (MSL) height.

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees
            h_ellipsoidal: Height above WGS84 ellipsoid in meters

        Returns:
            Orthometric height in meters, or None if conversion unavailable
        """
        if self._geoid is None:
            return None
        return self._geoid.ellipsoidal_to_orthometric(lat, lon, h_ellipsoidal)

    def convert_orthometric_to_ellipsoidal(self, lat: float, lon: float, h_orthometric: float) -> Optional[float]:
        """
        Convert orthometric (MSL) height to ellipsoidal (GPS) height.

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees
            h_orthometric: Height above mean sea level in meters

        Returns:
            Ellipsoidal height in meters, or None if conversion unavailable
        """
        if self._geoid is None:
            return None
        return self._geoid.orthometric_to_ellipsoidal(lat, lon, h_orthometric)

    def get_geoid_undulation(self, lat: float, lon: float) -> Optional[float]:
        """
        Get geoid undulation at a location.

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees

        Returns:
            Geoid undulation (N) in meters, or None if unavailable
        """
        if self._geoid is None:
            return None
        return self._geoid.get_undulation(lat, lon)

    def prefetch_area(self, lat: float, lon: float, radius_km: float = 5) -> int:
        """
        Pre-download terrain data for an area.

        Args:
            lat: Center latitude
            lon: Center longitude
            radius_km: Radius in kilometers

        Returns:
            Number of tiles downloaded
        """
        return self.cache.prefetch_tiles(lat, lon, radius_km, self.zoom)

    def is_terrain_available(self, lat: float, lon: float) -> bool:
        """Check if terrain data is available for a location (from cache)."""
        tile_x, tile_y = self.provider.lat_lon_to_tile(lat, lon, self.zoom)
        return self.cache.is_tile_cached(self.zoom, tile_x, tile_y)

    def is_online(self) -> bool:
        """Check if the terrain service is accessible online."""
        return self.cache.is_online()

    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the terrain service."""
        cache_info = self.cache.get_cache_info()
        geoid_info = self._geoid.get_cache_info() if self._geoid else None

        return {
            'enabled': self._enabled,
            'zoom_level': self.zoom,
            'resolution_m': self.ZOOM_RESOLUTION.get(self.zoom, 38),
            'provider': self.provider.get_provider_name(),
            'datum': self.provider.get_datum_info(),
            'cache': cache_info,
            'geoid': geoid_info
        }

    def clear_cache(self) -> int:
        """Clear all cached terrain data."""
        return self.cache.clear_cache()

    def set_zoom_level(self, zoom: int):
        """
        Set the zoom level for elevation queries.

        Args:
            zoom: Zoom level (10-14 recommended)
        """
        if 0 <= zoom <= 14:
            self.zoom = zoom
        else:
            self.logger.warning(f"Invalid zoom level {zoom}, using {self.DEFAULT_ZOOM}")
            self.zoom = self.DEFAULT_ZOOM

    def _create_flat_result(self, lat: float, lon: float) -> ElevationResult:
        """Create a result indicating flat terrain assumption."""
        geoid_undulation = None
        if self._geoid:
            geoid_undulation = self._geoid.get_undulation(lat, lon)

        return ElevationResult(
            elevation_m=None,
            source='flat',
            geoid_undulation_m=geoid_undulation,
            provider=None,
            zoom_level=None,
            resolution_m=None,
            from_cache=False
        )

    def _create_error_result(self, error: str) -> ElevationResult:
        """Create a result indicating an error."""
        return ElevationResult(
            elevation_m=None,
            source='error',
            geoid_undulation_m=None,
            provider=None,
            zoom_level=None,
            resolution_m=None,
            from_cache=False
        )

