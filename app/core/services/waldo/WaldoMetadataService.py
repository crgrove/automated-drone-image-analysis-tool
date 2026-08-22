"""
WaldoMetadataService - Detect WALDO airplane images and synthesise
ADIAT-compatible XMP gimbal/altitude/heading fields on first folder load.

WALDO airframe assumptions (per user spec):
    - Two Canon EOS 5DS R DSLRs in left/right pods.
    - Filename prefix `0_*` = left camera, `1_*` = right camera.
    - 22.5° outward roll about the heading axis. Camera otherwise nadir.
    - Plane assumed roughly level (bank ignored).
    - GPS altitude is ellipsoidal (WGS84-native).

The synthesised XMP fields use the standard `drone-dji:` namespace so the
existing ADIAT pipeline (ImageService, AOIService, GPSMapView,
CoverageExtentService) reads them without modification:
    drone-dji:GimbalPitchDegree, GimbalYawDegree, GimbalRollDegree,
    drone-dji:FlightYawDegree, RelativeAltitude, AbsoluteAltitude.

Plus a custom marker so the pre-pass doesn't re-run on already-processed images:
    waldo:Processed = "true"
    waldo:ProcessorVersion = "<int>"
"""

import math
import os
import piexif
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

import cv2
import numpy as np

from helpers.MetaDataHelper import MetaDataHelper
from helpers.LocationInfo import LocationInfo
from core.services.LoggerService import LoggerService
from core.services.shadow.SolarPosition import (
    SolarTimeUnresolvable,
    get_solar_position,
    resolve_capture_utc,
    timezone_name_for_position,
)
from core.services.waldo.WaldoTriggerLog import (
    TRIGGER_MIN_CHRONOLOGY_FRACTION,
    WaldoTriggerLogService,
)


WALDO_NAMESPACE_URI = "http://adiat.io/ns/waldo/1.0/"
# Version 7: GimbalRollDegree is expressed about the FLIGHT axis
# (FlightYawDegree) rather than the gimbal-yaw axis (consumers key the
# convention off version >= 6), and GimbalYawDegree comes from the mounting
# model unless inter-frame motion measurement confidently CONTRADICTS it
# (catches datasets whose post-flight software re-orients the frames).
# Version 7 also retires v6's sun-shadow orientation measurement: on steep
# terrain at low sun, slope shear and charred fallen logs mislead it.
# Version 8: per-image headings come from the WALDO *_Triggers.kml capture
# log when one is found near the images. Timestamp-derived headings flip
# ~180 deg on the first image of each serpentine lane (the >30 s turn gap
# starves the bearing pass and the fill then copies the OPPOSITE lane's
# heading - 15 of 1464 images on field data), and cannot handle frames
# re-flown in the opposite direction. The bump restamps existing datasets
# so those images get corrected on their next open.
# Version 9: cam 1 is stored with image-top = plane FORWARD, not backward.
# Content-vs-GPS-motion measurement on two independent flights proved the
# two cameras come out of the WALDO ground software rotated 180 deg from
# each other (the pods are body-opposed); v5..v8 stamped both cams
# image-top = backward, so every 1_* image had its pixel-to-ground mapping
# rotated 180 deg. The orientation safety net also aggregates in
# track-RELATIVE space now: the old absolute circular mean mixed opposite
# serpentine lanes into meaningless statistics and silently fell back to
# the (wrong, for cam 1) model.
WALDO_PROCESSOR_VERSION = "9"

DRONE_DJI_NS = "http://www.dji.com/drone-dji/1.0/"

# Clock-correction XMP fields (waldo namespace). The EXIF timestamps are
# never modified: the corrected UTC lives alongside them, and consumers
# (SolarPosition.resolve_capture_utc) prefer it when present.
CLOCK_CORRECTED_UTC_XMP = "CaptureUtcCorrected"
CLOCK_FACE_SHIFT_XMP = "ClockFaceShiftHours"
CLOCK_TIMEZONE_XMP = "ClockTimeZone"

# Heading-derivation tunables
STATIONARY_THRESHOLD_M = 5.0
MAX_NEIGHBOR_DT_S = 30.0
OUTWARD_ROLL_DEG = 22.5

# Mounting-model image-top offset from the plane heading, per camera.
# The two DSLR bodies are mounted opposed, and the ground software keeps
# each body's native orientation: cam 0 (`0_*`, RIGHT pod) comes out with
# image-top = plane BACKWARD, cam 1 (`1_*`, LEFT pod) with image-top =
# plane FORWARD. Field-verified by inter-frame content motion vs the GPS
# track on two independent flights (2026-07-25 and 2026-08-07).
MODEL_IMAGE_UP_OFFSET_DEG = {0: 180.0, 1: 0.0}

# Orientation-measurement tunables. Field imagery showed the mounting-model
# yaw assumption off by ~41 degrees (post-flight software had normalized the
# frames north-up), so orientation is measured from the imagery itself.
# The measurement: inter-frame content motion vs the GPS track (feature
# matching between consecutive frames). It carries tens-of-degrees of noise
# on tilted fixed-wing imagery over relief, so it never fine-tunes the
# model - it only OVERRIDES the model when it confidently disagrees by more
# than the override threshold (e.g. frames normalized north-up by post-flight
# software read ~180 deg away from the model; measurement noise never does).
ORIENTATION_SAMPLE_PAIRS = 16      # consecutive-image pairs sampled per camera
ORIENTATION_MIN_PAIRS = 4          # accept a measurement only with this many good pairs
ORIENTATION_MAX_STDERR_DEG = 8.0   # confidence required of the circular mean
ORIENTATION_MIN_BASELINE_M = 30.0  # pairs closer than this give unreliable bearings
ORIENTATION_MIN_INLIERS = 20       # ORB/RANSAC inliers required per pair
ORIENTATION_DOWNSCALE = 6          # feature matching runs at 1/N resolution
ORIENTATION_OVERRIDE_DEG = 60.0    # measured-vs-model gap that trips the override

# Filename prefix → cam index. 0_* = left, 1_* = right.
_WALDO_PREFIX_RE = re.compile(r'^(?P<cam>[01])_')


class WaldoHeadingUnavailable(Exception):
    """Raised when neither neighbour fill nor cross-cam fallback yields a heading."""


class WaldoCoverageError(Exception):
    """Raised when the configured DEM does not cover the image GPS location."""


class WaldoMissingGPSError(Exception):
    """Raised when an image has no GPS data to derive heading or AGL from."""


@dataclass
class WaldoImageRecord:
    """In-memory record built per WALDO image during the pre-pass."""
    path: str
    name: str
    cam_idx: int  # 0 or 1
    lat: Optional[float] = None
    lon: Optional[float] = None
    gps_alt_ellipsoidal: Optional[float] = None
    timestamp: Optional[datetime] = None
    heading_deg: Optional[float] = None
    error: Optional[str] = None


@dataclass
class WaldoProcessResult:
    """Aggregate result of process_folder."""
    processed: int = 0
    already_current: int = 0
    skipped: int = 0  # non-WALDO files
    errors: List[Tuple[str, str]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)  # informational, non-warning
    cancelled: bool = False


@dataclass
class ClockCorrectionProposal:
    """A detected camera-clock fault plus the correction offered to the user.

    Built by propose_clock_correction; the operator confirms (and may edit)
    the values before apply_clock_correction stamps anything.
    """
    face_shift_h: int                 # hours to ADD to the clock face (e.g. -12)
    tz_name: Optional[str]            # IANA zone from GPS (DST-correct), if known
    fixed_offset_h: Optional[float]   # fallback UTC offset when no zone found
    evidence: List[str]               # human-readable findings behind the proposal
    sample_name: str                  # image the preview line is built from
    sample_face: str                  # its raw EXIF DateTimeOriginal
    sample_corrected_utc: str         # its corrected time, ISO 8601 UTC


class WaldoMetadataService:
    """Pure-logic service: detection, heading derivation, XMP synthesis."""

    def __init__(self, terrain_service=None):
        self.terrain_service = terrain_service
        self.logger = LoggerService()

    # ------------------------------------------------------------------
    # Detection helpers
    # ------------------------------------------------------------------

    @staticmethod
    def is_waldo_image(filename: str) -> Optional[int]:
        """Return cam_idx (0 or 1) for WALDO files; None otherwise."""
        if not filename:
            return None
        base = os.path.basename(filename)
        m = _WALDO_PREFIX_RE.match(base)
        if not m:
            return None
        return int(m.group('cam'))

    @staticmethod
    def is_already_processed(image_path: str) -> bool:
        """True if the image's XMP carries the WALDO processed marker at the current version."""
        try:
            xmp = MetaDataHelper.get_xmp_data_merged(image_path) or {}
        except Exception:
            return False
        for key in ('waldo:Processed', 'Processed', 'XMP-waldo:Processed'):
            if key in xmp and str(xmp[key]).lower() in ('true', '1', 'yes'):
                version = (
                    xmp.get('waldo:ProcessorVersion')
                    or xmp.get('ProcessorVersion')
                    or xmp.get('XMP-waldo:ProcessorVersion')
                )
                if str(version) == WALDO_PROCESSOR_VERSION:
                    return True
                # Marker present but version mismatch: re-process.
                return False
        return False

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------

    @staticmethod
    def compute_optical_axis_angles(heading_deg: float, cam_idx: int,
                                    measured_orientation: Optional[Tuple[str, float]] = None
                                    ) -> Dict[str, float]:
        """Return drone-dji-style gimbal triple for a WALDO capture.

        Yaw — the compass bearing of the stored JPEG's top edge, which is
        what AOIService and the FOV-box renderer consume:

        - Default: the pod-mounting model. The two DSLR bodies are mounted
          opposed and each keeps its native orientation through the ground
          software, so the image-top offset from the plane heading is
          per-camera (MODEL_IMAGE_UP_OFFSET_DEG): cam 0 backward, cam 1
          FORWARD. v5..v8 wrongly stamped both cams backward — every 1_*
          image was 180 deg off (field-verified 2026-08-07).
        - `measured_orientation` overrides the model when the inter-frame
          content-motion measurement confidently contradicts it (see
          measure_image_up_orientation). It is ('offset', deg) for a
          track-relative image-top offset (normal WALDO storage), or
          ('absolute', deg) for a fixed compass image-top (post-flight
          software that normalizes frames, e.g. north-up).

        Roll — the pods physically tilt ±OUTWARD_ROLL_DEG cross-track
        (cam 0 to plane RIGHT, cam 1 to plane LEFT). As of processor
        version 6 the roll is expressed about the FLIGHT axis
        (FlightYawDegree), which stays physically meaningful whatever the
        stored image orientation is. About the *forward* flight axis a
        positive Rodrigues roll tilts the optical axis to plane LEFT, so
        cam 0 (right tilt) takes -OUTWARD_ROLL_DEG and cam 1 takes
        +OUTWARD_ROLL_DEG — the opposite signs from version 5, which
        expressed roll about the backward gimbal-yaw axis. Consumers pick
        the axis by ProcessorVersion. Pitch is fixed at nadir.
        """
        if cam_idx not in (0, 1):
            raise ValueError(f"Invalid WALDO cam_idx {cam_idx}")
        if measured_orientation is not None:
            mode, value = measured_orientation
            if mode == 'absolute':
                yaw = float(value) % 360.0
            elif mode == 'offset':
                yaw = (float(heading_deg) + float(value)) % 360.0
            else:
                raise ValueError(f"Invalid orientation mode {mode!r}")
        else:
            yaw = (float(heading_deg) + MODEL_IMAGE_UP_OFFSET_DEG[cam_idx]) % 360.0
        roll = (-OUTWARD_ROLL_DEG) if cam_idx == 0 else (+OUTWARD_ROLL_DEG)
        return {
            'pitch': -90.0,
            'yaw': yaw,
            'roll': roll,
        }

    # ------------------------------------------------------------------
    # Image-orientation measurement
    # ------------------------------------------------------------------

    @staticmethod
    def _pair_orientation_sample(path_a: str, path_b: str,
                                 bearing_deg: float) -> Optional[Tuple[float, int]]:
        """Measure image-top bearing from one consecutive image pair.

        Feature-matches the two frames, takes the content shift, and derives
        which compass bearing the image's top edge points to: the camera's
        world motion (GPS bearing a->b) appears in image coordinates as the
        negated content shift, and the angle between them is the rotation of
        the image frame relative to north.

        Returns:
            (image_up_bearing_deg, inlier_count), or None when the pair
            cannot be matched confidently.
        """
        try:
            f = ORIENTATION_DOWNSCALE
            imgs = []
            for p in (path_a, path_b):
                img = cv2.imdecode(np.fromfile(p, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                if img is None:
                    return None
                imgs.append(cv2.resize(img, (img.shape[1] // f, img.shape[0] // f),
                                       interpolation=cv2.INTER_AREA))
            a, b = imgs

            orb = cv2.ORB_create(3000)
            ka, da = orb.detectAndCompute(a, None)
            kb, db = orb.detectAndCompute(b, None)
            if da is None or db is None or len(ka) < ORIENTATION_MIN_INLIERS:
                return None
            matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = sorted(matcher.match(da, db), key=lambda m: m.distance)[:800]
            if len(matches) < ORIENTATION_MIN_INLIERS:
                return None
            src = np.float32([ka[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
            dst = np.float32([kb[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
            M, inliers = cv2.estimateAffinePartial2D(src, dst, ransacReprojThreshold=3.0)
            if M is None or inliers is None:
                return None
            n_inliers = int(inliers.sum())
            if n_inliers < ORIENTATION_MIN_INLIERS:
                return None
            # Consecutive frames share orientation; a big relative rotation
            # means the affine locked onto repeating texture, not real overlap
            rel_rot = math.degrees(math.atan2(M[1, 0], M[0, 0]))
            if abs(rel_rot) > 8.0:
                return None

            # Ground content at a's centre appears in b displaced by the
            # camera's motion, negated
            c = np.array([a.shape[1] / 2.0, a.shape[0] / 2.0, 1.0])
            mapped = M @ c
            content_dx, content_dy = mapped[0] - c[0], mapped[1] - c[1]
            cam_dx, cam_dy = -content_dx, -content_dy
            if abs(cam_dx) < 1e-6 and abs(cam_dy) < 1e-6:
                return None
            # Camera motion direction in image terms, clockwise from image-up
            motion_img_deg = math.degrees(math.atan2(cam_dx, -cam_dy)) % 360.0
            image_up = (float(bearing_deg) - motion_img_deg) % 360.0
            return image_up, n_inliers
        except Exception:
            return None

    @staticmethod
    def _circular_stats(angles_deg: List[float],
                        weights: List[float]) -> Tuple[float, float]:
        """Weighted circular mean and spread (degrees) of compass angles."""
        angles = np.radians(np.asarray(angles_deg, dtype=float))
        wgt = np.asarray(weights, dtype=float)
        sin_sum = float((wgt * np.sin(angles)).sum())
        cos_sum = float((wgt * np.cos(angles)).sum())
        mean_deg = math.degrees(math.atan2(sin_sum, cos_sum)) % 360.0
        resultant = math.hypot(sin_sum, cos_sum) / float(wgt.sum())
        resultant = min(1.0, max(1e-9, resultant))
        spread_deg = math.degrees(math.sqrt(-2.0 * math.log(resultant)))
        return mean_deg, spread_deg

    def _pair_motion_samples(self, group: List["WaldoImageRecord"]) -> List[Tuple[float, float, float]]:
        """Per-pair orientation samples from inter-frame motion vs the track.

        Pairs are name-consecutive frames (spatially adjacent regardless of
        capture order; the spatial displacement between two frames gives the
        same absolute image-top either way). Each sample carries the pair's
        plane heading so the caller can aggregate in track-relative space.

        Returns:
            list of (image_up_deg, pair_heading_deg, inlier_weight).
        """
        candidates = []
        for a, b in zip(group, group[1:]):
            if a.heading_deg is None:
                continue
            north_m = (b.lat - a.lat) * 111320.0
            east_m = (b.lon - a.lon) * 111320.0 * math.cos(math.radians(a.lat))
            dist = math.hypot(north_m, east_m)
            if dist < ORIENTATION_MIN_BASELINE_M:
                continue
            bearing = math.degrees(math.atan2(east_m, north_m)) % 360.0
            candidates.append((a.path, b.path, bearing, a.heading_deg))

        step = max(1, len(candidates) // ORIENTATION_SAMPLE_PAIRS) if candidates else 1
        samples = []
        for path_a, path_b, bearing, heading in candidates[::step][:ORIENTATION_SAMPLE_PAIRS]:
            result = self._pair_orientation_sample(path_a, path_b, bearing)
            if result is not None:
                image_up, inliers = result
                samples.append((image_up, heading, float(inliers)))
        return samples

    def measure_image_up_orientation(self, records: List["WaldoImageRecord"],
                                     cam_idx: int) -> Optional[Tuple[str, float]]:
        """Measure the stored image orientation; report ONLY refutations.

        The inter-frame-motion measurement is too noisy on tilted fixed-wing
        imagery over relief to fine-tune the mounting model, but a dataset
        whose frames were re-oriented reads far from the model (typically
        ~180 deg) - far beyond measurement noise.

        Samples are aggregated in TWO spaces and the tighter one wins:
        - track-RELATIVE (image_up minus plane heading): normal WALDO
          storage, where the orientation follows the flight direction. A
          plain absolute mean would blend opposite serpentine lanes into
          garbage statistics - exactly how the v5..v8 cam-1 fault stayed
          invisible.
        - ABSOLUTE compass: post-flight software that normalizes frames
          (e.g. north-up) gives a constant absolute orientation, which the
          relative space would scramble on serpentine flights.

        Returns:
            ('offset', deg) or ('absolute', deg) when the confident winner
            contradicts the mounting model by more than
            ORIENTATION_OVERRIDE_DEG; None otherwise (caller stamps the
            model).
        """
        group = [r for r in records
                 if r.cam_idx == cam_idx and r.lat is not None and r.lon is not None]
        group.sort(key=lambda r: r.name)
        if not group:
            return None

        samples = self._pair_motion_samples(group)
        if len(samples) < ORIENTATION_MIN_PAIRS:
            self.logger.info(
                f"WALDO cam {cam_idx}: orientation measurement inconclusive "
                f"({len(samples)} pairs); using the mounting model"
            )
            return None

        weights = [s[2] for s in samples]
        rel_mean, rel_spread = self._circular_stats(
            [(s[0] - s[1]) % 360.0 for s in samples], weights)
        abs_mean, abs_spread = self._circular_stats(
            [s[0] for s in samples], weights)
        count = len(samples)

        headings = [s[1] for s in samples]
        mean_heading, heading_spread = self._circular_stats(headings, weights)

        if rel_spread <= abs_spread:
            mode, mean_deg, spread_deg = 'offset', rel_mean, rel_spread
            model_deg = MODEL_IMAGE_UP_OFFSET_DEG[cam_idx]
        else:
            mode, mean_deg, spread_deg = 'absolute', abs_mean, abs_spread
            model_deg = (mean_heading + MODEL_IMAGE_UP_OFFSET_DEG[cam_idx]) % 360.0

        stderr_deg = spread_deg / math.sqrt(count)
        if stderr_deg > ORIENTATION_MAX_STDERR_DEG:
            self.logger.info(
                f"WALDO cam {cam_idx}: orientation measurement inconclusive "
                f"({count} pairs, {mode} stderr {stderr_deg:.1f} deg); "
                f"using the mounting model"
            )
            return None

        if mode == 'absolute' and heading_spread > 45.0:
            # A confident constant-ABSOLUTE orientation on a flight with
            # mixed headings (serpentine) cannot come from any track-relative
            # mounting: the frames were normalized by post-flight software.
            # The mean-heading model comparison below would be degenerate, so
            # this is a contradiction by construction.
            self.logger.warning(
                f"WALDO cam {cam_idx}: frames read a constant absolute "
                f"orientation ({mean_deg:.1f} deg, {count} pairs, stderr "
                f"{stderr_deg:.1f} deg) across mixed headings (spread "
                f"{heading_spread:.0f} deg) - post-flight normalized imagery; "
                f"stamping the measurement"
            )
            return ('absolute', mean_deg)

        gap = abs((mean_deg - model_deg + 180.0) % 360.0 - 180.0)
        if gap <= ORIENTATION_OVERRIDE_DEG:
            self.logger.info(
                f"WALDO cam {cam_idx}: measured orientation ({mode} {mean_deg:.1f} deg) "
                f"agrees with the mounting model ({model_deg:.1f} deg, gap {gap:.1f}); "
                f"stamping the model"
            )
            return None
        self.logger.warning(
            f"WALDO cam {cam_idx}: measured orientation ({mode} {mean_deg:.1f} deg, "
            f"{count} pairs, stderr {stderr_deg:.1f} deg) contradicts the mounting "
            f"model ({model_deg:.1f} deg, gap {gap:.1f} deg); stamping the measurement"
        )
        return (mode, mean_deg)

    # ------------------------------------------------------------------
    # Capture-time audit
    # ------------------------------------------------------------------
    #
    # A field camera with a mis-set clock silently poisons every time-based
    # computation (solar position, shadows) while looking perfectly healthy:
    # a 12-hour AM/PM flip produces nearly the same solar ELEVATION, so
    # nothing obvious breaks. These checks catch the detectable symptoms and
    # warn the operator; they never modify the files.

    AUDIT_SAMPLE_FILES = 3
    AUDIT_TZ_TOLERANCE_H = 1.75     # |stamped offset - longitude/15| beyond this is suspect
    AUDIT_MTIME_SLACK_S = 3600.0    # claimed capture this far after file-write is impossible
    AUDIT_DAYLIGHT_BRIGHTNESS = 45  # mean pixel value that cannot be a night exposure

    # A file can never be written BEFORE it was captured, so any claimed
    # capture time ahead of the file's mtime proves the clock runs ahead
    # (mtime survives Windows copies). The margin only needs to clear copy
    # jitter: the flip MAGNITUDE cannot be read from mtime because the
    # post-flight download delay offsets it (field data: a 12 h flip showed
    # as just 28 min ahead after a ~10 h download delay). The 12-hour AM/PM
    # flip is proposed as the known-fault default and the operator confirms
    # it against the preview.
    CLOCK_AHEAD_MIN_H = 0.1

    @staticmethod
    def _parse_offset_hours(raw) -> Optional[float]:
        """Parse an EXIF OffsetTime like '-06:00' into hours, or None."""
        if raw is None:
            return None
        try:
            text = raw.decode() if isinstance(raw, bytes) else str(raw)
            m = re.match(r'^([+-])(\d{2}):(\d{2})$', text.strip())
            if not m:
                return None
            sign = -1.0 if m.group(1) == '-' else 1.0
            return sign * (int(m.group(2)) + int(m.group(3)) / 60.0)
        except Exception:
            return None

    def audit_capture_times(self, paths: List[str]) -> List[str]:
        """Sanity-check the capture-time metadata of a few WALDO images.

        Checks:
        - Timezone vs GPS longitude: the stamped OffsetTime should be within
          ~AUDIT_TZ_TOLERANCE_H hours of longitude/15 (solar time; the margin
          absorbs civil-timezone and DST skew). A camera set to the wrong
          zone fails this deterministically.
        - Impossible file times: a capture time later than the file's own
          last-modified time means the clock runs ahead (mtime survives
          Windows copies, so this works even on relocated datasets when the
          post-flight files were written soon after the flight).
        - Sun below the horizon at the claimed time while the imagery is
          clearly daylight.

        Returns:
            Human-readable warning strings (empty when nothing is suspect).
        """
        warnings: List[str] = []
        sampled = paths[:self.AUDIT_SAMPLE_FILES]
        for path in sampled:
            name = os.path.basename(path)
            if self.get_corrected_utc_stamp(path):
                # An operator-confirmed clock correction is stamped on this
                # image: the EXIF faults below are known and already repaired.
                continue
            try:
                exif = MetaDataHelper.get_exif_data_piexif(path)
                exif_ifd = exif.get('Exif', {})
                raw_dt = exif_ifd.get(piexif.ExifIFD.DateTimeOriginal)
                offset_h = self._parse_offset_hours(
                    exif_ifd.get(piexif.ExifIFD.OffsetTimeOriginal)
                    or exif_ifd.get(piexif.ExifIFD.OffsetTime))
                gps = LocationInfo.get_gps(exif_data=exif)
                if raw_dt is None or gps is None:
                    continue
                local_dt = datetime.strptime(
                    (raw_dt.decode() if isinstance(raw_dt, bytes) else str(raw_dt)).strip(),
                    '%Y:%m:%d %H:%M:%S')

                # 1. Timezone field vs longitude
                if offset_h is not None:
                    solar_offset = gps['longitude'] / 15.0
                    if abs(offset_h - solar_offset) > self.AUDIT_TZ_TOLERANCE_H:
                        warnings.append(
                            f"{name}: camera timezone {offset_h:+.0f}h does not match its "
                            f"GPS longitude (expects about {solar_offset:+.1f}h). The "
                            f"camera clock settings are suspect; sun/shadow features "
                            f"will be unreliable."
                        )

                # 2. Capture claimed after the file was written
                if offset_h is not None:
                    claimed_utc = local_dt.replace(tzinfo=timezone.utc) - timedelta(hours=offset_h)
                    mtime_utc = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)
                    ahead_s = (claimed_utc - mtime_utc).total_seconds()
                    if ahead_s > self.AUDIT_MTIME_SLACK_S:
                        warnings.append(
                            f"{name}: claimed capture time is {ahead_s / 3600.0:.1f}h AFTER "
                            f"the file was last written - the camera clock runs ahead "
                            f"(a 12-hour AM/PM error is the usual cause)."
                        )

                    # 3. Night-time claim on daylight imagery
                    try:
                        elev, _az = get_solar_position(
                            gps['latitude'], gps['longitude'], claimed_utc)
                    except Exception:
                        elev = None
                    if elev is not None and elev < -2.0:
                        img = cv2.imdecode(np.fromfile(path, dtype=np.uint8),
                                           cv2.IMREAD_GRAYSCALE)
                        if img is not None:
                            small = img[::8, ::8]
                            if float(small.mean()) > self.AUDIT_DAYLIGHT_BRIGHTNESS:
                                warnings.append(
                                    f"{name}: the sun was below the horizon at the claimed "
                                    f"capture time, but the image is clearly daylight - "
                                    f"the camera clock is wrong."
                                )
            except Exception as e:
                self.logger.warning(f"Capture-time audit failed for {name}: {e}")

        # One warning per distinct message class is enough; drop duplicates
        deduped: List[str] = []
        seen_kinds = set()
        for w in warnings:
            kind = w.split(': ', 1)[1][:40]
            if kind not in seen_kinds:
                seen_kinds.add(kind)
                deduped.append(w)
        return deduped

    # ------------------------------------------------------------------
    # Clock correction (operator-confirmed, non-destructive)
    # ------------------------------------------------------------------

    @staticmethod
    def get_corrected_utc_stamp(image_path: str) -> Optional[str]:
        """Return the stamped corrected-UTC string for an image, or None."""
        try:
            xmp = MetaDataHelper.get_xmp_data_merged(image_path) or {}
        except Exception:
            return None
        for key in (f'waldo:{CLOCK_CORRECTED_UTC_XMP}', CLOCK_CORRECTED_UTC_XMP,
                    f'XMP-waldo:{CLOCK_CORRECTED_UTC_XMP}'):
            value = xmp.get(key)
            if value:
                return str(value)
        return None

    @staticmethod
    def _parse_exif_face_time(exif: dict) -> Optional[datetime]:
        """Raw DateTimeOriginal (+ subseconds) as a NAIVE datetime.

        Unlike _parse_exif_timestamp this deliberately ignores OffsetTime:
        the clock correction reinterprets the face reading from scratch, and
        the stamped offset is part of what is broken.
        """
        exif_ifd = exif.get('Exif') or {}
        dt_raw = exif_ifd.get(piexif.ExifIFD.DateTimeOriginal)
        if dt_raw is None:
            return None
        try:
            dt_str = dt_raw.decode('utf-8') if isinstance(dt_raw, bytes) else str(dt_raw)
            dt = datetime.strptime(dt_str.strip(), "%Y:%m:%d %H:%M:%S")
        except Exception:
            return None
        sub_raw = exif_ifd.get(piexif.ExifIFD.SubSecTimeOriginal)
        if sub_raw is not None:
            try:
                sub_str = (sub_raw.decode('utf-8') if isinstance(sub_raw, bytes)
                           else str(sub_raw)).strip()
                if sub_str:
                    dt = dt.replace(microsecond=int(round(float("0." + sub_str) * 1_000_000)))
            except Exception:
                pass
        return dt

    @staticmethod
    def compute_corrected_utc(face_dt: datetime, face_shift_h: float,
                              tz_name: Optional[str],
                              fixed_offset_h: Optional[float]) -> datetime:
        """Corrected capture time: shift the clock face, then localise.

        The shifted face reading is interpreted in the TRUE timezone (IANA
        zone when known - DST-correct for the date - else a fixed offset)
        and converted to UTC. Raises ValueError when neither timezone form
        is usable.
        """
        shifted = face_dt + timedelta(hours=face_shift_h)
        if tz_name:
            try:
                return shifted.replace(tzinfo=ZoneInfo(tz_name)).astimezone(timezone.utc)
            except Exception:
                pass  # unknown zone / no tzdata: fall through to fixed offset
        if fixed_offset_h is not None:
            tz = timezone(timedelta(hours=fixed_offset_h))
            return shifted.replace(tzinfo=tz).astimezone(timezone.utc)
        raise ValueError("No usable timezone for clock correction")

    def propose_clock_correction(self, paths: List[str]) -> Optional[ClockCorrectionProposal]:
        """Detect the known clock-fault signature and build a correction offer.

        Fires when a sampled image shows a PROVABLE clock symptom:
        - the stamped timezone disagrees with the GPS longitude, and/or
        - the claimed capture time is AFTER the file was written (a file
          cannot predate its capture; mtime survives Windows copies).

        The proposed face shift is the 12-hour AM/PM flip only when the
        ahead-proof exists; a timezone mismatch alone proposes a pure zone
        fix (face shift 0) and the operator adds the flip after checking
        the preview against the real flight window - the flip magnitude is
        not measurable from a zone mismatch. NOTE: any XMP write (including
        the pre-pass itself) resets mtime and destroys the ahead-proof, so
        detection must run on a folder BEFORE it is first stamped.

        Images already carrying a corrected stamp never fire. Returns None
        when no provable symptom is present (correcting an unknown fault
        would be guessing).
        """
        for path in paths[:self.AUDIT_SAMPLE_FILES]:
            name = os.path.basename(path)
            try:
                if self.get_corrected_utc_stamp(path):
                    continue
                exif = MetaDataHelper.get_exif_data_piexif(path)
                face_dt = self._parse_exif_face_time(exif)
                gps = LocationInfo.get_gps(exif_data=exif)
                offset_h = self._parse_offset_hours(
                    exif.get('Exif', {}).get(piexif.ExifIFD.OffsetTimeOriginal)
                    or exif.get('Exif', {}).get(piexif.ExifIFD.OffsetTime))
                if face_dt is None or gps is None or offset_h is None:
                    continue

                solar_offset = gps['longitude'] / 15.0
                tz_mismatch = abs(offset_h - solar_offset) > self.AUDIT_TZ_TOLERANCE_H

                claimed_utc = (face_dt.replace(tzinfo=timezone.utc)
                               - timedelta(hours=offset_h))
                mtime_utc = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)
                ahead_h = (claimed_utc - mtime_utc).total_seconds() / 3600.0
                clock_ahead = ahead_h > self.CLOCK_AHEAD_MIN_H

                if not (tz_mismatch or clock_ahead):
                    continue

                tz_name = timezone_name_for_position(gps['latitude'], gps['longitude'])
                fixed_offset_h = round(solar_offset)
                face_shift_h = -12 if clock_ahead else 0

                evidence = []
                if tz_mismatch:
                    evidence.append(
                        f"Stamped timezone is UTC{offset_h:+.0f} but the GPS "
                        f"longitude implies about UTC{solar_offset:+.1f}.")
                if clock_ahead:
                    evidence.append(
                        f"Claimed capture time is {ahead_h * 60.0:.0f} min AFTER the "
                        f"file was written - impossible, so the clock runs ahead. A "
                        f"12-hour AM/PM flip offset by the post-flight download delay "
                        f"produces exactly this.")
                else:
                    evidence.append(
                        "The clock face itself may additionally carry a 12-hour AM/PM "
                        "error that cannot be proven from these files - check the "
                        "corrected time below against when the flight actually flew "
                        "and adjust the face error if needed.")

                corrected = self.compute_corrected_utc(
                    face_dt, face_shift_h, tz_name, fixed_offset_h)
                return ClockCorrectionProposal(
                    face_shift_h=face_shift_h,
                    tz_name=tz_name,
                    fixed_offset_h=fixed_offset_h,
                    evidence=evidence,
                    sample_name=name,
                    sample_face=face_dt.strftime("%Y:%m:%d %H:%M:%S"),
                    sample_corrected_utc=corrected.strftime("%Y-%m-%d %H:%M:%S UTC"),
                )
            except Exception as e:
                self.logger.warning(f"Clock-correction detection failed for {name}: {e}")
        return None

    @staticmethod
    def get_correction_stamp_details(image_path: str) -> Optional[Tuple[float, str]]:
        """(face_shift_h, tz_text) parsed from an image's correction stamp."""
        try:
            xmp = MetaDataHelper.get_xmp_data_merged(image_path) or {}
        except Exception:
            return None
        shift_raw = None
        tz_raw = None
        for prefix in ('waldo:', '', 'XMP-waldo:'):
            shift_raw = shift_raw or xmp.get(f'{prefix}{CLOCK_FACE_SHIFT_XMP}')
            tz_raw = tz_raw or xmp.get(f'{prefix}{CLOCK_TIMEZONE_XMP}')
        if shift_raw is None or tz_raw is None:
            return None
        try:
            return float(str(shift_raw)), str(tz_raw)
        except ValueError:
            return None

    def propose_amendment(self, paths: List[str]) -> Optional[ClockCorrectionProposal]:
        """Build a proposal PRE-FILLED from an already-stamped correction.

        Used when the operator wants to change an applied correction (the
        normal detection deliberately goes quiet on corrected images).
        Returns None when no sampled image carries a correction stamp.
        """
        for path in paths[:self.AUDIT_SAMPLE_FILES]:
            name = os.path.basename(path)
            try:
                details = self.get_correction_stamp_details(path)
                if details is None:
                    continue
                shift_h, tz_text = details
                exif = MetaDataHelper.get_exif_data_piexif(path)
                face_dt = self._parse_exif_face_time(exif)
                if face_dt is None:
                    continue
                tz_name: Optional[str] = None
                fixed_offset_h: Optional[float] = None
                try:
                    ZoneInfo(tz_text)
                    tz_name = tz_text
                except Exception:
                    try:
                        fixed_offset_h = float(tz_text.replace('UTC', '').strip())
                    except ValueError:
                        continue
                corrected = self.compute_corrected_utc(
                    face_dt, shift_h, tz_name, fixed_offset_h)
                return ClockCorrectionProposal(
                    face_shift_h=int(shift_h),
                    tz_name=tz_name,
                    fixed_offset_h=fixed_offset_h,
                    evidence=[
                        f"A capture-time correction is already stamped on these "
                        f"images (face shift {shift_h:+.0f} h, zone {tz_text}). "
                        f"Applying different values replaces it on every image."
                    ],
                    sample_name=name,
                    sample_face=face_dt.strftime("%Y:%m:%d %H:%M:%S"),
                    sample_corrected_utc=corrected.strftime("%Y-%m-%d %H:%M:%S UTC"),
                )
            except Exception as e:
                self.logger.warning(f"Clock amendment proposal failed for {name}: {e}")
        return None

    def stamped_correction_suspect(self, paths: List[str]) -> Optional[str]:
        """Detect an applied correction that is physically impossible.

        A corrected capture time that puts the sun below the horizon while
        the image is clearly daylight proves the correction is wrong (e.g.
        a 12-hour shift applied to a camera whose clock face had already
        been fixed). Returns a human-readable reason, or None.
        """
        for path in paths[:self.AUDIT_SAMPLE_FILES]:
            name = os.path.basename(path)
            try:
                stamp = self.get_corrected_utc_stamp(path)
                if not stamp:
                    continue
                corrected_utc = datetime.fromisoformat(stamp).astimezone(timezone.utc)
                exif = MetaDataHelper.get_exif_data_piexif(path)
                gps = LocationInfo.get_gps(exif_data=exif)
                if gps is None:
                    continue
                elev, _az = get_solar_position(
                    gps['latitude'], gps['longitude'], corrected_utc)
                if elev >= -2.0:
                    continue
                img = cv2.imdecode(np.fromfile(path, dtype=np.uint8),
                                   cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue
                if float(img[::8, ::8].mean()) > self.AUDIT_DAYLIGHT_BRIGHTNESS:
                    return (
                        f"{name}: the stamped clock correction puts the capture at "
                        f"{corrected_utc.strftime('%Y-%m-%d %H:%M UTC')}, when the sun "
                        f"was below the horizon - but the image is clearly daylight. "
                        f"The applied correction is wrong."
                    )
            except Exception as e:
                self.logger.warning(f"Correction sanity check failed for {name}: {e}")
        return None

    def apply_clock_correction(
        self,
        image_paths: List[str],
        face_shift_h: float,
        tz_name: Optional[str] = None,
        fixed_offset_h: Optional[float] = None,
        progress_cb: Optional[Callable[[int, int, str], None]] = None,
        cancel_cb: Optional[Callable[[], bool]] = None,
    ) -> WaldoProcessResult:
        """Stamp a corrected capture UTC on every WALDO image.

        Non-destructive: EXIF stays untouched; the correction lives in the
        waldo XMP namespace and is preferred by resolve_capture_utc. Images
        whose stamp already matches are skipped, so re-running is cheap and
        idempotent.
        """
        result = WaldoProcessResult()
        cancel_cb = cancel_cb or (lambda: False)
        total = len(image_paths)
        for i, path in enumerate(image_paths):
            if cancel_cb():
                result.cancelled = True
                break
            name = os.path.basename(path)
            if progress_cb is not None:
                try:
                    progress_cb(i + 1, total, f"Correcting capture time {i + 1}/{total}: {name}")
                except Exception:
                    pass
            if self.is_waldo_image(path) is None:
                result.skipped += 1
                continue
            try:
                exif = MetaDataHelper.get_exif_data_piexif(path)
                face_dt = self._parse_exif_face_time(exif)
                if face_dt is None:
                    result.errors.append((name, "No DateTimeOriginal to correct"))
                    continue
                corrected = self.compute_corrected_utc(
                    face_dt, face_shift_h, tz_name, fixed_offset_h)
                corrected_str = corrected.strftime("%Y-%m-%dT%H:%M:%S+00:00")
                existing = self.get_corrected_utc_stamp(path)
                if existing == corrected_str:
                    result.already_current += 1
                    continue
                MetaDataHelper.add_xmp_fields(path, [
                    (WALDO_NAMESPACE_URI, CLOCK_CORRECTED_UTC_XMP, corrected_str),
                    (WALDO_NAMESPACE_URI, CLOCK_FACE_SHIFT_XMP, f"{face_shift_h:+.0f}"),
                    (WALDO_NAMESPACE_URI, CLOCK_TIMEZONE_XMP,
                     tz_name or f"UTC{fixed_offset_h:+.1f}"),
                ])
                result.processed += 1
            except Exception as e:
                result.errors.append((name, f"Clock correction failed: {e}"))
        return result

    def compute_relative_altitude_m(
        self, lat: float, lon: float, gps_alt_ellipsoidal_m: float
    ) -> Tuple[float, float]:
        """Return (agl_m, absolute_orthometric_m) using terrain + geoid.

        Raises WaldoCoverageError when the DEM has no coverage at lat/lon.
        """
        if self.terrain_service is None:
            raise WaldoCoverageError("No terrain service configured for WALDO pre-pass.")

        geoid_undulation = self.terrain_service.get_geoid_undulation(lat, lon) or 0.0
        absolute_orthometric = gps_alt_ellipsoidal_m - geoid_undulation

        elev_result = self.terrain_service.get_elevation(lat, lon)
        if elev_result.source != 'terrain' or elev_result.elevation_m is None:
            raise WaldoCoverageError(
                f"DEM has no coverage at ({lat:.6f}, {lon:.6f})"
            )
        agl = absolute_orthometric - elev_result.elevation_m
        agl = max(1.0, agl)
        return agl, absolute_orthometric

    # ------------------------------------------------------------------
    # EXIF reading
    # ------------------------------------------------------------------

    @staticmethod
    def _read_record(path: str, cam_idx: int) -> WaldoImageRecord:
        """Read EXIF/GPS/timestamp into a WaldoImageRecord (errors land in record.error)."""
        rec = WaldoImageRecord(path=path, name=os.path.basename(path), cam_idx=cam_idx)
        try:
            exif = MetaDataHelper.get_exif_data_piexif(path)
        except Exception as e:
            rec.error = f"EXIF read failed: {e}"
            return rec

        gps = LocationInfo.get_gps(exif_data=exif)
        if not gps:
            rec.error = "Missing GPS in EXIF"
            return rec
        rec.lat = gps['latitude']
        rec.lon = gps['longitude']

        gps_ifd = exif.get('GPS') or {}
        alt = gps_ifd.get(piexif.GPSIFD.GPSAltitude)
        if alt is not None:
            try:
                if isinstance(alt, tuple):
                    rec.gps_alt_ellipsoidal = alt[0] / alt[1]
                else:
                    rec.gps_alt_ellipsoidal = float(alt)
                if gps_ifd.get(piexif.GPSIFD.GPSAltitudeRef, 0) == 1:
                    rec.gps_alt_ellipsoidal = -rec.gps_alt_ellipsoidal
            except (TypeError, ValueError, ZeroDivisionError):
                rec.gps_alt_ellipsoidal = None

        rec.timestamp = WaldoMetadataService._parse_exif_timestamp(exif)
        return rec

    @staticmethod
    def _parse_exif_timestamp(exif: dict) -> Optional[datetime]:
        """Parse DateTimeOriginal + SubSecTimeOriginal + OffsetTimeOriginal into UTC."""
        exif_ifd = exif.get('Exif') or {}
        dt_raw = exif_ifd.get(piexif.ExifIFD.DateTimeOriginal)
        if dt_raw is None:
            return None
        try:
            dt_str = dt_raw.decode('utf-8') if isinstance(dt_raw, bytes) else str(dt_raw)
            dt = datetime.strptime(dt_str.strip(), "%Y:%m:%d %H:%M:%S")
        except Exception:
            return None

        sub_raw = exif_ifd.get(piexif.ExifIFD.SubSecTimeOriginal)
        if sub_raw is not None:
            try:
                sub_str = sub_raw.decode('utf-8') if isinstance(sub_raw, bytes) else str(sub_raw)
                sub_str = sub_str.strip()
                if sub_str:
                    micros = int(round(float("0." + sub_str) * 1_000_000))
                    dt = dt.replace(microsecond=micros)
            except Exception:
                pass

        offset_raw = exif_ifd.get(piexif.ExifIFD.OffsetTimeOriginal)
        if offset_raw is not None:
            try:
                offset_str = offset_raw.decode('utf-8') if isinstance(offset_raw, bytes) else str(offset_raw)
                offset_str = offset_str.strip()
                m = re.match(r'^([+-])(\d{2}):(\d{2})$', offset_str)
                if m:
                    sign = 1 if m.group(1) == '+' else -1
                    hh = int(m.group(2))
                    mm = int(m.group(3))
                    tz = timezone(sign * timedelta(hours=hh, minutes=mm))
                    dt = dt.replace(tzinfo=tz).astimezone(timezone.utc).replace(tzinfo=None)
            except Exception:
                pass

        return dt

    # ------------------------------------------------------------------
    # Heading derivation
    # ------------------------------------------------------------------

    def derive_headings(self, records: List[WaldoImageRecord]):
        """Populate `record.heading_deg` for every record that has GPS."""
        # Group by cam_idx, sort by timestamp (fall back to filename for missing).
        groups: Dict[int, List[WaldoImageRecord]] = {0: [], 1: []}
        for r in records:
            if r.lat is None or r.lon is None:
                continue
            groups.setdefault(r.cam_idx, []).append(r)

        for cam_idx, group in groups.items():
            if not group:
                continue
            group.sort(key=lambda r: (r.timestamp or datetime.min, r.name))
            self._derive_for_group(group)

        # Cross-cam fallback: if a record still has no heading, try the other
        # cam group's nearest-timestamp heading.
        all_with_heading = [r for r in records if r.heading_deg is not None]
        for r in records:
            if r.heading_deg is None and r.lat is not None and r.timestamp is not None:
                neighbour = self._nearest_other_cam(r, all_with_heading)
                if neighbour is not None:
                    r.heading_deg = neighbour.heading_deg

    @staticmethod
    def _nearest_other_cam(target: WaldoImageRecord,
                           candidates: List[WaldoImageRecord]) -> Optional[WaldoImageRecord]:
        best: Optional[WaldoImageRecord] = None
        best_dt = None
        for c in candidates:
            if c.cam_idx == target.cam_idx or c.timestamp is None:
                continue
            dt = abs((c.timestamp - target.timestamp).total_seconds())
            if best_dt is None or dt < best_dt:
                best_dt = dt
                best = c
        return best

    @staticmethod
    def _derive_for_group(group: List[WaldoImageRecord]):
        n = len(group)
        if n == 0:
            return

        def neighbour_search(idx: int, direction: int) -> Optional[int]:
            """Find next non-stationary, in-window neighbour from idx in given direction."""
            j = idx + direction
            anchor = group[idx]
            while 0 <= j < n:
                cand = group[j]
                if cand.timestamp and anchor.timestamp:
                    dt = abs((cand.timestamp - anchor.timestamp).total_seconds())
                    if dt > MAX_NEIGHBOR_DT_S:
                        return None
                dist = LocationInfo.haversine_m(anchor.lat, anchor.lon, cand.lat, cand.lon)
                if dist >= STATIONARY_THRESHOLD_M:
                    return j
                j += direction
            return None

        # Pass 1: bearing(prev → next) for interior images; edge images (a
        # lane start/end whose other neighbour sits beyond the turn window)
        # use the one in-window side. One-sided bearings are noisier but a
        # fill would copy the PREVIOUS lane's heading, which on a serpentine
        # flight is ~180 deg wrong (observed on field data at lane starts).
        for i in range(n):
            prev_idx = neighbour_search(i, -1)
            next_idx = neighbour_search(i, +1)
            if prev_idx is not None and next_idx is not None:
                heading = LocationInfo.bearing(
                    group[prev_idx].lat, group[prev_idx].lon,
                    group[next_idx].lat, group[next_idx].lon
                )
            elif prev_idx is not None:
                heading = LocationInfo.bearing(
                    group[prev_idx].lat, group[prev_idx].lon,
                    group[i].lat, group[i].lon
                )
            elif next_idx is not None:
                heading = LocationInfo.bearing(
                    group[i].lat, group[i].lon,
                    group[next_idx].lat, group[next_idx].lon
                )
            else:
                continue
            if not math.isnan(heading):
                group[i].heading_deg = heading

        # Pass 2: forward fill (stationary clusters inherit the last valid).
        last_seen: Optional[float] = None
        for r in group:
            if r.heading_deg is None and last_seen is not None:
                r.heading_deg = last_seen
            elif r.heading_deg is not None:
                last_seen = r.heading_deg

        # Pass 3: backward fill for any still-missing (e.g. very first image).
        last_seen = None
        for r in reversed(group):
            if r.heading_deg is None and last_seen is not None:
                r.heading_deg = last_seen
            elif r.heading_deg is not None:
                last_seen = r.heading_deg

        # Pass 4: if the entire group is stationary or has only 1 record,
        # fall back to bearing(first → last) when at least 2 distinct points exist.
        missing = [r for r in group if r.heading_deg is None]
        if missing and n >= 2:
            heading = LocationInfo.bearing(
                group[0].lat, group[0].lon, group[-1].lat, group[-1].lon
            )
            if not (math.isnan(heading)):
                for r in missing:
                    r.heading_deg = heading

    # ------------------------------------------------------------------
    # Trigger-log heading override
    # ------------------------------------------------------------------

    def _apply_trigger_log_headings(self, records: List[WaldoImageRecord],
                                    result: WaldoProcessResult):
        """Replace GPS/timestamp-derived headings with trigger-log headings.

        Runs AFTER derive_headings so the comparison can report how many
        images the log corrected; the log wins wherever it matches. A log
        whose document order contradicts the EXIF timestamps is rejected
        (it would flip serpentine lanes instead of fixing them). Failures
        never abort the pass - the timestamp-derived headings remain.
        """
        try:
            trigger_service = WaldoTriggerLogService()
            found = trigger_service.discover(records)
            if found is None:
                return
            kml_path, triggers = found
            kml_name = os.path.basename(kml_path)

            chrono = WaldoTriggerLogService.chronology_fraction(triggers, records)
            if chrono is not None and chrono < TRIGGER_MIN_CHRONOLOGY_FRACTION:
                result.warnings.append(
                    f"{kml_name}: trigger order disagrees with image timestamps "
                    f"({chrono:.0%} consistent) - the log was ignored for headings."
                )
                return

            headings = WaldoTriggerLogService.headings_by_name(triggers)
            applied = 0
            corrected = 0
            for rec in records:
                tname = WaldoTriggerLogService.image_trigger_name(rec.name)
                heading = headings.get(tname) if tname else None
                if heading is None:
                    continue
                if rec.heading_deg is not None:
                    diff = abs((rec.heading_deg - heading + 180.0) % 360.0 - 180.0)
                    if diff > 90.0:
                        corrected += 1
                        self.logger.info(
                            f"WALDO trigger log corrected {rec.name}: "
                            f"{rec.heading_deg:.1f} -> {heading:.1f} deg")
                rec.heading_deg = heading
                applied += 1

            result.notes.append(
                f"Trigger log {kml_name}: flight direction applied to "
                f"{applied} of {len(records)} image(s)."
            )
            if corrected:
                result.warnings.append(
                    f"{kml_name}: corrected the flight direction of {corrected} "
                    f"image(s) by more than 90 degrees (serpentine lane starts / "
                    f"re-flown frames). AOI positions on those images were "
                    f"unreliable in analyses run before this pass."
                )
        except Exception as e:
            self.logger.warning(f"WALDO trigger-log pass failed: {e}")

    # ------------------------------------------------------------------
    # Public folder pipeline
    # ------------------------------------------------------------------

    def process_folder(
        self,
        image_paths: List[str],
        progress_cb: Optional[Callable[[int, int, str], None]] = None,
        cancel_cb: Optional[Callable[[], bool]] = None,
    ) -> WaldoProcessResult:
        """Run the full WALDO synthesis pass on the given image paths.

        Args:
            image_paths: Absolute paths of every image considered for the pass.
                Non-WALDO files are silently skipped.
            progress_cb: Optional callback (current, total, status_text) for UI
                updates. total == 0 signals an indeterminate phase (the dialog
                paints a busy spinner). total > 0 signals determinate per-image
                progress.
            cancel_cb: Optional cancellation predicate; returning True aborts cleanly.

        Returns:
            WaldoProcessResult with counts + per-image errors.
        """
        result = WaldoProcessResult()
        cancel_cb = cancel_cb or (lambda: False)

        def emit(current: int, total: int, status_text: str):
            if progress_cb is None:
                return
            try:
                progress_cb(current, total, status_text)
            except Exception:
                pass

        # 1. Filter + classify (EXIF reads happen here; tick the bar so a long
        #    folder of 500+ images doesn't sit at 0% during this pass).
        emit(0, 0, "Reading image metadata...")
        records: List[WaldoImageRecord] = []
        waldo_paths: List[str] = []
        n_paths = len(image_paths)
        for i, path in enumerate(image_paths):
            if cancel_cb():
                result.cancelled = True
                return result
            if i % 10 == 0 or i == n_paths - 1:
                emit(i + 1, n_paths, f"Reading metadata {i + 1}/{n_paths}")
            cam_idx = self.is_waldo_image(path)
            if cam_idx is None:
                result.skipped += 1
                continue
            waldo_paths.append(path)
            if self.is_already_processed(path):
                result.already_current += 1
                continue
            rec = self._read_record(path, cam_idx)
            records.append(rec)

        # Capture-time audit runs on every open (already-current files too):
        # a mis-set camera clock stays wrong until the operator fixes it
        if waldo_paths:
            emit(0, 0, "Auditing capture-time metadata...")
            result.warnings.extend(self.audit_capture_times(waldo_paths))
            for warning in result.warnings:
                self.logger.warning(f"WALDO time audit: {warning}")

        if not records:
            return result

        # 2. Warm up terrain services so the multi-second EGM96 grid load
        #    happens behind a clear status message instead of stalling the
        #    first per-image iteration.
        if self.terrain_service is not None:
            emit(0, 0, "Loading geoid grid + DEM index...")
            try:
                self.terrain_service.warmup()
            except Exception as e:
                self.logger.warning(f"Terrain warmup failed: {e}")

        # 3. Derive headings across the full flight (no per-image progress;
        #    runs in milliseconds even for thousands of records).
        emit(0, 0, "Deriving plane heading from GPS track...")
        self.derive_headings(records)

        # 3a. Trigger-log override: WALDO's *_Triggers.kml lists every
        #     trigger in CAPTURE order with its position - authoritative for
        #     flight direction where timestamp sorting fails (serpentine
        #     lane starts, frames re-flown the opposite way, clock faults).
        emit(0, 0, "Looking for WALDO trigger log (*_Triggers.kml)...")
        self._apply_trigger_log_headings(records, result)

        # 3b. Measure the stored image orientation per camera by comparing
        #     inter-frame content motion against the GPS track. The mounting
        #     model is stamped unless the measurement confidently refutes it
        #     (catches post-flight software that re-orients frames).
        orientation_by_cam: Dict[int, Optional[Tuple[str, float]]] = {}
        for cam_idx in sorted({r.cam_idx for r in records}):
            if cancel_cb():
                result.cancelled = True
                return result
            emit(0, 0, f"Measuring image orientation (cam {cam_idx})...")
            orientation_by_cam[cam_idx] = self.measure_image_up_orientation(records, cam_idx)

        # 4. Per-image XMP synthesis
        total = len(records)
        for i, rec in enumerate(records):
            if cancel_cb():
                result.cancelled = True
                break

            emit(i + 1, total, f"Writing XMP {i + 1}/{total}: {rec.name}")

            if rec.error:
                result.errors.append((rec.name, rec.error))
                continue
            if rec.lat is None or rec.lon is None or rec.gps_alt_ellipsoidal is None:
                result.errors.append((rec.name, "Missing GPS lat/lon/altitude"))
                continue
            if rec.heading_deg is None:
                result.errors.append((rec.name, "Heading unavailable (single image / all stationary)"))
                continue

            try:
                agl_m, abs_orthometric = self.compute_relative_altitude_m(
                    rec.lat, rec.lon, rec.gps_alt_ellipsoidal
                )
            except WaldoCoverageError as e:
                result.errors.append((rec.name, str(e)))
                continue
            except Exception as e:
                result.errors.append((rec.name, f"AGL computation failed: {e}"))
                continue

            angles = self.compute_optical_axis_angles(
                rec.heading_deg, rec.cam_idx,
                measured_orientation=orientation_by_cam.get(rec.cam_idx)
            )

            try:
                self._write_synthesised_xmp(
                    rec.path, angles, rec.heading_deg, agl_m, abs_orthometric
                )
            except Exception as e:
                result.errors.append((rec.name, f"XMP write failed: {e}"))
                continue

            result.processed += 1

        return result

    @staticmethod
    def _write_synthesised_xmp(image_path: str, angles: Dict[str, float],
                               plane_heading_deg: float,
                               agl_m: float, abs_orthometric_m: float):
        """Write the synthesised drone-dji + waldo:Processed fields in one batch.

        FlightYawDegree carries the plane's true heading (drone-body direction).
        GimbalYawDegree carries the stored image-top bearing per camera:
        image-top = plane backward for cam 0, plane FORWARD for cam 1 (the
        opposed body mounting; see MODEL_IMAGE_UP_OFFSET_DEG).
        """
        flight_yaw = float(plane_heading_deg) % 360.0
        fields = [
            (DRONE_DJI_NS, "GimbalPitchDegree", f"{angles['pitch']:+.4f}"),
            (DRONE_DJI_NS, "GimbalYawDegree", f"{angles['yaw']:+.4f}"),
            (DRONE_DJI_NS, "GimbalRollDegree", f"{angles['roll']:+.4f}"),
            (DRONE_DJI_NS, "FlightYawDegree", f"{flight_yaw:+.4f}"),
            (DRONE_DJI_NS, "RelativeAltitude", f"{agl_m:+.4f}"),
            (DRONE_DJI_NS, "AbsoluteAltitude", f"{abs_orthometric_m:+.4f}"),
            (WALDO_NAMESPACE_URI, "Processed", "true"),
            (WALDO_NAMESPACE_URI, "ProcessorVersion", WALDO_PROCESSOR_VERSION),
        ]
        MetaDataHelper.add_xmp_fields(image_path, fields)
