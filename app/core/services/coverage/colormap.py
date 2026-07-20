"""
colormap - shared RGBA lookup tables for the POD / look-count products.

One hand-rolled viridis LUT feeds both the GeoTIFF writer and the in-viewer
overlay, so the two products are pixel-identical. Viridis is perceptually
uniform and colorblind-safe, and its bright high end reads well over dark
satellite basemaps; the dark low end is neutralized by the alpha ramp. No
matplotlib dependency (viridis control points are inlined).
"""

import numpy as np

# Standard viridis control points (t, r, g, b).
_VIRIDIS_ANCHORS = [
    (0.00, 68, 1, 84),
    (0.25, 59, 82, 139),
    (0.50, 33, 145, 140),
    (0.75, 94, 201, 98),
    (1.00, 253, 231, 37),
]

# Sequential light->dark green ramp for the canopy-height overlay
# (t = height / max_height_m).
_CANOPY_ANCHORS = [
    (0.00, 247, 252, 185),  # grass / very low vegetation: pale yellow-green
    (0.35, 120, 198, 121),  # shrub / young trees
    (0.70, 35, 132, 67),    # mature canopy
    (1.00, 0, 60, 30),      # tall timber
]

# Discrete look-count -> RGBA steps (>=5 saturates to the last).
_LOOKS_STEPS = [
    (255, 245, 157, 140),  # 1 look
    (174, 213, 129, 160),  # 2
    (77, 182, 172, 175),   # 3
    (66, 165, 245, 190),   # 4
    (94, 53, 177, 205),    # 5+
]


def _build_pod_lut(display_floor: float) -> np.ndarray:
    """(256, 4) uint8 RGBA. Index = round(pod * 255). Alpha 0 below the floor,
    then a 90->200 ramp above it."""
    lut = np.zeros((256, 4), dtype=np.uint8)
    t = np.linspace(0.0, 1.0, 256)
    xs = [a[0] for a in _VIRIDIS_ANCHORS]
    for ch in range(3):
        ys = [a[1 + ch] for a in _VIRIDIS_ANCHORS]
        lut[:, ch] = np.clip(np.interp(t, xs, ys), 0, 255).astype(np.uint8)
    floor_i = int(round(max(0.0, min(1.0, display_floor)) * 255))
    alpha = np.zeros(256, dtype=np.float64)
    if floor_i < 255:
        alpha[floor_i:] = np.linspace(90, 200, 256 - floor_i)
    lut[:, 3] = alpha.astype(np.uint8)
    return lut


def pod_to_rgba(pod: np.ndarray, look_count: np.ndarray, params) -> np.ndarray:
    """float32 POD grid -> (H, W, 4) uint8 RGBA; fully transparent where
    look_count == 0."""
    lut = _build_pod_lut(params.pod_display_floor)
    idx = np.clip(np.round(np.nan_to_num(pod, nan=0.0) * 255.0), 0, 255).astype(np.uint8)
    rgba = lut[idx]
    rgba[look_count == 0] = 0
    return rgba


def chm_to_rgba(chm: np.ndarray, max_height_m: float = 35.0,
                min_height_m: float = 0.5) -> np.ndarray:
    """float canopy-height grid (meters) -> (H, W, 4) uint8 RGBA.

    Transparent where the height is NaN or below ``min_height_m`` (open ground,
    roads), then a light->dark green ramp saturating at ``max_height_m`` with
    alpha rising alongside height so tall canopy reads strongest.
    """
    h = np.nan_to_num(np.asarray(chm, dtype=np.float32), nan=0.0)
    t = np.clip(h / max(max_height_m, 1e-6), 0.0, 1.0)
    rgba = np.zeros(t.shape + (4,), dtype=np.uint8)
    xs = [a[0] for a in _CANOPY_ANCHORS]
    for ch in range(3):
        ys = [a[1 + ch] for a in _CANOPY_ANCHORS]
        rgba[..., ch] = np.clip(np.interp(t, xs, ys), 0, 255).astype(np.uint8)
    rgba[..., 3] = (110.0 + 90.0 * t).astype(np.uint8)
    rgba[h < min_height_m] = 0
    return rgba


def look_count_to_rgba(look_count: np.ndarray) -> np.ndarray:
    """uint16 look-count grid -> (H, W, 4) uint8 RGBA (discrete, transparent at 0)."""
    H, W = look_count.shape
    rgba = np.zeros((H, W, 4), dtype=np.uint8)
    lc = np.clip(look_count.astype(np.int32), 0, len(_LOOKS_STEPS))
    for n, color in enumerate(_LOOKS_STEPS, start=1):
        sel = (lc == n) if n < len(_LOOKS_STEPS) else (lc >= n)
        rgba[sel] = color
    return rgba
