"""Cancelling the AOI derivation between images.

Terrain acquisition derives its area on a worker thread, and a window that
closes must be able to stop that thread promptly: the scans check
``cancel_check`` before each image and behave exactly as before without it.
"""

from unittest.mock import patch

from core.services.coverage import aoi
from core.services.coverage.params import PodParams
from core.services.image.FrameGeometry import FrameGeometry

IMAGES = [{"path": p} for p in ("a.jpg", "b.jpg", "c.jpg")]


def _cancel_after(calls):
    """A cancel_check that turns True once ``calls`` has a first entry."""
    return lambda: len(calls) >= 1


def _nadir_frame():
    return FrameGeometry(
        lat=38.7, lon=-120.5, agl_m=120.0, yaw_deg=0.0, pitch_deg=-90.0, roll_deg=0.0,
        focal_mm=8.8, sensor_mm=(13.2, 8.8), image_size=(4000, 3000),
        principal_point_mm=None, yaw_source='gimbal', bearing_confidence=1.0)


def test_bounds_scan_stops_at_the_next_image_once_cancelled():
    calls = []

    def gps(path):
        calls.append(path)
        return 38.7, -120.5

    with patch.object(aoi, "image_gps", side_effect=gps):
        assert aoi.compute_mission_gps_bounds(IMAGES, cancel_check=_cancel_after(calls)) is None
    assert calls == ["a.jpg"]


def test_bounds_scan_is_unchanged_when_never_cancelled():
    coords = {"a.jpg": (38.70, -120.50), "b.jpg": (38.72, -120.46), "c.jpg": (38.71, -120.48)}
    with patch.object(aoi, "image_gps", side_effect=lambda p: coords.get(p)):
        assert (aoi.compute_mission_gps_bounds(IMAGES, cancel_check=lambda: False)
                == aoi.compute_mission_gps_bounds(IMAGES))


def test_buffer_sampling_stops_at_the_next_image_once_cancelled():
    calls = []

    def frame(path):
        calls.append(path)
        return _nadir_frame()

    with patch.object(aoi, "_frame_geometry", side_effect=frame):
        buf = aoi.suggest_buffer_m(IMAGES, params=PodParams(), cancel_check=_cancel_after(calls))
    assert calls == ["a.jpg"]
    assert buf == aoi._DEFAULT_BUFFER_M


def test_buffer_is_unchanged_when_never_cancelled():
    with patch.object(aoi, "_frame_geometry", return_value=_nadir_frame()):
        assert (aoi.suggest_buffer_m(IMAGES, params=PodParams(), cancel_check=lambda: False)
                == aoi.suggest_buffer_m(IMAGES, params=PodParams()))
