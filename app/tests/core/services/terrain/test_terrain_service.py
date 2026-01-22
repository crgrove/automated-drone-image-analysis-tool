"""Tests for TerrainService."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
from PIL import Image
import io

from core.services.terrain.TerrainService import TerrainService, ElevationResult
from core.services.terrain.TerrainCacheService import TerrainCacheService
from core.services.terrain.GeoidService import GeoidService


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
