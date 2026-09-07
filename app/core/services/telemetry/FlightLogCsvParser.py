"""Parse CSV flight logs into telemetry.

Not every aircraft writes telemetry into the video. Skydio exports a
separate CSV flight log, and operators of aircraft whose SRT is missing or
unusable often have a log exported from a ground-station app instead. This
is the "secondary metadata file" route: the operator points ADIAT at a
``.csv`` and it supplies the location data the video lacks.

The important structural difference from
:mod:`~core.services.telemetry.DjiSrtParser`: SRT cue times are already
**relative to the start of the video**, but CSV rows are stamped with
**absolute UTC**. Aligning them therefore needs the video's own start
time, read from the container's ``creation_time`` tag. Without it there is
no defensible way to line the two up — guessing that the first log row is
frame 0 would silently mis-geotag every image, because logs routinely
start on the ramp minutes before recording. So a video with no
``creation_time`` is reported as a failure rather than aligned on a guess.

Column naming is not standardised across vendors, so columns are matched
against an alias table on a normalized form of the header
(``"GPS Altitude (ft MSL)"`` → ``"gps altitude ft msl"``) rather than by
exact string equality. Altitudes are converted to metres and kept in
**three separate fields**, because vendors export three different
quantities under headings that look alike:

* ``altitude_msl_m`` — above mean sea level (``GPS Altitude (ft MSL)``).
* ``altitude_ato_m`` — above the **takeoff point** (``Relative
  Altitude (m)``, ``Height Above Takeoff (m)``). DJI's ``rel_alt``.
* ``altitude_agl_terrain_m`` — above the **terrain beneath the
  aircraft** (``Altitude (m AGL)``, ``AGL Altitude (m)``). Skydio and
  similar aircraft resolve this from their own sensors.

ATO and AGL used to share one field, which meant a log whose heading said
``Altitude (m AGL)`` — a real terrain-referenced height — arrived
downstream labelled ATO, was differenced against the DEM a second time by
:class:`~core.services.telemetry.TelemetryEnrichmentService.TelemetryEnrichmentService`, and was stamped into
``drone-dji:RelativeAltitude`` as a takeoff-relative figure. The error is
zero over flat ground and grows with relief, so it only ever showed up in
the field. Keeping the three apart is the rule in CLAUDE.md § 2.11.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import pandas as pd

from core.services.telemetry.TelemetryTrack import TelemetryTrack

FEET_TO_METERS = 0.3048

# CSV logs are sampled far slower than DJI's per-frame SRT — 1-10 Hz is
# typical, and some exports are 1 Hz. The SRT default (1 s) would report a
# dropout between every pair of rows, so the guard is widened to match
# ``VideoParserService._find_closest_csv_entry``'s long-standing 5 s.
CSV_MAX_GAP_SECONDS = 5.0

# Rows outside the video's own recording window are dropped, with this much
# slack at each end. Some tolerance is needed because a 1 Hz log will rarely
# have a row exactly at frame 0, but keeping the whole flight would draw a
# path the video never shows — and, more importantly, a log from a
# *different* flight would otherwise produce a track full of fixes that can
# never be sampled, which reads as success.
_WINDOW_TOLERANCE_SECONDS = CSV_MAX_GAP_SECONDS

# Plausible range for a unix timestamp in seconds: 2001-09-09 to 2096-10-02.
# Some logs stamp rows with an epoch integer rather than an ISO string, and
# pandas reads a bare number as *nanoseconds*, silently landing every row in
# 1970. The window is what separates a real epoch from other numeric date
# encodings (an Excel serial date is ~46000, four orders of magnitude out).
_EPOCH_SECONDS_MIN = 1_000_000_000
_EPOCH_SECONDS_MAX = 4_000_000_000

# Quoted back to the operator when nothing matched, so the error names a
# real Skydio export header rather than our internal field names.
CANONICAL_COLUMNS = (
    "Datetime (UTC)",
    "Latitude",
    "Longitude",
    "GPS Altitude (ft MSL)",
)

# Normalized header -> (field, unit). Units are converted on read.
_COLUMN_ALIASES: Dict[str, Tuple[str, str]] = {}


def _alias(field_name: str, unit: str, *headers: str) -> None:
    for header in headers:
        _COLUMN_ALIASES[_normalize(header)] = (field_name, unit)


def _normalize(name) -> str:
    """Lower-case a header and collapse punctuation to single spaces."""
    return re.sub(r"[^a-z0-9]+", " ", str(name).lower()).strip()


_alias("time", "", "Datetime (UTC)", "DateTime (UTC)", "UTC Time", "Timestamp (UTC)",
       "Timestamp", "Time (UTC)", "datetime_utc")
_alias("latitude", "deg", "Latitude", "Lat", "GPS Latitude", "latitude_deg")
_alias("longitude", "deg", "Longitude", "Lon", "Lng", "GPS Longitude", "longitude_deg")
_alias("altitude_msl", "ft", "GPS Altitude (ft MSL)", "Altitude (ft MSL)",
       "MSL Altitude (ft)")
_alias("altitude_msl", "m", "GPS Altitude (m MSL)", "Altitude (m MSL)",
       "MSL Altitude (m)", "altitude_msl_m")
# Above the takeoff point. DJI's ``rel_alt`` under other vendors' names:
# the value does not change when the terrain beneath the aircraft rises.
_alias("altitude_ato", "ft", "Relative Altitude (ft)",
       "Height Above Takeoff (ft)", "altitude_ato_ft")
_alias("altitude_ato", "m", "Relative Altitude (m)",
       "Height Above Takeoff (m)", "altitude_ato_m")
# Above the terrain beneath the aircraft. A heading that says "AGL" means
# this, and must never be folded in with the ATO group above - see the
# module docstring.
_alias("altitude_agl", "ft", "Altitude (ft AGL)", "AGL Altitude (ft)",
       "Height Above Ground (ft)")
_alias("altitude_agl", "m", "Altitude (m AGL)", "AGL Altitude (m)",
       "Height Above Ground (m)", "altitude_agl_m")
_alias("yaw", "deg", "Heading", "Heading (deg)", "Yaw", "Yaw (deg)",
       "Compass Heading", "Gimbal Yaw")


@dataclass
class FlightLogColumns:
    """Which CSV column supplies each telemetry field, and in what unit.

    Three altitude slots, never interchangeable: ``altitude_msl`` is above
    sea level, ``altitude_ato`` above the takeoff point, ``altitude_agl``
    above the terrain beneath the aircraft. A log may carry any subset.
    """

    time: str
    latitude: str
    longitude: str
    altitude_msl: Optional[str] = None
    altitude_msl_unit: str = "m"
    altitude_ato: Optional[str] = None
    altitude_ato_unit: str = "m"
    altitude_agl: Optional[str] = None
    altitude_agl_unit: str = "m"
    yaw: Optional[str] = None

    @property
    def has_altitude(self) -> bool:
        return bool(self.altitude_msl or self.altitude_ato or self.altitude_agl)


@dataclass
class FlightLogSample:
    """One log row, expressed in seconds from the start of the video.

    Deliberately the same shape :meth:`TelemetryTrack.from_samples` reads
    off DJI's SRT cues, so both sources get identical speed derivation and
    sampling behaviour.
    """

    start_seconds: float
    end_seconds: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude_msl_m: Optional[float] = None
    # Above the takeoff point. Named to match
    # :class:`~core.services.telemetry.DjiSrtParser.DjiSrtSample`, so
    # :meth:`TelemetryTrack.from_samples` reads both structurally.
    altitude_ato_m: Optional[float] = None
    # Above the terrain beneath the aircraft, where the log resolved one.
    # Almost always None: only aircraft with their own terrain reference
    # export it.
    altitude_agl_terrain_m: Optional[float] = None
    yaw_deg: Optional[float] = None

    @property
    def has_position(self) -> bool:
        return self.latitude is not None and self.longitude is not None


@dataclass
class FlightLogRows:
    """Result of reading a CSV: rows, or an explanation of why not.

    ``rows`` are dicts sorted by ``utc_time`` and carry:

    * ``utc_time`` — timezone-aware UTC ``datetime``
    * ``latitude`` / ``longitude`` — degrees
    * ``altitude_m`` — the **absolute** altitude, in metres, or None.
      This is the EXIF-facing value
      :class:`~core.services.VideoParserService.VideoParserService` writes
      into ``GPSAltitude``, and EXIF's is an absolute height, so only MSL
      can fill it. It used to fall back to the relative reading, which put
      a height-above-takeoff figure in a sea-level field and made
      ``median(GPSAltitude - ATO)`` — the barometric datum test in
      :mod:`~core.services.image.AltitudeAnchorService` — collapse to a
      perfectly coherent zero.
    * ``altitude_msl_m`` / ``altitude_ato_m`` /
      ``altitude_agl_terrain_m`` — the three references, kept apart; any
      may be None
    * ``yaw_deg`` — degrees, or None
    """

    rows: List[dict] = field(default_factory=list)
    missing_columns: List[str] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return bool(self.rows) and self.error is None and not self.missing_columns


def match_columns(columns: Sequence[str]) -> Tuple[Optional[FlightLogColumns], List[str]]:
    """Map a CSV's headers onto telemetry fields.

    Returns:
        ``(columns, missing)``. ``columns`` is None when a required field
        has no match; ``missing`` then names the canonical headers to add.
    """
    found: Dict[str, Tuple[str, str]] = {}
    for original in columns:
        match = _COLUMN_ALIASES.get(_normalize(original))
        if not match:
            continue
        field_name, unit = match
        # First match wins, so a log carrying both a metre and a foot
        # column resolves deterministically by column order.
        found.setdefault(field_name, (original, unit))

    missing = [
        canonical
        for canonical, key in (
            (CANONICAL_COLUMNS[0], "time"),
            (CANONICAL_COLUMNS[1], "latitude"),
            (CANONICAL_COLUMNS[2], "longitude"),
        )
        if key not in found
    ]
    if not any(key in found for key in
               ("altitude_msl", "altitude_ato", "altitude_agl")):
        missing.append(CANONICAL_COLUMNS[3])
    if missing:
        return None, missing

    msl = found.get("altitude_msl")
    ato = found.get("altitude_ato")
    agl = found.get("altitude_agl")
    yaw = found.get("yaw")
    return FlightLogColumns(
        time=found["time"][0],
        latitude=found["latitude"][0],
        longitude=found["longitude"][0],
        altitude_msl=msl[0] if msl else None,
        altitude_msl_unit=msl[1] if msl else "m",
        altitude_ato=ato[0] if ato else None,
        altitude_ato_unit=ato[1] if ato else "m",
        altitude_agl=agl[0] if agl else None,
        altitude_agl_unit=agl[1] if agl else "m",
        yaw=yaw[0] if yaw else None,
    ), []


def read_flight_log_rows(csv_path) -> FlightLogRows:
    """Read and normalize a CSV flight log.

    Rows whose timestamp or coordinates cannot be parsed are dropped
    rather than failing the file — one truncated line at the end of an
    export must not cost the operator the rest of the flight.
    """
    try:
        # Decode leniently, for the same reason the SRT reader does: a CSV
        # exported from a spreadsheet often carries an accented character in
        # some notes column, and losing that character must not cost the
        # operator the whole GPS track.
        frame = pd.read_csv(csv_path, encoding="utf-8", encoding_errors="replace")
    except Exception as exc:  # noqa: BLE001 - surfaced to the operator
        return FlightLogRows(error=str(exc))

    if frame.empty:
        return FlightLogRows(error="the flight log is empty")

    columns, missing = match_columns(list(frame.columns))
    if columns is None:
        return FlightLogRows(missing_columns=missing)

    times = _parse_times(frame[columns.time])
    latitudes = pd.to_numeric(frame[columns.latitude], errors="coerce")
    longitudes = pd.to_numeric(frame[columns.longitude], errors="coerce")
    msl = _numeric_metres(frame, columns.altitude_msl, columns.altitude_msl_unit)
    ato = _numeric_metres(frame, columns.altitude_ato, columns.altitude_ato_unit)
    agl = _numeric_metres(frame, columns.altitude_agl, columns.altitude_agl_unit)
    yaw = pd.to_numeric(frame[columns.yaw], errors="coerce") if columns.yaw else None

    rows: List[dict] = []
    for index in range(len(frame)):
        stamp = times.iloc[index]
        latitude = latitudes.iloc[index]
        longitude = longitudes.iloc[index]
        if pd.isna(stamp) or pd.isna(latitude) or pd.isna(longitude):
            continue

        altitude_msl = _value_or_none(msl, index)
        altitude_ato = _value_or_none(ato, index)
        altitude_agl = _value_or_none(agl, index)
        rows.append({
            # warn=False: sub-microsecond precision is irrelevant here, and
            # the default warning fires once per row on any log with
            # nanosecond timestamps.
            "utc_time": stamp.to_pydatetime(warn=False),
            "latitude": float(latitude),
            "longitude": float(longitude),
            # EXIF's GPSAltitude is an absolute height, so only MSL can
            # fill it. A relative reading here would be read back as a
            # sea-level figure by everything downstream.
            "altitude_m": altitude_msl,
            "altitude_msl_m": altitude_msl,
            "altitude_ato_m": altitude_ato,
            "altitude_agl_terrain_m": altitude_agl,
            "yaw_deg": _value_or_none(yaw, index),
        })

    if not rows:
        return FlightLogRows(error="no rows carried a usable timestamp and position")

    rows.sort(key=lambda row: row["utc_time"])
    return FlightLogRows(rows=rows)


def build_track_from_rows(
    rows: Sequence[dict],
    video_start_utc,
    *,
    duration_seconds: Optional[float] = None,
    source: str = "flight-log-csv",
    max_gap_seconds: float = CSV_MAX_GAP_SECONDS,
) -> Optional[TelemetryTrack]:
    """Convert absolute-UTC rows into a video-relative track.

    Args:
        rows: Rows from :func:`read_flight_log_rows`.
        video_start_utc: The video's ``creation_time``, timezone-aware.
        duration_seconds: The video's length, when known. Rows past the end
            are dropped, which is what turns "this log is from a different
            flight" into an empty result the caller can report rather than a
            track whose fixes can never be sampled.
        source: Label recorded on the track.
        max_gap_seconds: Sampling dropout guard.

    Returns:
        A track, or None when there is nothing inside the video's window.
    """
    if not rows or video_start_utc is None:
        return None

    latest = None
    if duration_seconds is not None:
        latest = float(duration_seconds) + _WINDOW_TOLERANCE_SECONDS

    samples: List[FlightLogSample] = []
    # Sort defensively. :class:`TelemetryTrack` binary-searches its times and
    # derives speed from a forward-only cursor, so out-of-order input does
    # not fail loudly — it returns *plausible but wrong* positions. This
    # module's own reader already sorts; this guards other callers.
    for row in sorted(rows, key=lambda item: item["utc_time"]):
        offset = (row["utc_time"] - video_start_utc).total_seconds()
        if offset < -_WINDOW_TOLERANCE_SECONDS:
            continue
        if latest is not None and offset > latest:
            continue
        samples.append(FlightLogSample(
            start_seconds=offset,
            end_seconds=offset,
            latitude=row.get("latitude"),
            longitude=row.get("longitude"),
            altitude_msl_m=row.get("altitude_msl_m"),
            altitude_ato_m=row.get("altitude_ato_m"),
            altitude_agl_terrain_m=row.get("altitude_agl_terrain_m"),
            yaw_deg=row.get("yaw_deg"),
        ))

    if not samples:
        return None
    return TelemetryTrack.from_samples(
        samples, source=source, max_gap_seconds=max_gap_seconds
    )


def read_flight_log_track(csv_path, video_path, logger=None):
    """Load a CSV flight log as a track aligned to ``video_path``.

    Returns:
        ``(track, detail)``. ``track`` is None on failure, and ``detail``
        always explains the outcome in terms the operator can act on —
        which columns are missing, or that the video carries no
        ``creation_time`` to align against.
    """
    from helpers.VideoFileHelper import get_video_timing

    result = read_flight_log_rows(csv_path)
    if result.missing_columns:
        return None, (
            "flight log is missing required columns: "
            + ", ".join(result.missing_columns)
        )
    if result.error:
        return None, f"could not read flight log ({result.error})"

    video_start_utc, duration_seconds = get_video_timing(video_path, logger)
    if video_start_utc is None:
        return None, (
            "the video has no creation_time metadata, so the flight log's "
            "timestamps cannot be aligned to it (ffprobe required)"
        )

    track = build_track_from_rows(
        result.rows, video_start_utc, duration_seconds=duration_seconds
    )
    if track is None or not len(track):
        # Naming both spans makes this diagnosable at a glance — a log from
        # the wrong flight and a log whose timestamps were misread look
        # identical otherwise.
        return None, (
            f"none of the flight log's {len(result.rows)} rows fall within "
            f"this video's recording window; the video starts "
            f"{video_start_utc.isoformat()} but the log covers "
            f"{result.rows[0]['utc_time'].isoformat()} to "
            f"{result.rows[-1]['utc_time'].isoformat()}"
        )

    return track, f"{len(track)} fixes from flight log"


def _parse_times(series):
    """Parse a time column into tz-aware UTC, tolerating epoch seconds.

    A numeric column is a unix timestamp often enough to be worth handling,
    but pandas reads a bare number as *nanoseconds* — so an epoch-seconds
    log parses "successfully" with every row in 1970, then gets rejected for
    falling outside the video's recording window. That points the operator
    at the wrong problem entirely (they go looking for the right video
    instead of the right column format), so numeric columns are either
    recognised as epoch seconds or reported as unparseable.
    """
    if pd.api.types.is_numeric_dtype(series):
        numeric = pd.to_numeric(series, errors="coerce")
        usable = numeric.dropna()
        if not usable.empty and usable.between(
                _EPOCH_SECONDS_MIN, _EPOCH_SECONDS_MAX).all():
            return pd.to_datetime(numeric, unit="s", utc=True, errors="coerce")
        return pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns, UTC]")
    return pd.to_datetime(series, utc=True, errors="coerce")


def _numeric_metres(frame, column: Optional[str], unit: str):
    """Coerce an altitude column to metres, or return None if absent."""
    if not column:
        return None
    values = pd.to_numeric(frame[column], errors="coerce")
    if unit == "ft":
        return values * FEET_TO_METERS
    return values


def _value_or_none(series, index) -> Optional[float]:
    if series is None:
        return None
    value = series.iloc[index]
    if pd.isna(value):
        return None
    number = float(value)
    # A log that writes 'inf' for a lost sensor must not poison the HUD or
    # the DEM anchor downstream.
    return number if math.isfinite(number) else None
