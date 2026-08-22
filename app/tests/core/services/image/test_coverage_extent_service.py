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
                 roll_deg=0.0, reported_agl_m=100.0, yaw_deg=0.0,
                 pitch_deg=-90.0, waldo_version=None, roll_axis_deg=None):
        import math as _math
        self._math = _math
        self.terrain_gsd_cm = terrain_gsd_cm
        self.terrain_agl_m = terrain_agl_m
        self.flat_gsd_cm = flat_gsd_cm
        self.roll_deg = roll_deg
        self.reported_agl_m = reported_agl_m
        self.yaw_deg = yaw_deg
        self.pitch_deg = pitch_deg
        self.waldo_version = waldo_version
        self.roll_axis_deg = roll_axis_deg
        self.img_array = MagicMock(shape=(3000, 4000))
        self.compute_calls = []
        self.average_calls = []

    def get_camera_pitch(self):
        return self.pitch_deg

    def get_gimbal_roll(self):
        return self.roll_deg

    def get_camera_yaw(self):
        return self.yaw_deg

    def get_waldo_processor_version(self):
        return self.waldo_version

    def get_roll_axis_azimuth(self):
        return self.roll_axis_deg

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


def _centroid_north_m(corners):
    """Mean north-offset of the corners from the drone position, in meters."""
    import math
    lats = [lat for lat, _lon in corners]
    mean_dlat = sum(lats) / len(lats) - _LAT
    return mean_dlat * _EARTH_RADIUS * math.pi / 180.0


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


class _WaldoFakeImageService(_FakeImageService):
    """Fake with WALDO v6+ stamps: roll expressed about the FLIGHT axis."""

    def __init__(self, roll_axis_deg, **kwargs):
        super().__init__(**kwargs)
        self.roll_axis_deg = roll_axis_deg

    def get_roll_axis_azimuth(self):
        return self.roll_axis_deg


def test_fov_polygon_waldo_flight_axis_roll_lands_plane_right():
    """WALDO cam0 v6+ stamp: heading 319.7 (NW), image-top backward
    (yaw 139.7), roll -22.5 about the FLIGHT axis => footprint plane-RIGHT
    of the track (NE). Interpreting the roll about the camera axis instead
    mirrored the blue footprint to the SW - the field-reported bug."""
    if not _SHAPELY_AVAILABLE:
        pytest.skip(f"Shapely not available: {_SHAPELY_IMPORT_ERROR}")
    import math
    heading = 319.7
    fake = _WaldoFakeImageService(
        roll_axis_deg=heading, yaw_deg=(heading + 180.0) % 360.0,
        roll_deg=-22.5, flat_gsd_cm=4.0, reported_agl_m=776.0)
    service = CoverageExtentService(use_terrain=False)
    corners = _fov_corners_with(service, fake)

    assert corners is not None and len(corners) == 4
    # Offset direction: plane-right of 319.7 = bearing 49.7 (northeast).
    offset_m = 776.0 * math.tan(math.radians(22.5))
    expected_east = offset_m * math.sin(math.radians(heading + 90.0))
    assert expected_east > 0  # sanity: NE means east-positive
    assert _centroid_east_m(corners) == pytest.approx(expected_east, rel=0.02)


def test_fov_polygon_legacy_camera_axis_roll_unchanged():
    """Without a roll axis (DJI / WALDO v5 stamps) the old camera-axis
    interpretation must be preserved: same yaw/roll numbers land the
    footprint on the OPPOSITE side of the WALDO case above."""
    if not _SHAPELY_AVAILABLE:
        pytest.skip(f"Shapely not available: {_SHAPELY_IMPORT_ERROR}")
    import math
    heading = 319.7
    fake = _FakeImageService(
        yaw_deg=(heading + 180.0) % 360.0, roll_deg=-22.5,
        flat_gsd_cm=4.0, reported_agl_m=776.0)
    service = CoverageExtentService(use_terrain=False)
    corners = _fov_corners_with(service, fake)

    assert corners is not None and len(corners) == 4
    # Legacy: offset -h*tan(roll) along camera-X (yaw+90 = 229.7, SW).
    offset_m = -776.0 * math.tan(math.radians(-22.5))
    expected_east = offset_m * math.sin(math.radians(((heading + 180.0) % 360.0) + 90.0))
    assert expected_east < 0  # sanity: SW means east-negative
    assert _centroid_east_m(corners) == pytest.approx(expected_east, rel=0.02)


# ---------------------------------------------------------------------------
# Composite off-nadir gate (WALDO flight-log attitude)
# ---------------------------------------------------------------------------

def test_gate_dji_oblique_still_skipped_and_nadir_still_passes():
    """Non-WALDO images keep the historical pitch gate, unchanged."""
    if not _SHAPELY_AVAILABLE:
        pytest.skip(f"Shapely not available: {_SHAPELY_IMPORT_ERROR}")
    service = CoverageExtentService(use_terrain=False)
    oblique = _FakeImageService(pitch_deg=-60.0)
    assert _fov_corners_with(service, oblique) is None
    nadir = _FakeImageService(pitch_deg=-89.0)
    assert _fov_corners_with(service, nadir) is not None


def test_gate_waldo_constants_pass_as_before():
    """WALDO without a flight log: (-90, ±22.5) is 22.5° off nadir - inside."""
    if not _SHAPELY_AVAILABLE:
        pytest.skip(f"Shapely not available: {_SHAPELY_IMPORT_ERROR}")
    service = CoverageExtentService(use_terrain=False)
    fake = _FakeImageService(waldo_version="9", roll_deg=22.5, roll_axis_deg=0.0)
    assert _fov_corners_with(service, fake) is not None


def test_gate_waldo_composed_attitude_inside_threshold_passes():
    """Flight-log attitude: pitch -92 with roll -35 is ~35° off nadir - inside."""
    if not _SHAPELY_AVAILABLE:
        pytest.skip(f"Shapely not available: {_SHAPELY_IMPORT_ERROR}")
    service = CoverageExtentService(use_terrain=False)
    fake = _FakeImageService(waldo_version="9", pitch_deg=-92.0, roll_deg=-35.0,
                             roll_axis_deg=0.0)
    assert _fov_corners_with(service, fake) is not None


def test_gate_waldo_steep_bank_skipped():
    """A banked turn frame past the composite threshold drops out of coverage."""
    if not _SHAPELY_AVAILABLE:
        pytest.skip(f"Shapely not available: {_SHAPELY_IMPORT_ERROR}")
    service = CoverageExtentService(use_terrain=False)
    fake = _FakeImageService(waldo_version="9", roll_deg=45.0, roll_axis_deg=0.0)
    assert _fov_corners_with(service, fake) is None


def test_waldo_pitch_shifts_footprint_along_image_top_azimuth():
    """WALDO pitch off -90 adds an along-azimuth h*tan(pitch+90) offset."""
    if not _SHAPELY_AVAILABLE:
        pytest.skip(f"Shapely not available: {_SHAPELY_IMPORT_ERROR}")
    import math
    fake = _FakeImageService(waldo_version="9", pitch_deg=-95.0, roll_deg=0.0,
                             yaw_deg=0.0, flat_gsd_cm=4.0, reported_agl_m=100.0)
    service = CoverageExtentService(use_terrain=False)
    corners = _fov_corners_with(service, fake)
    assert corners is not None
    # pitch+90 = -5°: shifted AWAY from the yaw azimuth (south of the drone).
    expected_north = 100.0 * math.tan(math.radians(-5.0))
    assert _centroid_north_m(corners) == pytest.approx(expected_north, rel=0.02)


def test_dji_pitch_gets_no_footprint_shift():
    """Non-WALDO: a -89 pitch keeps the historical footprint center."""
    if not _SHAPELY_AVAILABLE:
        pytest.skip(f"Shapely not available: {_SHAPELY_IMPORT_ERROR}")
    fake = _FakeImageService(pitch_deg=-89.0, roll_deg=0.0, yaw_deg=0.0,
                             flat_gsd_cm=4.0, reported_agl_m=100.0)
    service = CoverageExtentService(use_terrain=False)
    corners = _fov_corners_with(service, fake)
    assert corners is not None
    assert _centroid_north_m(corners) == pytest.approx(0.0, abs=0.01)
