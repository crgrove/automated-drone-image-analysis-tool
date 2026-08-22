"""Camera-elevation resolution for the POD pipeline.

The reported AGL (``drone-dji:RelativeAltitude``) is height above the TAKEOFF
point, not above the ground below the aircraft. These tests pin the mission
takeoff anchor in ``CoveragePodService._resolve_altitude_anchor`` — including the
two rejections that keep a datum mismatch from silently biasing every frame —
and the per-frame resolution order in ``_resolve_cam_elev``.
"""

import numpy as np
import pytest

pytest.importorskip("scipy")
pytest.importorskip("shapely")

from core.services.coverage.params import PodParams
from core.services.coverage.CoveragePodService import CoveragePodService
from core.services.terrain.grid import GridSample
from ._kernel_helpers import make_fg


class _FakeProvider:
    def get_datum_info(self):
        return {"name": "FLAT", "type": "orthometric"}


class _Elevation:
    def __init__(self, elevation_m):
        self.source = 'terrain'
        self.elevation_m = elevation_m
        self.resolution_m = 10.0


class _GridOnlyTerrain:
    """DEM at a constant orthometric elevation. No geoid, no point lookup."""

    def __init__(self, elev_m=0.0):
        self.provider = _FakeProvider()
        self.elev_m = float(elev_m)
        self.specs = []

    def sample_grid_spec(self, spec):
        self.specs.append(spec)
        data = np.full((spec.height, spec.width), self.elev_m, dtype=np.float32)
        return GridSample(data=data, transform=spec.transform, crs=spec.crs,
                          datum_note="flat")


class _GeoidMixin:
    """``undulation=None`` models a service whose geoid grid is unavailable
    (EGM96 missing), which must not be read as 0 m."""

    def _init_geoid(self, undulation):
        self.undulation = undulation
        self.geoid_calls = []

    def get_geoid_undulation(self, lat, lon):
        self.geoid_calls.append((lat, lon))
        return self.undulation


class _NoGeoidTerrain(_GridOnlyTerrain):
    """Point lookups, but no geoid API at all."""

    def get_elevation(self, lat, lon):
        return _Elevation(self.elev_m)


class _NoPointTerrain(_GridOnlyTerrain, _GeoidMixin):
    """Geoid, but no ``get_elevation`` - the frame grid must then be re-sampled."""

    def __init__(self, elev_m=0.0, undulation=None):
        super().__init__(elev_m)
        self._init_geoid(undulation)


class _Terrain(_NoGeoidTerrain, _GeoidMixin):
    """The full service surface: grid sampling, point lookups and a geoid."""

    def __init__(self, elev_m=0.0, undulation=None):
        super().__init__(elev_m)
        self._init_geoid(undulation)


class _FlakyGeoidTerrain(_Terrain):
    """Geoid whose first lookup fails, as the lazily-loaded EGM96 grid can."""

    def __init__(self, elev_m=0.0, undulation=30.0):
        super().__init__(elev_m, undulation)
        self.failed = False

    def get_geoid_undulation(self, lat, lon):
        self.geoid_calls.append((lat, lon))
        if not self.failed:
            self.failed = True
            raise RuntimeError("EGM96 grid still loading")
        return self.undulation


def _service(terrain, custom_altitude_ft=None):
    svc = CoveragePodService(terrain=terrain, canopy=None,
                             params=PodParams(grid_res_m=3.0),
                             custom_altitude_ft=custom_altitude_ft)
    svc._frame_geometry = lambda image: image.get('_fg')
    return svc


def _frame(asl=None, agl=120.0, name='f', **extra):
    fg = make_fg(pitch=-90.0, agl=agl)
    fg.asl_alt_m = asl
    image = {'name': name, 'path': f"{name}.JPG", '_fg': fg}
    image.update(extra)
    return image, fg


def _mission(count=5, asl=None, agl=120.0, **extra):
    """``count`` frames sharing one altitude story (the anchor needs >= 3)."""
    pairs = [_frame(asl=asl, agl=agl, name=f"f{i}", **extra) for i in range(count)]
    return [p[0] for p in pairs], [p[1] for p in pairs]


# --- the correction ---------------------------------------------------------

def test_camera_elevation_is_anchored_to_takeoff_not_the_ground_below():
    """Ground 100 m above launch: elevation follows takeoff, not DEM(nadir).

    Reported AGL is 120 m above a 900 m takeoff, so the camera is really at
    1020 m while the ground below is at 1000 m. The flat-terrain rule would
    place it at 1120 m — 100 m too high, understating POD.
    """
    terrain = _Terrain(elev_m=1000.0, undulation=30.0)
    # Ellipsoidal GPS altitude for a true orthometric 1020 m.
    images, fgs = _mission(asl=1020.0 + 30.0, agl=120.0)

    result = _service(terrain).calculate(images)

    assert result.image_count == 5
    assert result.altitude_anchor_m == pytest.approx(900.0)
    assert result.altitude_anchor_reason == 'ok'
    assert all(fg.cam_elev_m == pytest.approx(1020.0) for fg in fgs)
    assert result.altitude_source_counts == {'anchor': 5}


def test_anchor_covers_frames_that_have_no_gps_altitude():
    """The anchor is mission-level, so frames missing ASL are corrected too."""
    terrain = _Terrain(elev_m=1000.0, undulation=30.0)
    images, fgs = _mission(count=4, asl=1020.0 + 30.0, agl=120.0)
    bare_image, bare_fg = _frame(asl=None, agl=120.0, name='bare')
    images.append(bare_image)

    result = _service(terrain).calculate(images)

    assert result.altitude_source_counts == {'anchor': 5}
    assert bare_fg.cam_elev_m == pytest.approx(1020.0)
    assert all(fg.cam_elev_m == pytest.approx(1020.0) for fg in fgs)


def test_anchor_uses_the_median_so_a_single_bad_fix_does_not_move_it():
    terrain = _Terrain(elev_m=1000.0, undulation=30.0)
    images, _ = _mission(count=5, asl=1050.0, agl=120.0)
    outlier, _ = _frame(asl=1050.0 + 9.0, agl=120.0, name='outlier')
    images.append(outlier)

    result = _service(terrain).calculate(images)

    assert result.altitude_anchor_reason == 'ok'
    assert result.altitude_anchor_m == pytest.approx(900.0)


# --- the two rejections (Finding 1) -----------------------------------------

def test_datum_error_putting_the_flight_underground_is_rejected():
    """A datum offset big enough to be non-physical is caught and falls back."""
    terrain = _Terrain(elev_m=1000.0, undulation=200.0)
    # (1150 - 200) - 120 = 830 m takeoff, which puts the flight 50 m below ground.
    images, fgs = _mission(asl=1150.0, agl=120.0)

    result = _service(terrain).calculate(images)

    assert result.altitude_anchor_m is None
    assert result.altitude_anchor_reason == 'implausible_agl'
    assert result.altitude_source_counts == {'agl_nadir': 5}
    # Falls back to the historical rule rather than projecting from a bad datum.
    assert all(fg.cam_elev_m == pytest.approx(1120.0) for fg in fgs)


def test_a_modest_datum_offset_is_not_detected_and_is_reported_instead():
    """Documents a real limitation rather than implying protection that is absent.

    A constant offset leaves the spread untouched and is indistinguishable from
    a genuine launch elevation, so a ~30 m mismatch is accepted. The resolved
    anchor is surfaced so it can be checked against the known launch elevation.
    """
    terrain = _Terrain(elev_m=1000.0, undulation=-25.0)
    images, _ = _mission(asl=1020.0, agl=120.0)

    result = _service(terrain).calculate(images)

    assert result.altitude_anchor_reason == 'ok'
    # 25 m high: the true takeoff was 900 m, not 925 m.
    assert result.altitude_anchor_m == pytest.approx(925.0)
    assert result.stats['altitude_anchor'] == {'elevation_m': pytest.approx(925.0),
                                               'reason': 'ok'}


def test_incoherent_altitude_chains_are_rejected():
    """GPS altitude and barometric AGL that do not track each other are unusable."""
    terrain = _Terrain(elev_m=1000.0, undulation=30.0)
    images = []
    for i, asl in enumerate([1050.0, 1090.0, 1010.0, 1075.0, 1120.0]):
        images.append(_frame(asl=asl, agl=120.0, name=f"f{i}")[0])

    result = _service(terrain).calculate(images)

    assert result.altitude_anchor_m is None
    assert result.altitude_anchor_reason == 'incoherent'
    assert result.altitude_source_counts == {'agl_nadir': 5}


def test_relief_alone_never_rejects_the_anchor():
    """Terrain far from takeoff elevation must NOT read as a datum error.

    This is the trap in a per-frame cross-check: the divergence it would see
    here is exactly the correction being applied.
    """
    # Flying 250 m above the terrain, which sits 250 m above launch.
    terrain = _Terrain(elev_m=1250.0, undulation=30.0)
    images, fgs = _mission(asl=1500.0 + 30.0, agl=500.0)

    result = _service(terrain).calculate(images)

    assert result.altitude_anchor_m == pytest.approx(1000.0)
    assert result.altitude_anchor_reason == 'ok'
    assert all(fg.cam_elev_m == pytest.approx(1500.0) for fg in fgs)


# --- fallbacks --------------------------------------------------------------

def test_falls_back_without_gps_altitude():
    terrain = _Terrain(elev_m=1000.0, undulation=30.0)
    images, fgs = _mission(asl=None, agl=120.0)

    result = _service(terrain).calculate(images)

    assert result.altitude_anchor_reason == 'insufficient_samples'
    assert all(fg.cam_elev_m == pytest.approx(1120.0) for fg in fgs)
    assert result.altitude_source_counts == {'agl_nadir': 5}


def test_falls_back_when_the_geoid_grid_is_unavailable():
    """A missing undulation must not be read as 0 m — that is a ~30 m datum error."""
    terrain = _Terrain(elev_m=1000.0, undulation=None)
    images, fgs = _mission(asl=1050.0, agl=120.0)

    result = _service(terrain).calculate(images)

    assert result.altitude_anchor_reason == 'insufficient_samples'
    assert all(fg.cam_elev_m == pytest.approx(1120.0) for fg in fgs)


def test_falls_back_when_terrain_service_has_no_geoid_api():
    terrain = _NoGeoidTerrain(elev_m=1000.0)
    images, fgs = _mission(asl=1050.0, agl=120.0)

    result = _service(terrain).calculate(images)

    assert result.altitude_source_counts == {'agl_nadir': 5}
    assert all(fg.cam_elev_m == pytest.approx(1120.0) for fg in fgs)


def test_too_few_frames_to_validate_falls_back():
    terrain = _Terrain(elev_m=1000.0, undulation=30.0)
    image, fg = _frame(asl=1050.0, agl=120.0)

    result = _service(terrain).calculate([image])

    assert result.altitude_anchor_reason == 'insufficient_samples'
    assert fg.cam_elev_m == pytest.approx(1120.0)


def test_custom_altitude_override_bypasses_the_anchor():
    """An explicit AGL is an assertion about height above the ground below."""
    terrain = _Terrain(elev_m=1000.0, undulation=30.0)
    images, fgs = _mission(asl=1050.0, agl=120.0)

    result = _service(terrain, custom_altitude_ft=400.0).calculate(images)

    assert result.altitude_source_counts == {'agl_override': 5}
    assert all(fg.cam_elev_m == pytest.approx(1120.0) for fg in fgs)
    # Override frames cannot inform a takeoff elevation either.
    assert result.altitude_anchor_m is None


def test_wingtra_per_image_agl_override_bypasses_the_anchor():
    terrain = _Terrain(elev_m=1000.0, undulation=30.0)
    images, fgs = _mission(asl=1020.0 + 30.0, agl=120.0)
    images[0]['wingtra_agl_ft'] = 390.0

    result = _service(terrain).calculate(images)

    assert result.altitude_source_counts == {'anchor': 4, 'agl_override': 1}
    assert fgs[0].cam_elev_m == pytest.approx(1120.0)
    assert fgs[1].cam_elev_m == pytest.approx(1020.0)


def test_frame_resolving_under_the_terrain_falls_back():
    """Per-frame guard: ground above the anchored camera means the anchor or the
    DEM is wrong at this frame, so it reverts to the height above nadir."""
    svc = _service(_Terrain())

    cam_z, source = svc._resolve_cam_elev(
        nadir_elev=1000.0, reported_agl=3.0, agl_is_override=False, anchor=995.0)

    assert source == 'agl_nadir'
    assert cam_z == pytest.approx(1003.0)


# --- grid sizing (Finding 3) ------------------------------------------------

def test_grid_is_sized_once_when_a_point_lookup_is_available():
    """The corrected AGL comes from a cache-backed point lookup, so the frame
    grid is sized right the first time — no second DEM sample per frame."""
    terrain = _Terrain(elev_m=1250.0, undulation=30.0)
    images, fgs = _mission(count=3, asl=1500.0 + 30.0, agl=500.0)

    result = _service(terrain).calculate(images)

    assert result.image_count == 3
    assert len(terrain.specs) == 3, "expected exactly one DEM sample per frame"
    # Sized for the true 250 m above ground, not the reported 500 m.
    assert all(fg.agl_m == pytest.approx(250.0) for fg in fgs)


def test_grid_is_re_sampled_when_no_point_lookup_is_available():
    """Safety net: without get_elevation the grid is sized from the reported AGL,
    so the large correction still has to trigger one re-sample per frame."""
    terrain = _NoPointTerrain(elev_m=1250.0, undulation=30.0)
    images, fgs = _mission(count=3, asl=1500.0 + 30.0, agl=500.0)

    result = _service(terrain).calculate(images)

    assert result.image_count == 3
    assert len(terrain.specs) == 6, "expected a re-sample after the AGL correction"
    assert all(fg.agl_m == pytest.approx(250.0) for fg in fgs)


# --- bookkeeping ------------------------------------------------------------

def test_geoid_undulation_is_memoised_across_frames():
    terrain = _Terrain(elev_m=1000.0, undulation=30.0)
    images, _ = _mission(count=5, asl=1050.0, agl=120.0)

    _service(terrain).calculate(images)

    assert len(terrain.geoid_calls) == 1


def test_a_transient_geoid_failure_is_not_memoised():
    """The EGM96 grid loads lazily; a first-call failure must not poison the run."""
    terrain = _FlakyGeoidTerrain(elev_m=1000.0, undulation=30.0)
    images, fgs = _mission(count=5, asl=1020.0 + 30.0, agl=120.0)

    result = _service(terrain).calculate(images)

    assert result.altitude_anchor_m == pytest.approx(900.0)
    assert result.altitude_source_counts == {'anchor': 5}
    assert all(fg.cam_elev_m == pytest.approx(1020.0) for fg in fgs)


def test_disagreement_is_counted_independently_of_the_re_sample_threshold(caplog):
    """A 250 m correction on a 500 m reported AGL clears the reporting bar even
    though it is only 50% of it — the counter must not inherit that ratio."""
    terrain = _Terrain(elev_m=1250.0, undulation=30.0)
    images, _ = _mission(count=3, asl=1500.0 + 30.0, agl=500.0)

    with caplog.at_level('INFO'):
        _service(terrain).calculate(images)

    assert any("3 frame(s) had a true height" in r.message for r in caplog.records)


def test_altitude_fields_default_to_none_on_an_empty_run():
    """Back-compat: consumers reading the new fields must tolerate no frames."""
    result = _service(_Terrain()).calculate([])

    assert result.image_count == 0
    assert result.altitude_source_counts is None
    assert result.altitude_anchor_m is None
    assert result.altitude_anchor_reason is None
