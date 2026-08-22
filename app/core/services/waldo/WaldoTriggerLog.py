"""
WaldoTriggerLog - Authoritative per-image heading from the WALDO trigger KML.

WALDO ground software writes a ``<flight>_Triggers.kml`` next to the flight's
image folders: one ``<Placemark>`` per camera trigger, named after the image
(``000_12_035`` for images ``0_000_12_035.jpg`` / ``1_000_12_035.jpg``) and
positioned where the trigger fired. Crucially the placemarks appear in
CAPTURE ORDER, not filename order: WALDO flights are flown serpentine
(alternating lanes flown in opposite directions while frame numbers ascend
in a fixed geographic direction) and any skipped frames may be re-flown at
the end of the flight travelling the other way. Filename order therefore
does NOT recover the flight direction, and EXIF timestamps do so only when
the camera clock behaved. The trigger log is the ground truth for both the
capture sequence and the trigger positions.

This module parses that log and derives a per-image plane heading from the
document-order neighbours of each trigger, giving every image a heading
accurate to a few degrees regardless of serpentine lanes, recapture passes,
or camera-clock faults.

Real-world tolerances baked in:
- files may be truncated mid-coordinates (the logger does not always close
  its tags) - parsing reads to EOF;
- placemark names carry trailing whitespace;
- trigger names are NOT globally unique across flights (every flight numbers
  lanes from zero), so discovery validates candidates by GPS proximity, not
  by name alone.
"""

import glob
import math
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from helpers.LocationInfo import LocationInfo

from core.services.LoggerService import LoggerService

# Consecutive triggers in a lane are ~150-250 m apart; anything beyond this is
# a lane-change turn or a jump to a recapture site and must not contribute to
# a bearing.
TRIGGER_NEIGHBOR_MAX_M = 600.0

# Consecutive segment bearings turning harder than this split the capture
# sequence into separate runs. Distance alone cannot detect a tight
# serpentine turn: adjacent lanes can sit closer together than
# TRIGGER_NEIGHBOR_MAX_M, making the turn segment look like lane spacing.
TRIGGER_TURN_BREAK_DEG = 60.0

# An image matches a trigger only when its EXIF GPS lies within this distance
# of the trigger position (observed misfit on field data: ~12 m median).
TRIGGER_MATCH_MAX_M = 300.0

# A candidate KML must position-match at least this fraction of the images
# before it is trusted as the flight's trigger log.
TRIGGER_MIN_MATCH_FRACTION = 0.5

# Doc order is trusted as capture order only when the EXIF timestamps of
# matched images agree with it at least this often (constant clock offsets do
# not affect the comparison; it only checks monotonicity).
TRIGGER_MIN_CHRONOLOGY_FRACTION = 0.8

# How many directory levels above the images to search for candidate KMLs
# (field layout: <root>/<flight>_Triggers.kml with images in
# <root>/<flight>/batch<N>/).
TRIGGER_SEARCH_LEVELS = 3


@dataclass
class TriggerPoint:
    """One camera trigger from the log, in document (= capture) order."""
    name: str
    lat: float
    lon: float
    alt: Optional[float]


class WaldoTriggerLogService:
    """Parse WALDO trigger KMLs and derive per-image headings from them."""

    def __init__(self):
        self.logger = LoggerService()

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    @staticmethod
    def parse_triggers_kml(path: str) -> List[TriggerPoint]:
        """Return the trigger points of a KML in document order.

        Tolerates truncated files and malformed placemarks (skipped).
        Returns [] when the file is unreadable or contains no point placemarks.
        """
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                text = f.read()
        except OSError:
            return []

        points: List[TriggerPoint] = []
        pattern = re.compile(
            r'<Placemark>\s*<name>([^<]+)</name>.*?'
            r'<Point>.*?<coordinates>([^<]*)',
            re.S)
        for m in pattern.finditer(text):
            name = m.group(1).strip()
            coords = m.group(2).strip().split(',')
            try:
                lon = float(coords[0])
                lat = float(coords[1])
                alt = float(coords[2]) if len(coords) > 2 else None
            except (ValueError, IndexError):
                continue
            points.append(TriggerPoint(name=name, lat=lat, lon=lon, alt=alt))
        return points

    @staticmethod
    def image_trigger_name(image_name: str) -> Optional[str]:
        """Map a WALDO image filename to its trigger placemark name.

        ``0_000_12_035.jpg`` -> ``000_12_035`` (cam prefix stripped; both
        cameras share one trigger). Returns None for non-WALDO names.
        """
        base = os.path.splitext(os.path.basename(image_name))[0]
        m = re.match(r'^[01]_(.+)$', base)
        if not m:
            return None
        return m.group(1)

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def discover(self, records: Sequence) -> Optional[Tuple[str, List[TriggerPoint]]]:
        """Find the trigger KML for a set of WaldoImageRecords, if any.

        Searches the image directories and up to TRIGGER_SEARCH_LEVELS parent
        levels for ``*.kml`` files, and scores each candidate by the fraction
        of records it matches BY NAME AND GPS POSITION. Position matching is
        essential: every flight numbers its lanes from zero, so a sibling
        flight's log can contain the same trigger names at different places.

        Returns (kml_path, triggers) for the best candidate above
        TRIGGER_MIN_MATCH_FRACTION, or None.
        """
        usable = [r for r in records if r.lat is not None and r.lon is not None]
        if not usable:
            return None

        candidates: List[str] = []
        seen_dirs = set()
        for rec in usable:
            d = os.path.dirname(os.path.abspath(rec.path))
            for _ in range(TRIGGER_SEARCH_LEVELS + 1):
                if d in seen_dirs:
                    break
                seen_dirs.add(d)
                candidates.extend(sorted(glob.glob(os.path.join(d, '*.kml'))))
                parent = os.path.dirname(d)
                if parent == d:
                    break
                d = parent

        best: Optional[Tuple[str, List[TriggerPoint]]] = None
        best_score = 0.0
        for kml_path in dict.fromkeys(candidates):  # dedupe, keep order
            triggers = self.parse_triggers_kml(kml_path)
            if not triggers:
                continue
            by_name = {t.name: t for t in triggers}
            matched = 0
            for rec in usable:
                tname = self.image_trigger_name(rec.name)
                trig = by_name.get(tname) if tname else None
                if trig is None:
                    continue
                dist = LocationInfo.haversine_m(rec.lat, rec.lon, trig.lat, trig.lon)
                if dist <= TRIGGER_MATCH_MAX_M:
                    matched += 1
            score = matched / len(usable)
            if score > best_score:
                best_score = score
                best = (kml_path, triggers)

        if best is None or best_score < TRIGGER_MIN_MATCH_FRACTION:
            return None
        self.logger.info(
            f"WALDO trigger log: {best[0]} matched "
            f"{best_score:.0%} of {len(usable)} images")
        return best

    # ------------------------------------------------------------------
    # Heading derivation
    # ------------------------------------------------------------------

    @staticmethod
    def headings_by_name(triggers: List[TriggerPoint]) -> Dict[str, float]:
        """Per-trigger plane heading from document-order neighbours.

        The capture sequence is first split into straight RUNS. A run break
        occurs at any segment that is too long / too short to be in-lane
        spacing, or that turns harder than TRIGGER_TURN_BREAK_DEG relative
        to the run's direction (a tight serpentine turn can bring the next
        lane closer than the distance guard alone would catch). Headings
        never cross a run boundary: interior triggers use the chord
        bearing(prev -> next), run-edge triggers the one in-run segment,
        and singleton runs (an isolated recapture) get no heading - the
        caller keeps its timestamp-derived fallback there.
        """
        n = len(triggers)
        if n == 0:
            return {}

        # Segment i connects trigger i to trigger i+1. None = unusable.
        seg_bearing: List[Optional[float]] = [None] * (n - 1)
        for i in range(n - 1):
            a, b = triggers[i], triggers[i + 1]
            dist = LocationInfo.haversine_m(a.lat, a.lon, b.lat, b.lon)
            if not (1.0 < dist < TRIGGER_NEIGHBOR_MAX_M):
                continue
            brg = LocationInfo.bearing(a.lat, a.lon, b.lat, b.lon)
            if not math.isnan(brg):
                seg_bearing[i] = brg % 360.0

        # Assign run ids. After a break the new run's direction is unknown
        # (the breaking segment belongs to the turn, not to either lane),
        # so it seeds from the first good segment inside the new run.
        run_id = [0] * n
        current = 0
        run_dir: Optional[float] = None
        for i in range(1, n):
            sb = seg_bearing[i - 1]
            turned = (
                sb is not None and run_dir is not None
                and abs((sb - run_dir + 180.0) % 360.0 - 180.0) > TRIGGER_TURN_BREAK_DEG
            )
            if sb is None or turned:
                current += 1
                run_dir = None
            else:
                run_dir = sb
            run_id[i] = current

        headings: Dict[str, float] = {}
        for i, trig in enumerate(triggers):
            # Adjacent same-run triggers always have a usable segment between
            # them (an unusable segment forces a run break).
            prev_in_run = i > 0 and run_id[i - 1] == run_id[i]
            next_in_run = i < n - 1 and run_id[i + 1] == run_id[i]
            if prev_in_run and next_in_run:
                heading = LocationInfo.bearing(
                    triggers[i - 1].lat, triggers[i - 1].lon,
                    triggers[i + 1].lat, triggers[i + 1].lon)
            elif prev_in_run:
                heading = seg_bearing[i - 1]
            elif next_in_run:
                heading = seg_bearing[i]
            else:
                continue
            if heading is not None and not math.isnan(heading):
                headings[trig.name] = heading % 360.0
        return headings

    @staticmethod
    def chronology_fraction(triggers: List[TriggerPoint],
                            records: Sequence) -> Optional[float]:
        """Fraction of doc-adjacent trigger pairs whose EXIF timestamps
        are non-decreasing.

        Guards against a hypothetical log written in name order rather than
        capture order: a serpentine flight would then get half its lanes
        flipped, which is worse than the timestamp-based fallback. Constant
        camera-clock offsets (the known WALDO AM/PM + timezone faults) shift
        every timestamp equally and do not affect the check.

        Returns None when fewer than 3 comparable pairs exist.
        """
        ts_by_trigger: Dict[str, object] = {}
        for rec in records:
            if rec.timestamp is None:
                continue
            tname = WaldoTriggerLogService.image_trigger_name(rec.name)
            if tname is None:
                continue
            # Prefer cam 0's clock; either cam alone is self-consistent.
            if tname not in ts_by_trigger or rec.cam_idx == 0:
                ts_by_trigger[tname] = rec.timestamp

        ordered = [ts_by_trigger[t.name] for t in triggers if t.name in ts_by_trigger]
        if len(ordered) < 4:
            return None
        pairs = len(ordered) - 1
        good = sum(1 for a, b in zip(ordered, ordered[1:]) if b >= a)
        return good / pairs
