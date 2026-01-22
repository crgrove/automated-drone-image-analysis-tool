"""Tests for ElevationProvider and TerrariumProvider."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import io
import struct

from core.services.terrain.ElevationProvider import TerrariumProvider, ElevationProvider


class TestTerrariumProvider:
    """Tests for TerrariumProvider class."""

    def test_initialization(self):
        """Test provider initializes correctly."""
        provider = TerrariumProvider()
        assert provider.timeout == 10.0
        assert provider.get_provider_name() == "AWS Terrain Tiles (Terrarium)"

    def test_get_tile_url(self):
        """Test tile URL generation."""
        provider = TerrariumProvider()
        url = provider.get_tile_url(12, 1234, 5678)
        assert "12/1234/5678.png" in url
        assert "elevation-tiles-prod" in url

    def test_get_datum_info(self):
        """Test datum information."""
        provider = TerrariumProvider()
        datum = provider.get_datum_info()
        assert datum['name'] == 'EGM96'
        assert datum['type'] == 'orthometric'
        assert 'resolution_m' in datum

    def test_decode_elevation_basic(self):
        """Test basic elevation decoding from Terrarium format."""
        provider = TerrariumProvider()

        # Create a simple 2x2 RGB image
        img = Image.new('RGB', (2, 2))

        # Test sea level (elevation = 0)
        # Formula: elevation = (R * 256 + G + B / 256) - 32768
        # For elevation 0: R * 256 + G + B/256 = 32768
        # R = 128, G = 0, B = 0 gives 32768
        img.putpixel((0, 0), (128, 0, 0))
        elevation = provider.decode_elevation(img, 0, 0)
        assert abs(elevation - 0) < 0.01

        # Test positive elevation (e.g., 100m)
        # elevation = 100 means R * 256 + G + B/256 = 32868
        # R = 128, G = 100, B = 0
        img.putpixel((1, 0), (128, 100, 0))
        elevation = provider.decode_elevation(img, 1, 0)
        assert abs(elevation - 100) < 0.01

        # Test negative elevation (e.g., -50m below sea level)
        # elevation = -50 means R * 256 + G + B/256 = 32718
        # R = 127, G = 206, B = 0
        img.putpixel((0, 1), (127, 206, 0))
        elevation = provider.decode_elevation(img, 0, 1)
        assert abs(elevation - (-50)) < 1  # Allow some tolerance

    def test_decode_elevation_bilinear(self):
        """Test bilinear interpolation of elevation."""
        provider = TerrariumProvider()

        # Create 2x2 image with different elevations at corners
        img = Image.new('RGB', (2, 2))

        # Set up corners with known elevations
        # Corner (0,0) = 0m
        img.putpixel((0, 0), (128, 0, 0))
        # Corner (1,0) = 100m
        img.putpixel((1, 0), (128, 100, 0))
        # Corner (0,1) = 200m
        img.putpixel((0, 1), (128, 200, 0))
        # Corner (1,1) = 300m
        img.putpixel((1, 1), (129, 44, 0))

        # Center should be interpolated average
        center_elevation = provider.decode_elevation_bilinear(img, 0.5, 0.5)
        # Expected average: (0 + 100 + 200 + 300) / 4 = 150
        assert 100 < center_elevation < 200  # Allow tolerance

    def test_lat_lon_to_tile(self):
        """Test coordinate to tile conversion."""
        # Known test cases
        # Equator, prime meridian at zoom 0 should be (0, 0)
        x, y = TerrariumProvider.lat_lon_to_tile(0, 0, 0)
        assert x == 0
        assert y == 0

        # At zoom 1, there are 2x2 tiles
        x, y = TerrariumProvider.lat_lon_to_tile(0, 0, 1)
        assert x == 1  # Just to the right of center
        assert y == 1  # Just below center

        # High zoom should give larger tile numbers
        x, y = TerrariumProvider.lat_lon_to_tile(40.7128, -74.0060, 12)  # NYC
        assert 0 <= x < 4096
        assert 0 <= y < 4096

    def test_lat_lon_to_pixel_in_tile(self):
        """Test coordinate to pixel conversion."""
        # Center of tile should give center pixel
        px, py = TerrariumProvider.lat_lon_to_pixel_in_tile(0, 0, 0, 256)
        # At zoom 0, the center of the single tile is around (128, 128)
        assert 120 < px < 136
        assert 120 < py < 136

    @patch('core.services.terrain.ElevationProvider.requests.Session')
    def test_download_tile_success(self, mock_session_class):
        """Test successful tile download."""
        provider = TerrariumProvider()

        # Create a minimal valid PNG
        img = Image.new('RGB', (256, 256), (128, 0, 0))
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        png_data = buffer.getvalue()

        # Mock the session and response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = png_data

        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        # Force session creation
        provider._session = mock_session

        result = provider.download_tile(12, 100, 100)
        assert result == png_data

    @patch('core.services.terrain.ElevationProvider.requests.Session')
    def test_download_tile_404(self, mock_session_class):
        """Test tile not found (ocean areas)."""
        provider = TerrariumProvider()

        mock_response = Mock()
        mock_response.status_code = 404

        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        provider._session = mock_session

        result = provider.download_tile(12, 100, 100)
        assert result is None

    def test_close_session(self):
        """Test session cleanup."""
        provider = TerrariumProvider()

        # Create a mock session
        mock_session = Mock()
        provider._session = mock_session

        provider.close()

        mock_session.close.assert_called_once()
        assert provider._session is None


class TestElevationProviderAbstract:
    """Test that ElevationProvider is properly abstract."""

    def test_cannot_instantiate_abstract(self):
        """Test that ElevationProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ElevationProvider()
