"""Solar position lookup and EXIF-time-to-UTC resolution.

Thin wrapper over `pysolar` plus a UTC resolver that walks the standard
EXIF/GPS timestamp fields. Kept separate from the rest of the shadow
pipeline so the underlying solar library can be swapped (e.g. for an
in-tree NREL SPA implementation) by editing only this file.

pysolar 0.13 conventions:
    altitude: degrees, 0 = horizon, 90 = zenith
    azimuth:  degrees, 0 = north, clockwise (0..360)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
from zoneinfo import ZoneInfo

import piexif
from pysolar.solar import get_altitude, get_azimuth


class SolarTimeUnresolvable(ValueError):
    """Raised when the EXIF/GPS timestamp cannot be resolved to UTC."""


@dataclass
class SolarPositionResult:
    """Sun position at a given location/time."""
    elevation_deg: float
    azimuth_deg: float
    utc_used: datetime
    time_source: str  # 'gps' | 'exif_with_offset'


def get_solar_position(lat: float, lon: float, utc_dt: datetime) -> Tuple[float, float]:
    """Return (elevation_deg, azimuth_deg) for the sun at lat/lon/utc_dt.

    utc_dt must be a timezone-aware datetime; pysolar relies on tz info to
    compute the true UTC offset.
    """
    if utc_dt.tzinfo is None:
        raise ValueError("utc_dt must be timezone-aware")
    elev = float(get_altitude(lat, lon, utc_dt))
    az = float(get_azimuth(lat, lon, utc_dt)) % 360.0
    return elev, az


def resolve_capture_utc(
    exif_data: dict,
    xmp_data: Optional[dict] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
) -> Tuple[datetime, str]:
    """Resolve image capture time to a tz-aware UTC datetime.

    Resolution order (first match wins, most authoritative first):
        1. EXIF GPSDateStamp + GPSTimeStamp — already UTC, preferred.
        2. EXIF DateTimeOriginal + OffsetTimeOriginal — canonical local+offset.
        3. XMP xmp:CreateDate / xmp:ModifyDate — ISO 8601 with offset.
           Enterprise DJI (Mavic 3E/T, Matrice, Zenmuse) writes the capture
           timezone here even when it skips OffsetTimeOriginal.
        4. EXIF DateTimeOriginal (naive) + the timezone derived from the GPS
           position via timezonefinder. Consumer drones (DJI Air/Mini, etc.)
           write only a bare local timestamp with no offset anywhere; the
           IANA zone for the capture location resolves that local time to UTC
           using the correct DST rule for that date. Tried last and flagged
           with a distinct source tag so callers can mark it as an estimate.

    A bare DateTimeOriginal with no offset and no usable GPS position stays
    unresolvable: guessing "local == UTC" can shift the sun azimuth by
    ~15°/hour and silently corrupt the height/shadow geometry. Reject loudly
    instead of guessing.

    Args:
        exif_data: piexif-format dict ({'0th': ..., 'Exif': ..., 'GPS': ...}).
        xmp_data: optional parsed XMP dict (keys without namespace prefix,
            as produced by MetaDataHelper.get_xmp_data(..., parse=True)).
        lat: optional capture latitude in decimal degrees, used only for the
            GPS-timezone fallback (step 4). Omit to disable that fallback.
        lon: optional capture longitude in decimal degrees (see lat).

    Returns:
        (utc_datetime, source_tag) where source_tag is one of
        'gps', 'exif_with_offset', 'xmp_create_date', 'xmp_modify_date',
        'exif_local_tz_from_gps'.

    Raises:
        SolarTimeUnresolvable: no resolvable timestamp present.
    """
    gps = exif_data.get('GPS') or {}
    gps_date = gps.get(piexif.GPSIFD.GPSDateStamp)
    gps_time = gps.get(piexif.GPSIFD.GPSTimeStamp)
    if gps_date and gps_time:
        try:
            return _from_gps(gps_date, gps_time), 'gps'
        except (ValueError, TypeError, ZeroDivisionError):
            pass

    exif = exif_data.get('Exif') or {}
    dt_orig = exif.get(piexif.ExifIFD.DateTimeOriginal)
    offset = exif.get(piexif.ExifIFD.OffsetTimeOriginal)
    if dt_orig and offset:
        try:
            return _from_local_with_offset(dt_orig, offset), 'exif_with_offset'
        except (ValueError, IndexError, TypeError):
            # Blank/garbage offset (e.g. a null-filled tag) -> fall through
            # rather than crash; a later path may still resolve the time.
            pass

    if xmp_data:
        for key, source in (('CreateDate', 'xmp_create_date'),
                            ('ModifyDate', 'xmp_modify_date')):
            value = xmp_data.get(key)
            if value:
                try:
                    return _from_iso8601(value), source
                except ValueError:
                    continue

    # Last resort: a naive DateTimeOriginal plus the timezone implied by the
    # GPS position. Only fires when no explicit offset was found above.
    if dt_orig and lat is not None and lon is not None:
        try:
            return (_from_local_via_gps_timezone(dt_orig, lat, lon),
                    'exif_local_tz_from_gps')
        except (ImportError, ValueError, KeyError, TypeError, OverflowError):
            # timezonefinder/tzdata unavailable, no zone for the position, or
            # an unparseable timestamp — fall through to the hard failure.
            pass

    raise SolarTimeUnresolvable(
        "Cannot resolve image capture time to UTC. Need GPSDateStamp+"
        "GPSTimeStamp, DateTimeOriginal+OffsetTimeOriginal, or an XMP "
        "CreateDate/ModifyDate with timezone offset."
    )


def _from_gps(gps_date, gps_time) -> datetime:
    """Build a UTC datetime from EXIF GPSDateStamp + GPSTimeStamp."""
    date_str = _to_str(gps_date)
    year, month, day = [int(part) for part in date_str.split(':')]
    hours = _rational_to_float(gps_time[0])
    minutes = _rational_to_float(gps_time[1])
    seconds = _rational_to_float(gps_time[2])
    h_int = int(hours)
    m_int = int(minutes)
    total_seconds = seconds + (hours - h_int) * 3600 + (minutes - m_int) * 60
    s_int = int(total_seconds)
    micro = int(round((total_seconds - s_int) * 1_000_000))
    if micro >= 1_000_000:
        s_int += 1
        micro -= 1_000_000
    return datetime(year, month, day, h_int, m_int, s_int, micro, tzinfo=timezone.utc)


def _from_local_with_offset(dt_orig, offset) -> datetime:
    """Build a UTC datetime from EXIF DateTimeOriginal + OffsetTimeOriginal."""
    dt_str = _to_str(dt_orig)
    off_str = _to_str(offset).strip()
    # EXIF format: 'YYYY:MM:DD HH:MM:SS'
    date_part, time_part = dt_str.split(' ')
    year, month, day = [int(p) for p in date_part.split(':')]
    hour, minute, second = [int(p) for p in time_part.split(':')]
    # Offset like '+05:30', '-07:00', 'Z'
    if off_str.upper() == 'Z':
        offset_minutes = 0
    else:
        sign = 1 if off_str[0] == '+' else -1
        oh, om = off_str[1:].split(':')
        offset_minutes = sign * (int(oh) * 60 + int(om))
    tz = timezone(timedelta(minutes=offset_minutes))
    local_dt = datetime(year, month, day, hour, minute, second, 0, tzinfo=tz)
    return local_dt.astimezone(timezone.utc)


_TZ_FINDER = None


def _get_timezone_finder():
    """Lazily construct a process-wide TimezoneFinder.

    The import is deferred so timezonefinder stays an optional dependency: if
    it is not installed the GPS-timezone fallback is skipped rather than
    breaking capture-time resolution for images that carry a real offset.
    Constructing the finder loads the bundled boundary dataset, so the
    instance is cached and reused across calls.
    """
    global _TZ_FINDER
    if _TZ_FINDER is None:
        from timezonefinder import TimezoneFinder
        _TZ_FINDER = TimezoneFinder()
    return _TZ_FINDER


def _from_local_via_gps_timezone(dt_orig, lat: float, lon: float) -> datetime:
    """Resolve a naive EXIF DateTimeOriginal to UTC using the GPS location.

    Looks up the IANA timezone covering lat/lon and applies it — with the
    correct DST offset for that calendar date — to the naive local
    timestamp. Raises ValueError if no timezone can be determined for the
    position or the timestamp cannot be parsed.
    """
    tz_name = _get_timezone_finder().timezone_at(lat=lat, lng=lon)
    if not tz_name:
        raise ValueError(f"No timezone for GPS position ({lat}, {lon})")
    dt_str = _to_str(dt_orig)
    # EXIF format: 'YYYY:MM:DD HH:MM:SS'
    date_part, time_part = dt_str.split(' ')
    year, month, day = [int(p) for p in date_part.split(':')]
    hour, minute, second = [int(p) for p in time_part.split(':')]
    local_dt = datetime(year, month, day, hour, minute, second, 0,
                        tzinfo=ZoneInfo(tz_name))
    return local_dt.astimezone(timezone.utc)


def _from_iso8601(value) -> datetime:
    """Parse an ISO 8601 datetime string with a timezone offset.

    Accepts the XMP form 'YYYY-MM-DDTHH:MM:SS±HH:MM' and a few common
    variants ('Z' suffix, space separator instead of 'T'). Raises
    ValueError if no offset is present — a naive timestamp here would
    silently corrupt the sun azimuth.
    """
    if isinstance(value, bytes):
        value = value.decode('ascii', errors='ignore')
    value = str(value).strip().replace(' ', 'T')
    # Python 3.11 handles 'Z' natively; on 3.10 we have to swap it.
    if value.endswith('Z'):
        value = value[:-1] + '+00:00'
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        raise ValueError(f"ISO 8601 timestamp lacks timezone: {value!r}")
    return dt.astimezone(timezone.utc)


def _to_str(value) -> str:
    """piexif returns most string fields as bytes; normalise."""
    if isinstance(value, bytes):
        return value.decode('ascii', errors='ignore').rstrip('\x00')
    return str(value)


def _rational_to_float(rational) -> float:
    """piexif rationals are (numerator, denominator) tuples."""
    if isinstance(rational, (tuple, list)) and len(rational) == 2:
        num, den = rational
        if den == 0:
            raise ZeroDivisionError("zero denominator in EXIF rational")
        return num / den
    return float(rational)
