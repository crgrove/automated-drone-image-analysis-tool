import pytest
from core.services.GridReviewService import GridReviewService


# ---------------------------------------------------------------------------
# cell_rects
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("width,height,rows,cols", [
    (8000, 6000, 4, 4),
    (8000, 6000, 1, 1),
    (1001, 757, 3, 5),     # non-divisible dimensions
    (640, 480, 12, 12),
    (7, 5, 2, 3),          # tiny image
])
def test_cell_rects_tile_image_exactly(width, height, rows, cols):
    """Cells cover every pixel exactly once: no gaps, no overlaps."""
    rects = GridReviewService.cell_rects(width, height, rows, cols)
    assert len(rects) == rows * cols

    covered = sum(w * h for _, _, w, h in rects)
    assert covered == width * height

    # No rect extends outside the image.
    for x, y, w, h in rects:
        assert x >= 0 and y >= 0
        assert x + w <= width
        assert y + h <= height

    # Cells in the same row don't overlap horizontally.
    for i in range(rows):
        row = rects[i * cols:(i + 1) * cols]
        for left, right in zip(row, row[1:]):
            assert left[0] + left[2] == right[0]


def test_cell_rects_row_major_order():
    rects = GridReviewService.cell_rects(100, 100, 2, 2)
    assert rects[0] == (0, 0, 50, 50)
    assert rects[1] == (50, 0, 50, 50)
    assert rects[2] == (0, 50, 50, 50)
    assert rects[3] == (50, 50, 50, 50)


def test_cell_rects_clamps_degenerate_grid():
    """Zero/negative rows or cols fall back to a single cell."""
    assert GridReviewService.cell_rects(100, 100, 0, -3) == [(0, 0, 100, 100)]


# ---------------------------------------------------------------------------
# serpentine_order
# ---------------------------------------------------------------------------

def test_serpentine_order_single_cell():
    assert GridReviewService.serpentine_order(1, 1) == [0]


def test_serpentine_order_4x4():
    assert GridReviewService.serpentine_order(4, 4) == [
        0, 1, 2, 3,
        7, 6, 5, 4,
        8, 9, 10, 11,
        15, 14, 13, 12,
    ]


def test_serpentine_order_3x5_visits_every_cell_once():
    order = GridReviewService.serpentine_order(3, 5)
    assert sorted(order) == list(range(15))
    # Odd rows run right-to-left.
    assert order[5:10] == [9, 8, 7, 6, 5]


def test_serpentine_order_consecutive_cells_are_adjacent():
    """Each step moves exactly one cell horizontally or vertically."""
    rows, cols = 4, 6
    order = GridReviewService.serpentine_order(rows, cols)
    for a, b in zip(order, order[1:]):
        ra, ca = divmod(a, cols)
        rb, cb = divmod(b, cols)
        assert abs(ra - rb) + abs(ca - cb) == 1


# ---------------------------------------------------------------------------
# suggest_grid
# ---------------------------------------------------------------------------

def test_suggest_grid_returns_none_without_gsd():
    assert GridReviewService.suggest_grid(8000, 6000, None, 1920, 1080) is None
    assert GridReviewService.suggest_grid(8000, 6000, 0, 1920, 1080) is None
    assert GridReviewService.suggest_grid(8000, 6000, -1.5, 1920, 1080) is None


def test_suggest_grid_returns_none_with_bad_dimensions():
    assert GridReviewService.suggest_grid(0, 6000, 2.0, 1920, 1080) is None
    assert GridReviewService.suggest_grid(8000, None, 2.0, 1920, 1080) is None
    assert GridReviewService.suggest_grid(8000, 6000, 2.0, 0, 1080) is None


def test_suggest_grid_coarser_gsd_means_more_cells():
    """Coarser GSD = fewer pixels on the person = smaller cells needed."""
    fine = GridReviewService.suggest_grid(8000, 6000, 0.5, 1920, 1080)
    coarse = GridReviewService.suggest_grid(8000, 6000, 5.0, 1920, 1080)
    assert fine is not None and coarse is not None
    assert coarse[0] >= fine[0]
    assert coarse[1] >= fine[1]


def test_suggest_grid_clamps_to_bounds():
    # Extremely fine GSD: person is huge, still at least min_n.
    rows, cols = GridReviewService.suggest_grid(8000, 6000, 0.01, 1920, 1080)
    assert (rows, cols) == (2, 2)
    # Extremely coarse GSD: clamped at max_n.
    rows, cols = GridReviewService.suggest_grid(8000, 6000, 100.0, 1920, 1080)
    assert (rows, cols) == (12, 12)


def test_suggest_grid_satisfies_min_person_px_when_unclamped():
    """For an unclamped suggestion, a person spans >= min_person_px on screen."""
    image_w, image_h, gsd, vp_w, vp_h = 8000, 6000, 2.5, 1920, 1080
    rows, cols = GridReviewService.suggest_grid(image_w, image_h, gsd, vp_w, vp_h)
    assert 2 < cols < 12  # meaningful (unclamped) suggestion for these inputs
    cell_w = image_w / cols
    person_px = GridReviewService.person_screen_px(gsd, cell_w, vp_w)
    assert person_px >= 60


def test_person_screen_px_unusable_inputs():
    assert GridReviewService.person_screen_px(None, 2000, 1920) is None
    assert GridReviewService.person_screen_px(2.0, 0, 1920) is None
    assert GridReviewService.person_screen_px(2.0, 2000, None) is None


# ---------------------------------------------------------------------------
# parse_reviewed / serialize_reviewed
# ---------------------------------------------------------------------------

def test_parse_serialize_round_trip():
    cells = {0, 1, 5, 14}
    serialized = GridReviewService.serialize_reviewed(cells)
    assert serialized == "0,1,5,14"
    assert GridReviewService.parse_reviewed(serialized) == cells


def test_parse_reviewed_tolerates_junk():
    assert GridReviewService.parse_reviewed("a,,5") == {5}
    assert GridReviewService.parse_reviewed(" 3 , 7 ") == {3, 7}
    assert GridReviewService.parse_reviewed("-1,2") == {2}
    assert GridReviewService.parse_reviewed("") == set()
    assert GridReviewService.parse_reviewed(None) == set()


def test_serialize_reviewed_deduplicates_and_sorts():
    assert GridReviewService.serialize_reviewed([5, 1, 5, 0]) == "0,1,5"
    assert GridReviewService.serialize_reviewed([]) == ""


# ---------------------------------------------------------------------------
# image_progress / run_progress
# ---------------------------------------------------------------------------

def test_image_progress_with_stored_grid():
    image = {'grid_review': {'rows': 4, 'cols': 4, 'reviewed': {0, 1, 5}}}
    assert GridReviewService.image_progress(image, 3, 3) == (3, 16)


def test_image_progress_without_grid_uses_defaults():
    assert GridReviewService.image_progress({'grid_review': None}, 4, 4) == (0, 16)
    assert GridReviewService.image_progress({}, 3, 3) == (0, 9)


def test_image_progress_ignores_out_of_range_indices():
    """Stale indices from a previously larger grid don't inflate progress."""
    image = {'grid_review': {'rows': 2, 'cols': 2, 'reviewed': {0, 3, 15, 99}}}
    assert GridReviewService.image_progress(image, 4, 4) == (2, 4)


def test_run_progress_excludes_hidden_images():
    images = [
        {'hidden': False, 'grid_review': {'rows': 2, 'cols': 2, 'reviewed': {0, 1, 2, 3}}},
        {'hidden': True, 'grid_review': {'rows': 2, 'cols': 2, 'reviewed': set()}},
        {'hidden': False, 'grid_review': None},
    ]
    # Visible: 4/4 from the first image + 0/16 default from the third.
    assert GridReviewService.run_progress(images, 4, 4) == (4, 20)


def test_run_progress_empty_inputs():
    assert GridReviewService.run_progress([], 4, 4) == (0, 0)
    assert GridReviewService.run_progress(None, 4, 4) == (0, 0)
