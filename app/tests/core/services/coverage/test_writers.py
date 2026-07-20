"""Tests for the GeoTIFF / GeoJSON / stats writers (tmp_path + rasterio read-back)."""

import json

import numpy as np
import pytest

pytest.importorskip("rasterio")
pytest.importorskip("shapely")

import rasterio
from rasterio.enums import ColorInterp
from shapely.geometry import box

from core.services.coverage.params import PodParams
from core.services.coverage.colormap import pod_to_rgba
from core.services.coverage.contracts import CoverageResult
from core.services.coverage import writers
from core.services.terrain.grid import make_lattice_spec, lonlat_to_mercator


@pytest.fixture
def small_result():
    minx, miny = lonlat_to_mercator(-120.50, 38.70)
    spec = make_lattice_spec((minx, miny, minx + 300.0, miny + 240.0), 3.0)
    H, W = spec.height, spec.width
    pod = np.zeros((H, W), dtype=np.float32)
    look = np.zeros((H, W), dtype=np.uint16)
    # A covered patch with high POD in the middle.
    pod[H // 4: 3 * H // 4, W // 4: 3 * W // 4] = 0.8
    look[H // 4: 3 * H // 4, W // 4: 3 * W // 4] = 3
    params = PodParams()
    result = CoverageResult(
        pod=pod, look_count=look, transform=spec.transform, image_count=5,
        skipped=[("a.jpg", "no_dem"), ("b.jpg", "no_dem")], stats={},
        gap_polygons=[], cancelled=False, params=params)
    result.stats = writers.build_stats(
        pod, look, spec.transform, result.skipped, [], params,
        canopy_source="none", terrain_info={"name": "NAVD88"})
    return spec, result


def test_pod_geotiff_roundtrip(tmp_path, small_result):
    spec, result = small_result
    path = str(tmp_path / "coverage_pod.tif")
    rgba = pod_to_rgba(result.pod, result.look_count, result.params)
    writers.write_pod_geotiff(path, rgba, result.transform, result.params)

    with rasterio.open(path) as ds:
        assert ds.count == 4
        assert ds.dtypes[0] == "uint8"
        assert ds.crs.to_epsg() == 3857
        assert ds.colorinterp[3] == ColorInterp.alpha
        assert tuple(ds.transform)[:6] == pytest.approx(tuple(result.transform)[:6])
        alpha = ds.read(4)
        # Uncovered cells (look 0) are fully transparent.
        assert alpha[0, 0] == 0
        # The covered patch is opaque.
        assert alpha[spec.height // 2, spec.width // 2] > 0
        assert ds.tags().get("ADIAT_PRODUCT") == "coverage_pod"


def test_pod_overlay_png_roundtrip(tmp_path, small_result):
    """The KML GroundOverlay product: a WGS84-reprojected RGBA PNG whose
    returned LatLonBox matches the grid's geographic bounds."""
    from PIL import Image
    from rasterio.warp import transform_bounds
    from rasterio.transform import array_bounds

    spec, result = small_result
    path = str(tmp_path / "pod_overlay.png")
    box = writers.write_pod_overlay_png(result, path)

    img = Image.open(path)
    assert img.mode == "RGBA"
    w, h = img.size
    assert w > 0 and h > 0

    # Box is a sane LatLonBox...
    assert box["north"] > box["south"]
    assert box["east"] > box["west"]
    # ...matching the source grid's WGS84 bounds (reprojection preserves extent).
    src_bounds = array_bounds(spec.height, spec.width, result.transform)
    exp_w, exp_s, exp_e, exp_n = transform_bounds("EPSG:3857", "EPSG:4326", *src_bounds)
    assert box["west"] == pytest.approx(exp_w, abs=1e-4)
    assert box["south"] == pytest.approx(exp_s, abs=1e-4)
    assert box["east"] == pytest.approx(exp_e, abs=1e-4)
    assert box["north"] == pytest.approx(exp_n, abs=1e-4)

    # Never-looked corners stay fully transparent; the covered middle doesn't.
    px = img.load()
    assert px[0, 0][3] == 0
    assert px[w // 2, h // 2][3] > 0


def test_pod_values_geotiff_roundtrip(tmp_path, small_result):
    spec, result = small_result
    path = str(tmp_path / "coverage_pod_values.tif")
    writers.write_pod_values_geotiff(path, result.pod, result.look_count,
                                     result.transform, result.params)
    with rasterio.open(path) as ds:
        assert ds.count == 1
        assert ds.dtypes[0] == "float32"
        assert ds.crs.to_epsg() == 3857
        assert np.isnan(ds.nodata)
        assert tuple(ds.transform)[:6] == pytest.approx(tuple(result.transform)[:6])
        band = ds.read(1)
        looked = result.look_count > 0
        # Actual probabilities are queryable where looked; NaN elsewhere.
        assert band[looked] == pytest.approx(result.pod[looked], abs=1e-6)
        assert np.isnan(band[~looked]).all()
        assert ds.tags()["ADIAT_PRODUCT"] == "coverage_pod_values"


def test_looks_geotiff_roundtrip(tmp_path, small_result):
    spec, result = small_result
    path = str(tmp_path / "coverage_looks.tif")
    writers.write_looks_geotiff(path, result.look_count, result.transform)
    with rasterio.open(path) as ds:
        assert ds.count == 1
        assert ds.dtypes[0] == "uint16"
        assert ds.nodata == 0
        band = ds.read(1)
        assert band.max() == 3


def test_gaps_geojson_is_valid_wgs84(tmp_path, small_result):
    spec, result = small_result
    # A gap polygon in EPSG:3857 near the grid.
    minx, miny, maxx, maxy = spec.bounds
    gap = box(minx + 10, miny + 10, minx + 40, miny + 40)
    path = str(tmp_path / "coverage_gaps.geojson")
    writers.write_gaps_geojson(path, [gap], gap_threshold=0.25)
    with open(path) as fh:
        gj = json.load(fh)
    assert gj["type"] == "FeatureCollection"
    assert len(gj["features"]) == 1
    feat = gj["features"][0]
    assert feat["properties"]["kind"] == "coverage_gap"
    # Coordinates are lon/lat (WGS84), near -120.5 / 38.7.
    lon, lat = feat["geometry"]["coordinates"][0][0]
    assert -121.0 < lon < -120.0
    assert 38.0 < lat < 39.0


def test_build_stats_keys_and_area(small_result):
    spec, result = small_result
    stats = result.stats
    assert set(stats["area_sqm"].keys()) == {
        "looks_ge_1", "pod_ge_0_25", "pod_ge_0_50", "pod_ge_0_75"}
    # Covered area = number of looked cells * ~9 m^2 (3 m cells), within Mercator scale.
    assert stats["area_sqm"]["looks_ge_1"] > 0
    assert stats["skipped_counts"]["no_dem"] == 2
    assert stats["canopy"]["source"] == "none"


def test_compute_gap_polygons_inside_hull(small_result):
    spec, result = small_result
    minx, miny, maxx, maxy = spec.bounds
    hull = box(minx, miny, maxx, maxy)
    polys = writers.compute_gap_polygons(
        result.pod, result.look_count, result.transform, hull, gap_threshold=0.25)
    # The uncovered border (POD 0 < 0.25) inside the hull yields gap polygon(s).
    assert len(polys) >= 1


def test_write_all_outputs(tmp_path, small_result):
    spec, result = small_result
    out = str(tmp_path / "coverage_pod")
    paths = writers.write_all_outputs(result, out)
    assert set(paths.keys()) == {"pod", "pod_values", "looks", "gaps", "stats"}
    for p in paths.values():
        import os
        assert os.path.exists(p)


# --- P3 writer edge cases (compute_gap_polygons / build_stats) ---


def _edge_spec():
    """A standalone lattice spec (3 m cells, 100x80) for edge-case grids."""
    minx, miny = lonlat_to_mercator(-120.50, 38.70)
    return make_lattice_spec((minx, miny, minx + 300.0, miny + 240.0), 3.0)


def test_compute_gap_polygons_hull_none_whole_grid(small_result):
    """hull_3857=None takes the whole-grid path: no clipping, gaps everywhere
    POD < threshold are reported."""
    spec, result = small_result
    # small_result: POD is 0 on the border, 0.8 in the centre patch. With no hull
    # the entire sub-threshold border participates.
    polys = writers.compute_gap_polygons(
        result.pod, result.look_count, result.transform,
        None, gap_threshold=0.25)
    assert len(polys) >= 1
    # The whole-grid gap area is substantial (the full uncovered border), and it
    # never exceeds the total grid area.
    cell_area = abs(result.transform.a * result.transform.e)
    total_grid_area = spec.height * spec.width * cell_area
    gap_area = sum(p.area for p in polys)
    assert 0.0 < gap_area <= total_grid_area


def test_compute_gap_polygons_no_subthreshold_cells_returns_empty():
    """A grid whose POD is everywhere >= threshold has no gaps -> []."""
    spec = _edge_spec()
    pod = np.full((spec.height, spec.width), 0.80, dtype=np.float32)
    look = np.full((spec.height, spec.width), 3, dtype=np.uint16)
    # Whole-grid path (hull=None): nothing is below 0.25.
    assert writers.compute_gap_polygons(
        pod, look, spec.transform, None, gap_threshold=0.25) == []
    # And with a hull covering the grid the result is likewise empty.
    hull = box(*spec.bounds)
    assert writers.compute_gap_polygons(
        pod, look, spec.transform, hull, gap_threshold=0.25) == []


def test_compute_gap_polygons_min_area_cells_filters_small_gaps():
    """min_area_cells drops gaps smaller than the threshold; a lower threshold
    keeps the same gap."""
    spec = _edge_spec()
    pod = np.full((spec.height, spec.width), 0.80, dtype=np.float32)
    look = np.full((spec.height, spec.width), 3, dtype=np.uint16)
    # A tiny 1x2-cell gap (2 cells, area = 2 * cell_area).
    pod[5, 5] = 0.0
    pod[5, 6] = 0.0

    # Default min_area_cells (4) requires >= 4 cells -> the 2-cell gap is dropped.
    dropped = writers.compute_gap_polygons(
        pod, look, spec.transform, None, gap_threshold=0.25)
    assert dropped == []

    # Lowering the threshold to 1 cell keeps it.
    kept = writers.compute_gap_polygons(
        pod, look, spec.transform, None, gap_threshold=0.25, min_area_cells=1)
    assert len(kept) == 1
    cell_area = abs(spec.transform.a * spec.transform.e)
    assert kept[0].area == pytest.approx(2 * cell_area, rel=1e-6)


def test_build_stats_mean_pod_zero_when_nothing_covered():
    """With no covered cells, mean_pod_covered is 0.0 and covered area is 0."""
    spec = _edge_spec()
    # Non-zero POD values, but look_count is all zero -> nothing is 'covered'.
    pod = np.full((spec.height, spec.width), 0.80, dtype=np.float32)
    look = np.zeros((spec.height, spec.width), dtype=np.uint16)
    params = PodParams()
    stats = writers.build_stats(
        pod, look, spec.transform, skipped=[], gap_polygons=[], params=params,
        canopy_source="none", terrain_info={"name": "NAVD88"})
    assert stats["mean_pod_covered"] == 0.0
    assert stats["area_sqm"]["looks_ge_1"] == 0.0
    assert stats["gaps"]["count"] == 0
    assert stats["gaps"]["area_sqm"] == 0.0
