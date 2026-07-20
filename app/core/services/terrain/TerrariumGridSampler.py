"""
TerrariumGridSampler - grid sampling for the tiled-web Terrarium provider.

Terrarium PNG tiles are Web Mercator, so sampling a grid is pure pixel
arithmetic (no reprojection): assemble the covering tiles into a mosaic, decode
the RGB elevation encoding vectorized, then resample to the requested GridSpec
with bilinear interpolation.

This lives as a module-level function rather than a provider method because the
provider does not own the tile cache — TerrainService drives the tiled path,
exactly as it does for point queries in ``TerrainService.get_elevation``.
"""

import math
from typing import Optional

import numpy as np

from core.services.LoggerService import LoggerService
from .grid import GridSpec, GridSample, WEB_MERCATOR_ORIGIN_SHIFT

TILE_SIZE = 256
# A single frame footprint at zoom 12 spans a handful of tiles; a request needing
# more than this is almost certainly mis-sized and would blow up memory.
MAX_TILES = 64

_logger = LoggerService()


def _global_pixel_bounds(spec: GridSpec, zoom: int):
    """Global Web-Mercator pixel coords (at ``zoom``) of the spec's bounds.

    Returns (px_min, py_min, px_max, py_max) as floats. y increases downward.
    """
    world = TILE_SIZE * (2.0 ** zoom)
    scale = world / (2.0 * WEB_MERCATOR_ORIGIN_SHIFT)
    minx, miny, maxx, maxy = spec.bounds
    px_min = (minx + WEB_MERCATOR_ORIGIN_SHIFT) * scale
    px_max = (maxx + WEB_MERCATOR_ORIGIN_SHIFT) * scale
    py_min = (WEB_MERCATOR_ORIGIN_SHIFT - maxy) * scale  # top edge -> smaller y
    py_max = (WEB_MERCATOR_ORIGIN_SHIFT - miny) * scale
    return px_min, py_min, px_max, py_max


def _decode_tile(img) -> np.ndarray:
    """Vectorized Terrarium decode of a PIL tile -> (H, W) float32 meters."""
    arr = np.asarray(img.convert('RGB'), dtype=np.float32)
    return arr[..., 0] * 256.0 + arr[..., 1] + arr[..., 2] / 256.0 - 32768.0


def sample_grid_tiled(provider, cache, spec: GridSpec, zoom: int,
                      offline_only: bool = False) -> Optional[GridSample]:
    """Sample a Web-Mercator tiled provider onto ``spec``.

    Args:
        provider: the tiled_web ElevationProvider (used for datum info + tile math).
        cache: a TerrainCacheService returning PIL tiles via get_tile/get_tile_if_cached.
        spec: the target EPSG:3857 GridSpec.
        zoom: tile zoom level (usually TerrainService.zoom).
        offline_only: only use already-cached tiles when True.

    Returns:
        GridSample, or None if no tiles are available or the request is too large.
    """
    if cache is None:
        return None

    px_min, py_min, px_max, py_max = _global_pixel_bounds(spec, zoom)
    x0 = int(math.floor(px_min / TILE_SIZE))
    x1 = int(math.floor((px_max - 1e-9) / TILE_SIZE))
    y0 = int(math.floor(py_min / TILE_SIZE))
    y1 = int(math.floor((py_max - 1e-9) / TILE_SIZE))

    n_tiles = (x1 - x0 + 1) * (y1 - y0 + 1)
    if n_tiles <= 0:
        return None
    if n_tiles > MAX_TILES:
        _logger.warning(
            f"TerrariumGridSampler: {n_tiles} tiles for grid exceeds MAX_TILES={MAX_TILES}; refusing."
        )
        return None

    mosaic_h = (y1 - y0 + 1) * TILE_SIZE
    mosaic_w = (x1 - x0 + 1) * TILE_SIZE
    mosaic = np.full((mosaic_h, mosaic_w), np.nan, dtype=np.float32)

    got_any = False
    for ty in range(y0, y1 + 1):
        for tx in range(x0, x1 + 1):
            if offline_only:
                tile = cache.get_tile_if_cached(zoom, tx, ty)
            else:
                tile = cache.get_tile(zoom, tx, ty)
            if tile is None:
                continue
            block = _decode_tile(tile)
            ry = (ty - y0) * TILE_SIZE
            rx = (tx - x0) * TILE_SIZE
            mosaic[ry:ry + TILE_SIZE, rx:rx + TILE_SIZE] = block
            got_any = True

    if not got_any:
        return None

    # Fractional mosaic pixel coordinates of each spec cell center.
    xs, ys = spec.cell_centers()
    world = TILE_SIZE * (2.0 ** zoom)
    scale = world / (2.0 * WEB_MERCATOR_ORIGIN_SHIFT)
    # global pixel of each center, minus mosaic origin
    gx = (xs + WEB_MERCATOR_ORIGIN_SHIFT) * scale - x0 * TILE_SIZE
    gy = (WEB_MERCATOR_ORIGIN_SHIFT - ys) * scale - y0 * TILE_SIZE
    grid_x, grid_y = np.meshgrid(gx, gy)  # (H, W)

    from scipy.ndimage import map_coordinates
    # Match ADIAT's point sampler (TerrariumProvider.decode_elevation_bilinear):
    # the continuous global-pixel coordinate is used directly, so an integer
    # coordinate lands on that pixel's value (no half-pixel center offset). This
    # keeps grid samples consistent with get_elevation() at the same location.
    sampled = map_coordinates(
        mosaic,
        [grid_y, grid_x],
        order=1,
        mode='constant',
        cval=np.nan,
    ).astype(np.float32)

    datum = provider.get_datum_info()
    datum_note = f"{datum.get('type', '')} {datum.get('name', '')}".strip()
    return GridSample(data=sampled, transform=spec.transform, crs=spec.crs,
                      datum_note=datum_note)
