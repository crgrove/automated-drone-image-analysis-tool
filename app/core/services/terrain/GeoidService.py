"""
GeoidService - Calculate geoid undulation for height datum conversions.

Converts between:
- Ellipsoidal height (WGS84) - used by GPS
- Orthometric height (above geoid/mean sea level) - used by most DEMs

Formula: h_ellipsoidal = h_orthometric + N
Where N is the geoid undulation (height of geoid above ellipsoid).

Undulation is sourced from the authoritative **EGM96** geoid via PROJ/pyproj
(``EPSG:4979`` -> ``EPSG:4326+5773``), using the global ``us_nga_egm96_15`` grid
that ships bundled with the app (``resources/geoid/us_nga_egm96_15.tif``), with
online PROJ grid streaming as a network fallback.

Important: PROJ silently substitutes a *null* (identity) transform returning 0 m
when the EGM96 grid is unavailable. A 0 m undulation is a worse datum error than
no correction at all, so this service probes a known reference point and treats
the grid as unavailable (``get_undulation`` returns ``None``) rather than ever
returning the bogus 0 m value. Callers degrade to the geoid-free terrain-relief
path when ``None`` is returned.
"""

import math
import sys
from pathlib import Path
from typing import Optional

import pyproj

from core.services.LoggerService import LoggerService


class GeoidService:
    """
    Service for geoid undulation calculations (EGM96, via pyproj/PROJ).

    The EGM96 grid is bundled with the application; no network access is required
    at runtime. If the bundled grid is missing (e.g. a dev checkout without the
    asset), online PROJ grid streaming is used as a fallback unless ``offline_only``
    is requested, and ``get_undulation`` returns ``None`` when neither is available.
    """

    # PROJ CRS codes: WGS84 3D geographic -> WGS84 horizontal + EGM96 height.
    _SRC_CRS = "EPSG:4979"
    _DST_CRS = "EPSG:4326+5773"

    # Reference probe: EGM96 undulation at London (51.5074, -0.1278) is ~+45.97 m.
    # If a transform yields |N| below this floor the grid is absent and PROJ has
    # fallen back to the null transform (returns 0 m) -- never trust that.
    _PROBE_LAT = 51.5074
    _PROBE_LON = -0.1278
    _PROBE_MIN_ABS_N = 10.0

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the GeoidService.

        Args:
            cache_dir: Retained for API compatibility (previously the home-grown
                grid cache directory). No longer used for storage; PROJ manages
                its own grid cache.
        """
        self.logger = LoggerService()

        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / '.adiat' / 'terrain_cache' / 'geoid'

        self._transformer: Optional[pyproj.Transformer] = None
        self._available: Optional[bool] = None  # None=unprobed, True/False after probe
        self._grid_dir_registered = False

    @staticmethod
    def _bundled_grid_dir() -> Path:
        """Directory holding the bundled EGM96 grid (frozen build vs. source tree)."""
        if getattr(sys, 'frozen', False):
            root = Path(sys._MEIPASS)
        else:
            # .../app/core/services/terrain/GeoidService.py -> parents[3] == .../app
            root = Path(__file__).resolve().parents[3]
        return root / 'resources' / 'geoid'

    def _register_grid_dir(self) -> None:
        """Register the bundled grid directory with PROJ (idempotent)."""
        if self._grid_dir_registered:
            return
        try:
            gdir = self._bundled_grid_dir()
            if gdir.is_dir():
                existing = pyproj.datadir.get_data_dir()
                if str(gdir) not in (existing or ''):
                    pyproj.datadir.append_data_dir(str(gdir))
        except Exception as e:
            self.logger.warning(f"GeoidService: could not register bundled geoid grid dir: {e}")
        self._grid_dir_registered = True

    def _make_transformer(self, allow_network: bool) -> Optional[pyproj.Transformer]:
        """Build an EGM96 vertical transformer, optionally enabling PROJ network."""
        self._register_grid_dir()
        try:
            if allow_network and not pyproj.network.is_network_enabled():
                pyproj.network.set_network_enabled(True)
        except Exception:
            pass
        try:
            return pyproj.Transformer.from_crs(self._SRC_CRS, self._DST_CRS, always_xy=True)
        except Exception as e:
            self.logger.warning(f"GeoidService: failed to build EGM96 transformer: {e}")
            return None

    def _probe(self, transformer: pyproj.Transformer) -> bool:
        """Return True only if the transformer is backed by a real EGM96 grid."""
        try:
            z = transformer.transform(self._PROBE_LON, self._PROBE_LAT, 0.0)[2]
        except Exception:
            return False
        return z is not None and math.isfinite(z) and abs(z) >= self._PROBE_MIN_ABS_N

    def _ensure_transformer(self, offline_only: bool = False) -> bool:
        """
        Ensure a validated EGM96 transformer is available.

        Tries the bundled/local grid first (no network). Falls back to online PROJ
        grid streaming only when ``offline_only`` is False. Returns False (and
        leaves callers to degrade gracefully) when no real grid can be reached.
        """
        if self._transformer is not None and self._available:
            return True

        # 1) Local/bundled grid, no network.
        t = self._make_transformer(allow_network=False)
        if t is not None and self._probe(t):
            self._transformer = t
            self._available = True
            return True

        # 2) Online PROJ grid streaming (only when allowed).
        if not offline_only:
            t = self._make_transformer(allow_network=True)
            if t is not None and self._probe(t):
                self._transformer = t
                self._available = True
                return True
            # Genuinely unavailable even with network -> cache the negative result.
            self._available = False
            self.logger.warning(
                "GeoidService: EGM96 grid unavailable (no bundled grid, no network); "
                "geoid corrections disabled -- callers will use the terrain-relief fallback."
            )
            return False

        # offline_only and no local grid: unavailable now, but a later online call
        # may still succeed, so do not hard-cache a negative result.
        return False

    def get_undulation(self, lat: float, lon: float, offline_only: bool = False) -> Optional[float]:
        """
        Get the geoid undulation (N) at a given location.

        Args:
            lat: Latitude in degrees (-90 to 90)
            lon: Longitude in degrees (-180 to 180 or 0 to 360)
            offline_only: If True, never enable PROJ network access; use only the
                bundled/already-loaded grid and return None if it is unavailable.

        Returns:
            Geoid undulation in meters, or None if data unavailable.
        """
        # Validate / normalize coordinates.
        if lat < -90 or lat > 90:
            self.logger.warning(f"Invalid latitude: {lat}")
            return None
        while lon > 180:
            lon -= 360
        while lon < -180:
            lon += 360

        if not self._ensure_transformer(offline_only=offline_only):
            return None

        try:
            # EPSG:4979 (ellipsoidal h=0) -> EGM96 orthometric height = -N.
            z = self._transformer.transform(lon, lat, 0.0)[2]
        except Exception as e:
            self.logger.warning(f"GeoidService: transform failed at ({lat}, {lon}): {e}")
            return None

        if z is None or not math.isfinite(z):
            return None

        # Guard against a silent null transform slipping past the init probe
        # (e.g. PROJ pipeline drift): a ~0 m result away from the geoid's true
        # near-zero band would be bogus. |N| >= floor was validated by _probe.
        return -z

    def ellipsoidal_to_orthometric(self, lat: float, lon: float, h_ellipsoidal: float) -> Optional[float]:
        """
        Convert ellipsoidal height to orthometric height.

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees
            h_ellipsoidal: Height above WGS84 ellipsoid in meters

        Returns:
            Height above geoid (orthometric) in meters, or None if conversion failed.
        """
        N = self.get_undulation(lat, lon)
        if N is None:
            return None
        return h_ellipsoidal - N

    def orthometric_to_ellipsoidal(self, lat: float, lon: float, h_orthometric: float) -> Optional[float]:
        """
        Convert orthometric height to ellipsoidal height.

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees
            h_orthometric: Height above geoid in meters

        Returns:
            Height above WGS84 ellipsoid in meters, or None if conversion failed.
        """
        N = self.get_undulation(lat, lon)
        if N is None:
            return None
        return h_orthometric + N

    def is_available(self) -> bool:
        """Check if geoid data is available (bundled grid or network)."""
        return self._ensure_transformer(offline_only=False)

    def get_cache_info(self) -> dict:
        """Get information about the geoid data source."""
        grid_file = self._bundled_grid_dir() / 'us_nga_egm96_15.tif'
        bundled = grid_file.exists()
        return {
            'model': 'EGM96',
            'resolution_arcmin': 15,
            'source': 'pyproj/PROJ (us_nga_egm96_15)',
            'bundled': bundled,
            'available': bool(self._available) if self._available is not None else self.is_available(),
            'cache_path': str(grid_file),
            'cache_size_mb': grid_file.stat().st_size / (1024 * 1024) if bundled else 0,
        }
