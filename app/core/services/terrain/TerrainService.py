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
from .TerrainProviderFactory import TerrainProviderFactory, DEFAULT_PROVIDER_ID


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

    def __init__(self, cache_dir: Optional[str] = None, enable_geoid: bool = True,
                 provider_id: Optional[str] = None, settings_service=None):
        """
        Initialize the TerrainService.

        Args:
            cache_dir: Custom cache directory
            enable_geoid: Whether to load geoid data for height conversions
            provider_id: Provider identifier (e.g. 'terrarium', 'usgs_3dep_local').
                If None, reads 'TerrainProviderId' from settings_service or
                defaults to Terrarium.
            settings_service: SettingsService used to load provider-specific
                config (e.g. 3DEP manifest/tiles paths). Lazy-imported when None.
        """
        self.logger = LoggerService()
        self.zoom = self.DEFAULT_ZOOM
        self._cache_dir = cache_dir
        self._enable_geoid = enable_geoid

        if settings_service is None:
            try:
                from core.services.SettingsService import SettingsService
                settings_service = SettingsService()
            except Exception:
                settings_service = None
        self._settings_service = settings_service

        if provider_id is None and settings_service is not None:
            provider_id = settings_service.get_setting(
                'TerrainProviderId', DEFAULT_PROVIDER_ID
            ) or DEFAULT_PROVIDER_ID

        # Build provider + cache (cache only relevant for tiled_web providers)
        self.provider = TerrainProviderFactory.create(provider_id, settings_service)
        self.cache = self._build_cache()

        self._geoid: Optional[GeoidService] = None
        if enable_geoid:
            try:
                cache_root = self.cache.cache_dir if self.cache is not None else None
                self._geoid = GeoidService(
                    cache_dir=str(cache_root / 'geoid') if (cache_root and cache_dir) else None
                )
            except Exception as e:
                self.logger.warning(f"Failed to initialize geoid service: {e}")

        self._enabled = True

        # When True, no method downloads elevation/geoid data over the network;
        # only already-cached data is used. Initialized from the app's
        # "Offline Only" preference (callers may still override, see
        # AOIService._get_terrain_service). Acts as a floor: an explicit
        # offline_only=True argument still wins.
        self.offline_only = False
        if settings_service is not None:
            try:
                self.offline_only = bool(
                    settings_service.get_bool_setting('OfflineOnly', False))
            except Exception:
                self.offline_only = False

        # Lazy Terrarium fallback used when a local-GeoTIFF provider has no
        # coverage for a query. Local 3DEP is an accuracy upgrade over the
        # global baseline, not a replacement for it: a mission outside the
        # downloaded tiles must degrade to ~30 m online data, not to nothing.
        self._fallback_provider = None
        self._fallback_cache = None
        self._fallback_logged = False

    def _build_cache(self) -> Optional[TerrainCacheService]:
        """Construct a tile cache only for tiled_web providers."""
        if self.provider.get_provider_kind() != 'tiled_web':
            return None
        return TerrainCacheService(cache_dir=self._cache_dir, provider=self.provider)

    def set_provider(self, provider_id: str):
        """Swap the active provider at runtime."""
        # Close any datasets the previous local-geotiff provider holds open
        prior_close = getattr(self.provider, 'close', None)
        if callable(prior_close):
            try:
                prior_close()
            except Exception:
                pass
        self.provider = TerrainProviderFactory.create(provider_id, self._settings_service)
        self.cache = self._build_cache()
        self._reset_fallback()

    def _reset_fallback(self):
        """Drop the lazily-built fallback pair (provider changed)."""
        if self._fallback_provider is not None:
            try:
                self._fallback_provider.close()
            except Exception:
                pass
        self._fallback_provider = None
        self._fallback_cache = None
        self._fallback_logged = False

    def _get_fallback(self):
        """(provider, cache) Terrarium pair for local-provider coverage gaps.

        Built lazily and only when the primary provider is local-GeoTIFF;
        returns (None, None) otherwise. Shares the tile cache directory with
        the normal online path so fallback downloads are reusable.
        """
        if self.provider.get_provider_kind() != 'local_geotiff':
            return None, None
        if self._fallback_provider is None:
            try:
                self._fallback_provider = TerrariumProvider()
                self._fallback_cache = TerrainCacheService(
                    cache_dir=self._cache_dir, provider=self._fallback_provider)
            except Exception as e:
                self.logger.warning(f"TerrainService: fallback unavailable: {e}")
                self._fallback_provider = None
                self._fallback_cache = None
                return None, None
        return self._fallback_provider, self._fallback_cache

    def _log_fallback_once(self, what: str):
        if not self._fallback_logged:
            self._fallback_logged = True
            self.logger.info(
                f"TerrainService: local DEM has no coverage for {what}; "
                "falling back to AWS Terrain Tiles (~30 m).")

    def warmup(self) -> None:
        """Eagerly load the geoid grid and any provider-specific indices.

        Called by long-running batch jobs (e.g. the WALDO pre-pass) so the
        first elevation sample doesn't pay a multi-second stall while the
        EGM96 grid loads from disk. Safe to call repeatedly.
        """
        if self._geoid is not None:
            try:
                self._geoid.is_available()
            except Exception as e:
                self.logger.warning(f"Geoid warmup failed: {e}")
        try:
            self.provider.warmup()
        except Exception as e:
            self.logger.warning(f"Provider warmup failed: {e}")

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

        # Honor the service-wide offline floor (e.g. app "Offline Only" mode).
        offline_only = offline_only or self.offline_only

        # Local-GeoTIFF providers (e.g. USGS 3DEP) bypass the tile cache.
        if self.provider.get_provider_kind() == 'local_geotiff':
            elevation = self.provider.sample_elevation(lat, lon)
            if elevation is None:
                # Outside the downloaded tiles: degrade to the global online
                # baseline instead of pretending the terrain is flat.
                fallback = self._fallback_elevation(lat, lon, offline_only)
                if fallback is not None:
                    return fallback
                return self._create_flat_result(lat, lon)
            geoid_undulation = None
            if self._geoid:
                geoid_undulation = self._geoid.get_undulation(lat, lon, offline_only=offline_only)
            datum = self.provider.get_datum_info()
            return ElevationResult(
                elevation_m=elevation,
                source='terrain',
                geoid_undulation_m=geoid_undulation,
                provider=self.provider.get_provider_name(),
                zoom_level=None,
                resolution_m=datum.get('resolution_m'),
                from_cache=True,
            )

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
            geoid_undulation = self._geoid.get_undulation(lat, lon, offline_only=offline_only)

        return ElevationResult(
            elevation_m=elevation,
            source='terrain',
            geoid_undulation_m=geoid_undulation,
            provider=self.provider.get_provider_name(),
            zoom_level=self.zoom,
            resolution_m=self.ZOOM_RESOLUTION.get(self.zoom, 38),
            from_cache=from_cache
        )

    def _fallback_elevation(self, lat: float, lon: float,
                            offline_only: bool) -> Optional[ElevationResult]:
        """Point elevation from the Terrarium fallback, or None.

        Mirrors the tiled_web branch of :meth:`get_elevation` but against the
        fallback provider/cache. Honors offline mode (cached tiles only).
        """
        provider, cache = self._get_fallback()
        if cache is None:
            return None
        self._log_fallback_once(f"({lat:.5f}, {lon:.5f})")

        tile_x, tile_y = provider.lat_lon_to_tile(lat, lon, self.zoom)
        pixel_x, pixel_y = provider.lat_lon_to_pixel_in_tile(lat, lon, self.zoom)
        if offline_only:
            tile = cache.get_tile_if_cached(self.zoom, tile_x, tile_y)
            from_cache = True
        else:
            tile = cache.get_tile(self.zoom, tile_x, tile_y)
            from_cache = cache.is_tile_cached(self.zoom, tile_x, tile_y)
        if tile is None:
            return None
        try:
            elevation = provider.decode_elevation_bilinear(tile, pixel_x, pixel_y)
        except Exception as e:
            self.logger.error(f"Fallback elevation decode failed: {e}")
            return None

        geoid_undulation = None
        if self._geoid:
            geoid_undulation = self._geoid.get_undulation(lat, lon, offline_only=offline_only)
        return ElevationResult(
            elevation_m=elevation,
            source='terrain',
            geoid_undulation_m=geoid_undulation,
            provider=f"{provider.get_provider_name()} (fallback)",
            zoom_level=self.zoom,
            resolution_m=self.ZOOM_RESOLUTION.get(self.zoom, 38),
            from_cache=from_cache,
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

    def sample_grid(self, bounds_wgs84, resolution_m: float, offline_only: bool = False):
        """Sample an elevation grid covering ``bounds_wgs84`` at ~``resolution_m``.

        Convenience wrapper deriving a lattice-snapped EPSG:3857 ``GridSpec`` and
        delegating to :meth:`sample_grid_spec`. Returns a ``GridSample`` or None.
        """
        from .grid import spec_for_bounds_wgs84
        return self.sample_grid_spec(spec_for_bounds_wgs84(bounds_wgs84, resolution_m),
                                     offline_only=offline_only)

    def sample_grid_spec(self, spec, offline_only: bool = False):
        """Sample the active provider onto ``spec`` (EPSG:3857 GridSpec).

        Dispatches by provider kind, mirroring :meth:`get_elevation`:
        local_geotiff providers use their windowed-reproject fast path; tiled_web
        providers go through the Terrarium mosaic sampler; any other provider
        falls back to the ABC per-point slow path. Returns a ``GridSample`` or
        None when terrain is disabled or no data covers the grid.
        """
        if not self._enabled:
            return None

        kind = self.provider.get_provider_kind()
        if kind == 'local_geotiff':
            # The provider's windowed-reproject path is authoritative; if no
            # tile covers the grid, degrade to the global online baseline
            # (offline mode still serves cached tiles) rather than skipping.
            sample = self.provider.sample_grid_spec(spec)
            if sample is not None:
                return sample
            fallback = self._sample_grid_fallback(spec, offline_only)
            if fallback is not None:
                return fallback
            return None

        if kind == 'tiled_web':
            from .TerrariumGridSampler import sample_grid_tiled
            sample = sample_grid_tiled(self.provider, self.cache, spec, self.zoom,
                                       offline_only=offline_only)
            if sample is not None:
                return sample

        # Last resort: ABC per-point slow path (works for any sample_elevation provider).
        return self.provider.sample_grid_spec(spec)

    def _sample_grid_fallback(self, spec, offline_only: bool):
        """Grid sample from the Terrarium fallback, tagged with its source."""
        provider, cache = self._get_fallback()
        if cache is None:
            return None
        self._log_fallback_once(
            f"grid {spec.width}x{spec.height} @ {spec.cell_size:.1f}m")
        try:
            from .TerrariumGridSampler import sample_grid_tiled
            sample = sample_grid_tiled(
                provider, cache, spec, self.zoom,
                offline_only=offline_only or self.offline_only)
        except Exception as e:
            self.logger.warning(f"TerrainService: fallback grid sample failed: {e}")
            return None
        if sample is not None:
            # Let consumers (e.g. the POD pass) count fallback-served frames.
            sample.source = 'terrarium_fallback'
        return sample

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

    def get_geoid_undulation(self, lat: float, lon: float, offline_only: bool = False) -> Optional[float]:
        """
        Get geoid undulation at a location.

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees
            offline_only: If True, never download/synthesize the geoid grid.
                Combined with the service-wide offline floor (self.offline_only).

        Returns:
            Geoid undulation (N) in meters, or None if unavailable
        """
        if self._geoid is None:
            return None
        return self._geoid.get_undulation(lat, lon, offline_only=offline_only or self.offline_only)

    def prefetch_area(self, lat: float, lon: float, radius_km: float = 5) -> int:
        """
        Pre-download terrain data for an area.

        Args:
            lat: Center latitude
            lon: Center longitude
            radius_km: Radius in kilometers

        Returns:
            Number of tiles downloaded (0 for local-only providers).
        """
        if self.cache is None:
            return 0
        return self.cache.prefetch_tiles(lat, lon, radius_km, self.zoom)

    def is_terrain_available(self, lat: float, lon: float) -> bool:
        """Check if terrain data is available for a location (from cache or local index)."""
        if self.provider.get_provider_kind() == 'local_geotiff':
            return self.provider.lookup_tile(lat, lon) is not None
        if self.cache is None:
            return False
        tile_x, tile_y = self.provider.lat_lon_to_tile(lat, lon, self.zoom)
        return self.cache.is_tile_cached(self.zoom, tile_x, tile_y)

    def is_online(self) -> bool:
        """Check if the terrain service is accessible online (or local data is reachable)."""
        if self.cache is None:
            return self.provider.get_provider_kind() == 'local_geotiff'
        return self.cache.is_online()

    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the terrain service."""
        cache_info = self.cache.get_cache_info() if self.cache is not None else None
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
        """Clear all cached terrain data (no-op for local-only providers)."""
        if self.cache is None:
            return 0
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
