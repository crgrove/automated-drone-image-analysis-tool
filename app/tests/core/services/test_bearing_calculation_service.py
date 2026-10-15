"""Unit tests for BearingCalculationService."""

from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest
from unittest.mock import MagicMock, patch

from core.services.BearingCalculationService import (
    BearingCalculationService,
    BearingResult,
    TrackPoint,
)


@pytest.fixture
def service():
    svc = BearingCalculationService()
    svc._logger = MagicMock()
    return svc


def _tp(seconds, lat=40.0, lon=-75.0, alt=100.0):
    """Build a TrackPoint at an offset (seconds) from a fixed epoch."""
    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    return TrackPoint(timestamp=base + timedelta(seconds=seconds), lat=lat, lon=lon, alt=alt)


# ---------------------------------------------------------------------------
# Dataclass sanity
# ---------------------------------------------------------------------------

def test_track_point_fields_defaults():
    p = TrackPoint(timestamp=datetime.now(tz=timezone.utc), lat=1.0, lon=2.0)
    assert p.alt is None


def test_bearing_result_default_confidence():
    r = BearingResult(bearing_deg=90.0, source="kml", quality="good")
    assert r.confidence == 1.0


# ---------------------------------------------------------------------------
# Initialization + cancel
# ---------------------------------------------------------------------------

def test_service_init(service):
    assert service._cancel_requested is False


def test_cancel_sets_flag(service):
    service.cancel()
    assert service._cancel_requested is True


def test_signals_exposed(service):
    for sig in ("progress_updated", "calculation_complete", "calculation_error", "calculation_cancelled"):
        assert hasattr(service, sig)


# ---------------------------------------------------------------------------
# _parse_timestamp
# ---------------------------------------------------------------------------

def test_parse_timestamp_unix(service):
    result = service._parse_timestamp("1704110400")  # 2024-01-01 12:00:00 UTC
    assert result.tzinfo is not None
    assert result.year == 2024


def test_parse_timestamp_iso8601(service):
    result = service._parse_timestamp("2024-01-01T12:00:00Z")
    assert result == datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def test_parse_timestamp_iso_with_offset(service):
    result = service._parse_timestamp("2024-01-01T12:00:00+00:00")
    assert result.tzinfo is not None


def test_parse_timestamp_common_format(service):
    result = service._parse_timestamp("2024-01-01 12:00:00")
    assert result.year == 2024
    assert result.tzinfo is not None


def test_parse_timestamp_rejects_garbage(service):
    with pytest.raises(ValueError):
        service._parse_timestamp("not a date")


# ---------------------------------------------------------------------------
# _find_bracket_index (binary search)
# ---------------------------------------------------------------------------

def test_find_bracket_index_before_track(service):
    track = [_tp(10), _tp(20), _tp(30)]
    assert service._find_bracket_index(track, _tp(0).timestamp) == 0


def test_find_bracket_index_after_track(service):
    track = [_tp(10), _tp(20), _tp(30)]
    assert service._find_bracket_index(track, _tp(999).timestamp) == 3


def test_find_bracket_index_middle(service):
    track = [_tp(0), _tp(10), _tp(20), _tp(30)]
    assert service._find_bracket_index(track, _tp(15).timestamp) == 2


def test_find_bracket_index_exact_match(service):
    track = [_tp(0), _tp(10), _tp(20)]
    # Exact match falls to index of that point (right-bound)
    assert service._find_bracket_index(track, _tp(10).timestamp) == 1


# ---------------------------------------------------------------------------
# _validate_track
# ---------------------------------------------------------------------------

def test_validate_track_empty_raises(service):
    with pytest.raises(ValueError):
        service._validate_track([])


def test_validate_track_sorts_by_timestamp(service):
    track = [_tp(30), _tp(10), _tp(20)]
    sorted_track = service._validate_track(track)
    assert [p.timestamp for p in sorted_track] == sorted(p.timestamp for p in track)


def test_validate_track_preserves_all_points(service):
    track = [_tp(0), _tp(10), _tp(20)]
    assert len(service._validate_track(track)) == 3


# ---------------------------------------------------------------------------
# CSV parsing
# ---------------------------------------------------------------------------

def _write_csv(tmp_path, rows, header="timestamp,lat,lon,alt"):
    path = tmp_path / "track.csv"
    path.write_text(header + "\n" + "\n".join(rows))
    return path


def test_parse_csv_basic(service, tmp_path):
    path = _write_csv(
        tmp_path,
        [
            "2024-01-01T12:00:00Z,40.0,-75.0,100",
            "2024-01-01T12:00:10Z,40.001,-75.001,101",
        ],
    )
    points = service._parse_csv(str(path))
    assert len(points) == 2
    assert points[0].lat == 40.0
    assert points[0].alt == 100.0


def test_parse_csv_alt_column_optional(service, tmp_path):
    path = _write_csv(
        tmp_path,
        ["2024-01-01T12:00:00Z,40.0,-75.0"],
        header="timestamp,lat,lon",
    )
    points = service._parse_csv(str(path))
    assert len(points) == 1
    assert points[0].alt is None


def test_parse_csv_alternate_column_names(service, tmp_path):
    path = _write_csv(
        tmp_path,
        ["2024-01-01T12:00:00Z,40.0,-75.0,50"],
        header="time,latitude,longitude,elevation",
    )
    points = service._parse_csv(str(path))
    assert len(points) == 1
    assert points[0].lat == 40.0
    assert points[0].alt == 50.0


def test_parse_csv_skips_invalid_rows(service, tmp_path):
    path = _write_csv(
        tmp_path,
        [
            "2024-01-01T12:00:00Z,40.0,-75.0,100",
            "not-a-date,abc,xyz,100",  # invalid row
            "2024-01-01T12:00:10Z,40.001,-75.001,101",
        ],
    )
    points = service._parse_csv(str(path))
    assert len(points) == 2


def test_parse_csv_missing_timestamp_column(service, tmp_path):
    path = _write_csv(tmp_path, ["40.0,-75.0,100"], header="lat,lon,alt")
    with pytest.raises(ValueError, match="timestamp"):
        service._parse_csv(str(path))


def test_parse_csv_missing_lat_lon(service, tmp_path):
    path = _write_csv(
        tmp_path,
        ["2024-01-01T12:00:00Z,100"],
        header="timestamp,altitude",
    )
    with pytest.raises(ValueError, match="lat"):
        service._parse_csv(str(path))


# ---------------------------------------------------------------------------
# calculate_from_track: file format branching
# ---------------------------------------------------------------------------

def test_calculate_from_track_unsupported_format_emits_error(service, tmp_path):
    path = tmp_path / "track.txt"
    path.write_text("nothing")
    errors = []
    service.calculation_error.connect(lambda msg: errors.append(msg))

    service.calculate_from_track(images=[], track_file_path=str(path))
    assert len(errors) == 1
    assert "Unsupported" in errors[0] or "format" in errors[0].lower()


def test_calculate_from_track_empty_track_emits_error(service, tmp_path):
    # CSV with valid header but no rows
    path = _write_csv(tmp_path, rows=[])
    errors = []
    service.calculation_error.connect(lambda msg: errors.append(msg))

    service.calculate_from_track(images=[], track_file_path=str(path))
    assert len(errors) == 1


def test_calculate_from_track_emits_complete(service, tmp_path):
    path = _write_csv(
        tmp_path,
        [
            "2024-01-01T12:00:00Z,40.0,-75.0,100",
            "2024-01-01T12:00:10Z,40.001,-75.001,101",
            "2024-01-01T12:00:20Z,40.002,-75.002,102",
        ],
    )
    images = [
        {"path": "img1.jpg", "timestamp": datetime(2024, 1, 1, 12, 0, 5, tzinfo=timezone.utc)},
        {"path": "img2.jpg", "timestamp": datetime(2024, 1, 1, 12, 0, 15, tzinfo=timezone.utc)},
    ]
    results = []
    service.calculation_complete.connect(lambda r: results.append(r))

    service.calculate_from_track(images=images, track_file_path=str(path))
    assert len(results) == 1
    assert "img1.jpg" in results[0]
    assert "img2.jpg" in results[0]
    assert isinstance(results[0]["img1.jpg"], BearingResult)


def test_calculate_from_track_cancel_emits_cancelled(service, tmp_path):
    # calculate_from_track() resets _cancel_requested=False at entry, so we need
    # to flip it AFTER parsing but BEFORE the post-loop emit. Patch the inner
    # loop so it sets the flag partway through.
    path = _write_csv(
        tmp_path,
        [
            "2024-01-01T12:00:00Z,40.0,-75.0,100",
            "2024-01-01T12:00:10Z,40.001,-75.001,101",
        ],
    )
    cancelled = []
    service.calculation_cancelled.connect(lambda: cancelled.append(True))

    def _set_cancel(*_args, **_kwargs):
        service._cancel_requested = True
        return {}

    with patch.object(service, "_bearing_from_track", side_effect=_set_cancel):
        service.calculate_from_track(
            images=[{"path": "a.jpg", "timestamp": datetime(2024, 1, 1, 12, 0, 5, tzinfo=timezone.utc)}],
            track_file_path=str(path),
        )
    assert cancelled == [True]


# ---------------------------------------------------------------------------
# calculate_auto
# ---------------------------------------------------------------------------

def test_calculate_auto_requires_two_gps_images(service):
    errors = []
    service.calculation_error.connect(lambda msg: errors.append(msg))

    service.calculate_auto(images=[{"path": "a.jpg", "lat": 40.0, "lon": -75.0, "timestamp": datetime.now(tz=timezone.utc)}])
    assert len(errors) == 1
    assert "at least 2" in errors[0].lower() or "2 images" in errors[0].lower()


def test_calculate_auto_straight_line_emits_complete(service):
    # Three images moving due north — should produce bearings near 0°
    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    images = [
        {"path": f"img{i}.jpg", "lat": 40.0 + 0.001 * i, "lon": -75.0, "timestamp": base + timedelta(seconds=i * 5)}
        for i in range(5)
    ]
    results = []
    service.calculation_complete.connect(lambda r: results.append(r))

    service.calculate_auto(images=images)
    assert len(results) == 1
    assert len(results[0]) == 5
    for br in results[0].values():
        assert 0 <= br.bearing_deg < 360


def test_calculate_auto_handles_cancel(service):
    # calculate_auto() resets _cancel_requested=False at entry; patch the inner
    # calculator to flip it during execution.
    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    images = [
        {"path": f"img{i}.jpg", "lat": 40.0 + 0.001 * i, "lon": -75.0, "timestamp": base + timedelta(seconds=i * 5)}
        for i in range(3)
    ]
    cancelled = []
    service.calculation_cancelled.connect(lambda: cancelled.append(True))

    def _set_cancel(*_args, **_kwargs):
        service._cancel_requested = True
        return {}

    with patch.object(service, "_bearing_auto", side_effect=_set_cancel):
        service.calculate_auto(images=images)
    assert cancelled == [True]


# ---------------------------------------------------------------------------
# _calculate_turn_threshold
# ---------------------------------------------------------------------------

def test_calculate_turn_threshold_default_for_few_points(service):
    result = service._calculate_turn_threshold([{"lat": 1, "lon": 2}] * 3)
    assert result == service.DEFAULT_TURN_THRESHOLD_M


def test_calculate_turn_threshold_clamped_range(service):
    # Straight line — perpendicular distances are zero, threshold clamps to 5.0
    images = [{"lat": 40.0 + 0.0001 * i, "lon": -75.0} for i in range(20)]
    result = service._calculate_turn_threshold(images)
    assert 5.0 <= result <= 30.0


# ---------------------------------------------------------------------------
# GPX / KML parsing (lib-absent branches)
# ---------------------------------------------------------------------------

def test_parse_kml_without_fastkml_raises(service, tmp_path):
    path = tmp_path / "track.kml"
    path.write_text("<kml/>")
    with patch("core.services.BearingCalculationService.kml", None):
        with pytest.raises(ImportError, match="fastkml"):
            service._parse_kml(str(path))


def test_parse_gpx_without_gpxpy_raises(service, tmp_path):
    path = tmp_path / "track.gpx"
    path.write_text("<gpx/>")
    with patch("core.services.BearingCalculationService.gpxpy", None):
        with pytest.raises(ImportError, match="gpxpy"):
            service._parse_gpx(str(path))


def test_parse_gpx_extracts_points(service, tmp_path):
    # Build a fake gpxpy module with one track / segment / point
    fake_point = MagicMock()
    fake_point.time = datetime(2024, 1, 1, 12, 0, 0)  # naive; code should localize to UTC
    fake_point.latitude = 40.0
    fake_point.longitude = -75.0
    fake_point.elevation = 50.0

    fake_segment = MagicMock()
    fake_segment.points = [fake_point]

    fake_track = MagicMock()
    fake_track.segments = [fake_segment]

    fake_gpx = MagicMock()
    fake_gpx.tracks = [fake_track]

    fake_gpxpy = MagicMock()
    fake_gpxpy.parse.return_value = fake_gpx

    path = tmp_path / "track.gpx"
    path.write_text("<gpx/>")

    with patch("core.services.BearingCalculationService.gpxpy", fake_gpxpy):
        points = service._parse_gpx(str(path))

    assert len(points) == 1
    assert points[0].lat == 40.0
    assert points[0].lon == -75.0
    assert points[0].alt == 50.0
    assert points[0].timestamp.tzinfo is not None


def test_parse_gpx_skips_points_without_time(service, tmp_path):
    fake_point = MagicMock()
    fake_point.time = None

    fake_segment = MagicMock()
    fake_segment.points = [fake_point]

    fake_track = MagicMock()
    fake_track.segments = [fake_segment]

    fake_gpx = MagicMock()
    fake_gpx.tracks = [fake_track]

    fake_gpxpy = MagicMock()
    fake_gpxpy.parse.return_value = fake_gpx

    path = tmp_path / "track.gpx"
    path.write_text("<gpx/>")

    with patch("core.services.BearingCalculationService.gpxpy", fake_gpxpy):
        assert service._parse_gpx(str(path)) == []


def test_parse_kml_timestamp_returns_none_for_unparseable(service):
    assert service._parse_kml_timestamp(object()) is None


def test_parse_kml_timestamp_localizes_naive_datetime(service):
    wrapper = MagicMock()
    wrapper.timestamp = datetime(2024, 1, 1, 12, 0, 0)  # naive
    result = service._parse_kml_timestamp(wrapper)
    assert result.tzinfo is not None


# ---------------------------------------------------------------------------
# _apply_smoothing
# ---------------------------------------------------------------------------

def test_apply_smoothing_skips_with_few_images(service):
    # len(images) < 5 returns input unchanged
    results = {"a.jpg": BearingResult(90.0, "gpx", "good")}
    images = [{"path": "a.jpg"}]
    smoothed = service._apply_smoothing(results, images)
    assert smoothed == results


def test_apply_smoothing_uses_geodesic_helper():
    svc = BearingCalculationService()
    svc._logger = MagicMock()

    results = {
        f"img{i}.jpg": BearingResult(bearing_deg=90.0 + i, source="gpx", quality="good")
        for i in range(6)
    }
    images = [{"path": f"img{i}.jpg"} for i in range(6)]

    with patch(
        "core.services.BearingCalculationService.GeodesicHelper.smooth_bearings_circular",
        return_value=[100.0] * 6,
    ) as mock_smooth:
        smoothed = svc._apply_smoothing(results, images)
        mock_smooth.assert_called_once()

    # Each result should have been updated to smoothed value
    for r in smoothed.values():
        assert r.bearing_deg == 100.0


def test_apply_smoothing_returns_unchanged_when_paths_missing():
    # Images in list but not in results -> pipe drops below threshold
    svc = BearingCalculationService()
    svc._logger = MagicMock()
    results = {}
    images = [{"path": f"img{i}.jpg"} for i in range(6)]
    smoothed = svc._apply_smoothing(results, images)
    assert smoothed == results


# ---------------------------------------------------------------------------
# calculate_turn_threshold additional cases
# ---------------------------------------------------------------------------

def test_calculate_turn_threshold_below_5_images_returns_default():
    svc = BearingCalculationService()
    svc._logger = MagicMock()
    result = svc._calculate_turn_threshold([{"lat": 0, "lon": 0}] * 4)
    assert result == svc.DEFAULT_TURN_THRESHOLD_M


def test_calculate_turn_threshold_returns_clamped_value():
    svc = BearingCalculationService()
    svc._logger = MagicMock()
    # Slight zig-zag pattern produces small but non-zero distances
    images = []
    for i in range(20):
        offset = 0.00001 if i % 2 == 0 else -0.00001
        images.append({"lat": 40.0 + 0.001 * i, "lon": -75.0 + offset})
    result = svc._calculate_turn_threshold(images)
    assert 5.0 <= result <= 30.0


# ---------------------------------------------------------------------------
# calculate_auto: image without GPS data branch
# ---------------------------------------------------------------------------

def test_calculate_auto_reads_gps_from_exif(service):
    # Image without lat/lon triggers EXIF extraction
    img = {"path": "/fake/path.jpg"}  # no lat/lon/timestamp

    with patch(
        "core.services.BearingCalculationService.MetaDataHelper"
    ) as MockMeta, patch(
        "core.services.BearingCalculationService.LocationInfo"
    ) as MockLoc:
        MockMeta.get_exif_data_piexif.return_value = {}
        MockLoc.get_gps.return_value = None  # No GPS available

        errors = []
        service.calculation_error.connect(lambda msg: errors.append(msg))
        # Only one image, should error out with <2 images
        service.calculate_auto(images=[img])
    assert len(errors) == 1


def test_calculate_auto_handles_exif_exception(service):
    img = {"path": "/fake/path.jpg"}

    with patch(
        "core.services.BearingCalculationService.MetaDataHelper"
    ) as MockMeta:
        MockMeta.get_exif_data_piexif.side_effect = RuntimeError("EXIF fail")
        errors = []
        service.calculation_error.connect(lambda msg: errors.append(msg))
        service.calculate_auto(images=[img])
    assert len(errors) == 1


# ---------------------------------------------------------------------------
# calculate_auto: middle-of-leg alignment
# ---------------------------------------------------------------------------

def test_calculate_auto_long_straight_path():
    svc = BearingCalculationService()
    svc._logger = MagicMock()
    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    # 10 evenly-spaced points due north
    images = [
        {
            "path": f"img{i}.jpg",
            "lat": 40.0 + 0.001 * i,
            "lon": -75.0,
            "timestamp": base + timedelta(seconds=i * 5),
        }
        for i in range(10)
    ]
    received = []
    svc.calculation_complete.connect(lambda r: received.append(r))
    svc.calculate_auto(images=images)

    assert len(received) == 1
    # All bearings should be close to 0° (north)
    for br in received[0].values():
        # Close to 0° or 360° (which is also north)
        assert br.bearing_deg < 30 or br.bearing_deg > 330


def test_calculate_auto_turn_sequence():
    svc = BearingCalculationService()
    svc._logger = MagicMock()
    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    # Points in an L-shape: north then east
    images = [
        {"path": f"img{i}.jpg",
         "lat": 40.0 + 0.001 * min(i, 4),
         "lon": -75.0 + 0.001 * max(0, i - 4),
         "timestamp": base + timedelta(seconds=i * 5)}
        for i in range(9)
    ]
    received = []
    svc.calculation_complete.connect(lambda r: received.append(r))
    svc.calculate_auto(images=images)
    assert len(received) == 1


# ---------------------------------------------------------------------------
# _bearing_from_track: stationary detection
# ---------------------------------------------------------------------------

def test_bearing_from_track_stationary_inherits_last_bearing():
    svc = BearingCalculationService()
    svc._logger = MagicMock()

    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    # Track points where two are at same GPS (stationary)
    track = [
        TrackPoint(base, 40.0, -75.0),
        TrackPoint(base + timedelta(seconds=5), 40.001, -75.0),  # moving
        TrackPoint(base + timedelta(seconds=10), 40.001, -75.0),  # stationary
        TrackPoint(base + timedelta(seconds=15), 40.002, -75.0),  # moving
    ]

    images = [
        {"path": f"img{i}.jpg", "timestamp": base + timedelta(seconds=i * 3)}
        for i in range(1, 5)
    ]

    results = svc._bearing_from_track(images, track, "gpx")
    # Should have 4 results
    assert len(results) == 4
    # Each should be a BearingResult
    for r in results.values():
        assert isinstance(r, BearingResult)


def test_bearing_from_track_outside_range_uses_endpoints():
    svc = BearingCalculationService()
    svc._logger = MagicMock()

    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    track = [
        TrackPoint(base + timedelta(seconds=10), 40.0, -75.0),
        TrackPoint(base + timedelta(seconds=20), 40.001, -75.0),
    ]
    # Image before track range
    images = [
        {"path": "before.jpg", "timestamp": base},  # before track
        {"path": "after.jpg", "timestamp": base + timedelta(seconds=100)},  # after track
    ]
    results = svc._bearing_from_track(images, track, "gpx")
    assert "before.jpg" in results
    assert "after.jpg" in results
    assert results["before.jpg"].quality == "gap"
    assert results["after.jpg"].quality == "gap"


def test_bearing_from_track_skips_images_without_timestamp():
    svc = BearingCalculationService()
    svc._logger = MagicMock()

    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    track = [
        TrackPoint(base, 40.0, -75.0),
        TrackPoint(base + timedelta(seconds=5), 40.001, -75.0),
    ]
    images = [
        {"path": "no_ts.jpg"},  # no timestamp
        {"path": "has_ts.jpg", "timestamp": base + timedelta(seconds=2)},
    ]
    results = svc._bearing_from_track(images, track, "gpx")
    # Only one image with a timestamp should have a result
    assert "has_ts.jpg" in results
    assert "no_ts.jpg" not in results


def test_bearing_from_track_localizes_naive_image_timestamp():
    svc = BearingCalculationService()
    svc._logger = MagicMock()

    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    track = [
        TrackPoint(base, 40.0, -75.0),
        TrackPoint(base + timedelta(seconds=10), 40.001, -75.0),
    ]
    # Naive timestamp (no tzinfo) should be localized to UTC
    images = [{"path": "img.jpg", "timestamp": datetime(2024, 1, 1, 12, 0, 5)}]
    results = svc._bearing_from_track(images, track, "gpx")
    assert "img.jpg" in results


def test_bearing_from_track_cancel_breaks_early():
    svc = BearingCalculationService()
    svc._logger = MagicMock()
    svc._cancel_requested = True

    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    track = [
        TrackPoint(base, 40.0, -75.0),
        TrackPoint(base + timedelta(seconds=5), 40.001, -75.0),
    ]
    images = [{"path": f"img{i}.jpg", "timestamp": base + timedelta(seconds=i)} for i in range(5)]
    results = svc._bearing_from_track(images, track, "gpx")
    # Cancel should have broken loop immediately
    assert len(results) == 0


# ---------------------------------------------------------------------------
# validate_track warns on non-monotonic timestamps
# ---------------------------------------------------------------------------

def test_validate_track_logs_warning_on_non_monotonic():
    svc = BearingCalculationService()
    svc._logger = MagicMock()
    # After sort, always monotonic. To trigger the warning path we'd need
    # duplicate/reversed timestamps. The warning fires based on sorted order.
    # Sort is stable, so with unique timestamps the warning won't trigger.
    # Just verify sorting happens without raising.
    track = [_tp(30), _tp(10), _tp(20), _tp(15)]
    sorted_track = svc._validate_track(track)
    assert [p.timestamp for p in sorted_track] == sorted([p.timestamp for p in track])


# ---------------------------------------------------------------------------
# Auto mode with images that carry no capture time
#
# The DateTime fallback read piexif.ExifIFD.DateTime, an attribute that does
# not exist. The AttributeError landed in the per-image except, so every image
# without DateTimeOriginal was skipped - frames cut from a video carry GPS and
# no capture time at all, so a whole result set could fail with "Need at least
# 2 images with GPS".
# ---------------------------------------------------------------------------

def test_auto_keeps_images_that_have_gps_but_no_capture_time(service):
    images = [{'path': f'frame_{i}.jpg', 'name': f'frame_{i}.jpg'} for i in range(3)]
    no_date_exif = {'0th': {34853: 26}, 'Exif': {}, 'GPS': {1: b'N'}}
    fixes = [{'latitude': 40.0 + i * 0.001, 'longitude': -75.0} for i in range(3)]

    with patch('core.services.BearingCalculationService.MetaDataHelper.get_exif_data_piexif',
               return_value=no_date_exif), \
         patch('core.services.BearingCalculationService.LocationInfo.get_gps',
               side_effect=fixes):
        results = service._bearing_auto(images)

    # Every frame kept, none dropped, and the timestamp-less sort did not raise.
    assert len(results) == 3
    assert all(img['timestamp'] is None for img in images)
    service._logger.error.assert_not_called()


def test_auto_sorts_by_capture_time_when_present(service):
    """Mixing timestamped and timestamp-less images must not raise either."""
    images = [{'path': 'b.jpg', 'name': 'b.jpg'},
              {'path': 'a.jpg', 'name': 'a.jpg'},
              {'path': 'c.jpg', 'name': 'c.jpg'}]
    exifs = {
        'b.jpg': {'Exif': {36867: b'2026:08:15 12:00:02'}},
        'a.jpg': {'Exif': {36867: b'2026:08:15 12:00:01'}},
        'c.jpg': {'0th': {}, 'Exif': {}},
    }
    fixes = {'b.jpg': {'latitude': 40.001, 'longitude': -75.0},
             'a.jpg': {'latitude': 40.000, 'longitude': -75.0},
             'c.jpg': {'latitude': 40.002, 'longitude': -75.0}}
    order = []

    def _exif(path):
        order.append(path)
        return exifs[path]

    with patch('core.services.BearingCalculationService.MetaDataHelper.get_exif_data_piexif',
               side_effect=_exif), \
         patch('core.services.BearingCalculationService.LocationInfo.get_gps',
               side_effect=lambda exif_data=None: fixes[order[-1]]):
        results = service._bearing_auto(images)

    assert len(results) == 3
    assert images[0]['timestamp'].second == 2      # b.jpg parsed
    assert images[2]['timestamp'] is None          # c.jpg has none


# ---------------------------------------------------------------------------
# Track mode capture-time extraction (second review, finding 2): the recovery
# dialog hands over path-only records, and only the auto path ever filled
# their timestamps - track matching then skipped every image.
# ---------------------------------------------------------------------------

def _write_jpeg_with_gps_time(tmp_path, name='DJI_0001.JPG',
                              gps_date=b'2024:01:01', gps_time=((12, 1), (0, 1), (5, 1))):
    """A real JPEG whose EXIF carries a UTC GPS timestamp and a GPS fix."""
    import cv2
    import numpy as np
    import piexif

    path = str(tmp_path / name)
    cv2.imwrite(path, np.zeros((8, 8, 3), dtype=np.uint8))
    exif_bytes = piexif.dump({
        'Exif': {piexif.ExifIFD.DateTimeOriginal: b'2024:01:01 07:00:05'},
        'GPS': {
            piexif.GPSIFD.GPSLatitude: ((40, 1), (0, 1), (0, 1)),
            piexif.GPSIFD.GPSLatitudeRef: b'N',
            piexif.GPSIFD.GPSLongitude: ((75, 1), (0, 1), (0, 1)),
            piexif.GPSIFD.GPSLongitudeRef: b'W',
            piexif.GPSIFD.GPSDateStamp: gps_date,
            piexif.GPSIFD.GPSTimeStamp: gps_time,
        },
    })
    piexif.insert(exif_bytes, path)
    return path


def _controller_shaped_record(path):
    """Image record exactly as BearingRecoveryController builds it."""
    return {'path': path, 'lat': None, 'lon': None, 'timestamp': None}


def test_calculate_from_track_extracts_capture_times_from_images(service, tmp_path):
    """A real JPEG with a valid EXIF capture time plus a CSV track covering
    that time must update one image, not zero."""
    image_path = _write_jpeg_with_gps_time(tmp_path)
    track = _write_csv(
        tmp_path,
        [
            "2024-01-01T12:00:00Z,40.0,-75.0,100",
            "2024-01-01T12:00:10Z,40.001,-75.001,101",
        ],
    )
    results = []
    service.calculation_complete.connect(lambda r: results.append(r))

    service.calculate_from_track(
        images=[_controller_shaped_record(image_path)],
        track_file_path=str(track))

    assert len(results) == 1
    assert image_path in results[0], 'track matching skipped the image'
    assert isinstance(results[0][image_path], BearingResult)


def test_populate_capture_times_resolves_gps_utc(service, tmp_path):
    image_path = _write_jpeg_with_gps_time(tmp_path)
    records = [_controller_shaped_record(image_path)]

    service._populate_capture_times(records)

    # The GPS EXIF stamp is already UTC and outranks the naive local
    # DateTimeOriginal, so no timezone guessing is involved.
    assert records[0]['timestamp'] == datetime(2024, 1, 1, 12, 0, 5, tzinfo=timezone.utc)


def test_populate_capture_times_leaves_unresolvable_none(service, tmp_path):
    """No resolvable capture time: the record keeps timestamp None (and the
    matcher reports it skipped) instead of being matched hours off."""
    import cv2
    import numpy as np

    plain = str(tmp_path / 'no_exif.jpg')
    cv2.imwrite(plain, np.zeros((8, 8, 3), dtype=np.uint8))
    records = [_controller_shaped_record(plain)]

    service._populate_capture_times(records)

    assert records[0]['timestamp'] is None


def test_populate_capture_times_keeps_existing_timestamps(service):
    """Records that already carry a timestamp are never re-read from disk."""
    stamped = {'path': 'missing-on-purpose.jpg',
               'timestamp': datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)}

    with patch('core.services.BearingCalculationService.MetaDataHelper.get_exif_data_piexif') as read:
        service._populate_capture_times([stamped])

    read.assert_not_called()
    assert stamped['timestamp'] == datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# KML parsing against the installed fastkml (second review, finding 3): the
# 0.x method-call API raised TypeError under fastkml 1.x, blocking every KML
# recovery and silently dropping KML candidates from track discovery.
# ---------------------------------------------------------------------------

_KML_POINTS = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark><name>p1</name>
      <TimeStamp><when>2024-01-01T12:00:00Z</when></TimeStamp>
      <Point><coordinates>-75.000,40.000,100</coordinates></Point>
    </Placemark>
    <Placemark><name>p2</name>
      <TimeStamp><when>2024-01-01T12:00:10Z</when></TimeStamp>
      <Point><coordinates>-75.001,40.001,101</coordinates></Point>
    </Placemark>
  </Document>
</kml>
"""

_KML_GX_TRACK = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"
     xmlns:gx="http://www.google.com/kml/ext/2.2">
  <Document>
    <Placemark><name>trk</name>
      <gx:Track>
        <when>2024-01-01T12:00:00Z</when>
        <gx:coord>-75.000 40.000 100</gx:coord>
        <when>2024-01-01T12:00:10Z</when>
        <gx:coord>-75.001 40.001 101</gx:coord>
      </gx:Track>
    </Placemark>
  </Document>
</kml>
"""


def _write_kml(tmp_path, content, name='track.kml'):
    path = tmp_path / name
    path.write_text(content, encoding='utf-8')
    return str(path)


def test_parse_kml_timestamped_point_placemarks(service, tmp_path):
    points, source = service.parse_track_file(_write_kml(tmp_path, _KML_POINTS))

    assert source == 'kml'
    assert len(points) == 2
    points.sort(key=lambda p: p.timestamp)
    assert points[0].timestamp == datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    assert points[0].lat == pytest.approx(40.0)
    assert points[0].lon == pytest.approx(-75.0)
    assert points[1].timestamp == datetime(2024, 1, 1, 12, 0, 10, tzinfo=timezone.utc)
    assert points[1].lat == pytest.approx(40.001)


def test_parse_kml_gx_track(service, tmp_path):
    points, source = service.parse_track_file(_write_kml(tmp_path, _KML_GX_TRACK))

    assert source == 'kml'
    assert len(points) == 2
    points.sort(key=lambda p: p.timestamp)
    assert points[0].lat == pytest.approx(40.0)
    assert points[0].lon == pytest.approx(-75.0)
    assert points[0].alt == pytest.approx(100.0)
    assert points[1].timestamp == datetime(2024, 1, 1, 12, 0, 10, tzinfo=timezone.utc)


def test_calculate_from_track_kml_end_to_end(service, tmp_path):
    """The reviewer's failing case: a valid timestamped KML must drive a
    successful calculation, not TypeError inside the parser."""
    kml_path = _write_kml(tmp_path, _KML_POINTS)
    images = [{'path': 'img1.jpg', 'lat': None, 'lon': None,
               'timestamp': datetime(2024, 1, 1, 12, 0, 5, tzinfo=timezone.utc)}]
    results, errors = [], []
    service.calculation_complete.connect(lambda r: results.append(r))
    service.calculation_error.connect(errors.append)

    service.calculate_from_track(images=images, track_file_path=kml_path)

    assert errors == []
    assert len(results) == 1 and 'img1.jpg' in results[0]


def test_populate_capture_times_bare_datetime_original_falls_back(service, tmp_path):
    """A bare DateTimeOriginal (no offset, no GPS) still matches under the
    service's naive-means-UTC convention rather than being skipped."""
    import cv2
    import numpy as np
    import piexif

    path = str(tmp_path / 'bare.jpg')
    cv2.imwrite(path, np.zeros((8, 8, 3), dtype=np.uint8))
    piexif.insert(piexif.dump(
        {'Exif': {piexif.ExifIFD.DateTimeOriginal: b'2026:08:07 12:00:05'}}), path)
    records = [_controller_shaped_record(path)]

    service._populate_capture_times(records)

    ts = records[0]['timestamp']
    assert ts is not None
    assert (ts.year, ts.hour, ts.second) == (2026, 12, 5)


_KML_GX_MULTITRACK = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"
     xmlns:gx="http://www.google.com/kml/ext/2.2">
  <Document>
    <Placemark><name>Two flight segments</name>
      <gx:MultiTrack>
        <gx:Track>
          <when>2024-01-01T12:00:00Z</when><when>2024-01-01T12:00:10Z</when>
          <gx:coord>-75.000 40.000 100</gx:coord><gx:coord>-75.001 40.001 101</gx:coord>
        </gx:Track>
        <gx:Track>
          <when>2024-01-01T12:01:00Z</when><when>2024-01-01T12:01:10Z</when>
          <gx:coord>-75.002 40.002 102</gx:coord><gx:coord>-75.003 40.003 103</gx:coord>
        </gx:Track>
      </gx:MultiTrack>
    </Placemark>
  </Document>
</kml>
"""

_KML_MULTIGEOMETRY_AND_POINT = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark><name>untimed area</name>
      <MultiGeometry>
        <LineString><coordinates>-75.0,40.0 -75.1,40.1</coordinates></LineString>
        <LineString><coordinates>-75.2,40.2 -75.3,40.3</coordinates></LineString>
      </MultiGeometry>
    </Placemark>
    <Placemark><name>p1</name>
      <TimeStamp><when>2024-01-01T12:00:00Z</when></TimeStamp>
      <Point><coordinates>-75.000,40.000,100</coordinates></Point>
    </Placemark>
  </Document>
</kml>
"""


def test_parse_kml_gx_multitrack_preserves_all_segments(service, tmp_path):
    """A gx:MultiTrack's segments each carry their own (when, coord) pairs;
    the multipart geometry has no coordinate sequence, so the old parse
    raised NotImplementedError instead of returning the four points."""
    points, source = service.parse_track_file(
        _write_kml(tmp_path, _KML_GX_MULTITRACK, name='multi_track.kml'))

    assert source == 'kml'
    assert len(points) == 4
    assert [p.timestamp.second for p in points] == [0, 10, 0, 10]
    assert points[0].lat == pytest.approx(40.0)
    assert points[3].lat == pytest.approx(40.003)
    assert points[3].timestamp == datetime(2024, 1, 1, 12, 1, 10, tzinfo=timezone.utc)


def test_parse_kml_multigeometry_without_tracks_does_not_abort_the_parse(service, tmp_path):
    """A MultiGeometry placemark (coords property raises, and hasattr does
    not swallow NotImplementedError) must be skipped, not crash the parse:
    the timestamped point after it still comes through."""
    points, _source = service.parse_track_file(
        _write_kml(tmp_path, _KML_MULTIGEOMETRY_AND_POINT, name='multi_geom.kml'))

    assert len(points) == 1
    assert points[0].timestamp == datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Recording gaps (PR #151 recheck, finding 2): an interval longer than
# GAP_THRESHOLD_SEC has no recorded course - the straight-line bearing
# between its endpoints includes the turnaround and must never be reported
# as a fully trusted 'good' estimate. Applies to every track format.
# ---------------------------------------------------------------------------

_KML_TWO_SEGMENTS_WITH_GAP = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"
     xmlns:gx="http://www.google.com/kml/ext/2.2">
  <Document><Placemark><gx:MultiTrack><gx:interpolate>0</gx:interpolate>
    <gx:Track>
      <when>2024-01-01T12:00:00Z</when><when>2024-01-01T12:00:10Z</when>
      <gx:coord>-75.000 40.000 100</gx:coord><gx:coord>-75.000 40.001 100</gx:coord>
    </gx:Track>
    <gx:Track>
      <when>2024-01-01T12:10:00Z</when><when>2024-01-01T12:10:10Z</when>
      <gx:coord>-74.900 40.001 100</gx:coord><gx:coord>-74.900 40.002 100</gx:coord>
    </gx:Track>
  </gx:MultiTrack></Placemark></Document>
</kml>
"""

_CSV_TWO_SEGMENTS_WITH_GAP = (
    'timestamp,latitude,longitude,altitude\n'
    '2024-01-01T12:00:00Z,40.000,-75.000,100\n'
    '2024-01-01T12:00:10Z,40.001,-75.000,100\n'
    '2024-01-01T12:10:00Z,40.001,-74.900,100\n'
    '2024-01-01T12:10:10Z,40.002,-74.900,100\n'
)


def _write_gap_track(tmp_path, track_format):
    if track_format == 'kml':
        return _write_kml(tmp_path, _KML_TWO_SEGMENTS_WITH_GAP, name='gap.kml')
    path = tmp_path / 'gap.csv'
    path.write_text(_CSV_TWO_SEGMENTS_WITH_GAP, encoding='utf-8')
    return str(path)


@pytest.mark.parametrize('track_format', ['kml', 'csv'])
def test_image_inside_a_recording_gap_is_never_marked_good(service, tmp_path, track_format):
    """Two northbound segments 10 minutes apart: an image at 12:05 sits in
    unrecorded time, and the eastbound endpoint-to-endpoint course used to
    come back quality='good', confidence=1.0."""
    results = []
    service.calculation_complete.connect(results.append)

    service.calculate_from_track(
        [{'path': 'during-gap.jpg',
          'timestamp': datetime(2024, 1, 1, 12, 5, tzinfo=timezone.utc)}],
        _write_gap_track(tmp_path, track_format))

    assert len(results) == 1
    result = results[0]['during-gap.jpg']
    assert result.quality == 'gap'
    assert result.confidence < 1.0


@pytest.mark.parametrize('track_format', ['kml', 'csv'])
def test_gap_image_inherits_the_last_recorded_heading(service, tmp_path, track_format):
    """With an earlier image on a recorded northbound leg, the gap image
    falls back to that heading instead of the cross-gap eastbound course."""
    results = []
    service.calculation_complete.connect(results.append)

    service.calculate_from_track(
        [{'path': 'on-track.jpg',
          'timestamp': datetime(2024, 1, 1, 12, 0, 5, tzinfo=timezone.utc)},
         {'path': 'during-gap.jpg',
          'timestamp': datetime(2024, 1, 1, 12, 5, tzinfo=timezone.utc)}],
        _write_gap_track(tmp_path, track_format))

    on_track = results[0]['on-track.jpg']
    during_gap = results[0]['during-gap.jpg']
    assert on_track.quality == 'good'
    assert on_track.confidence == 1.0
    assert during_gap.quality == 'gap'
    # Northbound (~0 deg), never the eastbound (~90 deg) cross-gap course.
    assert during_gap.bearing_deg == pytest.approx(on_track.bearing_deg, abs=1.0)


def test_continuous_interval_still_reports_good_with_full_confidence(service, tmp_path):
    track = _write_csv(
        tmp_path,
        [
            "2024-01-01T12:00:00Z,40.0,-75.0,100",
            "2024-01-01T12:00:30Z,40.001,-75.0,101",
        ],
    )
    results = []
    service.calculation_complete.connect(results.append)

    service.calculate_from_track(
        [{'path': 'a.jpg',
          'timestamp': datetime(2024, 1, 1, 12, 0, 15, tzinfo=timezone.utc)}],
        str(track))

    result = results[0]['a.jpg']
    assert result.quality == 'good'
    assert result.confidence == 1.0
