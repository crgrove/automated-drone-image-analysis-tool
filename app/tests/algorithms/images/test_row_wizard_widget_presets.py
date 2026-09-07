"""The row wizard widgets' preset combos, and what they must not depend on.

These four widgets are near-duplicates that nothing else constructed, so a
method landing on the wrong class in the same file went unnoticed: the combo
loop called ``self._preset_label(...)`` on a widget that did not have it.
Constructing each one is most of the value here.

The rest guards the contract the localization work rests on: the preset's
*index* is the identity, and the visible text is free to change with the
locale. Nothing may read the label back.
"""

import pytest

from algorithms.images.ColorRange.views.ColorRowWizardWidget import (
    ColorRowWizardWidget,
)
from algorithms.images.HSVColorRange.views.HSVColorRowWizardWidget import (
    HSVColorRowWizardWidget as ImagesHSVRowWizardWidget,
)
from algorithms.images.MatchedFilter.views.MatchedFilterRowWizardWidget import (
    MatchedFilterRowWizardWidget,
)
from algorithms.Shared.views.HSVColorRowWizardWidget import (
    HSVColorRowWizardWidget as SharedHSVRowWizardWidget,
)

# (class, preset attribute, combo attribute). Both HSV copies are live -
# the images one via HSVColorRangeWizardController, the Shared one via
# ColorDetectionWizardController - so both are covered.
WIDGETS = [
    (ColorRowWizardWidget, 'TOLERANCE_PRESETS', 'toleranceCombo'),
    (ImagesHSVRowWizardWidget, 'TOLERANCE_PRESETS', 'toleranceCombo'),
    (SharedHSVRowWizardWidget, 'TOLERANCE_PRESETS', 'toleranceCombo'),
    (MatchedFilterRowWizardWidget, 'AGGRESSIVENESS_PRESETS',
     'aggressivenessCombo'),
]

IDS = [f"{cls.__module__.split('.')[2]}.{cls.__name__}"
       for cls, _presets, _combo in WIDGETS]


@pytest.mark.parametrize('widget_class, presets_attr, combo_attr',
                         WIDGETS, ids=IDS)
def test_the_widget_builds_and_fills_its_preset_combo(
        app, qtbot, widget_class, presets_attr, combo_attr):
    widget = widget_class()
    qtbot.addWidget(widget)

    presets = getattr(widget_class, presets_attr)
    combo = getattr(widget, combo_attr)
    assert combo.count() == len(presets)


@pytest.mark.parametrize('widget_class, presets_attr, combo_attr',
                         WIDGETS, ids=IDS)
def test_combo_text_comes_from_the_localizable_label(
        app, qtbot, widget_class, presets_attr, combo_attr):
    """Each item shows what _preset_label returns for its key, so a locale
    with real translations changes the display and nothing else."""
    widget = widget_class()
    qtbot.addWidget(widget)

    presets = getattr(widget_class, presets_attr)
    combo = getattr(widget, combo_attr)
    for index, (key, _value) in enumerate(presets):
        assert combo.itemText(index) == widget._preset_label(key)


@pytest.mark.parametrize('widget_class, presets_attr, combo_attr',
                         WIDGETS, ids=IDS)
def test_an_unknown_preset_key_falls_back_to_itself(
        app, qtbot, widget_class, presets_attr, combo_attr):
    """A preset added to the table without a catalog entry must still show
    something, not vanish."""
    widget = widget_class()
    qtbot.addWidget(widget)

    assert widget._preset_label('Nonexistent Preset') == 'Nonexistent Preset'


@pytest.mark.parametrize('widget_class, presets_attr, combo_attr',
                         WIDGETS, ids=IDS)
def test_selection_survives_a_relabelled_combo(
        app, qtbot, widget_class, presets_attr, combo_attr):
    """The index is the identity. Overwriting every visible label - what a
    translator effectively does - must not change the value read back."""
    widget = widget_class()
    qtbot.addWidget(widget)

    presets = getattr(widget_class, presets_attr)
    combo = getattr(widget, combo_attr)
    combo.setCurrentIndex(len(presets) - 1)

    for index in range(combo.count()):
        combo.setItemText(index, f"traducido {index}")

    # The accessors differ across the four (get_tolerance_value vs
    # get_tolerance_values vs none at all); the index is the one they share
    # and the one persistence uses.
    if hasattr(widget, 'get_tolerance_index'):
        assert widget.get_tolerance_index() == len(presets) - 1
    else:
        assert widget.get_aggressiveness_index() == len(presets) - 1

    if hasattr(widget, 'get_tolerance_value'):
        assert widget.get_tolerance_value() == presets[-1][1]
    elif hasattr(widget, 'get_tolerance_values'):
        assert tuple(widget.get_tolerance_values()) == tuple(presets[-1][1])
