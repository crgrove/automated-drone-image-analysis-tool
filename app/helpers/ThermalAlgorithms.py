"""
NumPy ports of ADIAT Temperature* AOI cores (platform-agnostic).

These mirror the mask logic used by:
  - ThermalRangeService
  - ThermalAnomalyService
  - ThermalResidualAnomalyService

On Darwin, algorithms.conf enables the same services; they still call
ThermalParserService for decode. This module exists so unit tests and
tools/thermal_decode.py can exercise AOI logic on synthetic float32 maps
without DJI DIRP DLLs or real R-JPEG fixtures.

Gating for UI availability is ``platform.system()`` via algorithms.conf
platforms lists (Windows + Darwin). Windows continues to use DIRP ctypes.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple

import cv2
import numpy as np

try:
    from scipy.ndimage import median_filter
except ImportError:  # pragma: no cover
    median_filter = None


def temperature_range_mask(
    temperature_c: np.ndarray,
    min_temp: float,
    max_temp: float,
) -> np.ndarray:
    """Binary mask (uint8 0/1) where min_temp < T < max_temp (same as ThermalRangeService)."""
    temps = np.asarray(temperature_c, dtype=np.float32)
    return np.uint8(1 * ((temps > min_temp) & (temps < max_temp)))


def split_image(image: np.ndarray, segments: int) -> List[List[np.ndarray]]:
    """Split a 2D array into a segments x segments grid of tiles."""
    segments = max(1, int(segments))
    h, w = image.shape[:2]
    tile_h = h // segments
    tile_w = w // segments
    rows: List[List[np.ndarray]] = []
    for i in range(segments):
        row = []
        y0 = i * tile_h
        y1 = h if i == segments - 1 else (i + 1) * tile_h
        for j in range(segments):
            x0 = j * tile_w
            x1 = w if j == segments - 1 else (j + 1) * tile_w
            row.append(image[y0:y1, x0:x1])
        rows.append(row)
    return rows


def glue_image(tiles: Sequence[Sequence[np.ndarray]]) -> np.ndarray:
    """Reassemble a grid of tiles into one 2D array."""
    return np.vstack([np.hstack(list(row)) for row in tiles])


def temperature_anomaly_mask(
    temperature_c: np.ndarray,
    threshold: float,
    segments: int = 1,
    direction: str = "Above Mean",
) -> np.ndarray:
    """
    Per-segment mean/std anomaly mask (uint8 0/1), matching ThermalAnomalyService.

    direction: 'Above Mean', 'Below Mean', or 'Above or Below Mean'
    """
    temps = np.asarray(temperature_c, dtype=np.float32)
    pieces = split_image(temps, segments)
    masks = [[None for _ in row] for row in pieces]
    for i, row in enumerate(pieces):
        for j, tile in enumerate(row):
            mean = float(np.mean(tile))
            std = float(np.std(tile))
            max_threshold = mean + (std * threshold)
            min_threshold = mean - (std * threshold)
            if direction == "Above or Below Mean":
                masks[i][j] = np.uint8(1 * ((tile > max_threshold) | (tile < min_threshold)))
            elif direction == "Above Mean":
                masks[i][j] = np.uint8(1 * (tile > max_threshold))
            else:
                masks[i][j] = np.uint8(1 * (tile < min_threshold))
    return glue_image(masks)


def temperature_residual_anomaly_mask(
    temperature_c: np.ndarray,
    delta_t_threshold: float = 4.0,
    background_kernel: int = 51,
    direction: str = "Both",
    score_sigma_multiplier: float = 2.5,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Local background residual anomaly mask (simplified NumPy port of
    ThermalResidualAnomalyService core thresholds).

    Returns:
        (binary_mask uint8 0/1, residual float32)
    """
    temperature_c = np.asarray(temperature_c, dtype=np.float32)
    finite_mask = np.isfinite(temperature_c)
    if not np.any(finite_mask):
        raise ValueError("Radiometric temperature matrix contains no finite values")

    fill_value = float(np.nanmedian(temperature_c[finite_mask]))
    working = np.where(finite_mask, temperature_c, fill_value)

    kernel = int(background_kernel)
    if kernel % 2 == 0:
        kernel += 1
    kernel = max(1, min(kernel, min(working.shape[:2])))
    if kernel % 2 == 0 and kernel > 1:
        kernel -= 1

    if median_filter is not None and kernel > 1:
        background = median_filter(working, size=(kernel, kernel), mode="nearest").astype(np.float32)
    elif kernel > 1:
        background = cv2.GaussianBlur(
            working, (kernel, kernel), sigmaX=0, sigmaY=0, borderType=cv2.BORDER_REPLICATE
        )
    else:
        background = working.copy()

    residual = working - background
    residual[~finite_mask] = 0.0

    residual_values = residual[finite_mask]
    residual_median = float(np.median(residual_values))
    mad = float(np.median(np.abs(residual_values - residual_median)))
    robust_sigma = max(1e-6, 1.4826 * mad)
    score_map = (residual - residual_median) / robust_sigma
    score_map[~finite_mask] = 0.0

    effective_delta = max(float(delta_t_threshold), float(score_sigma_multiplier) * robust_sigma)
    hot = (residual >= effective_delta) & (score_map >= score_sigma_multiplier) & finite_mask
    cold = ((-residual) >= effective_delta) & ((-score_map) >= score_sigma_multiplier) & finite_mask

    direction_norm = (direction or "Both").strip().lower()
    if direction_norm in ("hot", "above mean", "above"):
        candidate = hot
    elif direction_norm in ("cold", "below mean", "below"):
        candidate = cold
    else:
        candidate = hot | cold

    return candidate.astype(np.uint8), residual.astype(np.float32)


def contours_from_mask(mask: np.ndarray):
    """External contours from a uint8 0/1 or 0/255 mask."""
    binary = np.asarray(mask)
    if binary.dtype != np.uint8:
        binary = binary.astype(np.uint8)
    if binary.max() <= 1:
        binary = binary * 255
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return contours
