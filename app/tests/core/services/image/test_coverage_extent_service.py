"""
Comprehensive tests for CoverageExtentService.

Tests coverage extent calculation and polygon generation.
"""

import pytest
from unittest.mock import patch, MagicMock

# Try to import CoverageExtentService, skip tests if shapely is not available
try:
    from core.services.image.CoverageExtentService import CoverageExtentService
    _SHAPELY_AVAILABLE = True
except ImportError as e:
    _SHAPELY_AVAILABLE = False
    _SHAPELY_IMPORT_ERROR = str(e)


@pytest.fixture
def coverage_extent_service():
    """Fixture providing a CoverageExtentService instance."""
    if not _SHAPELY_AVAILABLE:
        pytest.skip(f"Shapely not available: {_SHAPELY_IMPORT_ERROR}")
    return CoverageExtentService()


@pytest.fixture
def sample_images():
    """Sample image data with GPS coordinates."""
    return [
        {
            'path': 'test1.jpg',
            'lat': 37.7749,
            'lon': -122.4194,
            'width': 4000,
            'height': 3000,
            'altitude': 100.0,
            'gimbal_pitch': -90.0,
            'gimbal_yaw': 0.0
        },
        {
            'path': 'test2.jpg',
            'lat': 37.7750,
            'lon': -122.4195,
            'width': 4000,
            'height': 3000,
            'altitude': 100.0,
            'gimbal_pitch': -90.0,
            'gimbal_yaw': 0.0
        }
    ]


def test_coverage_extent_service_initialization(coverage_extent_service):
    """Test CoverageExtentService initialization."""
    if not _SHAPELY_AVAILABLE:
        pytest.skip(f"Shapely not available: {_SHAPELY_IMPORT_ERROR}")
    assert coverage_extent_service is not None


def test_calculate_coverage_extent(coverage_extent_service, sample_images):
    """Test calculating coverage extent from images."""
    if not _SHAPELY_AVAILABLE:
        pytest.skip(f"Shapely not available: {_SHAPELY_IMPORT_ERROR}")
    result = coverage_extent_service.calculate_coverage_extents(sample_images)

    assert result is not None
    assert 'polygons' in result
    assert 'image_count' in result
    assert 'total_area_sqm' in result
    assert isinstance(result['polygons'], list)
    assert isinstance(result['image_count'], int)
    assert isinstance(result['total_area_sqm'], (int, float))
