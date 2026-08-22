"""Tests for GeoidService (EGM96 via pyproj/PROJ, bundled global grid)."""

import pytest
from pathlib import Path
import tempfile
from unittest.mock import patch

from core.services.terrain.GeoidService import GeoidService


# Authoritative EGM96 undulations (m), reproduced from pyproj EPSG:4979 -> EPSG:4326+5773.
# Tolerance covers 15' grid interpolation; the point is to be within a couple of
# metres of truth and, above all, NOT the old ~-1.55 m synthetic-fallback value.
REFERENCE_UNDULATIONS = [
    (30.654, -97.952, -26.56),   # central Texas (the bug's dataset)
    (51.5074, -0.1278, 45.97),   # London
    (-33.8688, 151.2093, 22.42),  # Sydney
    (35.6762, 139.6503, 36.92),  # Tokyo
    (-5.0, 80.0, -92.93),        # Indian Ocean low
]


class TestGeoidService:
    """Tests for GeoidService class."""

    def test_initialization(self):
        """Test service initializes correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = GeoidService(cache_dir=tmpdir)
            assert service.cache_dir == Path(tmpdir)
            assert service._transformer is None
            assert service._available is None

    def test_reference_values_are_authoritative_egm96(self):
        """Undulation must match authoritative EGM96 worldwide (regression guard
        against the -1.55 m synthetic-fallback bug that shortened AOI throws)."""
        service = GeoidService()
        for lat, lon, expected in REFERENCE_UNDULATIONS:
            N = service.get_undulation(lat, lon)
            assert N is not None, f"no undulation at ({lat}, {lon})"
            assert abs(N - expected) < 2.0, (
                f"undulation at ({lat}, {lon}) = {N:.2f} m, expected ~{expected} m"
            )

    def test_central_texas_is_not_synthetic_fallback(self):
        """The specific regression: central TX must be ~-26.5 m, never the
        synthetic model's ~-1.55 m."""
        service = GeoidService()
        N = service.get_undulation(30.654, -97.952)
        assert N is not None
        assert N < -20.0, f"central TX N={N} looks like the synthetic fallback"

    def test_get_undulation_returns_float(self):
        service = GeoidService()
        N = service.get_undulation(40.7128, -74.0060)
        assert isinstance(N, float)

    def test_longitude_normalization(self):
        """-90 and 270 denote the same meridian and must agree."""
        service = GeoidService()
        n1 = service.get_undulation(0, -90)
        n2 = service.get_undulation(0, 270)
        assert n1 is not None and n2 is not None
        assert abs(n1 - n2) < 0.01

    def test_invalid_latitude_returns_none(self):
        service = GeoidService()
        assert service.get_undulation(100, 0) is None
        assert service.get_undulation(-100, 0) is None

    def test_unavailable_grid_returns_none_not_zero(self):
        """When no real grid is reachable the probe fails; get_undulation must
        return None (never the PROJ null-transform's bogus 0 m)."""
        service = GeoidService()
        # Simulate a genuinely-absent grid: the identity probe fails.
        with patch.object(service, '_probe', return_value=False):
            assert service.get_undulation(30.654, -97.952) is None
            assert service.get_undulation(30.654, -97.952, offline_only=True) is None
            assert service.is_available() is False

    def test_offline_only_does_not_enable_network(self):
        """offline_only must never toggle PROJ network on; the bundled grid
        answers locally (freeze-safe on the GUI hot path)."""
        service = GeoidService()
        with patch('core.services.terrain.GeoidService.pyproj.network.set_network_enabled') as mock_net:
            N = service.get_undulation(30.654, -97.952, offline_only=True)
        assert N is not None
        assert abs(N + 26.56) < 2.0
        mock_net.assert_not_called()

    def test_ellipsoidal_to_orthometric(self):
        service = GeoidService()
        # central TX N ~ -26.5, so orthometric = ellipsoidal - N ~ ellipsoidal + 26.5
        h_ortho = service.ellipsoidal_to_orthometric(30.654, -97.952, 100.0)
        assert h_ortho is not None
        assert abs(h_ortho - (100.0 + 26.56)) < 2.0

    def test_orthometric_to_ellipsoidal(self):
        service = GeoidService()
        h_ellip = service.orthometric_to_ellipsoidal(30.654, -97.952, 100.0)
        assert h_ellip is not None
        assert abs(h_ellip - (100.0 - 26.56)) < 2.0

    def test_round_trip_conversion(self):
        service = GeoidService()
        original = 50.0
        h_ortho = service.ellipsoidal_to_orthometric(35.6762, 139.6503, original)
        h_ellip = service.orthometric_to_ellipsoidal(35.6762, 139.6503, h_ortho)
        assert abs(h_ellip - original) < 0.001

    def test_is_available(self):
        service = GeoidService()
        assert service.is_available() is True

    def test_get_cache_info(self):
        service = GeoidService()
        info = service.get_cache_info()
        assert info['model'] == 'EGM96'
        assert info['resolution_arcmin'] == 15
        assert info['bundled'] is True
        assert info['available'] is True
        assert 'cache_path' in info
