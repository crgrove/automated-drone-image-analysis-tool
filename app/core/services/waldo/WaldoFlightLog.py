"""
WaldoFlightLog - Per-image aircraft attitude from a ForeFlight track log.

ForeFlight (the pilot's EFB app) exports a per-second track log CSV with the
aircraft position, ground course, ground speed, and - when an attitude source
is available (device sensors or an external AHRS such as a Sentry) - bank and
pitch. WALDO cameras are rigidly mounted to the airframe, so this is the first
data source that lets the pre-pass stamp TRUE per-image camera attitude
instead of assuming a level airframe.

File format (verified on field data, 2026-08-07 N183CP sortie):
    row 1: flight-summary header (starts ``Pilot,Tail Number,...``)
    row 2: summary values (timestamps in epoch MILLISECONDS)
    row 3: point header ``Timestamp,Latitude,Longitude,Altitude,Course,
           Speed,Bank,Pitch,Horizontal Error,Vertical Error``
    rows 4+: points - epoch SECONDS (float, often scientific notation),
           Altitude in feet, Speed in KNOTS, Course in degrees true with
           -1 meaning invalid (stationary), Bank + = right wing down,
           Pitch + = nose up.

Two calibrations are solved before the log is trusted (both field-verified):

Clock offset - the pod camera clock is not GPS-disciplined (measured 17 s
fast on field data). The offset is fit by sliding the folder's capture times
against the log and minimising the distance between each image's EXIF GPS
and the interpolated track position. A good fit (residual at GPS noise
level) doubles as proof that this log belongs to this folder; a bad fit
rejects the pairing.

Attitude lag - ForeFlight's attitude channel is recorded LATE relative to
its GPS channel (~4-5 s on field data; the AHRS filter and logging path
delay it). The lag is fit by cross-correlating logged bank against the bank
a coordinated turn would need for the observed course rate
(tan(bank) = v*omega/g). Without the fitted lag the bank samples decorrelate
from the capture instants; with it, correlation reached 0.89-0.97 on field
data. A low peak correlation means the attitude channel is unusable
(hand-held phone, no attitude source) and only the clock refinement is kept.
"""

import csv
import glob
import hashlib
import math
import os
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

from helpers.LocationInfo import LocationInfo

from core.services.LoggerService import LoggerService

# First cells of row 1 that identify a ForeFlight track-log export.
FLIGHTLOG_SNIFF_PREFIX = "Pilot,Tail Number"

KNOTS_TO_MPS = 0.514444
FEET_TO_M = 0.3048
GRAVITY_MPS2 = 9.80665

# Clock-offset fit: coarse scan range/step, then a fine pass around the best
# coarse offset. The pod clock error observed in the field is tens of
# seconds; +/-120 s leaves generous margin without risking a false lock onto
# a different lane pass.
CLOCK_SCAN_RANGE_S = 120.0
CLOCK_SCAN_STEP_S = 1.0
CLOCK_FINE_RANGE_S = 2.0
CLOCK_FINE_STEP_S = 0.1
# Accept the fit only when images sit this close to the track on average
# (GPS + interpolation noise measured 13-20 m; 50 m keeps margin without
# accepting a neighbouring-lane false lock at typical 150-300 m lane pitch).
CLOCK_FIT_MAX_MEAN_DIST_M = 50.0
# The fit subsamples large folders: this many images spread evenly is plenty
# to lock a single scalar offset.
CLOCK_FIT_MAX_SAMPLES = 60

# Attitude-lag fit tunables.
LAG_SCAN_RANGE_S = 10
LAG_MIN_CORRELATION = 0.7
# Course-rate bank prediction is only meaningful in flight.
LAG_MIN_SPEED_MPS = 20.0
# Box half-width (seconds) for smoothing both series before correlating;
# kills 1 Hz differencing noise without erasing the turn structure.
LAG_SMOOTH_HALF_WIDTH_S = 2

# Interpolating across a logging dropout longer than this is guessing.
MAX_INTERP_GAP_S = 5.0

# Directory levels above the images searched for candidate CSVs (same field
# layout rationale as WaldoTriggerLog.TRIGGER_SEARCH_LEVELS).
FLIGHTLOG_SEARCH_LEVELS = 3


@dataclass
class FlightLogTrack:
    """A parsed ForeFlight track log as parallel per-point arrays.

    ``course`` entries are None where ForeFlight logged -1 (invalid).
    All arrays share indices and are strictly time-ordered.
    """
    path: str
    t: List[float] = field(default_factory=list)            # epoch seconds
    lat: List[float] = field(default_factory=list)
    lon: List[float] = field(default_factory=list)
    alt_m: List[float] = field(default_factory=list)
    course: List[Optional[float]] = field(default_factory=list)
    speed_mps: List[float] = field(default_factory=list)
    bank: List[float] = field(default_factory=list)
    pitch: List[float] = field(default_factory=list)

    def __len__(self):
        return len(self.t)

    @property
    def t_start(self) -> float:
        return self.t[0]

    @property
    def t_end(self) -> float:
        return self.t[-1]


@dataclass
class AttitudeSample:
    """Interpolated aircraft state at one capture instant."""
    in_coverage: bool
    bank_deg: Optional[float] = None
    pitch_deg: Optional[float] = None
    course_deg: Optional[float] = None


@dataclass
class FlightLogFit:
    """Result of calibrating a track log against one image folder."""
    log_path: str
    log_sha256: str
    accepted: bool
    reason: str = ""
    clock_offset_s: float = 0.0
    mean_track_dist_m: float = float('inf')
    matched_fraction: float = 0.0
    attitude_reliable: bool = False
    attitude_lag_s: float = 0.0
    lag_correlation: float = 0.0
    bank_min_deg: float = 0.0
    bank_max_deg: float = 0.0


def _bracket(times: Sequence[float], t: float) -> int:
    """Index i of the last point with times[i] <= t (binary search).

    Returns -1 before the first point and len-1 at/after the last.
    Mirrors the search shape of BearingCalculationService._find_bracket_index.
    """
    lo, hi = 0, len(times) - 1
    if t < times[0]:
        return -1
    if t >= times[hi]:
        return hi
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if times[mid] <= t:
            lo = mid
        else:
            hi = mid
    return lo


def _lerp_angle(a: float, b: float, f: float) -> float:
    """Circular linear interpolation between bearings a and b (degrees)."""
    delta = (b - a + 180.0) % 360.0 - 180.0
    return (a + f * delta) % 360.0


def _box_smooth(values: List[float], half_width: int) -> List[float]:
    """Centered box smoothing; plain lists, edges shrink the window."""
    if half_width <= 0:
        return list(values)
    out = []
    n = len(values)
    for i in range(n):
        lo = max(0, i - half_width)
        hi = min(n, i + half_width + 1)
        out.append(sum(values[lo:hi]) / (hi - lo))
    return out


def _correlation(a: List[float], b: List[float]) -> float:
    """Pearson correlation; 0.0 when either series is flat."""
    n = len(a)
    if n < 3:
        return 0.0
    ma = sum(a) / n
    mb = sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a) / n)
    sb = math.sqrt(sum((y - mb) ** 2 for y in b) / n)
    if sa < 1e-9 or sb < 1e-9:
        return 0.0
    return cov / (sa * sb)


class WaldoFlightLogService:
    """Parse ForeFlight track logs and calibrate them to WALDO image folders."""

    def __init__(self):
        self.logger = LoggerService()

    # ------------------------------------------------------------------
    # Discovery + parsing
    # ------------------------------------------------------------------

    @staticmethod
    def sniff(path: str) -> bool:
        """True when the file's first line identifies a ForeFlight export."""
        try:
            with open(path, 'r', encoding='utf-8-sig', errors='replace') as f:
                first = f.readline()
        except OSError:
            return False
        return first.strip().startswith(FLIGHTLOG_SNIFF_PREFIX)

    @staticmethod
    def candidate_files(image_dir: str) -> List[str]:
        """ForeFlight CSVs in the image folder or up to FLIGHTLOG_SEARCH_LEVELS parents."""
        candidates: List[str] = []
        d = os.path.abspath(image_dir)
        seen = set()
        for _ in range(FLIGHTLOG_SEARCH_LEVELS + 1):
            if d in seen:
                break
            seen.add(d)
            for path in sorted(glob.glob(os.path.join(d, '*.csv'))):
                if WaldoFlightLogService.sniff(path):
                    candidates.append(path)
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent
        return candidates

    @staticmethod
    def content_hash(path: str) -> str:
        """SHA-256 of the log file content (identity survives copies/moves)."""
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(1 << 20), b''):
                h.update(chunk)
        return h.hexdigest()

    def parse(self, path: str) -> Optional[FlightLogTrack]:
        """Parse a ForeFlight track log; None when unusable.

        Tolerates truncated tails and malformed rows (skipped). Rejects
        non-ForeFlight files and logs with fewer than 2 usable points.
        """
        if not self.sniff(path):
            return None
        track = FlightLogTrack(path=path)
        try:
            with open(path, 'r', encoding='utf-8-sig', errors='replace', newline='') as f:
                reader = csv.reader(f)
                in_points = False
                for row in reader:
                    if not row:
                        continue
                    if not in_points:
                        # The point header marks the start of point rows;
                        # everything before it is flight summary.
                        if row[0].strip().lower() == 'timestamp':
                            in_points = True
                        continue
                    if len(row) < 8:
                        continue
                    try:
                        t = float(row[0])
                        lat = float(row[1])
                        lon = float(row[2])
                        alt_ft = float(row[3])
                        course = float(row[4])
                        speed_kt = float(row[5])
                        bank = float(row[6])
                        pitch = float(row[7])
                    except ValueError:
                        continue
                    # Strictly increasing time keeps interpolation honest.
                    if track.t and t <= track.t[-1]:
                        continue
                    track.t.append(t)
                    track.lat.append(lat)
                    track.lon.append(lon)
                    track.alt_m.append(alt_ft * FEET_TO_M)
                    track.course.append(course if course >= 0.0 else None)
                    track.speed_mps.append(speed_kt * KNOTS_TO_MPS)
                    track.bank.append(bank)
                    track.pitch.append(pitch)
        except OSError:
            return None
        if len(track) < 2:
            return None
        return track

    # ------------------------------------------------------------------
    # Interpolation
    # ------------------------------------------------------------------

    @staticmethod
    def interpolate_position(track: FlightLogTrack, t: float) -> Optional[Tuple[float, float]]:
        """(lat, lon) at epoch t, or None outside coverage / across a gap."""
        i = _bracket(track.t, t)
        if i < 0 or i >= len(track) - 1:
            # Exactly at the final point still counts.
            if i == len(track) - 1 and abs(t - track.t[i]) < 1e-9:
                return (track.lat[i], track.lon[i])
            return None
        dt = track.t[i + 1] - track.t[i]
        if dt > MAX_INTERP_GAP_S:
            return None
        f = (t - track.t[i]) / dt
        return (
            track.lat[i] + f * (track.lat[i + 1] - track.lat[i]),
            track.lon[i] + f * (track.lon[i + 1] - track.lon[i]),
        )

    @staticmethod
    def sample_attitude(track: FlightLogTrack, t: float, lag_s: float) -> AttitudeSample:
        """Aircraft attitude at capture instant t.

        Bank/pitch are read at t + lag_s (the attitude channel is logged
        late; the fitted lag re-aligns it). Course is GPS-chained and read
        at t directly, circularly interpolated, None across invalid spans.
        """
        ta = t + lag_s
        i = _bracket(track.t, ta)
        sample = AttitudeSample(in_coverage=False)
        if 0 <= i < len(track) - 1:
            dt = track.t[i + 1] - track.t[i]
            if dt <= MAX_INTERP_GAP_S:
                f = (ta - track.t[i]) / dt
                sample.in_coverage = True
                sample.bank_deg = track.bank[i] + f * (track.bank[i + 1] - track.bank[i])
                sample.pitch_deg = track.pitch[i] + f * (track.pitch[i + 1] - track.pitch[i])
        elif i == len(track) - 1 and abs(ta - track.t[i]) < 1e-9:
            sample.in_coverage = True
            sample.bank_deg = track.bank[i]
            sample.pitch_deg = track.pitch[i]

        j = _bracket(track.t, t)
        if 0 <= j < len(track) - 1:
            c0 = track.course[j]
            c1 = track.course[j + 1]
            dt = track.t[j + 1] - track.t[j]
            if c0 is not None and c1 is not None and dt <= MAX_INTERP_GAP_S:
                f = (t - track.t[j]) / dt
                sample.course_deg = _lerp_angle(c0, c1, f)
        return sample

    # ------------------------------------------------------------------
    # Clock-offset fit
    # ------------------------------------------------------------------

    def fit_clock_offset(self, track: FlightLogTrack,
                         images: Sequence[Tuple[float, float, float]]) -> Tuple[float, float, float]:
        """Fit the capture-clock offset against the track.

        ``images`` is (capture_utc_epoch, lat, lon) per image; the corrected
        capture time is capture + offset. Returns (offset_s, mean_dist_m,
        matched_fraction) for the best offset - the caller judges acceptance.
        """
        usable = [im for im in images if im[1] is not None and im[2] is not None]
        if not usable:
            return (0.0, float('inf'), 0.0)
        step = max(1, len(usable) // CLOCK_FIT_MAX_SAMPLES)
        samples = usable[::step]

        def mean_dist(offset: float) -> Tuple[float, int]:
            total = 0.0
            hit = 0
            for t_img, lat, lon in samples:
                pos = self.interpolate_position(track, t_img + offset)
                if pos is None:
                    continue
                total += LocationInfo.haversine_m(lat, lon, pos[0], pos[1])
                hit += 1
            if hit == 0:
                return (float('inf'), 0)
            return (total / hit, hit)

        best_offset = 0.0
        best_dist = float('inf')
        offset = -CLOCK_SCAN_RANGE_S
        while offset <= CLOCK_SCAN_RANGE_S:
            d, hit = mean_dist(offset)
            # Require the offset to keep most samples inside the log; an
            # offset that pushes the folder off the log's end can look
            # artificially good on the few points that remain.
            if hit >= max(2, len(samples) // 2) and d < best_dist:
                best_dist = d
                best_offset = offset
            offset += CLOCK_SCAN_STEP_S

        fine = best_offset - CLOCK_FINE_RANGE_S
        while fine <= best_offset + CLOCK_FINE_RANGE_S:
            d, hit = mean_dist(fine)
            if hit >= max(2, len(samples) // 2) and d < best_dist:
                best_dist = d
                best_offset = fine
            fine += CLOCK_FINE_STEP_S

        matched = 0
        for t_img, lat, lon in usable:
            pos = self.interpolate_position(track, t_img + best_offset)
            if pos is not None and LocationInfo.haversine_m(lat, lon, pos[0], pos[1]) <= CLOCK_FIT_MAX_MEAN_DIST_M:
                matched += 1
        return (best_offset, best_dist, matched / len(usable))

    # ------------------------------------------------------------------
    # Attitude-lag fit
    # ------------------------------------------------------------------

    def fit_attitude_lag(self, track: FlightLogTrack,
                         t0: float, t1: float) -> Tuple[float, float]:
        """Fit the attitude channel's lag over window [t0, t1].

        Cross-correlates logged bank against coordinated-turn bank predicted
        from the GPS course rate. Returns (lag_s, peak_correlation); the
        caller compares the correlation against LAG_MIN_CORRELATION.
        """
        # Build a uniform 1 Hz grid over the (padded) window so integer
        # shifts are exact seconds.
        pad = float(LAG_SCAN_RANGE_S)
        g0 = max(track.t_start, t0 - pad)
        g1 = min(track.t_end, t1 + pad)
        n = int(g1 - g0)
        if n < 30:
            return (0.0, 0.0)

        pred: List[float] = []
        logged: List[float] = []
        for k in range(n):
            t = g0 + k
            i = _bracket(track.t, t)
            if i < 1 or i >= len(track) - 1:
                pred.append(0.0)
                logged.append(0.0)
                continue
            c0 = track.course[i - 1]
            c1 = track.course[i + 1]
            dt = track.t[i + 1] - track.t[i - 1]
            v = track.speed_mps[i]
            if c0 is None or c1 is None or dt <= 0.0 or dt > 6.0 or v < LAG_MIN_SPEED_MPS:
                pred.append(0.0)
            else:
                dcourse = (c1 - c0 + 180.0) % 360.0 - 180.0
                omega = math.radians(dcourse / dt)
                pred.append(math.degrees(math.atan(v * omega / GRAVITY_MPS2)))
            logged.append(track.bank[i] + (track.bank[i + 1] - track.bank[i])
                          * ((t - track.t[i]) / (track.t[i + 1] - track.t[i])))

        pred = _box_smooth(pred, LAG_SMOOTH_HALF_WIDTH_S)
        logged = _box_smooth(logged, LAG_SMOOTH_HALF_WIDTH_S)

        best_lag = 0
        best_corr = -1.0
        for lag in range(-LAG_SCAN_RANGE_S, LAG_SCAN_RANGE_S + 1):
            # logged[k + lag] against pred[k]: positive lag = attitude late.
            if lag >= 0:
                a = pred[:n - lag] if lag else pred
                b = logged[lag:]
            else:
                a = pred[-lag:]
                b = logged[:lag]
            c = _correlation(a, b)
            if c > best_corr:
                best_corr = c
                best_lag = lag
        return (float(best_lag), best_corr)

    # ------------------------------------------------------------------
    # Full calibration
    # ------------------------------------------------------------------

    def calibrate(self, log_path: str,
                  images: Sequence[Tuple[float, float, float]]) -> FlightLogFit:
        """Parse + fit a log against a folder's (capture_utc, lat, lon) images.

        The returned fit carries acceptance and every stat the confirmation
        dialog shows. Attitude unreliability (low lag correlation) does NOT
        reject the fit - the clock refinement alone is still valuable; the
        caller reads ``attitude_reliable``.
        """
        sha = self.content_hash(log_path)
        track = self.parse(log_path)
        if track is None:
            return FlightLogFit(log_path=log_path, log_sha256=sha, accepted=False,
                                reason="not a readable ForeFlight track log")

        offset, mean_dist, matched = self.fit_clock_offset(track, images)
        if mean_dist > CLOCK_FIT_MAX_MEAN_DIST_M:
            return FlightLogFit(
                log_path=log_path, log_sha256=sha, accepted=False,
                reason=(f"images do not lie on this log's track "
                        f"(best mean distance {mean_dist:.0f} m)"),
                clock_offset_s=offset, mean_track_dist_m=mean_dist,
                matched_fraction=matched)

        times = [im[0] + offset for im in images if im[1] is not None]
        t0, t1 = min(times), max(times)
        lag, corr = self.fit_attitude_lag(track, t0, t1)
        reliable = corr >= LAG_MIN_CORRELATION

        banks = [track.bank[i] for i in range(len(track)) if t0 <= track.t[i] <= t1]
        fit = FlightLogFit(
            log_path=log_path, log_sha256=sha, accepted=True,
            clock_offset_s=offset, mean_track_dist_m=mean_dist,
            matched_fraction=matched,
            attitude_reliable=reliable, attitude_lag_s=lag if reliable else 0.0,
            lag_correlation=corr,
            bank_min_deg=min(banks) if banks else 0.0,
            bank_max_deg=max(banks) if banks else 0.0)
        self.logger.info(
            f"WALDO flight log {os.path.basename(log_path)}: offset {offset:+.1f} s, "
            f"mean track dist {mean_dist:.0f} m, matched {matched:.0%}, "
            f"attitude lag {lag:+.0f} s (corr {corr:.2f}, "
            f"{'reliable' if reliable else 'UNRELIABLE - constants kept'})")
        return fit
