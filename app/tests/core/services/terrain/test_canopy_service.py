"""Tests for CanopyService: EVH/EVC LUTs, sample_grid_spec, cover derivation."""

import csv

import numpy as np
import pytest

pytest.importorskip("shapely")
rasterio = pytest.importorskip("rasterio")

from rasterio.transform import from_bounds

from core.services.terrain.CanopyService import (
    CanopyService,
    evh_code_to_meters,
    evc_code_to_fraction,
    KIND_META,
    PRODUCT_CC_PCT,
)
from core.services.terrain.grid import (
    lonlat_to_mercator,
    mercator_to_lonlat,
    spec_for_bounds_wgs84,
)

# A small 3857 region near the Sierra foothills.
_MINX, _MINY = lonlat_to_mercator(-120.50, 38.70)
_MAXX, _MAXY = lonlat_to_mercator(-120.48, 38.72)


def _write_tile(path, value, dtype, nodata=None):
    cols = rows = 24
    transform = from_bounds(_MINX, _MINY, _MAXX, _MAXY, cols, rows)
    data = np.full((rows, cols), value, dtype=dtype)
    with rasterio.open(path, "w", driver="GTiff", height=rows, width=cols, count=1,
                       dtype=dtype, crs="EPSG:3857", transform=transform,
                       nodata=nodata) as dst:
        dst.write(data, 1)


def _wgs84_bbox():
    lo, la = mercator_to_lonlat(_MINX, _MINY)
    hi, ha = mercator_to_lonlat(_MAXX, _MAXY)
    return lo, la, hi, ha


def _manifest(tmp_path, entries, has_product=True):
    path = tmp_path / "canopy_manifest.csv"
    lo, la, hi, ha = _wgs84_bbox()
    fields = ['filename'] + (['product'] if has_product else []) + ['minX', 'minY', 'maxX', 'maxY']
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for e in entries:
            row = {'filename': e['filename'], 'minX': lo, 'minY': la, 'maxX': hi, 'maxY': ha}
            if has_product:
                row['product'] = e['product']
            w.writerow(row)
    return str(path)


def _spec():
    return spec_for_bounds_wgs84(_wgs84_bbox(), 10.0)


# --- LUTs ---

def test_evh_lut():
    codes = np.array([101, 150, 199, 205, 230, 305, 11, 99, -9999])
    m = evh_code_to_meters(codes)
    assert m[0] == pytest.approx(1.0)
    assert m[1] == pytest.approx(50.0)
    assert m[2] == pytest.approx(99.0)
    assert m[3] == pytest.approx(0.5)
    assert m[4] == pytest.approx(3.0)
    assert m[5] == pytest.approx(0.5)
    assert m[6] == 0.0        # water -> 0
    assert np.isnan(m[7])     # 99 fill
    assert np.isnan(m[8])     # -9999 nodata


def test_evc_lut():
    codes = np.array([110, 155, 199, 250, 355, 100, 99, -9999])
    f = evc_code_to_fraction(codes)
    assert f[0] == pytest.approx(0.10)
    assert f[1] == pytest.approx(0.55)
    assert f[2] == pytest.approx(0.99)
    assert f[3] == pytest.approx(0.50)
    assert f[4] == pytest.approx(0.55)
    assert f[5] == 0.0        # sparse -> 0
    assert np.isnan(f[6])
    assert np.isnan(f[7])


# --- sample_grid_spec ---

def test_landfire_evh_evc_coregistered(tmp_path):
    _write_tile(tmp_path / "evh.tif", 150, "int16")   # 50 m tree
    _write_tile(tmp_path / "evc.tif", 155, "int16")   # 0.55 cover
    manifest = _manifest(tmp_path, [
        {'filename': 'evh.tif', 'product': 'landfire_evh'},
        {'filename': 'evc.tif', 'product': 'landfire_evc'},
    ])
    svc = CanopyService(manifest, str(tmp_path), kind='landfire')
    spec = _spec()
    sample = svc.sample_grid_spec(spec)
    assert sample is not None
    assert sample.chm.shape == (spec.height, spec.width)
    assert sample.cover.shape == (spec.height, spec.width)
    # Interior cells decode to the tile constants.
    ch, cw = spec.height // 2, spec.width // 2
    assert sample.chm[ch, cw] == pytest.approx(50.0, abs=0.5)
    assert sample.cover[ch, cw] == pytest.approx(0.55, abs=0.02)
    assert sample.cover_derived is False
    svc.close()


def test_meta_chm_derives_cover(tmp_path):
    _write_tile(tmp_path / "chm.tif", 30.0, "float32", nodata=-9999.0)
    manifest = _manifest(tmp_path, [{'filename': 'chm.tif', 'product': 'meta_chm'}])
    svc = CanopyService(manifest, str(tmp_path), kind=KIND_META)
    spec = _spec()
    sample = svc.sample_grid_spec(spec)
    assert sample is not None
    ch, cw = spec.height // 2, spec.width // 2
    assert sample.chm[ch, cw] == pytest.approx(30.0, abs=0.5)
    # cover = clip(30/20,0,1)*0.9 = 0.9
    assert sample.cover[ch, cw] == pytest.approx(0.9, abs=0.02)
    assert sample.cover_derived is True
    svc.close()


def test_empty_aoi_returns_none(tmp_path):
    _write_tile(tmp_path / "chm.tif", 30.0, "float32")
    manifest = _manifest(tmp_path, [{'filename': 'chm.tif', 'product': 'meta_chm'}])
    svc = CanopyService(manifest, str(tmp_path), kind=KIND_META)
    far = spec_for_bounds_wgs84((-100.0, 20.0, -99.99, 20.01), 10.0)
    assert svc.sample_grid_spec(far) is None
    svc.close()


def test_missing_manifest_does_not_raise(tmp_path):
    svc = CanopyService(str(tmp_path / "nope.csv"), str(tmp_path), kind=KIND_META)
    assert svc.sample_grid_spec(_spec()) is None


def test_landfire_without_product_column_refuses(tmp_path):
    _write_tile(tmp_path / "evh.tif", 150, "int16")
    manifest = _manifest(tmp_path, [{'filename': 'evh.tif'}], has_product=False)
    svc = CanopyService(manifest, str(tmp_path), kind='landfire')
    # EVH/EVC indistinguishable without 'product' -> manifest refused -> no tiles.
    assert svc.sample_grid_spec(_spec()) is None


# --- landfire_cc_pct decode branch ---

def _write_tile_data(path, data, dtype, nodata=None):
    """Write a full 2-D ``data`` array (not a constant) over the shared bbox."""
    rows, cols = data.shape
    transform = from_bounds(_MINX, _MINY, _MAXX, _MAXY, cols, rows)
    with rasterio.open(path, "w", driver="GTiff", height=rows, width=cols, count=1,
                       dtype=dtype, crs="EPSG:3857", transform=transform,
                       nodata=nodata) as dst:
        dst.write(data.astype(dtype), 1)


def test_cc_pct_decode_values():
    """P2/P3 landfire_cc_pct decode: percent->fraction, clip>100, negatives->NaN."""
    raw = np.array([-1, 0, 55, 150], dtype=np.int16)
    out = CanopyService._decode(PRODUCT_CC_PCT, raw, None)
    assert np.isnan(out[0])                       # -1 -> NaN (nodata sentinel)
    assert out[1] == pytest.approx(0.0)           # 0% -> 0.0
    assert out[2] == pytest.approx(0.55)          # 55% -> 0.55
    assert out[3] == pytest.approx(1.0)           # 150 clipped to 100% -> 1.0
    assert out.dtype == np.float32


def test_cc_pct_sample_grid_spec_cover(tmp_path):
    """landfire_cc_pct routed through sample_grid_spec decodes cover, no derive."""
    _write_tile(tmp_path / "cc.tif", 55, "int16")   # 55% -> 0.55 cover
    manifest = _manifest(tmp_path, [{'filename': 'cc.tif', 'product': 'landfire_cc_pct'}])
    svc = CanopyService(manifest, str(tmp_path), kind='landfire')
    spec = _spec()
    sample = svc.sample_grid_spec(spec)
    assert sample is not None
    ch, cw = spec.height // 2, spec.width // 2
    assert sample.cover[ch, cw] == pytest.approx(0.55, abs=0.02)
    # cc_pct is a cover-only product: no height tile -> chm defaults to 0 and cover
    # is genuine (not synthesized) so cover_derived stays False.
    assert sample.cover_derived is False
    assert sample.chm[ch, cw] == pytest.approx(0.0, abs=0.01)
    svc.close()


# --- cover derivation into NaN holes (need = isnan(cover) & chm>0) ---

def test_cover_derived_fills_evc_nodata_holes(tmp_path):
    """EVC cover with a central nodata hole is filled from CHM only in the hole,
    while decoded EVC cover is preserved everywhere it is present."""
    # Constant EVH tile -> 50 m canopy everywhere (chm > 0 across the grid).
    _write_tile(tmp_path / "evh.tif", 150, "int16")
    # EVC tile: outer region code 155 (-> 0.55), central block code 99 (fill -> NaN).
    evc = np.full((24, 24), 155, dtype=np.int16)
    evc[8:16, 8:16] = 99
    _write_tile_data(tmp_path / "evc.tif", evc, "int16")
    manifest = _manifest(tmp_path, [
        {'filename': 'evh.tif', 'product': 'landfire_evh'},
        {'filename': 'evc.tif', 'product': 'landfire_evc'},
    ])
    svc = CanopyService(manifest, str(tmp_path), kind='landfire')
    spec = _spec()
    sample = svc.sample_grid_spec(spec)
    assert sample is not None

    ch, cw = spec.height // 2, spec.width // 2       # deep inside the nodata hole
    outer_r, outer_c = spec.height // 8, spec.width // 8  # deep inside the 0.55 region

    # chm is present (50 m) everywhere including the hole.
    assert sample.chm[ch, cw] == pytest.approx(50.0, abs=0.5)
    # Hole: cover was NaN but chm>0 -> filled = clip(50/20,0,1)*0.9 = 0.9 (not 0.0).
    assert sample.cover[ch, cw] == pytest.approx(0.9, abs=0.02)
    # Elsewhere: decoded EVC cover (0.55) is preserved, not overwritten.
    assert sample.cover[outer_r, outer_c] == pytest.approx(0.55, abs=0.03)
    # Any derivation flips the flag.
    assert sample.cover_derived is True
    svc.close()


def test_covers_classifies_aoi_against_manifest(tmp_path):
    """covers() mirrors the 3DEP provider: full inside the tile bbox, partial
    when extending past it, none when disjoint."""
    _write_tile(tmp_path / "chm.tif", 30.0, "float32")
    manifest = _manifest(tmp_path, [{'filename': 'chm.tif', 'product': 'meta_chm'}])
    svc = CanopyService(manifest, str(tmp_path), kind=KIND_META)

    lo, la, hi, ha = _wgs84_bbox()
    span_lon = hi - lo
    span_lat = ha - la
    inside = (lo + 0.1 * span_lon, la + 0.1 * span_lat,
              hi - 0.1 * span_lon, ha - 0.1 * span_lat)
    overflowing = (lo, la, hi + 5 * span_lon, ha)
    disjoint = (hi + 1.0, ha + 1.0, hi + 1.1, ha + 1.1)

    assert svc.covers(inside) == 'full'
    assert svc.covers(overflowing) == 'partial'
    assert svc.covers(disjoint) == 'none'
    svc.close()


def test_sample_grid_spec_reports_covered_mask(tmp_path):
    """The sample exposes which cells the tiles actually provided data for,
    captured before uncovered cells are filled with 0 height (so POD can tell
    'no canopy tile here' from genuine bare ground)."""
    _write_tile(tmp_path / "chm.tif", 30.0, "float32", nodata=-9999.0)
    manifest = _manifest(tmp_path, [{'filename': 'chm.tif', 'product': 'meta_chm'}])
    svc = CanopyService(manifest, str(tmp_path), kind=KIND_META)
    sample = svc.sample_grid_spec(_spec())
    assert sample is not None
    assert sample.covered is not None
    assert sample.covered.shape == (sample.chm.shape[0], sample.chm.shape[1])
    assert sample.covered.dtype == bool
    # The tile spans the whole spec, so coverage is near-total (bilinear
    # reprojection leaves only the outermost edge cells unfilled).
    assert sample.covered.mean() > 0.9
    ch, cw = sample.covered.shape[0] // 2, sample.covered.shape[1] // 2
    assert sample.covered[ch, cw]
    svc.close()


def test_sample_grid_spec_covered_false_outside_tiles(tmp_path):
    """A spec only partially overlapping the tile has covered=False where no
    data exists (the signal POD uses to avoid overstating there)."""
    _write_tile(tmp_path / "chm.tif", 30.0, "float32")
    manifest = _manifest(tmp_path, [{'filename': 'chm.tif', 'product': 'meta_chm'}])
    svc = CanopyService(manifest, str(tmp_path), kind=KIND_META)
    # Shift the query east so only its western part overlaps the tile.
    lo, la, hi, ha = _wgs84_bbox()
    span = hi - lo
    shifted = spec_for_bounds_wgs84((lo + span * 0.5, la, hi + span * 0.5, ha), 10.0)
    sample = svc.sample_grid_spec(shifted)
    assert sample is not None
    # Some cells covered (west), some not (east beyond the tile).
    assert sample.covered.any()
    assert not sample.covered.all()
    svc.close()
