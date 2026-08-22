"""Orchestration tests for CoveragePodService with mocked geometry/terrain seams."""

import numpy as np
import pytest

pytest.importorskip("scipy")
pytest.importorskip("shapely")

from core.services.coverage.params import PodParams
from core.services.coverage.CoveragePodService import CoveragePodService
from core.services.coverage.contracts import (
    SKIP_HIDDEN, SKIP_NO_POSE, SKIP_PITCH_TOO_SHALLOW, SKIP_NO_DEM, SKIP_ERROR,
)
from core.services.terrain.grid import GridSample
from ._kernel_helpers import make_fg


class _FakeProvider:
    def get_datum_info(self):
        return {"name": "FLAT", "type": "orthometric"}


class _FlatTerrain:
    """Returns a flat (zero-elevation) DEM co-registered to any requested spec."""
    def __init__(self):
        self.provider = _FakeProvider()

    def sample_grid_spec(self, spec):
        data = np.zeros((spec.height, spec.width), dtype=np.float32)
        return GridSample(data=data, transform=spec.transform, crs=spec.crs,
                          datum_note="flat")


class _NoTerrain:
    def __init__(self):
        self.provider = _FakeProvider()

    def sample_grid_spec(self, spec):
        return None


def _service(terrain, params=None, canopy=None):
    svc = CoveragePodService(terrain=terrain, canopy=canopy,
                             params=params or PodParams(grid_res_m=3.0))

    def fake_fg(image):
        if image.get('_raise'):
            raise RuntimeError("boom")
        return image.get('_fg')

    svc._frame_geometry = fake_fg
    return svc


class _CoverageCanopy:
    """Canopy stub reporting coverage over a fraction of each frame grid's
    columns, so the POD pass can measure canopy-coverage of searched cells.

    mode: 'full' (all cells), 'none' (no cells), 'left_half' (left columns),
    or 'null' (sample_grid_spec returns None, i.e. no tile intersected)."""
    source_name = "coverage_canopy"

    def __init__(self, mode='full'):
        self.mode = mode

    def sample_grid_spec(self, spec):
        from core.services.terrain.CanopyService import CanopySample
        h, w = spec.height, spec.width
        if self.mode == 'null':
            return None
        covered = np.zeros((h, w), dtype=bool)
        if self.mode == 'full':
            covered[:] = True
        elif self.mode == 'left_half':
            covered[:, :max(1, w // 2)] = True
        # 'none' leaves covered all-False
        return CanopySample(
            chm=np.zeros((h, w), dtype=np.float32),
            cover=np.zeros((h, w), dtype=np.float32),
            transform=spec.transform, crs=spec.crs, cover_derived=False,
            source_name=self.source_name, covered=covered)


def test_skip_taxonomy_and_processing():
    images = [
        {'name': 'hidden', 'hidden': True},
        {'name': 'nopose', '_fg': None},
        {'name': 'shallow', '_fg': make_fg(pitch=-5.0)},
        {'name': 'err', '_raise': True},
        {'name': 'good', '_fg': make_fg(pitch=-90.0)},
    ]
    calls = []
    svc = _service(_FlatTerrain())
    result = svc.calculate(images, progress_callback=lambda c, t, m: calls.append((c, t, m)))

    assert result.cancelled is False
    assert result.image_count == 1
    reasons = dict(result.skipped)
    assert reasons['hidden'] == SKIP_HIDDEN
    assert reasons['nopose'] == SKIP_NO_POSE
    assert reasons['shallow'] == SKIP_PITCH_TOO_SHALLOW
    assert reasons['err'] == SKIP_ERROR
    assert result.stats['skipped_counts'][SKIP_ERROR] == 1
    # Altitude-anchor pre-pass (1) + per-image progress (5) + 2 finalize ticks.
    assert len(calls) == len(images) + 3


def test_no_dem_skips_all():
    images = [{'name': 'g', '_fg': make_fg(pitch=-90.0)}]
    svc = _service(_NoTerrain())
    result = svc.calculate(images)
    # No frames could be placed (no accumulator) -> empty result.
    assert result.image_count == 0
    assert dict(result.skipped)['g'] == SKIP_NO_DEM
    assert result.pod.size == 0


def test_cancel_immediately():
    images = [{'name': 'g', '_fg': make_fg(pitch=-90.0)}]
    svc = _service(_FlatTerrain())
    result = svc.calculate(images, cancel_check=lambda: True)
    assert result.cancelled is True
    assert result.image_count == 0


def test_cancel_midway():
    images = [{'name': f'g{i}', '_fg': make_fg(pitch=-90.0)} for i in range(4)]
    svc = _service(_FlatTerrain())
    state = {'n': 0}

    def cancel():
        state['n'] += 1
        return state['n'] > 2   # allow a couple of frames, then cancel

    result = svc.calculate(images, cancel_check=cancel)
    assert result.cancelled is True


def test_processed_result_has_products():
    images = [
        {'name': 'a', '_fg': make_fg(pitch=-90.0, yaw=0.0)},
        {'name': 'b', '_fg': make_fg(pitch=-90.0, yaw=90.0)},
    ]
    svc = _service(_FlatTerrain())
    result = svc.calculate(images)
    assert result.image_count == 2
    assert result.pod.ndim == 2 and result.pod.size > 0
    assert result.limiting_factor is not None
    assert result.frame_index is not None
    assert 'area_sqm' in result.stats
    assert result.stats['terrain']['name'] == 'FLAT'


# ---------------------------------------------------------------------------
# P2: error / edge-path coverage (canopy branches, nadir-elevation fallback,
# no-DEM-at-nadir skip, and the ExifTool safety-net retry in _frame_geometry).
# ---------------------------------------------------------------------------

import math  # noqa: E402
from unittest.mock import patch, MagicMock  # noqa: E402

from core.services.terrain.grid import lonlat_to_mercator  # noqa: E402
from core.services.coverage.contracts import SKIP_NO_DEM_AT_NADIR  # noqa: E402
from helpers.MetaDataHelper import MetaDataHelper  # noqa: E402
from helpers.LocationInfo import LocationInfo  # noqa: E402


class _CanopySample:
    """Minimal canopy sample exposing the .chm / .cover ndarrays the service reads."""
    def __init__(self, chm, cover):
        self.chm = chm
        self.cover = cover


class _FakeCanopy:
    """Canopy provider returning uniform CHM/cover co-registered to the frame spec."""
    source_name = "TEST_CHM"

    def __init__(self, chm_h=5.0, cover=0.8):
        self.chm_h = chm_h
        self.cover = cover
        self.calls = 0

    def sample_grid_spec(self, spec):
        self.calls += 1
        chm = np.full((spec.height, spec.width), self.chm_h, dtype=np.float32)
        cov = np.full((spec.height, spec.width), self.cover, dtype=np.float32)
        return _CanopySample(chm, cov)


class _NoneCanopy:
    """Canopy provider whose sample misses the footprint (returns None)."""
    source_name = "EMPTY_CHM"

    def sample_grid_spec(self, spec):
        return None


class _RaisingCanopy:
    """Canopy provider whose sample raises (e.g. a tile read failure)."""
    source_name = "BROKEN_CHM"

    def sample_grid_spec(self, spec):
        raise RuntimeError("canopy read failed")


class _NadirNanTerrain:
    """Finite DEM everywhere except NaN in the 2x2 block around the camera nadir.

    That is exactly the block ``GridSample.sample_bilinear`` reads, so the nadir
    bilinear sample returns None and the median-of-finite-DEM fallback fires.
    """
    def __init__(self, lon, lat, elev=100.0):
        self.provider = _FakeProvider()
        self.lon = lon
        self.lat = lat
        self.elev = elev

    def sample_grid_spec(self, spec):
        data = np.full((spec.height, spec.width), self.elev, dtype=np.float32)
        cam_x, cam_y = lonlat_to_mercator(self.lon, self.lat)
        rows, cols = spec.world_to_index(cam_x, cam_y)
        r0 = int(math.floor(float(rows)))
        c0 = int(math.floor(float(cols)))
        for rr in (r0, r0 + 1):
            for cc in (c0, c0 + 1):
                if 0 <= rr < spec.height and 0 <= cc < spec.width:
                    data[rr, cc] = np.nan
        return GridSample(data=data, transform=spec.transform, crs=spec.crs,
                          datum_note="nadir-nan")


class _AllNanTerrain:
    """DEM sample that co-registers but is entirely nodata (all NaN)."""
    def __init__(self):
        self.provider = _FakeProvider()

    def sample_grid_spec(self, spec):
        data = np.full((spec.height, spec.width), np.nan, dtype=np.float32)
        return GridSample(data=data, transform=spec.transform, crs=spec.crs,
                          datum_note="all-nan")


def _nadir_image(name='a'):
    return {'name': name, '_fg': make_fg(pitch=-90.0, yaw=0.0)}


def test_canopy_lowers_pod_and_records_source():
    """A canopy providing CHM/cover must be sampled, attenuate POD via
    Beer-Lambert transmittance, and surface its source name in the stats."""
    base = _service(_FlatTerrain())
    base_result = base.calculate([_nadir_image()])

    svc = _service(_FlatTerrain())
    canopy = _FakeCanopy()
    svc.canopy = canopy
    result = svc.calculate([_nadir_image()])

    assert canopy.calls == 1                     # the canopy was actually sampled
    assert result.image_count == 1
    assert result.stats['canopy']['source'] == 'TEST_CHM'
    assert base_result.stats['canopy']['source'] == 'none'
    # Foliage attenuation must reduce mean POD relative to the bare-earth run.
    assert result.stats['mean_pod_covered'] < base_result.stats['mean_pod_covered']


def test_canopy_sample_none_skips_canopy_but_processes():
    """When the canopy sample returns None the frame is still placed with no
    attenuation (identical mean POD to the bare-earth run)."""
    base = _service(_FlatTerrain())
    base_result = base.calculate([_nadir_image()])

    svc = _service(_FlatTerrain())
    svc.canopy = _NoneCanopy()
    result = svc.calculate([_nadir_image()])

    assert result.image_count == 1
    # Source name still reflects the configured provider even when sampling missed.
    assert result.stats['canopy']['source'] == 'EMPTY_CHM'
    # No CHM/cover -> transmittance 1.0 -> POD unchanged vs. bare earth.
    assert result.stats['mean_pod_covered'] == pytest.approx(
        base_result.stats['mean_pod_covered'])


def test_canopy_sample_raises_logs_warning_and_skips_canopy():
    """A raising canopy sample is caught, logged as a warning, and the canopy is
    dropped for that frame (the frame is not marked SKIP_ERROR)."""
    svc = _service(_FlatTerrain())
    svc.canopy = _RaisingCanopy()
    svc.logger = MagicMock()
    result = svc.calculate([_nadir_image()])

    assert result.image_count == 1
    assert result.skipped == []
    assert svc.logger.warning.called
    warn_text = " ".join(str(c.args[0]) for c in svc.logger.warning.call_args_list)
    assert "Canopy sample failed" in warn_text


def test_nadir_nan_falls_back_to_median_dem():
    """NaN DEM at the camera-nadir cell (finite elsewhere) must not skip the
    frame: the median-of-finite-DEM fallback supplies the nadir elevation."""
    svc = _service(_NadirNanTerrain(lon=-120.5, lat=38.7))
    result = svc.calculate([_nadir_image(name='g')])

    assert result.image_count == 1
    assert result.skipped == []
    assert result.pod.ndim == 2 and result.pod.size > 0


def test_all_nan_dem_skips_no_dem_at_nadir():
    """An entirely-NaN DEM sample (no finite cells) skips the frame with the
    SKIP_NO_DEM_AT_NADIR reason rather than crashing."""
    svc = _service(_AllNanTerrain())
    result = svc.calculate([_nadir_image(name='g')])

    assert result.image_count == 0
    assert dict(result.skipped)['g'] == SKIP_NO_DEM_AT_NADIR


def test_frame_geometry_retries_merged_reader_when_direct_misses_pose():
    """When the fast direct XMP parse misses pose (fg is None) but the image is
    GPS-tagged, _frame_geometry must retry with the ExifTool-backed merged reader
    and build a FrameGeometry from it."""
    svc = CoveragePodService(terrain=_FlatTerrain(), canopy=None,
                             params=PodParams(grid_res_m=3.0))

    direct_xmp = {'no_pose': True}
    merged_xmp = {'drone-dji:GimbalPitchDegree': '-90.0'}
    good_fg = make_fg(pitch=-90.0)

    def fake_build(image, path, exif_data, xmp_data):
        # Direct read misses pose -> None; merged read supplies it -> FrameGeometry.
        return good_fg if xmp_data is merged_xmp else None

    with patch.object(MetaDataHelper, 'get_exif_data_piexif', return_value={'exif': 1}), \
            patch.object(MetaDataHelper, 'get_xmp_data_direct',
                         return_value=direct_xmp) as m_direct, \
            patch.object(MetaDataHelper, 'get_xmp_data_merged',
                         return_value=merged_xmp) as m_merged, \
            patch.object(LocationInfo, 'get_gps',
                         return_value={'latitude': 38.7, 'longitude': -120.5}) as m_gps:
        svc._build_frame_geometry = fake_build
        fg = svc._frame_geometry({'path': '/fake/img.jpg'})

    assert fg is good_fg
    m_direct.assert_called_once_with('/fake/img.jpg')
    m_merged.assert_called_once_with('/fake/img.jpg')   # the retry actually fired
    m_gps.assert_called_once()                           # retry is GPS-gated


def test_frame_geometry_no_retry_when_no_gps():
    """The merged-reader retry is GPS-gated: with no GPS fix, _frame_geometry
    returns None without spawning the expensive ExifTool merged read."""
    svc = CoveragePodService(terrain=_FlatTerrain(), canopy=None,
                             params=PodParams(grid_res_m=3.0))

    with patch.object(MetaDataHelper, 'get_exif_data_piexif', return_value={}), \
            patch.object(MetaDataHelper, 'get_xmp_data_direct',
                         return_value={}) as m_direct, \
            patch.object(MetaDataHelper, 'get_xmp_data_merged') as m_merged, \
            patch.object(LocationInfo, 'get_gps', return_value=None):
        svc._build_frame_geometry = lambda image, path, exif_data, xmp_data: None
        fg = svc._frame_geometry({'path': '/fake/img.jpg'})

    assert fg is None
    m_direct.assert_called_once()
    m_merged.assert_not_called()


class _FallbackTerrain(_FlatTerrain):
    """Flat DEM served through the online fallback (source-tagged)."""
    def sample_grid_spec(self, spec):
        sample = super().sample_grid_spec(spec)
        sample.source = 'terrarium_fallback'
        return sample


def test_dem_fallback_frames_counted():
    """Frames served by the Terrarium fallback are counted in the result and
    stats so the completion UI can report the degraded resolution honestly."""
    images = [{'name': f'g{i}', '_fg': make_fg(pitch=-90.0)} for i in range(3)]
    svc = _service(_FallbackTerrain())
    result = svc.calculate(images)

    assert result.image_count == 3
    assert result.dem_fallback_frames == 3
    assert result.stats['dem_fallback_frames'] == 3


def test_dem_fallback_zero_for_primary_served_frames():
    images = [{'name': 'g', '_fg': make_fg(pitch=-90.0)}]
    svc = _service(_FlatTerrain())
    result = svc.calculate(images)
    assert result.dem_fallback_frames == 0
    assert result.stats['dem_fallback_frames'] == 0


def test_frame_sources_recorded_for_all_inputs():
    """The result records every input frame's identity (path/name) indexed by
    frame id, so consumers can resolve a FrameIndex id back to an image
    without assuming any particular ordering of the caller's list."""
    images = [
        {'name': 'a', 'path': '/f/a.jpg', '_fg': make_fg(pitch=-90.0)},
        {'name': 'b', 'path': '/f/b.jpg', 'hidden': True},
        {'name': 'c', 'path': '/f/c.jpg', '_fg': make_fg(pitch=-90.0)},
    ]
    svc = _service(_FlatTerrain())
    result = svc.calculate(images)
    assert result.frame_sources is not None
    assert [s['name'] for s in result.frame_sources] == ['a', 'b', 'c']
    assert [s['path'] for s in result.frame_sources] == ['/f/a.jpg', '/f/b.jpg', '/f/c.jpg']
    # frame_sources aligns with frame ids: the processed frames (0 and 2) index
    # back to the right images.
    assert result.frame_sources[0]['name'] == 'a'
    assert result.frame_sources[2]['name'] == 'c'


# ---------------------------------------------------------------------------
# Canopy coverage of the searched area (are we accounting for vegetation?)
# ---------------------------------------------------------------------------

def test_canopy_coverage_full():
    """Canopy tiles cover every searched cell -> fraction 1.0, none missing."""
    images = [{'name': f'g{i}', '_fg': make_fg(pitch=-90.0)} for i in range(3)]
    svc = _service(_FlatTerrain(), canopy=_CoverageCanopy('full'))
    result = svc.calculate(images)
    assert result.canopy_coverage_fraction == pytest.approx(1.0)
    assert result.canopy_frames_missing == 0
    assert result.stats['canopy_coverage']['fraction'] == pytest.approx(1.0)


def test_canopy_coverage_none_when_tiles_miss_the_flight():
    """Canopy configured but no tile covers any frame -> fraction 0, every
    processed frame flagged missing (POD there computed as bare ground)."""
    images = [{'name': f'g{i}', '_fg': make_fg(pitch=-90.0)} for i in range(3)]
    svc = _service(_FlatTerrain(), canopy=_CoverageCanopy('none'))
    result = svc.calculate(images)
    assert result.canopy_coverage_fraction == pytest.approx(0.0)
    assert result.canopy_frames_missing == 3


def test_canopy_coverage_none_when_sample_returns_none():
    """A frame whose footprint intersects no canopy tile (sample None) counts
    as uncovered, not an error."""
    images = [{'name': 'g', '_fg': make_fg(pitch=-90.0)}]
    svc = _service(_FlatTerrain(), canopy=_CoverageCanopy('null'))
    result = svc.calculate(images)
    assert result.canopy_coverage_fraction == pytest.approx(0.0)
    assert result.canopy_frames_missing == 1


def test_canopy_coverage_partial():
    """Tiles cover part of each frame -> fraction strictly between 0 and 1."""
    images = [{'name': 'g', '_fg': make_fg(pitch=-90.0)}]
    svc = _service(_FlatTerrain(), canopy=_CoverageCanopy('left_half'))
    result = svc.calculate(images)
    assert 0.0 < result.canopy_coverage_fraction < 1.0
    assert 'canopy_coverage' in result.stats


def test_canopy_coverage_none_metric_when_no_canopy_configured():
    """No canopy source -> no coverage metric (None), stats key absent."""
    images = [{'name': 'g', '_fg': make_fg(pitch=-90.0)}]
    svc = _service(_FlatTerrain())   # canopy=None
    result = svc.calculate(images)
    assert result.canopy_coverage_fraction is None
    assert result.canopy_frames_missing == 0
    assert 'canopy_coverage' not in result.stats
