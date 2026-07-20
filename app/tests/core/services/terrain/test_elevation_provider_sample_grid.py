"""Tests for the ElevationProvider.sample_grid ABC default (per-point slow path)."""

import numpy as np
import pytest

pytest.importorskip("affine")

from core.services.terrain.ElevationProvider import ElevationProvider, TerrariumProvider  # noqa: E402
from core.services.terrain.grid import (  # noqa: E402
    make_lattice_spec,
    spec_for_bounds_wgs84,
    mercator_to_lonlat,
)


class _PlaneProvider(ElevationProvider):
    """Analytic provider: elevation is a plane in lat/lon, so the slow-path grid
    can be checked against a closed form at every cell center."""

    def __init__(self):
        self.calls = 0

    def get_provider_name(self):
        return "plane"

    def get_datum_info(self):
        return {'name': 'TEST', 'type': 'orthometric', 'geoid_model': 'none'}

    def get_provider_kind(self):
        return 'local_geotiff'

    def sample_elevation(self, lat, lon):
        self.calls += 1
        return 2.0 * lat + 3.0 * lon


def test_slow_path_matches_plane_at_cell_centers():
    provider = _PlaneProvider()
    spec = spec_for_bounds_wgs84((-120.50, 38.70, -120.48, 38.72), 30.0)
    sample = provider.sample_grid_spec(spec)
    assert sample is not None
    assert sample.data.shape == (spec.height, spec.width)
    assert sample.crs == spec.crs
    assert "orthometric" in sample.datum_note

    xs, ys = spec.cell_centers()
    for i in (0, spec.height // 2, spec.height - 1):
        for j in (0, spec.width // 2, spec.width - 1):
            lon, lat = mercator_to_lonlat(float(xs[j]), float(ys[i]))
            expected = 2.0 * lat + 3.0 * lon
            assert sample.data[i, j] == pytest.approx(expected, abs=1e-3)


def test_none_values_become_nan():
    class _Sparse(_PlaneProvider):
        def sample_elevation(self, lat, lon):
            return None if lon < -120.49 else 100.0

    provider = _Sparse()
    spec = spec_for_bounds_wgs84((-120.50, 38.70, -120.48, 38.71), 30.0)
    sample = provider.sample_grid_spec(spec)
    assert sample is not None
    assert np.isnan(sample.data).any()
    assert np.nanmax(sample.data) == pytest.approx(100.0)


def test_unimplemented_sample_elevation_returns_none():
    # Terrarium raises NotImplementedError for sample_elevation -> grid slow path None.
    provider = TerrariumProvider()
    spec = spec_for_bounds_wgs84((-120.50, 38.70, -120.49, 38.71), 30.0)
    assert provider.sample_grid_spec(spec) is None


def test_cell_limit_guard_returns_none():
    provider = _PlaneProvider()
    # A grid far exceeding SLOW_GRID_CELL_LIMIT.
    big = make_lattice_spec((0.0, 0.0, 3000.0, 3000.0), 3.0)  # 1_000_000 cells
    assert big.width * big.height > ElevationProvider.SLOW_GRID_CELL_LIMIT
    assert provider.sample_grid_spec(big) is None
    assert provider.calls == 0
