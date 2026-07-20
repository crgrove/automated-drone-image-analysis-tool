"""Tests for the shared HueRingSelector component."""

import pytest
from PySide6.QtWidgets import QApplication

from core.views.components.HueRingSelector import HueRingSelector


@pytest.fixture(scope='session')
def app():
    """Create QApplication for widget tests."""
    return QApplication.instance() or QApplication([])


def test_reports_positive_size_hints(app):
    """Regression: the ring provided no size hint, so it collapsed to zero
    height (and became invisible) in layouts that size by hint, such as the
    color histogram dialog's range group box."""
    ring = HueRingSelector()

    assert ring.minimumSizeHint().width() > 0
    assert ring.minimumSizeHint().height() > 0
    assert ring.sizeHint().width() >= ring.minimumSizeHint().width()
    assert ring.sizeHint().height() >= ring.minimumSizeHint().height()


def test_set_values_round_trips(app):
    """set_values/values preserve the (h, h_minus, h_plus) model."""
    ring = HueRingSelector()
    ring.set_values(0.25, 0.05, 0.1)
    assert ring.values() == (0.25, 0.05, 0.1)


def test_ring_fills_most_of_widget(app):
    """The ring should occupy most of its footprint so it stays large enough to
    use easily (regression guard against the ring being drawn too small)."""
    ring = HueRingSelector()
    ring.resize(300, 300)
    _, outer_radius, inner_radius, handle_radius = ring._metrics()

    size = 300 - ring.RING_MARGIN
    # Outer diameter uses a large share of the available square footprint.
    assert outer_radius * 2 >= 0.85 * size
    # Handles sit within the ring band (between inner and outer radius).
    assert inner_radius < handle_radius < outer_radius
