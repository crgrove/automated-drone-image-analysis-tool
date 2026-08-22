"""The contract AOI-in-neighbouring-images rests on: the inverse is an inverse.

The feature computes an AOI's GPS with AOIService (forward: pixel -> ground),
then asks AOINeighborService where that GPS falls in each candidate image
(inverse: ground -> pixel). The two are only correct as a pair, and nothing
used to check that they were. They drifted: the forward path gained gimbal-roll
support and terrain-corrected AGL, the inverse got neither, and each omission
put the AOI hundreds or thousands of pixels from where it actually appears --
far outside the ~200 px thumbnail, so every crop showed unrelated ground with a
red circle confidently drawn on it. No error was raised and no test failed.

These tests close the loop numerically. A tolerance of 1 px is not
aspirational: the inversion is analytic, so anything above floating-point noise
means the two models disagree.
"""

import math

import pytest

from core.services.image.AOIService import AOIService
from core.services.image.AOINeighborService import AOINeighborService

# A DJI-class nadir rig: 5472x3648 at 8.8 mm on a 13.2x8.8 mm sensor.
WIDTH, HEIGHT = 5472, 3648
FOCAL_MM, SENSOR_W_MM, SENSOR_H_MM = 8.8, 13.2, 8.8
DRONE_LAT, DRONE_LON = 32.0, -97.0

TOLERANCE_PX = 1.0


def _service():
    """An AOINeighborService without the LoggerService its __init__ builds."""
    return AOINeighborService.__new__(AOINeighborService)


def _coverage_info(yaw, pitch, altitude, roll=0.0, roll_axis=None):
    """The metadata dict get_image_coverage_info produces for this camera."""
    return {
        'center_lat': DRONE_LAT,
        'center_lon': DRONE_LON,
        'yaw': yaw,
        'pitch': pitch,
        'roll': roll,
        'roll_axis_azimuth': roll_axis,
        'altitude': altitude,
        'width': WIDTH,
        'height': HEIGHT,
        'focal_mm': FOCAL_MM,
        'sensor_w_mm': SENSOR_W_MM,
        'sensor_h_mm': SENSOR_H_MM,
        'fov_alignment': None,
    }


def _round_trip_error_px(pixel, yaw, pitch, altitude, roll=0.0, roll_axis=None):
    """Project *pixel* to ground and back; return the pixel distance."""
    u, v = pixel
    ground = AOIService._calculate_ground_position(
        DRONE_LAT, DRONE_LON, u, v, WIDTH / 2.0, HEIGHT / 2.0, WIDTH, HEIGHT,
        FOCAL_MM, SENSOR_W_MM, SENSOR_H_MM, altitude, pitch, yaw, roll,
        roll_axis_azimuth_deg=roll_axis,
    )
    assert ground is not None, "forward projection found no ground intersection"

    back = _service().gps_to_pixel(
        ground[0], ground[1], _coverage_info(yaw, pitch, altitude, roll, roll_axis)
    )
    assert back is not None, "inverse projection rejected its own forward result"
    return math.hypot(back[0] - u, back[1] - v)


@pytest.mark.parametrize("pixel", [
    (WIDTH / 2, HEIGHT / 2),   # centre
    (4322, 471),               # the AOI from the sample dataset
    (10, 10),                  # corners, where any model error is largest
    (WIDTH - 10, HEIGHT - 10),
])
@pytest.mark.parametrize("yaw", [0.0, 45.0, 180.0, 271.5, 359.9])
def test_nadir_round_trip_is_exact(pixel, yaw):
    assert _round_trip_error_px(pixel, yaw, -90.0, 100.0) < TOLERANCE_PX


@pytest.mark.parametrize("pitch", [-80.0, -60.0, -45.0, -30.0])
def test_oblique_round_trip_is_exact(pitch):
    """Oblique imagery is where a wrong camera frame shows up first."""
    assert _round_trip_error_px((4322, 471), 45.0, pitch, 120.0) < TOLERANCE_PX


@pytest.mark.parametrize("roll", [22.5, -22.5, 40.0])
def test_gimbal_roll_round_trip_is_exact(roll):
    """Regression: the inverse never read roll, so a WALDO pod tilt was dropped.

    The forward path applied a Rodrigues roll and the inverse did not, which
    left the AOI ~1500 px away at +-22.5 degrees -- seven thumbnails' worth --
    with nothing reporting a problem.
    """
    assert _round_trip_error_px((4322, 471), 45.0, -90.0, 100.0, roll=roll) < TOLERANCE_PX


def test_roll_about_the_flight_axis_round_trips():
    """WALDO processor >= 6 stamps roll about the flight axis, not the gimbal's."""
    error = _round_trip_error_px(
        (4322, 471), 45.0, -60.0, 120.0, roll=-22.5, roll_axis=310.0
    )
    assert error < TOLERANCE_PX


def test_roll_actually_changes_the_projection():
    """Guard the guard: the roll tests would pass trivially if roll were ignored.

    If a future change drops roll from BOTH paths the round trip still closes,
    so this pins that roll is genuinely part of the model.
    """
    service = _service()
    ground = AOIService._calculate_ground_position(
        DRONE_LAT, DRONE_LON, 4322, 471, WIDTH / 2.0, HEIGHT / 2.0, WIDTH, HEIGHT,
        FOCAL_MM, SENSOR_W_MM, SENSOR_H_MM, 100.0, -90.0, 45.0, 22.5,
    )
    without_roll = service.gps_to_pixel(
        ground[0], ground[1], _coverage_info(45.0, -90.0, 100.0, roll=0.0)
    )
    assert without_roll is not None
    assert math.hypot(without_roll[0] - 4322, without_roll[1] - 471) > 100.0


def test_inverse_rejects_a_point_behind_the_camera():
    """A GPS far behind an oblique camera has no valid forward ray."""
    service = _service()
    # 2 km due south of a camera looking north at 30 degrees below horizontal.
    behind_lat = DRONE_LAT - 2000.0 / 111320.0
    result = service.gps_to_pixel(
        behind_lat, DRONE_LON, _coverage_info(0.0, -30.0, 120.0)
    )
    if result is not None:
        # Not rejected outright, but it must not land inside the frame.
        u, v = result
        assert not (0 <= u < WIDTH and 0 <= v < HEIGHT)


# ------------------------- terrain-consistent altitude ---------------------- #


class _Elevation:
    """Stands in for the DEM lookup result, including the resolution the
    forward pass records on its AOIGPSResult."""

    def __init__(self, elevation_m, source='terrain', resolution_m=30.0):
        self.elevation_m = elevation_m
        self.source = source
        self.resolution_m = resolution_m


class _TerrainService:
    """Stands in for TerrainService, including the geoid the DEM path needs.

    Both accessors matter: the altitude selection uses the DEM elevation AND
    the geoid undulation, exactly as AOIService does. A stub with only
    get_elevation makes the service degrade to the unadjusted altitude, which
    looks like a passing test for the wrong reason.
    """

    def __init__(self, elevation, enabled=True, geoid=0.0):
        self._elevation = elevation
        self.enabled = enabled
        self._geoid = geoid

    def get_elevation(self, lat, lon):
        return self._elevation

    def get_geoid_undulation(self, lat, lon):
        return self._geoid


def _patch_terrain(monkeypatch, service):
    import core.services.image.AOINeighborService as module
    monkeypatch.setattr(module, '_get_terrain_service', lambda: service)


def test_altitude_is_measured_to_the_aoi_ground_not_the_cameras(monkeypatch):
    """Regression: the inverse used raw EXIF AGL while the forward used terrain.

    30 m of relief at 100 m AGL moved the AOI ~625 px, which is why the
    originating image did not even project the AOI back onto its own pixel.
    """
    _patch_terrain(monkeypatch, _TerrainService(_Elevation(280.0)))
    coverage = _coverage_info(0.0, -90.0, 100.0)

    adjusted = _service()._terrain_adjusted_altitude(coverage, aoi_terrain_elevation_m=250.0)

    assert adjusted == pytest.approx(130.0)


def test_altitude_is_unchanged_without_an_aoi_elevation(monkeypatch):
    """A flat/no-DEM forward result must leave flat-earth behaviour alone."""
    _patch_terrain(monkeypatch, _TerrainService(_Elevation(280.0)))
    coverage = _coverage_info(0.0, -90.0, 100.0)

    assert _service()._terrain_adjusted_altitude(coverage, None) == 100.0


@pytest.mark.parametrize("terrain", [
    None,
    _TerrainService(_Elevation(None, source='none')),
    _TerrainService(_Elevation(280.0), enabled=False),
])
def test_altitude_degrades_to_unadjusted_when_the_dem_cannot_answer(monkeypatch, terrain):
    """A terrain gap must degrade to today's behaviour, not drop the image."""
    _patch_terrain(monkeypatch, terrain)
    coverage = _coverage_info(0.0, -90.0, 100.0)

    assert _service()._terrain_adjusted_altitude(coverage, 250.0) == 100.0


def test_altitude_is_floored_above_zero(monkeypatch):
    """An AOI on ground above the camera must not produce a non-positive AGL.

    A non-positive AGL has no ground intersection, which would silently drop
    the image from the results rather than place the AOI imprecisely.
    """
    _patch_terrain(monkeypatch, _TerrainService(_Elevation(10.0)))
    coverage = _coverage_info(0.0, -90.0, 100.0)

    assert _service()._terrain_adjusted_altitude(coverage, 250.0) == 1.0


# --------------------- the crop must survive metadata error ----------------- #

def test_edge_margin_does_not_scale_with_the_crop():
    """A wide crop must not start rejecting images that do show the AOI.

    The margin answers "is the AOI really in this frame", which is unrelated
    to how much context the thumbnail shows. It used to be thumbnail_radius//2,
    so widening the crop to cover metadata error would have thrown away every
    hit within half a crop of the edge.
    """
    service = _service()
    service.logger = None
    width, height = WIDTH, HEIGHT
    margin = AOINeighborService.EDGE_MARGIN_PX

    assert margin < 100, "the in-frame test must stay a small fixed margin"
    # A point 120 px from the edge is in frame, whatever the crop width.
    assert service.is_point_in_image(120, 120, width, height, margin)
    assert not service.is_point_in_image(10, 10, width, height, margin)


def test_crop_is_sized_to_positional_uncertainty_not_to_the_aoi():
    """Regression: every thumbnail showed bare ground.

    Adjacent captures disagree about where the same object is by 1.5-4 m of
    real metadata error -- ~110-300 px at a typical 1.33 cm/px GSD. The crop
    was max(100, aoi_radius*2), i.e. 200 px across for a small AOI, covering
    2.7 m of ground: narrower than the error, so the object sat just outside
    almost every thumbnail.
    """
    from core.controllers.images.viewer.neighbor.AOINeighborTrackingController import (
        AOINeighborTrackingController,
    )

    radius = AOINeighborTrackingController.UNCERTAINTY_RADIUS_PX
    gsd_m_per_px = 0.0133
    covered_m = radius * gsd_m_per_px

    assert covered_m >= 4.0, (
        f"a {radius} px crop covers {covered_m:.1f} m; measured inter-image "
        "disagreement reaches ~4 m, so the AOI would fall outside"
    )


# ------------- the two sides must AGREE on which AGL estimate wins ---------- #

_DRONE_GROUND = 1180.0
_AOI_GROUND = 1170.0
_REPORTED_AGL = 100.0
_DRONE_ORTHOMETRIC = 1290.0     # absolute_alt - geoid


class _TwoCellTerrain:
    """A DEM where the camera's cell and the AOI's cell differ by 10 m."""

    enabled = True

    def get_elevation(self, lat, lon):
        at_camera = abs(lat - DRONE_LAT) < 1e-9 and abs(lon - DRONE_LON) < 1e-9
        return _Elevation(_DRONE_GROUND if at_camera else _AOI_GROUND)

    def get_geoid_undulation(self, lat, lon):
        return 0.0


def test_inverse_picks_the_same_agl_estimate_as_the_forward(monkeypatch):
    """Regression: the two sides chose different altitudes on RTK data.

    _select_effective_agl PREFERS the absolute-elevation chain whenever it
    agrees with the terrain-relief chain within tolerance. The forward pass
    therefore used agl_abs (120 m here) while the inverse rebuilt only agl_rel
    (110 m) -- an 8% scale error that put a corner AOI ~300 px away, outside
    the crop, on exactly the datasets whose metadata is most trustworthy.

    On this repo's demo flight the two estimates DISAGREE (77.9 vs 46.5), so
    the forward falls back to relief and the mismatch is invisible; it needs a
    sound geoid/ASL to appear, which is why no real-data check caught it.
    """
    terrain = _TwoCellTerrain()
    aoi_service = AOIService.__new__(AOIService)
    aoi_service.logger = None

    u, v = WIDTH - 10, HEIGHT - 10      # corner: worst case for a scale error
    initial = AOIService._calculate_ground_position(
        DRONE_LAT, DRONE_LON, u, v, WIDTH / 2.0, HEIGHT / 2.0, WIDTH, HEIGHT,
        FOCAL_MM, SENSOR_W_MM, SENSOR_H_MM, _REPORTED_AGL, -90.0, 0.0, 0.0)

    forward = aoi_service._calculate_with_terrain(
        {'path': 'x.jpg'}, {'center': (u, v)}, DRONE_LAT, DRONE_LON,
        initial[0], initial[1], u, v, WIDTH / 2.0, HEIGHT / 2.0, WIDTH, HEIGHT,
        FOCAL_MM, SENSOR_W_MM, SENSOR_H_MM, _REPORTED_AGL, -90.0, 0.0, 0.0,
        terrain, absolute_alt=_DRONE_ORTHOMETRIC, precomputed_geoid=0.0)

    assert forward.effective_agl_m == pytest.approx(120.0), \
        "precondition: the forward pass should prefer the absolute chain here"

    _patch_terrain(monkeypatch, terrain)
    service = _service()
    service.logger = None
    coverage = _coverage_info(0.0, -90.0, _REPORTED_AGL)
    coverage['asl_altitude'] = _DRONE_ORTHOMETRIC
    coverage['altitude'] = service._terrain_adjusted_altitude(
        coverage, forward.terrain_elevation_m)

    assert coverage['altitude'] == pytest.approx(forward.effective_agl_m), \
        "the inverse must select the same AGL estimate as the forward"

    back = service.gps_to_pixel(forward.latitude, forward.longitude, coverage)
    assert back is not None
    assert math.hypot(back[0] - u, back[1] - v) < TOLERANCE_PX


def test_inverse_falls_back_to_relief_without_an_absolute_altitude(monkeypatch):
    """No ASL in the metadata -> the datum-robust estimate, as before."""
    _patch_terrain(monkeypatch, _TwoCellTerrain())
    service = _service()
    service.logger = None
    coverage = _coverage_info(0.0, -90.0, _REPORTED_AGL)
    coverage['asl_altitude'] = None

    adjusted = service._terrain_adjusted_altitude(coverage, _AOI_GROUND)

    assert adjusted == pytest.approx(110.0)
