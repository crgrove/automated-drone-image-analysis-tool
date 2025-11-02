"""
GeodesicHelper - Geodesic and geometric calculations for bearing recovery.

Provides utilities for:
- Great-circle bearing calculation (initial course)
- Geodesic distance (Haversine)
- Point-to-segment distance
- Circular statistics for angle smoothing
- Coordinate handling with antimeridian support
"""

import math
import numpy as np
from typing import Tuple, List, Optional


class GeodesicHelper:
    """Helper class for geodesic calculations on WGS-84 ellipsoid."""

    # WGS-84 Earth radius in meters
    EARTH_RADIUS_M = 6378137.0

    @staticmethod
    def initial_course(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the initial bearing (course) from point 1 to point 2.

        Uses the great-circle initial course formula. This is the bearing you would
        need to follow at the start of a journey along a great circle arc.

        Args:
            lat1: Latitude of first point in decimal degrees
            lon1: Longitude of first point in decimal degrees
            lat2: Latitude of second point in decimal degrees
            lon2: Longitude of second point in decimal degrees

        Returns:
            Initial bearing in degrees [0, 360), measured clockwise from North

        Note:
            - All coordinates assumed WGS-84
            - Handles antimeridian crossing (±180° longitude)
            - Returns 0.0 if points are identical or antipodal
        """
        # Handle identical points
        if abs(lat1 - lat2) < 1e-9 and abs(lon1 - lon2) < 1e-9:
            return 0.0

        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlon_rad = math.radians(lon2 - lon1)

        # Calculate bearing using initial course formula
        # θ = atan2(sin(Δλ)*cos(φ₂), cos(φ₁)*sin(φ₂) - sin(φ₁)*cos(φ₂)*cos(Δλ))
        x = math.sin(dlon_rad) * math.cos(lat2_rad)
        y = (math.cos(lat1_rad) * math.sin(lat2_rad) -
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad))

        bearing_rad = math.atan2(x, y)
        bearing_deg = math.degrees(bearing_rad)

        # Normalize to [0, 360)
        return (bearing_deg + 360.0) % 360.0

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great-circle distance between two points using Haversine formula.

        Args:
            lat1: Latitude of first point in decimal degrees
            lon1: Longitude of first point in decimal degrees
            lat2: Latitude of second point in decimal degrees
            lon2: Longitude of second point in decimal degrees

        Returns:
            Distance in meters

        Note:
            - Accurate for most distances, less precise for antipodal points
            - For very high accuracy, consider Vincenty's formula (more complex)
        """
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat_rad = math.radians(lat2 - lat1)
        dlon_rad = math.radians(lon2 - lon1)

        # Haversine formula
        a = (math.sin(dlat_rad / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(dlon_rad / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))

        return GeodesicHelper.EARTH_RADIUS_M * c

    @staticmethod
    def point_to_segment_distance(
        point_lat: float, point_lon: float,
        seg_lat1: float, seg_lon1: float,
        seg_lat2: float, seg_lon2: float
    ) -> float:
        """
        Calculate perpendicular distance from a point to a line segment.

        Uses planar approximation in local tangent plane for efficiency.
        Accurate enough for drone flight distances (<1km segments).

        Args:
            point_lat, point_lon: Point coordinates (decimal degrees)
            seg_lat1, seg_lon1: Segment start coordinates (decimal degrees)
            seg_lat2, seg_lon2: Segment end coordinates (decimal degrees)

        Returns:
            Perpendicular distance in meters

        Note:
            - For very long segments (>10km), consider more precise methods
            - Returns distance to nearest point on segment (not infinite line)
        """
        # Convert to local Cartesian coordinates (meters)
        # Use segment midpoint as origin for better accuracy
        mid_lat = (seg_lat1 + seg_lat2) / 2
        mid_lon = (seg_lon1 + seg_lon2) / 2

        # Meters per degree at this latitude
        m_per_deg_lat = 111132.92 - 559.82 * math.cos(2 * math.radians(mid_lat))
        m_per_deg_lon = 111412.84 * math.cos(math.radians(mid_lat))

        # Convert to Cartesian (meters from midpoint)
        px = (point_lon - mid_lon) * m_per_deg_lon
        py = (point_lat - mid_lat) * m_per_deg_lat

        x1 = (seg_lon1 - mid_lon) * m_per_deg_lon
        y1 = (seg_lat1 - mid_lat) * m_per_deg_lat

        x2 = (seg_lon2 - mid_lon) * m_per_deg_lon
        y2 = (seg_lat2 - mid_lat) * m_per_deg_lat

        # Segment vector
        dx = x2 - x1
        dy = y2 - y1

        # Handle degenerate segment (points are identical)
        seg_length_sq = dx * dx + dy * dy
        if seg_length_sq < 1e-10:
            # Distance to segment start/end (they're the same)
            return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)

        # Parameter t for closest point on infinite line
        # t = ((P - A) · (B - A)) / |B - A|²
        t = ((px - x1) * dx + (py - y1) * dy) / seg_length_sq

        # Clamp t to [0, 1] to stay on segment
        t = max(0.0, min(1.0, t))

        # Closest point on segment
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        # Distance from point to closest point
        dist = math.sqrt((px - closest_x) ** 2 + (py - closest_y) ** 2)

        return dist

    @staticmethod
    def normalize_angle_deg(angle: float) -> float:
        """Normalize angle to [0, 360) range."""
        return (angle % 360.0 + 360.0) % 360.0

    @staticmethod
    def angle_difference_deg(angle1: float, angle2: float) -> float:
        """
        Calculate the signed difference between two angles.

        Args:
            angle1: First angle in degrees
            angle2: Second angle in degrees

        Returns:
            Difference in degrees, in range [-180, 180)
            Positive means angle2 is clockwise from angle1
        """
        diff = (angle2 - angle1 + 180.0) % 360.0 - 180.0
        return diff

    @staticmethod
    def circular_mean(angles: List[float]) -> float:
        """
        Calculate the circular mean of a list of angles.

        Uses unit vector averaging to handle wraparound correctly.

        Args:
            angles: List of angles in degrees

        Returns:
            Mean angle in degrees [0, 360), or 0.0 if input is empty
        """
        if not angles:
            return 0.0

        # Convert to unit vectors and average
        angles_rad = np.radians(angles)
        x_sum = np.sum(np.cos(angles_rad))
        y_sum = np.sum(np.sin(angles_rad))

        # Convert back to angle
        mean_rad = np.arctan2(y_sum, x_sum)
        mean_deg = np.degrees(mean_rad)

        return GeodesicHelper.normalize_angle_deg(mean_deg)

    @staticmethod
    def circular_median(angles: List[float]) -> float:
        """
        Calculate the circular median of a list of angles.

        More robust to outliers than circular mean.

        Args:
            angles: List of angles in degrees

        Returns:
            Median angle in degrees [0, 360), or 0.0 if input is empty

        Note:
            Uses the approach of finding the angle that minimizes sum of
            angular distances to all other angles.
        """
        if not angles:
            return 0.0

        if len(angles) == 1:
            return GeodesicHelper.normalize_angle_deg(angles[0])

        # For small lists, use simple approach
        if len(angles) <= 5:
            # Try each angle as candidate median
            candidates = angles
        else:
            # For larger lists, use binned approach for efficiency
            angles_norm = [GeodesicHelper.normalize_angle_deg(a) for a in angles]
            candidates = angles_norm

        best_angle = 0.0
        min_sum_dist = float('inf')

        for candidate in candidates:
            # Sum of angular distances to all points
            sum_dist = sum(abs(GeodesicHelper.angle_difference_deg(candidate, a))
                          for a in angles)
            if sum_dist < min_sum_dist:
                min_sum_dist = sum_dist
                best_angle = candidate

        return GeodesicHelper.normalize_angle_deg(best_angle)

    @staticmethod
    def smooth_bearings_circular(
        bearings: List[float],
        window: int = 5,
        use_savgol: bool = True
    ) -> List[float]:
        """
        Smooth a sequence of bearings using circular statistics.

        Applies:
        1. Robust median filter (wrap-aware)
        2. Optional Savitzky-Golay filter on unwrapped angles

        Args:
            bearings: List of bearing angles in degrees
            window: Window size for filtering (must be odd)
            use_savgol: Whether to apply Savitzky-Golay after median filter

        Returns:
            Smoothed bearings in degrees [0, 360)
        """
        if len(bearings) < window:
            return bearings.copy()

        # Ensure window is odd
        if window % 2 == 0:
            window += 1

        half_window = window // 2
        smoothed = []

        # Step 1: Circular median filter
        for i in range(len(bearings)):
            # Get window around current point
            start = max(0, i - half_window)
            end = min(len(bearings), i + half_window + 1)
            window_vals = bearings[start:end]

            # Calculate circular median
            median_val = GeodesicHelper.circular_median(window_vals)
            smoothed.append(median_val)

        # Step 2: Optional Savitzky-Golay smoothing
        if use_savgol and len(smoothed) >= window:
            try:
                from scipy.signal import savgol_filter

                # Unwrap angles to avoid discontinuities at 0/360
                unwrapped = np.unwrap(np.radians(smoothed))

                # Apply Savitzky-Golay filter
                # Polynomial order 2, window as specified
                poly_order = min(2, window - 1)
                filtered = savgol_filter(unwrapped, window, poly_order)

                # Rewrap to [0, 360)
                smoothed = [GeodesicHelper.normalize_angle_deg(math.degrees(a))
                           for a in filtered]
            except ImportError:
                # scipy not available, skip Savitzky-Golay
                pass

        return smoothed

    @staticmethod
    def unwrap_angles(angles: List[float]) -> List[float]:
        """
        Unwrap a sequence of angles to avoid 360° discontinuities.

        Args:
            angles: List of angles in degrees

        Returns:
            Unwrapped angles (may be outside [0, 360))
        """
        if len(angles) <= 1:
            return angles.copy()

        unwrapped = [angles[0]]
        for i in range(1, len(angles)):
            diff = GeodesicHelper.angle_difference_deg(unwrapped[-1], angles[i])
            unwrapped.append(unwrapped[-1] + diff)

        return unwrapped
