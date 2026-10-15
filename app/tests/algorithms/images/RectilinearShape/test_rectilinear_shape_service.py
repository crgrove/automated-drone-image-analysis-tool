"""End-to-end tests for RectilinearShapeService.process_image on synthetic frames.

Frames are built with numpy/cv2 from a fixed seed: a filled rectangle of
known physical size on Gaussian or fractal-noise ground. GSD is supplied by
stubbing the service's lookup, so 1 cm/px makes a 60 x 40 cm suitcase a
60 x 40 px rectangle.
"""

import math
import os
from unittest.mock import MagicMock

import cv2
import numpy as np
import pytest

from algorithms.AlgorithmService import AnalysisResult
from algorithms.images.RectilinearShape.services.RectilinearPresets import DEFAULT_OPTIONS, normalize_options
from algorithms.images.RectilinearShape.services.RectilinearShapeService import RectilinearShapeService
from core.services.XmlService import XmlService

FRAME = 300
CENTRE = FRAME / 2


def _gaussian_ground(rng, size=FRAME, sigma=8.0):
    return rng.normal(110, sigma, (size, size)).astype(np.float32)


def _fractal_ground(rng, size=FRAME, amplitude=12.0):
    """Octave-summed noise: large soft blotches like mixed vegetation."""
    ground = np.zeros((size, size), np.float32)
    for octave in range(1, 7):
        cells = 2 ** octave
        layer = rng.normal(0, 1, (cells, cells)).astype(np.float32)
        ground += cv2.resize(layer, (size, size), interpolation=cv2.INTER_CUBIC) * amplitude / octave
    return ground + 110 + rng.normal(0, 3, (size, size)).astype(np.float32)


def _with_rectangle(ground, cx, cy, length, width, angle, value):
    """Blend a slightly blurred filled rectangle into ``ground``."""
    corners = cv2.boxPoints(((cx, cy), (length, width), angle))
    mask = np.zeros(ground.shape, np.uint8)
    cv2.fillPoly(mask, [np.rint(corners * 8).astype(np.int32)], 255, shift=3)
    alpha = cv2.GaussianBlur(mask.astype(np.float32) / 255.0, (0, 0), 0.8)
    return ground * (1.0 - alpha) + value * alpha


def _bgr(gray):
    return cv2.cvtColor(np.clip(gray, 0, 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)


def _service(gsd_cm=1.0, min_area=10, max_area=0, **options):
    service = RectilinearShapeService((255, 0, 0), min_area, max_area, 0, False, options)
    service._resolve_gsd_cm = lambda img, path: (gsd_cm, None)
    return service


def _run(service, img, tmp_path):
    return service.process_image(img, str(tmp_path / 'frame.jpg'), str(tmp_path), str(tmp_path / 'out'))


def _hit(aois, cx, cy, radius):
    return any(math.hypot(a['center'][0] - cx, a['center'][1] - cy) <= radius for a in aois or [])


# --- positives ----------------------------------------------------------------

@pytest.mark.parametrize('ground, contrast, min_hits', [
    ('gaussian', 40, 36),
    ('gaussian', 20, 35),
    ('fractal', 40, 34),
    ('fractal', 25, 28),
])
def test_rectangles_are_found_at_every_rotation(tmp_path, ground, contrast, min_hits):
    """A 60 x 40 cm target at 0-175 degrees in 5 degree steps.

    A hit is an AOI centred within a quarter of the short side of the truth.
    Low contrast on blotchy ground is genuinely ambiguous - the target's
    edge vanishes wherever a blotch matches it - so that case asserts a rate.
    """
    rng = np.random.default_rng(1)
    service = _service()
    hits = 0
    for angle in range(0, 180, 5):
        base = _gaussian_ground(rng) if ground == 'gaussian' else _fractal_ground(rng)
        img = _bgr(_with_rectangle(base, CENTRE, CENTRE, 60, 40, angle, 110 + contrast))
        result = _run(service, img, tmp_path)
        assert result.error_message is None
        hits += _hit(result.areas_of_interest, CENTRE, CENTRE, 0.25 * 40)
    assert hits >= min_hits


def test_aois_carry_a_shape_confidence(tmp_path):
    img = _bgr(_with_rectangle(_gaussian_ground(np.random.default_rng(2)), CENTRE, CENTRE, 60, 40, 25, 160))
    result = _run(_service(), img, tmp_path)
    assert isinstance(result, AnalysisResult)
    assert result.areas_of_interest
    for aoi in result.areas_of_interest:
        assert aoi['score_type'] == 'shape'
        assert isinstance(aoi['confidence'], float)
        assert 0.0 <= aoi['confidence'] <= 100.0
        assert isinstance(aoi['center'][0], int)
    assert result.output_path is not None


@pytest.mark.parametrize('length_cm, width_cm, gsd, options', [
    (40, 25, 1.0, {}),                       # carry-on standing upright
    (75, 48, 1.5, {}),                       # checked bag lying flat
    (215, 145, 2.5, {'target_preset': 'tent_small', 'long_side_cm_min': 200, 'long_side_cm_max': 230,
                     'short_side_cm_min': 130, 'short_side_cm_max': 160}),
])
def test_targets_are_found_across_presets_and_scales(tmp_path, length_cm, width_cm, gsd, options):
    rng = np.random.default_rng(3)
    img = _bgr(_with_rectangle(_gaussian_ground(rng, 400), 200, 200, length_cm / gsd, width_cm / gsd, 35, 150))
    result = _run(_service(gsd, **options), img, tmp_path)
    assert _hit(result.areas_of_interest, 200, 200, 0.25 * width_cm / gsd)


@pytest.mark.parametrize('length_cm, width_cm', [(160, 110), (20, 12)])
def test_rectangles_of_the_wrong_physical_size_are_ignored(tmp_path, length_cm, width_cm):
    rng = np.random.default_rng(4)
    img = _bgr(_with_rectangle(_gaussian_ground(rng, 400), 200, 200, length_cm, width_cm, 20, 150))
    assert not _run(_service(), img, tmp_path).areas_of_interest


def test_a_shape_larger_than_the_batch_max_area_is_still_emitted(tmp_path):
    """The preset governs size; the guide's batch area limits are diagnostic only."""
    img = _bgr(_with_rectangle(_gaussian_ground(np.random.default_rng(5)), CENTRE, CENTRE, 60, 40, 10, 160))
    service = _service(min_area=10, max_area=100)
    service.logger = MagicMock()
    result = _run(service, img, tmp_path)
    assert _hit(result.areas_of_interest, CENTRE, CENTRE, 10)
    assert any('batch area limits' in str(c) for c in service.logger.info.call_args_list)


# --- negatives ----------------------------------------------------------------

def _regular_polygons(rng):
    """Triangles, pentagons and hexagons - straight edges, but no right angles."""
    ground = _gaussian_ground(rng)
    for cx, cy in ((80, 80), (220, 80), (80, 220), (220, 220)):
        sides = int(rng.choice([3, 5, 6]))
        radius = rng.uniform(25, 40)
        angles = rng.uniform(0, 2 * np.pi) + np.arange(sides) * 2 * np.pi / sides
        points = np.stack([cx + radius * np.cos(angles), cy + radius * np.sin(angles)], 1).astype(np.int32)
        cv2.fillPoly(ground, [points], float(rng.uniform(140, 180)))
    return _bgr(cv2.GaussianBlur(ground, (0, 0), 0.8))


def _trail(rng):
    ground = _gaussian_ground(rng)
    angle = math.radians(rng.uniform(0, 180))
    dx, dy = 400 * math.cos(angle), 400 * math.sin(angle)
    cv2.line(ground, (int(CENTRE - dx), int(CENTRE - dy)), (int(CENTRE + dx), int(CENTRE + dy)), 150, 8)
    return _bgr(cv2.GaussianBlur(ground, (0, 0), 0.8))


def _jpeg_blocking(rng):
    yy, xx = np.mgrid[0:FRAME, 0:FRAME]
    smooth = 110 + 30 * np.sin(xx / 40.0 + rng.uniform(0, 3)) * np.cos(yy / 55.0)
    ok, encoded = cv2.imencode('.jpg', _bgr(smooth), [cv2.IMWRITE_JPEG_QUALITY, 30])
    assert ok
    return cv2.imdecode(encoded, cv2.IMREAD_COLOR)


def _block_pattern(rng):
    """Constant 8 x 8 blocks: the axis-aligned, balanced edges JPEG leaves in flat areas."""
    blocks = rng.normal(0, 4, (FRAME // 8 + 1, FRAME // 8 + 1)).astype(np.float32)
    return _bgr(110 + np.kron(blocks, np.ones((8, 8), np.float32))[:FRAME, :FRAME])


@pytest.mark.parametrize('make', [
    lambda rng: _bgr(_gaussian_ground(rng)),
    lambda rng: _bgr(_fractal_ground(rng, amplitude=25)),
    _trail,
    _regular_polygons,
    _jpeg_blocking,
    _block_pattern,
], ids=['gaussian_noise', 'fractal_noise', 'trail', 'regular_polygons', 'jpeg_blocking', 'block_pattern'])
def test_negatives_produce_no_aois(tmp_path, make):
    service = _service()
    for seed in range(3):
        result = _run(service, make(np.random.default_rng(seed)), tmp_path)
        assert result.error_message is None
        assert not result.areas_of_interest, f"seed {seed}: {result.areas_of_interest}"


# --- options ------------------------------------------------------------------

def _several_targets(rng):
    ground = _gaussian_ground(rng, 500)
    for k, (cx, cy) in enumerate(((100, 100), (250, 100), (400, 100), (100, 300), (300, 330))):
        ground = _with_rectangle(ground, cx, cy, 60, 40, 15 * k, 120 + 15 * k)
    return _bgr(ground)


def test_the_top_n_cap_keeps_the_strongest(tmp_path):
    img = _several_targets(np.random.default_rng(6))
    everything = _run(_service(), img, tmp_path).areas_of_interest
    capped = _run(_service(max_detections_per_image=2), img, tmp_path).areas_of_interest
    assert len(everything) > 2
    assert len(capped) == 2
    best_two = sorted((a['confidence'] for a in everything), reverse=True)[:2]
    assert sorted((a['confidence'] for a in capped), reverse=True) == best_two


def test_min_confidence_is_honoured(tmp_path):
    img = _several_targets(np.random.default_rng(6))
    result = _run(_service(min_confidence=40.0), img, tmp_path)
    assert all(a['confidence'] >= 40.0 for a in result.areas_of_interest)
    assert not _run(_service(min_confidence=100.0), img, tmp_path).areas_of_interest


def test_boxiness_can_be_switched_off(tmp_path):
    img = _bgr(_with_rectangle(_gaussian_ground(np.random.default_rng(7)), CENTRE, CENTRE, 60, 40, 40, 160))
    assert _hit(_run(_service(use_boxiness=False), img, tmp_path).areas_of_interest, CENTRE, CENTRE, 10)


def test_missing_option_keys_take_defaults():
    service = RectilinearShapeService((255, 0, 0), 10, 0, 0, False, {'min_confidence': '35.0'})
    assert service.settings == dict(normalize_options({}), min_confidence=35.0)


@pytest.mark.parametrize('frame', [
    np.zeros((120, 120), np.uint8),
    np.zeros((120, 120, 4), np.uint8),
    np.zeros((120, 120, 3), np.uint16),
], ids=['gray', 'bgra', 'sixteen_bit'])
def test_unusual_decodes_are_accepted(tmp_path, frame):
    result = _run(_service(), frame, tmp_path)
    assert result.error_message is None


# --- GSD and the resolution floor ---------------------------------------------

def test_below_the_resolution_floor_the_image_is_skipped_with_a_warning(tmp_path):
    """20 cm at 2 cm/px is 10 px, under the default 12 px floor."""
    img = _bgr(_with_rectangle(_gaussian_ground(np.random.default_rng(8)), CENTRE, CENTRE, 30, 20, 0, 160))
    service = _service(gsd_cm=2.0)
    service.logger = MagicMock()
    result = _run(service, img, tmp_path)
    assert result.error_message is None
    assert not result.areas_of_interest
    warning = str(service.logger.warning.call_args)
    assert 'below the 12 px floor' in warning
    assert 'frame.jpg' in warning


def test_no_gsd_and_no_fallback_is_an_error_result_not_an_exception(tmp_path):
    """The file does not exist, so the real metadata lookup finds nothing."""
    service = RectilinearShapeService((255, 0, 0), 10, 0, 0, False, {})
    result = service.process_image(np.zeros((100, 100, 3), np.uint8), str(tmp_path / 'missing.jpg'),
                                   str(tmp_path), str(tmp_path))
    assert result.error_message
    assert 'missing.jpg' in result.error_message
    assert 'RectilinearShape' in result.error_message


def test_the_fallback_gsd_is_used_and_scaled_to_processing_resolution(tmp_path):
    """Fallback is a full-resolution figure: 0.5 cm/px native at 50% is 1 cm/px processed."""
    img = _bgr(_with_rectangle(_gaussian_ground(np.random.default_rng(9)), CENTRE, CENTRE, 60, 40, 30, 160))
    service = RectilinearShapeService((255, 0, 0), 10, 0, 0, False, {'fallback_gsd_cm': 0.5})
    service.set_scale_factor(0.5)
    gsd, gsd_service = service._resolve_gsd_cm(img, str(tmp_path / 'missing.jpg'))
    assert gsd == pytest.approx(1.0)
    assert gsd_service is None
    result = service.process_image(img, str(tmp_path / 'missing.jpg'), str(tmp_path), str(tmp_path))
    assert _hit(result.areas_of_interest, CENTRE, CENTRE, 10)


class _FakeImageService:
    """Stands in for ImageService: records how it was asked, answers a fixed GSD."""

    calls = []

    def __init__(self, path, defer_load=False):
        self.path = path
        self.defer_load = defer_load

    def get_gsd_service(self, **kwargs):
        _FakeImageService.calls.append((self.defer_load, kwargs))
        gsd_service = MagicMock()
        gsd_service.compute_average_gsd.return_value = 0.5
        gsd_service.image = (800, 600)
        gsd_service.title_angle = 0.0
        return gsd_service


def test_metadata_gsd_is_cache_only_and_rescaled_to_the_processed_frame(monkeypatch):
    """0.5 cm per EXIF pixel on an 800 px frame processed at 400 px is 1 cm/px."""
    monkeypatch.setattr('core.services.image.ImageService.ImageService', _FakeImageService)
    _FakeImageService.calls = []
    service = RectilinearShapeService((255, 0, 0), 10, 0, 0, False, {})
    service.set_scale_factor(0.5)
    gsd, _ = service._resolve_gsd_cm(np.zeros((300, 400, 3), np.uint8), 'frame.jpg')
    assert gsd == pytest.approx(1.0)
    defer_load, kwargs = _FakeImageService.calls[0]
    assert defer_load is True
    assert kwargs['offline_only'] is True
    assert kwargs['use_terrain'] is True
    assert kwargs['frame_size'] == (800, 600)


def test_an_oblique_frame_widens_the_size_tolerance():
    gsd_service = MagicMock()
    gsd_service.title_angle = 30.0
    gsd_service.image = (4000, 3000)
    gsd_service.compute_gsd.side_effect = lambda row, col: 1.0 if row == 0 else 1.5
    service = RectilinearShapeService((255, 0, 0), 10, 0, 0, False, {})
    assert service._effective_tolerance(0.2, gsd_service, 'frame.jpg') == pytest.approx(1.2 * 1.5 - 1.0)


def test_a_nadir_frame_keeps_the_size_tolerance():
    gsd_service = MagicMock()
    gsd_service.title_angle = 3.0
    service = RectilinearShapeService((255, 0, 0), 10, 0, 0, False, {})
    assert service._effective_tolerance(0.2, gsd_service, 'frame.jpg') == 0.2
    gsd_service.compute_gsd.assert_not_called()


# --- outputs ------------------------------------------------------------------

def test_the_debug_overlay_is_written_only_when_enabled(tmp_path):
    img = _bgr(_with_rectangle(_gaussian_ground(np.random.default_rng(10)), CENTRE, CENTRE, 60, 40, 30, 160))
    debug_file = tmp_path / 'out' / 'rectilinear_debug' / 'frame_debug.jpg'
    _run(_service(), img, tmp_path)
    assert not debug_file.exists()
    _run(_service(debug_output=True), img, tmp_path)
    assert debug_file.exists()
    assert cv2.imread(str(debug_file)).shape == img.shape


def test_aois_and_options_survive_an_adiat_data_round_trip(tmp_path):
    """Only keys the XML writer already persists are emitted, and options read back typed."""
    img = _bgr(_with_rectangle(_gaussian_ground(np.random.default_rng(11)), CENTRE, CENTRE, 60, 40, 30, 160))
    options = dict(DEFAULT_OPTIONS, use_boxiness=False, fallback_gsd_cm=None, min_confidence=40.0)
    result = _run(_service(**options), img, tmp_path)
    assert result.areas_of_interest

    writer = XmlService()
    writer.add_settings_to_xml(algorithm='RectilinearShape', options=options)
    writer.add_image_to_xml({'path': str(tmp_path / 'frame.jpg'), 'aois': result.areas_of_interest})
    xml_path = str(tmp_path / 'ADIAT_Data.xml')
    writer.save_xml_file(xml_path)

    reader = XmlService(xml_path)
    settings, _ = reader.get_settings()
    assert normalize_options(settings['options']) == normalize_options(options)
    images = reader.get_images()
    loaded = images[0]['areas_of_interest']
    assert [a['confidence'] for a in loaded] == [a['confidence'] for a in result.areas_of_interest]
    assert {a['score_type'] for a in loaded} == {'shape'}


def test_a_target_cut_by_the_frame_edge_stays_inside_the_frame(tmp_path):
    """Two sides visible at the image edge: a corner hypothesis, but no out-of-frame pixels."""
    img = _bgr(_with_rectangle(_gaussian_ground(np.random.default_rng(13)), 12, CENTRE, 60, 40, 0, 170))
    result = _run(_service(), img, tmp_path)
    assert result.areas_of_interest
    for aoi in result.areas_of_interest:
        for x, y in aoi['contour'] + aoi['detected_pixels']:
            assert 0 <= x < FRAME and 0 <= y < FRAME


def test_contours_are_clipped_to_the_frame():
    from algorithms.Shared.services.RectilinearGeometry import RotRect
    contour = RectilinearShapeService._contour_in_frame(RotRect(5, 50, 60, 40, 0), (100, 120, 3))
    xs, ys = contour[:, 0, 0], contour[:, 0, 1]
    assert xs.min() == 0 and xs.max() == 35
    assert ys.min() == 30 and ys.max() == 70


def test_no_detections_store_no_mask(tmp_path):
    result = _run(_service(), _bgr(_gaussian_ground(np.random.default_rng(12))), tmp_path)
    assert result.output_path is None
    assert not os.path.exists(tmp_path / 'out' / 'frame.tif')
