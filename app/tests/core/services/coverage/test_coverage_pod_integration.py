"""End-to-end integration tests for the Coverage/POD pipeline.

Unlike ``test_coverage_pod_service.py`` (which monkeypatches the ``_frame_geometry``
seam and injects synthetic FrameGeometry literals), these tests exercise the REAL
image -> EXIF/XMP metadata -> FrameGeometry -> terrain/canopy sampling -> kernel
ray-march -> accumulate -> write chain against real drone imagery
(``DJI_0082..0084.JPG`` carry real GPS + gimbal pose + relative-altitude XMP).

Terrain is a small synthetic flat DEM co-registered to each requested frame spec
(the ``_FlatTerrain`` pattern from the sibling orchestration test), so the kernel
runs on real geometry while staying fully deterministic and offline. The products
are written with ``writers.write_all_outputs`` into ``tmp_path`` and read back with
rasterio / json to assert internal consistency.
"""

import json
import os
import types

import numpy as np
import pytest

pytest.importorskip("scipy")
pytest.importorskip("shapely")
pytest.importorskip("rasterio")
pytest.importorskip("pyproj")

import rasterio

from core.services.coverage.params import PodParams
from core.services.coverage.CoveragePodService import CoveragePodService
from core.services.coverage import writers
from core.services.coverage.contracts import SKIP_NO_DEM_AT_NADIR
from core.services.terrain.grid import GridSample, lonlat_to_mercator


# --- synthetic terrain / canopy providers (real spec-driven sampling) ----------

class _FakeProvider:
    def get_datum_info(self):
        return {"name": "FLAT", "type": "orthometric"}


class _FlatTerrain:
    """Flat (zero-elevation) DEM co-registered to any requested frame spec."""

    def __init__(self):
        self.provider = _FakeProvider()

    def sample_grid_spec(self, spec):
        data = np.zeros((spec.height, spec.width), dtype=np.float32)
        return GridSample(data=data, transform=spec.transform, crs=spec.crs,
                          datum_note="flat")


class _AllNanTerrain:
    """DEM that is NaN everywhere (no usable elevation for the footprint)."""

    def __init__(self):
        self.provider = _FakeProvider()

    def sample_grid_spec(self, spec):
        data = np.full((spec.height, spec.width), np.nan, dtype=np.float32)
        return GridSample(data=data, transform=spec.transform, crs=spec.crs,
                          datum_note="all-nan")


class _NanAtNadirTerrain:
    """Flat DEM everywhere except a NaN patch centered on the camera nadir.

    Forces ``dem_sample.sample_bilinear(nadir)`` to return None while leaving
    finite DEM in the surrounding footprint, exercising the service's
    median-of-finite fallback (frame still processed, not skipped).
    """

    def __init__(self, lon, lat, patch=3):
        self.provider = _FakeProvider()
        self._lon = lon
        self._lat = lat
        self._patch = patch

    def sample_grid_spec(self, spec):
        data = np.zeros((spec.height, spec.width), dtype=np.float32)
        cam_x, cam_y = lonlat_to_mercator(self._lon, self._lat)
        rows, cols = spec.world_to_index(cam_x, cam_y)
        r = int(round(float(rows)))
        c = int(round(float(cols)))
        p = self._patch
        data[max(0, r - p):min(spec.height, r + p + 1),
             max(0, c - p):min(spec.width, c + p + 1)] = np.nan
        return GridSample(data=data, transform=spec.transform, crs=spec.crs,
                          datum_note="nan-at-nadir")


class _FakeCanopy:
    """Dense-canopy provider matching what ``_sample_canopy`` reads.

    ``sample_grid_spec`` returns an object exposing ``.chm`` and ``.cover``
    ndarrays co-registered to the spec; ``source_name`` is read by the service
    for stats. Records call count so tests can assert the canopy path executed.
    """

    def __init__(self, chm_m=30.0, cover=1.0, source_name="FAKE_CHM_30m"):
        self.source_name = source_name
        self._chm_m = float(chm_m)
        self._cover = float(cover)
        self.calls = 0

    def sample_grid_spec(self, spec):
        self.calls += 1
        chm = np.full((spec.height, spec.width), self._chm_m, dtype=np.float32)
        cover = np.full((spec.height, spec.width), self._cover, dtype=np.float32)
        return types.SimpleNamespace(chm=chm, cover=cover)


# --- helpers -------------------------------------------------------------------

def _images(testData, names):
    """Build image dicts (name + path) for real RGB inputs, skipping if absent."""
    paths = []
    for n in names:
        p = os.path.join(testData['RGB_Input'], n)
        if not os.path.exists(p):
            pytest.skip(f"missing test image {p}")
        paths.append({'name': n, 'path': p})
    return paths


def _params():
    return PodParams(grid_res_m=3.0)


# --- P1: full end-to-end with real geometry + write/read-back ------------------

def test_end_to_end_real_geometry_writes_valid_products(tmp_path, testData):
    """Real image->geometry->terrain->kernel->accumulate->write, then read back.

    No seam is patched: ``_frame_geometry`` runs the real EXIF/XMP metadata path.
    """
    images = _images(testData, ['DJI_0082.JPG', 'DJI_0083.JPG', 'DJI_0084.JPG'])
    svc = CoveragePodService(terrain=_FlatTerrain(), canopy=None, params=_params())
    result = svc.calculate(images)

    # All three nadir frames carry pose+GPS+AGL, so all are placed, none skipped.
    assert result.cancelled is False
    assert result.image_count == 3
    assert result.skipped == []
    assert result.stats['skipped_counts'] == {}

    # POD raster: real geometry produced a non-empty grid with valid probabilities.
    pod = result.pod
    look = result.look_count
    assert pod.ndim == 2 and pod.size > 0
    assert np.isfinite(pod).all()
    assert float(pod.min()) >= 0.0
    assert float(pod.max()) <= 1.0
    assert float(pod.max()) > 0.0                      # something was actually seen

    # Internal consistency between looks and POD.
    assert int(look.max()) >= 1
    assert bool((pod[look > 0] > 0).all())             # covered -> nonzero POD
    assert bool((pod[look == 0] == 0).all())           # never seen -> zero POD

    # Write the four mission products and confirm all exist.
    out_dir = str(tmp_path / "coverage_out")
    paths = writers.write_all_outputs(result, out_dir)
    assert set(paths.keys()) == {"pod", "pod_values", "looks", "gaps", "stats"}
    for p in paths.values():
        assert os.path.exists(p)

    # coverage_pod.tif: 4-band uint8 RGBA GeoTIFF in EPSG:3857.
    with rasterio.open(paths["pod"]) as ds:
        assert ds.count == 4
        assert ds.dtypes[0] == "uint8"
        assert ds.crs.to_epsg() == 3857
        assert (ds.height, ds.width) == pod.shape
        assert ds.tags().get("ADIAT_PRODUCT") == "coverage_pod"

    # coverage_pod_values.tif: float32 probabilities, NaN where never looked at.
    with rasterio.open(paths["pod_values"]) as ds:
        assert ds.count == 1
        assert ds.dtypes[0] == "float32"
        assert np.isnan(ds.nodata)
        band = ds.read(1)
        assert band[look > 0] == pytest.approx(pod[look > 0], abs=1e-6)
        assert np.isnan(band[look == 0]).all()
        finite = band[np.isfinite(band)]
        assert finite.size > 0
        assert float(finite.min()) >= 0.0 and float(finite.max()) <= 1.0

    # coverage_looks.tif: uint16 look-count raster matching in-memory counts.
    with rasterio.open(paths["looks"]) as ds:
        assert ds.count == 1
        assert ds.dtypes[0] == "uint16"
        assert ds.nodata == 0
        looks_band = ds.read(1)
        assert int(looks_band.max()) == int(look.max())
        assert np.array_equal(looks_band, look.astype("uint16"))

    # coverage_gaps.geojson: a valid WGS84 FeatureCollection.
    with open(paths["gaps"], encoding="utf-8") as fh:
        gj = json.load(fh)
    assert gj["type"] == "FeatureCollection"
    assert isinstance(gj["features"], list)
    assert len(gj["features"]) == len(result.gap_polygons)

    # stats.json: counts and metadata match the computed result.
    with open(paths["stats"], encoding="utf-8") as fh:
        stats = json.load(fh)
    assert set(stats["area_sqm"].keys()) == {
        "looks_ge_1", "pod_ge_0_25", "pod_ge_0_50", "pod_ge_0_75"}
    assert stats["area_sqm"]["looks_ge_1"] > 0.0
    assert stats["grid"]["rows"] == pod.shape[0]
    assert stats["grid"]["cols"] == pod.shape[1]
    assert stats["terrain"]["name"] == "FLAT"
    assert stats["canopy"]["source"] == "none"
    assert stats["skipped_counts"] == {}
    assert stats["gaps"]["count"] == len(result.gap_polygons)


# --- P1(a): canopy-enabled path runs and attenuates POD ------------------------

def test_end_to_end_canopy_enabled_reduces_pod(tmp_path, testData):
    """A dense fake canopy is sampled per frame and measurably lowers POD."""
    images = _images(testData, ['DJI_0082.JPG', 'DJI_0083.JPG', 'DJI_0084.JPG'])

    baseline = CoveragePodService(
        terrain=_FlatTerrain(), canopy=None, params=_params()).calculate(images)

    canopy = _FakeCanopy(chm_m=30.0, cover=1.0, source_name="FAKE_CHM_30m")
    result = CoveragePodService(
        terrain=_FlatTerrain(), canopy=canopy, params=_params()).calculate(images)

    # The canopy path executed once per processed frame.
    assert result.image_count == baseline.image_count == 3
    assert canopy.calls == result.image_count

    # Dense foliage attenuates transmittance -> strictly lower peak POD.
    assert float(result.pod.max()) > 0.0
    assert float(result.pod.max()) < float(baseline.pod.max())
    assert np.isfinite(result.pod).all()
    assert float(result.pod.min()) >= 0.0 and float(result.pod.max()) <= 1.0

    # Canopy source is threaded into stats and persisted to disk.
    assert result.stats["canopy"]["source"] == "FAKE_CHM_30m"
    out_dir = str(tmp_path / "canopy_out")
    paths = writers.write_all_outputs(result, out_dir)
    with open(paths["stats"], encoding="utf-8") as fh:
        stats = json.load(fh)
    assert stats["canopy"]["source"] == "FAKE_CHM_30m"


# --- P1(b): no-DEM-at-nadir handling ------------------------------------------

def test_no_dem_at_nadir_uses_median_fallback(testData):
    """NaN at nadir but finite DEM elsewhere -> median fallback, frame processed."""
    images = _images(testData, ['DJI_0082.JPG'])

    # Read the real pose first so the NaN patch is placed exactly on nadir.
    probe = CoveragePodService(terrain=_FlatTerrain(), canopy=None, params=_params())
    fg = probe._frame_geometry(images[0])
    assert fg is not None                              # real EXIF/XMP pose resolved

    terrain = _NanAtNadirTerrain(fg.lon, fg.lat, patch=3)
    result = CoveragePodService(
        terrain=terrain, canopy=None, params=_params()).calculate(images)

    # The frame is still processed via the median-of-finite-DEM fallback.
    assert result.image_count == 1
    assert result.skipped == []
    assert SKIP_NO_DEM_AT_NADIR not in dict(result.skipped).values()
    assert float(result.pod.max()) > 0.0
    assert np.isfinite(result.pod).all()


def test_all_nan_dem_skips_no_dem_at_nadir(testData):
    """DEM NaN everywhere -> frame skipped with SKIP_NO_DEM_AT_NADIR."""
    images = _images(testData, ['DJI_0082.JPG'])
    result = CoveragePodService(
        terrain=_AllNanTerrain(), canopy=None, params=_params()).calculate(images)

    assert result.image_count == 0
    assert dict(result.skipped)['DJI_0082.JPG'] == SKIP_NO_DEM_AT_NADIR
    # accumulator was created before DEM sampling, so a (degenerate) stats dict is
    # still assembled and records the skip.
    assert result.stats['skipped_counts'][SKIP_NO_DEM_AT_NADIR] == 1
