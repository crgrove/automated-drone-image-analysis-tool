"""Tests for TerrariumGridSampler.sample_grid_tiled and its helpers.

TerrariumGridSampler decodes the Web-Mercator elevation mosaic that feeds the
whole Coverage/POD kernel, so this file exercises it end to end with a fake tile
cache that returns synthetic PIL RGB tiles encoding *known* elevations via the
Terrarium formula: ``elevation_m = (R * 256 + G + B / 256) - 32768``.

Covered:
* ``_decode_tile`` recovers hand-computed meters from known RGB pixels.
* ``_global_pixel_bounds`` matches the classic slippy-map global-pixel formula
  (independent derivation) and the floor tiling covers exactly the right tiles.
* A constant mosaic and a closed-form linear ramp both resample to the values
  hand-computed at each cell center (bilinear via scipy map_coordinates).
* ``datum_note`` is passed through from the provider.
* Every None branch: cache is None, all tiles missing (got_any False), and the
  ``n_tiles > MAX_TILES`` guard (which must refuse *before* fetching).
* Partial coverage (some tiles missing) still returns a sample.
"""

import math

import numpy as np
import pytest

pytest.importorskip("affine")
pytest.importorskip("scipy")
from PIL import Image  # noqa: E402

from core.services.terrain.TerrariumGridSampler import (  # noqa: E402
    sample_grid_tiled,
    _decode_tile,
    _global_pixel_bounds,
    TILE_SIZE,
    MAX_TILES,
)
from core.services.terrain.grid import (  # noqa: E402
    spec_for_bounds_wgs84,
    make_lattice_spec,
    GridSample,
    WEB_MERCATOR_ORIGIN_SHIFT,
)
from core.services.terrain.ElevationProvider import TerrariumProvider  # noqa: E402
from core.services.terrain.grid import mercator_to_lonlat  # noqa: E402


ZOOM = 12
# A small western-US footprint that lands in a single tile at zoom 12.
SMALL_BOUNDS = (-120.50, 38.70, -120.495, 38.705)


# --------------------------------------------------------------------------- #
# Terrarium encode/decode helpers
# --------------------------------------------------------------------------- #
def _tile_from_elev(elev) -> Image.Image:
    """Build a 256x256 (or matching-shape) PIL tile that decodes to ``elev``.

    Accepts a scalar (uniform tile) or an (H, W) array of per-pixel elevations.
    Uses the exact inverse of the Terrarium formula so integer elevations round
    trip exactly.
    """
    elev = np.asarray(elev, dtype=np.float64)
    if elev.ndim == 0:
        elev = np.full((TILE_SIZE, TILE_SIZE), float(elev))
    V = elev + 32768.0
    r = np.floor(V / 256.0)
    rem = V - r * 256.0
    g = np.floor(rem)
    b = np.rint((rem - g) * 256.0)
    # Normalize any rounding rollover so channels stay in [0, 255].
    g = g + (b // 256)
    b = b % 256
    r = r + (g // 256)
    g = g % 256
    arr = np.zeros(elev.shape + (3,), dtype=np.uint8)
    arr[..., 0] = r.astype(np.uint8)
    arr[..., 1] = g.astype(np.uint8)
    arr[..., 2] = b.astype(np.uint8)
    return Image.fromarray(arr, mode="RGB")


def _mercator_scale(zoom: int) -> float:
    """3857-units -> global-pixel scale at ``zoom`` (mirrors the sampler)."""
    world = TILE_SIZE * (2.0 ** zoom)
    return world / (2.0 * WEB_MERCATOR_ORIGIN_SHIFT)


def _tile_rect(spec, zoom):
    """(x0, y0, x1, y1) covering tiles, reproducing the sampler's floor tiling."""
    px_min, py_min, px_max, py_max = _global_pixel_bounds(spec, zoom)
    x0 = int(math.floor(px_min / TILE_SIZE))
    x1 = int(math.floor((px_max - 1e-9) / TILE_SIZE))
    y0 = int(math.floor(py_min / TILE_SIZE))
    y1 = int(math.floor((py_max - 1e-9) / TILE_SIZE))
    return x0, y0, x1, y1


# --------------------------------------------------------------------------- #
# Fakes
# --------------------------------------------------------------------------- #
class _FakeProvider:
    """Minimal tiled_web provider stand-in: only datum info is consulted."""

    def __init__(self, datum=None):
        self._datum = datum if datum is not None else {
            "type": "orthometric", "name": "EGM96",
        }

    def get_datum_info(self):
        return self._datum


class _ConstantCache:
    """Returns the same constant-elevation tile for every (z, x, y)."""

    def __init__(self, elev):
        self._tile = _tile_from_elev(elev)

    def get_tile(self, z, x, y):
        return self._tile

    def get_tile_if_cached(self, z, x, y):
        return self._tile


class _RecordingConstantCache(_ConstantCache):
    """Constant cache that records which tiles were requested."""

    def __init__(self, elev):
        super().__init__(elev)
        self.requested = []

    def get_tile(self, z, x, y):
        self.requested.append((z, x, y))
        return self._tile

    def get_tile_if_cached(self, z, x, y):
        self.requested.append((z, x, y))
        return self._tile


class _RampTileCache:
    """Returns tiles whose decoded value equals the *mosaic row index*.

    For tile row ``ty`` and in-tile pixel row ``r`` the elevation is
    ``(ty - y0) * TILE_SIZE + r``. Once assembled the mosaic is therefore a
    perfect vertical ramp ``mosaic[m_row, :] == m_row`` regardless of tiling,
    which makes the resampled result independently predictable in closed form.
    """

    def __init__(self, y0):
        self._y0 = y0

    def _tile(self, ty):
        rows = (ty - self._y0) * TILE_SIZE + np.arange(TILE_SIZE, dtype=np.float64)
        elev = np.repeat(rows[:, None], TILE_SIZE, axis=1)
        return _tile_from_elev(elev)

    def get_tile(self, z, x, y):
        return self._tile(y)

    def get_tile_if_cached(self, z, x, y):
        return self._tile(y)


class _EmptyCache:
    def get_tile(self, z, x, y):
        return None

    def get_tile_if_cached(self, z, x, y):
        return None


class _ExplodingCache:
    """Any fetch is a test failure (used to prove the MAX_TILES guard)."""

    def get_tile(self, z, x, y):
        raise AssertionError("cache should not be queried when tile count guard trips")

    def get_tile_if_cached(self, z, x, y):
        raise AssertionError("cache should not be queried when tile count guard trips")


class _SingleTileCache:
    """Returns a constant tile only for one (x, y); None for all others."""

    def __init__(self, elev, tx, ty):
        self._tile = _tile_from_elev(elev)
        self._tx = tx
        self._ty = ty

    def get_tile(self, z, x, y):
        return self._tile if (x == self._tx and y == self._ty) else None

    def get_tile_if_cached(self, z, x, y):
        return self._tile if (x == self._tx and y == self._ty) else None


# --------------------------------------------------------------------------- #
# _decode_tile
# --------------------------------------------------------------------------- #
def test_decode_tile_recovers_known_meters_per_pixel():
    # Hand-pick four pixels with distinct RGB and hand-compute their meters.
    arr = np.zeros((2, 2, 3), dtype=np.uint8)
    arr[0, 0] = (128, 0, 0)      # 128*256 - 32768 = 0.0
    arr[0, 1] = (128, 100, 64)   # +100 + 64/256 = 100.25
    arr[1, 0] = (0, 0, 0)        # 0 - 32768 = -32768.0
    arr[1, 1] = (129, 244, 64)   # 129*256+244+0.25-32768 = 500.25
    img = Image.fromarray(arr, mode="RGB")

    decoded = _decode_tile(img)
    assert decoded.dtype == np.float32
    assert decoded[0, 0] == pytest.approx(0.0, abs=1e-4)
    assert decoded[0, 1] == pytest.approx(100.25, abs=1e-4)
    assert decoded[1, 0] == pytest.approx(-32768.0, abs=1e-3)
    assert decoded[1, 1] == pytest.approx(500.25, abs=1e-4)


def test_decode_tile_matches_formula_for_full_tile():
    # A synthetic tile encoding a known constant must decode back to it exactly.
    img = _tile_from_elev(1234.5)
    decoded = _decode_tile(img)
    assert decoded.shape == (TILE_SIZE, TILE_SIZE)
    assert np.max(np.abs(decoded - 1234.5)) < 1e-3


def test_tile_from_elev_roundtrips_through_terrarium_formula():
    # Sanity-check the test helper itself against the documented decode formula.
    img = _tile_from_elev(2500.75)
    r, g, b = img.getpixel((10, 10))
    assert (r * 256 + g + b / 256) - 32768.0 == pytest.approx(2500.75, abs=1e-6)


# --------------------------------------------------------------------------- #
# _global_pixel_bounds and floor tiling
# --------------------------------------------------------------------------- #
def test_global_pixel_bounds_matches_slippy_map_formula():
    spec = spec_for_bounds_wgs84(SMALL_BOUNDS, 40.0)
    px_min, py_min, px_max, py_max = _global_pixel_bounds(spec, ZOOM)

    minx, miny, maxx, maxy = spec.bounds
    n = 2.0 ** ZOOM

    def global_pixel(x_3857, y_3857):
        lon, lat = mercator_to_lonlat(x_3857, y_3857)
        gx = (lon + 180.0) / 360.0 * n * TILE_SIZE
        gy = (1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n * TILE_SIZE
        return gx, gy

    # Top-left corner (minx, maxy) is the smaller-y edge; bottom-right is larger.
    tl_x, tl_y = global_pixel(minx, maxy)
    br_x, br_y = global_pixel(maxx, miny)
    assert px_min == pytest.approx(tl_x, rel=1e-9)
    assert py_min == pytest.approx(tl_y, rel=1e-9)
    assert px_max == pytest.approx(br_x, rel=1e-9)
    assert py_max == pytest.approx(br_y, rel=1e-9)


def test_global_pixel_bounds_ordering_and_span():
    spec = spec_for_bounds_wgs84(SMALL_BOUNDS, 40.0)
    px_min, py_min, px_max, py_max = _global_pixel_bounds(spec, ZOOM)
    minx, miny, maxx, maxy = spec.bounds
    scale = _mercator_scale(ZOOM)

    # x increases eastward, y increases downward (maxy -> smaller py).
    assert px_max > px_min
    assert py_max > py_min
    # Pixel span equals ground span times the mercator scale.
    assert (px_max - px_min) == pytest.approx((maxx - minx) * scale, rel=1e-9)
    assert (py_max - py_min) == pytest.approx((maxy - miny) * scale, rel=1e-9)


def test_floor_tiling_covers_exact_tile_rectangle():
    # A footprint wide enough to span more than one tile in each direction.
    spec = spec_for_bounds_wgs84((-120.60, 38.60, -120.40, 38.80), 200.0)
    x0, y0, x1, y1 = _tile_rect(spec, ZOOM)
    n_tiles = (x1 - x0 + 1) * (y1 - y0 + 1)
    assert n_tiles > 1  # the multi-tile mosaic path is genuinely exercised

    cache = _RecordingConstantCache(300.0)
    sample = sample_grid_tiled(_FakeProvider(), cache, spec, ZOOM)
    assert sample is not None

    expected = {(ZOOM, tx, ty)
                for tx in range(x0, x1 + 1)
                for ty in range(y0, y1 + 1)}
    assert set(cache.requested) == expected
    assert len(cache.requested) == n_tiles


def test_floor_tiling_agrees_with_provider_tile_index():
    # The tile covering the grid center must fall inside the covered rectangle,
    # cross-checked against the provider's independent lon/lat tile math.
    spec = spec_for_bounds_wgs84((-120.60, 38.60, -120.40, 38.80), 200.0)
    x0, y0, x1, y1 = _tile_rect(spec, ZOOM)

    minx, miny, maxx, maxy = spec.bounds
    lon, lat = mercator_to_lonlat((minx + maxx) / 2.0, (miny + maxy) / 2.0)
    tx, ty = TerrariumProvider.lat_lon_to_tile(lat, lon, ZOOM)
    assert x0 <= tx <= x1
    assert y0 <= ty <= y1


# --------------------------------------------------------------------------- #
# Mosaic decode + resample
# --------------------------------------------------------------------------- #
def test_constant_mosaic_recovers_constant_at_every_cell():
    spec = spec_for_bounds_wgs84(SMALL_BOUNDS, 40.0)
    sample = sample_grid_tiled(_FakeProvider(), _ConstantCache(1234.0), spec, ZOOM)

    assert sample is not None
    assert sample.data.shape == (spec.height, spec.width)
    assert sample.transform == spec.transform
    assert sample.crs == spec.crs
    # Every finite (non-edge) cell recovers the encoded constant to sub-mm.
    finite = np.isfinite(sample.data)
    assert finite.any()
    assert np.nanmax(np.abs(sample.data[finite] - 1234.0)) < 0.01


def test_constant_fractional_mosaic_recovers_fraction():
    spec = spec_for_bounds_wgs84(SMALL_BOUNDS, 40.0)
    sample = sample_grid_tiled(_FakeProvider(), _ConstantCache(500.25), spec, ZOOM)
    assert sample is not None
    assert np.nanmax(np.abs(sample.data - 500.25)) < 0.02


def test_linear_ramp_matches_closed_form_bilinear():
    """The resampled value at each cell center must equal its global pixel-y.

    With the mosaic set to a perfect vertical ramp (value == mosaic row), the
    bilinear resample at fractional row ``grid_y`` returns ``grid_y`` exactly,
    so the closed form is ``elev = (SHIFT - y_center) * scale - y0 * TILE_SIZE``.
    """
    spec = spec_for_bounds_wgs84(SMALL_BOUNDS, 30.0)
    x0, y0, x1, y1 = _tile_rect(spec, ZOOM)
    scale = _mercator_scale(ZOOM)

    cache = _RampTileCache(y0)
    sample = sample_grid_tiled(_FakeProvider(), cache, spec, ZOOM)
    assert sample is not None
    assert sample.data.shape == (spec.height, spec.width)

    _, ys = spec.cell_centers()
    expected_col = (WEB_MERCATOR_ORIGIN_SHIFT - ys) * scale - y0 * TILE_SIZE  # (H,)
    expected = np.repeat(expected_col[:, None], spec.width, axis=1)

    finite = np.isfinite(sample.data)
    # The overwhelming majority of cells are interior; only a thin edge band can
    # fall on the constant-extrapolation boundary and become NaN.
    assert finite.mean() > 0.5
    np.testing.assert_allclose(sample.data[finite], expected[finite], atol=0.05)


def test_ramp_values_vary_across_rows_but_not_columns():
    # Guards against a transposed/broadcast bug: a vertical ramp must change
    # down the rows and stay constant across each row.
    spec = spec_for_bounds_wgs84(SMALL_BOUNDS, 30.0)
    _, y0, _, _ = _tile_rect(spec, ZOOM)
    sample = sample_grid_tiled(_FakeProvider(), _RampTileCache(y0), spec, ZOOM)
    assert sample is not None
    data = sample.data
    # Use an interior row that is fully finite.
    for row in data:
        if np.all(np.isfinite(row)) and row.size > 1:
            assert np.nanmax(row) - np.nanmin(row) < 0.05  # ~constant across cols
            break
    else:
        pytest.skip("no fully-finite row to compare columns")
    # Consecutive finite rows differ (ramp increases going south).
    col = data[:, 0]
    finite_vals = col[np.isfinite(col)]
    assert finite_vals.size >= 2
    assert np.max(finite_vals) - np.min(finite_vals) > 0.5


# --------------------------------------------------------------------------- #
# datum_note passthrough
# --------------------------------------------------------------------------- #
def test_datum_note_passthrough_default():
    spec = spec_for_bounds_wgs84(SMALL_BOUNDS, 40.0)
    provider = _FakeProvider({"type": "orthometric", "name": "EGM96"})
    sample = sample_grid_tiled(provider, _ConstantCache(10.0), spec, ZOOM)
    assert sample is not None
    assert sample.datum_note == "orthometric EGM96"


def test_datum_note_passthrough_custom_and_partial():
    spec = spec_for_bounds_wgs84(SMALL_BOUNDS, 40.0)
    cache = _ConstantCache(10.0)

    # Only a type key -> trailing/leading whitespace stripped.
    s1 = sample_grid_tiled(_FakeProvider({"type": "ellipsoidal"}), cache, spec, ZOOM)
    assert s1 is not None
    assert s1.datum_note == "ellipsoidal"

    # Empty datum dict -> empty note (no crash).
    s2 = sample_grid_tiled(_FakeProvider({}), cache, spec, ZOOM)
    assert s2 is not None
    assert s2.datum_note == ""

    # Matches the real TerrariumProvider datum info.
    real = sample_grid_tiled(TerrariumProvider(), cache, spec, ZOOM)
    assert real is not None
    assert real.datum_note == "orthometric EGM96"


# --------------------------------------------------------------------------- #
# None branches
# --------------------------------------------------------------------------- #
def test_returns_none_when_cache_is_none():
    spec = spec_for_bounds_wgs84(SMALL_BOUNDS, 40.0)
    assert sample_grid_tiled(_FakeProvider(), None, spec, ZOOM) is None


def test_returns_none_when_all_tiles_missing():
    spec = spec_for_bounds_wgs84(SMALL_BOUNDS, 40.0)
    assert sample_grid_tiled(_FakeProvider(), _EmptyCache(), spec, ZOOM) is None


def test_returns_none_when_all_tiles_missing_offline():
    spec = spec_for_bounds_wgs84(SMALL_BOUNDS, 40.0)
    result = sample_grid_tiled(_FakeProvider(), _EmptyCache(), spec, ZOOM,
                               offline_only=True)
    assert result is None


def test_returns_none_and_does_not_fetch_when_over_max_tiles():
    # A ~2deg x 2deg footprint spans far more than MAX_TILES tiles at zoom 12.
    big = (-121.5, 38.0, -119.5, 40.0)
    spec = spec_for_bounds_wgs84(big, 500.0)
    x0, y0, x1, y1 = _tile_rect(spec, ZOOM)
    assert (x1 - x0 + 1) * (y1 - y0 + 1) > MAX_TILES

    # The guard must return before any tile is fetched.
    result = sample_grid_tiled(_FakeProvider(), _ExplodingCache(), spec, ZOOM)
    assert result is None


def test_partial_coverage_returns_sample_with_gaps():
    # Wide enough to span multiple tiles; only one tile is available.
    spec = spec_for_bounds_wgs84((-120.60, 38.60, -120.40, 38.80), 200.0)
    x0, y0, x1, y1 = _tile_rect(spec, ZOOM)
    assert (x1 - x0 + 1) * (y1 - y0 + 1) > 1

    cache = _SingleTileCache(777.0, x0, y0)
    sample = sample_grid_tiled(_FakeProvider(), cache, spec, ZOOM)

    # got_any is True (one tile decoded) so a sample is returned...
    assert sample is not None
    # ...with real values where the tile exists and NaN gaps where it does not.
    assert np.isfinite(sample.data).any()
    assert np.isnan(sample.data).any()
    finite = sample.data[np.isfinite(sample.data)]
    assert np.max(np.abs(finite - 777.0)) < 0.01


def test_returns_gridsample_instance():
    spec = spec_for_bounds_wgs84(SMALL_BOUNDS, 40.0)
    sample = sample_grid_tiled(_FakeProvider(), _ConstantCache(5.0), spec, ZOOM)
    assert isinstance(sample, GridSample)
    assert sample.data.dtype == np.float32
