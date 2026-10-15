"""Tests for AOIDuplicateService - linking repeat detections to a primary AOI."""

from unittest.mock import MagicMock

import pytest

from core.services import AOIDuplicateService as dup


def _aoi(number, **extra):
    aoi = {'center': (number * 10, number * 10), 'radius': 10, 'area': 100, 'number': number}
    aoi.update(extra)
    return aoi


@pytest.fixture
def images():
    """Three images; AOI #1 is flagged."""
    return [
        {'path': '/data/IMG_0001.JPG', 'name': 'IMG_0001.JPG',
         'areas_of_interest': [_aoi(1, flagged=True), _aoi(2)]},
        {'path': '/data/IMG_0002.JPG', 'name': 'IMG_0002.JPG',
         'areas_of_interest': [_aoi(3), _aoi(4, flagged=True)]},
        {'path': '/data/IMG_0003.JPG',
         'areas_of_interest': [_aoi(5)]},
    ]


def _aoi_at(images, ref):
    return images[ref[0]]['areas_of_interest'][ref[1]]


# ---------------------------------------------------------------------------
# Reading links
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('value, expected', [
    ('12', 12), (' 7 ', 7), (None, None), ('', None), ('abc', None), ('1.5', None),
])
def test_parse_duplicate_of(value, expected):
    assert dup.parse_duplicate_of(value) == expected


def test_get_duplicate_of_ignores_non_int_values():
    assert dup.get_duplicate_of({'duplicate_of': 3}) == 3
    assert dup.get_duplicate_of({'duplicate_of': '3'}) is None
    assert dup.get_duplicate_of({'duplicate_of': True}) is None
    assert dup.get_duplicate_of({}) is None
    assert dup.get_duplicate_of(None) is None


def test_link_to_missing_or_self_number_is_not_a_duplicate(images):
    orphan = images[0]['areas_of_interest'][1]
    orphan['duplicate_of'] = 99
    assert dup.is_duplicate(images, orphan) is False

    self_linked = images[1]['areas_of_interest'][0]
    self_linked['duplicate_of'] = 3
    assert dup.is_duplicate(images, self_linked) is False
    assert dup.duplicates_by_primary(images) == {}


def test_image_display_name_falls_back_to_path_basename(images):
    assert dup.image_display_name(images[0]) == 'IMG_0001.JPG'
    assert dup.image_display_name(images[2]) == 'IMG_0003.JPG'
    assert dup.image_display_name({'path': 'C:\\flight\\DJI_9.JPG'}) == 'DJI_9.JPG'


# ---------------------------------------------------------------------------
# mark_duplicates / clear_duplicates
# ---------------------------------------------------------------------------

def test_mark_links_items_and_clears_their_flags(images):
    change = dup.mark_duplicates(images, [(0, 1), (1, 1)], (0, 0))

    assert change.primary == (0, 0)
    assert change.changed == [(0, 1), (1, 1)]
    assert change.count == 2
    assert _aoi_at(images, (0, 1))['duplicate_of'] == 1
    # #4 was flagged: as a duplicate it is reported through #1 instead
    assert _aoi_at(images, (1, 1))['duplicate_of'] == 1
    assert _aoi_at(images, (1, 1))['flagged'] is False
    assert dup.duplicates_by_primary(images) == {1: [(0, 1), (1, 1)]}
    assert dup.duplicate_counts(images) == {1: 2}


def test_mark_skips_the_primary_invalid_refs_and_unnumbered_aois(images):
    images[2]['areas_of_interest'].append({'center': (1, 1), 'radius': 5})
    change = dup.mark_duplicates(images, [(0, 0), (9, 9), (2, 1), (None, 0)], (0, 0))

    assert change.primary == (0, 0)
    assert change.changed == []
    assert 'duplicate_of' not in _aoi_at(images, (0, 0))
    assert 'duplicate_of' not in _aoi_at(images, (2, 1))


def test_mark_with_unusable_primary_changes_nothing(images):
    assert dup.mark_duplicates(images, [(0, 1)], (5, 0)).primary is None
    images[1]['areas_of_interest'][0].pop('number')
    change = dup.mark_duplicates(images, [(0, 1)], (1, 0))
    assert change.primary is None
    assert 'duplicate_of' not in _aoi_at(images, (0, 1))


def test_mark_again_with_same_primary_is_a_no_op(images):
    dup.mark_duplicates(images, [(0, 1)], (0, 0))
    change = dup.mark_duplicates(images, [(0, 1)], (0, 0))
    assert change.count == 0
    assert change.touched == []


def test_marking_a_duplicate_of_a_duplicate_links_to_its_primary(images):
    dup.mark_duplicates(images, [(0, 1)], (0, 0))          # #2 -> #1

    change = dup.mark_duplicates(images, [(1, 0)], (0, 1))  # #3 -> #2 means #3 -> #1

    assert change.primary == (0, 0)
    assert _aoi_at(images, (1, 0))['duplicate_of'] == 1


def test_marking_a_primary_moves_its_duplicates_along(images):
    dup.mark_duplicates(images, [(0, 1), (1, 0)], (0, 0))   # #2, #3 -> #1

    change = dup.mark_duplicates(images, [(0, 0)], (1, 1))  # #1 -> #4

    assert change.primary == (1, 1)
    assert change.changed == [(0, 0)]
    assert set(change.touched) == {(0, 0), (0, 1), (1, 0)}
    assert dup.duplicates_by_primary(images) == {4: [(0, 0), (0, 1), (1, 0)]}
    assert _aoi_at(images, (0, 0))['flagged'] is False


def test_marking_a_primary_as_duplicate_of_its_own_duplicate_swaps_them(images):
    dup.mark_duplicates(images, [(0, 1), (1, 0)], (0, 0))   # #2, #3 -> #1

    change = dup.mark_duplicates(images, [(0, 0)], (0, 1))  # #1 -> #2: #2 becomes the primary

    assert change.primary == (0, 1)
    assert 'duplicate_of' not in _aoi_at(images, (0, 1))
    assert dup.duplicates_by_primary(images) == {2: [(0, 0), (1, 0)]}


def test_clear_removes_links_only_where_present(images):
    dup.mark_duplicates(images, [(0, 1)], (0, 0))

    change = dup.clear_duplicates(images, [(0, 1), (1, 0), (7, 7)])

    assert change.changed == [(0, 1)]
    assert change.touched == [(0, 1)]
    assert 'duplicate_of' not in _aoi_at(images, (0, 1))


def test_release_duplicates_of_a_deleted_primary(images):
    dup.mark_duplicates(images, [(0, 1), (2, 0)], (0, 0))

    change = dup.release_duplicates_of(images, 1)

    assert set(change.changed) == {(0, 1), (2, 0)}
    assert dup.duplicates_by_primary(images) == {}
    assert dup.release_duplicates_of(images, None).changed == []


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def test_sightings_list_every_duplicate_under_its_primary(images):
    dup.mark_duplicates(images, [(1, 0), (2, 0)], (0, 0))

    by_primary = dup.sightings_by_primary(images)
    sightings = dup.sightings_for(_aoi_at(images, (0, 0)), by_primary)

    assert [(s.image_name, s.number) for s in sightings] == [('IMG_0002.JPG', 3), ('IMG_0003.JPG', 5)]
    assert dup.format_sightings(sightings) == "IMG_0002.JPG (AOI #3), IMG_0003.JPG (AOI #5)"
    assert dup.sightings_line(_aoi_at(images, (0, 0)), by_primary) == (
        "Also seen in: IMG_0002.JPG (AOI #3), IMG_0003.JPG (AOI #5)")
    # Nothing for an AOI without duplicates, or with no map at all
    assert dup.sightings_line(_aoi_at(images, (1, 1)), by_primary) == ""
    assert dup.sightings_for(_aoi_at(images, (0, 0)), None) == []


def test_format_sightings_without_number():
    sighting = dup.Sighting('IMG_9.JPG', None, 0, 0)
    assert dup.format_sightings([sighting]) == "IMG_9.JPG"


# ---------------------------------------------------------------------------
# Candidates and ranking
# ---------------------------------------------------------------------------

def test_candidates_are_flagged_aois_and_existing_primaries(images):
    dup.mark_duplicates(images, [(2, 0)], (0, 1))  # #5 -> #2 (unflagged primary)

    candidates = dup.candidate_primaries(images, exclude=(1, 0))

    # #1 and #4 flagged, #2 has a duplicate; the duplicate #5 and excluded #3 are out
    assert candidates == [(0, 0), (0, 1), (1, 1)]


def test_rank_prefers_close_and_alike():
    images = [
        {'path': 'a.jpg', 'areas_of_interest': [_aoi(1)]},                   # source
        {'path': 'b.jpg', 'areas_of_interest': [_aoi(2, flagged=True)]},     # far, alike
        {'path': 'c.jpg', 'areas_of_interest': [_aoi(3, flagged=True)]},     # near, alike
        {'path': 'd.jpg', 'areas_of_interest': [_aoi(4, flagged=True)]},     # near, different
    ]
    positions = {'a.jpg': (40.0, -105.0), 'b.jpg': (40.01, -105.0),
                 'c.jpg': (40.00005, -105.0), 'd.jpg': (40.00005, -105.0)}
    alike = {1: 0.0, 2: 0.05, 3: 0.05, 4: 0.8}

    service = MagicMock()
    service.get_descriptor.side_effect = lambda path, aoi: aoi['number']
    service.compare.side_effect = lambda a, b: alike[b]
    progress = []

    ranked = dup.rank_candidates(
        images, (0, 0), [(1, 0), (2, 0), (3, 0)],
        similarity_service=service,
        locate_aois=lambda image: [positions[image['path']]],
        progress_callback=lambda done, total: progress.append((done, total)))

    assert [c.number for c in ranked] == [3, 4, 2]
    best = ranked[0]
    assert best.similarity == 95
    assert best.distance_m == pytest.approx(5.6, abs=0.2)
    assert best.image_name == 'c.jpg'
    assert ranked[2].distance_m == pytest.approx(1112, rel=0.01)
    assert progress[-1] == (3, 3)


def test_rank_without_position_or_descriptor_uses_unknown_factor():
    images = [
        {'path': 'a.jpg', 'areas_of_interest': [_aoi(1)]},
        {'path': 'b.jpg', 'areas_of_interest': [_aoi(2, flagged=True)]},
    ]
    service = MagicMock()
    service.get_descriptor.return_value = None

    ranked = dup.rank_candidates(images, (0, 0), [(1, 0)], similarity_service=service,
                                 locate_aois=lambda image: [None])

    assert ranked[0].similarity is None
    assert ranked[0].distance_m is None
    assert ranked[0].score == pytest.approx(dup.UNKNOWN_FACTOR * dup.UNKNOWN_FACTOR)


def test_rank_survives_a_failing_locator_and_reports_duplicate_counts(images):
    dup.mark_duplicates(images, [(2, 0)], (1, 1))

    def broken_locator(image):
        raise RuntimeError("no metadata")

    ranked = dup.rank_candidates(images, (0, 1), [(1, 1)], locate_aois=broken_locator)

    assert ranked[0].distance_m is None
    assert ranked[0].duplicate_count == 1


def test_rank_returns_none_when_cancelled(images):
    assert dup.rank_candidates(images, (0, 1), [(0, 0)], cancel_check=lambda: True) is None


def test_rank_with_missing_source_returns_empty(images):
    assert dup.rank_candidates(images, (9, 0), [(0, 0)]) == []


def test_proximity_halves_at_the_half_distance():
    assert dup.proximity(0) == 1.0
    assert dup.proximity(dup.PROXIMITY_HALF_DISTANCE_M) == pytest.approx(0.5)
    assert dup.proximity(None) == dup.UNKNOWN_FACTOR
