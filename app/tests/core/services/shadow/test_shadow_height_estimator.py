"""Tests for ShadowHeightEstimator.

AOIService and pysolar are stubbed so each test exercises only the
geometry inside the estimator. The integration with real EXIF/DEM/sun
data is verified by the smoke test against a known capture.
"""

import math
from datetime import datetime, timezone
from typing import Optional, Tuple

import piexif
import pytest
import utm

import core.services.shadow.ShadowHeightEstimator as she_module
from core.services.image.AOIService import AOIGPSResult
from core.services.shadow.ShadowHeightEstimator import (
    ShadowHeightEstimator,
    ShadowHeightResult,
)


# El Dorado Hills, CA — used as the anchor location for synthetic scenes.
ANCHOR_LAT = 38.685
ANCHOR_LON = -121.082

# Anchor in UTM so test scenes can round-trip exactly through the same
# projection the estimator uses (utm.from_latlon). Avoids sub-degree
# azimuth drift from a sphere-vs-ellipsoid mismatch.
_ANCHOR_EAST, _ANCHOR_NORTH, _ANCHOR_ZONE_NO, _ANCHOR_ZONE_LETTER = utm.from_latlon(
    ANCHOR_LAT, ANCHOR_LON
)


@pytest.fixture(autouse=True)
def stub_exif(monkeypatch):
    """Make EXIF reads return a canned GPS-stamped exif dict."""

    def fake_exif(_path):
        return {
            '0th': {},
            'Exif': {},
            'GPS': {
                piexif.GPSIFD.GPSDateStamp: b'2025:06:15',
                piexif.GPSIFD.GPSTimeStamp: ((19, 1), (30, 1), (0, 1)),
            },
        }

    monkeypatch.setattr(
        she_module.MetaDataHelper, 'get_exif_data_piexif', fake_exif
    )


class _FakeImageService:
    """Mimics the slice of ImageService that the sigma estimator touches."""

    def __init__(self):
        # Real-ish drone optics: 1/2.3" sensor, 24mm equiv, 4000 px wide.
        self.img_array = None

    def get_camera_intrinsics(self):
        return None  # forces estimator to fall back to its 1 m sigma default


class _FakeAOIService:
    """Returns canned AOIGPSResult per pixel; never touches disk or EXIF."""

    def __init__(self, scene):
        self._scene = scene
        self.image_service = _FakeImageService()

    def estimate_aoi_gps(self, _image, aoi, **_):
        return self._scene.project(aoi['center'])


class _Scene:
    """Translates pixel clicks into (lat, lon, elev) ground positions.

    The "shadow geometry" is defined directly in metres relative to the
    anchor; pixels are just keys into a dict of points the test sets up.
    """

    def __init__(
        self,
        points: dict,
        elevation_source: str = 'terrain',
        terrain_resolution_m: float = 1.0,
        effective_agl_m: float = 100.0,
    ):
        self._points = points
        self._source = elevation_source
        self._res = terrain_resolution_m
        self._agl = effective_agl_m

    def project(self, pixel) -> Optional[AOIGPSResult]:
        if pixel not in self._points:
            return None
        east_m, north_m, elev_m = self._points[pixel]
        lat, lon = utm.to_latlon(
            _ANCHOR_EAST + east_m,
            _ANCHOR_NORTH + north_m,
            _ANCHOR_ZONE_NO,
            _ANCHOR_ZONE_LETTER,
        )
        return AOIGPSResult(
            latitude=lat,
            longitude=lon,
            elevation_source=self._source,
            terrain_elevation_m=elev_m if self._source == 'terrain' else None,
            effective_agl_m=self._agl,
            terrain_resolution_m=self._res if self._source == 'terrain' else None,
        )


def _install(monkeypatch, scene: _Scene, sun_elev_deg: float, sun_az_deg: float):
    """Patch the AOIService class and pysolar wrapper used by the estimator."""

    def fake_aoi_service(_image, *args, **kwargs):
        return _FakeAOIService(scene)

    def fake_solar(_lat, _lon, _utc):
        return sun_elev_deg, sun_az_deg

    monkeypatch.setattr(she_module, 'AOIService', fake_aoi_service)
    monkeypatch.setattr(she_module, 'get_solar_position', fake_solar)


# ---------------------------------------------------------------------------
# Flat-terrain geometry
# ---------------------------------------------------------------------------

def test_flat_ground_45deg_sun_yields_height_equal_to_shadow(monkeypatch):
    """alpha=45° -> H = d_h."""
    # Sun due east (az=90°) -> shadow points due west; base east of tip by 2 m.
    base = (1, 1)
    tip = (2, 2)
    scene = _Scene({
        base: (0.0, 0.0, 100.0),
        tip:  (-2.0, 0.0, 100.0),  # 2 m west of base
    })
    _install(monkeypatch, scene, sun_elev_deg=45.0, sun_az_deg=90.0)

    result = ShadowHeightEstimator().estimate(
        {'path': '/fake'}, base_px=base, tip_px=tip
    )
    assert result.confidence in ('ok', 'warning'), result.rejection_reason
    assert result.height_m == pytest.approx(2.0, abs=0.02)
    assert result.elev_delta_m == pytest.approx(0.0, abs=0.01)
    assert result.horizontal_dist_m == pytest.approx(2.0, abs=0.02)


def test_flat_ground_30deg_sun(monkeypatch):
    """alpha=30°, d_h=sqrt(3) -> H = 1 m."""
    base = ('b',)
    tip = ('t',)
    scene = _Scene({
        base: (0.0, 0.0, 50.0),
        tip:  (0.0, -math.sqrt(3.0), 50.0),  # shadow extends south
    })
    # Sun due north (az=0) -> shadow points south (expected az 180).
    _install(monkeypatch, scene, sun_elev_deg=30.0, sun_az_deg=0.0)

    result = ShadowHeightEstimator().estimate(
        {'path': '/fake'}, base_px=base, tip_px=tip
    )
    assert result.confidence == 'ok'
    assert result.height_m == pytest.approx(1.0, abs=0.02)


# ---------------------------------------------------------------------------
# Sloping-terrain correction
# ---------------------------------------------------------------------------

def test_uphill_slope_adds_to_height(monkeypatch):
    """Tip uphill (delta_h > 0) -> H exceeds the flat-ground estimate."""
    base = ('b',)
    tip = ('t',)
    # Shadow tip is 4 m west and 1 m higher than base.
    scene = _Scene({
        base: (0.0, 0.0, 100.0),
        tip:  (-4.0, 0.0, 101.0),
    })
    _install(monkeypatch, scene, sun_elev_deg=45.0, sun_az_deg=90.0)

    result = ShadowHeightEstimator().estimate(
        {'path': '/fake'}, base_px=base, tip_px=tip
    )
    assert result.confidence == 'ok'
    # H = 1 (slope) + 4 * tan(45) = 5 m
    assert result.height_m == pytest.approx(5.0, abs=0.02)
    assert result.elev_delta_m == pytest.approx(1.0, abs=0.01)


def test_downhill_slope_subtracts_from_height(monkeypatch):
    """Tip downhill (delta_h < 0) -> H less than the flat-ground estimate."""
    base = ('b',)
    tip = ('t',)
    scene = _Scene({
        base: (0.0, 0.0, 100.0),
        tip:  (-4.0, 0.0, 99.0),
    })
    _install(monkeypatch, scene, sun_elev_deg=45.0, sun_az_deg=90.0)

    result = ShadowHeightEstimator().estimate(
        {'path': '/fake'}, base_px=base, tip_px=tip
    )
    assert result.confidence == 'ok'
    # H = -1 + 4 * tan(45) = 3 m
    assert result.height_m == pytest.approx(3.0, abs=0.02)


# ---------------------------------------------------------------------------
# Confidence gates
# ---------------------------------------------------------------------------

def test_azimuth_within_5deg_is_ok(monkeypatch):
    """Drawn line within tolerance of expected shadow azimuth -> ok."""
    base = ('b',)
    tip = ('t',)
    # Sun azimuth 90 -> expected shadow azimuth 270 (west).
    # Place tip 2 m west, no offset -> measured az ~270.
    scene = _Scene({
        base: (0.0, 0.0, 100.0),
        tip:  (-2.0, 0.0, 100.0),
    })
    _install(monkeypatch, scene, sun_elev_deg=45.0, sun_az_deg=90.0)

    result = ShadowHeightEstimator().estimate(
        {'path': '/fake'}, base_px=base, tip_px=tip
    )
    assert result.confidence == 'ok'
    assert abs(result.delta_az_deg) < 1.0


def test_azimuth_between_5_and_15_is_warning(monkeypatch):
    """8° off expected -> warning, but still computes a height."""
    base = ('b',)
    tip = ('t',)
    # 8° offset from due-west: rotate (-2, 0) by 8° CCW about origin.
    theta = math.radians(8.0)
    dx = -2.0 * math.cos(theta) - 0.0 * math.sin(theta)
    dy = -2.0 * math.sin(theta) + 0.0 * math.cos(theta)
    scene = _Scene({
        base: (0.0, 0.0, 100.0),
        tip:  (dx, dy, 100.0),
    })
    _install(monkeypatch, scene, sun_elev_deg=45.0, sun_az_deg=90.0)

    result = ShadowHeightEstimator().estimate(
        {'path': '/fake'}, base_px=base, tip_px=tip
    )
    assert result.confidence == 'warning'
    assert result.height_m is not None
    assert 5.0 < abs(result.delta_az_deg) <= 15.0


def test_azimuth_off_by_90deg_rejects(monkeypatch):
    """Drawn perpendicular to expected shadow direction -> reject."""
    base = ('b',)
    tip = ('t',)
    # Sun east, expected shadow west; draw tip north of base instead.
    scene = _Scene({
        base: (0.0, 0.0, 100.0),
        tip:  (0.0, 2.0, 100.0),
    })
    _install(monkeypatch, scene, sun_elev_deg=45.0, sun_az_deg=90.0)

    result = ShadowHeightEstimator().estimate(
        {'path': '/fake'}, base_px=base, tip_px=tip
    )
    assert result.confidence == 'rejected'
    assert 'shadow direction' in (result.rejection_reason or '').lower()
    # The dialog uses this flag to surface a "Use anyway" button.
    assert result.azimuth_override_available is True


def test_azimuth_override_demotes_rejection_to_warning(monkeypatch):
    """With override on, an off-azimuth click yields a warning, not a reject."""
    base = ('b',)
    tip = ('t',)
    # Same off-direction geometry as the rejection test above.
    scene = _Scene({
        base: (0.0, 0.0, 100.0),
        tip:  (0.0, 2.0, 100.0),
    })
    _install(monkeypatch, scene, sun_elev_deg=45.0, sun_az_deg=90.0)

    result = ShadowHeightEstimator().estimate(
        {'path': '/fake'}, base_px=base, tip_px=tip,
        allow_azimuth_override=True,
    )
    assert result.confidence == 'warning'
    assert result.height_m is not None
    assert any('override accepted' in w.lower() for w in result.warnings)


def test_azimuth_override_only_relaxes_azimuth(monkeypatch):
    """Override must NOT rescue a sun-too-low or other gate failure."""
    base = ('b',)
    tip = ('t',)
    scene = _Scene({
        base: (0.0, 0.0, 100.0),
        tip:  (-2.0, 0.0, 100.0),  # aligned with expected shadow direction
    })
    _install(monkeypatch, scene, sun_elev_deg=3.0, sun_az_deg=90.0)

    result = ShadowHeightEstimator().estimate(
        {'path': '/fake'}, base_px=base, tip_px=tip,
        allow_azimuth_override=True,
    )
    assert result.confidence == 'rejected'
    assert 'too low' in (result.rejection_reason or '').lower()


def test_sun_too_low_rejects(monkeypatch):
    scene = _Scene({
        ('b',): (0.0, 0.0, 100.0),
        ('t',): (-2.0, 0.0, 100.0),
    })
    _install(monkeypatch, scene, sun_elev_deg=3.0, sun_az_deg=90.0)

    result = ShadowHeightEstimator().estimate(
        {'path': '/fake'}, base_px=('b',), tip_px=('t',)
    )
    assert result.confidence == 'rejected'
    assert 'too low' in (result.rejection_reason or '').lower()


def test_sun_too_high_rejects(monkeypatch):
    scene = _Scene({
        ('b',): (0.0, 0.0, 100.0),
        ('t',): (-2.0, 0.0, 100.0),
    })
    _install(monkeypatch, scene, sun_elev_deg=88.0, sun_az_deg=90.0)

    result = ShadowHeightEstimator().estimate(
        {'path': '/fake'}, base_px=('b',), tip_px=('t',)
    )
    assert result.confidence == 'rejected'
    assert 'overhead' in (result.rejection_reason or '').lower()


def test_degenerate_clicks_reject(monkeypatch):
    """Same projected ground point twice -> reject."""
    p = ('p',)
    scene = _Scene({p: (0.0, 0.0, 100.0)})
    _install(monkeypatch, scene, sun_elev_deg=45.0, sun_az_deg=90.0)

    result = ShadowHeightEstimator().estimate(
        {'path': '/fake'}, base_px=p, tip_px=p
    )
    assert result.confidence == 'rejected'
    assert 'same ground point' in (result.rejection_reason or '').lower()


def test_reversed_click_order_rejects(monkeypatch):
    """If base is east of tip but sun is east, the implied shadow goes east -> mismatch."""
    base = ('b',)
    tip = ('t',)
    # Sun east (az=90), expected shadow points west (az=270).
    # User swapped clicks: "base" is actually the shadow tip, "tip" is the object base.
    # measured az = base->tip direction = east (az=90) — 180° off expected.
    scene = _Scene({
        base: (0.0, 0.0, 100.0),
        tip:  (2.0, 0.0, 100.0),
    })
    _install(monkeypatch, scene, sun_elev_deg=45.0, sun_az_deg=90.0)

    result = ShadowHeightEstimator().estimate(
        {'path': '/fake'}, base_px=base, tip_px=tip
    )
    assert result.confidence == 'rejected'


# ---------------------------------------------------------------------------
# Time / EXIF handling
# ---------------------------------------------------------------------------

def test_unresolvable_time_rejects(monkeypatch):
    monkeypatch.setattr(
        she_module.MetaDataHelper,
        'get_exif_data_piexif',
        lambda _p: {'0th': {}, 'GPS': {}, 'Exif': {}},
    )
    scene = _Scene({
        ('b',): (0.0, 0.0, 100.0),
        ('t',): (-2.0, 0.0, 100.0),
    })
    _install(monkeypatch, scene, sun_elev_deg=45.0, sun_az_deg=90.0)

    result = ShadowHeightEstimator().estimate(
        {'path': '/fake'}, base_px=('b',), tip_px=('t',)
    )
    assert result.confidence == 'rejected'
    assert 'capture time' in (result.rejection_reason or '').lower()


def test_aoi_projection_failure_rejects(monkeypatch):
    """If AOIService can't project (e.g. missing metadata) -> reject."""
    scene = _Scene({('b',): (0.0, 0.0, 100.0)})  # tip not in scene
    _install(monkeypatch, scene, sun_elev_deg=45.0, sun_az_deg=90.0)

    result = ShadowHeightEstimator().estimate(
        {'path': '/fake'}, base_px=('b',), tip_px=('t',)
    )
    assert result.confidence == 'rejected'
    assert 'project' in (result.rejection_reason or '').lower()


def test_flat_terrain_warning_when_no_dem(monkeypatch):
    """No DEM -> estimator falls back to flat ground and warns."""
    scene = _Scene(
        {
            ('b',): (0.0, 0.0, 0.0),
            ('t',): (-2.0, 0.0, 0.0),
        },
        elevation_source='flat',
    )
    _install(monkeypatch, scene, sun_elev_deg=45.0, sun_az_deg=90.0)

    result = ShadowHeightEstimator().estimate(
        {'path': '/fake'}, base_px=('b',), tip_px=('t',)
    )
    assert result.confidence == 'warning'
    assert result.height_m == pytest.approx(2.0, abs=0.02)
    assert any('flat terrain' in w.lower() for w in result.warnings)


# ---------------------------------------------------------------------------
# Uncertainty propagation
# ---------------------------------------------------------------------------

def test_sigma_is_positive_and_reasonable(monkeypatch):
    """σ_H should be finite, positive, and small compared to H for a clean case."""
    scene = _Scene({
        ('b',): (0.0, 0.0, 100.0),
        ('t',): (-2.0, 0.0, 100.0),
    })
    _install(monkeypatch, scene, sun_elev_deg=45.0, sun_az_deg=90.0)

    result = ShadowHeightEstimator().estimate(
        {'path': '/fake'}, base_px=('b',), tip_px=('t',)
    )
    assert result.sigma_m is not None
    assert 0.0 < result.sigma_m < result.height_m  # noise smaller than signal


def test_sigma_grows_toward_zenith(monkeypatch):
    """sec²α blows up as the sun nears zenith -> absolute σ_H grows there.

    (Counter-intuitive: low sun gives a small absolute σ but a huge
    *relative* σ because H itself shrinks toward zero. The rejection at
    α < 5° is about that ratio, not the absolute sigma.)
    """
    scene = _Scene({
        ('b',): (0.0, 0.0, 100.0),
        ('t',): (-2.0, 0.0, 100.0),
    })

    _install(monkeypatch, scene, sun_elev_deg=45.0, sun_az_deg=90.0)
    mid = ShadowHeightEstimator().estimate(
        {'path': '/fake'}, base_px=('b',), tip_px=('t',)
    )

    _install(monkeypatch, scene, sun_elev_deg=80.0, sun_az_deg=90.0)
    high = ShadowHeightEstimator().estimate(
        {'path': '/fake'}, base_px=('b',), tip_px=('t',)
    )

    assert high.sigma_m > mid.sigma_m


# ---------------------------------------------------------------------------
# Terrain-preference propagation
# ---------------------------------------------------------------------------

def _install_recording(monkeypatch, scene: _Scene, sun_elev_deg: float, sun_az_deg: float):
    """Like _install, but records the use_terrain kwarg of each projection."""
    recorded = []

    class _RecordingAOIService(_FakeAOIService):
        def estimate_aoi_gps(self, _image, aoi, *args, **kwargs):
            recorded.append(kwargs.get('use_terrain', 'MISSING'))
            return self._scene.project(aoi['center'])

    monkeypatch.setattr(
        she_module, 'AOIService', lambda _image, *a, **k: _RecordingAOIService(scene)
    )
    monkeypatch.setattr(
        she_module, 'get_solar_position', lambda *_: (sun_elev_deg, sun_az_deg)
    )
    return recorded


def test_use_terrain_false_propagates_to_both_projections(monkeypatch):
    """use_terrain=False reaches both ground projections and keeps the flat warning."""
    base = ('b',)
    tip = ('t',)
    scene = _Scene({
        base: (0.0, 0.0, 0.0),
        tip:  (-2.0, 0.0, 0.0),
    }, elevation_source='flat')
    recorded = _install_recording(monkeypatch, scene, sun_elev_deg=45.0, sun_az_deg=90.0)

    result = ShadowHeightEstimator().estimate(
        {'path': '/fake'}, base_px=base, tip_px=tip, use_terrain=False
    )

    assert recorded == [False, False]
    assert result.confidence in ('ok', 'warning')
    assert any('flat terrain' in w.lower() for w in result.warnings)


def test_use_terrain_defaults_to_true(monkeypatch):
    """Omitting use_terrain projects with terrain enabled (backward compatible)."""
    base = ('b',)
    tip = ('t',)
    scene = _Scene({
        base: (0.0, 0.0, 100.0),
        tip:  (-2.0, 0.0, 100.0),
    })
    recorded = _install_recording(monkeypatch, scene, sun_elev_deg=45.0, sun_az_deg=90.0)

    result = ShadowHeightEstimator().estimate(
        {'path': '/fake'}, base_px=base, tip_px=tip
    )

    assert recorded == [True, True]
    assert result.confidence in ('ok', 'warning')
