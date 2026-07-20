"""Tests for ColorHistogramDialog's shared hue-ring integration."""

from unittest.mock import MagicMock

import pytest

from core.views.components.HueRingSelector import HueRingSelector
from core.views.images.viewer.dialogs.ColorHistogramDialog import ColorHistogramDialog


@pytest.fixture
def dialog(app, qtbot):
    dlg = ColorHistogramDialog()
    qtbot.addWidget(dlg)
    dlg._hue_domain = (0.0, 360.0)
    return dlg


def test_dialog_uses_shared_hue_ring_selector(dialog):
    """The histogram must use the shared HueRingSelector component."""
    assert isinstance(dialog.hueWheelSelector, HueRingSelector)


def test_hue_ring_is_visible_in_layout(dialog):
    """Regression: the hue-ring range selector did not appear because it had no
    size hint and collapsed to zero height inside the range group box."""
    ring = dialog.hueWheelSelector
    assert ring.minimumSizeHint().height() > 0
    # The group box hosting the ring must reserve real vertical space for it.
    assert dialog.rangeSliderContainer.minimumSizeHint().height() > 0


@pytest.mark.parametrize("lo,hi", [(0, 360), (30, 90), (0, 45), (200, 360), (175, 185)])
def test_range_hsv_round_trip(dialog, lo, hi):
    """Absolute degrees -> ring (centre,+/-) -> absolute degrees is lossless."""
    h, h_minus, h_plus = dialog._range_to_hsv(float(lo), float(hi))
    for v in (h, h_minus, h_plus):
        assert 0.0 <= v <= 1.0
    lo2, hi2 = dialog._hsv_to_range(h, h_minus, h_plus)
    assert lo2 == pytest.approx(lo, abs=1e-6)
    assert hi2 == pytest.approx(hi, abs=1e-6)


def test_ring_change_emits_converted_range(dialog):
    """A hue-ring change emits rangeChanged in absolute degrees."""
    dialog.histogram_context = {
        'histogram_data': {'min_temperature': 0.0, 'max_temperature': 360.0}
    }
    dialog.chartWidget = MagicMock()

    emitted = []
    dialog.rangeChanged.connect(lambda a, b: emitted.append((round(a), round(b))))

    # centre = 0.25 -> 90 deg, +/- 0.05 -> +/-18 deg => [72, 108]
    dialog._on_hue_ring_changed(0.25, 0.05, 0.05)

    assert emitted == [(72, 108)]
