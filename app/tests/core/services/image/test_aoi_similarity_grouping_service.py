"""
Tests for AOISimilarityGroupingService.

Covers the near-AND-similar linking rule, star clustering (no chaining), group
and member ordering, AOIs without a position or descriptor, cancellation and
progress, the GPS locator, and an end-to-end run over real cached thumbnails.
"""

import math
from unittest.mock import MagicMock

import numpy as np
import pytest

from core.services.image import AOISimilarityGroupingService as grouping_module
from core.services.image.AOISimilarityGroupingService import (
    AOISimilarityGroupingService,
    SimilarityGroupingResult,
    aoi_sort_key,
    make_aoi_locator,
)
from core.services.image.AOISimilarityService import AOISimilarityService, THUMB_SIZE

LAT0, LON0 = 40.0, -105.0
METRES_PER_DEG_LAT = 111194.9


def north_of(metres, lon_metres=0.0):
    """(lat, lon) offset from the origin by metres north / east."""
    return (LAT0 + metres / METRES_PER_DEG_LAT,
            LON0 + lon_metres / (METRES_PER_DEG_LAT * math.cos(math.radians(LAT0))))


class FakeSimilarityService:
    """Descriptors are labels; same label -> distance 0, else distance 1."""

    def __init__(self, labels=None, distances=None):
        self.labels = labels or {}          # (path, center) -> label or None
        self.distances = distances or {}    # frozenset({label_a, label_b}) -> distance

    def get_descriptor(self, image_path, aoi):
        return self.labels.get((image_path, tuple(aoi['center'])), 'default')

    def compare(self, a, b):
        if a == b:
            return 0.0
        return self.distances.get(frozenset((a, b)), 1.0)


def dataset(spec):
    """
    Build images + a locator from [(image_name, [(center, label, position), ...]), ...].
    """
    images, labels, positions = [], {}, {}
    for name, aois in spec:
        image = {'path': name, 'areas_of_interest': []}
        for center, label, position in aois:
            image['areas_of_interest'].append({'center': center, 'radius': 10, 'area': 100})
            labels[(name, center)] = label
            positions[(name, center)] = position
        images.append(image)

    def locate(image):
        return [positions[(image['path'], tuple(aoi['center']))] for aoi in image['areas_of_interest']]

    return images, FakeSimilarityService(labels), locate


def run(spec, **kwargs):
    images, similarity, locate = dataset(spec)
    service = AOISimilarityGroupingService(similarity)
    return service.group(images, locate, **kwargs), images


class TestLinking:

    def test_near_and_similar_are_grouped(self):
        result, _ = run([
            ('a.jpg', [((10, 10), 'red', north_of(0))]),
            ('b.jpg', [((20, 20), 'red', north_of(5))]),
        ], max_distance_m=15, min_similarity=70)
        assert result.groups == [[(0, 0), (1, 0)]]
        assert result.order == [(0, 0), (1, 0)]

    def test_similar_but_far_apart_not_grouped(self):
        result, _ = run([
            ('a.jpg', [((10, 10), 'red', north_of(0))]),
            ('b.jpg', [((20, 20), 'red', north_of(100))]),
        ], max_distance_m=15, min_similarity=70)
        assert result.groups == []
        assert result.order == [(0, 0), (1, 0)]

    def test_near_but_dissimilar_not_grouped(self):
        result, _ = run([
            ('a.jpg', [((10, 10), 'red', north_of(0))]),
            ('b.jpg', [((20, 20), 'blue', north_of(2))]),
        ], max_distance_m=15, min_similarity=70)
        assert result.groups == []

    def test_similarity_threshold_is_inclusive(self):
        images, similarity, locate = dataset([
            ('a.jpg', [((10, 10), 'red', north_of(0))]),
            ('b.jpg', [((20, 20), 'orange', north_of(2))]),
        ])
        similarity.distances[frozenset(('red', 'orange'))] = 0.30  # -> 70%
        service = AOISimilarityGroupingService(similarity)
        assert len(service.group(images, locate, 15, 70).groups) == 1
        assert service.group(images, locate, 15, 71).groups == []

    def test_distance_uses_both_axes(self):
        # 10 m north + 10 m east = 14.1 m apart
        result, _ = run([
            ('a.jpg', [((10, 10), 'red', north_of(0))]),
            ('b.jpg', [((20, 20), 'red', north_of(10, lon_metres=10))]),
        ], max_distance_m=14)
        assert result.groups == []
        result, _ = run([
            ('a.jpg', [((10, 10), 'red', north_of(0))]),
            ('b.jpg', [((20, 20), 'red', north_of(10, lon_metres=10))]),
        ], max_distance_m=15)
        assert len(result.groups) == 1

    def test_aois_in_the_same_image_can_group(self):
        result, _ = run([
            ('a.jpg', [((10, 10), 'red', north_of(0)), ((50, 50), 'red', north_of(1))]),
        ])
        assert result.groups == [[(0, 0), (0, 1)]]

    def test_rejects_non_positive_distance(self):
        images, similarity, locate = dataset([('a.jpg', [((10, 10), 'red', north_of(0))])])
        with pytest.raises(ValueError):
            AOISimilarityGroupingService(similarity).group(images, locate, max_distance_m=0)


class TestClusteringAndOrder:

    def test_star_clustering_does_not_chain(self):
        # A-B-C-D in a line, 10 m apart: B (2 links, earliest) anchors A and C;
        # D is only linked to C, which is already taken, so it stays ungrouped.
        result, _ = run([
            ('a.jpg', [((1, 1), 'red', north_of(0))]),
            ('b.jpg', [((2, 2), 'red', north_of(10))]),
            ('c.jpg', [((3, 3), 'red', north_of(20))]),
            ('d.jpg', [((4, 4), 'red', north_of(30))]),
        ], max_distance_m=12)
        assert result.groups == [[(1, 0), (0, 0), (2, 0)]]
        assert result.order == [(1, 0), (0, 0), (2, 0), (3, 0)]

    def test_members_ordered_by_similarity_then_distance(self):
        images, similarity, locate = dataset([
            ('anchor.jpg', [((1, 1), 'red', north_of(0))]),
            ('close_but_less_alike.jpg', [((2, 2), 'red2', north_of(1))]),
            ('far_identical.jpg', [((3, 3), 'red', north_of(9))]),
            ('near_identical.jpg', [((4, 4), 'red', north_of(4))]),
        ])
        similarity.distances[frozenset(('red', 'red2'))] = 0.2  # 80%
        result = AOISimilarityGroupingService(similarity).group(images, locate, 10, 70)
        assert result.groups == [[(0, 0), (3, 0), (2, 0), (1, 0)]]

    def test_largest_group_first_then_ungrouped_in_default_order(self):
        result, _ = run([
            ('a.jpg', [((1, 1), 'blue', north_of(0)), ((2, 2), 'lonely', north_of(500))]),
            ('b.jpg', [((3, 3), 'blue', north_of(1))]),
            ('c.jpg', [((4, 4), 'red', north_of(1000)), ((5, 5), 'other', north_of(2000))]),
            ('d.jpg', [((6, 6), 'red', north_of(1001)), ((7, 7), 'red', north_of(1002))]),
        ])
        assert result.groups == [[(2, 0), (3, 0), (3, 1)], [(0, 0), (1, 0)]]
        assert result.order == [(2, 0), (3, 0), (3, 1), (0, 0), (1, 0), (0, 1), (2, 1)]
        assert result.total == 7
        assert result.grouped_count == 5

    def test_ranks_follow_order_and_use_content_keys(self):
        result, images = run([
            ('a.jpg', [((10, 10), 'red', north_of(0)), ((90, 90), 'x', north_of(400))]),
            ('b.jpg', [((20, 20), 'red', north_of(5))]),
        ])
        for rank, (image_idx, aoi_idx) in enumerate(result.order):
            aoi = images[image_idx]['areas_of_interest'][aoi_idx]
            assert result.ranks[aoi_sort_key(images[image_idx]['path'], aoi)] == rank

    def test_identical_input_gives_identical_output(self):
        spec = [(f'{i}.jpg', [((i, i), 'red' if i % 2 else 'blue', north_of(i * 3))]) for i in range(30)]
        first, _ = run(spec)
        second, _ = run(spec)
        assert first.order == second.order
        assert first.groups == second.groups


class TestMissingData:

    def test_unlocated_aois_are_ungrouped_and_counted(self):
        result, _ = run([
            ('a.jpg', [((10, 10), 'red', None)]),
            ('b.jpg', [((20, 20), 'red', north_of(0))]),
            ('c.jpg', [((30, 30), 'red', north_of(1))]),
        ])
        assert result.groups == [[(1, 0), (2, 0)]]
        assert result.order == [(1, 0), (2, 0), (0, 0)]
        assert result.unlocated_count == 1

    def test_unanalyzed_aois_are_ungrouped_and_counted(self):
        result, _ = run([
            ('a.jpg', [((10, 10), None, north_of(0))]),
            ('b.jpg', [((20, 20), None, north_of(1))]),
        ])
        assert result.groups == []
        assert result.unanalyzed_count == 2

    def test_invalid_positions_count_as_unlocated(self):
        result, _ = run([
            ('a.jpg', [((10, 10), 'red', (float('nan'), 0.0))]),
            ('b.jpg', [((20, 20), 'red', (95.0, 0.0))]),
            ('c.jpg', [((30, 30), 'red', 'garbage')]),
        ])
        assert result.unlocated_count == 3

    def test_locator_failure_leaves_that_image_unlocated(self):
        images, similarity, _ = dataset([
            ('a.jpg', [((10, 10), 'red', None)]),
            ('b.jpg', [((20, 20), 'red', None)]),
        ])

        def locate(image):
            if image['path'] == 'a.jpg':
                raise OSError("unreadable")
            return [north_of(0)]

        result = AOISimilarityGroupingService(similarity).group(images, locate)
        assert result.unlocated_count == 1
        assert result.total == 2

    def test_short_locator_result_is_padded(self):
        images, similarity, _ = dataset([
            ('a.jpg', [((10, 10), 'red', None), ((20, 20), 'red', None)]),
        ])
        result = AOISimilarityGroupingService(similarity).group(images, lambda image: [north_of(0)])
        assert result.unlocated_count == 1

    def test_descriptor_exception_counts_as_unanalyzed(self):
        images, similarity, locate = dataset([('a.jpg', [((10, 10), 'red', north_of(0))])])
        similarity.get_descriptor = lambda path, aoi: (_ for _ in ()).throw(RuntimeError("bad"))
        result = AOISimilarityGroupingService(similarity).group(images, locate)
        assert result.unanalyzed_count == 1

    def test_images_without_aois_are_skipped(self):
        images, similarity, locate = dataset([('a.jpg', [((10, 10), 'red', north_of(0))])])
        images.insert(0, {'path': 'empty.jpg'})
        calls = []

        def counting_locate(image):
            calls.append(image['path'])
            return locate(image)

        result = AOISimilarityGroupingService(similarity).group(images, counting_locate)
        assert calls == ['a.jpg']
        assert result.order == [(1, 0)]


class TestProgressAndCancel:

    def test_progress_reaches_total(self):
        spec = [(f'{i}.jpg', [((i, i), 'red', north_of(i * 100))]) for i in range(250)]
        images, similarity, locate = dataset(spec)
        progress = []
        AOISimilarityGroupingService(similarity).group(
            images, locate, progress_callback=lambda done, total: progress.append((done, total)))
        assert progress == [(100, 250), (200, 250), (250, 250)]

    def test_cancel_during_analysis_returns_none(self):
        images, similarity, locate = dataset([('a.jpg', [((10, 10), 'red', north_of(0))])])
        result = AOISimilarityGroupingService(similarity).group(images, locate, cancel_check=lambda: True)
        assert result is None

    def test_cancel_during_linking_returns_none(self):
        images, similarity, locate = dataset([
            ('a.jpg', [((10, 10), 'red', north_of(0))]),
            ('b.jpg', [((20, 20), 'red', north_of(1))]),
        ])
        checks = []

        def cancel_after_analysis():
            checks.append(1)
            return len(checks) > 4  # 2 image checks + 2 AOI checks pass, linking cancels

        result = AOISimilarityGroupingService(similarity).group(
            images, locate, cancel_check=cancel_after_analysis)
        assert result is None


class TestWithRealDescriptors:

    def test_end_to_end_with_cached_thumbnails(self, tmp_path):
        similarity = AOISimilarityService(dataset_thumbnail_dir=str(tmp_path / '.thumbnails'))
        crops = {'red': (220, 30, 30), 'blue': (30, 30, 220)}
        layout = [  # name, color, metres north
            ('r1.jpg', 'red', 0), ('b1.jpg', 'blue', 3), ('r2.jpg', 'red', 5), ('r_far.jpg', 'red', 400),
        ]
        images, positions = [], {}
        for name, color, metres in layout:
            path = str(tmp_path / name)
            aoi = {'center': (100, 100), 'radius': 40, 'area': 5000}
            key = similarity.thumbnail_cache.get_cache_key(path, aoi)
            crop = np.full((THUMB_SIZE, THUMB_SIZE, 3), crops[color], dtype=np.uint8)
            assert similarity.thumbnail_cache.save_thumbnail_to_disk(
                key, crop, similarity.thumbnail_cache.dataset_cache_dir)
            images.append({'path': path, 'areas_of_interest': [aoi]})
            positions[path] = north_of(metres)

        result = AOISimilarityGroupingService(similarity).group(
            images, lambda image: [positions[image['path']]], max_distance_m=15, min_similarity=70)

        assert isinstance(result, SimilarityGroupingResult)
        assert result.groups == [[(0, 0), (2, 0)]]
        assert result.order == [(0, 0), (2, 0), (1, 0), (3, 0)]
        assert result.unanalyzed_count == 0


def test_aoi_sort_key_normalizes_center():
    assert aoi_sort_key('a.jpg', {'center': [10.4, 19.6]}) == ('a.jpg', 10, 20)
    assert aoi_sort_key('a.jpg', {'center': (10, 20)}) == ('a.jpg', 10, 20)


class TestAoiLocator:

    def test_locates_each_aoi_with_the_given_settings(self, monkeypatch):
        image_service_cls = MagicMock()
        aoi_service_cls = MagicMock()
        gps = MagicMock(latitude=40.0, longitude=-105.0)
        aoi_service_cls.return_value.calculate_gps_with_metadata.side_effect = [gps, None]
        monkeypatch.setattr(grouping_module, 'ImageService', image_service_cls)
        monkeypatch.setattr(grouping_module, 'AOIService', aoi_service_cls)
        image = {'path': 'a.jpg', 'areas_of_interest': [{'center': (1, 1)}, {'center': (2, 2)}]}

        positions = make_aoi_locator(custom_altitude_ft=300, use_terrain=False)(image)

        assert positions == [(40.0, -105.0), None]
        assert image_service_cls.call_args.kwargs['defer_load'] is True  # never decodes pixels
        assert aoi_service_cls.call_args.kwargs['image_service'] is image_service_cls.return_value
        first_call = aoi_service_cls.return_value.calculate_gps_with_metadata.call_args_list[0]
        assert first_call.args[2:] == (300, False)

    def test_unreadable_image_gives_no_positions(self, monkeypatch):
        monkeypatch.setattr(grouping_module, 'ImageService', MagicMock(side_effect=OSError("gone")))
        image = {'path': 'a.jpg', 'areas_of_interest': [{'center': (1, 1)}, {'center': (2, 2)}]}
        assert make_aoi_locator()(image) == [None, None]

    @pytest.mark.parametrize('custom_altitude_ft', [None, 0, -5])
    def test_unset_custom_altitude_is_not_passed(self, monkeypatch, custom_altitude_ft):
        aoi_service_cls = MagicMock()
        aoi_service_cls.return_value.calculate_gps_with_metadata.return_value = None
        monkeypatch.setattr(grouping_module, 'ImageService', MagicMock())
        monkeypatch.setattr(grouping_module, 'AOIService', aoi_service_cls)

        make_aoi_locator(custom_altitude_ft)({'path': 'a.jpg', 'areas_of_interest': [{'center': (1, 1)}]})

        assert aoi_service_cls.return_value.calculate_gps_with_metadata.call_args.args[2] is None
