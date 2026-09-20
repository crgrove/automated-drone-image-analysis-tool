"""TrackDiscoveryService - Find a compatible flight track file for an image set.

Bearing recovery normally asks the user to browse for a track log (KML, GPX,
or CSV - a ForeFlight tracklog export is the common fixed-wing case). When a
result set was opened from a results-folder scan, that log usually sits
somewhere in the scanned tree already; this service finds it so the user can
be offered the file instead of a file dialog.

A candidate is trusted on POSITIONAL evidence only: a sample of the images'
EXIF GPS positions must each lie close to the candidate's track. Timestamps
are deliberately not used for validation - WALDO camera clocks carry known
AM/PM and timezone faults, and a constant clock offset would veto exactly the
file that fixes the flight. Position cannot be faked by the wrong flight:
another mission's track is typically kilometres away.
"""

import os

from core.services.BearingCalculationService import BearingCalculationService
from core.services.LoggerService import LoggerService
from helpers.LocationInfo import LocationInfo

# Extensions bearing recovery can load; discovery sweeps the same set.
TRACK_EXTENSIONS = ('.kml', '.gpx', '.csv')

# How many images to sample (evenly across the set) for EXIF GPS evidence.
SAMPLE_IMAGE_COUNT = 10

# Cap on track points used for distance checks; long logs are subsampled.
TRACK_SUBSAMPLE_MAX = 512

# A sampled image matches when some (subsampled) track point is this close.
# Generous versus the trigger-log matcher's 300 m because subsampling opens
# gaps between the checked points; a wrong flight is still kilometres out.
TRACK_MATCH_MAX_M = 1000.0

# Fraction of sampled images that must match before a candidate is offered.
TRACK_MIN_MATCH_FRACTION = 0.6

# Fewer points than this is a placemark file or a stub, not a tracklog.
TRACK_MIN_POINTS = 10


class TrackDiscoveryService:
    """Score candidate track files against a flight's image positions."""

    def __init__(self):
        self.logger = LoggerService()
        self._bearing_service = BearingCalculationService()

    def discover_track(self, image_paths, candidate_files):
        """Return the best position-validated track file, or None.

        Args:
            image_paths (list): Paths of the images needing bearings.
            candidate_files (list): Candidate track file paths (any mix of
                KML/GPX/CSV; unparseable files are skipped silently).

        Returns:
            str | None: The winning candidate's path, or None when nothing
            clears TRACK_MIN_MATCH_FRACTION.
        """
        positions = self._sample_image_positions(image_paths)
        if len(positions) < 3:
            # Too little evidence to validate anything - offering a guess
            # would risk persisting wrong bearings into the result XML.
            return None

        best_path = None
        best_score = 0.0
        for path in candidate_files:
            points = self._parse_candidate(path)
            if len(points) < TRACK_MIN_POINTS:
                continue
            step = max(1, len(points) // TRACK_SUBSAMPLE_MAX)
            subsampled = points[::step]
            matched = sum(
                1 for lat, lon in positions
                if self._near_track(lat, lon, subsampled)
            )
            score = matched / len(positions)
            if score > best_score:
                best_score = score
                best_path = path

        if best_path is not None and best_score >= TRACK_MIN_MATCH_FRACTION:
            self.logger.info(
                f"Track discovery: {best_path} matched "
                f"{best_score:.0%} of {len(positions)} sampled images")
            return best_path
        return None

    def _sample_image_positions(self, image_paths):
        """EXIF GPS for up to SAMPLE_IMAGE_COUNT images spread across the set."""
        existing = [p for p in image_paths if p and os.path.exists(p)]
        if not existing:
            return []
        step = max(1, len(existing) // SAMPLE_IMAGE_COUNT)
        positions = []
        for path in existing[::step][:SAMPLE_IMAGE_COUNT]:
            try:
                gps = LocationInfo.get_gps(full_path=path)
            except Exception:
                continue
            if gps and 'latitude' in gps and 'longitude' in gps:
                positions.append((gps['latitude'], gps['longitude']))
        return positions

    def _parse_candidate(self, path):
        """Parse one candidate; unparseable or wrong-shape files become []."""
        try:
            points, _ = self._bearing_service.parse_track_file(path)
            return points
        except Exception:
            # Not an error: sweeps hand us every KML/CSV in the tree, and
            # most (detection exports, placemark files) simply are not tracks.
            return []

    @staticmethod
    def _near_track(lat, lon, track_points):
        """True when some track point lies within TRACK_MATCH_MAX_M."""
        for point in track_points:
            if LocationInfo.haversine_m(lat, lon, point.lat, point.lon) <= TRACK_MATCH_MAX_M:
                return True
        return False
