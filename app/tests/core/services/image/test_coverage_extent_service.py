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


# ---------------------------------------------------------------------------
# Terrain-aware FOV polygon behavior
# ---------------------------------------------------------------------------

_LAT = 38.685
_LON = -121.082
_EARTH_RADIUS = 6371000.0


class _FakeImageService:
    """Configurable stand-in for ImageService in the FOV polygon path."""

    def __init__(self, terrain_gsd_cm=None, terrain_agl_m=None, flat_gsd_cm=4.0,
                 roll_deg=0.0, reported_agl_m=100.0, yaw_deg=0.0):
        import math as _math
        self._math = _math
        self.terrain_gsd_cm = terrain_gsd_cm
        self.terrain_agl_m = terrain_agl_m
        self.flat_gsd_cm = flat_gsd_cm
        self.roll_deg = roll_deg
        self.reported_agl_m = reported_agl_m
        self.yaw_deg = yaw_deg
        self.img_array = MagicMock(shape=(3000, 4000))
        self.compute_calls = []
        self.average_calls = []

    def get_camera_pitch(self):
        return -90.0

    def get_gimbal_roll(self):
        return self.roll_deg

    def get_camera_yaw(self):
        return self.yaw_deg

    def get_relative_altitude(self, unit):
        assert unit == 'm'
        return self.reported_agl_m

    def compute_gsd_at_pixel(self, col, row, use_terrain=True, custom_altitude_ft=None):
        self.compute_calls.append({'col': col, 'row': row, 'use_terrain': use_terrain})
        return self.terrain_gsd_cm

    def get_effective_agl_at_pixel(self, col, row, use_terrain=True, custom_altitude_ft=None):
        return self.terrain_agl_m

    def get_average_gsd(self, custom_altitude_ft=None):
        self.average_calls.append(custom_altitude_ft)
        return self.flat_gsd_cm


def _fov_corners_with(service, fake_image_service):
    """Run get_image_fov_corners with EXIF/GPS/ImageService patched out."""
    image = {'path': 'fake.jpg', 'name': 'fake.jpg'}
    with patch('core.services.image.CoverageExtentService.MetaDataHelper') as mdh, \
            patch('core.services.image.CoverageExtentService.LocationInfo') as loc, \
            patch('core.services.image.CoverageExtentService.ImageService',
                  return_value=fake_image_service):
        mdh.get_exif_data_piexif.return_value = {}
        loc.get_gps.return_value = {'latitude': _LAT, 'longitude': _LON}
        return service.get_image_fov_corners(image)


def _centroid_east_m(corners):
    """Mean east-offset of the corners from the drone position, in meters."""
    import math
    lons = [lon for _lat, lon in corners]
    mean_dlon = sum(lons) / len(lons) - _LON
    return mean_dlon * _EARTH_RADIUS * math.cos(math.radians(_LAT)) * math.pi / 180.0


def _span_east_m(corners):
    """East-west extent of the corners in meters."""
    import math
    lons = [lon for _lat, lon in corners]
    return (max(lons) - min(lons)) * _EARTH_RADIUS * math.cos(math.radians(_LAT)) * math.pi / 180.0


def test_fov_polygon_uses_terrain_gsd_and_agl():
    """Terrain-corrected center GSD and effective AGL drive the footprint."""
    if not _SHAPELY_AVAILABLE:
        pytest.skip(f"Shapely not available: {_SHAPELY_IMPORT_ERROR}")
    import math
    fake = _FakeImageService(terrain_gsd_cm=2.0, terrain_agl_m=120.0,
                             flat_gsd_cm=4.0, roll_deg=22.5)
    service = CoverageExtentService(use_terrain=True)
    corners = _fov_corners_with(service, fake)

    assert corners is not None and len(corners) == 4
    # Terrain GSD was requested at the image center with use_terrain=True
    assert fake.compute_calls == [{'col': 2000.0, 'row': 1500.0, 'use_terrain': True}]
    # Flat average GSD was never consulted
    assert fake.average_calls == []
    # Footprint width reflects the terrain GSD (2 cm/px * 4000 px = 80 m)
    assert _span_east_m(corners) == pytest.approx(80.0, rel=0.01)
    # Roll offset uses the DEM-corrected effective AGL (120 m), not reported (100 m)
    expected_offset = -120.0 * math.tan(math.radians(22.5))
    assert _centroid_east_m(corners) == pytest.approx(expected_offset, rel=0.01)


def test_fov_polygon_use_terrain_false_uses_flat_gsd():
    """With use_terrain=False the terrain path is never touched."""
    if not _SHAPELY_AVAILABLE:
        pytest.skip(f"Shapely not available: {_SHAPELY_IMPORT_ERROR}")
    import math
    fake = _FakeImageService(terrain_gsd_cm=2.0, terrain_agl_m=120.0,
                             flat_gsd_cm=4.0, roll_deg=22.5)
    service = CoverageExtentService(use_terrain=False)
    corners = _fov_corners_with(service, fake)

    assert corners is not None and len(corners) == 4
    assert fake.compute_calls == []
    assert len(fake.average_calls) == 1
    # Footprint width reflects the flat GSD (4 cm/px * 4000 px = 160 m)
    assert _span_east_m(corners) == pytest.approx(160.0, rel=0.01)
    # Roll offset falls back to the reported AGL (100 m)
    expected_offset = -100.0 * math.tan(math.radians(22.5))
    assert _centroid_east_m(corners) == pytest.approx(expected_offset, rel=0.01)


def test_fov_polygon_records_camera_yaw():
    """The camera yaw used is exposed for the Align Image dialog to reuse."""
    if not _SHAPELY_AVAILABLE:
        pytest.skip(f"Shapely not available: {_SHAPELY_IMPORT_ERROR}")
    fake = _FakeImageService(flat_gsd_cm=4.0, yaw_deg=97.5)
    service = CoverageExtentService(use_terrain=False)
    assert service.last_camera_yaw is None  # nothing computed yet

    corners = _fov_corners_with(service, fake)

    assert corners is not None and len(corners) == 4
    assert service.last_camera_yaw == pytest.approx(97.5)


def test_fov_polygon_falls_back_to_flat_when_terrain_unavailable():
    """Terrain enabled but no DEM coverage -> flat average GSD fallback."""
    if not _SHAPELY_AVAILABLE:
        pytest.skip(f"Shapely not available: {_SHAPELY_IMPORT_ERROR}")
    fake = _FakeImageService(terrain_gsd_cm=None, terrain_agl_m=None, flat_gsd_cm=4.0)
    service = CoverageExtentService(use_terrain=True)
    corners = _fov_corners_with(service, fake)

    assert corners is not None and len(corners) == 4
    assert len(fake.compute_calls) == 1  # terrain was attempted
    assert len(fake.average_calls) == 1  # then fell back
    assert _span_east_m(corners) == pytest.approx(160.0, rel=0.01)
