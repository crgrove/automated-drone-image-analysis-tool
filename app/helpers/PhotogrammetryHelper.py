"""
PhotogrammetryHelper - Geometry for manual FOV (field-of-view) alignment.

Provides the math used by the Align Image feature, where the user pins a drone
image to satellite imagery with control points (the four image corners plus
optional interior tie points).

- FovHomography: a planar pixel<->GPS mapping fit from those control points. A
  camera viewing flat ground relates the image to the ground by a projective
  transform; four point correspondences determine it exactly, additional tie
  points refine it by least squares. This is the fallback path for AOI GPS
  estimation when terrain (DEM) data is not available.
- validate_alignment: rejects degenerate corner quadrilaterals before a
  transform is built.

The DEM-resection path (camera-pose recovery) is added separately and also
lives in this module.
"""

import math
from typing import List, Optional, Sequence, Tuple

import cv2
import numpy as np

# WGS-84 Earth radius in metres. Matches AOIService and GeodesicHelper so the
# refined geometry stays consistent with the rest of the codebase.
EARTH_RADIUS_M = 6378137.0

# Pixel corners of the drone image, in the order corner GPS coordinates are
# stored and supplied: top-left, top-right, bottom-right, bottom-left.
CORNER_ORDER = ("tl", "tr", "br", "bl")


def gps_to_local_enu(lat, lon, origin_lat, origin_lon):
    """Convert a GPS coordinate to local East/North metres about an origin.

    Uses a tangent-plane approximation; accurate to well under a metre over a
    single drone image footprint.
    """
    cos_lat = math.cos(math.radians(origin_lat))
    east = math.radians(lon - origin_lon) * EARTH_RADIUS_M * cos_lat
    north = math.radians(lat - origin_lat) * EARTH_RADIUS_M
    return east, north


def local_enu_to_gps(east, north, origin_lat, origin_lon):
    """Convert local East/North metres back to a GPS coordinate."""
    cos_lat = math.cos(math.radians(origin_lat))
    lat = origin_lat + math.degrees(north / EARTH_RADIUS_M)
    lon = origin_lon + math.degrees(east / (EARTH_RADIUS_M * cos_lat))
    return lat, lon


def validate_alignment(corners_gps: Sequence[Tuple[float, float]]) -> bool:
    """Return True if four corner coordinates form a usable footprint quad.

    Rejects missing/non-finite values, coincident corners, non-convex or
    self-intersecting (bow-tie) quads, and quads with a negligible area. A
    convex non-degenerate quad guarantees the resulting homography is
    invertible.

    Args:
        corners_gps: four (lat, lon) pairs in TL, TR, BR, BL order.
    """
    if corners_gps is None or len(corners_gps) != 4:
        return False

    for corner in corners_gps:
        if corner is None or len(corner) != 2:
            return False
        lat, lon = corner
        if not (math.isfinite(lat) and math.isfinite(lon)):
            return False
        if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
            return False

    origin_lat = sum(c[0] for c in corners_gps) / 4.0
    origin_lon = sum(c[1] for c in corners_gps) / 4.0
    points = [gps_to_local_enu(lat, lon, origin_lat, origin_lon) for lat, lon in corners_gps]

    # No two corners may coincide.
    for i in range(4):
        for j in range(i + 1, 4):
            if math.hypot(points[i][0] - points[j][0], points[i][1] - points[j][1]) < 0.5:
                return False

    # Convex with a consistent winding: every turn must have the same sign.
    signs = []
    for i in range(4):
        ax, ay = points[i]
        bx, by = points[(i + 1) % 4]
        cx, cy = points[(i + 2) % 4]
        cross = (bx - ax) * (cy - by) - (by - ay) * (cx - bx)
        signs.append(cross)
    if any(s == 0.0 for s in signs):
        return False
    if not (all(s > 0.0 for s in signs) or all(s < 0.0 for s in signs)):
        return False

    # Shoelace area must be non-negligible.
    area = 0.0
    for i in range(4):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % 4]
        area += x1 * y2 - x2 * y1
    if abs(area) / 2.0 < 1.0:
        return False

    return True


def corners_are_mirrored(corners_gps) -> bool:
    """Return True if the four corners are in a mirrored (flipped) order.

    The corners correspond to drone-image pixels (0,0), (W,0), (W,H), (0,H).
    A real photo always projects onto the ground as an orientation-preserving
    map, so a correct corner quad has one fixed winding. The opposite winding
    means two corners were placed on the wrong handles - typically the top and
    bottom (or left and right) corners swapped - which would map the image to
    the ground mirrored.

    Args:
        corners_gps: four (lat, lon) pairs in TL, TR, BR, BL order.
    """
    if not corners_gps or len(corners_gps) != 4:
        return False
    origin_lat = sum(c[0] for c in corners_gps) / 4.0
    origin_lon = sum(c[1] for c in corners_gps) / 4.0
    points = [gps_to_local_enu(lat, lon, origin_lat, origin_lon)
              for lat, lon in corners_gps]
    area = 0.0
    for i in range(4):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % 4]
        area += x1 * y2 - x2 * y1
    # A correct corner order yields a negative signed area; a positive area
    # means the quad winding is reversed, i.e. the corners are mirrored.
    return area > 0.0


class FovHomography:
    """Planar pixel<->GPS mapping fit from manual FOV alignment control points.

    Source points are drone-image pixels; destination points are GPS
    coordinates expressed in a local East/North metres frame about the four
    corners' centroid. The four image-corner correspondences are the primary
    control and are fit first (exact for four points); optional interior tie
    points then refine the fit by least squares.

    A tie point that grossly disagrees with the four-corner fit - almost
    always because its two handles were placed on the wrong layers (the drone
    image and the map swapped) - is dropped before the final fit, so a single
    misplaced tie point cannot drag the carefully placed corners off.
    """

    # A tie point whose ground position disagrees with the four-corner fit by
    # more than this fraction of the footprint diagonal (or the floor below,
    # whichever is larger) is treated as a mistake and dropped.
    TIE_POINT_REJECT_FRACTION = 0.12
    TIE_POINT_REJECT_FLOOR_M = 20.0

    def __init__(self, corners_gps, width, height, tie_points=None):
        """
        Args:
            corners_gps: four (lat, lon) pairs for the drone-image pixel
                corners (0,0), (W,0), (W,H), (0,H) in that order.
            width: drone image width in pixels.
            height: drone image height in pixels.
            tie_points: optional list of (u, v, lat, lon) extra correspondences.

        Raises:
            ValueError: if the inputs cannot produce an invertible homography.

        Attributes:
            tie_points: the supplied tie points consistent with the four
                corners; these were used in the fit.
            rejected_tie_points: the supplied tie points dropped as
                inconsistent (e.g. their two handles were placed on the wrong
                layers).
        """
        if corners_gps is None or len(corners_gps) != 4:
            raise ValueError("FovHomography requires exactly four corner coordinates")
        if not width or not height or width <= 0 or height <= 0:
            raise ValueError("FovHomography requires positive image dimensions")

        self.width = float(width)
        self.height = float(height)

        supplied_ties = list(tie_points) if tie_points else []

        # Local ENU origin: centroid of the four corners. The corners are
        # always present, so the frame does not shift when tie points are
        # added or filtered out.
        self.origin_lat = sum(c[0] for c in corners_gps) / 4.0
        self.origin_lon = sum(c[1] for c in corners_gps) / 4.0

        corner_src = np.array([
            (0.0, 0.0),
            (self.width, 0.0),
            (self.width, self.height),
            (0.0, self.height),
        ], dtype=np.float64)
        corner_dst = np.array([
            gps_to_local_enu(lat, lon, self.origin_lat, self.origin_lon)
            for lat, lon in corners_gps
        ], dtype=np.float64)

        # The four corners are the primary control. Fit them on their own
        # first (exact for four points); tie points only refine this.
        corner_homography, _ = cv2.findHomography(corner_src, corner_dst, 0)
        if corner_homography is None:
            raise ValueError("FovHomography: failed to fit a homography to the corners")

        # Drop tie points inconsistent with the four-corner fit so a misplaced
        # one cannot drag the corners off. The threshold scales with the
        # footprint so it works at any altitude.
        diagonal_m = math.hypot(
            corner_dst[2][0] - corner_dst[0][0],
            corner_dst[2][1] - corner_dst[0][1],
        )
        max_error_m = max(self.TIE_POINT_REJECT_FLOOR_M,
                          self.TIE_POINT_REJECT_FRACTION * diagonal_m)
        self.tie_points, self.rejected_tie_points = self._filter_tie_points(
            corner_homography, supplied_ties, max_error_m
        )

        # Final fit: the four corners plus the tie points that survived.
        if self.tie_points:
            tie_src = np.array([(float(u), float(v))
                                for u, v, _, _ in self.tie_points], dtype=np.float64)
            tie_dst = np.array([
                gps_to_local_enu(lat, lon, self.origin_lat, self.origin_lon)
                for _, _, lat, lon in self.tie_points], dtype=np.float64)
            homography, _ = cv2.findHomography(
                np.vstack([corner_src, tie_src]),
                np.vstack([corner_dst, tie_dst]), 0
            )
            if homography is None:
                homography = corner_homography  # refined fit failed - use corners
        else:
            homography = corner_homography

        try:
            inverse = np.linalg.inv(homography)
        except np.linalg.LinAlgError as exc:
            raise ValueError("FovHomography: control points produced a singular transform") from exc

        self._homography = homography
        self._inverse = inverse

    def _filter_tie_points(self, corner_homography, tie_points, max_error_m):
        """Split tie points by whether they agree with the four-corner fit.

        Each tie point claims a pixel maps to a GPS coordinate. Comparing that
        GPS with the position the four-corner homography predicts for the same
        pixel catches points whose two handles were placed on the wrong layers
        (the drone image and the map swapped) - a common mistake - before they
        corrupt the least-squares fit.

        Args:
            corner_homography: the 3x3 transform fit from the four corners only.
            tie_points: supplied (u, v, lat, lon) tuples.
            max_error_m: reject a tie point disagreeing by more metres than this.

        Returns:
            (accepted, rejected) lists of (u, v, lat, lon) tuples.
        """
        accepted = []
        rejected = []
        for tie in tie_points:
            try:
                u, v, lat, lon = tie
                point = np.array([[[float(u), float(v)]]], dtype=np.float64)
                pred_e, pred_n = cv2.perspectiveTransform(point, corner_homography)[0][0]
                tie_e, tie_n = gps_to_local_enu(lat, lon, self.origin_lat, self.origin_lon)
                error_m = math.hypot(pred_e - tie_e, pred_n - tie_n)
            except (ValueError, TypeError, cv2.error):
                rejected.append(tuple(tie))
                continue
            if math.isfinite(error_m) and error_m <= max_error_m:
                accepted.append((float(u), float(v), float(lat), float(lon)))
            else:
                rejected.append(tuple(tie))
        return accepted, rejected

    def pixel_to_gps(self, u, v) -> Tuple[float, float]:
        """Map a drone-image pixel (u, v) to a (lat, lon) coordinate."""
        point = np.array([[[float(u), float(v)]]], dtype=np.float64)
        east, north = cv2.perspectiveTransform(point, self._homography)[0][0]
        return local_enu_to_gps(east, north, self.origin_lat, self.origin_lon)

    def gps_to_pixel(self, lat, lon) -> Tuple[float, float]:
        """Map a (lat, lon) coordinate to a drone-image pixel (u, v)."""
        east, north = gps_to_local_enu(lat, lon, self.origin_lat, self.origin_lon)
        point = np.array([[[east, north]]], dtype=np.float64)
        u, v = cv2.perspectiveTransform(point, self._inverse)[0][0]
        return float(u), float(v)


# --- DEM resection (camera pose recovery) ---
#
# When terrain data is available the alignment control points, with their DEM
# elevations, let us recover the full camera pose with solvePnP. Ray-casting
# pixels against the terrain surface then handles variable GSD and relief
# inside the footprint - things a planar homography cannot model.

# SQPNP solves both planar and non-planar point sets without the planar pose
# ambiguity. Fall back to the iterative solver on older OpenCV builds.
_SOLVEPNP_FLAG = getattr(cv2, 'SOLVEPNP_SQPNP', cv2.SOLVEPNP_ITERATIVE)


def build_camera_matrix(focal_mm, sensor_w_mm, sensor_h_mm, width, height):
    """Build a 3x3 pinhole camera intrinsic matrix from physical parameters."""
    fx = focal_mm / (sensor_w_mm / width)
    fy = focal_mm / (sensor_h_mm / height)
    return np.array([
        [fx, 0.0, width / 2.0],
        [0.0, fy, height / 2.0],
        [0.0, 0.0, 1.0],
    ], dtype=np.float64)


def recover_camera_pose(object_points, image_points, camera_matrix,
                        max_reprojection_error_px=40.0):
    """Recover the camera pose from 2D-3D correspondences via solvePnP.

    Args:
        object_points: sequence of (x, y, z) world points in metres.
        image_points: sequence of (u, v) pixels, paired with object_points.
        camera_matrix: 3x3 intrinsic matrix.
        max_reprojection_error_px: reject the solve above this RMS error.

    Returns:
        (rvec, tvec, reprojection_error_px), or None if the solve fails or is
        too inaccurate. rvec/tvec map world points into the camera frame
        (X_cam = R @ X_world + t).
    """
    if len(object_points) != len(image_points) or len(object_points) < 4:
        return None

    obj = np.array(object_points, dtype=np.float64).reshape(-1, 1, 3)
    img = np.array(image_points, dtype=np.float64).reshape(-1, 1, 2)
    dist = np.zeros((5, 1), dtype=np.float64)

    try:
        ok, rvec, tvec = cv2.solvePnP(obj, img, camera_matrix, dist, flags=_SOLVEPNP_FLAG)
    except cv2.error:
        return None
    if not ok:
        return None

    projected, _ = cv2.projectPoints(obj, rvec, tvec, camera_matrix, dist)
    residuals = projected.reshape(-1, 2) - img.reshape(-1, 2)
    error = float(np.sqrt(np.mean(np.sum(residuals ** 2, axis=1))))
    if not math.isfinite(error) or error > max_reprojection_error_px:
        return None
    return rvec, tvec, error


def camera_center_world(rvec, tvec):
    """Return the camera centre in world coordinates from a solvePnP pose."""
    rotation, _ = cv2.Rodrigues(rvec)
    return (-rotation.T @ tvec).reshape(3)


def project_pixel_to_plane(rvec, tvec, camera_matrix, u, v, plane_z):
    """Intersect the ray through pixel (u, v) with the horizontal plane z=plane_z.

    Args:
        rvec, tvec: camera pose from recover_camera_pose.
        camera_matrix: 3x3 intrinsic matrix.
        u, v: pixel coordinates.
        plane_z: world Z (elevation) of the horizontal target plane.

    Returns:
        (x, y) world coordinates of the intersection, or None if the ray does
        not descend to the plane.
    """
    rotation, _ = cv2.Rodrigues(rvec)
    cam_center = (-rotation.T @ tvec).reshape(3)
    ray_cam = np.linalg.inv(camera_matrix) @ np.array([float(u), float(v), 1.0])
    ray_world = (rotation.T @ ray_cam.reshape(3, 1)).reshape(3)
    if abs(ray_world[2]) < 1e-12:
        return None
    t = (plane_z - cam_center[2]) / ray_world[2]
    if t <= 0:
        return None
    point = cam_center + t * ray_world
    return float(point[0]), float(point[1])
