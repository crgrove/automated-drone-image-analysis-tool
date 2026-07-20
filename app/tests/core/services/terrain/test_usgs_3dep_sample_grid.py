"""Tests for USGS3DEPProvider.sample_grid_spec (windowed reproject fast path).

Writes tiny real GeoTIFFs (EPSG:26910 UTM) into tmp_path so the reproject +
mosaic + nodata handling is exercised against actual rasterio datasets.
"""

import csv

import numpy as np
import pytest

pytest.importorskip("shapely")
rasterio = pytest.importorskip("rasterio")

from rasterio.transform import from_origin  # noqa: E402
from pyproj import Transformer  # noqa: E402

from core.services.terrain.USGS3DEPProvider import USGS3DEPProvider  # noqa: E402
from core.services.terrain.grid import spec_for_bounds_wgs84  # noqa: E402

UTM10 = "EPSG:26910"
NODATA = -9999.0
_to_wgs84 = Transformer.from_crs(UTM10, "EPSG:4326", always_xy=True).transform


def _utm_bbox_to_wgs84(west, south, east, north):
    lons, lats = [], []
    for x, y in [(west, south), (west, north), (east, south), (east, north)]:
        lon, lat = _to_wgs84(x, y)
        lons.append(lon)
        lats.append(lat)
    return min(lons), min(lats), max(lons), max(lats)


def _write_tile(path, west, north, data, res=10.0):
    rows, cols = data.shape
    transform = from_origin(west, north, res, res)
    with rasterio.open(
        path, "w", driver="GTiff", height=rows, width=cols, count=1,
        dtype="float32", crs=UTM10, transform=transform, nodata=NODATA,
    ) as dst:
        dst.write(data.astype("float32"), 1)
    east = west + cols * res
    south = north - rows * res
    return _utm_bbox_to_wgs84(west, south, east, north)


@pytest.fixture
def two_tile_provider(tmp_path):
    tiles_dir = tmp_path / "tiles"
    tiles_dir.mkdir()

    west0, north0 = 350000.0, 4286000.0  # Sierra-ish UTM 10N
    # Tile A: constant 500 m.
    a = np.full((100, 100), 500.0, dtype=np.float32)
    bbox_a = _write_tile(tiles_dir / "a.tif", west0, north0, a)

    # Tile B: adjacent east, eastward gradient + a nodata stripe in columns 40:60.
    b = np.tile(np.arange(100, dtype=np.float32) + 600.0, (100, 1))
    b[:, 40:60] = NODATA
    bbox_b = _write_tile(tiles_dir / "b.tif", west0 + 1000.0, north0, b)

    manifest = tmp_path / "dem_manifest.csv"
    with open(manifest, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["filename", "minX", "minY", "maxX", "maxY"])
        w.writeheader()
        for name, bbox in (("a.tif", bbox_a), ("b.tif", bbox_b)):
            w.writerow({"filename": name, "minX": bbox[0], "minY": bbox[1],
                        "maxX": bbox[2], "maxY": bbox[3]})

    provider = USGS3DEPProvider(str(manifest), str(tiles_dir))
    yield provider, bbox_a, bbox_b
    provider.close()


def test_lookup_tiles_bbox_returns_both(two_tile_provider):
    provider, bbox_a, bbox_b = two_tile_provider
    union = (min(bbox_a[0], bbox_b[0]), min(bbox_a[1], bbox_b[1]),
             max(bbox_a[2], bbox_b[2]), max(bbox_a[3], bbox_b[3]))
    tiles = provider.lookup_tiles_bbox(*union)
    names = sorted(t["filename"] for t in tiles)
    assert names == ["a.tif", "b.tif"]


def test_sample_grid_mosaics_both_tiles_no_seam(two_tile_provider):
    provider, bbox_a, bbox_b = two_tile_provider
    union = (min(bbox_a[0], bbox_b[0]), min(bbox_a[1], bbox_b[1]),
             max(bbox_a[2], bbox_b[2]), max(bbox_a[3], bbox_b[3]))
    # Shrink slightly to avoid edge cells that only partially overlap.
    pad_lon = (union[2] - union[0]) * 0.05
    pad_lat = (union[3] - union[1]) * 0.05
    spec = spec_for_bounds_wgs84(
        (union[0] + pad_lon, union[1] + pad_lat, union[2] - pad_lon, union[3] - pad_lat),
        15.0,
    )
    sample = provider.sample_grid_spec(spec)
    assert sample is not None
    assert sample.data.shape == (spec.height, spec.width)

    # Constant tile A: its western portion should sit at ~500 with no NaN.
    west_quarter = sample.data[:, : spec.width // 4]
    assert np.nanmedian(west_quarter) == pytest.approx(500.0, abs=2.0)

    # There must be finite coverage spanning the A/B seam (middle columns).
    mid = sample.data[:, spec.width // 2 - 2: spec.width // 2 + 2]
    assert np.isfinite(mid).any()


def test_nodata_stripe_becomes_nan(two_tile_provider):
    provider, bbox_a, bbox_b = two_tile_provider
    # Grid over just tile B's nodata stripe region (its central columns).
    spec = spec_for_bounds_wgs84(bbox_b, 12.0)
    sample = provider.sample_grid_spec(spec)
    assert sample is not None
    # The nodata stripe (columns 40:60 of a 100-wide tile) must surface as NaN,
    # and it must NOT have bled a -9999 sentinel into finite values.
    assert np.isnan(sample.data).any()
    finite = sample.data[np.isfinite(sample.data)]
    assert finite.min() > -1000.0  # no sentinel bleed


def test_bbox_outside_coverage_returns_none(two_tile_provider):
    provider, _, _ = two_tile_provider
    spec = spec_for_bounds_wgs84((-100.0, 20.0, -99.99, 20.01), 15.0)
    assert provider.sample_grid_spec(spec) is None
