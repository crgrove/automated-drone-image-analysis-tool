"""Tests for FrameGeometry + the ImageService yaw-source / projection-context refactor."""

import os
import tempfile

import cv2
import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from core.services.image.FrameGeometry import (
    FrameGeometry,
    BEARING_QUALITY_CONFIDENCE,
    NO_YAW_CONFIDENCE,
)
from core.services.image.ImageService import ImageService

EXIF_IMAGE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "rgb", "input", "DJI_0082.JPG")
)


def _mock_image_service(**overrides):
    """A duck-typed ImageService with the getters FrameGeometry consumes."""
    svc = MagicMock()
    svc.img_array = np.zeros((3000, 4000, 3), dtype=np.uint8)
    svc.exif_data = {"GPS": {}}  # LocationInfo.get_gps is patched by callers
    svc.get_camera_intrinsics.return_value = {
        'focal_length_mm': 8.8,
        'sensor_width_mm': 13.2,
        'sensor_height_mm': 8.8,
    }
    svc.get_camera_yaw_with_source.return_value = (137.0, 'gimbal')
    svc.get_camera_pitch.return_value = -90.0
    svc.get_gimbal_roll.return_value = 0.0
    svc.get_relative_altitude.return_value = 120.0
    svc.get_asl_altitude.return_value = 1500.0
    for k, v in overrides.items():
        setattr(svc, k, v)
    return svc


def _patch_gps(lat=38.7, lon=-120.5):
    return patch(
        "core.services.image.FrameGeometry.LocationInfo.get_gps",
        return_value={'latitude': lat, 'longitude': lon},
    )


def test_from_image_service_populates_all_fields():
    svc = _mock_image_service()
    with _patch_gps():
        fg = FrameGeometry.from_image_service(svc)
    assert fg is not None
    assert fg.lat == pytest.approx(38.7)
    assert fg.lon == pytest.approx(-120.5)
    assert fg.agl_m == pytest.approx(120.0)
    assert fg.yaw_deg == pytest.approx(137.0)
    assert fg.yaw_source == 'gimbal'
    assert fg.bearing_confidence == 1.0
    assert fg.pitch_deg == pytest.approx(-90.0)
    assert fg.focal_mm == pytest.approx(8.8)
    assert fg.sensor_mm == (13.2, 8.8)
    assert fg.image_size == (4000, 3000)   # (width, height)
    assert fg.principal_point_mm is None
    assert fg.cam_elev_m is None           # no terrain access
    assert fg.asl_alt_m == pytest.approx(1500.0)


def test_no_gps_returns_none():
    svc = _mock_image_service()
    with patch("core.services.image.FrameGeometry.LocationInfo.get_gps", return_value={}):
        assert FrameGeometry.from_image_service(svc) is None


def test_missing_intrinsics_returns_none():
    svc = _mock_image_service()
    svc.get_camera_intrinsics.return_value = None
    with _patch_gps():
        assert FrameGeometry.from_image_service(svc) is None


def test_nonpositive_agl_returns_none():
    svc = _mock_image_service()
    svc.get_relative_altitude.return_value = 0.0
    with _patch_gps():
        assert FrameGeometry.from_image_service(svc) is None


def test_agl_override_and_custom_priority():
    svc = _mock_image_service()
    # agl_override_ft (e.g. wingtra) wins over custom and XMP.
    with _patch_gps():
        fg = FrameGeometry.from_image_service(svc, custom_altitude_ft=400.0,
                                              agl_override_ft=328.084)
    assert fg.agl_m == pytest.approx(100.0, abs=1e-3)   # 328.084 ft
    with _patch_gps():
        fg2 = FrameGeometry.from_image_service(svc, custom_altitude_ft=328.084)
    assert fg2.agl_m == pytest.approx(100.0, abs=1e-3)


def test_roll_over_90_is_zeroed():
    svc = _mock_image_service()
    svc.get_gimbal_roll.return_value = 178.0
    with _patch_gps():
        fg = FrameGeometry.from_image_service(svc)
    assert fg.roll_deg == 0.0


def test_yaw_fallback_confidence_mapping():
    svc = _mock_image_service()
    svc.get_camera_yaw_with_source.return_value = (200.0, 'calculated')
    with _patch_gps():
        fg = FrameGeometry.from_image_service(svc, bearing_quality='turn_inferred')
    assert fg.yaw_source == 'calculated'
    assert fg.bearing_confidence == BEARING_QUALITY_CONFIDENCE['turn_inferred']


def test_no_yaw_defaults_to_zero_low_confidence():
    svc = _mock_image_service()
    svc.get_camera_yaw_with_source.return_value = (None, None)
    with _patch_gps():
        fg = FrameGeometry.from_image_service(svc)
    assert fg.yaw_deg == 0.0
    assert fg.yaw_source == 'default'
    assert fg.bearing_confidence == NO_YAW_CONFIDENCE


def test_image_size_from_exif_when_no_array():
    import piexif
    svc = _mock_image_service()
    svc.img_array = None
    svc.exif_data = {
        "GPS": {},
        "Exif": {piexif.ExifIFD.PixelXDimension: 5472, piexif.ExifIFD.PixelYDimension: 3648},
    }
    with _patch_gps():
        fg = FrameGeometry.from_image_service(svc)
    assert fg.image_size == (5472, 3648)


# --- ImageService integration: yaw parity + projection-context golden keys ---

@pytest.fixture
def synthetic_service():
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        cv2.imwrite(tmp.name, np.zeros((60, 80, 3), dtype=np.uint8))
        path = tmp.name
    svc = ImageService(path, img_array=np.zeros((60, 80, 3), dtype=np.uint8))
    yield svc
    if os.path.exists(path):
        os.unlink(path)


PROJ_CTX_KEYS = {
    'drone_lat', 'drone_lon', 'img_w', 'img_h', 'cx', 'cy', 'focal_mm',
    'sensor_w_mm', 'sensor_h_mm', 'pitch', 'yaw', 'roll', 'roll_axis',
    'reported_agl', 'drone_terrain_elev_m', 'drone_absolute_elev_m',
    'terrain_service',
}


def test_projection_context_golden_keys(synthetic_service):
    svc = synthetic_service
    # Stub the pose/intrinsics getters on the instance.
    svc.get_camera_intrinsics = lambda: {
        'focal_length_mm': 8.8, 'sensor_width_mm': 13.2, 'sensor_height_mm': 8.8}
    svc.get_camera_yaw_with_source = lambda: (45.0, 'gimbal')
    svc.get_camera_pitch = lambda: -90.0
    svc.get_gimbal_roll = lambda: 0.0
    svc.get_relative_altitude = lambda unit='m': 120.0
    svc.get_asl_altitude = lambda unit: 1500.0

    disabled_terrain = MagicMock()
    disabled_terrain.enabled = False
    with patch("core.services.image.FrameGeometry.LocationInfo.get_gps",
               return_value={'latitude': 38.7, 'longitude': -120.5}), \
         patch("core.services.terrain.TerrainService", return_value=disabled_terrain):
        ctx = svc._get_projection_context()

    assert ctx is not None
    assert set(ctx.keys()) == PROJ_CTX_KEYS
    assert ctx['drone_lat'] == pytest.approx(38.7)
    assert ctx['img_w'] == 80 and ctx['img_h'] == 60
    assert ctx['cx'] == pytest.approx(40.0) and ctx['cy'] == pytest.approx(30.0)
    assert ctx['yaw'] == pytest.approx(45.0)
    assert ctx['pitch'] == pytest.approx(-90.0)
    assert ctx['reported_agl'] == pytest.approx(120.0)
    # Terrain disabled -> reconciliation fields stay None.
    assert ctx['drone_terrain_elev_m'] is None
    assert ctx['drone_absolute_elev_m'] is None


def test_projection_context_none_without_img_array(synthetic_service):
    synthetic_service.img_array = None
    assert synthetic_service._get_projection_context() is None


@pytest.mark.skipif(not os.path.exists(EXIF_IMAGE),
                    reason="test data DJI_0082.JPG not present in this checkout")
def test_real_image_frame_geometry_and_yaw_parity():
    svc = ImageService(EXIF_IMAGE)
    assert svc.get_camera_yaw() == svc.get_camera_yaw_with_source()[0]
    fg = svc.get_frame_geometry()
    assert fg is not None
    assert fg.yaw_source in ('gimbal', 'flight')
    assert fg.bearing_confidence == 1.0
    assert -180.0 <= fg.pitch_deg <= 180.0
    assert fg.agl_m > 0


# --- ImageService.get_frame_geometry caching (determinism) ---

def test_get_frame_geometry_caches_per_args(synthetic_service):
    """Same (custom_altitude_ft, agl_override_ft) -> cached object, computed once;
    a different arg combination recomputes (cache keyed per-args)."""
    svc = synthetic_service
    sentinel_a = MagicMock(name="fg_a")
    sentinel_b = MagicMock(name="fg_b")
    with patch(
        "core.services.image.FrameGeometry.FrameGeometry.from_image_service",
        side_effect=[sentinel_a, sentinel_b],
    ) as spy:
        first = svc.get_frame_geometry(custom_altitude_ft=400.0, agl_override_ft=None)
        second = svc.get_frame_geometry(custom_altitude_ft=400.0, agl_override_ft=None)
        # Identical args: same object returned, from_image_service invoked once.
        assert first is sentinel_a
        assert second is sentinel_a
        assert first is second
        assert spy.call_count == 1

        # A different (custom_altitude_ft, agl_override_ft) combo recomputes.
        third = svc.get_frame_geometry(custom_altitude_ft=500.0, agl_override_ft=None)
        assert third is sentinel_b
        assert spy.call_count == 2

        # And a distinct agl_override_ft (custom held constant) is also a new key.
        with patch(
            "core.services.image.FrameGeometry.FrameGeometry.from_image_service",
            return_value=MagicMock(name="fg_c"),
        ) as spy2:
            svc.get_frame_geometry(custom_altitude_ft=400.0, agl_override_ft=200.0)
            assert spy2.call_count == 1


def test_get_frame_geometry_cache_ignores_bearing_quality(synthetic_service):
    """Cache key is (custom_altitude_ft, agl_override_ft) only: a changed
    bearing_quality with the same altitude args returns the cached object and does
    NOT trigger a recompute (documented keying in get_frame_geometry)."""
    svc = synthetic_service
    sentinel = MagicMock(name="fg")
    with patch(
        "core.services.image.FrameGeometry.FrameGeometry.from_image_service",
        return_value=sentinel,
    ) as spy:
        first = svc.get_frame_geometry(custom_altitude_ft=None, agl_override_ft=None,
                                       bearing_quality='good')
        second = svc.get_frame_geometry(custom_altitude_ft=None, agl_override_ft=None,
                                        bearing_quality='gap')
        assert first is second is sentinel
        assert spy.call_count == 1


def test_get_frame_geometry_caches_none_result(synthetic_service):
    """A None result (e.g. no GPS) is cached too: the second call with the same
    args does not re-invoke from_image_service."""
    svc = synthetic_service
    with patch(
        "core.services.image.FrameGeometry.FrameGeometry.from_image_service",
        return_value=None,
    ) as spy:
        assert svc.get_frame_geometry(custom_altitude_ft=None, agl_override_ft=None) is None
        assert svc.get_frame_geometry(custom_altitude_ft=None, agl_override_ft=None) is None
        assert spy.call_count == 1
