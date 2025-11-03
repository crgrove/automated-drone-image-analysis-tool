"""
BearingCalculationService - Calculate image bearings from tracks or GPS data.

Supports:
- Mode 1: Load track from KML/GPX/CSV and interpolate bearings
- Mode 2: Auto-calculate bearings from image GPS coordinates
- Turn detection for lawn-mower patterns
- Stationary/hover handling
- Bearing smoothing with circular statistics
"""

import math
import csv
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QObject, Signal, QThread
import numpy as np

from helpers.GeodesicHelper import GeodesicHelper
from core.services.LoggerService import LoggerService


@dataclass
class TrackPoint:
    """A single point in a GPS track."""
    timestamp: datetime
    lat: float
    lon: float
    alt: Optional[float] = None


@dataclass
class BearingResult:
    """Result of bearing calculation for a single image."""
    bearing_deg: float
    source: str  # 'kml', 'gpx', 'csv', 'auto_prev_next', 'auto_prev_leg', 'auto_next_leg', 'fallback_carry'
    quality: str  # 'good', 'turn_inferred', 'gap', 'hover_estimate'
    confidence: float = 1.0  # 0.0 to 1.0


class BearingCalculationService(QObject):
    """Service for calculating image bearings from tracks or image GPS."""

    # Signals
    progress_updated = Signal(int, int, str)  # current, total, message
    calculation_complete = Signal(dict)  # results dict: {image_path: BearingResult}
    calculation_error = Signal(str)  # error message
    calculation_cancelled = Signal()

    # Configuration constants
    MIN_SPEED_MPS = 0.5  # Minimum speed to consider drone moving (m/s)
    MIN_LEG_LENGTH_M = 2.5  # Minimum segment length (meters)
    GAP_THRESHOLD_SEC = 60.0  # Max time gap for interpolation (seconds)
    DEFAULT_TURN_THRESHOLD_M = 15.0  # Default perpendicular distance for turn detection
    PROGRESS_UPDATE_INTERVAL = 100  # Update progress every N images or 100ms

    def __init__(self):
        super().__init__()
        self._cancel_requested = False
        self._logger = LoggerService()

    def cancel(self):
        """Request cancellation of current calculation."""
        self._cancel_requested = True
        self._logger.info("Bearing calculation cancellation requested")

    def calculate_from_track(
        self,
        images: List[Dict[str, Any]],
        track_file_path: str
    ):
        """
        Calculate bearings for images using an external track file.

        Args:
            images: List of image dicts with 'path', 'timestamp', 'lat', 'lon'
            track_file_path: Path to KML, GPX, or CSV track file
        """
        self._cancel_requested = False

        try:
            # Parse track file
            file_ext = Path(track_file_path).suffix.lower()
            self._logger.info(f"Parsing track file: {track_file_path} ({file_ext})")

            if file_ext == '.kml':
                track_points = self._parse_kml(track_file_path)
                source_type = 'kml'
            elif file_ext == '.gpx':
                track_points = self._parse_gpx(track_file_path)
                source_type = 'gpx'
            elif file_ext == '.csv':
                track_points = self._parse_csv(track_file_path)
                source_type = 'csv'
            else:
                raise ValueError(f"Unsupported track file format: {file_ext}")

            if not track_points:
                raise ValueError("Track file contains no valid trackpoints")

            # Validate and sort trackpoints by timestamp
            track_points = self._validate_track(track_points)
            self._logger.info(f"Loaded {len(track_points)} trackpoints from {file_ext}")

            # Calculate bearings
            results = self._bearing_from_track(images, track_points, source_type)

            if not self._cancel_requested:
                self.calculation_complete.emit(results)
            else:
                self.calculation_cancelled.emit()

        except Exception as e:
            self._logger.error(f"Error calculating bearings from track: {str(e)}")
            self.calculation_error.emit(str(e))

    def calculate_auto(self, images: List[Dict[str, Any]]):
        """
        Auto-calculate bearings from image GPS coordinates only.

        Args:
            images: List of image dicts with 'path', 'timestamp', 'lat', 'lon'
        """
        self._cancel_requested = False

        try:
            self._logger.info(f"Auto-calculating bearings for {len(images)} images")

            # Calculate bearings
            results = self._bearing_auto(images)

            if not self._cancel_requested:
                self.calculation_complete.emit(results)
            else:
                self.calculation_cancelled.emit()

        except Exception as e:
            self._logger.error(f"Error auto-calculating bearings: {str(e)}")
            self.calculation_error.emit(str(e))

    def _parse_kml(self, file_path: str) -> List[TrackPoint]:
        """Parse KML file to extract trackpoints."""
        try:
            from fastkml import kml
        except ImportError:
            raise ImportError("fastkml library not installed. Run: pip install fastkml")

        track_points = []

        with open(file_path, 'rb') as f:
            doc = f.read()

        k = kml.KML()
        k.from_string(doc)

        # Recursively extract placemarks and tracks
        def extract_from_feature(feature):
            if hasattr(feature, 'features'):
                for f in feature.features():
                    extract_from_feature(f)

            # Handle gx:Track (timestamped coordinates)
            if hasattr(feature, '_geometry') and feature._geometry:
                geom = feature._geometry

                # Check if it's a gx:Track or LineString with timestamps
                if hasattr(geom, 'coords'):
                    coords = list(geom.coords)

                    # Try to get timestamps from gx:when elements
                    # For simple LineString without timestamps, skip
                    if hasattr(feature, 'timeStamp') and feature.timeStamp:
                        # Single timestamp for placemark
                        ts = self._parse_kml_timestamp(feature.timeStamp)
                        if ts and len(coords) > 0:
                            lon, lat, alt = coords[0][0], coords[0][1], coords[0][2] if len(coords[0]) > 2 else 0
                            track_points.append(TrackPoint(ts, lat, lon, alt))
                    elif hasattr(feature, '_times') and feature._times:
                        # gx:Track with multiple timestamps
                        for i, coord in enumerate(coords):
                            if i < len(feature._times):
                                ts = feature._times[i]
                                lon, lat = coord[0], coord[1]
                                alt = coord[2] if len(coord) > 2 else None
                                track_points.append(TrackPoint(ts, lat, lon, alt))

        # Extract from all documents and folders
        for feature in k.features():
            extract_from_feature(feature)

        return track_points

    def _parse_gpx(self, file_path: str) -> List[TrackPoint]:
        """Parse GPX file to extract trackpoints."""
        try:
            import gpxpy
        except ImportError:
            raise ImportError("gpxpy library not installed. Run: pip install gpxpy")

        track_points = []

        with open(file_path, 'r', encoding='utf-8') as f:
            gpx = gpxpy.parse(f)

        # Extract all track points
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    if point.time:
                        # Ensure timezone-aware datetime
                        ts = point.time
                        if ts.tzinfo is None:
                            ts = ts.replace(tzinfo=timezone.utc)

                        track_points.append(TrackPoint(
                            timestamp=ts,
                            lat=point.latitude,
                            lon=point.longitude,
                            alt=point.elevation
                        ))

        return track_points

    def _parse_csv(self, file_path: str) -> List[TrackPoint]:
        """
        Parse CSV file to extract trackpoints.

        Expected CSV format:
        - Header row required
        - Columns: timestamp, lat/latitude, lon/longitude, alt/altitude (optional)
        - Timestamp formats: ISO-8601, Unix timestamp, or common date formats
        """
        track_points = []

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Detect column names (case-insensitive)
            if not reader.fieldnames:
                raise ValueError("CSV file has no header row")

            fieldnames_lower = {k.lower(): k for k in reader.fieldnames}

            # Find timestamp column
            ts_col = None
            for name in ['timestamp', 'time', 'datetime', 'date']:
                if name in fieldnames_lower:
                    ts_col = fieldnames_lower[name]
                    break

            if not ts_col:
                raise ValueError("CSV must have a 'timestamp', 'time', or 'datetime' column")

            # Find lat/lon columns
            lat_col = None
            for name in ['lat', 'latitude']:
                if name in fieldnames_lower:
                    lat_col = fieldnames_lower[name]
                    break

            lon_col = None
            for name in ['lon', 'longitude', 'lng']:
                if name in fieldnames_lower:
                    lon_col = fieldnames_lower[name]
                    break

            if not lat_col or not lon_col:
                raise ValueError("CSV must have 'lat'/'latitude' and 'lon'/'longitude' columns")

            # Find altitude column (optional)
            alt_col = None
            for name in ['alt', 'altitude', 'elevation']:
                if name in fieldnames_lower:
                    alt_col = fieldnames_lower[name]
                    break

            # Parse rows
            for row in reader:
                try:
                    ts = self._parse_timestamp(row[ts_col])
                    lat = float(row[lat_col])
                    lon = float(row[lon_col])
                    alt = float(row[alt_col]) if alt_col and row[alt_col] else None

                    track_points.append(TrackPoint(ts, lat, lon, alt))
                except (ValueError, KeyError) as e:
                    # Skip invalid rows
                    continue

        return track_points

    def _parse_timestamp(self, ts_str: str) -> datetime:
        """Parse timestamp string to datetime object."""
        ts_str = ts_str.strip()

        # Try Unix timestamp
        try:
            return datetime.fromtimestamp(float(ts_str), tz=timezone.utc)
        except (ValueError, OSError):
            pass

        # Try ISO-8601
        try:
            dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            pass

        # Try common formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y/%m/%d %H:%M:%S',
            '%d/%m/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M:%S',
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(ts_str, fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue

        raise ValueError(f"Unable to parse timestamp: {ts_str}")

    def _parse_kml_timestamp(self, timestamp_obj) -> Optional[datetime]:
        """Parse KML timestamp object."""
        if hasattr(timestamp_obj, 'timestamp'):
            ts = timestamp_obj.timestamp
            if isinstance(ts, datetime):
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                return ts
        return None

    def _validate_track(self, track_points: List[TrackPoint]) -> List[TrackPoint]:
        """Validate and sort trackpoints by timestamp."""
        if not track_points:
            raise ValueError("No trackpoints found in file")

        # Remove duplicates and sort by timestamp
        track_points = sorted(track_points, key=lambda p: p.timestamp)

        # Check for monotonic timestamps (warn but don't fail)
        for i in range(1, len(track_points)):
            if track_points[i].timestamp < track_points[i-1].timestamp:
                self._logger.warning(f"Track has non-monotonic timestamps at index {i}")

        return track_points

    def _bearing_from_track(
        self,
        images: List[Dict[str, Any]],
        track: List[TrackPoint],
        source_type: str
    ) -> Dict[str, BearingResult]:
        """
        Calculate bearings for images using track interpolation.

        Mode 1 implementation from spec.
        """
        results = {}
        total = len(images)
        last_valid_bearing = None

        for idx, img in enumerate(images):
            if self._cancel_requested:
                break

            # Emit progress
            if idx % self.PROGRESS_UPDATE_INTERVAL == 0 or idx == total - 1:
                self.progress_updated.emit(idx + 1, total, f"Processing {source_type.upper()} track...")

            # Get image timestamp
            img_time = img.get('timestamp')
            if not img_time:
                self._logger.warning(f"Image {img['path']} has no timestamp, skipping")
                continue

            # Ensure timezone-aware
            if isinstance(img_time, datetime) and img_time.tzinfo is None:
                img_time = img_time.replace(tzinfo=timezone.utc)

            # Find bracketing trackpoints
            k = self._find_bracket_index(track, img_time)

            if k == 0:
                # Before first trackpoint - use first segment bearing
                bearing = GeodesicHelper.initial_course(
                    track[0].lat, track[0].lon,
                    track[1].lat, track[1].lon
                )
                quality = 'gap'  # Outside track range
            elif k >= len(track):
                # After last trackpoint - use last segment bearing
                bearing = GeodesicHelper.initial_course(
                    track[-2].lat, track[-2].lon,
                    track[-1].lat, track[-1].lon
                )
                quality = 'gap'  # Outside track range
            else:
                # Between trackpoints k-1 and k
                p1, p2 = track[k-1], track[k]

                # Calculate segment bearing
                bearing = GeodesicHelper.initial_course(
                    p1.lat, p1.lon, p2.lat, p2.lon
                )

                # Check if stationary (slow speed)
                distance = GeodesicHelper.haversine_distance(
                    p1.lat, p1.lon, p2.lat, p2.lon
                )
                time_diff = (p2.timestamp - p1.timestamp).total_seconds()

                if time_diff > 0 and distance / time_diff < self.MIN_SPEED_MPS:
                    # Stationary - inherit last valid bearing
                    if last_valid_bearing is not None:
                        bearing = last_valid_bearing
                        quality = 'hover_estimate'
                    else:
                        quality = 'good'
                else:
                    quality = 'good'
                    last_valid_bearing = bearing

            results[img['path']] = BearingResult(
                bearing_deg=bearing,
                source=source_type,
                quality=quality
            )

        return results

    def _find_bracket_index(self, track: List[TrackPoint], img_time: datetime) -> int:
        """
        Find index k such that track[k-1] <= img_time <= track[k].

        Returns:
            - 0 if img_time < track[0].timestamp
            - len(track) if img_time > track[-1].timestamp
            - k where track[k-1].timestamp <= img_time <= track[k].timestamp
        """
        # Binary search
        left, right = 0, len(track)

        while left < right:
            mid = (left + right) // 2
            if track[mid].timestamp < img_time:
                left = mid + 1
            else:
                right = mid

        return left

    def _bearing_auto(self, images: List[Dict[str, Any]]) -> Dict[str, BearingResult]:
        """
        Auto-calculate bearings from image GPS coordinates.

        Mode 2 implementation from spec.
        """
        from helpers.LocationInfo import LocationInfo
        from helpers.MetaDataHelper import MetaDataHelper
        import piexif

        self._logger.info(f"Starting auto-bearing calculation for {len(images)} images")

        # Extract GPS and timestamps if not already provided
        imgs_with_gps = []
        total = len(images)

        # Debug: Check first image structure
        if len(images) > 0:
            first_img = images[0]
            self._logger.info(f"First image data: path={first_img.get('path')}, lat={first_img.get('lat')}, lon={first_img.get('lon')}, timestamp={first_img.get('timestamp')}")

        for idx, img in enumerate(images):
            # Emit progress during extraction
            if idx % 10 == 0 or idx == total - 1:
                self.progress_updated.emit(idx + 1, total, "Extracting GPS data...")

            # Check if GPS/timestamp already extracted
            if img.get('lat') is None or img.get('lon') is None or img.get('timestamp') is None:
                # Extract from EXIF
                try:
                    exif_data = MetaDataHelper.get_exif_data_piexif(img['path'])

                    # Get GPS
                    gps_data = LocationInfo.get_gps(exif_data=exif_data)
                    if not gps_data:
                        self._logger.debug(f"Image {img['path']} has no GPS in EXIF")
                        continue

                    img['lat'] = gps_data.get('latitude')
                    img['lon'] = gps_data.get('longitude')

                    # Get timestamp
                    timestamp = None
                    if exif_data and 'Exif' in exif_data:
                        datetime_original = exif_data['Exif'].get(piexif.ExifIFD.DateTimeOriginal)
                        if datetime_original:
                            datetime_str = datetime_original.decode('utf-8') if isinstance(datetime_original, bytes) else datetime_original
                            try:
                                timestamp = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
                            except ValueError:
                                pass

                        if not timestamp:
                            datetime_tag = exif_data['Exif'].get(piexif.ExifIFD.DateTime)
                            if datetime_tag:
                                datetime_str = datetime_tag.decode('utf-8') if isinstance(datetime_tag, bytes) else datetime_tag
                                try:
                                    timestamp = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
                                except ValueError:
                                    pass

                    img['timestamp'] = timestamp

                except Exception as e:
                    self._logger.error(f"Error extracting data from {img['path']}: {e}")
                    import traceback
                    self._logger.error(traceback.format_exc())
                    continue

            # Add to list if has GPS
            if img.get('lat') is not None and img.get('lon') is not None:
                imgs_with_gps.append(img)

        self._logger.info(f"Extracted GPS from {len(imgs_with_gps)}/{total} images")

        if len(imgs_with_gps) < 2:
            raise ValueError("Need at least 2 images with GPS for auto-calculation")

        # Sort by timestamp
        imgs_with_gps.sort(key=lambda x: x.get('timestamp', datetime.min))

        N = len(imgs_with_gps)
        results = {}
        last_valid_bearing = None

        # Calculate auto turn threshold from data
        turn_threshold = self._calculate_turn_threshold(imgs_with_gps)
        self._logger.info(f"Auto-calculated turn threshold: {turn_threshold:.1f}m")

        for i in range(N):
            if self._cancel_requested:
                break

            # Emit progress
            if i % self.PROGRESS_UPDATE_INTERVAL == 0 or i == N - 1:
                self.progress_updated.emit(i + 1, N, "Auto-calculating bearings...")

            img = imgs_with_gps[i]
            lat, lon = img['lat'], img['lon']

            # Handle first/last images
            if i == 0:
                bearing = GeodesicHelper.initial_course(
                    lat, lon,
                    imgs_with_gps[1]['lat'], imgs_with_gps[1]['lon']
                )
                source = 'auto_prev_next'
                quality = 'good'
                last_valid_bearing = bearing

            elif i == N - 1:
                bearing = GeodesicHelper.initial_course(
                    imgs_with_gps[N-2]['lat'], imgs_with_gps[N-2]['lon'],
                    lat, lon
                )
                source = 'auto_prev_next'
                quality = 'good'

            else:
                # Middle images - improved turn detection for lawn-mower patterns
                # Key insight: Drone doesn't take pictures during turns, so there are gaps
                # We need to check ANGULAR alignment, not perpendicular distance

                prev_img = imgs_with_gps[i-1]
                next_img = imgs_with_gps[i+1]

                # Angular threshold for considering points aligned (degrees)
                # Tighter threshold to avoid GPS noise causing misalignment
                ANGLE_THRESHOLD = 20.0

                # Check alignment with PREVIOUS leg using best-fit bearing from multiple points
                aligned_with_prev_leg = False
                if i >= 2:
                    prev_prev = imgs_with_gps[i-2]

                    # Calculate leg bearing using the furthest points available for stability
                    # Look back up to 5 points or start of data
                    leg_start_idx = max(0, i - 5)
                    leg_bearing = GeodesicHelper.initial_course(
                        imgs_with_gps[leg_start_idx]['lat'], imgs_with_gps[leg_start_idx]['lon'],
                        prev_img['lat'], prev_img['lon']
                    )

                    # Bearing from previous point to current point (i-1 → i)
                    current_from_prev_bearing = GeodesicHelper.initial_course(
                        prev_img['lat'], prev_img['lon'],
                        lat, lon
                    )

                    # Check if bearings are similar (angular alignment)
                    angle_diff = abs(GeodesicHelper.angle_difference_deg(
                        leg_bearing, current_from_prev_bearing
                    ))

                    # If angles are similar, we're continuing on the same leg
                    if angle_diff <= ANGLE_THRESHOLD:
                        aligned_with_prev_leg = True
                        # Use the stable leg bearing (averaged over multiple points)
                        bearing = leg_bearing
                        source = 'auto_prev_leg'
                        quality = 'good'
                        last_valid_bearing = bearing

                        # Debug logging
                        if i <= 10:  # Log first 10 points
                            self._logger.info(f"Point {i}: Aligned with PREV leg. leg_bearing={leg_bearing:.2f}°, point_bearing={current_from_prev_bearing:.2f}°, diff={angle_diff:.2f}°")

                # If NOT aligned with previous leg, check NEXT leg using best-fit bearing
                if not aligned_with_prev_leg and i <= N - 3:
                    next_next = imgs_with_gps[i+2]

                    # Calculate leg bearing using the furthest points available for stability
                    # Look ahead up to 5 points or end of data
                    leg_end_idx = min(N - 1, i + 6)
                    next_leg_bearing = GeodesicHelper.initial_course(
                        next_img['lat'], next_img['lon'],
                        imgs_with_gps[leg_end_idx]['lat'], imgs_with_gps[leg_end_idx]['lon']
                    )

                    # Bearing from current point to next point (i → i+1)
                    current_to_next_bearing = GeodesicHelper.initial_course(
                        lat, lon,
                        next_img['lat'], next_img['lon']
                    )

                    # Check if bearings are similar (angular alignment)
                    angle_diff = abs(GeodesicHelper.angle_difference_deg(
                        next_leg_bearing, current_to_next_bearing
                    ))

                    # If angles are similar, we're starting the next leg
                    if angle_diff <= ANGLE_THRESHOLD:
                        # Use the stable leg bearing (averaged over multiple points)
                        bearing = next_leg_bearing
                        source = 'auto_next_leg'
                        quality = 'turn_inferred'

                        # Debug logging
                        if i <= 10:
                            self._logger.info(f"Point {i}: Aligned with NEXT leg. leg_bearing={next_leg_bearing:.2f}°, point_bearing={current_to_next_bearing:.2f}°, diff={angle_diff:.2f}°")
                    else:
                        # Not aligned with either leg - we're in transition between legs
                        # Use bearing from current to next point as best estimate
                        bearing = current_to_next_bearing
                        source = 'auto_prev_next'
                        quality = 'turn_inferred'

                        # Debug logging
                        if i <= 10:
                            self._logger.info(f"Point {i}: NOT aligned with either leg. Using current→next bearing={current_to_next_bearing:.2f}°")

                # Fallback if we only have 3 points total (can't check 2 points ahead)
                elif not aligned_with_prev_leg:
                    # Use bearing from prev to current
                    bearing = GeodesicHelper.initial_course(
                        prev_img['lat'], prev_img['lon'],
                        lat, lon
                    )
                    source = 'auto_prev_to_current'
                    quality = 'good'
                    last_valid_bearing = bearing

                # Check for stationary segment
                seg_len = GeodesicHelper.haversine_distance(
                    prev_img['lat'], prev_img['lon'],
                    lat, lon
                )
                if seg_len < self.MIN_LEG_LENGTH_M and last_valid_bearing is not None:
                    bearing = last_valid_bearing
                    source = 'fallback_carry'
                    quality = 'hover_estimate'

            results[img['path']] = BearingResult(
                bearing_deg=bearing,
                source=source,
                quality=quality
            )

        # Apply smoothing - DISABLED for lawn-mower patterns
        # Smoothing averages across leg boundaries which ruins bearings
        # results = self._apply_smoothing(results, imgs_with_gps)

        return results

    def _calculate_turn_threshold(self, images: List[Dict[str, Any]]) -> float:
        """
        Auto-calculate turn threshold from perpendicular distance distribution.

        Uses 95th percentile of perpendicular distances.
        """
        if len(images) < 5:
            return self.DEFAULT_TURN_THRESHOLD_M

        perp_dists = []

        for i in range(1, len(images) - 1):
            lat, lon = images[i]['lat'], images[i]['lon']
            prev_lat, prev_lon = images[i-1]['lat'], images[i-1]['lon']
            next_lat, next_lon = images[i+1]['lat'], images[i+1]['lon']

            d = GeodesicHelper.point_to_segment_distance(
                lat, lon, prev_lat, prev_lon, next_lat, next_lon
            )
            perp_dists.append(d)

        if not perp_dists:
            return self.DEFAULT_TURN_THRESHOLD_M

        # Use 85th percentile as threshold (below this is considered straight)
        threshold = np.percentile(perp_dists, 85)

        # Clamp to reasonable range
        threshold = max(5.0, min(threshold, 30.0))

        return threshold

    def _apply_smoothing(
        self,
        results: Dict[str, BearingResult],
        images: List[Dict[str, Any]]
    ) -> Dict[str, BearingResult]:
        """Apply circular smoothing to bearing results."""
        if len(images) < 5:
            return results

        # Extract bearings in image order
        bearings = []
        paths = []
        for img in images:
            path = img['path']
            if path in results:
                bearings.append(results[path].bearing_deg)
                paths.append(path)

        if len(bearings) < 5:
            return results

        # Smooth bearings
        smoothed = GeodesicHelper.smooth_bearings_circular(
            bearings, window=5, use_savgol=True
        )

        # Update results
        for path, smoothed_bearing in zip(paths, smoothed):
            results[path].bearing_deg = smoothed_bearing

        return results
