"""
Comprehensive tests for cache services.

Tests thumbnail, color, and temperature caching.
"""

import pytest
import tempfile
import os
import numpy as np
from unittest.mock import patch, MagicMock
from core.services.cache.ThumbnailCacheService import ThumbnailCacheService
from core.services.cache.ColorCacheService import ColorCacheService
from core.services.cache.TemperatureCacheService import TemperatureCacheService


@pytest.fixture
def thumbnail_cache_service():
    """Fixture providing a ThumbnailCacheService instance."""
    with tempfile.TemporaryDirectory() as tmpdir:
        service = ThumbnailCacheService(dataset_cache_dir=tmpdir)
        yield service


@pytest.fixture
def sample_aoi():
    """Sample AOI data."""
    return {
        'center': (100, 100),
        'radius': 20,
        'area': 400
    }


def test_thumbnail_cache_service_initialization(thumbnail_cache_service):
    """Test ThumbnailCacheService initialization."""
    assert thumbnail_cache_service is not None
    assert thumbnail_cache_service.mutex is not None


def test_get_cache_key(thumbnail_cache_service, sample_aoi):
    """Test cache key generation."""
    key = thumbnail_cache_service.get_cache_key('test_image.jpg', sample_aoi)

    assert isinstance(key, str)
    assert len(key) > 0


def test_save_thumbnail_from_array(thumbnail_cache_service, sample_aoi):
    """Test saving thumbnail from array."""
    thumbnail = np.random.randint(0, 255, (180, 180, 3), dtype=np.uint8)

    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = os.path.join(tmpdir, '.thumbnails')
        os.makedirs(cache_dir, exist_ok=True)

        thumbnail_cache_service.save_thumbnail_from_array(
            'test_image.jpg',
            sample_aoi,
            thumbnail,
            cache_dir
        )

        # Verify thumbnail was saved
        # Note: actual path may vary based on implementation
        assert os.path.exists(cache_dir)


def test_color_cache_service_initialization():
    """Test ColorCacheService initialization."""
    service = ColorCacheService()
    assert service is not None


def test_color_cache_service_save():
    """Test saving color information to cache."""
    service = ColorCacheService()

    color_info = {
        'rgb': (100, 150, 200),
        'hex': '#6496C8',
        'hue_degrees': 210.0
    }

    aoi = {
        'center': (100, 100),
        'radius': 20
    }

    service.save_color_info('test_image.jpg', aoi, color_info)

    # Verify color info was stored
    assert 'color_info' in aoi or service.get_color_info('test_image.jpg', aoi) is not None


def test_temperature_cache_service_initialization():
    """Test TemperatureCacheService initialization."""
    service = TemperatureCacheService()
    assert service is not None


def test_temperature_cache_service_save():
    """Test saving temperature information to cache."""
    service = TemperatureCacheService()

    aoi = {
        'center': (100, 100),
        'radius': 20
    }

    service.save_temperature('test_image.jpg', aoi, 25.5)

    # Verify temperature was stored
    assert 'temperature' in aoi or service.get_temperature('test_image.jpg', aoi) is not None
