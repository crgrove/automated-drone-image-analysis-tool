"""Tests for deriving a download AOI from a mission's images."""

import math

import pytest
from unittest.mock import patch

from core.services.coverage import aoi
from core.services.coverage.params import PodParams


def test_compute_mission_gps_bounds():
    coords = {
        "a.jpg": (38.70, -120.50),
        "b.jpg": (38.72, -120.46),
        "c.jpg": (38.71, -120.48),
    }
    images = [{"path": p} for p in coords]
    with patch.object(aoi, "image_gps", side_effect=lambda p: coords.get(p)):
        b = aoi.compute_mission_gps_bounds(images)
    assert b == pytest.approx((-120.50, 38.70, -120.46, 38.72))


def test_compute_bounds_none_without_gps():
    images = [{"path": "a.jpg"}, {"path": "b.jpg"}]
    with patch.object(aoi, "image_gps", return_value=None):
        assert aoi.compute_mission_gps_bounds(images) is None


def test_pad_bounds_expands_outward():
    raw = (-120.50, 38.70, -120.46, 38.72)
    padded = aoi.pad_bounds(raw, 1000.0)
    assert padded[0] < raw[0] and padded[1] < raw[1]
    assert padded[2] > raw[2] and padded[3] > raw[3]
    # ~1 km in latitude is ~0.009 deg.
    assert (raw[1] - padded[1]) == pytest.approx(1000.0 / 111320.0, rel=1e-3)


def test_suggest_buffer_from_footprint(monkeypatch):
    # Fake a nadir frame at 120 m AGL -> footprint half-diagonal ~ 108 m.
    from core.services.image.FrameGeometry import FrameGeometry
    fg = FrameGeometry(
        lat=38.7, lon=-120.5, agl_m=120.0, yaw_deg=0.0, pitch_deg=-90.0, roll_deg=0.0,
        focal_mm=8.8, sensor_mm=(13.2, 8.8), image_size=(4000, 3000),
        principal_point_mm=None, yaw_source='gimbal', bearing_confidence=1.0)
    monkeypatch.setattr(aoi, "_frame_geometry", lambda p: fg)
    images = [{"path": "a.jpg"}, {"path": "b.jpg"}]
    buf = aoi.suggest_buffer_m(images, params=PodParams())
    # Reach ~108 m, floored at 100, rounded up to a 50 m step.
    assert 100.0 <= buf <= 200.0
    assert buf % 50.0 == 0


def test_suggest_buffer_capped_at_max_range(monkeypatch):
    from core.services.image.FrameGeometry import FrameGeometry
    # Very oblique frame -> reach clamps to max_range_m.
    fg = FrameGeometry(
        lat=38.7, lon=-120.5, agl_m=120.0, yaw_deg=0.0, pitch_deg=-12.0, roll_deg=0.0,
        focal_mm=8.8, sensor_mm=(13.2, 8.8), image_size=(4000, 3000),
        principal_point_mm=None, yaw_source='gimbal', bearing_confidence=1.0)
    monkeypatch.setattr(aoi, "_frame_geometry", lambda p: fg)
    params = PodParams(max_range_m=800.0)
    buf = aoi.suggest_buffer_m([{"path": "a.jpg"}], params=params)
    assert buf <= params.max_range_m


def test_suggest_buffer_default_when_no_geometry(monkeypatch):
    monkeypatch.setattr(aoi, "_frame_geometry", lambda p: None)
    buf = aoi.suggest_buffer_m([{"path": "a.jpg"}])
    assert buf == pytest.approx(aoi._DEFAULT_BUFFER_M)


def test_estimate_download_aoi(monkeypatch):
    coords = {"a.jpg": (38.70, -120.50), "b.jpg": (38.72, -120.46)}
    monkeypatch.setattr(aoi, "image_gps", lambda p: coords.get(p))
    monkeypatch.setattr(aoi, "suggest_buffer_m", lambda *a, **k: 500.0)
    images = [{"path": p} for p in coords]
    est = aoi.estimate_download_aoi(images)
    assert est is not None
    padded, raw, buffer_m = est
    assert buffer_m == 500.0
    assert raw == pytest.approx((-120.50, 38.70, -120.46, 38.72))
    assert padded[0] < raw[0] and padded[2] > raw[2]


def test_estimate_none_without_gps(monkeypatch):
    monkeypatch.setattr(aoi, "image_gps", lambda p: None)
    assert aoi.estimate_download_aoi([{"path": "a.jpg"}]) is None


# --- image_gps error/fallback paths -----------------------------------------

def test_image_gps_none_when_path_empty():
    # Falsy paths short-circuit before any EXIF read.
    assert aoi.image_gps("") is None
    assert aoi.image_gps(None) is None


def test_image_gps_returns_lat_lon():
    with patch("helpers.MetaDataHelper.MetaDataHelper") as mdh, \
            patch("helpers.LocationInfo.LocationInfo") as loc:
        mdh.get_exif_data_piexif.return_value = {"fake": "exif"}
        loc.get_gps.return_value = {"latitude": 38.7, "longitude": -120.5}
        assert aoi.image_gps("a.jpg") == (38.7, -120.5)
    loc.get_gps.assert_called_once()


def test_image_gps_none_when_gps_missing():
    # EXIF reads fine but no GPS block -> None.
    with patch("helpers.MetaDataHelper.MetaDataHelper") as mdh, \
            patch("helpers.LocationInfo.LocationInfo") as loc:
        mdh.get_exif_data_piexif.return_value = {"fake": "exif"}
        loc.get_gps.return_value = None
        assert aoi.image_gps("a.jpg") is None


def test_image_gps_none_when_exif_read_raises():
    # Any exception during the EXIF read is swallowed -> None.
    with patch("helpers.MetaDataHelper.MetaDataHelper") as mdh, \
            patch("helpers.LocationInfo.LocationInfo") as loc:
        mdh.get_exif_data_piexif.side_effect = RuntimeError("bad exif")
        assert aoi.image_gps("a.jpg") is None
        loc.get_gps.assert_not_called()


# --- _frame_geometry error/fallback paths -----------------------------------

def test_frame_geometry_returns_geometry():
    sentinel = object()
    with patch("core.services.image.ImageService.ImageService") as IS:
        IS.return_value.get_frame_geometry.return_value = sentinel
        assert aoi._frame_geometry("a.jpg") is sentinel


def test_frame_geometry_none_when_imageservice_raises():
    # Construction failure is swallowed -> None.
    with patch("core.services.image.ImageService.ImageService") as IS:
        IS.side_effect = RuntimeError("cannot open image")
        assert aoi._frame_geometry("a.jpg") is None


def test_frame_geometry_none_when_get_frame_geometry_raises():
    # Geometry extraction failure is swallowed -> None.
    with patch("core.services.image.ImageService.ImageService") as IS:
        IS.return_value.get_frame_geometry.side_effect = RuntimeError("no pose")
        assert aoi._frame_geometry("a.jpg") is None


# --- suggest_buffer_m error/fallback paths ----------------------------------

def test_suggest_buffer_default_when_no_images():
    assert aoi.suggest_buffer_m([]) == pytest.approx(aoi._DEFAULT_BUFFER_M)


def test_suggest_buffer_default_when_all_paths_blank():
    # Images present but every path resolves to empty -> default buffer.
    assert aoi.suggest_buffer_m([{"path": ""}, {"other": "x"}]) == \
        pytest.approx(aoi._DEFAULT_BUFFER_M)


def test_suggest_buffer_default_when_projection_error(monkeypatch):
    # Geometry resolves, but the footprint projection raises for every sample
    # -> no reaches collected -> default buffer.
    monkeypatch.setattr(aoi, "_frame_geometry", lambda p: object())
    with patch("core.services.coverage.kernel.project_footprint_corners",
               side_effect=RuntimeError("projection failed")):
        buf = aoi.suggest_buffer_m([{"path": "a.jpg"}], params=PodParams())
    assert buf == pytest.approx(aoi._DEFAULT_BUFFER_M)


def test_suggest_buffer_floors_at_min(monkeypatch):
    # Tiny footprint reach floors up to _MIN_BUFFER_M (a 50 m multiple).
    monkeypatch.setattr(aoi, "_frame_geometry", lambda p: object())
    with patch("core.services.coverage.kernel.project_footprint_corners",
               return_value=[(10.0, 10.0)]):
        buf = aoi.suggest_buffer_m([{"path": "a.jpg"}], params=PodParams())
    assert buf == pytest.approx(aoi._MIN_BUFFER_M)


def test_suggest_buffer_rounds_up_to_50_step(monkeypatch):
    # Reach of 120 m rounds up to the next tidy 50 m step -> 150 m.
    monkeypatch.setattr(aoi, "_frame_geometry", lambda p: object())
    with patch("core.services.coverage.kernel.project_footprint_corners",
               return_value=[(120.0, 0.0)]):
        buf = aoi.suggest_buffer_m([{"path": "a.jpg"}], params=PodParams())
    assert buf == pytest.approx(150.0)
    assert buf % 50.0 == 0
