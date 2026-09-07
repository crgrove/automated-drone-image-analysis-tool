"""Tests for the shared CSV flight-log parser.

The parser's job is two-fold and both halves can fail quietly, so both are
covered here:

1. **Column matching.** Vendors do not agree on header names, so columns
   are matched against an alias table. A miss must name the missing field
   rather than producing a half-populated track.
2. **Time alignment.** CSV rows are stamped with absolute UTC while the
   rest of the telemetry pipeline works in seconds-from-video-start.
   Getting this wrong geotags every image with the wrong position, which
   is worse than no geotag at all, so alignment is asserted explicitly.

No file I/O beyond ``tmp_path`` and no ffprobe: the video's timing is
supplied directly to :func:`build_track_from_rows`.
"""

from datetime import datetime, timedelta, timezone

import pytest

from core.services.telemetry.FlightLogCsvParser import (
    CSV_MAX_GAP_SECONDS,
    FEET_TO_METERS,
    build_track_from_rows,
    match_columns,
    read_flight_log_rows,
    read_flight_log_track,
)

VIDEO_START = datetime(2026, 7, 25, 14, 38, 26, tzinfo=timezone.utc)

SKYDIO_CSV = """\
Datetime (UTC),Latitude,Longitude,GPS Altitude (ft MSL)
2026-07-25T14:38:26Z,30.648730,-97.675867,679.2
2026-07-25T14:38:27Z,30.648740,-97.675877,682.5
2026-07-25T14:38:28Z,30.648750,-97.675887,685.8
"""


def _write(tmp_path, text, name="flight.csv"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return str(path)


class TestColumnMatching:
    def test_matches_the_skydio_headers(self):
        columns, missing = match_columns(
            ["Datetime (UTC)", "Latitude", "Longitude", "GPS Altitude (ft MSL)"]
        )
        assert missing == []
        assert columns.time == "Datetime (UTC)"
        assert columns.altitude_msl_unit == "ft"

    def test_matching_is_case_and_punctuation_insensitive(self):
        columns, missing = match_columns(
            ["datetime_utc", "LAT", "lon", "altitude_msl_m"]
        )
        assert missing == []
        assert columns.altitude_msl_unit == "m"

    def test_accepts_an_ato_only_log(self):
        """Height above takeoff is a usable altitude even without MSL."""
        columns, missing = match_columns(
            ["Timestamp", "Latitude", "Longitude", "Relative Altitude (m)"]
        )
        assert missing == []
        assert columns.altitude_msl is None
        assert columns.altitude_ato == "Relative Altitude (m)"
        # ...and it is emphatically not filed as an AGL.
        assert columns.altitude_agl is None

    def test_accepts_a_terrain_agl_only_log(self):
        """A heading that says AGL means above the terrain, not the ramp."""
        columns, missing = match_columns(
            ["Timestamp", "Latitude", "Longitude", "Altitude (m AGL)"]
        )
        assert missing == []
        assert columns.altitude_agl == "Altitude (m AGL)"
        assert columns.altitude_ato is None
        assert columns.altitude_msl is None

    def test_ato_and_agl_columns_land_in_separate_slots(self):
        """The two are equal only over flat ground, so a log carrying both
        must keep both. Folding them together is what made a Skydio log's
        terrain AGL arrive downstream labelled ATO."""
        columns, missing = match_columns([
            "Timestamp", "Latitude", "Longitude",
            "Relative Altitude (m)", "Altitude (m AGL)",
            "GPS Altitude (m MSL)",
        ])
        assert missing == []
        assert columns.altitude_ato == "Relative Altitude (m)"
        assert columns.altitude_agl == "Altitude (m AGL)"
        assert columns.altitude_msl == "GPS Altitude (m MSL)"

    def test_height_above_takeoff_is_ato_whatever_the_unit(self):
        columns, _missing = match_columns([
            "Timestamp", "Latitude", "Longitude", "Height Above Takeoff (ft)",
        ])
        assert columns.altitude_ato == "Height Above Takeoff (ft)"
        assert columns.altitude_ato_unit == "ft"
        assert columns.altitude_agl is None

    def test_names_the_missing_fields(self):
        columns, missing = match_columns(["Datetime (UTC)", "Latitude"])
        assert columns is None
        assert "Longitude" in missing
        assert "GPS Altitude (ft MSL)" in missing

    def test_altitude_is_required(self):
        columns, missing = match_columns(["Datetime (UTC)", "Latitude", "Longitude"])
        assert columns is None
        assert missing == ["GPS Altitude (ft MSL)"]

    def test_unrelated_columns_are_ignored(self):
        columns, missing = match_columns([
            "Datetime (UTC)", "Latitude", "Longitude",
            "GPS Altitude (ft MSL)", "Battery %", "Notes",
        ])
        assert missing == []
        assert columns.yaw is None

    def test_optional_heading_is_picked_up(self):
        columns, _missing = match_columns([
            "Datetime (UTC)", "Latitude", "Longitude",
            "GPS Altitude (ft MSL)", "Heading",
        ])
        assert columns.yaw == "Heading"


class TestReadRows:
    def test_reads_and_converts(self, tmp_path):
        result = read_flight_log_rows(_write(tmp_path, SKYDIO_CSV))
        assert result.ok
        assert len(result.rows) == 3
        assert result.rows[0]["latitude"] == pytest.approx(30.648730)
        assert result.rows[0]["altitude_msl_m"] == pytest.approx(679.2 * FEET_TO_METERS)
        # altitude_m is the EXIF-facing value VideoParserService writes.
        assert result.rows[0]["altitude_m"] == result.rows[0]["altitude_msl_m"]

    def test_rows_are_sorted_by_time(self, tmp_path):
        shuffled = (
            "Datetime (UTC),Latitude,Longitude,GPS Altitude (ft MSL)\n"
            "2026-07-25T14:38:28Z,30.3,-97.3,3\n"
            "2026-07-25T14:38:26Z,30.1,-97.1,1\n"
            "2026-07-25T14:38:27Z,30.2,-97.2,2\n"
        )
        rows = read_flight_log_rows(_write(tmp_path, shuffled)).rows
        assert [row["latitude"] for row in rows] == [30.1, 30.2, 30.3]

    def test_an_ato_only_log_leaves_the_exif_altitude_empty(self, tmp_path):
        """EXIF's GPSAltitude is absolute; a height above the takeoff point
        is not one. Substituting it wrote a frame claiming the aircraft flew
        42 m above sea level, and made the barometric datum test in
        AltitudeAnchorService - median(GPSAltitude - ATO) - collapse to a
        perfectly consistent zero."""
        text = (
            "Timestamp,Latitude,Longitude,Relative Altitude (m)\n"
            "2026-07-25T14:38:26Z,30.1,-97.1,42.0\n"
        )
        row = read_flight_log_rows(_write(tmp_path, text)).rows[0]
        assert row["altitude_msl_m"] is None
        assert row["altitude_ato_m"] == pytest.approx(42.0)
        assert row["altitude_agl_terrain_m"] is None
        assert row["altitude_m"] is None

    def test_a_terrain_agl_log_is_not_read_as_ato(self, tmp_path):
        """The high-severity case: "Altitude (m AGL)" is a genuine
        terrain-referenced height. Filed as ATO it was differenced against
        the DEM a second time and stamped into RelativeAltitude as a
        takeoff-relative figure."""
        text = (
            "Timestamp,Latitude,Longitude,Altitude (m AGL)\n"
            "2026-07-25T14:38:26Z,30.1,-97.1,42.0\n"
        )
        row = read_flight_log_rows(_write(tmp_path, text)).rows[0]
        assert row["altitude_agl_terrain_m"] == pytest.approx(42.0)
        assert row["altitude_ato_m"] is None
        assert row["altitude_msl_m"] is None
        assert row["altitude_m"] is None

    def test_all_three_references_survive_together(self, tmp_path):
        text = (
            "Timestamp,Latitude,Longitude,GPS Altitude (m MSL),"
            "Relative Altitude (m),Altitude (m AGL)\n"
            "2026-07-25T14:38:26Z,30.1,-97.1,310.0,120.0,95.0\n"
        )
        row = read_flight_log_rows(_write(tmp_path, text)).rows[0]
        assert row["altitude_msl_m"] == pytest.approx(310.0)
        assert row["altitude_ato_m"] == pytest.approx(120.0)
        assert row["altitude_agl_terrain_m"] == pytest.approx(95.0)
        # Only the absolute one is EXIF-facing.
        assert row["altitude_m"] == pytest.approx(310.0)

    def test_unparseable_rows_are_skipped_not_fatal(self, tmp_path):
        """One bad line must not cost the operator the rest of the flight."""
        text = (
            "Datetime (UTC),Latitude,Longitude,GPS Altitude (ft MSL)\n"
            "2026-07-25T14:38:26Z,30.1,-97.1,100\n"
            "not-a-date,30.2,-97.2,100\n"
            "2026-07-25T14:38:28Z,,,100\n"
            "2026-07-25T14:38:29Z,30.4,-97.4,100\n"
        )
        result = read_flight_log_rows(_write(tmp_path, text))
        assert result.ok
        assert len(result.rows) == 2

    def test_blank_altitude_cell_is_none_not_nan(self, tmp_path):
        text = (
            "Datetime (UTC),Latitude,Longitude,GPS Altitude (ft MSL)\n"
            "2026-07-25T14:38:26Z,30.1,-97.1,\n"
        )
        row = read_flight_log_rows(_write(tmp_path, text)).rows[0]
        assert row["altitude_m"] is None

    def test_missing_columns_are_reported(self, tmp_path):
        result = read_flight_log_rows(_write(tmp_path, "A,B\n1,2\n"))
        assert not result.ok
        assert result.missing_columns

    def test_empty_file_is_reported(self, tmp_path):
        result = read_flight_log_rows(_write(tmp_path, "Datetime (UTC),Latitude\n"))
        assert not result.ok
        assert result.error

    def test_unreadable_file_is_reported(self, tmp_path):
        result = read_flight_log_rows(str(tmp_path / "nope.csv"))
        assert not result.ok
        assert result.error

    def test_no_usable_rows_is_reported(self, tmp_path):
        text = (
            "Datetime (UTC),Latitude,Longitude,GPS Altitude (ft MSL)\n"
            "not-a-date,x,y,z\n"
        )
        result = read_flight_log_rows(_write(tmp_path, text))
        assert not result.ok
        assert "usable" in result.error

    def test_a_bom_is_tolerated(self, tmp_path):
        result = read_flight_log_rows(_write(tmp_path, "﻿" + SKYDIO_CSV))
        assert result.ok

    def test_naive_timestamps_are_read_as_utc(self, tmp_path):
        text = (
            "Datetime (UTC),Latitude,Longitude,GPS Altitude (ft MSL)\n"
            "2026-07-25 14:38:26,30.1,-97.1,100\n"
        )
        row = read_flight_log_rows(_write(tmp_path, text)).rows[0]
        assert row["utc_time"] == datetime(2026, 7, 25, 14, 38, 26, tzinfo=timezone.utc)

    def test_mixed_timezone_offsets_normalize(self, tmp_path):
        text = (
            "Datetime (UTC),Latitude,Longitude,GPS Altitude (ft MSL)\n"
            "2026-07-25T09:38:26-05:00,30.1,-97.1,100\n"
            "2026-07-25T14:38:27+00:00,30.2,-97.2,100\n"
        )
        rows = read_flight_log_rows(_write(tmp_path, text)).rows
        assert rows[0]["utc_time"] == datetime(
            2026, 7, 25, 14, 38, 26, tzinfo=timezone.utc)
        assert rows[1]["utc_time"] > rows[0]["utc_time"]

    def test_a_non_utf8_export_still_parses(self, tmp_path):
        """A spreadsheet export with an accented note must not fail outright,
        the same leniency the SRT reader applies."""
        path = tmp_path / "latin1.csv"
        path.write_bytes(
            ("Datetime (UTC),Latitude,Longitude,GPS Altitude (ft MSL),Note\n"
             "2026-07-25T14:38:26Z,30.1,-97.1,100,caf\xe9\n").encode("latin-1")
        )
        result = read_flight_log_rows(str(path))
        assert result.ok
        assert len(result.rows) == 1

    def test_epoch_seconds_timestamps(self, tmp_path):
        """Some logs stamp rows with a unix integer. Pandas reads a bare
        number as nanoseconds, which silently puts every row in 1970."""
        text = (
            "Timestamp,Latitude,Longitude,GPS Altitude (ft MSL)\n"
            "1784144306,30.1,-97.1,100\n"
        )
        row = read_flight_log_rows(_write(tmp_path, text)).rows[0]
        assert row["utc_time"].year == 2026

    def test_other_numeric_dates_are_rejected_not_misread(self, tmp_path):
        """An Excel serial date is not an epoch. Reporting it as unparseable
        beats parsing it into 1970 and then blaming the wrong video."""
        text = (
            "Timestamp,Latitude,Longitude,GPS Altitude (ft MSL)\n"
            "46228.8183,30.1,-97.1,100\n"
        )
        result = read_flight_log_rows(_write(tmp_path, text))
        assert not result.ok
        assert "timestamp" in result.error

    def test_no_nanosecond_warnings_are_emitted(self, tmp_path, recwarn):
        """The default to_pydatetime warns once per row on a nanosecond log."""
        text = (
            "Datetime (UTC),Latitude,Longitude,GPS Altitude (ft MSL)\n"
            "2026-07-25T14:38:26.123456789Z,30.1,-97.1,100\n"
        )
        read_flight_log_rows(_write(tmp_path, text))
        assert [w for w in recwarn if "nanosecond" in str(w.message)] == []


def _rows(count=3, step=1.0, start=VIDEO_START, offset=0.0):
    return [
        {
            "utc_time": start + timedelta(seconds=offset + index * step),
            "latitude": 30.0 + index * 0.001,
            "longitude": -97.0 - index * 0.001,
            "altitude_m": 200.0 + index,
            "altitude_msl_m": 200.0 + index,
            "altitude_ato_m": 15.0 + index,
            "yaw_deg": 90.0,
        }
        for index in range(count)
    ]


class TestTrackAlignment:
    def test_offsets_are_relative_to_the_video(self):
        track = build_track_from_rows(_rows(), VIDEO_START)
        assert [p.time_seconds for p in track.points] == [0.0, 1.0, 2.0]

    def test_a_log_starting_mid_video_keeps_its_offset(self):
        track = build_track_from_rows(_rows(offset=30.0), VIDEO_START)
        assert track.points[0].time_seconds == pytest.approx(30.0)

    def test_speed_is_derived_like_the_srt_path(self):
        track = build_track_from_rows(_rows(count=5), VIDEO_START)
        speeds = [p.horizontal_speed_ms for p in track.points if
                  p.horizontal_speed_ms is not None]
        assert speeds and all(speed > 0 for speed in speeds)

    def test_pre_roll_rows_are_dropped(self):
        """A log that starts on the ramp must not draw a path the video
        never shows."""
        rows = _rows(count=4, offset=-600.0) + _rows(count=2)
        track = build_track_from_rows(rows, VIDEO_START, duration_seconds=120.0)
        assert len(track) == 2

    def test_rows_past_the_end_are_dropped(self):
        rows = _rows(count=2) + _rows(count=3, offset=5000.0)
        track = build_track_from_rows(rows, VIDEO_START, duration_seconds=60.0)
        assert len(track) == 2

    def test_a_log_from_another_flight_yields_nothing(self):
        """The failure mode that matters: without the duration bound this
        produced a track whose fixes could never be sampled, which reads to
        the operator as success followed by an empty HUD."""
        rows = _rows(count=3, offset=86400.0)
        assert build_track_from_rows(
            rows, VIDEO_START, duration_seconds=120.0) is None

    def test_slack_at_the_edges(self):
        """A 1 Hz log rarely has a row exactly at frame 0."""
        rows = _rows(count=1, offset=-2.0)
        track = build_track_from_rows(rows, VIDEO_START, duration_seconds=60.0)
        assert len(track) == 1

    def test_unknown_duration_keeps_everything_after_the_start(self):
        rows = _rows(count=3, offset=500.0)
        track = build_track_from_rows(rows, VIDEO_START, duration_seconds=None)
        assert len(track) == 3

    def test_no_video_start_yields_nothing(self):
        assert build_track_from_rows(_rows(), None) is None

    def test_no_rows_yields_nothing(self):
        assert build_track_from_rows([], VIDEO_START) is None

    def test_unsorted_rows_are_sorted(self):
        """TelemetryTrack binary-searches its times and derives speed from a
        forward-only cursor, so unsorted input does not fail loudly — it
        returns plausible but wrong positions."""
        rows = _rows(count=4)
        shuffled = [rows[3], rows[1], rows[2], rows[0]]
        track = build_track_from_rows(shuffled, VIDEO_START, duration_seconds=60.0)

        times = [p.time_seconds for p in track.points]
        assert times == sorted(times)
        assert track.point_at(0.0).latitude == pytest.approx(30.0)
        assert track.point_at(3.0).latitude == pytest.approx(30.003)

    def test_gap_guard_is_widened_for_slow_logs(self):
        """A 1 Hz log would report a dropout between every pair of rows
        under the SRT default."""
        track = build_track_from_rows(_rows(count=3, step=3.0), VIDEO_START)
        # 1.5 s from a fix: inside the CSV guard, outside the SRT one.
        assert track.point_at(1.5) is not None
        assert CSV_MAX_GAP_SECONDS > 1.0


class TestReadTrack:
    """End-to-end, with the container timing stubbed."""

    def test_reads_a_track(self, tmp_path, monkeypatch):
        import helpers.VideoFileHelper as helper
        monkeypatch.setattr(helper, "get_video_timing",
                            lambda *_a, **_k: (VIDEO_START, 120.0))
        track, detail = read_flight_log_track(
            _write(tmp_path, SKYDIO_CSV), "video.mp4"
        )
        assert len(track) == 3
        assert "flight log" in detail

    def test_missing_columns_short_circuit_before_ffprobe(self, tmp_path, monkeypatch):
        import helpers.VideoFileHelper as helper
        calls = []

        def timing(*_args, **_kwargs):
            calls.append(1)
            return (VIDEO_START, 120.0)

        monkeypatch.setattr(helper, "get_video_timing", timing)
        track, detail = read_flight_log_track(
            _write(tmp_path, "A,B\n1,2\n"), "video.mp4"
        )
        assert track is None
        assert "missing required columns" in detail
        assert calls == []

    def test_video_without_creation_time(self, tmp_path, monkeypatch):
        import helpers.VideoFileHelper as helper
        monkeypatch.setattr(helper, "get_video_timing",
                            lambda *_a, **_k: (None, 120.0))
        track, detail = read_flight_log_track(
            _write(tmp_path, SKYDIO_CSV), "video.mp4"
        )
        assert track is None
        assert "creation_time" in detail

    def test_log_outside_the_window(self, tmp_path, monkeypatch):
        import helpers.VideoFileHelper as helper
        monkeypatch.setattr(
            helper, "get_video_timing",
            lambda *_a, **_k: (datetime(2020, 1, 1, tzinfo=timezone.utc), 120.0),
        )
        track, detail = read_flight_log_track(
            _write(tmp_path, SKYDIO_CSV), "video.mp4"
        )
        assert track is None
        assert "recording window" in detail
        # Both spans named: a log from the wrong flight and a log whose
        # timestamps were misread are indistinguishable without them.
        assert "2020-01-01" in detail
        assert "2026-07-25" in detail
