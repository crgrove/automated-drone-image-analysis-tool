"""
grid - Web Mercator grid contracts and lattice helpers for terrain sampling.

The Coverage/POD pipeline samples DEM, canopy-height (CHM) and canopy-cover
rasters onto a shared, co-registered grid so the ray-march kernel can index all
three with identical (row, col) arithmetic. To make that possible every grid is:

* EPSG:3857 (Web Mercator), north-up, square cells, and
* snapped to a single global lattice whose cell edges fall on integer multiples
  of the cell size measured from the 3857 origin.

Any two ``GridSpec`` built with the same cell size are therefore integer-offset
co-registered by construction (see :func:`integer_offset`).

Web Mercator inflates horizontal ground distance by ``1 / cos(lat)``. This module
only carries the geometry; callers that need true ground meters multiply
horizontal deltas by ``meters_per_unit = cos(lat_ref)`` (the reciprocal of
:func:`mercator_units_per_meter`).

Only ``affine`` (a pure-Python dependency of rasterio) and numpy are imported at
module load; nothing here needs rasterio/pyproj, so importing this module is
cheap and safe even when the heavy geo stack is unavailable.
"""

import math
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
from affine import Affine

WEB_MERCATOR_R = 6378137.0
WEB_MERCATOR_CRS = "EPSG:3857"
# Half the Web Mercator world extent in meters (pi * R). Grid coordinates live in
# roughly [-ORIGIN_SHIFT, +ORIGIN_SHIFT] on both axes.
WEB_MERCATOR_ORIGIN_SHIFT = math.pi * WEB_MERCATOR_R


def lonlat_to_mercator(lon: float, lat: float) -> Tuple[float, float]:
    """Closed-form EPSG:4326 -> EPSG:3857 (no rasterio/pyproj needed)."""
    x = WEB_MERCATOR_R * math.radians(lon)
    y = WEB_MERCATOR_R * math.asinh(math.tan(math.radians(lat)))
    return x, y


def mercator_to_lonlat(x: float, y: float) -> Tuple[float, float]:
    """Closed-form EPSG:3857 -> EPSG:4326."""
    lon = math.degrees(x / WEB_MERCATOR_R)
    lat = math.degrees(math.atan(math.sinh(y / WEB_MERCATOR_R)))
    return lon, lat


def mercator_units_per_meter(lat: float) -> float:
    """EPSG:3857 units per true ground meter at ``lat`` (== 1 / cos(lat))."""
    return 1.0 / math.cos(math.radians(lat))


@dataclass(frozen=True)
class GridSpec:
    """A fully-determined raster grid: north-up, square cells.

    ``transform`` maps *pixel corners* to CRS coordinates (rasterio convention),
    so cell center ``(i, j)`` sits at
    ``(minx + (j + 0.5) * cell, maxy - (i + 0.5) * cell)``.
    """

    crs: str
    transform: Affine
    width: int
    height: int

    @property
    def cell_size(self) -> float:
        """Cell size in CRS units (``transform.a``; ``-transform.e`` matches)."""
        return self.transform.a

    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        """(minx, miny, maxx, maxy) in the grid CRS."""
        minx = self.transform.c
        maxy = self.transform.f
        maxx = minx + self.transform.a * self.width
        miny = maxy + self.transform.e * self.height
        return (minx, miny, maxx, maxy)

    def cell_centers(self) -> Tuple[np.ndarray, np.ndarray]:
        """(xs[width], ys[height]) center coordinates in the grid CRS."""
        minx, _, _, maxy = self.bounds
        cell = self.transform.a
        xs = minx + (np.arange(self.width, dtype=np.float64) + 0.5) * cell
        ys = maxy - (np.arange(self.height, dtype=np.float64) + 0.5) * cell
        return xs, ys

    def wgs84_bounds(self) -> Tuple[float, float, float, float]:
        """(min_lon, min_lat, max_lon, max_lat); closed-form for EPSG:3857.

        Raises ``ValueError`` for non-3857 grids (the POD pipeline is 3857-only).
        """
        if self.crs != WEB_MERCATOR_CRS:
            raise ValueError(
                f"wgs84_bounds only supports {WEB_MERCATOR_CRS}, got {self.crs}"
            )
        minx, miny, maxx, maxy = self.bounds
        min_lon, min_lat = mercator_to_lonlat(minx, miny)
        max_lon, max_lat = mercator_to_lonlat(maxx, maxy)
        return (min_lon, min_lat, max_lon, max_lat)

    def world_to_index(self, x, y) -> Tuple[np.ndarray, np.ndarray]:
        """Fractional (rows, cols) in *pixel-center* space for map_coordinates.

        ``cols = (x - minx) / cell - 0.5``; ``rows = (maxy - y) / cell - 0.5``.
        Accepts scalars or arrays; returns numpy arrays.
        """
        minx, _, _, maxy = self.bounds
        cell = self.transform.a
        cols = (np.asarray(x, dtype=np.float64) - minx) / cell - 0.5
        rows = (maxy - np.asarray(y, dtype=np.float64)) / cell - 0.5
        return rows, cols


@dataclass
class GridSample:
    """A sampled elevation (or other scalar) grid at a known transform."""

    data: np.ndarray            # (rows, cols) float32, np.nan = nodata
    transform: Affine
    crs: str
    datum_note: str             # e.g. "orthometric NAVD88 (GEOID18)"
    source: Optional[str] = None  # e.g. 'terrarium_fallback' when a fallback served it

    @property
    def spec(self) -> GridSpec:
        rows, cols = self.data.shape[:2]
        return GridSpec(crs=self.crs, transform=self.transform,
                        width=int(cols), height=int(rows))

    def sample_bilinear(self, x: float, y: float) -> Optional[float]:
        """Bilinear sample at a single (x, y) in the grid CRS.

        Returns ``None`` when the point is out of the grid or any of the four
        surrounding cells is nodata (NaN).
        """
        spec = self.spec
        rows, cols = spec.world_to_index(x, y)
        row_f = float(rows)
        col_f = float(cols)
        r0 = int(math.floor(row_f))
        c0 = int(math.floor(col_f))
        if r0 < 0 or c0 < 0 or r0 + 1 >= self.data.shape[0] or c0 + 1 >= self.data.shape[1]:
            return None
        fr = row_f - r0
        fc = col_f - c0
        d = self.data
        v00 = float(d[r0, c0])
        v01 = float(d[r0, c0 + 1])
        v10 = float(d[r0 + 1, c0])
        v11 = float(d[r0 + 1, c0 + 1])
        if any(math.isnan(v) for v in (v00, v01, v10, v11)):
            return None
        top = v00 * (1 - fc) + v01 * fc
        bot = v10 * (1 - fc) + v11 * fc
        return top * (1 - fr) + bot * fr


def make_lattice_spec(bounds_3857: Tuple[float, float, float, float],
                      cell_size: float, crs: str = WEB_MERCATOR_CRS) -> GridSpec:
    """Snap ``bounds_3857`` OUTWARD to the global lattice and return a GridSpec.

    Lattice edges fall on integer multiples of ``cell_size`` from the CRS origin,
    so two specs built with the same ``cell_size`` are integer-offset
    co-registered. Always yields a grid at least 1x1.
    """
    if cell_size <= 0:
        raise ValueError(f"cell_size must be positive, got {cell_size}")
    minx, miny, maxx, maxy = bounds_3857
    if maxx < minx or maxy < miny:
        raise ValueError(f"degenerate bounds: {bounds_3857}")

    left = math.floor(minx / cell_size) * cell_size
    right = math.ceil(maxx / cell_size) * cell_size
    bottom = math.floor(miny / cell_size) * cell_size
    top = math.ceil(maxy / cell_size) * cell_size

    width = max(1, int(round((right - left) / cell_size)))
    height = max(1, int(round((top - bottom) / cell_size)))
    transform = Affine(cell_size, 0.0, left, 0.0, -cell_size, top)
    return GridSpec(crs=crs, transform=transform, width=width, height=height)


def spec_for_bounds_wgs84(bounds_wgs84: Tuple[float, float, float, float],
                          resolution_m: float) -> GridSpec:
    """Build a lattice-snapped EPSG:3857 GridSpec covering a WGS84 bbox.

    ``resolution_m`` is the desired *true ground* cell size; it is converted to
    3857 units at the bbox mid-latitude (``cell = resolution_m / cos(mid_lat)``)
    so cells are ~``resolution_m`` on the ground. Backs the spec's
    ``sample_grid(bounds, resolution_m)`` convenience signature.
    """
    min_lon, min_lat, max_lon, max_lat = bounds_wgs84
    mid_lat = (min_lat + max_lat) / 2.0
    cell_size = resolution_m * mercator_units_per_meter(mid_lat)
    minx, miny = lonlat_to_mercator(min_lon, min_lat)
    maxx, maxy = lonlat_to_mercator(max_lon, max_lat)
    return make_lattice_spec((minx, miny, maxx, maxy), cell_size)


def read_window(ds, spec: GridSpec, nodata=None, pad_px: int = 4):
    """Read only the ``spec`` footprint from an open rasterio dataset (band 1).

    Returns (array, window_transform), or (None, None) if the footprint does not
    intersect the tile. Reading a bounded window keeps huge (Cloud-Optimized)
    tiles from ever loading in full -- e.g. the ~65536x65536 (16 GB) Meta/WRI
    canopy COGs, or large USGS 3DEP tiles.

    When the source window is much denser than the target grid (a native ~1 m
    canopy read against a coarse overlay spec), the read is decimated via
    ``out_shape`` so rasterio pulls COG overviews instead of tens of millions
    of native pixels; the returned transform is scaled to match. Decimation
    uses NEAREST resampling on purpose: the raw band may hold categorical
    LANDFIRE class codes that are decoded to physical units only after this
    read -- averaging codes would be meaningless (and would smear the
    boundless fill value into the data).
    """
    from rasterio.windows import from_bounds, Window
    from rasterio.warp import transform_bounds

    left, bottom, right, top = spec.bounds
    src_bounds = transform_bounds(spec.crs, ds.crs, left, bottom, right, top)
    try:
        win = from_bounds(*src_bounds, transform=ds.transform)
    except Exception:
        return None, None
    win = win.round_offsets().round_lengths()
    win = Window(win.col_off - pad_px, win.row_off - pad_px,
                 win.width + 2 * pad_px, win.height + 2 * pad_px)
    if (win.col_off + win.width <= 0 or win.row_off + win.height <= 0
            or win.col_off >= ds.width or win.row_off >= ds.height
            or win.width <= 0 or win.height <= 0):
        return None, None
    fill = float(nodata) if nodata is not None else -9999.0

    # Decimate when the source window is >=2x denser than the target grid.
    decim = 1
    if spec.width > 0 and spec.height > 0:
        decim = int(min(win.width / spec.width, win.height / spec.height))
        decim = max(1, decim)
    if decim > 1:
        from rasterio.enums import Resampling
        from affine import Affine
        out_h = max(1, math.ceil(win.height / decim))
        out_w = max(1, math.ceil(win.width / decim))
        raw = ds.read(1, window=win, out_shape=(out_h, out_w), boundless=True,
                      fill_value=fill, resampling=Resampling.nearest)
        if raw.size == 0:
            return None, None
        # Scale the window transform so the decimated array stays registered.
        transform = ds.window_transform(win) * Affine.scale(
            win.width / out_w, win.height / out_h)
        return raw, transform

    raw = ds.read(1, window=win, boundless=True, fill_value=fill)
    if raw.size == 0:
        return None, None
    return raw, ds.window_transform(win)


def integer_offset(child: GridSpec, parent: GridSpec,
                   tol: float = 1e-6) -> Tuple[int, int]:
    """(row_off, col_off) of ``child``'s top-left cell within ``parent``.

    Raises ``ValueError`` if the cell sizes differ or the offset is not an
    integer number of cells within ``tol`` (a fraction of a cell).
    """
    cell = parent.transform.a
    if abs(child.transform.a - cell) > tol * cell:
        raise ValueError(
            f"cell size mismatch: child={child.transform.a} parent={cell}"
        )
    col_off = (child.transform.c - parent.transform.c) / cell
    # transform.f is the top (maxy); rows increase downward, so use parent - child.
    row_off = (parent.transform.f - child.transform.f) / cell
    col_r = round(col_off)
    row_r = round(row_off)
    if abs(col_off - col_r) > tol or abs(row_off - row_r) > tol:
        raise ValueError(
            f"non-integer lattice offset: row={row_off}, col={col_off}"
        )
    return int(row_r), int(col_r)


# Fraction of a query bbox that must be covered by tile bboxes to count as
# 'full' coverage (tolerates hairline gaps from manifest rounding).
COVERS_FULL_RATIO = 0.99

COVERS_FULL = 'full'
COVERS_PARTIAL = 'partial'
COVERS_NONE = 'none'


def bbox_coverage(tile_bboxes, bounds_wgs84,
                  full_ratio: float = COVERS_FULL_RATIO) -> str:
    """How much of a WGS84 bbox a set of tile bboxes covers.

    Args:
        tile_bboxes: iterable of (minX, minY, maxX, maxY) WGS84 tuples.
        bounds_wgs84: (min_lon, min_lat, max_lon, max_lat) query box.
        full_ratio: covered-area fraction at or above which coverage is 'full'.

    Returns:
        'full' | 'partial' | 'none'. A degenerate (zero-area) query box counts
        as 'full' when any tile intersects it.
    """
    from shapely.geometry import box as shp_box
    from shapely.ops import unary_union

    query = shp_box(*bounds_wgs84)
    boxes = [shp_box(*b) for b in tile_bboxes]
    intersecting = [b for b in boxes if b.intersects(query)]
    if not intersecting:
        return COVERS_NONE
    if query.area <= 0:
        return COVERS_FULL
    covered = unary_union(intersecting).intersection(query)
    ratio = covered.area / query.area
    if ratio >= full_ratio:
        return COVERS_FULL
    return COVERS_PARTIAL if ratio > 0 else COVERS_NONE
