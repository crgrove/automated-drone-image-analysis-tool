"""Derive a recording bundle's finished artifacts from its live logs.

:mod:`~core.services.streaming.RecordingSessionService` appends two
crash-safe logs while a recording runs — ``detections.jsonl`` and
``telemetry.jsonl``. This module turns those into the artifacts an
operator actually opens once the recording stops:

* ``ADIAT_Data.xml`` — an image-mode results file, so a streaming
  recording re-opens in the Images window via *Load Results File* with no
  new loader code. Each stored detection becomes one ``image`` entry
  pointing at its saved thumbnail, with a single ``areas_of_interest``
  re-projected onto that thumbnail.
* ``detections.csv`` — the same rows as a flat table, for spreadsheets
  and scripts.
* ``telemetry.csv`` — every fix recorded during the session, carrying all
  three altitude references: ``aircraft_altitude_msl_m`` (sea level),
  ``aircraft_altitude_agl_m`` (ATO — above the takeoff point) and
  ``aircraft_altitude_agl_terrain_m`` (AGL — above the terrain beneath
  the aircraft), plus the ``agl_source`` that produced the last of them.
  A detection has no altitude of its own; joining ``detections.csv`` to
  this file on ``video_time_seconds`` supplies all three.

  Bundles recorded before the references were split apart have an
  ``aircraft_altitude_agl_m`` column holding ATO on some rows and
  terrain-referenced AGL on others, because enrichment used to overwrite
  it in place. Nothing reads that column back, so no migration exists;
  treat the value in an old bundle as "one of the two, unknown which".
* ``flight_map.html`` — a self-contained Leaflet page (path + pins).
* ``flight_path.kml`` — path + detection placemarks for CalTopo and
  Google Earth.
* a sidecar ``.SRT`` beside the recorded MP4, so opening that MP4 in the
  streaming window replays the flight: the telemetry resolver discovers
  the sidecar automatically and the HUD, aircraft marker and trail follow
  the playhead. Together with :func:`find_bundle_for_video` /
  :func:`load_replay_detections` (which pre-load the stored detections
  into the gallery and map), the bundle replays on one screen — no
  detectors re-run; the record is the record.

Deriving is deliberately separate from capturing. It reads only the
bundle directory, so it also serves as the repair path for a bundle left
behind by a crash: the logs are there, and calling
:func:`finalize_bundle` on the folder produces everything that was never
written.
"""

from __future__ import annotations

import csv
import json
import os
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np

from core.services.LoggerService import LoggerService
from core.services.streaming.RecordingSessionService import (
    DETECTIONS_LOG,
    MANIFEST_FILE,
    TELEMETRY_LOG,
    read_jsonl,
    read_manifest,
)

RESULTS_XML = "ADIAT_Data.xml"
REPLAY_DETECTIONS_LOG = DETECTIONS_LOG  # re-exported for replay callers
DETECTIONS_CSV = "detections.csv"
TELEMETRY_CSV = "telemetry.csv"
FLIGHT_MAP_HTML = "flight_map.html"
FLIGHT_PATH_KML = "flight_path.kml"

# Identifies the producing pipeline in the exported results file, the way
# an image-mode run records the algorithm it came from.
_XML_ALGORITHM_FALLBACK = "StreamingRecording"

_DETECTION_CSV_COLUMNS = [
    "seq",
    "track_id",
    "detection_type",
    "confidence",
    "video_time_seconds",
    "recorded_frame_index",
    "first_frame_index",
    "latitude",
    "longitude",
    "bbox_x",
    "bbox_y",
    "bbox_w",
    "bbox_h",
    "centroid_x",
    "centroid_y",
    "pixel_area",
    "frame_width",
    "frame_height",
    "thumbnail",
    "recorded_at_epoch_s",
    # ADIAT Flight identity + clock (blank for streaming-window bundles).
    "track_key",
    "captured_at_ms",
]

# The writer uses ``extrasaction="ignore"``, so a key absent from this
# list is silently dropped from the CSV no matter what the envelope
# carries. All three altitude references are listed explicitly:
# ``aircraft_altitude_agl_m`` is above the takeoff point (ATO),
# ``aircraft_altitude_agl_terrain_m`` is above the terrain beneath the
# aircraft, and ``agl_source`` says which produced the latter.
#
# ``aircraft_altitude_agl_terrain_m`` and ``terrain_elevation_m`` are
# blank for ADIAT Flight sessions by design: Flight sends a measured AGL
# and desktop enrichment then issues no DEM lookups at all, so there is
# no terrain sample to record. See TelemetryEnrichmentService.
_TELEMETRY_CSV_COLUMNS = [
    "video_time_seconds",
    "captured_at_ms",
    "aircraft_latitude",
    "aircraft_longitude",
    "aircraft_altitude_msl_m",
    "aircraft_altitude_agl_m",
    "aircraft_altitude_agl_terrain_m",
    "aircraft_yaw_deg",
    "horizontal_speed_ms",
    "vertical_speed_ms",
    "agl_source",
    "terrain_elevation_m",
    "recorded_at_epoch_s",
    # The recorded video's own clock at the moment the fix arrived (see
    # RecordingService.append_telemetry). Blank for bundles recorded
    # before the stamp existed.
    "recorded_frame_index",
    "recorded_video_seconds",
]


def _pair(value: Any, index: int) -> Optional[float]:
    """Read one element of a stored ``[a, b]`` pair, tolerating junk."""
    if isinstance(value, (list, tuple)) and len(value) > index:
        item = value[index]
        if isinstance(item, (int, float)):
            return item
    return None


def _coords(rows: Sequence[dict]) -> List[Tuple[float, float]]:
    """Extract the flight path as ordered ``(lat, lon)`` fixes.

    Two corrections turn the raw fix log into a path worth drawing:

    * **Order by video time where every fix carries one.** Fixes are logged
      in the order they were played, and an operator recording a video file
      can scrub backwards - which would otherwise draw a path zigzagging
      between wherever the playhead jumped. Sorting by the source's own
      timeline recovers the route the aircraft actually flew. Live feeds
      carry no video time and are already chronological, so they are left
      exactly as logged.
    * **Drop consecutive duplicate positions.** A hovering aircraft, and
      the second (DEM-corrected) emission of a fix, both repeat a position
      that adds nothing to a polyline. ``telemetry.csv`` still carries
      every row - this only tidies the path.
    """
    fixes: List[Tuple[Optional[float], float, float]] = []
    for row in rows:
        lat = row.get("aircraft_latitude")
        lon = row.get("aircraft_longitude")
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            continue
        seconds = row.get("video_time_seconds")
        fixes.append((
            float(seconds) if isinstance(seconds, (int, float)) else None,
            float(lat),
            float(lon),
        ))

    if fixes and all(seconds is not None for seconds, _lat, _lon in fixes):
        fixes.sort(key=lambda fix: fix[0])

    path: List[Tuple[float, float]] = []
    for _seconds, lat, lon in fixes:
        point = (lat, lon)
        if path and path[-1] == point:
            continue
        path.append(point)
    return path


def _has_location(detection: dict) -> bool:
    return (
        isinstance(detection.get("latitude"), (int, float))
        and isinstance(detection.get("longitude"), (int, float))
    )


def _detection_label(detection: dict) -> str:
    """Human-facing name for a detection in a map popup or placemark."""
    kind = detection.get("detection_type") or "detection"
    return f"{kind} #{int(detection.get('seq', 0)) + 1}"


def _detection_details(detection: dict) -> List[str]:
    """Popup/description lines: confidence, time, position."""
    details: List[str] = []
    confidence = detection.get("confidence")
    if isinstance(confidence, (int, float)) and confidence:
        details.append(f"Confidence: {float(confidence):.2f}")
    video_time = detection.get("video_time_seconds")
    if isinstance(video_time, (int, float)):
        details.append(f"Video time: {_format_clock(float(video_time))}")
    if _has_location(detection):
        details.append(
            f"Position: {float(detection['latitude']):.6f}, "
            f"{float(detection['longitude']):.6f}"
        )
    return details


def _format_clock(seconds: float) -> str:
    """Render seconds as ``h:mm:ss`` / ``m:ss`` for operator-facing text."""
    seconds = max(0, int(round(seconds)))
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def _bgr_to_rgb(color: Any) -> Optional[Tuple[int, int, int]]:
    """Convert a stored BGR triple into RGB for KML styling."""
    if isinstance(color, (list, tuple)) and len(color) >= 3:
        try:
            b, g, r = int(color[0]), int(color[1]), int(color[2])
        except (TypeError, ValueError):
            return None
        return (r, g, b)
    return None


def write_detections_csv(bundle_dir: str, detections: Sequence[dict]) -> Optional[str]:
    """Write ``detections.csv``; returns its path, or ``None`` if empty."""
    if not detections:
        return None
    target = os.path.join(bundle_dir, DETECTIONS_CSV)
    with open(target, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=_DETECTION_CSV_COLUMNS)
        writer.writeheader()
        for detection in detections:
            bbox = detection.get("bbox") or []
            centroid = detection.get("centroid") or []
            resolution = detection.get("frame_resolution") or []
            writer.writerow({
                "seq": detection.get("seq"),
                "track_id": detection.get("track_id"),
                "detection_type": detection.get("detection_type"),
                "confidence": detection.get("confidence"),
                "video_time_seconds": detection.get("video_time_seconds"),
                "recorded_frame_index": detection.get("recorded_frame_index"),
                "first_frame_index": detection.get("first_frame_index"),
                "latitude": detection.get("latitude"),
                "longitude": detection.get("longitude"),
                "bbox_x": _pair(bbox, 0),
                "bbox_y": _pair(bbox, 1),
                "bbox_w": _pair(bbox, 2),
                "bbox_h": _pair(bbox, 3),
                "centroid_x": _pair(centroid, 0),
                "centroid_y": _pair(centroid, 1),
                "pixel_area": detection.get("pixel_area"),
                "frame_width": _pair(resolution, 0),
                "frame_height": _pair(resolution, 1),
                "thumbnail": detection.get("thumbnail"),
                "recorded_at_epoch_s": detection.get("recorded_at_epoch_s"),
                "track_key": detection.get("track_key"),
                "captured_at_ms": detection.get("captured_at_ms"),
            })
    return target


def write_telemetry_csv(bundle_dir: str, fixes: Sequence[dict]) -> Optional[str]:
    """Write ``telemetry.csv``; returns its path, or ``None`` if empty."""
    if not fixes:
        return None
    target = os.path.join(bundle_dir, TELEMETRY_CSV)
    with open(target, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=_TELEMETRY_CSV_COLUMNS, extrasaction="ignore"
        )
        writer.writeheader()
        for fix in fixes:
            writer.writerow({key: fix.get(key) for key in _TELEMETRY_CSV_COLUMNS})
    return target


def build_aoi(detection: dict) -> dict:
    """Compose one ``areas_of_interest`` entry for a stored detection.

    The exported image is the detection's own thumbnail crop, so the AOI
    is expressed in thumbnail pixels: the crop is centered on the
    detection but clamped at the frame edges, which is why
    ``thumbnail_origin`` is needed rather than assuming the center.
    """
    bbox = detection.get("bbox") or []
    x = _pair(bbox, 0) or 0
    y = _pair(bbox, 1) or 0
    width = _pair(bbox, 2) or 0
    height = _pair(bbox, 3) or 0

    thumb_size = detection.get("thumbnail_size")
    thumb_w = _pair(thumb_size, 0)
    thumb_h = _pair(thumb_size, 1)

    origin = detection.get("thumbnail_origin")
    origin_known = _pair(origin, 0) is not None and _pair(origin, 1) is not None

    if origin_known and width and height:
        # Streaming-window records: the thumbnail was cropped locally, so
        # the bbox projects exactly onto it.
        origin_x = _pair(origin, 0) or 0
        origin_y = _pair(origin, 1) or 0
        center_x = int(round(x + width / 2.0 - origin_x))
        center_y = int(round(y + height / 2.0 - origin_y))
    elif thumb_w and thumb_h:
        # Crop geometry unknown (an ADIAT Flight thumb was cropped on the
        # mobile publisher): the crop is centered on the detection by
        # construction, so the thumbnail's own center is the best - and
        # only defensible - placement.
        center_x = int(thumb_w) // 2
        center_y = int(thumb_h) // 2
    else:
        center_x = int(round(x + width / 2.0))
        center_y = int(round(y + height / 2.0))

    if thumb_w and thumb_h:
        # A clamped crop can put the nominal center outside the saved
        # image; keep the marker on the thumbnail either way.
        center_x = max(0, min(int(thumb_w) - 1, center_x))
        center_y = max(0, min(int(thumb_h) - 1, center_y))

    radius = max(8, int(round(min(width, height) / 2.0))) if width and height else 20
    pixel_area = detection.get("pixel_area")
    if isinstance(pixel_area, (int, float)) and pixel_area > 0:
        area = int(round(pixel_area))
    else:
        area = int(round(width * height)) or 100

    aoi: Dict[str, Any] = {
        "center": (center_x, center_y),
        "radius": radius,
        "area": area,
        "number": int(detection.get("seq", 0)) + 1,
    }

    confidence = detection.get("confidence")
    if isinstance(confidence, (int, float)):
        aoi["confidence"] = float(confidence)
        aoi["score_type"] = "confidence"
        aoi["raw_score"] = float(confidence)
        aoi["score_method"] = "StreamingRecording"

    comment_parts: List[str] = []
    kind = detection.get("detection_type")
    if kind:
        comment_parts.append(str(kind))
    video_time = detection.get("video_time_seconds")
    if isinstance(video_time, (int, float)):
        comment_parts.append(f"at {_format_clock(float(video_time))}")
    if _has_location(detection):
        comment_parts.append(
            f"GPS: {float(detection['latitude']):.6f}, "
            f"{float(detection['longitude']):.6f}"
        )
    if comment_parts:
        aoi["user_comment"] = " | ".join(comment_parts)

    return aoi


def write_results_xml(
    bundle_dir: str,
    detections: Sequence[dict],
    manifest: dict,
) -> Optional[str]:
    """Write an image-mode ``ADIAT_Data.xml`` for the stored detections.

    Mirrors the Mission Gallery export: one ``image`` per detection
    pointing at its thumbnail, so the Images window's *Load Results File*
    opens a streaming recording with no receiving-side changes.
    """
    if not detections:
        return None

    # Imported lazily so the streaming stack does not pull XmlService (and
    # its dependencies) in at module import time.
    from core.services.XmlService import XmlService

    target = os.path.join(bundle_dir, RESULTS_XML)
    xml = XmlService()
    xml.xml_path = target

    options = {
        "source": "ADIAT Streaming Recording",
        "recorded_at": manifest.get("started_at") or "",
        "stream_source": (manifest.get("source") or {}).get("url") or "",
        "stream_type": (manifest.get("source") or {}).get("type") or "",
    }
    for key, value in (manifest.get("algorithm_options") or {}).items():
        # Namespaced so an algorithm option can never collide with the
        # provenance keys above.
        options[f"algorithm.{key}"] = value

    xml.add_settings_to_xml(**{
        "output_dir": bundle_dir,
        "input_dir": bundle_dir,
        "num_processes": 1,
        "identifier_color": (0, 255, 0),
        "aoi_radius": 20,
        "min_area": 1,
        "max_area": 0,
        "hist_ref_path": "",
        "kmeans_clusters": 0,
        "algorithm": manifest.get("algorithm") or _XML_ALGORITHM_FALLBACK,
        "thermal": "False",
        "options": options,
    })

    for detection in detections:
        thumbnail = detection.get("thumbnail")
        if not thumbnail:
            # Without an image there is nothing for the viewer to show;
            # the row still lives in detections.csv.
            continue
        thumb_size = detection.get("thumbnail_size") or []
        xml.add_image_to_xml({
            # Stored relative to the XML, with forward slashes: XmlService
            # resolves a relative path against the file's own directory, so
            # the whole bundle can be copied to a team drive and still open.
            # An absolute path would break the moment the folder moved.
            "path": str(thumbnail),
            "width": int(_pair(thumb_size, 0) or 0),
            "height": int(_pair(thumb_size, 1) or 0),
            "aois": [build_aoi(detection)],
        })

    xml.save_xml_file(target)
    return target


def _flight_map_requested(manifest: dict) -> bool:
    """Whether the operator asked for a flight map for this recording.

    Defaults to ``True`` when the manifest cannot say: a bundle recovered
    from a crash is better off with a map it may not have wanted than
    silently missing the one it did.
    """
    options = manifest.get("options")
    if not isinstance(options, dict) or "save_flight_map" not in options:
        return True
    return bool(options.get("save_flight_map"))


def write_flight_map(
    bundle_dir: str,
    path: Sequence[Tuple[float, float]],
    detections: Sequence[dict],
    manifest: dict,
) -> Optional[str]:
    """Write ``flight_map.html``; ``None`` when there is nothing to plot.

    Detections are geotagged whether or not a map was asked for, so the
    operator's choice has to be checked here - otherwise unchecking "Save
    flight map" would still produce one from the detections alone.
    """
    if not _flight_map_requested(manifest):
        return None
    geotagged = [d for d in detections if _has_location(d)]
    if not path and not geotagged:
        return None

    from core.services.export.FlightMapHtmlService import write_flight_map_html

    pins = [{
        "lat": float(d["latitude"]),
        "lon": float(d["longitude"]),
        "label": _detection_label(d),
        "details": _detection_details(d),
        "detection_type": d.get("detection_type"),
        "thumbnail": d.get("thumbnail"),
    } for d in geotagged]

    started = manifest.get("started_at") or ""
    caption_parts = []
    if started:
        caption_parts.append(started.replace("T", " "))
    caption_parts.append(f"{len(pins)} detection{'s' if len(pins) != 1 else ''}")
    caption_parts.append(f"{len(path)} fix{'es' if len(path) != 1 else ''}")
    algorithm = manifest.get("algorithm")
    if algorithm:
        caption_parts.append(str(algorithm))

    return write_flight_map_html(
        os.path.join(bundle_dir, FLIGHT_MAP_HTML),
        path=path,
        detections=pins,
        title="ADIAT Flight Map",
        caption=" · ".join(caption_parts),
    )


def write_flight_kml(
    bundle_dir: str,
    path: Sequence[Tuple[float, float]],
    detections: Sequence[dict],
    manifest: dict,
) -> Optional[str]:
    """Write ``flight_path.kml``; ``None`` when there is nothing to plot."""
    if not _flight_map_requested(manifest):
        return None
    geotagged = [d for d in detections if _has_location(d)]
    if len(path) < 2 and not geotagged:
        return None

    from core.services.export.KMLGeneratorService import KMLGeneratorService

    kml = KMLGeneratorService(use_terrain=False)
    started = manifest.get("started_at") or ""
    kml.add_flight_path(
        path,
        name="Flight Path",
        description=f"ADIAT streaming recording{f' - {started}' if started else ''}",
    )
    for detection in geotagged:
        kml.add_aoi_placemark(
            _detection_label(detection),
            float(detection["latitude"]),
            float(detection["longitude"]),
            "<br>".join(_detection_details(detection)),
            color_rgb=_bgr_to_rgb(detection.get("detection_color")),
        )

    target = os.path.join(bundle_dir, FLIGHT_PATH_KML)
    kml.save_kml(target)
    return target


def _srt_timecode(seconds: float) -> str:
    total_ms = max(0, int(round(seconds * 1000)))
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def write_replay_srt(
    bundle_dir: str,
    fixes: Sequence[dict],
    manifest: dict,
    logger: Optional[LoggerService] = None,
) -> Optional[str]:
    """Write a sidecar ``.SRT`` beside the recorded MP4 for replay.

    Opening the recorded MP4 in the streaming window then behaves like
    opening a DJI clip from the card: :func:`~core.services.telemetry.\
TelemetrySourceResolver.find_sidecar_srt` discovers the file, and the HUD,
    aircraft marker and flight trail track the playhead.

    Cue times ride the recorded video's own clock:
    ``recorded_video_seconds`` (the writer's frame count / its fps at the
    moment the fix arrived) when the fix carries it, falling back to
    ``recorded_at_epoch_s - started_at_epoch_s`` for bundles recorded
    before the stamp existed. The recorded clock matters because the
    writer splices connection gaps out of the MP4 - wall-clock cues after
    an outage would lag the picture by the outage's length for the rest
    of the replay, while frame-count cues compress the gap exactly as the
    video does. Alignment remains best-effort, not frame-exact.

    Altitudes are written as the explicit ``rel_alt``/``abs_alt`` pair
    (ATO / MSL — never the terrain AGL, which is desktop-derived), which
    also spares the reader its ffprobe datum probe. Written only for the
    first video segment; a multi-segment recording gets telemetry replay
    for its first 30 minutes and a logged note for the rest.
    """
    log = logger or LoggerService()
    started = manifest.get("started_at_epoch_s")
    videos = (manifest.get("video") or {}).get("files") or []
    if not fixes or not isinstance(started, (int, float)) or not videos:
        return None

    if len(videos) > 1:
        log.warning(
            f"Recording bundle {bundle_dir}: {len(videos)} video segments; "
            "replay telemetry is written for the first segment only."
        )

    cues: List[Tuple[float, dict]] = []
    for fix in fixes:
        lat = fix.get("aircraft_latitude")
        lon = fix.get("aircraft_longitude")
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            continue
        recorded = fix.get("recorded_video_seconds")
        if isinstance(recorded, (int, float)):
            cues.append((max(0.0, float(recorded)), fix))
            continue
        stamped = fix.get("recorded_at_epoch_s")
        if not isinstance(stamped, (int, float)):
            continue
        cues.append((max(0.0, float(stamped) - float(started)), fix))
    if not cues:
        return None
    cues.sort(key=lambda item: item[0])

    blocks: List[str] = []
    for index, (seconds, fix) in enumerate(cues):
        end_seconds = cues[index + 1][0] if index + 1 < len(cues) else seconds + 1.0
        if end_seconds <= seconds:
            end_seconds = seconds + 0.001

        tokens = [
            f"[latitude: {float(fix['aircraft_latitude']):.6f}]",
            f"[longitude: {float(fix['aircraft_longitude']):.6f}]",
        ]
        ato = fix.get("aircraft_altitude_agl_m")
        msl = fix.get("aircraft_altitude_msl_m")
        if isinstance(ato, (int, float)) and isinstance(msl, (int, float)):
            tokens.append(f"[rel_alt: {float(ato):.3f} abs_alt: {float(msl):.3f}]")
        elif isinstance(msl, (int, float)):
            tokens.append(f"[abs_alt: {float(msl):.3f}]")
        elif isinstance(ato, (int, float)):
            tokens.append(f"[rel_alt: {float(ato):.3f}]")
        yaw = fix.get("aircraft_yaw_deg")
        if isinstance(yaw, (int, float)):
            tokens.append(f"[gb_yaw: {float(yaw):.1f}]")

        lines = [
            str(index + 1),
            f"{_srt_timecode(seconds)} --> {_srt_timecode(end_seconds)}",
            f"FrameCnt: {index + 1}, DiffTime: 0ms",
        ]
        captured = fix.get("captured_at_ms")
        if isinstance(captured, (int, float)):
            # The publisher's own wall clock, in the format DJI uses —
            # frame extraction stamps EXIF capture time from this.
            lines.append(
                time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(float(captured) / 1000.0)
                )
                + f",{int(captured) % 1000:03d}"
            )
        lines.append(" ".join(tokens))
        blocks.append("\n".join(lines))

    video_name = str(videos[0])
    srt_name = os.path.splitext(video_name)[0] + ".SRT"
    target = os.path.join(bundle_dir, srt_name)
    with open(target, "w", encoding="utf-8") as handle:
        handle.write("\n\n".join(blocks) + "\n")
    return target


def find_bundle_for_video(video_path: str) -> Optional[str]:
    """The recording bundle a video belongs to, or ``None``.

    A video "belongs to" a bundle when its own directory carries the
    bundle manifest — which is exactly how recordings are laid out, and
    survives the folder being renamed or copied elsewhere.
    """
    if not video_path:
        return None
    directory = os.path.dirname(os.path.abspath(str(video_path)))
    if os.path.isfile(os.path.join(directory, MANIFEST_FILE)):
        return directory
    return None


def load_replay_detections(bundle_dir: str) -> List[dict]:
    """The bundle's stored detections, ready for the replay gallery.

    Rows come back in the shape ``detections.jsonl`` recorded — bbox,
    confidence, type, geotag, ``recorded_frame_index`` for seeking —
    plus ``thumbnail_path`` resolved to an absolute path when the
    thumbnail file is actually present. Replay renders the record; it
    never re-runs a detector.
    """
    rows = read_jsonl(os.path.join(bundle_dir, DETECTIONS_LOG))
    for row in rows:
        thumbnail = row.get("thumbnail")
        if thumbnail:
            candidate = os.path.join(bundle_dir, str(thumbnail).replace("/", os.sep))
            if os.path.isfile(candidate):
                row["thumbnail_path"] = candidate
    return rows


def finalize_bundle(bundle_dir: str, logger: Optional[LoggerService] = None,
                    *, exports: bool = False) -> Dict[str, Any]:
    """Finish a bundle: always the replay essentials, exports on request.

    A recording's default footprint is what internal replay needs and
    nothing more: the video, the sidecar ``.SRT`` (derived here from the
    telemetry log), the detection log + thumbnails, and the manifest. The
    five export artifacts — ``ADIAT_Data.xml``, the two CSVs,
    ``flight_map.html`` and ``flight_path.kml`` — exist for OTHER tools
    (the Images window, spreadsheets, browsers, CalTopo) and are written
    only when ``exports=True`` (see :func:`export_bundle`, wired to the
    Replay window's Export button).

    Each artifact is attempted independently: a failure writing the KML
    must not cost the operator the results XML. Failures are logged and
    reported in the returned dict under ``errors``.

    Returns:
        ``{"bundle_dir", "artifacts", "counts", "errors"}``. Also rewrites
        ``manifest.json`` with the artifact list so the bundle describes
        itself.
    """
    log = logger or LoggerService()
    manifest = read_manifest(bundle_dir)
    detections = read_jsonl(os.path.join(bundle_dir, DETECTIONS_LOG))
    telemetry = read_jsonl(os.path.join(bundle_dir, TELEMETRY_LOG))
    path = _coords(telemetry)

    artifacts: Dict[str, Optional[str]] = {}
    errors: List[str] = []

    steps = [
        ("replay_srt", lambda: write_replay_srt(bundle_dir, telemetry, manifest, log)),
    ]
    if exports:
        steps += [
            ("detections_csv", lambda: write_detections_csv(bundle_dir, detections)),
            ("results_xml", lambda: write_results_xml(bundle_dir, detections, manifest)),
            ("telemetry_csv", lambda: write_telemetry_csv(bundle_dir, telemetry)),
            ("flight_map_html", lambda: write_flight_map(bundle_dir, path, detections, manifest)),
            ("flight_path_kml", lambda: write_flight_kml(bundle_dir, path, detections, manifest)),
        ]
    for name, step in steps:
        try:
            written = step()
        except Exception as exc:  # noqa: BLE001 - one artifact must not sink the rest
            log.error(f"Recording bundle {bundle_dir}: could not write {name}: {exc}")
            errors.append(f"{name}: {exc}")
            written = None
        artifacts[name] = os.path.basename(written) if written else None

    counts = {
        "detections_stored": len(detections),
        "detections_geotagged": sum(1 for d in detections if _has_location(d)),
        "telemetry_fixes": len(telemetry),
    }

    result = {
        "bundle_dir": bundle_dir,
        "artifacts": artifacts,
        "counts": counts,
        "errors": errors,
    }

    try:
        manifest.setdefault("counts", {}).update(counts)
        merged = dict(manifest.get("artifacts") or {})
        merged.update({k: v for k, v in artifacts.items() if v is not None})
        manifest["artifacts"] = merged
        manifest.setdefault("telemetry", {})["available"] = bool(path)
        manifest["finalized_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        if errors:
            manifest["finalize_errors"] = errors
        with open(os.path.join(bundle_dir, MANIFEST_FILE), "w", encoding="utf-8") as handle:
            json.dump(manifest, handle, indent=2)
    except (OSError, TypeError, ValueError) as exc:
        log.error(f"Recording bundle {bundle_dir}: could not update manifest: {exc}")
        errors.append(f"manifest: {exc}")

    return result


def export_bundle(bundle_dir: str, logger: Optional[LoggerService] = None) -> Dict[str, Any]:
    """Write the bundle's export artifacts for other tools.

    ``ADIAT_Data.xml`` (Images-window review), ``detections.csv`` /
    ``telemetry.csv`` (spreadsheets), ``flight_map.html`` (any browser)
    and ``flight_path.kml`` (CalTopo / Google Earth). Idempotent — safe to
    run again after more artifacts were asked for.
    """
    return finalize_bundle(bundle_dir, logger, exports=True)


__all__ = [
    "DETECTIONS_CSV",
    "FLIGHT_MAP_HTML",
    "FLIGHT_PATH_KML",
    "RESULTS_XML",
    "TELEMETRY_CSV",
    "build_aoi",
    "export_bundle",
    "finalize_bundle",
    "find_bundle_for_video",
    "load_replay_detections",
    "write_replay_srt",
    "write_detections_csv",
    "write_flight_kml",
    "write_flight_map",
    "write_results_xml",
    "write_telemetry_csv",
]


# ---------------------------------------------------------------------------
# Mission Gallery export
#
# The Flight Viewer's gallery can be written out as an ordinary image-mode
# results folder (plan §15 M3), which is the same job write_results_xml does
# for a recorded bundle - one detection per image entry, one AOI each. It
# lived in MissionGalleryController until CLAUDE.md 2.1 caught it: building an
# XML tree, writing JPEG bytes and cv2-encoding a placeholder are not UI
# orchestration.
# ---------------------------------------------------------------------------

def write_gallery_export(out_dir: str, rows: Sequence[dict]) -> str:
    """Write a Mission Gallery export into ``out_dir``.

    Thumbnails plus an ``ADIAT_Data.xml`` shaped like an ordinary
    image-mode results file, so the operator can re-open the folder from
    the Image Analysis window with no new code on the receiving side.

    Lives here rather than in the gallery controller because it is file
    I/O and XML construction (CLAUDE.md 2.1), and because this module
    already writes the same shape for a recorded bundle - see
    :func:`write_results_xml`, whose docstring has always said it
    "mirrors the Mission Gallery export".

    Args:
        out_dir: Directory to create and write into.
        rows: Detection snapshots, already filtered by the caller.

    Returns:
        str: Path of the XML file that was written.
    """
    # Import lazily so the gallery module doesn't pull in XmlService
    # (and its dependencies) at import time.
    from core.services.XmlService import XmlService

    os.makedirs(out_dir, exist_ok=True)
    xml = XmlService()
    xml.xml_path = os.path.join(out_dir, RESULTS_XML)

    # Settings block — fields are required by the image-mode loader
    # even though they're meaningless for a Flight Viewer export.
    settings = {
        "output_dir": out_dir,
        "input_dir": out_dir,
        "num_processes": 1,
        "identifier_color": (0, 255, 0),
        "aoi_radius": 20,
        "min_area": 1,
        "max_area": 0,
        "hist_ref_path": "",
        "kmeans_clusters": 0,
        "algorithm": "FlightViewer",
        "thermal": "False",
        "options": {
            "exported_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "source": "ADIAT Flight Viewer",
        },
    }
    # XmlService.add_settings_to_xml is the dedicated path for writing
    # settings into the new tree.
    xml.add_settings_to_xml(**settings)

    # One ``image`` per detection. The image's areas_of_interest
    # captures the bbox (in fractional coords) and the GPS location
    # so the standard viewer can re-render the pin + AOI overlay.
    for idx, detection in enumerate(rows):
        thumb_path = write_gallery_thumb(out_dir, idx, detection)
        img_record = {
            "path": thumb_path,
            "width": 0,
            "height": 0,
            "aois": [build_gallery_aoi(detection)],
        }
        xml.add_image_to_xml(img_record)

    xml.save_xml_file(xml.xml_path)
    return xml.xml_path


def write_gallery_thumb(out_dir: str, idx: int, detection: dict) -> str:
    """Write the detection's thumbnail (or a placeholder) and return its path."""
    thumb_bytes = detection.get("thumb_bytes")
    filename = f"detection_{idx:04d}.jpg"
    thumb_path = os.path.join(out_dir, filename)
    if isinstance(thumb_bytes, (bytes, bytearray)) and thumb_bytes:
        with open(thumb_path, "wb") as fp:
            fp.write(thumb_bytes)
    else:
        # No thumbnail in the snapshot — encode a tiny 1x1 black JPEG
        # so the XML loader doesn't choke on a missing file.
        placeholder = np.zeros((1, 1, 3), dtype=np.uint8)
        ok, buf = cv2.imencode(".jpg", placeholder)
        if ok:
            with open(thumb_path, "wb") as fp:
                fp.write(buf.tobytes())
        else:
            # Last-resort: write the minimal SOI+EOI marker pair. Not a
            # valid renderable JPEG but enough to satisfy "file exists".
            with open(thumb_path, "wb") as fp:
                fp.write(b"\xff\xd8\xff\xd9")
    return thumb_path


def build_gallery_aoi(detection: dict) -> dict:
    """Compose a single areas_of_interest entry for ``detection``.

    Kept separate from :func:`build_aoi`: that one takes pixel ``bbox``
    plus a ``thumbnail_origin``, this one fractional ``bbox_norm``
    against a synthetic reference frame. Merging them would need a
    caller to say which convention it is using, which is the bug.
    """
    bbox = detection.get("bbox_norm") or []
    # Default to a small AOI in the center of a synthetic 256x256 frame
    # so the image-mode viewer can render a pin even when bbox is missing.
    if isinstance(bbox, (list, tuple)) and len(bbox) >= 4:
        try:
            # Translate normalized bbox into a center+radius pair.
            # `bbox_norm` is [x_min, y_min, w, h] in 0..1 coords; we
            # synthesize against a 256x256 reference so the AOI lands
            # somewhere recognisable in the exported placeholder JPEG.
            w_ref, h_ref = 256, 256
            cx = int((float(bbox[0]) + float(bbox[2]) / 2.0) * w_ref)
            cy = int((float(bbox[1]) + float(bbox[3]) / 2.0) * h_ref)
            radius = max(8, int(min(bbox[2], bbox[3]) * min(w_ref, h_ref) / 2.0))
            area = int(float(bbox[2]) * float(bbox[3]) * w_ref * h_ref)
        except (TypeError, ValueError):
            cx, cy, radius, area = 128, 128, 20, 100
    else:
        cx, cy, radius, area = 128, 128, 20, 100

    aoi = {
        "center": (cx, cy),
        "radius": radius,
        "area": area,
    }
    confidence = detection.get("confidence")
    if isinstance(confidence, (int, float)):
        aoi["confidence"] = float(confidence)
        aoi["score_type"] = "confidence"
        aoi["raw_score"] = float(confidence)
        aoi["score_method"] = "FlightViewer"

    loc = detection.get("location")
    if isinstance(loc, dict):
        lat = loc.get("lat")
        lon = loc.get("lon")
        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
            comment = f"GPS: {lat:.6f}, {lon:.6f}"
            cls = detection.get("class_name") or detection.get("detector_id") or ""
            if cls:
                comment = f"{cls} @ {comment}"
            aoi["user_comment"] = comment

    return aoi
