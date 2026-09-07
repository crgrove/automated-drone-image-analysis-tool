"""Shared drone-telemetry services.

One pipeline feeding every surface that shows aircraft location:

* image analysis (:class:`~core.services.VideoParserService.VideoParserService`)
* streaming analysis (``core.controllers.streaming``)
* the Flight Viewer (``core.controllers.flight``)

Telemetry reaches ADIAT from a ``.SRT`` sidecar, a ``.csv`` flight log, a
subtitle track embedded in the MP4, or a live ADIAT Flight WebRTC feed.
All of them normalize to the envelope shape
:class:`~core.views.flight.TelemetryHud.TelemetryHud` consumes, so the
same HUD renders any source.
"""

from core.services.telemetry.VideoProfileService import (
    DATUM_EXPLICIT,
    DATUM_MSL,
    DATUM_RELATIVE,
    LOCATION_EMBEDDED,
    LOCATION_SIDECAR,
    VideoProfile,
    datum_for_video,
    load_profiles,
    normalize_datum,
    profile_for_video,
    profiles_for_device_tag,
)
from core.services.telemetry.DjiSrtParser import (
    DjiSrtSample,
    extract_fields,
    parse_dji_srt,
    parse_timecode,
    parse_wall_clock,
)
from core.services.telemetry.FlightLogCsvParser import (
    CANONICAL_COLUMNS,
    CSV_MAX_GAP_SECONDS,
    FlightLogColumns,
    FlightLogRows,
    FlightLogSample,
    build_track_from_rows,
    match_columns,
    read_flight_log_rows,
    read_flight_log_track,
)
from core.services.telemetry.TelemetryEnrichmentService import (
    AGL_SOURCE_FLIGHT_LOG,
    AGL_SOURCE_REPORTED,
    AGL_SOURCE_TERRAIN,
    TelemetryEnrichmentService,
)
from core.services.telemetry.TelemetrySourceResolver import (
    METADATA_EXTENSIONS,
    SOURCE_EMBEDDED,
    SOURCE_EXPLICIT_FILE,
    SOURCE_NONE,
    SOURCE_SIDECAR,
    TelemetryResolution,
    find_sidecar_srt,
    load_telemetry_for_video,
    read_srt_track,
)
from core.services.telemetry.TelemetryTrack import (
    TelemetryPoint,
    TelemetryTrack,
    haversine_meters,
)

__all__ = [
    "AGL_SOURCE_FLIGHT_LOG",
    "AGL_SOURCE_REPORTED",
    "AGL_SOURCE_TERRAIN",
    "CANONICAL_COLUMNS",
    "CSV_MAX_GAP_SECONDS",
    "DATUM_EXPLICIT",
    "DATUM_MSL",
    "DATUM_RELATIVE",
    "DjiSrtSample",
    "FlightLogColumns",
    "FlightLogRows",
    "FlightLogSample",
    "LOCATION_EMBEDDED",
    "LOCATION_SIDECAR",
    "METADATA_EXTENSIONS",
    "SOURCE_EMBEDDED",
    "SOURCE_EXPLICIT_FILE",
    "SOURCE_NONE",
    "SOURCE_SIDECAR",
    "TelemetryEnrichmentService",
    "TelemetryPoint",
    "TelemetryResolution",
    "TelemetryTrack",
    "VideoProfile",
    "build_track_from_rows",
    "datum_for_video",
    "extract_fields",
    "find_sidecar_srt",
    "haversine_meters",
    "load_profiles",
    "load_telemetry_for_video",
    "match_columns",
    "normalize_datum",
    "parse_dji_srt",
    "profile_for_video",
    "profiles_for_device_tag",
    "parse_timecode",
    "parse_wall_clock",
    "read_flight_log_rows",
    "read_flight_log_track",
    "read_srt_track",
]
