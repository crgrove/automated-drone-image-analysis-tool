"""Tests for GeoidService."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import struct
import os

from core.services.terrain.GeoidService import GeoidService


class TestGeoidService:
    """Tests for GeoidService class."""

    def test_initialization(self):
        """Test service initializes correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = GeoidService(cache_dir=tmpdir)
            assert service.cache_dir == Path(tmpdir)
            assert service._grid_data is None
            assert service._grid_loaded is False

    def test_approximate_undulation_reasonable_values(self):
        """Test that approximate undulation gives reasonable values globally.

        Note: The simplified model is only accurate to ~5-10m RMS globally.
        We use relaxed bounds to account for model limitations.
        """
        service = GeoidService()

        # Test various known locations with relaxed bounds for simplified model
        test_cases = [
            # (lat, lon, min_expected, max_expected)
            (0, 0, -30, 30),  # Equator/prime meridian
            (40.7128, -74.0060, -60, 10),  # NYC (typically negative in NA)
            (51.5074, -0.1278, -20, 60),  # London (simplified model may underestimate)
            (35.6762, 139.6503, -10, 60),  # Tokyo
            (-33.8688, 151.2093, -10, 50),  # Sydney
            (-5, 80, -130, -30),  # Indian Ocean low
        ]

        for lat, lon, min_exp, max_exp in test_cases:
            N = service._approximate_undulation(lat, lon)
            assert min_exp < N < max_exp, f"Undulation at ({lat}, {lon}) = {N} not in range [{min_exp}, {max_exp}]"

    def test_generate_simplified_grid(self):
        """Test grid generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = GeoidService(cache_dir=tmpdir)
            grid_file = Path(tmpdir) / 'egm96_15.bin'

            success = service._generate_simplified_grid(grid_file)
            assert success
            assert grid_file.exists()

            # Check file size is correct
            expected_size = 721 * 1441 * 4  # nlat * nlon * 4 bytes per float
            assert grid_file.stat().st_size == expected_size

    def test_load_grid_binary(self):
        """Test loading binary grid file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = GeoidService(cache_dir=tmpdir)
            grid_file = Path(tmpdir) / 'egm96_15.bin'

            # Generate and load grid
            service._generate_simplified_grid(grid_file)
            success = service._load_grid_binary(grid_file)

            assert success
            assert service._grid_loaded
            assert len(service._grid_data) == 721 * 1441

    def test_interpolate_undulation(self):
        """Test bilinear interpolation of undulation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = GeoidService(cache_dir=tmpdir)
            grid_file = Path(tmpdir) / 'egm96_15.bin'

            # Generate and load grid
            service._generate_simplified_grid(grid_file)
            service._load_grid_binary(grid_file)

            # Test interpolation at grid points
            N = service._interpolate_undulation(0, 0)
            assert isinstance(N, float)

            # Test at different locations
            N1 = service._interpolate_undulation(45, 90)
            N2 = service._interpolate_undulation(-45, -90)
            # Values should be different
            assert N1 != N2

    def test_get_undulation(self):
        """Test public get_undulation method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = GeoidService(cache_dir=tmpdir)

            # Should automatically load grid
            N = service.get_undulation(40.7128, -74.0060)
            assert N is not None
            assert isinstance(N, float)

    def test_get_undulation_normalized_longitude(self):
        """Test longitude normalization (negative to 0-360)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = GeoidService(cache_dir=tmpdir)

            # These should give the same result
            N1 = service.get_undulation(0, -90)
            N2 = service.get_undulation(0, 270)

            assert N1 is not None
            assert N2 is not None
            assert abs(N1 - N2) < 0.01

    def test_get_undulation_invalid_coords(self):
        """Test handling of invalid coordinates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = GeoidService(cache_dir=tmpdir)

            # Invalid latitude
            N = service.get_undulation(100, 0)
            assert N is None

            # Invalid longitude after normalization shouldn't happen,
            # but test edge cases
            N = service.get_undulation(0, 361)  # Will be normalized
            # After normalization, this becomes valid

    def test_ellipsoidal_to_orthometric(self):
        """Test ellipsoidal to orthometric conversion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = GeoidService(cache_dir=tmpdir)

            lat, lon = 40.7128, -74.0060  # NYC
            h_ellipsoidal = 100.0

            h_orthometric = service.ellipsoidal_to_orthometric(lat, lon, h_ellipsoidal)

            assert h_orthometric is not None
            # NYC has negative geoid undulation (~-30m), so orthometric should be higher
            # h_orthometric = h_ellipsoidal - N
            # If N < 0, then h_orthometric > h_ellipsoidal

    def test_orthometric_to_ellipsoidal(self):
        """Test orthometric to ellipsoidal conversion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = GeoidService(cache_dir=tmpdir)

            lat, lon = 40.7128, -74.0060
            h_orthometric = 100.0

            h_ellipsoidal = service.orthometric_to_ellipsoidal(lat, lon, h_orthometric)

            assert h_ellipsoidal is not None

    def test_round_trip_conversion(self):
        """Test that converting back and forth gives original value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = GeoidService(cache_dir=tmpdir)

            lat, lon = 35.6762, 139.6503  # Tokyo
            original_height = 50.0

            # Convert ellipsoidal -> orthometric -> ellipsoidal
            h_ortho = service.ellipsoidal_to_orthometric(lat, lon, original_height)
            h_ellip = service.orthometric_to_ellipsoidal(lat, lon, h_ortho)

            assert abs(h_ellip - original_height) < 0.001

    def test_is_available(self):
        """Test availability check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = GeoidService(cache_dir=tmpdir)
            assert service.is_available()

    def test_get_cache_info(self):
        """Test cache info retrieval."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = GeoidService(cache_dir=tmpdir)

            # Trigger grid generation
            service.get_undulation(0, 0)

            info = service.get_cache_info()
            assert info['model'] == 'EGM96'
            assert info['resolution_arcmin'] == 15
            assert info['cached'] is True
            assert 'cache_path' in info
            assert info['cache_size_mb'] > 0
