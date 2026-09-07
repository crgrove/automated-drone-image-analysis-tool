"""The team-planning map's fit-to-points, and why it is not on a timer.

``fitInView`` needs a laid-out viewport. A rebuild driven by ``set_aoi_data``
can arrive before the widget's first layout pass, and the old code waited
50 ms and hoped.

Fitting into a 0x0 viewport is not merely cosmetic here: the fit seeds
``_min_zoom_scale`` once and only once, so a degenerate transform
permanently poisons the zoom-out floor - the operator can then never zoom
back out, for the rest of the dialog's life, on whichever machine was slow
enough to lose the race.

Qt will not hand out a genuinely 0x0 viewport on demand (``resize(0, 0)`` on
an unshown QGraphicsView still reports its size hint), so the unsized state
is injected rather than provoked. That is the honest thing to test anyway:
what changed is the *handoff* - hold the request, let the sizing event
consume it - not Qt's layout.
"""

import pytest
from PySide6.QtCore import QSize
from PySide6.QtGui import QResizeEvent

from core.views.images.viewer.widgets.TeamPlanningMapView import (
    TeamPlanningMapView,
)

AOIS = [
    {'uid': 1, 'latitude': 30.2672, 'longitude': -97.7431},
    {'uid': 2, 'latitude': 30.2700, 'longitude': -97.7400},
]


@pytest.fixture
def view(app, qtbot):
    widget = TeamPlanningMapView(offline_only=True)
    qtbot.addWidget(widget)
    widget.resize(600, 400)
    return widget


def _unsize(view, monkeypatch):
    """Make the view report an unlaid-out viewport."""
    monkeypatch.setattr(type(view), '_viewport_is_sized', lambda self: False)


def _resize(view, monkeypatch):
    """Undo :func:`_unsize` - the layout pass has happened."""
    monkeypatch.setattr(type(view), '_viewport_is_sized', lambda self: True)


def test_a_fit_before_layout_is_held_not_lost(view, monkeypatch):
    _unsize(view, monkeypatch)

    view.set_aoi_data(AOIS)

    assert view._fit_pending is True
    # Nothing was fitted, so the zoom floor is still unseeded.
    assert view._min_zoom_scale == 0.0


def test_the_resize_that_sizes_the_viewport_completes_the_fit(view, monkeypatch):
    _unsize(view, monkeypatch)
    view.set_aoi_data(AOIS)
    assert view._fit_pending is True

    _resize(view, monkeypatch)
    view.resizeEvent(QResizeEvent(QSize(600, 400), QSize(600, 400)))

    assert view._fit_pending is False
    assert view._min_zoom_scale > 0.0


def test_the_show_event_also_completes_a_held_fit(view, monkeypatch):
    """Whichever of the two events arrives first is the one that serves it."""
    _unsize(view, monkeypatch)
    view.set_aoi_data(AOIS)

    _resize(view, monkeypatch)
    view.show()

    assert view._fit_pending is False
    assert view._min_zoom_scale > 0.0


def test_a_fit_with_a_real_viewport_runs_immediately(view):
    view.set_aoi_data(AOIS)

    assert view._fit_pending is False
    assert view._min_zoom_scale > 0.0


def test_fit_all_points_refuses_a_degenerate_viewport(view, monkeypatch):
    """The guard is on the method, not only on its caller: a direct call
    must not seed the zoom floor from a transform that means nothing."""
    _unsize(view, monkeypatch)
    view._aoi_data = list(AOIS)

    view.fit_all_points()

    assert view._min_zoom_scale == 0.0     # never seeded from nothing
    assert view._fit_pending is True       # re-armed for a later layout event


def test_the_zoom_floor_is_seeded_once_from_a_real_fit(view):
    """Seeding is deliberately one-shot, so it must not happen until a fit
    that actually had a viewport."""
    view.set_aoi_data(AOIS)
    seeded = view._min_zoom_scale
    assert seeded > 0.0

    view.resize(900, 700)
    view.fit_all_points()

    assert view._min_zoom_scale == pytest.approx(seeded)


def test_no_aoi_data_means_no_fit_and_no_request(view):
    view.fit_all_points()

    assert view._fit_pending is False
    assert view._min_zoom_scale == 0.0
