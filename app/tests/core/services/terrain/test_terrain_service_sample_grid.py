"""Tests for TerrainService.sample_grid_spec dispatch + the Terrarium mosaic path."""

import numpy as np
import pytest

pytest.importorskip("affine")
pytest.importorskip("scipy")
from PIL import Image  # noqa: E402

from core.services.terrain.TerrainService import TerrainService  # noqa: E402
from core.services.terrain.grid import (  # noqa: E402
    spec_for_bounds_wgs84,
    make_lattice_spec,
    GridSample,
)


def _terrarium_tile(elevation_m: float) -> Image.Image:
    """Build a 256x256 PIL tile whose every pixel decodes to ``elevation_m``."""
    total = elevation_m + 32768.0
    r = int(total // 256)
    rem = total - r * 256
    g = int(rem)
    b = int(round((rem - g) * 256)) % 256
    arr = np.zeros((256, 256, 3), dtype=np.uint8)
    arr[..., 0] = r
    arr[..., 1] = g
    arr[..., 2] = b
    return Image.fromarray(arr, mode="RGB")


class _FakeTileCache:
    def __init__(self, elevation_m):
        self._tile = _terrarium_tile(elevation_m)

    def get_tile(self, z, x, y):
        return self._tile

    def get_tile_if_cached(self, z, x, y):
        return self._tile


@pytest.fixture
def terrarium_service(tmp_path):
    svc = TerrainService(cache_dir=str(tmp_path), enable_geoid=False,
                         provider_id="terrarium")
    return svc


def test_disabled_service_returns_none(terrarium_service):
    terrarium_service.enabled = False
    spec = spec_for_bounds_wgs84((-120.50, 38.70, -120.495, 38.705), 30.0)
    assert terrarium_service.sample_grid_spec(spec) is None


def test_tiled_web_mosaic_returns_constant(terrarium_service):
    terrarium_service.cache = _FakeTileCache(1234.0)
    spec = spec_for_bounds_wgs84((-120.50, 38.70, -120.495, 38.705), 40.0)
    sample = terrarium_service.sample_grid_spec(spec)
    assert sample is not None
    assert sample.data.shape == (spec.height, spec.width)
    # Every decoded cell should recover the encoded constant (within 1/256 m).
    assert np.nanmax(np.abs(sample.data - 1234.0)) < 0.02


def test_local_geotiff_dispatch(terrarium_service, monkeypatch):
    spec = make_lattice_spec((0.0, 0.0, 30.0, 30.0), 3.0)
    sentinel = GridSample(
        data=np.zeros((spec.height, spec.width), dtype=np.float32),
        transform=spec.transform, crs=spec.crs, datum_note="stub",
    )

    class _Stub:
        def get_provider_kind(self):
            return "local_geotiff"

        def sample_grid_spec(self, s):
            return sentinel

    terrarium_service.provider = _Stub()
    assert terrarium_service.sample_grid_spec(spec) is sentinel


def test_sample_grid_convenience_wrapper(terrarium_service):
    terrarium_service.cache = _FakeTileCache(500.0)
    sample = terrarium_service.sample_grid((-120.50, 38.70, -120.495, 38.705), 40.0)
    assert sample is not None
    assert np.nanmax(np.abs(sample.data - 500.0)) < 0.02
