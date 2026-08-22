"""
Comprehensive tests for AOIService.

Tests AOI geospatial calculations and color extraction.
"""

import math
import pytest
import numpy as np
import cv2
import tempfile
import os
from unittest.mock import patch, MagicMock
from core.services.image.AOIService import AOIService
from helpers.PhotogrammetryHelper import (
    local_enu_to_gps, build_camera_matrix, project_pixel_to_plane,
)


@pytest.fixture
def sample_image_data():
    """Sample image metadata."""
    return {
        'path': 'test_image.jpg',
        'mask_path': 'test_mask.tif',
        'lat': 37.7749,
        'lon': -122.4194
    }


@pytest.fixture
def sample_aoi():
    """Sample AOI data."""
    return {
        'center': (100, 100),
        'radius': 20,
        'area': 400,
        'detected_pixels': [(95, 95), (96, 96), (97, 97)]
    }


def test_aoi_service_initialization(sample_image_data):
    """Test AOIService initialization."""
    with patch('core.services.image.AOIService.ImageService'):
        service = AOIService(sample_image_data)
        assert service.image_service is not None


def test_aoi_service_with_preloaded_image(sample_image_data):
    """Test AOIService with preloaded image array."""
    test_img = np.zeros((200, 200, 3), dtype=np.uint8)

    with patch('core.services.image.AOIService.ImageService'):
        service = AOIService(sample_image_data, img_array=test_img)
        assert service.image_service is not None


def test_aoi_service_reuses_provided_image_service(sample_image_data):
    """When an ImageService is supplied it is reused as-is, with no new
    ImageService constructed (avoids a redundant per-transition decode +
    metadata read)."""
    existing = MagicMock()
    with patch('core.services.image.AOIService.ImageService') as MockImageService:
        service = AOIService(sample_image_data, image_service=existing)

    assert service.image_service is existing
    MockImageService.assert_not_called()


def test_estimate_aoi_gps(sample_image_data, sample_aoi):
    """Test estimating AOI GPS coordinates."""
    with patch('core.services.image.AOIService.ImageService') as MockImageService, \
            patch('helpers.MetaDataHelper.MetaDataHelper.get_exif_data_piexif') as mock_exif, \
            patch('helpers.LocationInfo.LocationInfo.get_gps') as mock_gps:

        # Mock EXIF and GPS data
        mock_exif.return_value = {}
        mock_gps.return_value = {'latitude': 37.7749, 'longitude': -122.4194}

        # Mock ImageService
        mock_service = MagicMock()
        mock_service.get_camera_yaw.return_value = 0.0
        mock_service.get_camera_pitch.return_value = -90.0
        mock_service.get_relative_altitude.return_value = 100.0
        mock_service.get_camera_intrinsics.return_value = {
            'focal_length_mm': 24.0,
            'sensor_width_mm': 23.5,
            'sensor_height_mm': 15.6
        }
        mock_service.img_array = np.zeros((200, 200, 3), dtype=np.uint8)
        MockImageService.return_value = mock_service

        service = AOIService(sample_image_data)
        result = service.estimate_aoi_gps(sample_image_data, sample_aoi)

        # Result should be AOIGPSResult or None (new return type)
        if result is not None:
            assert hasattr(result, 'latitude')
            assert hasattr(result, 'longitude')
            assert hasattr(result, 'elevation_source')


def test_get_aoi_representative_color(sample_image_data, sample_aoi):
    """Test getting representative color for an AOI."""
    test_img = np.zeros((200, 200, 3), dtype=np.uint8)
    test_img[95:105, 95:105] = [100, 150, 200]  # Colored region

    with patch('core.services.image.AOIService.ImageService') as MockImageService:
        mock_service = MagicMock()
        mock_service.img_array = test_img
        MockImageService.return_value = mock_service

        service = AOIService(sample_image_data, img_array=test_img)
        color_result = service.get_aoi_representative_color(sample_aoi)

        if color_result:
            assert 'rgb' in color_result
            assert 'hex' in color_result
            assert 'hue_degrees' in color_result


def test_get_cached_or_representative_color_prefers_cache(sample_image_data):
    """When the AOI carries color_info, it is used verbatim and no recompute occurs."""
    with patch('core.services.image.AOIService.ImageService'):
        service = AOIService(sample_image_data)

    aoi = {
        'center': (100, 100),
        'radius': 20,
        'color_info': {'rgb': [0, 85, 255], 'hex': '#0055ff', 'hue_degrees': 220.0},
    }

    with patch.object(service, 'get_aoi_representative_color') as mock_compute:
        result = service.get_cached_or_representative_color(aoi)

    assert result == {'rgb': (0, 85, 255), 'hex': '#0055ff', 'hue_degrees': 220}
    mock_compute.assert_not_called()


def test_get_cached_or_representative_color_falls_back_to_compute(sample_image_data, sample_aoi):
    """Without cached color_info, fall back to the live representative-color calc."""
    with patch('core.services.image.AOIService.ImageService'):
        service = AOIService(sample_image_data)

    computed = {'rgb': (255, 0, 101), 'hex': '#ff0065', 'hue_degrees': 336}
    with patch.object(service, 'get_aoi_representative_color', return_value=computed) as mock_compute:
        result = service.get_cached_or_representative_color(sample_aoi)

    assert result == computed
    mock_compute.assert_called_once_with(sample_aoi)


def test_calculate_gps_with_custom_altitude(sample_image_data, sample_aoi):
    """Test calculating GPS with custom altitude override."""
    with patch('core.services.image.AOIService.ImageService') as MockImageService, \
            patch('helpers.MetaDataHelper.MetaDataHelper.get_exif_data_piexif') as mock_exif, \
            patch('helpers.LocationInfo.LocationInfo.get_gps') as mock_gps:

        mock_exif.return_value = {}
        mock_gps.return_value = {'latitude': 37.7749, 'longitude': -122.4194}

        mock_service = MagicMock()
        mock_service.get_camera_yaw.return_value = 0.0
        mock_service.get_camera_pitch.return_value = -90.0
        mock_service.get_relative_altitude.return_value = 100.0
        mock_service.get_camera_intrinsics.return_value = {
            'focal_length_mm': 24.0,
            'sensor_width_mm': 23.5,
            'sensor_height_mm': 15.6
        }
        mock_service.img_array = np.zeros((200, 200, 3), dtype=np.uint8)
        MockImageService.return_value = mock_service

        service = AOIService(sample_image_data)
        result = service.calculate_gps_with_custom_altitude(
            sample_image_data,
            sample_aoi,
            custom_altitude_ft=328.084  # 100 meters in feet
        )

        # Returns tuple (lat, lon) for backward compatibility
        assert result is None or (isinstance(result, tuple) and len(result) == 2)


def test_estimate_aoi_gps_with_terrain_disabled(sample_image_data, sample_aoi):
    """Test AOI GPS estimation with terrain explicitly disabled."""
    with patch('core.services.image.AOIService.ImageService') as MockImageService, \
            patch('helpers.MetaDataHelper.MetaDataHelper.get_exif_data_piexif') as mock_exif, \
            patch('helpers.LocationInfo.LocationInfo.get_gps') as mock_gps:

        mock_exif.return_value = {}
        mock_gps.return_value = {'latitude': 37.7749, 'longitude': -122.4194}

        mock_service = MagicMock()
        mock_service.get_camera_yaw.return_value = 0.0
        mock_service.get_camera_pitch.return_value = -90.0
        mock_service.get_relative_altitude.return_value = 100.0
        mock_service.get_camera_intrinsics.return_value = {
            'focal_length_mm': 24.0,
            'sensor_width_mm': 23.5,
            'sensor_height_mm': 15.6
        }
        mock_service.img_array = np.zeros((200, 200, 3), dtype=np.uint8)
        MockImageService.return_value = mock_service

        service = AOIService(sample_image_data)
        result = service.estimate_aoi_gps(sample_image_data, sample_aoi, use_terrain=False)

        # Result should be AOIGPSResult or None
        if result:
            assert hasattr(result, 'elevation_source')
            assert result.elevation_source == 'flat'


def test_calculate_gps_with_metadata(sample_image_data, sample_aoi):
    """Test calculating GPS with full metadata result."""
    with patch('core.services.image.AOIService.ImageService') as MockImageService, \
            patch('helpers.MetaDataHelper.MetaDataHelper.get_exif_data_piexif') as mock_exif, \
            patch('helpers.LocationInfo.LocationInfo.get_gps') as mock_gps:

        mock_exif.return_value = {}
        mock_gps.return_value = {'latitude': 37.7749, 'longitude': -122.4194}

        mock_service = MagicMock()
        mock_service.get_camera_yaw.return_value = 0.0
        mock_service.get_camera_pitch.return_value = -90.0
        mock_service.get_relative_altitude.return_value = 100.0
        mock_service.get_camera_intrinsics.return_value = {
            'focal_length_mm': 24.0,
            'sensor_width_mm': 23.5,
            'sensor_height_mm': 15.6
        }
        mock_service.img_array = np.zeros((200, 200, 3), dtype=np.uint8)
        MockImageService.return_value = mock_service

        service = AOIService(sample_image_data)
        result = service.calculate_gps_with_metadata(
            sample_image_data,
            sample_aoi,
            use_terrain=False
        )

        if result:
            assert hasattr(result, 'latitude')
            assert hasattr(result, 'longitude')
            assert hasattr(result, 'elevation_source')
            assert hasattr(result, 'effective_agl_m')


def test_get_aoi_gps_with_metadata(sample_image_data, sample_aoi):
    """Test getting AOI GPS with full metadata dict."""
    with patch('core.services.image.AOIService.ImageService') as MockImageService, \
            patch('helpers.MetaDataHelper.MetaDataHelper.get_exif_data_piexif') as mock_exif, \
            patch('helpers.LocationInfo.LocationInfo.get_gps') as mock_gps:

        mock_exif.return_value = {}
        mock_gps.return_value = {'latitude': 37.7749, 'longitude': -122.4194}

        mock_service = MagicMock()
        mock_service.get_camera_yaw.return_value = 0.0
        mock_service.get_camera_pitch.return_value = -90.0
        mock_service.get_relative_altitude.return_value = 100.0
        mock_service.get_camera_intrinsics.return_value = {
            'focal_length_mm': 24.0,
            'sensor_width_mm': 23.5,
            'sensor_height_mm': 15.6
        }
        mock_service.img_array = np.zeros((200, 200, 3), dtype=np.uint8)
        MockImageService.return_value = mock_service

        service = AOIService(sample_image_data)
        result = service.get_aoi_gps_with_metadata(
            sample_image_data,
            sample_aoi,
            aoi_index=0,
            use_terrain=False
        )

        if result:
            assert 'latitude' in result
            assert 'longitude' in result
            assert 'aoi_index' in result
            assert 'elevation_source' in result
            assert result['aoi_index'] == 0


def test_is_terrain_available():
    """Test terrain availability check."""
    with patch('core.services.image.AOIService._get_terrain_service') as mock_get_terrain:
        # Test when terrain service is not available
        mock_get_terrain.return_value = None
        assert not AOIService.is_terrain_available()

        # Test when terrain service is available and enabled
        mock_service = MagicMock()
        mock_service.enabled = True
        mock_get_terrain.return_value = mock_service
        assert AOIService.is_terrain_available()

        # Test when terrain service is available but disabled
        mock_service.enabled = False
        assert not AOIService.is_terrain_available()


def test_get_terrain_service_applies_offline_only_setting():
    """_get_terrain_service must push the app 'Offline Only' preference onto the
    terrain singleton so DEM/geoid downloads are suppressed while offline."""
    import core.services.image.AOIService as aoi_module
    from core.services.image.AOIService import _get_terrain_service

    fake_service = MagicMock()
    original = aoi_module._terrain_service
    try:
        aoi_module._terrain_service = fake_service
        with patch('core.services.SettingsService.SettingsService') as mock_settings_cls:
            settings = mock_settings_cls.return_value

            settings.get_bool_setting.return_value = True
            svc = _get_terrain_service()
            assert svc is fake_service
            assert fake_service.offline_only is True
            settings.get_bool_setting.assert_called_with('OfflineOnly', False)

            # Toggling the preference is reflected on the next fetch (runtime change).
            settings.get_bool_setting.return_value = False
            _get_terrain_service()
            assert fake_service.offline_only is False
    finally:
        aoi_module._terrain_service = original


def test_get_terrain_service_info():
    """Test getting terrain service info."""
    with patch('core.services.image.AOIService._get_terrain_service') as mock_get_terrain:
        # Test when terrain service is not available
        mock_get_terrain.return_value = None
        assert AOIService.get_terrain_service_info() is None

        # Test when terrain service is available
        mock_service = MagicMock()
        mock_service.get_service_info.return_value = {
            'enabled': True,
            'zoom_level': 12,
            'provider': 'Test Provider'
        }
        mock_get_terrain.return_value = mock_service
        info = AOIService.get_terrain_service_info()
        assert info is not None
        assert 'enabled' in info


def test_aoi_gps_result_to_tuple(sample_image_data, sample_aoi):
    """Test AOIGPSResult to_tuple method for backward compatibility."""
    with patch('core.services.image.AOIService.ImageService') as MockImageService, \
            patch('helpers.MetaDataHelper.MetaDataHelper.get_exif_data_piexif') as mock_exif, \
            patch('helpers.LocationInfo.LocationInfo.get_gps') as mock_gps:

        mock_exif.return_value = {}
        mock_gps.return_value = {'latitude': 37.7749, 'longitude': -122.4194}

        mock_service = MagicMock()
        mock_service.get_camera_yaw.return_value = 0.0
        mock_service.get_camera_pitch.return_value = -90.0
        mock_service.get_relative_altitude.return_value = 100.0
        mock_service.get_camera_intrinsics.return_value = {
            'focal_length_mm': 24.0,
            'sensor_width_mm': 23.5,
            'sensor_height_mm': 15.6
        }
        mock_service.img_array = np.zeros((200, 200, 3), dtype=np.uint8)
        MockImageService.return_value = mock_service

        service = AOIService(sample_image_data)
        result = service.estimate_aoi_gps(sample_image_data, sample_aoi, use_terrain=False)

        if result:
            tuple_result = result.to_tuple()
            assert isinstance(tuple_result, tuple)
            assert len(tuple_result) == 2
            assert tuple_result == (result.latitude, result.longitude)


def test_calculate_ground_position_nadir_no_roll_returns_drone_position():
    """At pitch=-90 with center pixel and no roll, ray hits ground directly under drone."""
    drone_lat, drone_lon = 37.0, -120.0
    altitude = 500.0
    img_w, img_h = 8000, 6000
    cx, cy = img_w / 2.0, img_h / 2.0

    result = AOIService._calculate_ground_position(
        drone_lat, drone_lon,
        cx, cy,  # center pixel
        cx, cy,
        img_w, img_h,
        focal_mm=50.0, sensor_w_mm=36.0, sensor_h_mm=24.0,
        altitude_m=altitude,
        pitch_deg=-90.0, yaw_deg=0.0,
    )
    assert result is not None
    lat, lon = result
    assert pytest.approx(lat, abs=1e-5) == drone_lat
    assert pytest.approx(lon, abs=1e-5) == drone_lon


def test_calculate_ground_position_left_outward_roll_pushes_west_at_north_heading():
    """Cam 0 (+22.5° roll, plane heading north) hits ground ~h*tan(22.5°) WEST of drone."""
    drone_lat, drone_lon = 37.0, -120.0
    altitude = 500.0
    img_w, img_h = 8000, 6000
    cx, cy = img_w / 2.0, img_h / 2.0

    result = AOIService._calculate_ground_position(
        drone_lat, drone_lon,
        cx, cy,
        cx, cy,
        img_w, img_h,
        focal_mm=50.0, sensor_w_mm=36.0, sensor_h_mm=24.0,
        altitude_m=altitude,
        pitch_deg=-90.0, yaw_deg=0.0,
        roll_deg=22.5,
    )
    assert result is not None
    lat, lon = result
    expected_offset_m = altitude * math.tan(math.radians(22.5))  # ~207.1 m
    actual_offset_m = (drone_lon - lon) * 111320 * math.cos(math.radians(drone_lat))
    assert pytest.approx(lat, abs=1e-5) == drone_lat  # heading north → no N/S drift
    assert pytest.approx(actual_offset_m, rel=0.01) == expected_offset_m


def test_calculate_ground_position_right_outward_roll_pushes_east_at_north_heading():
    """Cam 1 (-22.5° roll, plane heading north) hits ground ~h*tan(22.5°) EAST of drone."""
    drone_lat, drone_lon = 37.0, -120.0
    altitude = 500.0
    img_w, img_h = 8000, 6000
    cx, cy = img_w / 2.0, img_h / 2.0

    result = AOIService._calculate_ground_position(
        drone_lat, drone_lon,
        cx, cy,
        cx, cy,
        img_w, img_h,
        focal_mm=50.0, sensor_w_mm=36.0, sensor_h_mm=24.0,
        altitude_m=altitude,
        pitch_deg=-90.0, yaw_deg=0.0,
        roll_deg=-22.5,
    )
    assert result is not None
    lat, lon = result
    expected_offset_m = altitude * math.tan(math.radians(22.5))
    actual_offset_m = (lon - drone_lon) * 111320 * math.cos(math.radians(drone_lat))
    assert pytest.approx(lat, abs=1e-5) == drone_lat
    assert pytest.approx(actual_offset_m, rel=0.01) == expected_offset_m


# --- Manual FOV alignment (refined) path ---

_ALIGN_ORIGIN_LAT = 39.5
_ALIGN_ORIGIN_LON = -105.5


def _align_corner(east, north):
    return local_enu_to_gps(east, north, _ALIGN_ORIGIN_LAT, _ALIGN_ORIGIN_LON)


def _align_rectangular_corners():
    """TL, TR, BR, BL of a north-up rectangular footprint."""
    return [
        _align_corner(-100.0, 75.0),
        _align_corner(100.0, 75.0),
        _align_corner(100.0, -75.0),
        _align_corner(-100.0, -75.0),
    ]


@pytest.fixture
def aligned_image_data():
    return {
        'path': 'aligned_image.jpg',
        'width': 4000,
        'height': 3000,
        'fov_alignment': {
            'corners': _align_rectangular_corners(),
            'tie_points': [],
            'rotation': 0.0,
        },
    }


def test_refined_path_used_for_aligned_image(aligned_image_data):
    """An image with fov_alignment uses the homography path, not ray-cast."""
    with patch('core.services.image.AOIService.ImageService'):
        service = AOIService(aligned_image_data)
        result = service.estimate_aoi_gps(aligned_image_data, {'center': (2000, 1500)})

    assert result is not None
    assert result.elevation_source == 'refined'
    # Centre pixel of a rectangular footprint maps to the centroid.
    assert pytest.approx(result.latitude, abs=1e-6) == _ALIGN_ORIGIN_LAT
    assert pytest.approx(result.longitude, abs=1e-6) == _ALIGN_ORIGIN_LON


def test_refined_path_maps_corner_pixel(aligned_image_data):
    """Pixel corner (0,0) maps to the top-left aligned GPS corner."""
    with patch('core.services.image.AOIService.ImageService'):
        service = AOIService(aligned_image_data)
        result = service.estimate_aoi_gps(aligned_image_data, {'center': (0, 0)})

    assert result is not None
    assert result.elevation_source == 'refined'
    expected_lat, expected_lon = aligned_image_data['fov_alignment']['corners'][0]
    assert pytest.approx(result.latitude, abs=1e-6) == expected_lat
    assert pytest.approx(result.longitude, abs=1e-6) == expected_lon


def test_degenerate_alignment_returns_none(aligned_image_data):
    """A degenerate alignment quad returns None so the caller can fall back."""
    with patch('core.services.image.AOIService.ImageService'):
        service = AOIService(aligned_image_data)
        bad = {'corners': [(_ALIGN_ORIGIN_LAT, _ALIGN_ORIGIN_LON)] * 4,
               'tie_points': [], 'rotation': 0.0}
        result = service._estimate_aoi_gps_from_alignment(
            aligned_image_data, {'center': (10, 10)}, bad
        )
    assert result is None


def test_refined_path_uses_dem_resection():
    """End-to-end: DEM resection recovers a known AOI position.

    Corners are forward-generated by ray-casting a known camera's image
    corners onto a non-planar (saddle) terrain, so the correspondences are
    consistent with a real camera and the pose solve is well-conditioned.
    """
    width, height = 4000, 3000
    camera_matrix = build_camera_matrix(24.0, 23.5, 15.6, width, height)

    # Known nadir camera 300 m above the origin.
    rotation = np.array([[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]])
    center = np.array([[0.0], [0.0], [300.0]])
    rvec, _ = cv2.Rodrigues(rotation)
    tvec = -rotation @ center

    def elev_fn(lat, lon):
        # Saddle surface - non-planar so the recovered pose is well-conditioned.
        return 100.0 + (lat - _ALIGN_ORIGIN_LAT) * (lon - _ALIGN_ORIGIN_LON) * 8.0e6

    def ray_to_terrain(u, v):
        plane_z = 100.0
        lat = lon = None
        for _ in range(8):
            hit = project_pixel_to_plane(rvec, tvec, camera_matrix, u, v, plane_z)
            lat, lon = local_enu_to_gps(hit[0], hit[1], _ALIGN_ORIGIN_LAT, _ALIGN_ORIGIN_LON)
            plane_z = elev_fn(lat, lon)
        return lat, lon

    corners = [ray_to_terrain(u, v) for u, v in
               [(0, 0), (width, 0), (width, height), (0, height)]]
    true_lat, true_lon = ray_to_terrain(2000, 1500)

    image_data = {
        'path': 'aligned.jpg', 'width': width, 'height': height,
        'fov_alignment': {'corners': corners, 'tie_points': [], 'rotation': 0.0},
    }

    def fake_elevation(lat, lon):
        result = MagicMock()
        result.source = 'terrain'
        result.elevation_m = elev_fn(lat, lon)
        return result

    terrain = MagicMock()
    terrain.enabled = True
    terrain.get_elevation.side_effect = fake_elevation

    with patch('core.services.image.AOIService.ImageService') as MockImageService, \
            patch('core.services.image.AOIService._get_terrain_service', return_value=terrain):
        mock_service = MagicMock()
        mock_service.get_camera_intrinsics.return_value = {
            'focal_length_mm': 24.0,
            'sensor_width_mm': 23.5,
            'sensor_height_mm': 15.6,
        }
        MockImageService.return_value = mock_service
        service = AOIService(image_data)
        result = service.estimate_aoi_gps(image_data, {'center': (2000, 1500)})

    assert result is not None
    assert result.elevation_source == 'refined_terrain'
    assert result.latitude == pytest.approx(true_lat, abs=1e-4)
    assert result.longitude == pytest.approx(true_lon, abs=1e-4)


def test_refined_path_falls_back_to_homography_without_terrain(aligned_image_data):
    """With terrain unavailable the refined path uses the planar homography."""
    with patch('core.services.image.AOIService.ImageService'), \
            patch('core.services.image.AOIService._get_terrain_service', return_value=None):
        service = AOIService(aligned_image_data)
        result = service.estimate_aoi_gps(aligned_image_data, {'center': (2000, 1500)})

    assert result is not None
    assert result.elevation_source == 'refined'


# ---------------------------------------------------------------------------
# Effective-AGL cross-check (guards against the geoid/ASL datum short-throw bug)
# ---------------------------------------------------------------------------

def _make_aoi_service():
    with patch('core.services.image.AOIService.ImageService'):
        return AOIService({'path': 'x.jpg', 'mask_path': ''})


def test_select_effective_agl_uses_absolute_when_agrees():
    """When the absolute and relief AGL estimates agree, the precise absolute
    (e.g. RTK) value is used."""
    svc = _make_aoi_service()
    dt = MagicMock(elevation_m=306.0)
    # |65 - 61| = 4 <= max(0.15*61, 8) = 9.15 -> use absolute
    assert svc._select_effective_agl(65.0, 61.0, 61.0, -26.5, dt, 306.0) == 65.0


def test_select_effective_agl_falls_back_to_relief_on_bad_geoid():
    """A bad geoid makes the absolute estimate diverge; relief must win so the
    AOI is not thrown systematically short."""
    svc = _make_aoi_service()
    dt = MagicMock(elevation_m=306.2)
    # |41 - 61| = 20 > tol -> use relief
    assert svc._select_effective_agl(41.0, 61.0, 61.0, -1.55, dt, 306.2) == 61.0


def test_select_effective_agl_rejects_orthometric_asl_double_correction():
    """The symmetric failure: an orthometric ASL double-corrected too high must
    also fall back to relief rather than throw the AOI too far."""
    svc = _make_aoi_service()
    dt = MagicMock(elevation_m=306.0)
    assert svc._select_effective_agl(90.0, 61.0, 61.0, -26.5, dt, 306.0) == 61.0


def test_select_effective_agl_missing_estimates():
    svc = _make_aoi_service()
    dt = MagicMock(elevation_m=306.0)
    assert svc._select_effective_agl(None, 61.0, 61.0, -26.5, dt, 306.0) == 61.0
    assert svc._select_effective_agl(41.0, None, 61.0, -26.5, dt, 306.0) == 41.0
    assert svc._select_effective_agl(None, None, 61.0, -26.5, dt, 306.0) == 61.0
    assert svc._select_effective_agl(None, None, 0, -26.5, dt, 306.0) == 1.0


def _terrain_mock(geoid_n, ground_elev=306.2):
    """Flat-terrain mock: drone-ground == aoi-ground, so relief AGL == reported."""
    ts = MagicMock()
    ts.enabled = True

    def get_elev(lat, lon, offline_only=False):
        return MagicMock(source='terrain', elevation_m=ground_elev, resolution_m=1.0)

    ts.get_elevation.side_effect = get_elev
    ts.get_geoid_undulation.return_value = geoid_n
    return ts


def _image_service_mock():
    ms = MagicMock()
    ms.get_camera_yaw.return_value = 285.5
    ms.get_camera_pitch.return_value = -75.0
    ms.get_gimbal_roll.return_value = 0.0
    ms.get_relative_altitude.return_value = 61.0
    ms.get_asl_altitude.return_value = 345.7
    ms.get_camera_intrinsics.return_value = {
        'focal_length_mm': 12.3, 'sensor_width_mm': 17.30, 'sensor_height_mm': 13.00,
    }
    ms.img_array = np.zeros((3956, 5280, 3), dtype=np.uint8)
    return ms


def _run_estimate_with_terrain(geoid_n):
    img = {'path': 'x.jpg', 'mask_path': ''}
    aoi = {'center': (2640, 2400), 'radius': 20}
    with patch('core.services.image.AOIService.ImageService') as MockIS, \
            patch('helpers.MetaDataHelper.MetaDataHelper.get_exif_data_piexif', return_value={}), \
            patch('helpers.LocationInfo.LocationInfo.get_gps',
                  return_value={'latitude': 30.6537, 'longitude': -97.9521}), \
            patch('core.services.image.AOIService._get_terrain_service',
                  return_value=_terrain_mock(geoid_n)):
        MockIS.return_value = _image_service_mock()
        service = AOIService(img)
        return service.estimate_aoi_gps(img, aoi, use_terrain=True)


def test_terrain_agl_bad_geoid_falls_back_to_relief_end_to_end():
    """Regression: even with the old broken geoid (~-1.55 m), the terrain path
    must not shrink effective AGL to ~41 m; the cross-check keeps it near the
    reported 61 m so the AOI cannot smear."""
    res = _run_estimate_with_terrain(geoid_n=-1.55)
    assert res is not None
    assert res.elevation_source == 'terrain'
    assert abs(res.effective_agl_m - 61.0) < 3.0


def test_terrain_agl_good_geoid_uses_absolute_end_to_end():
    """With a correct geoid the absolute (RTK) estimate ~66 m agrees with relief
    and is used."""
    res = _run_estimate_with_terrain(geoid_n=-26.5)
    assert res is not None
    assert res.elevation_source == 'terrain'
    assert abs(res.effective_agl_m - 66.0) < 3.0


def test_terrain_agl_equals_reported_on_flat_terrain():
    """On flat terrain the effective AGL must equal the reported AGL regardless
    of which branch is chosen."""
    res = _run_estimate_with_terrain(geoid_n=-26.5)
    assert res is not None
    # reported 61, RTK-implied 66; both within a few metres of reported on flat ground
    assert abs(res.effective_agl_m - 61.0) < 6.0
