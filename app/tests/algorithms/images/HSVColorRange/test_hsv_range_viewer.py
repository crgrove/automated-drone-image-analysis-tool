"""The View Range preview must select the same hues detection does.

The viewer clamped the hue bounds to 0..179 before testing for a wrap, so the
wrap branch could never run: a 200-20 degree range around red previewed as
0-20 degrees only, while HSVColorRangeService (which does not clamp) detected
the full 200-360 + 0-20 span.
"""

import cv2
import numpy as np
import pytest

from algorithms.Shared.views.HSVColorRangeRangeViewer import HSVColorRangeRangeViewer


def _rgb_for_hue(h):
    """RGB of a fully saturated, full-value colour at OpenCV hue h (0-179)."""
    return tuple(int(c) for c in cv2.cvtColor(np.uint8([[[h, 255, 255]]]), cv2.COLOR_HSV2RGB)[0][0])


def _selected_hues(center_h, hue_minus, hue_plus):
    every_hue = np.zeros((1, 180, 3), dtype=np.uint8)
    every_hue[0, :, 0] = np.arange(180)
    every_hue[0, :, 1:] = 255
    config = {'rgb': _rgb_for_hue(center_h), 'hue_minus': hue_minus, 'hue_plus': hue_plus,
              'sat_minus': 255, 'sat_plus': 255, 'val_minus': 255, 'val_plus': 255}
    # generate_combined_hsv_mask reads nothing off the instance; building the
    # dialog would render every palette first.
    mask = HSVColorRangeRangeViewer.generate_combined_hsv_mask(None, every_hue, [config])
    return set(np.nonzero(mask[0])[0].tolist())


@pytest.mark.parametrize('center_h, hue_minus, hue_plus, expected', [
    # 200-20 degrees around red: wraps below 0
    (0, 80, 10, set(range(100, 180)) | set(range(0, 11))),
    # 300-20 degrees around 340: wraps above 179
    (170, 20, 20, set(range(150, 180)) | set(range(0, 11))),
    # No wrap
    (60, 10, 10, set(range(50, 71))),
    # A span of the whole circle selects every hue
    (0, 90, 90, set(range(180))),
], ids=['wraps-below-zero', 'wraps-above-179', 'no-wrap', 'full-circle'])
def test_preview_selects_the_hues_detection_does(center_h, hue_minus, hue_plus, expected):
    assert _selected_hues(center_h, hue_minus, hue_plus) == expected


# The row 'H 200-20' around pure red, as each entry point's rows report it
_TYPED_ACROSS_ZERO = {'h': 0.0, 's': 1.0, 'v': 1.0, 'h_minus': 160 / 360, 'h_plus': 20 / 360,
                      's_minus': 0.5, 's_plus': 0.0, 'v_minus': 0.5, 'v_plus': 0.0}


class _Row:
    """The slice of a colour row the View Range buttons read."""

    def get_rgb(self):
        return (255, 0, 0)

    def get_hsv_ranges(self):
        return dict(_TYPED_ACROSS_ZERO)

    # Wizard rows
    def has_hsv_ranges(self):
        return True

    def get_hsv_ranges_fractional(self):
        return dict(_TYPED_ACROSS_ZERO)


@pytest.mark.parametrize('module_path, class_name', [
    ('algorithms.images.HSVColorRange.controllers.HSVColorRangeController', 'HSVColorRangeController'),
    ('algorithms.images.HSVColorRange.controllers.HSVColorRangeWizardController', 'HSVColorRangeWizardController'),
], ids=['main', 'wizard'])
def test_view_range_previews_the_typed_range_exactly(monkeypatch, module_path, class_name):
    """Both View Range buttons hand the viewer the typed bounds: 200 degrees is
    hue 100 and 20 degrees is hue 10 (x179-and-truncate gave 202 and 18)."""
    import importlib
    from types import SimpleNamespace
    module = importlib.import_module(module_path)
    captured = {}

    class _Viewer:
        def __init__(self, hsv_ranges_list):
            captured['configs'] = hsv_ranges_list

        def exec(self):
            pass

    monkeypatch.setattr(module, 'HSVColorRangeRangeViewer', _Viewer)
    getattr(module, class_name).view_range_button_clicked(SimpleNamespace(color_rows=[_Row()]))

    (config,) = captured['configs']
    assert (config['hue_minus'], config['hue_plus']) == (80, 10)
    every_hue = np.zeros((1, 180, 3), dtype=np.uint8)
    every_hue[0, :, 0] = np.arange(180)
    every_hue[0, :, 1:] = 255
    mask = HSVColorRangeRangeViewer.generate_combined_hsv_mask(None, every_hue, [config])
    assert set(np.nonzero(mask[0])[0].tolist()) == set(range(100, 180)) | set(range(0, 11))
