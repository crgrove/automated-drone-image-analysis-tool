"""The per-colour row's threshold control carries its help text.

The tooltip lived in MatchedFilter.ui until the multi-colour refactor moved the
slider into this Python-built row and the text was not carried across. Guard
against that happening again.
"""

from algorithms.images.MatchedFilter.views.MatchedFilterRowWidget import MatchedFilterRowWidget


def test_threshold_controls_and_swatch_have_tooltips(qtbot):
    row = MatchedFilterRowWidget(color=(255, 0, 0), threshold=0.3)
    qtbot.addWidget(row)

    tip = row.thresholdSlider.toolTip()
    assert "0.1-0.3" in tip and "0.7-1.0" in tip
    assert row.thresholdValueLabel.toolTip() == tip
    assert row.colorSwatch.toolTip()
