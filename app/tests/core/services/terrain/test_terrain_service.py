"""Tests for TerrainService."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
from PIL import Image
import io

from core.services.terrain.TerrainService import TerrainService as _TerrainService, ElevationResult
from core.services.terrain.TerrainProviderFactory import PROVIDER_TERRARIUM
from core.services.terrain.TerrainCacheService import TerrainCacheService
from core.services.terrain.GeoidService import GeoidService


def TerrainService(**kwargs):
    """Construct a TerrainService pinned to the Terrarium provider.

    Without an explicit provider_id, TerrainService reads TerrainProviderId
    from the machine's real settings, so a developer who has configured the
    3DEP local provider would silently flip these tests onto a different
    backend. Pinning keeps them hermetic.
    """
    kwargs.setdefault('provider_id', PROVIDER_TERRARIUM)
    return _TerrainService(**kwargs)


class TestElevationResult:
    """Tests for ElevationResult dataclass."""

    def test_creation(self):
        """Test ElevationResult creation."""
        result = ElevationResult(
            elevation_m=100.5,
            source='terrain',
            geoid_undulation_m=-30.5,
            provider='Test Provider',
            zoom_level=12,
            resolution_m=38,
            from_cache=True
        )

        assert result.elevation_m == 100.5
        assert result.source == 'terrain'
        assert result.from_cache is True

    def test_to_dict(self):
        """Test dictionary conversion."""
        result = ElevationResult(
            elevation_m=100.5,
            source='terrain',
            geoid_undulation_m=-30.5,
            provider='Test Provider',
            zoom_level=12,
            resolution_m=38,
            from_cache=True
        )

        d = result.to_dict()
        assert d['elevation_m'] == 100.5
        assert d['source'] == 'terrain'
        assert 'geoid_undulation_m' in d


class TestTerrainService:
    """Tests for TerrainService class."""

    def create_test_tile(self, elevation=100):
        """Create a test tile with uniform elevation."""
        # Encode elevation in Terrarium format
        # elevation = (R * 256 + G + B / 256) - 32768
        value = elevation + 32768
        r = int(value // 256)
        g = int(value % 256)
        b = 0

        img = Image.new('RGB', (256, 256), (r, g, b))
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()

    def test_initialization(self):
        """Test service initializes correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = TerrainService(cache_dir=tmpdir, enable_geoid=False)

            assert service.enabled is True
            assert service.zoom == 12
            assert service.cache is not None

    def test_enable_disable(self):
        """Test enabling/disabling terrain lookup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = TerrainService(cache_dir=tmpdir, enable_geoid=False)

            assert service.enabled is True
            service.enabled = False
            assert service.enabled is False

    def test_get_elevation_disabled(self):
        """Test that disabled service returns flat result."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = TerrainService(cache_dir=tmpdir, enable_geoid=False)
            service.enabled = False

            result = service.get_elevation(40.7128, -74.0060)

            assert result.source == 'flat'
            assert result.elevation_m is None

    def test_get_elevation_invalid_coords(self):
        """Test handling of invalid coordinates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = TerrainService(cache_dir=tmpdir, enable_geoid=False)

            result = service.get_elevation(100, 0)  # Invalid latitude
            assert result.source == 'error'

    @patch.object(TerrainCacheService, 'get_tile')
    def test_get_elevation_from_cache(self, mock_get_tile):
        """Test elevation retrieval from cached tile."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = TerrainService(cache_dir=tmpdir, enable_geoid=False)

            # Create a tile with known elevation (100m)
            tile_data = self.create_test_tile(100)
            mock_get_tile.return_value = Image.open(io.BytesIO(tile_data))

            result = service.get_elevation(40.7128, -74.0060)

            assert result.source == 'terrain'
            assert 95 < result.elevation_m < 105  # Allow some tolerance

    @patch.object(TerrainCacheService, 'get_tile')
    def test_get_elevation_no_tile(self, mock_get_tile):
        """Test fallback when no tile available."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = TerrainService(cache_dir=tmpdir, enable_geoid=False)

            mock_get_tile.return_value = None

            result = service.get_elevation(40.7128, -74.0060)

            assert result.source == 'flat'
            assert result.elevation_m is None

    @patch.object(TerrainCacheService, 'get_tile_if_cached')
    def test_get_elevation_offline_only(self, mock_get_tile):
        """Test offline-only mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = TerrainService(cache_dir=tmpdir, enable_geoid=False)

            mock_get_tile.return_value = None

            result = service.get_elevation(40.7128, -74.0060, offline_only=True)

            assert result.source == 'flat'
            mock_get_tile.assert_called_once()

    @patch.object(TerrainCacheService, 'get_tile_if_cached')
    @patch.object(TerrainCacheService, 'get_tile')
    def test_offline_only_floor_blocks_download(self, mock_get_tile, mock_get_cached):
        """service.offline_only=True (from app Offline Only mode) must prevent
        any network download even when get_elevation is called with no flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = TerrainService(cache_dir=tmpdir, enable_geoid=False)
            service.offline_only = True
            mock_get_cached.return_value = None

            result = service.get_elevation(40.7128, -74.0060)

            # Only the cache-only path is consulted; the downloading path is not.
            mock_get_cached.assert_called_once()
            mock_get_tile.assert_not_called()
            assert result.source == 'flat'

    @patch.object(TerrainCacheService, 'get_tile_if_cached')
    @patch.object(TerrainCacheService, 'get_tile')
    def test_offline_floor_off_allows_download(self, mock_get_tile, mock_get_cached):
        """With the floor off, the normal (downloading) cache path is used."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = TerrainService(cache_dir=tmpdir, enable_geoid=False)
            assert service.offline_only is False  # default
            mock_get_tile.return_value = None

            service.get_elevation(40.7128, -74.0060)

            mock_get_tile.assert_called_once()
            mock_get_cached.assert_not_called()

    @patch.object(TerrainCacheService, 'get_tile')
    def test_get_elevation_batch(self, mock_get_tile):
        """Test batch elevation retrieval."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = TerrainService(cache_dir=tmpdir, enable_geoid=False)

            tile_data = self.create_test_tile(100)
            mock_get_tile.return_value = Image.open(io.BytesIO(tile_data))

            locations = [
                (40.7128, -74.0060),
                (34.0522, -118.2437),
                (51.5074, -0.1278)
            ]

            results = service.get_elevation_batch(locations)

            assert len(results) == 3
            for result in results:
                assert result.source == 'terrain'

    @patch.object(TerrainCacheService, 'get_tile')
    def test_get_effective_altitude_agl_with_terrain(self, mock_get_tile):
        """Test effective AGL calculation with terrain data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = TerrainService(cache_dir=tmpdir, enable_geoid=False)

            # Drone terrain = 50m, target terrain = 100m
            # If drone reports 120m AGL from takeoff:
            # Drone absolute = 50 + 120 = 170m
            # Effective AGL at target = 170 - 100 = 70m

            # We need to return different elevations for different coords
            def tile_for_coords(z, x, y):
                # Simple mock - we'll control via position
                return Image.open(io.BytesIO(self.create_test_tile(50)))

            mock_get_tile.side_effect = tile_for_coords

            effective_agl, source = service.get_effective_altitude_agl(
                drone_lat=40.71,
                drone_lon=-74.00,
                takeoff_elevation_m=50,
                relative_altitude_m=120,
                target_lat=40.72,
                target_lon=-74.01
            )

            # Since we're mocking same elevation everywhere, result should be 120m
            assert source == 'terrain'
            assert effective_agl > 0

    @patch.object(TerrainCacheService, 'get_tile')
    def test_get_effective_altitude_agl_no_terrain(self, mock_get_tile):
        """Test effective AGL fallback when no terrain."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = TerrainService(cache_dir=tmpdir, enable_geoid=False)

            mock_get_tile.return_value = None

            effective_agl, source = service.get_effective_altitude_agl(
                drone_lat=40.71,
                drone_lon=-74.00,
                takeoff_elevation_m=None,
                relative_altitude_m=120,
                target_lat=40.72,
                target_lon=-74.01
            )

            assert source == 'flat'
            assert effective_agl == 120  # Returns original AGL

    def test_is_terrain_available_not_cached(self):
        """Test terrain availability check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = TerrainService(cache_dir=tmpdir, enable_geoid=False)

            # No tiles cached
            assert not service.is_terrain_available(40.7128, -74.0060)

    @patch.object(TerrainCacheService, 'prefetch_tiles')
    def test_prefetch_area(self, mock_prefetch):
        """Test prefetch delegates to cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = TerrainService(cache_dir=tmpdir, enable_geoid=False)

            mock_prefetch.return_value = 10

            count = service.prefetch_area(40.7128, -74.0060, radius_km=5)

            assert count == 10
            mock_prefetch.assert_called_once()

    def test_get_service_info(self):
        """Test service info retrieval."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = TerrainService(cache_dir=tmpdir, enable_geoid=False)

            info = service.get_service_info()

            assert 'enabled' in info
            assert 'zoom_level' in info
            assert 'provider' in info
            assert 'cache' in info

    @patch.object(TerrainCacheService, 'clear_cache')
    def test_clear_cache(self, mock_clear):
        """Test cache clearing delegates to cache service."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = TerrainService(cache_dir=tmpdir, enable_geoid=False)

            mock_clear.return_value = 50

            count = service.clear_cache()

            assert count == 50
            mock_clear.assert_called_once()

    def test_set_zoom_level(self):
        """Test zoom level setting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = TerrainService(cache_dir=tmpdir, enable_geoid=False)

            service.set_zoom_level(10)
            assert service.zoom == 10

            service.set_zoom_level(14)
            assert service.zoom == 14

            # Invalid zoom should use default
            service.set_zoom_level(20)
            assert service.zoom == 12


class TestTerrainServiceWithGeoid:
    """Tests for TerrainService with geoid enabled."""

    def test_geoid_conversion(self):
        """Test geoid height conversions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = TerrainService(cache_dir=tmpdir, enable_geoid=True)

            # Skip if geoid didn't load
            if service._geoid is None:
                pytest.skip("Geoid service not available")

            lat, lon = 40.7128, -74.0060
            h_ellip = 100.0

            h_ortho = service.convert_ellipsoidal_to_orthometric(lat, lon, h_ellip)
            assert h_ortho is not None

            h_back = service.convert_orthometric_to_ellipsoidal(lat, lon, h_ortho)
            assert abs(h_back - h_ellip) < 0.001

    def test_get_geoid_undulation(self):
        """Test geoid undulation retrieval."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = TerrainService(cache_dir=tmpdir, enable_geoid=True)

            if service._geoid is None:
                pytest.skip("Geoid service not available")

            N = service.get_geoid_undulation(40.7128, -74.0060)
            assert N is not None
            assert isinstance(N, float)


# ---------------------------------------------------------------------------
# Local-provider fallback to AWS Terrain Tiles (Terrarium)
# ---------------------------------------------------------------------------

def _local_provider_service(tmp_path):
    """TerrainService whose primary provider mocks a local-GeoTIFF backend."""
    svc = TerrainService(cache_dir=str(tmp_path), enable_geoid=False)
    local = MagicMock()
    local.get_provider_kind.return_value = 'local_geotiff'
    local.get_provider_name.return_value = 'USGS 3DEP 1m (Local GeoTIFF)'
    local.get_datum_info.return_value = {'resolution_m': 1}
    svc.provider = local
    svc.cache = None
    return svc, local


def _inject_fallback(svc, elevation=42.0, tile=None):
    """Pre-seed the lazy fallback pair with mocks (skips real construction)."""
    provider = MagicMock()
    provider.get_provider_name.return_value = 'AWS Terrain Tiles'
    provider.lat_lon_to_tile.return_value = (1, 2)
    provider.lat_lon_to_pixel_in_tile.return_value = (0.5, 0.5)
    provider.decode_elevation_bilinear.return_value = elevation
    cache = MagicMock()
    cache.get_tile.return_value = tile if tile is not None else Image.new('RGB', (256, 256))
    cache.get_tile_if_cached.return_value = tile
    cache.is_tile_cached.return_value = False
    svc._fallback_provider = provider
    svc._fallback_cache = cache
    return provider, cache


def test_grid_fallback_when_local_has_no_coverage(tmp_path):
    """Local DEM misses the grid -> the Terrarium fallback serves it, tagged."""
    svc, local = _local_provider_service(tmp_path)
    local.sample_grid_spec.return_value = None
    _inject_fallback(svc)
    sentinel = MagicMock()
    sentinel.source = None
    spec = MagicMock(width=4, height=4, cell_size=3.0)

    with patch('core.services.terrain.TerrariumGridSampler.sample_grid_tiled',
               return_value=sentinel) as mock_tiled:
        sample = svc.sample_grid_spec(spec)

    assert sample is sentinel
    assert sample.source == 'terrarium_fallback'
    mock_tiled.assert_called_once()


def test_grid_no_fallback_when_local_covers(tmp_path):
    """Local coverage is authoritative; the fallback must not run."""
    svc, local = _local_provider_service(tmp_path)
    covered = MagicMock()
    local.sample_grid_spec.return_value = covered

    with patch('core.services.terrain.TerrariumGridSampler.sample_grid_tiled') as mock_tiled:
        sample = svc.sample_grid_spec(MagicMock())

    assert sample is covered
    mock_tiled.assert_not_called()


def test_grid_returns_none_when_fallback_also_empty(tmp_path):
    svc, local = _local_provider_service(tmp_path)
    local.sample_grid_spec.return_value = None
    _inject_fallback(svc)
    spec = MagicMock(width=4, height=4, cell_size=3.0)
    with patch('core.services.terrain.TerrariumGridSampler.sample_grid_tiled',
               return_value=None):
        assert svc.sample_grid_spec(spec) is None


def test_point_fallback_when_local_returns_none(tmp_path):
    """Point lookups outside the local tiles degrade to the online baseline."""
    svc, local = _local_provider_service(tmp_path)
    local.sample_elevation.return_value = None
    _inject_fallback(svc, elevation=123.0)

    result = svc.get_elevation(38.7, -120.5)

    assert result.source == 'terrain'
    assert result.elevation_m == 123.0
    assert 'fallback' in result.provider


def test_point_fallback_offline_uses_cache_only(tmp_path):
    """Offline mode must not download fallback tiles - cached only."""
    svc, local = _local_provider_service(tmp_path)
    local.sample_elevation.return_value = None
    provider, cache = _inject_fallback(svc)
    cache.get_tile_if_cached.return_value = None   # nothing cached

    result = svc.get_elevation(38.7, -120.5, offline_only=True)

    cache.get_tile.assert_not_called()
    assert result.source == 'flat'   # no data at all -> flat, but never a download


def test_point_no_fallback_when_local_covers(tmp_path):
    svc, local = _local_provider_service(tmp_path)
    local.sample_elevation.return_value = 99.0

    result = svc.get_elevation(38.7, -120.5)

    assert result.elevation_m == 99.0
    assert result.provider == 'USGS 3DEP 1m (Local GeoTIFF)'


def test_no_fallback_pair_for_tiled_web_provider(tmp_path):
    """Terrarium primaries never build a fallback (they ARE the baseline)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        svc = TerrainService(cache_dir=tmpdir, enable_geoid=False)
        assert svc._get_fallback() == (None, None)


def test_set_provider_resets_fallback(tmp_path):
    svc, local = _local_provider_service(tmp_path)
    _inject_fallback(svc)
    assert svc._fallback_provider is not None
    svc.set_provider(PROVIDER_TERRARIUM)
    assert svc._fallback_provider is None
    assert svc._fallback_cache is None


def test_offline_only_initialized_from_settings(tmp_path):
    """The app-wide OfflineOnly preference is honored without callers having
    to remember to set service.offline_only themselves."""
    settings = MagicMock()
    settings.get_setting.return_value = PROVIDER_TERRARIUM
    settings.get_bool_setting.return_value = True

    svc = _TerrainService(cache_dir=str(tmp_path), enable_geoid=False,
                          provider_id=PROVIDER_TERRARIUM, settings_service=settings)

    assert svc.offline_only is True


# ---------------------------------------------------------------------------
# Factory: dangling 3DEP registration falls back to the online baseline
# ---------------------------------------------------------------------------

def test_factory_falls_back_when_3dep_files_missing(tmp_path):
    """Registered 3DEP paths that no longer exist on disk (moved/deleted
    results folder) must fall back to Terrarium with a warning instead of
    building a provider that ERROR-logs on first use."""
    from core.services.terrain.TerrainProviderFactory import TerrainProviderFactory
    from core.services.terrain.ElevationProvider import TerrariumProvider

    settings = MagicMock()
    settings.get_setting.side_effect = lambda k, d='': {
        'Terrain3DEPManifestPath': str(tmp_path / "gone" / "dem_manifest.csv"),
        'Terrain3DEPTilesDir': str(tmp_path / "gone"),
    }.get(k, d)

    provider = TerrainProviderFactory.create('usgs_3dep_local', settings)
    assert isinstance(provider, TerrariumProvider)


def test_factory_builds_3dep_when_files_exist(tmp_path):
    from core.services.terrain.TerrainProviderFactory import TerrainProviderFactory

    manifest = tmp_path / "dem_manifest.csv"
    manifest.write_text("filename,minX,minY,maxX,maxY\n")
    settings = MagicMock()
    settings.get_setting.side_effect = lambda k, d='': {
        'Terrain3DEPManifestPath': str(manifest),
        'Terrain3DEPTilesDir': str(tmp_path),
    }.get(k, d)

    provider = TerrainProviderFactory.create('usgs_3dep_local', settings)
    assert provider.get_provider_kind() == 'local_geotiff'
