"""Unit tests for USGS3DEPProvider tile-index lookup.

These tests focus on the manifest-based STRtree lookup that runs without rasterio.
Live elevation sampling is exercised separately by the end-to-end Temple Crag flow.
"""

import csv
from pathlib import Path

import pytest

shapely = pytest.importorskip("shapely")

from core.services.terrain.USGS3DEPProvider import USGS3DEPProvider


@pytest.fixture
def fake_manifest(tmp_path):
    """Build a manifest CSV + dummy tile filenames covering two tiles in CA."""
    manifest = tmp_path / "dem_manifest.csv"
    tiles_dir = tmp_path / "tiles"
    tiles_dir.mkdir()
    rows = [
        # filename, publicationDate, sourceName, minX, minY, maxX, maxY, sizeMB
        {"filename": "USGS_1M_10_x75y427_CA.tif",
         "publicationDate": "2025-05-15", "sourceName": "ScienceBase",
         "minX": -120.13, "minY": 38.45, "maxX": -120.01, "maxY": 38.55, "sizeMB": 290.0},
        {"filename": "USGS_1M_10_x75y428_CA.tif",
         "publicationDate": "2025-05-15", "sourceName": "ScienceBase",
         "minX": -120.13, "minY": 38.55, "maxX": -120.01, "maxY": 38.65, "sizeMB": 290.0},
    ]
    with manifest.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return manifest, tiles_dir


def test_lookup_tile_finds_correct_bbox(fake_manifest):
    manifest, tiles_dir = fake_manifest
    provider = USGS3DEPProvider(str(manifest), str(tiles_dir))
    # Inside the first tile (lat range 38.45-38.55, lon range -120.13 to -120.01).
    tile = provider.lookup_tile(38.50, -120.07)
    assert tile is not None
    assert tile['filename'] == "USGS_1M_10_x75y427_CA.tif"
    # Inside the second tile.
    tile = provider.lookup_tile(38.60, -120.07)
    assert tile is not None
    assert tile['filename'] == "USGS_1M_10_x75y428_CA.tif"


def test_lookup_tile_returns_none_outside_coverage(fake_manifest):
    manifest, tiles_dir = fake_manifest
    provider = USGS3DEPProvider(str(manifest), str(tiles_dir))
    # Outside the bounding boxes (way north).
    assert provider.lookup_tile(40.0, -120.07) is None
    # Outside (way west).
    assert provider.lookup_tile(38.50, -130.0) is None


def test_provider_kind_is_local_geotiff(fake_manifest):
    manifest, tiles_dir = fake_manifest
    provider = USGS3DEPProvider(str(manifest), str(tiles_dir))
    assert provider.get_provider_kind() == 'local_geotiff'
    info = provider.get_datum_info()
    assert info['name'] == 'NAVD88'


def test_missing_manifest_does_not_raise(tmp_path):
    """A missing manifest yields an empty provider — sample_elevation returns None gracefully."""
    provider = USGS3DEPProvider(str(tmp_path / "does_not_exist.csv"), str(tmp_path))
    assert provider.lookup_tile(38.5, -120.07) is None
    assert provider.sample_elevation(38.5, -120.07) is None


# ---------------------------------------------------------------------------
# covers(): manifest-driven AOI coverage classification
# ---------------------------------------------------------------------------

def test_covers_full_when_tiles_blanket_aoi(fake_manifest):
    manifest, tiles_dir = fake_manifest
    provider = USGS3DEPProvider(str(manifest), str(tiles_dir))
    # Interior box well inside the two stacked tiles (-120.13..-120.01, 38.45..38.65).
    assert provider.covers((-120.12, 38.46, -120.02, 38.64)) == 'full'


def test_covers_partial_when_aoi_extends_past_tiles(fake_manifest):
    manifest, tiles_dir = fake_manifest
    provider = USGS3DEPProvider(str(manifest), str(tiles_dir))
    assert provider.covers((-120.12, 38.46, -119.50, 38.64)) == 'partial'


def test_covers_none_outside_all_tiles(fake_manifest):
    manifest, tiles_dir = fake_manifest
    provider = USGS3DEPProvider(str(manifest), str(tiles_dir))
    assert provider.covers((-119.00, 30.00, -118.90, 30.10)) == 'none'


def test_covers_none_with_unloaded_manifest(tmp_path):
    provider = USGS3DEPProvider(str(tmp_path / "missing.csv"), str(tmp_path))
    assert provider.covers((-120.12, 38.46, -120.02, 38.64)) == 'none'
