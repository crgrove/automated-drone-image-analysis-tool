"""Parser for DJI SRT telemetry, in both sidecar and embedded variants.

DJI aircraft record per-frame telemetry as SubRip text. The payload is a
run of bracketed ``[key: value]`` tokens, but the surrounding structure
varies by model and firmware, and the same data reaches ADIAT by two
routes:

* **Sidecar** — a ``.SRT`` written next to the ``.MP4`` on the card.
* **Embedded** — a ``tx3g`` / ``mov_text`` subtitle track inside the MP4
  itself (see :func:`helpers.VideoFileHelper.extract_embedded_subtitles`).
  Newer aircraft write only this, so an operator who copies just the
  ``.MP4`` has telemetry that older ADIAT builds could not see.

Two shapes are common, and both must parse:

*Classic sidecar* (5+ lines, HTML-wrapped, telemetry on line index 4)::

    1
    00:00:00,000 --> 00:00:00,033
    <font size="28">FrameCnt: 1, DiffTime: 33ms
    2023-05-01 10:00:00,000
    [iso: 100] [latitude: 30.1] [longitude: -97.2] [altitude: 210.0] </font>

*Embedded / newer firmware* (4 lines, timestamp folded onto the FrameCnt
line, telemetry on line index 3)::

    1
    00:00:00,000 --> 00:00:00,033
    FrameCnt: 0 2026-07-25 14:38:26.477
    [iso: 120] [latitude: 30.648730] [longitude: -97.675867]
    [rel_alt: 14.885 abs_alt: 207.027] [gb_yaw: -161.5 ...]

The previous implementation indexed line 4 and required 5+ lines, so the
embedded variant parsed to **zero** samples. It also split each bracket
on the first ``:``, which mangles DJI's multi-pair brackets — in
``[rel_alt: 14.885 abs_alt: 207.027]`` the key ``rel_alt`` captured
``"14.885 abs_alt"`` and altitude silently fell back to 0.

This module therefore:

* scans **every** line of an entry for bracketed tokens rather than
  trusting a fixed index, and tolerates 3-line entries;
* tokenizes with a key/value regex so multi-pair brackets split
  correctly;
* distinguishes MSL (``abs_alt``) from ATO (``rel_alt`` — above the
  takeoff point, never height above the terrain) instead of
  collapsing both into one ``altitude``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from core.services.telemetry.VideoProfileService import DATUM_MSL, DATUM_RELATIVE

# A bracketed run, e.g. ``[rel_alt: 14.885 abs_alt: 207.027]``. Non-greedy
# so adjacent brackets on one line stay separate.
_BRACKET_RE = re.compile(r"\[(.+?)\]")

# One ``key: value`` pair inside a bracket. The value stops at whitespace
# so a bracket carrying several pairs yields several matches. Values may
# carry units or slashes (``1/1250.0``), hence the broad value class.
_KEY_VALUE_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([^\s\]]+)")

# ``00:00:01,234 --> 00:00:01,267``
_TIMECODE_RE = re.compile(
    r"(\d{1,2}:\d{2}:\d{2}[,.]\d{1,3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}[,.]\d{1,3})"
)

# Entries are separated by one or more blank lines.
_ENTRY_SPLIT_RE = re.compile(r"(?:\r?\n){2,}")

# DJI stamps each cue with the aircraft's own wall clock, e.g.
# ``2026-08-15 12:09:26,347`` on its own line in the classic sidecar, or
# folded onto the FrameCnt line in the embedded variant. Found by scanning
# the whole block so either placement works.
_WALL_CLOCK_RE = re.compile(
    r"(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?)"
)

# Tried in order against the matched wall-clock text.
_WALL_CLOCK_FORMATS = (
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S,%f",
    "%Y-%m-%d %H:%M:%S",
)

# Below this, a legacy ``altitude`` track is read as takeoff-relative rather
# than MSL. See _resolve_legacy_altitude for why the threshold is safe.
_LEGACY_RELATIVE_CEILING_M = 50.0


@dataclass
class DjiSrtSample:
    """One parsed SRT cue.

    Times are **seconds from the start of the video**, which is what both
    the frame-extraction path and streaming playback need; the original
    code carried ``datetime`` objects anchored to 1900-01-01, which only
    worked because both sides used the same fake epoch.
    """

    start_seconds: float
    end_seconds: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude_msl_m: Optional[float] = None   # abs_alt — above mean sea level
    # ``rel_alt``: above the takeoff point (ATO). The value does not change
    # when the terrain beneath the aircraft rises, so it is never an AGL.
    # It reaches the HUD on the wire key ``aircraft_altitude_agl_m``, whose
    # name is kept for compatibility and has always carried ATO; nothing
    # inside ADIAT calls this quantity "agl" (CLAUDE.md § 2.11).
    altitude_ato_m: Optional[float] = None
    yaw_deg: Optional[float] = None          # gimbal yaw; see module note below
    frame_index: Optional[int] = None
    # The aircraft's own wall clock for this cue, in drone local time.
    # Distinct from start_seconds, which is an offset into the video:
    # this is the datum a frame's EXIF capture time is written from.
    captured_at: Optional[datetime] = None
    # True when the altitude came from the legacy single ``altitude`` key,
    # whose datum varies by aircraft. See _resolve_legacy_altitude.
    altitude_datum_unknown: bool = False

    @property
    def has_position(self) -> bool:
        """True when both coordinates parsed — the minimum useful fix."""
        return self.latitude is not None and self.longitude is not None


def parse_timecode(value: str) -> Optional[float]:
    """Convert ``HH:MM:SS,mmm`` to seconds. Returns None if unparseable."""
    if not value:
        return None
    text = value.strip().replace(".", ",")
    match = re.match(r"^(\d{1,2}):(\d{2}):(\d{2}),(\d{1,3})$", text)
    if not match:
        return None
    hours, minutes, seconds, millis = match.groups()
    # Pad so ",5" reads as 500 ms rather than 5 ms.
    millis_padded = millis.ljust(3, "0")
    return (
        int(hours) * 3600
        + int(minutes) * 60
        + int(seconds)
        + int(millis_padded) / 1000.0
    )


def parse_wall_clock(text: str) -> Optional[datetime]:
    """Absolute capture time from a cue's date stamp, or None.

    Returns drone *local* time — DJI writes the aircraft's clock, not UTC.
    Callers must not mix it with times derived from the MP4 container,
    which are UTC.
    """
    if not text:
        return None
    match = _WALL_CLOCK_RE.search(text)
    if not match:
        return None
    stamp = match.group(1).replace("T", " ")
    for time_format in _WALL_CLOCK_FORMATS:
        try:
            return datetime.strptime(stamp, time_format)
        except ValueError:
            continue
    # Sub-second field present but unparseable (DJI has written 6+ digits
    # and comma-grouped triples); the whole-second prefix is still good.
    try:
        return datetime.strptime(stamp[:19], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def _to_float(value: Optional[str]) -> Optional[float]:
    """Best-effort float conversion tolerating trailing units (``14.885m``)."""
    if value is None:
        return None
    match = re.match(r"^[-+]?\d*\.?\d+", str(value).strip())
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def _to_int(value: Optional[str]) -> Optional[int]:
    number = _to_float(value)
    return int(number) if number is not None else None


def extract_fields(text: str) -> dict:
    """Pull every ``key: value`` pair out of every bracket in ``text``.

    Handles both one-pair brackets (``[latitude: 30.6]``) and DJI's
    multi-pair brackets (``[rel_alt: 14.885 abs_alt: 207.027]``), which
    the previous single-split approach corrupted.
    """
    fields: dict = {}
    for bracket in _BRACKET_RE.findall(text or ""):
        for key, value in _KEY_VALUE_RE.findall(bracket):
            fields[key.lower()] = value
    return fields


def _parse_entry(block: str) -> Optional[DjiSrtSample]:
    """Parse one SRT cue block, or return None if it carries no timecode."""
    lines = re.split(r"\r?\n", block.strip())
    if not lines:
        return None

    start_seconds = end_seconds = None
    frame_index = None
    for line in lines:
        match = _TIMECODE_RE.search(line)
        if match:
            start_seconds = parse_timecode(match.group(1))
            end_seconds = parse_timecode(match.group(2))
            break

    if start_seconds is None:
        return None
    if end_seconds is None:
        end_seconds = start_seconds

    # FrameCnt may sit on its own line or share one with the wall clock.
    frame_match = re.search(r"FrameCnt\s*:?\s*(\d+)", block, re.IGNORECASE)
    if frame_match:
        frame_index = int(frame_match.group(1))

    # Scan the WHOLE block for bracketed telemetry rather than assuming a
    # fixed line index — this is what makes the 4-line embedded variant
    # and the 5-line sidecar variant both work.
    fields = extract_fields(block)

    longitude = _to_float(fields.get("longitude"))
    if longitude is None:
        # Some firmware misspells the key; preserved from the original parser.
        longitude = _to_float(fields.get("longtitude"))

    # Altitude precedence: DJI's explicit MSL/ATO pair when present,
    # otherwise the legacy single ``altitude`` key. That key's datum is not
    # knowable from one cue, so it is parked in the MSL slot and flagged;
    # :func:`_resolve_legacy_altitude` decides once it can see the whole
    # track.
    altitude_msl = _to_float(fields.get("abs_alt"))
    altitude_ato = _to_float(fields.get("rel_alt"))
    datum_unknown = False
    if altitude_msl is None and altitude_ato is None:
        altitude_msl = _to_float(fields.get("altitude"))
        datum_unknown = altitude_msl is not None

    return DjiSrtSample(
        start_seconds=start_seconds,
        end_seconds=end_seconds,
        latitude=_to_float(fields.get("latitude")),
        longitude=longitude,
        altitude_msl_m=altitude_msl,
        altitude_ato_m=altitude_ato,
        # NB: ``gb_yaw`` is the *gimbal* yaw, not the airframe heading. It
        # is the only bearing DJI's SRT carries, so consumers surface it as
        # heading with that caveat.
        yaw_deg=_to_float(fields.get("gb_yaw")),
        frame_index=frame_index,
        altitude_datum_unknown=datum_unknown,
        # Scanned from the whole block, not a fixed line index, so the
        # sidecar and embedded layouts both yield a time.
        captured_at=parse_wall_clock(block),
    )


def _resolve_legacy_altitude(
    samples: List[DjiSrtSample],
    altitude_datum: Optional[str] = None,
) -> None:
    """Decide whether a legacy ``altitude`` key is MSL or takeoff-relative.

    Older DJI firmware writes one ``altitude`` value with no datum, and the
    datum is **not consistent between aircraft** — verified against four
    sample tracks, three relative (one starting at −9.7 m) and one Mavic 2
    Pro genuinely MSL at 1622 m. Modern firmware removed the ambiguity by
    writing the explicit ``rel_alt``/``abs_alt`` pair instead, so this only
    applies to legacy files.

    Filing a relative altitude as MSL is not cosmetic: the HUD labels it
    "MSL" and leaves ATO blank, the wizard's altitude auto-detection reads
    ATO only and so finds nothing, and
    :class:`~core.services.telemetry.TelemetryEnrichmentService.\
TelemetryEnrichmentService` needs a reported AGL to anchor its DEM
    correction — without one there is no terrain correction at all.

    Args:
        samples: Parsed cues, mutated in place.
        altitude_datum: The datum recorded for this aircraft in
            ``drones.csv`` (see :mod:`~core.services.telemetry.\
VideoProfileService`). When given it is authoritative. When None — an
            unrecorded aircraft, or a remuxed video that no longer names
            itself — the datum is inferred from the track minimum instead.

    Inference is a fallback, not the primary answer, because it is a guess.
    It is nonetheless a safe one: a drone's *MSL* altitude can only dip
    below ~50 m where the ground itself is near sea level, and at those
    elevations the two readings differ by less than the threshold anyway,
    so a wrong call costs less than the threshold that produced it. No DEM
    lookup, so this stays off the network.
    """
    ambiguous = [s for s in samples if s.altitude_datum_unknown]
    if not ambiguous:
        return

    if altitude_datum == DATUM_MSL:
        # Already parked in the MSL slot; nothing to move.
        return
    if altitude_datum != DATUM_RELATIVE:
        values = [s.altitude_msl_m for s in ambiguous if s.altitude_msl_m is not None]
        if not values or min(values) >= _LEGACY_RELATIVE_CEILING_M:
            return

    for sample in ambiguous:
        sample.altitude_ato_m = sample.altitude_msl_m
        sample.altitude_msl_m = None


def parse_dji_srt(text: str, altitude_datum: Optional[str] = None) -> List[DjiSrtSample]:
    """Parse DJI SRT content into samples ordered by start time.

    Malformed cues are skipped rather than aborting the whole file — a
    single truncated entry at the end of a card-pull should not cost the
    operator the other 890 fixes.

    Args:
        text: SRT content.
        altitude_datum: Datum recorded for the capturing aircraft, if
            known. Only consulted for legacy single-``altitude`` tracks;
            see :func:`_resolve_legacy_altitude`.
    """
    if not text:
        return []

    samples: List[DjiSrtSample] = []
    for block in _ENTRY_SPLIT_RE.split(text):
        if not block.strip():
            continue
        try:
            sample = _parse_entry(block)
        except Exception:  # noqa: BLE001 - one bad cue must not kill the file
            continue
        if sample is not None:
            samples.append(sample)

    samples.sort(key=lambda s: s.start_seconds)
    # Deferred to here because inference needs the whole track: one cue
    # cannot reveal which datum a legacy ``altitude`` key is using.
    _resolve_legacy_altitude(samples, altitude_datum)
    return samples
