"""
RectilinearGeometry.py - pure, stateless geometry for rectilinear shape detection.

Everything here works in processing-resolution pixels and knows nothing of
GSD, options dictionaries or AOIs: RectilinearShapeService turns physical
sizes into pixel ranges and hands them in. Keeping the geometry free of the
service lets it be unit-tested on synthetic frames and reused as a score term
by other algorithms (the boxiness map in particular).

Conventions:
    * ``ang`` is gradient orientation in radians, as returned by arctan2(gy, gx).
    * ``mag`` is Sobel magnitude divided by four, so a sharp step of height h
      in the working channel peaks at roughly h - the same 0-255 scale the
      contrast thresholds are expressed in.
    * A rectangle is a ``RotRect``: centre, long side, short side, and the
      direction of the long side in degrees, normalised to [0, 180).
"""

import math
from collections import namedtuple

import cv2
import numpy as np


# A rotated rectangle in pixel coordinates. ``angle_deg`` is the direction of
# the long side; ``length >= width`` always holds for rectangles built here.
RotRect = namedtuple('RotRect', ['cx', 'cy', 'length', 'width', 'angle_deg'])

# Offset (px) either side of a segment at which its cross-edge contrast is
# sampled. Two pixels clears the blurred edge itself on both sides.
_CONTRAST_OFFSET_PX = 2.0

# Samples taken along each segment when measuring its contrast.
_CONTRAST_SAMPLES = 16

# LSD parameters. OpenCV's defaults except the region-growing angle
# tolerance, widened from 22.5 degrees: on textured ground the default
# fragments a low-contrast edge into pieces too short to keep, and the
# pairing stage needs whole sides. Segment length and contrast gates
# remove the extra clutter this admits.
_LSD_SCALE = 0.8
_LSD_SIGMA_SCALE = 0.6
_LSD_QUANT = 2.0
_LSD_ANGLE_TOLERANCE_DEG = 30.0

# Re-centred fits per boxiness peak (see boxiness_hypotheses).
_BOXINESS_FIT_ITERATIONS = 3

# Half-width (px) of the band searched along a side's normal for its edge.
# Hypotheses are fitted from fragments, so the true edge can sit a pixel or
# two off the fitted line.
_EDGE_SEARCH_HALF_WIDTH = 2


def _make_rect(cx, cy, side_a, side_b, angle_a_deg):
    """Build a RotRect from two side lengths, the first along ``angle_a_deg``."""
    if side_a >= side_b:
        return RotRect(float(cx), float(cy), float(side_a), float(side_b), float(angle_a_deg % 180.0))
    return RotRect(float(cx), float(cy), float(side_b), float(side_a), float((angle_a_deg + 90.0) % 180.0))


def rect_corners(rect):
    """Return the four corners of ``rect`` as a float32 (4, 2) array."""
    return cv2.boxPoints(((rect.cx, rect.cy), (rect.length, rect.width), rect.angle_deg)).astype(np.float32)


def _axial_difference_deg(a_deg, b_deg):
    """Smallest difference between two undirected line directions, in [0, 90]."""
    diff = abs(a_deg - b_deg) % 180.0
    return min(diff, 180.0 - diff)


def compute_gradients(gray):
    """Sobel gradients of the working channel.

    Args:
        gray (np.ndarray): Single-channel image (uint8 or float32).

    Returns:
        tuple: (mag, ang) float32 arrays - magnitude on the step-height scale
        described in the module header, and orientation in radians.
    """
    source = gray.astype(np.float32)
    gx = cv2.Sobel(source, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(source, cv2.CV_32F, 0, 1, ksize=3)
    mag = cv2.magnitude(gx, gy) * 0.25
    ang = np.arctan2(gy, gx).astype(np.float32)
    return mag, ang


def boxiness_weights(mag, noise_multiple=2.0):
    """Gradient weights for the boxiness map, with the noise floor removed.

    Weighting by raw magnitude lets a frame's background texture - present
    at every pixel of the window - outweigh a target's edges, which occupy
    only its perimeter. Subtracting a multiple of the frame's median
    magnitude zeroes most texture while barely denting a real edge.

    Args:
        mag (np.ndarray): Gradient magnitude.
        noise_multiple (float): Multiple of the median subtracted.

    Returns:
        np.ndarray: float32 weights, >= 0.
    """
    floor = noise_multiple * float(np.median(mag))
    return np.maximum(mag - floor, 0.0).astype(np.float32)


def boxiness_map(mag, ang, window_px, energy_floor, decimation=1):
    """Orientation-coherence ("boxiness") map.

    For gradient weight m and orientation phi inside a window:
        C4 = |sum m e^{i4phi}| / sum m   - 1 when every edge is at 90 degree multiples
        C2 = |sum m e^{i2phi}| / sum m   - 1 for a single straight edge
        B  = C4 * (1 - C2)               - high only where two perpendicular
                                           edge families are both present

    The component maps are first area-averaged down by ``decimation`` (an
    area resize is itself a box average, so the result is the same smoothing)
    which keeps the five float maps small on 48 MP frames.

    Args:
        mag (np.ndarray): Gradient magnitude.
        ang (np.ndarray): Gradient orientation in radians.
        window_px (float): Window side in full-resolution pixels.
        energy_floor (float): Minimum mean magnitude inside a window. Windows
            below it are near-flat and get B = 0, so a handful of noisy
            gradients cannot score high by chance.
        decimation (int): Integer reduction factor for the output grid.

    Returns:
        tuple: (B, C4, C2, theta, energy) on the decimated grid. ``theta`` is
        the dominant gradient orientation modulo 90 degrees, in degrees
        [0, 90); ``energy`` is the window mean magnitude.
    """
    decimation = max(1, int(decimation))
    height, width = mag.shape[:2]
    size = (max(1, width // decimation), max(1, height // decimation))

    def _reduced(component):
        if decimation == 1:
            return component
        return cv2.resize(component, size, interpolation=cv2.INTER_AREA)

    # Built and reduced one at a time so only one extra full-resolution
    # float map is alive at once.
    components = [_reduced(mag)]
    for multiple, trig in ((4.0, np.cos), (4.0, np.sin), (2.0, np.cos), (2.0, np.sin)):
        components.append(_reduced(mag * trig(multiple * ang)))

    window = max(3, int(round(window_px / decimation)))
    if window % 2 == 0:
        window += 1
    smoothed = [cv2.boxFilter(c, -1, (window, window), normalize=True, borderType=cv2.BORDER_REFLECT) for c in components]
    energy, cos4, sin4, cos2, sin2 = smoothed

    safe_energy = np.maximum(energy, 1e-6)
    c4 = np.sqrt(cos4 * cos4 + sin4 * sin4) / safe_energy
    c2 = np.sqrt(cos2 * cos2 + sin2 * sin2) / safe_energy
    c4 = np.clip(c4, 0.0, 1.0)
    c2 = np.clip(c2, 0.0, 1.0)
    boxiness = c4 * (1.0 - c2)
    boxiness[energy < energy_floor] = 0.0

    theta = (np.degrees(np.arctan2(sin4, cos4)) / 4.0) % 90.0
    return (
        boxiness.astype(np.float32),
        c4.astype(np.float32),
        c2.astype(np.float32),
        theta.astype(np.float32),
        energy.astype(np.float32),
    )


def _sample_nearest(image, xs, ys):
    """Nearest-pixel lookup with coordinates clamped to the image."""
    height, width = image.shape[:2]
    cols = np.clip(np.rint(xs).astype(np.int64), 0, width - 1)
    rows = np.clip(np.rint(ys).astype(np.int64), 0, height - 1)
    return image[rows, cols]


def segment_contrast(gray, segments):
    """Mean absolute intensity step across each segment.

    Samples the working channel a couple of pixels either side of each
    segment and averages the difference - an edge's contrast in the same
    0-255 units the operator sets ``min_edge_contrast`` in.

    Args:
        gray (np.ndarray): Working channel.
        segments (np.ndarray): (N, 4) float array of x1, y1, x2, y2.

    Returns:
        np.ndarray: (N,) float32 contrast per segment.
    """
    if len(segments) == 0:
        return np.zeros(0, dtype=np.float32)
    x1, y1, x2, y2 = (segments[:, k:k + 1] for k in range(4))
    lengths = np.maximum(np.hypot(x2 - x1, y2 - y1), 1e-6)
    normal_x = -(y2 - y1) / lengths
    normal_y = (x2 - x1) / lengths
    # Interior samples only: endpoints are where LSD is least certain.
    t = np.linspace(0.1, 0.9, _CONTRAST_SAMPLES, dtype=np.float32)[None, :]
    px = x1 + (x2 - x1) * t
    py = y1 + (y2 - y1) * t
    side_a = _sample_nearest(gray, px + normal_x * _CONTRAST_OFFSET_PX, py + normal_y * _CONTRAST_OFFSET_PX)
    side_b = _sample_nearest(gray, px - normal_x * _CONTRAST_OFFSET_PX, py - normal_y * _CONTRAST_OFFSET_PX)
    diff = np.abs(side_a.astype(np.float32) - side_b.astype(np.float32))
    return diff.mean(axis=1).astype(np.float32)


def detect_segments(gray, min_len_px, max_len_px, min_contrast):
    """Line segments of plausible length and contrast.

    Uses OpenCV's LSD. The detector object is created per call so nothing
    unpicklable is ever held on a service instance (AnalyzeService runs
    services in a multiprocessing pool).

    Args:
        gray (np.ndarray): uint8 working channel.
        min_len_px (float): Shortest segment kept.
        max_len_px (float): Longest segment kept.
        min_contrast (float): Minimum mean cross-segment step (0-255 scale).

    Returns:
        np.ndarray: (N, 4) float32 array of x1, y1, x2, y2. Empty (0, 4) when
        LSD finds nothing.
    """
    detector = cv2.createLineSegmentDetector(
        cv2.LSD_REFINE_STD, _LSD_SCALE, _LSD_SIGMA_SCALE, _LSD_QUANT, _LSD_ANGLE_TOLERANCE_DEG
    )
    lines = detector.detect(gray)[0]
    if lines is None or len(lines) == 0:
        return np.zeros((0, 4), dtype=np.float32)
    segments = lines.reshape(-1, 4).astype(np.float32)
    lengths = np.hypot(segments[:, 2] - segments[:, 0], segments[:, 3] - segments[:, 1])
    keep = (lengths >= min_len_px) & (lengths <= max_len_px)
    segments = segments[keep]
    if len(segments) == 0:
        return np.zeros((0, 4), dtype=np.float32)
    contrast = segment_contrast(gray, segments)
    return segments[contrast >= min_contrast]


class SegmentHash:
    """Uniform spatial hash of segment midpoints.

    Neighbour lookup is a handful of dictionary probes rather than a scan of
    every segment, keeping hypothesis generation near-linear in segment count.
    """

    def __init__(self, segments, cell_px):
        self.cell_px = max(1.0, float(cell_px))
        self.midpoints = np.column_stack((
            (segments[:, 0] + segments[:, 2]) * 0.5,
            (segments[:, 1] + segments[:, 3]) * 0.5,
        )) if len(segments) else np.zeros((0, 2), dtype=np.float32)
        self.cells = {}
        for index, (mx, my) in enumerate(self.midpoints):
            key = (int(mx // self.cell_px), int(my // self.cell_px))
            self.cells.setdefault(key, []).append(index)

    def query(self, x, y, radius_px):
        """Indices of segments whose midpoint may lie within ``radius_px`` of (x, y).

        A superset: callers apply their own exact test.
        """
        reach = int(math.ceil(radius_px / self.cell_px))
        cell_x = int(x // self.cell_px)
        cell_y = int(y // self.cell_px)
        found = []
        for dy in range(-reach, reach + 1):
            for dx in range(-reach, reach + 1):
                bucket = self.cells.get((cell_x + dx, cell_y + dy))
                if bucket:
                    found.extend(bucket)
        return found


def build_segment_hash(segments, cell_px):
    """Build a SegmentHash over ``segments`` with square cells of ``cell_px``."""
    return SegmentHash(segments, cell_px)


def _segment_direction_deg(segment):
    """Undirected direction of a segment, degrees in [0, 180)."""
    return math.degrees(math.atan2(segment[3] - segment[1], segment[2] - segment[0])) % 180.0


def _line_intersection(seg_a, seg_b):
    """Intersection of the infinite lines through two segments, or None if parallel."""
    x1, y1, x2, y2 = seg_a
    x3, y3, x4, y4 = seg_b
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-9:
        return None
    det_a = x1 * y2 - y1 * x2
    det_b = x3 * y4 - y3 * x4
    px = (det_a * (x3 - x4) - (x1 - x2) * det_b) / denom
    py = (det_a * (y3 - y4) - (y1 - y2) * det_b) / denom
    return px, py


def _mean_axis_deg(angle_a_deg, angle_b_deg):
    """Mean of two undirected directions that are already close (mod 180)."""
    delta = ((angle_b_deg - angle_a_deg + 90.0) % 180.0) - 90.0
    return (angle_a_deg + delta * 0.5) % 180.0


def corner_hypotheses(segments, segment_hash, angle_tol_deg, join_px, max_len_px):
    """Rectangles implied by two perpendicular segments meeting at a corner.

    The corner is the intersection of the two lines; the far endpoints give
    the two side lengths. The parallelogram is snapped to a rectangle using
    the mean orientation of the pair.

    Args:
        segments (np.ndarray): (N, 4) segments.
        segment_hash (SegmentHash): Hash over ``segments``.
        angle_tol_deg (float): Allowed deviation from 90 degrees.
        join_px (float): Maximum gap between the two nearest endpoints.
        max_len_px (float): Longest segment present (bounds the hash query).

    Returns:
        list[RotRect]
    """
    rects = []
    for i in range(len(segments)):
        seg_i = segments[i]
        dir_i = _segment_direction_deg(seg_i)
        mid_x, mid_y = segment_hash.midpoints[i]
        length_i = math.hypot(seg_i[2] - seg_i[0], seg_i[3] - seg_i[1])
        radius = length_i * 0.5 + max_len_px * 0.5 + join_px
        for j in segment_hash.query(mid_x, mid_y, radius):
            if j <= i:
                continue
            seg_j = segments[j]
            dir_j = _segment_direction_deg(seg_j)
            if abs(_axial_difference_deg(dir_i, dir_j) - 90.0) > angle_tol_deg:
                continue
            ends_i = ((seg_i[0], seg_i[1]), (seg_i[2], seg_i[3]))
            ends_j = ((seg_j[0], seg_j[1]), (seg_j[2], seg_j[3]))
            best = None
            for a in range(2):
                for b in range(2):
                    gap = math.hypot(ends_i[a][0] - ends_j[b][0], ends_i[a][1] - ends_j[b][1])
                    if best is None or gap < best[0]:
                        best = (gap, a, b)
            if best[0] > join_px:
                continue
            _, near_i, near_j = best
            corner = _line_intersection(seg_i, seg_j)
            near_point_i = ends_i[near_i]
            near_point_j = ends_j[near_j]
            if corner is None or math.hypot(corner[0] - near_point_i[0], corner[1] - near_point_i[1]) > 2.0 * join_px:
                corner = ((near_point_i[0] + near_point_j[0]) * 0.5, (near_point_i[1] + near_point_j[1]) * 0.5)
            far_i = ends_i[1 - near_i]
            far_j = ends_j[1 - near_j]

            theta = _mean_axis_deg(dir_i, (dir_j - 90.0) % 180.0)
            ux, uy = math.cos(math.radians(theta)), math.sin(math.radians(theta))
            vx, vy = -uy, ux
            side_u = (far_i[0] - corner[0]) * ux + (far_i[1] - corner[1]) * uy
            side_v = (far_j[0] - corner[0]) * vx + (far_j[1] - corner[1]) * vy
            if abs(side_u) < 1.0 or abs(side_v) < 1.0:
                continue
            cx = corner[0] + (side_u * ux + side_v * vx) * 0.5
            cy = corner[1] + (side_u * uy + side_v * vy) * 0.5
            rects.append(_make_rect(cx, cy, abs(side_u), abs(side_v), theta))
    return rects


def parallel_hypotheses(segments, segment_hash, angle_tol_deg, sep_range_px, max_len_px):
    """Rectangles implied by two parallel segments at a plausible separation.

    The ends are closed at the overlap of the two projections. When the union
    of the projections is noticeably longer (one side fragmented by LSD), a
    second hypothesis closed at the union is emitted too; scoring decides.

    Args:
        segments (np.ndarray): (N, 4) segments.
        segment_hash (SegmentHash): Hash over ``segments``.
        angle_tol_deg (float): Allowed deviation from parallel.
        sep_range_px (tuple): (min, max) perpendicular separation.
        max_len_px (float): Longest segment present (bounds the hash query).

    Returns:
        list[RotRect]
    """
    rects = []
    sep_min, sep_max = sep_range_px
    for i in range(len(segments)):
        seg_i = segments[i]
        dir_i = _segment_direction_deg(seg_i)
        mid_x, mid_y = segment_hash.midpoints[i]
        length_i = math.hypot(seg_i[2] - seg_i[0], seg_i[3] - seg_i[1])
        radius = math.hypot(sep_max, (length_i + max_len_px) * 0.5)
        for j in segment_hash.query(mid_x, mid_y, radius):
            if j <= i:
                continue
            seg_j = segments[j]
            dir_j = _segment_direction_deg(seg_j)
            if _axial_difference_deg(dir_i, dir_j) > angle_tol_deg:
                continue
            theta = _mean_axis_deg(dir_i, dir_j)
            ux, uy = math.cos(math.radians(theta)), math.sin(math.radians(theta))
            vx, vy = -uy, ux
            # Positions of each segment's endpoints along the shared axis (t)
            # and across it (s), relative to segment i's first endpoint.
            ox, oy = seg_i[0], seg_i[1]
            t_i = sorted(((seg_i[0] - ox) * ux + (seg_i[1] - oy) * uy, (seg_i[2] - ox) * ux + (seg_i[3] - oy) * uy))
            t_j = sorted(((seg_j[0] - ox) * ux + (seg_j[1] - oy) * uy, (seg_j[2] - ox) * ux + (seg_j[3] - oy) * uy))
            s_i = ((seg_i[0] + seg_i[2]) * 0.5 - ox) * vx + ((seg_i[1] + seg_i[3]) * 0.5 - oy) * vy
            s_j = ((seg_j[0] + seg_j[2]) * 0.5 - ox) * vx + ((seg_j[1] + seg_j[3]) * 0.5 - oy) * vy
            separation = abs(s_j - s_i)
            if separation < sep_min or separation > sep_max:
                continue
            overlap_lo = max(t_i[0], t_j[0])
            overlap_hi = min(t_i[1], t_j[1])
            overlap = overlap_hi - overlap_lo
            shorter = min(t_i[1] - t_i[0], t_j[1] - t_j[0])
            if shorter <= 0 or overlap < 0.5 * shorter:
                continue
            s_mid = (s_i + s_j) * 0.5
            extents = [(overlap_lo, overlap_hi)]
            union_lo = min(t_i[0], t_j[0])
            union_hi = max(t_i[1], t_j[1])
            if (union_hi - union_lo) > 1.15 * overlap:
                extents.append((union_lo, union_hi))
            for lo, hi in extents:
                t_mid = (lo + hi) * 0.5
                cx = ox + t_mid * ux + s_mid * vx
                cy = oy + t_mid * uy + s_mid * vy
                rects.append(_make_rect(cx, cy, hi - lo, separation, theta))
    return rects


def _point_in_rect(x, y, rect):
    """True when (x, y) lies inside ``rect``."""
    theta = math.radians(rect.angle_deg)
    dx = x - rect.cx
    dy = y - rect.cy
    along = dx * math.cos(theta) + dy * math.sin(theta)
    across = -dx * math.sin(theta) + dy * math.cos(theta)
    return abs(along) <= rect.length * 0.5 and abs(across) <= rect.width * 0.5


def boxiness_hypotheses(boxiness, theta_deg, mag, ang, min_boxiness, nms_radius_px, window_px,
                        decimation, angle_tol_deg, existing=None, max_peaks=200):
    """Rectangles fitted at boxiness peaks that no line hypothesis covers.

    Covers blur and low contrast, where LSD fragments the edges but the two
    perpendicular gradient families are still there. At each peak, strong
    gradient pixels aligned with the dominant orientation (or perpendicular
    to it) are projected onto that orientation and a rectangle is fitted to
    their robust (5th-95th percentile) extent.

    Args:
        boxiness (np.ndarray): B on the decimated grid.
        theta_deg (np.ndarray): Dominant orientation (mod 90) on the decimated grid.
        mag (np.ndarray): Full-resolution gradient magnitude.
        ang (np.ndarray): Full-resolution gradient orientation (radians).
        min_boxiness (float): Peak threshold.
        nms_radius_px (float): Peak suppression radius, full-resolution px.
        window_px (float): Fitting window side, full-resolution px.
        decimation (int): Grid factor of ``boxiness``/``theta_deg``.
        angle_tol_deg (float): Orientation tolerance for contributing pixels.
        existing (list[RotRect], optional): Line hypotheses; peaks inside
            any of them are skipped.
        max_peaks (int): Cap on peaks examined, strongest first.

    Returns:
        list[RotRect]
    """
    existing = existing or []
    radius = max(1, int(round(nms_radius_px / decimation)))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2 * radius + 1, 2 * radius + 1))
    dilated = cv2.dilate(boxiness, kernel)
    peaks = np.argwhere((boxiness >= min_boxiness) & (boxiness >= dilated))
    if len(peaks) == 0:
        return []
    order = np.argsort(-boxiness[peaks[:, 0], peaks[:, 1]])[:max_peaks]

    half = int(round(window_px * 0.5))
    rects = []
    for row, col in peaks[order]:
        cx = (col + 0.5) * decimation
        cy = (row + 0.5) * decimation
        if any(_point_in_rect(cx, cy, r) for r in existing):
            continue
        theta = float(theta_deg[row, col])
        # B is a plateau over a target smaller than the window, so the peak
        # can sit off-centre and the first window clip the target. Each fit
        # moves the centre toward the target's; a couple of re-centred fits
        # settle it.
        fit = None
        for _ in range(_BOXINESS_FIT_ITERATIONS):
            fit = _fit_aligned_extent(mag, ang, cx, cy, half, theta, angle_tol_deg)
            if fit is None:
                break
            moved = math.hypot(fit[0] - cx, fit[1] - cy)
            cx, cy = fit[0], fit[1]
            if moved < 1.0:
                break
        if fit is None:
            continue
        fit_x, fit_y, side_a, side_c = fit
        # Re-centring can walk an off-target peak onto a target a line
        # hypothesis already covers.
        if any(_point_in_rect(fit_x, fit_y, r) for r in existing):
            continue
        # The window that peaked can straddle several shapes; the fitted
        # rectangle must be boxy where it actually sits, not just where the
        # search started.
        fit_row = min(boxiness.shape[0] - 1, max(0, int(fit_y // decimation)))
        fit_col = min(boxiness.shape[1] - 1, max(0, int(fit_x // decimation)))
        if boxiness[fit_row, fit_col] < min_boxiness:
            continue
        rects.append(_make_rect(fit_x, fit_y, side_a, side_c, theta))
    return rects


def _fit_aligned_extent(mag, ang, cx, cy, half, theta, angle_tol_deg):
    """Fit a rectangle at orientation ``theta`` to the strong aligned gradients near (cx, cy).

    Pixels count when their gradient is strong for the window and lies
    within ``angle_tol_deg`` of ``theta`` or ``theta + 90``. The rectangle
    spans their 5th-95th percentile extent along and across ``theta``.

    Returns:
        tuple | None: (centre x, centre y, side along theta, side across), or
        None when too few pixels qualify or the extent is degenerate.
    """
    height, width = mag.shape[:2]
    x0, x1 = max(0, int(cx) - half), min(width, int(cx) + half + 1)
    y0, y1 = max(0, int(cy) - half), min(height, int(cy) + half + 1)
    window_mag = mag[y0:y1, x0:x1]
    if window_mag.size == 0:
        return None
    window_ang = np.degrees(ang[y0:y1, x0:x1]) % 90.0
    aligned_diff = np.abs(((window_ang - theta + 45.0) % 90.0) - 45.0)
    # The 80th percentile on textured ground; a fifth of the peak on smooth
    # ground, where the percentile can be zero.
    strong_floor = max(float(np.quantile(window_mag, 0.8)), 0.2 * float(window_mag.max()))
    mask = (window_mag >= strong_floor) & (aligned_diff <= angle_tol_deg) & (window_mag > 0)
    ys, xs = np.nonzero(mask)
    if len(xs) < 8:
        return None
    ux, uy = math.cos(math.radians(theta)), math.sin(math.radians(theta))
    px = xs + x0 - cx
    py = ys + y0 - cy
    along = px * ux + py * uy
    across = -px * uy + py * ux
    a_lo, a_hi = np.percentile(along, (5, 95))
    c_lo, c_hi = np.percentile(across, (5, 95))
    side_a = a_hi - a_lo
    side_c = c_hi - c_lo
    if side_a < 2.0 or side_c < 2.0:
        return None
    a_mid = (a_lo + a_hi) * 0.5
    c_mid = (c_lo + c_hi) * 0.5
    return cx + a_mid * ux - c_mid * uy, cy + a_mid * uy + c_mid * ux, side_a, side_c


def edge_support(rect, mag, ang, angle_tol_deg, contrast_floor, n_samples=64):
    """Fraction of the perimeter backed by an aligned gradient.

    Samples are spread over the four sides in proportion to their length.
    A sample counts when, within a couple of pixels along the side's normal,
    some pixel has magnitude above ``contrast_floor`` and an orientation
    within ``angle_tol_deg`` of that normal (either polarity).

    Returns:
        float: Support in [0, 1].
    """
    corners = rect_corners(rect)
    perimeter = 2.0 * (rect.length + rect.width)
    if perimeter <= 0:
        return 0.0
    points = []
    normals = []
    for k in range(4):
        start = corners[k]
        end = corners[(k + 1) % 4]
        side = end - start
        side_len = float(np.hypot(side[0], side[1]))
        if side_len <= 0:
            continue
        count = max(2, int(round(n_samples * side_len / perimeter)))
        t = (np.arange(count, dtype=np.float32) + 0.5) / count
        points.append(start[None, :] + t[:, None] * side[None, :])
        normal = np.array([-side[1], side[0]], dtype=np.float32) / side_len
        normals.append(np.repeat(normal[None, :], count, axis=0))
    if not points:
        return 0.0
    points = np.concatenate(points)
    normals = np.concatenate(normals)
    offsets = np.arange(-_EDGE_SEARCH_HALF_WIDTH, _EDGE_SEARCH_HALF_WIDTH + 1, dtype=np.float32)
    xs = points[:, 0:1] + normals[:, 0:1] * offsets[None, :]
    ys = points[:, 1:2] + normals[:, 1:2] * offsets[None, :]
    sample_mag = _sample_nearest(mag, xs, ys)
    sample_ang = np.degrees(_sample_nearest(ang, xs, ys))
    normal_deg = np.degrees(np.arctan2(normals[:, 1], normals[:, 0]))[:, None]
    diff = np.abs(((sample_ang - normal_deg + 90.0) % 180.0) - 90.0)
    hit = (sample_mag >= contrast_floor) & (diff <= angle_tol_deg)
    return float(np.mean(np.any(hit, axis=1)))


def ring_contrast_lab(lab, rect, ring_frac):
    """CIE76 colour difference between a rectangle's interior and a ring around it.

    Medians are used on both sides so a few edge or shadow pixels do not
    swing the result. Works in a local ROI so the cost is independent of
    frame size.

    Args:
        lab (np.ndarray): 8-bit OpenCV LAB image (L scaled to 0-255, a/b offset by 128).
        rect (RotRect): Rectangle to test.
        ring_frac (float): Ring width as a fraction of the short side.

    Returns:
        float: Delta E (CIE76), 0 when either region is empty.
    """
    ring_px = max(2.0, ring_frac * rect.width)
    gap_px = 1.5
    inner = RotRect(rect.cx, rect.cy, rect.length * 0.7, rect.width * 0.7, rect.angle_deg)
    gap = RotRect(rect.cx, rect.cy, rect.length + 2 * gap_px, rect.width + 2 * gap_px, rect.angle_deg)
    outer = RotRect(rect.cx, rect.cy, rect.length + 2 * (gap_px + ring_px), rect.width + 2 * (gap_px + ring_px), rect.angle_deg)
    outer_corners = rect_corners(outer)
    height, width = lab.shape[:2]
    x0 = max(0, int(math.floor(outer_corners[:, 0].min())))
    y0 = max(0, int(math.floor(outer_corners[:, 1].min())))
    x1 = min(width, int(math.ceil(outer_corners[:, 0].max())) + 1)
    y1 = min(height, int(math.ceil(outer_corners[:, 1].max())) + 1)
    if x1 <= x0 or y1 <= y0:
        return 0.0
    roi = lab[y0:y1, x0:x1]
    offset = np.array([x0, y0], dtype=np.float32)
    shape = (y1 - y0, x1 - x0)

    def _poly_mask(r):
        mask = np.zeros(shape, dtype=np.uint8)
        cv2.fillPoly(mask, [np.rint(rect_corners(r) - offset).astype(np.int32)], 255)
        return mask

    inner_mask = _poly_mask(inner)
    ring_mask = cv2.subtract(_poly_mask(outer), _poly_mask(gap))
    inside = roi[inner_mask > 0]
    around = roi[ring_mask > 0]
    if len(inside) == 0 or len(around) == 0:
        return 0.0
    inside_median = np.median(inside.reshape(-1, 3).astype(np.float32), axis=0)
    around_median = np.median(around.reshape(-1, 3).astype(np.float32), axis=0)
    delta = inside_median - around_median
    # OpenCV stores L as L * 255 / 100; a and b are already in CIE units.
    delta[0] *= 100.0 / 255.0
    return float(np.sqrt(np.sum(delta * delta)))


def size_score(length_cm, width_cm, ranges, tolerance):
    """Physical-size score in [0, 1].

    1 inside the range on both sides. Outside, each side decays as a Gaussian
    in log-ratio distance to the nearest bound, with sigma log(1 + tolerance),
    so the fall-off is symmetric for too-large and too-small.

    Args:
        length_cm (float): Long side.
        width_cm (float): Short side.
        ranges (tuple): (long_min, long_max, short_min, short_max) in cm.
        tolerance (float): Fractional slack (0.2 = 20 %).

    Returns:
        float
    """
    long_min, long_max, short_min, short_max = ranges
    sigma = math.log(1.0 + max(tolerance, 1e-3))

    def _side(value, lo, hi):
        if value <= 0:
            return 0.0
        if lo <= value <= hi:
            return 1.0
        bound = lo if value < lo else hi
        distance = math.log(value / bound)
        return math.exp(-0.5 * (distance / sigma) ** 2)

    return _side(length_cm, long_min, long_max) * _side(width_cm, short_min, short_max)


def _rect_area_overlap(rect_a, rect_b):
    """Intersection area of two rotated rectangles."""
    status, points = cv2.rotatedRectangleIntersection(
        ((rect_a.cx, rect_a.cy), (rect_a.length, rect_a.width), rect_a.angle_deg),
        ((rect_b.cx, rect_b.cy), (rect_b.length, rect_b.width), rect_b.angle_deg),
    )
    if status == cv2.INTERSECT_NONE or points is None or len(points) < 3:
        return 0.0
    hull = cv2.convexHull(points)
    return float(cv2.contourArea(hull))


def rotated_nms(rects, scores, iou_thresh):
    """Greedy non-maximum suppression over rotated rectangles.

    Returns:
        list[int]: Indices of kept rectangles, highest score first.
    """
    order = sorted(range(len(rects)), key=lambda k: -scores[k])
    kept = []
    for index in order:
        candidate = rects[index]
        candidate_area = candidate.length * candidate.width
        suppressed = False
        for kept_index in kept:
            other = rects[kept_index]
            reach = (math.hypot(candidate.length, candidate.width) + math.hypot(other.length, other.width)) * 0.5
            if math.hypot(candidate.cx - other.cx, candidate.cy - other.cy) > reach:
                continue
            inter = _rect_area_overlap(candidate, other)
            union = candidate_area + other.length * other.width - inter
            if union > 0 and inter / union >= iou_thresh:
                suppressed = True
                break
        if not suppressed:
            kept.append(index)
    return kept
