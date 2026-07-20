"""Regression tests for gallery wheel-scroll snapping.

Covers the bug where the final wheel notch could not reach the bottom of the
AOI gallery: snapping the scroll target down to the nearest grid-row boundary
stranded the view a fraction of a row short of the end whenever the scroll
range was not an exact multiple of the row height.
"""

from core.controllers.images.viewer.gallery.GalleryUIComponent import GalleryUIComponent

snap = GalleryUIComponent._snap_wheel_scroll_value

ROW = 200


def test_scroll_down_reaches_unaligned_maximum():
    """Scrolling down at the end lands exactly on a non-row-multiple maximum."""
    # maximum (1850) is not a multiple of ROW (200); the old code snapped to
    # 1800 and could never reach the bottom.
    result = snap(scroll_up=False, current=1600, scroll_amount=400,
                  minimum=0, maximum=1850, grid_row_height=ROW)
    assert result == 1850


def test_scroll_down_short_overflow_reaches_bottom():
    """A range smaller than one row is still fully reachable downward."""
    result = snap(scroll_up=False, current=0, scroll_amount=400,
                  minimum=0, maximum=150, grid_row_height=ROW)
    assert result == 150


def test_scroll_down_midway_snaps_to_row_boundary():
    """Mid-range downward scrolling still snaps to a clean row boundary."""
    result = snap(scroll_up=False, current=0, scroll_amount=450,
                  minimum=0, maximum=1850, grid_row_height=ROW)
    # min(1850, 450) = 450 -> snapped down to 400
    assert result == 400


def test_scroll_up_snaps_to_row_boundary():
    """Upward scrolling snaps to a row boundary and never overshoots the top."""
    result = snap(scroll_up=True, current=1850, scroll_amount=400,
                  minimum=0, maximum=1850, grid_row_height=ROW)
    # max(0, 1850 - 400) = 1450 -> snapped down to 1400
    assert result == 1400


def test_scroll_up_clamps_to_minimum():
    """Scrolling up from near the top clamps to the minimum."""
    result = snap(scroll_up=True, current=150, scroll_amount=400,
                  minimum=0, maximum=1850, grid_row_height=ROW)
    assert result == 0
