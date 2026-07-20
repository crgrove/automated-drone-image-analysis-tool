# Hue / Anomaly Expansion — Design Spec

## User-facing

### MRMap (image algorithm)
Two new optional inputs at the bottom of the MRMap wizard:
- `threshold_expansion` (int, default 0 = off). Accept pixels where `bin_counts < threshold + threshold_expansion`.
- `hue_expansion` (int degrees 0–180, default 0 = off). ± window around mean seed hue.

### HSV Color Range (image algorithm)
One new optional input at the bottom of the HSV wizard:
- `hue_expansion` (int degrees 0–180, default 0 = off).

Backward compat: both default to 0 (off) → identical behavior to today.

## Per-AOI processing pipeline

Runs after initial detection, before pixel area calculation and overlay rendering.

### MRMap — two stages
1. **Threshold expansion** (only if `threshold_expansion > 0`)
   - `expanded_mask = (0 < bin_counts) & (bin_counts < threshold + threshold_expansion)`
   - Phase A (inside cluster rectangle): `selected |= expanded_mask & rect_mask`. No connectivity required.
   - Phase B (outside cluster rectangle): BFS / morphological dilation from phase-A `selected` pixels, constrained to `expanded_mask`, until no new pixels.
2. **Hue expansion** (only if `hue_expansion > 0`)
   - Reference: circular mean hue of the **original** detected pixels (pre-threshold-expansion).
   - Build `hue_ok` mask (global, per-AOI): `circular_hue_dist(H, mean_seed_hue) <= hue_expansion`.
   - `cv2.floodFill` from `selected` into `hue_ok`, bounded by safety cap.

### HSV — single stage
1. **Hue expansion** only (no threshold expansion).
   - Seed pixels: mask pixels inside each AOI.
   - Mean seed hue: circular mean over seed pixels.
   - Expand as above.

### Safety cap
- Per-AOI max expanded-pixel count = `max(10_000, 10 * cluster_rect_area)`.
- If cap hit, stop expansion and log a warning.

### Area calculation
- When any expansion is applied: `area = cv2.contourArea(cv2.convexHull(selected_coords))`.
- When expansion is off: unchanged (current behavior — `len(selected_pixels)` for MRMap; `len(aoi_pixels_list)` for HSV).

## Implementation structure

### New shared module: `app/algorithms/Shared/services/DetectionExpansion.py`
- `circular_mean_hue(hues_uint8) -> float` (OpenCV H ∈ [0,180), wraps at 180).
- `circular_hue_distance_mask(hsv_image, mean_hue, hue_expansion) -> bool mask`.
- `expand_threshold_mrmap(bin_counts_grid, threshold_plus_expansion, cluster_rect, seed_mask) -> bool mask`.
- `expand_hue_flood(selected_mask, hue_ok_mask, cap) -> bool mask`.
- `convex_hull_area(pixel_coords) -> float`.

### MRMapService changes (`app/algorithms/images/MRMap/services/MRMapService.py`)
- Read `threshold_expansion`, `hue_expansion` from options in `__init__`.
- In `process_image`, if either > 0, convert image to HSV once.
- In `_build_aois_from_clusters`, for each cluster:
  - Run threshold expansion (uses existing `bin_counts` grid).
  - Run hue expansion (reference = original cluster pixels).
  - Compute area via convex hull.
  - Update detected-pixel overlay to expanded mask.

### HSVColorRangeService changes
- Read `hue_expansion` from options.
- After base `identify_areas_of_interest`, for each AOI run hue expansion on the AOI's seed pixels.
- Recompute area via convex hull when expanded.

### Wizard changes
- MRMap wizard view + controller: add two QSpinBox fields. Pipe into options dict as `threshold_expansion`, `hue_expansion`.
- HSV wizard view + controller: add one QSpinBox field for `hue_expansion`.

## Performance
- Global `hsv_image` conversion once per image: negligible.
- Per-AOI `hue_ok` mask: O(image_pixels), cheap vectorized numpy.
- Per-AOI flood fill: O(reachable pixels), bounded by safety cap.
- Threshold expansion phase A: vectorized mask AND inside rectangle.
- Threshold expansion phase B: iterative `cv2.dilate` + AND with `expanded_mask`, loop until stable (bounded).
- Expected net impact: +10–25% on typical images when expansion enabled; 0% overhead when disabled.
