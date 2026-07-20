"""Tests for SolarPosition wrapper + EXIF UTC resolution."""

from datetime import datetime, timezone

import piexif
import pytest

from core.services.shadow import SolarPosition as solar_mod
from core.services.shadow.SolarPosition import (
    get_solar_position,
    resolve_capture_utc,
    SolarTimeUnresolvable,
)

# Real coordinates from a DJI Air 2S (FC3411) sample: central Texas, which
# timezonefinder maps to America/Chicago (CDT in summer, CST in winter).
_TX_LAT, _TX_LON = 30.653516, -97.953659


def _make_gps_exif(date_bytes, time_rationals):
    return {
        '0th': {},
        'Exif': {},
        'GPS': {
            piexif.GPSIFD.GPSDateStamp: date_bytes,
            piexif.GPSIFD.GPSTimeStamp: time_rationals,
        },
    }


def _make_offset_exif(dt_bytes, offset_bytes):
    return {
        '0th': {},
        'GPS': {},
        'Exif': {
            piexif.ExifIFD.DateTimeOriginal: dt_bytes,
            piexif.ExifIFD.OffsetTimeOriginal: offset_bytes,
        },
    }


def test_resolve_utc_from_gps_stamps():
    exif = _make_gps_exif(b'2025:06:15', ((19, 1), (30, 1), (0, 1)))
    utc, source = resolve_capture_utc(exif)
    assert source == 'gps'
    assert utc == datetime(2025, 6, 15, 19, 30, 0, tzinfo=timezone.utc)


def test_resolve_utc_from_gps_with_fractional_seconds():
    # 19h, 30m, 15.5s
    exif = _make_gps_exif(b'2025:06:15', ((19, 1), (30, 1), (155, 10)))
    utc, _ = resolve_capture_utc(exif)
    assert utc.second == 15
    assert utc.microsecond == 500_000


def test_resolve_utc_from_datetime_with_offset_west():
    exif = _make_offset_exif(b'2025:06:15 12:30:00', b'-07:00')
    utc, source = resolve_capture_utc(exif)
    assert source == 'exif_with_offset'
    assert utc == datetime(2025, 6, 15, 19, 30, 0, tzinfo=timezone.utc)


def test_resolve_utc_from_datetime_with_offset_east():
    exif = _make_offset_exif(b'2025:06:15 12:30:00', b'+05:30')
    utc, _ = resolve_capture_utc(exif)
    assert utc == datetime(2025, 6, 15, 7, 0, 0, tzinfo=timezone.utc)


def test_resolve_utc_prefers_gps_over_offset():
    exif = {
        '0th': {},
        'GPS': {
            piexif.GPSIFD.GPSDateStamp: b'2025:06:15',
            piexif.GPSIFD.GPSTimeStamp: ((19, 1), (0, 1), (0, 1)),
        },
        'Exif': {
            piexif.ExifIFD.DateTimeOriginal: b'2025:06:15 12:30:00',
            piexif.ExifIFD.OffsetTimeOriginal: b'-07:00',
        },
    }
    _, source = resolve_capture_utc(exif)
    assert source == 'gps'


def test_resolve_utc_rejects_when_only_naive_datetime():
    exif = {
        '0th': {},
        'GPS': {},
        'Exif': {
            piexif.ExifIFD.DateTimeOriginal: b'2025:06:15 12:30:00',
        },
    }
    with pytest.raises(SolarTimeUnresolvable):
        resolve_capture_utc(exif)


def test_resolve_utc_rejects_when_nothing_present():
    with pytest.raises(SolarTimeUnresolvable):
        resolve_capture_utc({'0th': {}, 'GPS': {}, 'Exif': {}})


def test_resolve_utc_from_xmp_create_date():
    """DJI puts the timezone offset in XMP, not in OffsetTimeOriginal."""
    exif = {'0th': {}, 'GPS': {}, 'Exif': {}}
    xmp = {'CreateDate': '2026-01-18T12:15:08-08:00'}
    utc, source = resolve_capture_utc(exif, xmp)
    assert source == 'xmp_create_date'
    assert utc == datetime(2026, 1, 18, 20, 15, 8, tzinfo=timezone.utc)


def test_resolve_utc_xmp_modify_date_fallback():
    """If CreateDate is missing, fall through to ModifyDate."""
    exif = {'0th': {}, 'GPS': {}, 'Exif': {}}
    xmp = {'ModifyDate': '2026-01-18T12:15:08-08:00'}
    utc, source = resolve_capture_utc(exif, xmp)
    assert source == 'xmp_modify_date'
    assert utc == datetime(2026, 1, 18, 20, 15, 8, tzinfo=timezone.utc)


def test_resolve_utc_xmp_z_suffix_works():
    """ISO 8601 'Z' should be accepted as UTC."""
    exif = {'0th': {}, 'GPS': {}, 'Exif': {}}
    utc, _ = resolve_capture_utc(exif, {'CreateDate': '2026-01-18T20:15:08Z'})
    assert utc == datetime(2026, 1, 18, 20, 15, 8, tzinfo=timezone.utc)


def test_resolve_utc_xmp_naive_rejected():
    """An XMP timestamp without an offset must NOT be silently accepted."""
    exif = {'0th': {}, 'GPS': {}, 'Exif': {}}
    with pytest.raises(SolarTimeUnresolvable):
        resolve_capture_utc(exif, {'CreateDate': '2026-01-18T12:15:08'})


def test_resolve_utc_gps_still_wins_over_xmp():
    exif = {
        '0th': {},
        'GPS': {
            piexif.GPSIFD.GPSDateStamp: b'2025:06:15',
            piexif.GPSIFD.GPSTimeStamp: ((19, 1), (30, 1), (0, 1)),
        },
        'Exif': {},
    }
    xmp = {'CreateDate': '2026-01-18T12:15:08-08:00'}
    _, source = resolve_capture_utc(exif, xmp)
    assert source == 'gps'


# ---------------- GPS-position timezone fallback (step 4) ----------------

def _naive_dt_exif(dt_bytes):
    """EXIF with a bare DateTimeOriginal and no offset/GPS time."""
    return {
        '0th': {},
        'GPS': {},
        'Exif': {piexif.ExifIFD.DateTimeOriginal: dt_bytes},
    }


def test_resolve_utc_from_gps_timezone_dst():
    """Naive local time + GPS position resolves via the location's timezone.

    2023-08-30 is inside US DST, so central Texas is CDT (UTC-5):
    16:52:11 local -> 21:52:11 UTC. Mirrors the real DJI Air 2S case.
    """
    exif = _naive_dt_exif(b'2023:08:30 16:52:11')
    utc, source = resolve_capture_utc(exif, None, lat=_TX_LAT, lon=_TX_LON)
    assert source == 'exif_local_tz_from_gps'
    assert utc == datetime(2023, 8, 30, 21, 52, 11, tzinfo=timezone.utc)


def test_resolve_utc_from_gps_timezone_standard_time():
    """The same location in winter uses CST (UTC-6), proving DST is honoured."""
    exif = _naive_dt_exif(b'2023:01:15 12:00:00')
    utc, source = resolve_capture_utc(exif, None, lat=_TX_LAT, lon=_TX_LON)
    assert source == 'exif_local_tz_from_gps'
    assert utc == datetime(2023, 1, 15, 18, 0, 0, tzinfo=timezone.utc)


def test_resolve_utc_offset_wins_over_gps_timezone():
    """An explicit EXIF offset outranks the location-derived timezone."""
    exif = _make_offset_exif(b'2025:06:15 12:30:00', b'-07:00')
    _, source = resolve_capture_utc(exif, None, lat=_TX_LAT, lon=_TX_LON)
    assert source == 'exif_with_offset'


def test_resolve_utc_xmp_offset_wins_over_gps_timezone():
    """A real XMP offset outranks the location-derived timezone."""
    exif = _naive_dt_exif(b'2026:01:18 12:15:08')
    xmp = {'CreateDate': '2026-01-18T12:15:08-08:00'}
    _, source = resolve_capture_utc(exif, xmp, lat=_TX_LAT, lon=_TX_LON)
    assert source == 'xmp_create_date'


def test_resolve_utc_gps_timezone_requires_latlon():
    """Without lat/lon the naive timestamp stays unresolvable (no guessing)."""
    exif = _naive_dt_exif(b'2023:08:30 16:52:11')
    with pytest.raises(SolarTimeUnresolvable):
        resolve_capture_utc(exif, None)


def test_resolve_utc_placeholder_xmp_falls_through_to_gps_timezone():
    """DJI Air 2S shape: naive DateTimeOriginal + a bogus 1970-01-01 XMP date.

    The placeholder XMP has no time/offset and must be skipped, letting the
    GPS-timezone fallback resolve the capture instant.
    """
    exif = _naive_dt_exif(b'2023:08:30 16:52:11')
    xmp = {'CreateDate': '1970-01-01', 'ModifyDate': '1970-01-01'}
    utc, source = resolve_capture_utc(exif, xmp, lat=_TX_LAT, lon=_TX_LON)
    assert source == 'exif_local_tz_from_gps'
    assert utc == datetime(2023, 8, 30, 21, 52, 11, tzinfo=timezone.utc)


def test_resolve_utc_gps_timezone_none_zone_rejected(monkeypatch):
    """If no timezone covers the position, resolution fails loudly."""
    class _NoZoneFinder:
        def timezone_at(self, **kwargs):
            return None

    monkeypatch.setattr(solar_mod, '_get_timezone_finder',
                        lambda: _NoZoneFinder())
    exif = _naive_dt_exif(b'2023:08:30 16:52:11')
    with pytest.raises(SolarTimeUnresolvable):
        resolve_capture_utc(exif, None, lat=_TX_LAT, lon=_TX_LON)


def test_resolve_utc_blank_offset_does_not_crash():
    """A null-filled OffsetTimeOriginal must not raise; fall through to GPS tz."""
    exif = {
        '0th': {},
        'GPS': {},
        'Exif': {
            piexif.ExifIFD.DateTimeOriginal: b'2023:08:30 16:52:11',
            piexif.ExifIFD.OffsetTimeOriginal: b'\x00\x00\x00\x00\x00\x00\x00',
        },
    }
    utc, source = resolve_capture_utc(exif, None, lat=_TX_LAT, lon=_TX_LON)
    assert source == 'exif_local_tz_from_gps'
    assert utc == datetime(2023, 8, 30, 21, 52, 11, tzinfo=timezone.utc)


def test_resolve_utc_blank_offset_no_gps_rejected():
    """A blank offset with no fallback available rejects cleanly (not IndexError)."""
    exif = {
        '0th': {},
        'GPS': {},
        'Exif': {
            piexif.ExifIFD.DateTimeOriginal: b'2023:08:30 16:52:11',
            piexif.ExifIFD.OffsetTimeOriginal: b'\x00\x00\x00\x00\x00\x00\x00',
        },
    }
    with pytest.raises(SolarTimeUnresolvable):
        resolve_capture_utc(exif, None)


def test_resolve_utc_gps_timezone_missing_dependency(monkeypatch):
    """A missing timezonefinder degrades gracefully to unresolvable."""
    def _boom():
        raise ImportError("timezonefinder not installed")

    monkeypatch.setattr(solar_mod, '_get_timezone_finder', _boom)
    exif = _naive_dt_exif(b'2023:08:30 16:52:11')
    with pytest.raises(SolarTimeUnresolvable):
        resolve_capture_utc(exif, None, lat=_TX_LAT, lon=_TX_LON)


def test_get_solar_position_requires_aware_datetime():
    with pytest.raises(ValueError):
        get_solar_position(38.685, -121.082, datetime(2025, 6, 15, 19, 30))


def test_get_solar_position_returns_sane_values():
    # El Dorado Hills, CA, summer afternoon — sun should be high and SE-ish.
    dt = datetime(2025, 6, 15, 19, 30, 0, tzinfo=timezone.utc)
    elev, az = get_solar_position(38.685, -121.082, dt)
    assert 60.0 < elev < 80.0
    assert 120.0 < az < 200.0


def test_get_solar_position_below_horizon_at_night():
    # Same spot, ~06:00 UTC = ~11pm PDT prior day — sun should be below horizon.
    dt = datetime(2025, 6, 15, 6, 0, 0, tzinfo=timezone.utc)
    elev, _ = get_solar_position(38.685, -121.082, dt)
    assert elev < 0.0
