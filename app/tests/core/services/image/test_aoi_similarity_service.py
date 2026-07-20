"""
Tests for AOISimilarityService.

Covers the circular mask geometry, descriptor determinism, chromatic gating,
the blended distance regimes, and the find_similar ranking pipeline against
real cached thumbnail JPEGs in a temporary .thumbnails directory.
"""

import numpy as np
import pytest
from PIL import Image

from core.services.image.AOISimilarityService import (
    AOISimilarityService,
    MIXED_PENALTY,
    THUMB_SIZE,
)

RED = (255, 0, 0)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)


def solid_crop(rgb):
    """Create a solid-color 180x180 RGB crop."""
    return np.full((THUMB_SIZE, THUMB_SIZE, 3), rgb, dtype=np.uint8)


def split_crop(rgb_left, rgb_right, right_fraction):
    """Create a crop with a vertical split: right_fraction of columns get rgb_right."""
    crop = np.full((THUMB_SIZE, THUMB_SIZE, 3), rgb_left, dtype=np.uint8)
    split_col = int(THUMB_SIZE * (1.0 - right_fraction))
    crop[:, split_col:] = rgb_right
    return crop


def make_aoi(center=(200, 200), radius=50, area=1000, number=None):
    aoi = {'center': center, 'radius': radius, 'area': area}
    if number is not None:
        aoi['number'] = number
    return aoi


@pytest.fixture
def service(tmp_path):
    """Service backed by a temporary per-dataset thumbnail cache directory."""
    cache_dir = tmp_path / '.thumbnails'
    return AOISimilarityService(dataset_thumbnail_dir=str(cache_dir))


def seed_thumbnail(service, image_path, aoi, crop):
    """Write a crop into the service's thumbnail disk cache under the portable key."""
    key = service.thumbnail_cache.get_cache_key(image_path, aoi)
    assert service.thumbnail_cache.save_thumbnail_to_disk(
        key, crop, service.thumbnail_cache.dataset_cache_dir)


def build_dataset(service, tmp_path, crops_by_name):
    """Build viewer-style image dicts with one AOI each and seeded cached thumbnails."""
    images = []
    for i, (name, crop) in enumerate(crops_by_name):
        path = str(tmp_path / name)
        aoi = make_aoi(number=i + 1)
        if crop is not None:
            seed_thumbnail(service, path, aoi, crop)
        images.append({'path': path, 'areas_of_interest': [aoi]})
    return images


# ---------------------------------------------------------------------------
# Circular mask
# ---------------------------------------------------------------------------

class TestCircleMask:

    def test_mask_radius_formula(self, service):
        # radius=50 -> 90 * 50/60 = 75 px in thumbnail coordinates
        mask = service.build_circle_mask(50)
        assert mask[90, 90 + 74] == 255
        assert mask[90, 90 + 76] == 0

    def test_mask_radius_small_aoi(self, service):
        # radius=3 -> round(90 * 3/13) = 21
        mask = service.build_circle_mask(3)
        assert mask[90, 90 + 20] == 255
        assert mask[90, 90 + 22] == 0

    def test_mask_radius_clamped_to_tile(self, service):
        # Huge radius asymptotically approaches 90; clamped to 88
        mask = service.build_circle_mask(100000)
        assert mask[90, 90 + 87] == 255
        assert mask[90, 90 + 89] == 0

    def test_mask_excludes_corners(self, service):
        mask = service.build_circle_mask(100000)
        assert mask[0, 0] == 0
        assert mask[0, THUMB_SIZE - 1] == 0
        assert mask[THUMB_SIZE - 1, 0] == 0
        assert mask[THUMB_SIZE - 1, THUMB_SIZE - 1] == 0


# ---------------------------------------------------------------------------
# Descriptor computation
# ---------------------------------------------------------------------------

class TestComputeDescriptor:

    def test_deterministic(self, service):
        crop = split_crop(RED, ORANGE, 0.3)
        aoi = make_aoi()
        d1 = service.compute_descriptor(crop, aoi)
        d2 = service.compute_descriptor(crop, aoi)
        assert np.array_equal(d1.hs_hist, d2.hs_hist)
        assert np.array_equal(d1.v_hist, d2.v_hist)
        assert d1.mean_s == d2.mean_s
        assert d1.mean_v == d2.mean_v
        assert d1.area == d2.area

    def test_gray_crop_is_achromatic(self, service):
        descriptor = service.compute_descriptor(solid_crop(GRAY), make_aoi())
        assert descriptor is not None
        assert descriptor.hs_hist is None
        assert not descriptor.is_chromatic

    def test_red_crop_is_chromatic(self, service):
        descriptor = service.compute_descriptor(solid_crop(RED), make_aoi())
        assert descriptor.is_chromatic
        assert descriptor.hs_hist is not None
        assert descriptor.chromatic_fraction > 0.99
        # L1-normalized
        assert descriptor.hs_hist.sum() == pytest.approx(1.0, abs=1e-5)
        assert descriptor.v_hist.sum() == pytest.approx(1.0, abs=1e-5)

    def test_mask_excludes_background_corners(self, service):
        """A red disc on green background scores the same as pure red."""
        import cv2
        green_corners = solid_crop((0, 255, 0))
        # Paint the AOI circle red exactly where the mask samples (radius 50 -> 75px)
        cv2.circle(green_corners, (90, 90), 75, RED, -1)
        aoi = make_aoi(radius=50)
        d_disc = service.compute_descriptor(green_corners, aoi)
        d_red = service.compute_descriptor(solid_crop(RED), aoi)
        assert service.compare(d_disc, d_red) == pytest.approx(0.0, abs=0.01)

    def test_none_crop_returns_none(self, service):
        assert service.compute_descriptor(None, make_aoi()) is None

    def test_grayscale_2d_crop_handled(self, service):
        crop = np.full((THUMB_SIZE, THUMB_SIZE), 128, dtype=np.uint8)
        descriptor = service.compute_descriptor(crop, make_aoi())
        assert descriptor is not None
        assert not descriptor.is_chromatic

    def test_area_fallback_when_missing(self, service):
        aoi = {'center': (200, 200), 'radius': 50}
        descriptor = service.compute_descriptor(solid_crop(RED), aoi)
        assert descriptor.area == pytest.approx(np.pi * 50 ** 2, rel=0.01)


# ---------------------------------------------------------------------------
# Distance / compare
# ---------------------------------------------------------------------------

class TestCompare:

    def test_identical_chromatic_is_zero(self, service):
        d = service.compute_descriptor(solid_crop(RED), make_aoi())
        assert service.compare(d, d) == pytest.approx(0.0, abs=1e-4)

    def test_red_vs_blue_is_high(self, service):
        aoi = make_aoi()
        d_red = service.compute_descriptor(solid_crop(RED), aoi)
        d_blue = service.compute_descriptor(solid_crop(BLUE), aoi)
        assert service.compare(d_red, d_blue) > 0.5

    def test_partial_hue_overlap_ranks_between(self, service):
        aoi = make_aoi()
        d_red = service.compute_descriptor(solid_crop(RED), aoi)
        d_mostly_red = service.compute_descriptor(split_crop(RED, ORANGE, 0.3), aoi)
        d_blue = service.compute_descriptor(solid_crop(BLUE), aoi)
        assert (service.compare(d_red, d_mostly_red)
                < service.compare(d_red, d_blue))

    def test_achromatic_brightness_ordering(self, service):
        aoi = make_aoi()
        d_gray = service.compute_descriptor(solid_crop(GRAY), aoi)
        d_gray_close = service.compute_descriptor(solid_crop((140, 140, 140)), aoi)
        d_white = service.compute_descriptor(solid_crop((250, 250, 250)), aoi)
        assert (service.compare(d_gray, d_gray_close)
                < service.compare(d_gray, d_white))

    def test_mixed_regime_has_floor(self, service):
        aoi = make_aoi()
        d_red = service.compute_descriptor(solid_crop(RED), aoi)
        d_gray = service.compute_descriptor(solid_crop(GRAY), aoi)
        assert service.compare(d_red, d_gray) >= MIXED_PENALTY

    def test_area_log_ratio_monotonic(self, service):
        crop = solid_crop(RED)
        d_100 = service.compute_descriptor(crop, make_aoi(area=100))
        d_200 = service.compute_descriptor(crop, make_aoi(area=200))
        d_400 = service.compute_descriptor(crop, make_aoi(area=400))
        assert service.compare(d_100, d_200) < service.compare(d_100, d_400)

    def test_area_ratio_saturates(self, service):
        crop = solid_crop(RED)
        d_small = service.compute_descriptor(crop, make_aoi(area=100))
        d_big = service.compute_descriptor(crop, make_aoi(area=100 * 20))
        d_bigger = service.compute_descriptor(crop, make_aoi(area=100 * 200))
        assert service.compare(d_small, d_big) == pytest.approx(
            service.compare(d_small, d_bigger), abs=1e-6)

    def test_symmetry(self, service):
        aoi = make_aoi()
        d_a = service.compute_descriptor(split_crop(RED, ORANGE, 0.3), aoi)
        d_b = service.compute_descriptor(solid_crop(BLUE), make_aoi(area=5000))
        assert service.compare(d_a, d_b) == pytest.approx(service.compare(d_b, d_a), abs=1e-6)

    def test_bounds(self, service):
        descriptors = [
            service.compute_descriptor(solid_crop(c), make_aoi(area=a))
            for c, a in [(RED, 1), (BLUE, 10 ** 6), (GRAY, 500), ((250, 250, 250), 3)]
        ]
        for d_a in descriptors:
            for d_b in descriptors:
                assert 0.0 <= service.compare(d_a, d_b) <= 1.0


# ---------------------------------------------------------------------------
# find_similar pipeline
# ---------------------------------------------------------------------------

class TestFindSimilar:

    def test_ranking_order(self, service, tmp_path):
        images = build_dataset(service, tmp_path, [
            ('DJI_0001.JPG', solid_crop(RED)),            # reference
            ('DJI_0002.JPG', solid_crop(GRAY)),
            ('DJI_0003.JPG', solid_crop(RED)),            # clone -> best match
            ('DJI_0004.JPG', solid_crop(BLUE)),
            ('DJI_0005.JPG', split_crop(RED, ORANGE, 0.3)),  # mostly red -> second
        ])
        results = service.find_similar(images, 0, 0)

        names = [r['image_name'] for r in results]
        assert names[0] == 'DJI_0003.JPG'
        assert names[1] == 'DJI_0005.JPG'
        similarities = [r['similarity'] for r in results]
        assert similarities == sorted(similarities, reverse=True)
        assert all(isinstance(s, int) and 0 <= s <= 100 for s in similarities)
        # Blue (chromatic) outranks gray (mixed-regime penalty)
        assert names.index('DJI_0004.JPG') < names.index('DJI_0002.JPG')

    def test_reference_excluded_and_fields_present(self, service, tmp_path):
        images = build_dataset(service, tmp_path, [
            ('DJI_0001.JPG', solid_crop(RED)),
            ('DJI_0002.JPG', solid_crop(RED)),
        ])
        results = service.find_similar(images, 0, 0)
        assert len(results) == 1
        result = results[0]
        assert (result['image_idx'], result['aoi_idx']) == (1, 0)
        for key in ('image_name', 'image_path', 'aoi_number', 'center', 'area',
                    'similarity', 'thumbnail', 'aoi_data', 'is_reference'):
            assert key in result
        assert result['is_reference'] is False
        assert result['thumbnail'].shape == (THUMB_SIZE, THUMB_SIZE, 3)

    def test_max_results_honored(self, service, tmp_path):
        images = build_dataset(service, tmp_path, [
            (f'DJI_{i:04d}.JPG', solid_crop(RED)) for i in range(6)
        ])
        results = service.find_similar(images, 0, 0, max_results=2)
        assert len(results) == 2

    def test_deterministic_tie_order(self, service, tmp_path):
        images = build_dataset(service, tmp_path, [
            ('DJI_0001.JPG', solid_crop(RED)),
            ('DJI_0002.JPG', solid_crop(RED)),
            ('DJI_0003.JPG', solid_crop(RED)),
            ('DJI_0004.JPG', solid_crop(RED)),
        ])
        results = service.find_similar(images, 0, 0)
        assert [r['image_idx'] for r in results] == [1, 2, 3]

    def test_unreadable_image_skipped(self, service, tmp_path):
        images = build_dataset(service, tmp_path, [
            ('DJI_0001.JPG', solid_crop(RED)),
            ('DJI_0002.JPG', solid_crop(RED)),
            ('missing.JPG', None),  # no cached thumbnail, no source file
        ])
        results = service.find_similar(images, 0, 0)
        assert len(results) == 1
        assert results[0]['image_name'] == 'DJI_0002.JPG'

    def test_unanalyzable_reference_raises(self, service, tmp_path):
        images = build_dataset(service, tmp_path, [
            ('missing.JPG', None),
            ('DJI_0002.JPG', solid_crop(RED)),
        ])
        with pytest.raises(ValueError):
            service.find_similar(images, 0, 0)

    def test_invalid_reference_index_raises(self, service, tmp_path):
        images = build_dataset(service, tmp_path, [('DJI_0001.JPG', solid_crop(RED))])
        with pytest.raises(ValueError):
            service.find_similar(images, 5, 0)

    def test_cancel_returns_empty(self, service, tmp_path):
        images = build_dataset(service, tmp_path, [
            ('DJI_0001.JPG', solid_crop(RED)),
            ('DJI_0002.JPG', solid_crop(RED)),
        ])
        assert service.find_similar(images, 0, 0, cancel_check=lambda: True) == []

    def test_progress_callback_reports_total(self, service, tmp_path):
        images = build_dataset(service, tmp_path, [
            (f'DJI_{i:04d}.JPG', solid_crop(RED)) for i in range(4)
        ])
        calls = []
        service.find_similar(images, 0, 0, progress_callback=lambda d, t: calls.append((d, t)))
        assert calls[-1] == (3, 3)

    def test_descriptor_cache_prevents_recompute(self, service, tmp_path, monkeypatch):
        images = build_dataset(service, tmp_path, [
            ('DJI_0001.JPG', solid_crop(RED)),
            ('DJI_0002.JPG', solid_crop(BLUE)),
        ])
        calls = {'n': 0}
        original = service.compute_descriptor

        def counting(crop, aoi_data):
            calls['n'] += 1
            return original(crop, aoi_data)

        monkeypatch.setattr(service, 'compute_descriptor', counting)
        service.find_similar(images, 0, 0)
        first_pass = calls['n']
        assert first_pass == 2
        service.find_similar(images, 0, 0)
        assert calls['n'] == first_pass

    def test_build_reference_entry(self, service, tmp_path):
        images = build_dataset(service, tmp_path, [('DJI_0001.JPG', solid_crop(RED))])
        entry = service.build_reference_entry(images, 0, 0)
        assert entry['is_reference'] is True
        assert entry['similarity'] == 100
        assert entry['image_idx'] == 0
        assert entry['thumbnail'] is not None


# ---------------------------------------------------------------------------
# Crop acquisition fallback
# ---------------------------------------------------------------------------

class TestCropFallback:

    def test_fallback_extracts_and_self_heals_cache(self, service, tmp_path):
        """With no cached thumbnail, the crop comes from the source image and is
        written back to the dataset cache."""
        source_path = tmp_path / 'DJI_0100.JPG'
        Image.fromarray(np.full((400, 400, 3), RED, dtype=np.uint8)).save(source_path, 'JPEG')
        aoi = make_aoi(center=(200, 200), radius=50)

        crop = service.get_crop(str(source_path), aoi)
        assert crop is not None
        assert crop.shape == (THUMB_SIZE, THUMB_SIZE, 3)

        key = service.thumbnail_cache.get_cache_key(str(source_path), aoi)
        cached = service.thumbnail_cache.dataset_cache_dir / f'{key}.jpg'
        assert cached.exists()

        descriptor = service.compute_descriptor(crop, aoi)
        assert descriptor.is_chromatic

    def test_get_crop_missing_everything_returns_none(self, service, tmp_path):
        crop = service.get_crop(str(tmp_path / 'nope.JPG'), make_aoi())
        assert crop is None
