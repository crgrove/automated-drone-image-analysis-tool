# DetectionExpansion.py
# Shared helpers for MRMap threshold expansion, hue-based flood expansion,
# and convex-hull area calculation. Used by MRMapService and
# HSVColorRangeService to make anomalous detections more prominent.

import numpy as np
import cv2


# OpenCV represents Hue as [0, 180) (half-degrees). 180 = full circle.
HUE_MAX = 180

# Fixed defaults applied when the user enables the corresponding checkbox in
# the algorithm settings. Values are intentionally not user-editable — these
# constants are the single source of truth for both wizard and advanced UIs.
DEFAULT_THRESHOLD_EXPANSION = 400
DEFAULT_HUE_EXPANSION = 5
DEFAULT_HUE_EXPANSION_SAT_FLOOR_PCT = 35
DEFAULT_HUE_EXPANSION_VAL_FLOOR_PCT = 20


def circular_mean_hue(hues):
    """Compute circular mean of OpenCV hue values.

    Handles wraparound correctly (e.g. mean of [175, 5] is ~0, not 90).

    Args:
        hues: Iterable of hue values in OpenCV units [0, 180).

    Returns:
        Circular mean hue in OpenCV units [0, 180), or None if input empty.
    """
    arr = np.asarray(hues, dtype=np.float64)
    if arr.size == 0:
        return None
    angles = arr * (2.0 * np.pi / HUE_MAX)
    mean_angle = np.arctan2(np.sin(angles).mean(), np.cos(angles).mean())
    if mean_angle < 0:
        mean_angle += 2.0 * np.pi
    return float(mean_angle * (HUE_MAX / (2.0 * np.pi)))


def hue_distance_mask(hsv_image, mean_hue, hue_expansion, sat_floor=0, val_floor=0):
    """Build boolean mask of pixels whose hue is within +/- hue_expansion of mean_hue.

    Circular distance (handles wraparound at 0/180 boundary). Optionally
    rejects pixels whose saturation or value is below a floor — useful for
    preventing hue expansion from sweeping up gray or dark pixels whose hue
    is effectively noise.

    Args:
        hsv_image: HxWx3 uint8 image in OpenCV HSV space.
        mean_hue: Reference hue in OpenCV units [0, 180).
        hue_expansion: Half-window size in OpenCV units [0, 90].
        sat_floor: Minimum saturation in OpenCV units [0, 255]. 0 = no floor.
        val_floor: Minimum value/brightness in OpenCV units [0, 255]. 0 = no floor.

    Returns:
        HxW bool array; True where pixel hue is within range AND sat/val floors
        are met.
    """
    h = hsv_image[:, :, 0].astype(np.int32)
    ref = int(round(mean_hue)) % HUE_MAX
    d = np.abs(h - ref)
    d = np.minimum(d, HUE_MAX - d)
    mask = d <= int(hue_expansion)
    if sat_floor > 0:
        mask &= hsv_image[:, :, 1] >= int(sat_floor)
    if val_floor > 0:
        mask &= hsv_image[:, :, 2] >= int(val_floor)
    return mask


def expand_threshold_mrmap(expanded_bin_mask, cluster_rect, image_shape):
    """Two-phase threshold expansion for MRMap.

    Phase A (in-rectangle): every pixel inside the AOI cluster rectangle
    whose bin_count is below threshold+expansion is selected. Connectivity
    to the original detection is NOT required.

    Phase B (out-of-rectangle): pixels outside the rectangle are added only
    if they meet the expanded threshold AND are connected (8-way) through
    other expanded pixels to a Phase-A pixel. Iterates until stable.

    Args:
        expanded_bin_mask: HxW bool. True where bin_counts > 0 and
            bin_counts < (threshold + threshold_expansion).
        cluster_rect: [xmin, ymin, xmax, ymax] of the AOI cluster.
        image_shape: (H, W[, C]) of the processing-resolution image.

    Returns:
        HxW bool mask of selected pixels after both phases.
    """
    h, w = int(image_shape[0]), int(image_shape[1])
    xmin, ymin, xmax, ymax = cluster_rect
    xmin = max(0, int(xmin))
    ymin = max(0, int(ymin))
    xmax = min(w - 1, int(xmax))
    ymax = min(h - 1, int(ymax))

    # Phase A: everything inside the rectangle that passes the expanded threshold.
    selected = np.zeros((h, w), dtype=bool)
    selected[ymin:ymax + 1, xmin:xmax + 1] = expanded_bin_mask[ymin:ymax + 1, xmin:xmax + 1]

    if not selected.any():
        return selected

    # Phase B: flood outward through connected expanded pixels. Using
    # connectedComponents on expanded_bin_mask and collecting any component
    # that overlaps the Phase-A selection is equivalent to iterative dilation
    # but O(N) instead of O(N*iterations).
    allowed = expanded_bin_mask | selected
    num_labels, labels = cv2.connectedComponents(allowed.astype(np.uint8), connectivity=8)
    seed_labels = np.unique(labels[selected])
    seed_labels = seed_labels[seed_labels != 0]
    if seed_labels.size == 0:
        return selected
    return np.isin(labels, seed_labels)


def expand_hue_flood(selected_mask, hue_ok_mask, safety_cap):
    """Flood-fill expansion from selected pixels through hue-matching neighbors.

    A pixel is added if it matches the hue criterion and is 8-connected to
    an already-selected pixel (directly or through other hue-matching pixels).
    Iterates implicitly via connected components.

    Args:
        selected_mask: HxW bool. Starting seed pixels.
        hue_ok_mask: HxW bool. True where hue matches the AOI reference hue
            within the expansion window.
        safety_cap: Maximum number of expanded pixels. If exceeded, the
            expansion is aborted and the original selected_mask is returned
            along with a capped flag.

    Returns:
        (expanded_mask, cap_hit):
            expanded_mask: HxW bool, the result.
            cap_hit: bool, True if the safety cap was exceeded.
    """
    if not selected_mask.any():
        return selected_mask, False

    allowed = hue_ok_mask | selected_mask
    num_labels, labels = cv2.connectedComponents(allowed.astype(np.uint8), connectivity=8)
    seed_labels = np.unique(labels[selected_mask])
    seed_labels = seed_labels[seed_labels != 0]
    if seed_labels.size == 0:
        return selected_mask, False

    expanded = np.isin(labels, seed_labels)
    pixel_count = int(np.count_nonzero(expanded))
    if safety_cap > 0 and pixel_count > safety_cap:
        return selected_mask, True
    return expanded, False


def convex_hull_area_from_mask(mask):
    """Compute convex-hull area (in pixels) of all True pixels in mask.

    The hull's area includes interior non-selected pixels, which is the
    intended "total footprint" measure for expanded AOIs.

    Args:
        mask: HxW bool or uint8 mask.

    Returns:
        Float area in pixels. Returns pixel count for degenerate cases
        (fewer than 3 points, collinear points).
    """
    if mask.dtype != np.uint8:
        mask_u8 = mask.astype(np.uint8)
    else:
        mask_u8 = mask
    ys, xs = np.where(mask_u8 > 0)
    n = len(xs)
    if n == 0:
        return 0.0
    if n < 3:
        return float(n)
    pts = np.stack([xs, ys], axis=1).reshape(-1, 1, 2).astype(np.int32)
    try:
        hull = cv2.convexHull(pts)
        area = float(cv2.contourArea(hull))
    except cv2.error:
        return float(n)
    # Guard against collinear points producing zero-area hull.
    if area <= 0.0:
        return float(n)
    return area


def compute_safety_cap(cluster_rect, min_floor=10000, multiplier=10):
    """Compute per-AOI expansion safety cap.

    Args:
        cluster_rect: [xmin, ymin, xmax, ymax].
        min_floor: Minimum cap regardless of rect size.
        multiplier: Cap = multiplier * rect_area.

    Returns:
        Integer pixel cap.
    """
    xmin, ymin, xmax, ymax = cluster_rect
    rect_w = max(1, int(xmax) - int(xmin) + 1)
    rect_h = max(1, int(ymax) - int(ymin) + 1)
    rect_area = rect_w * rect_h
    return max(min_floor, multiplier * rect_area)
