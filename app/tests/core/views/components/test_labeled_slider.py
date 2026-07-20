"""
Tests for LabeledSlider / TextLabeledSlider label theming.

These sliders paint their own labels and therefore read colours from the
palette. The regression guarded here: qdarktheme's stylesheet-mode palette
leaves ``WindowText``/``Mid`` unset, so on a light-mode-OS machine those roles
resolve to black and the labels rendered black on the dark theme. The widgets
must instead read the roles qdarktheme always sets (``Text`` and ``Link``).
"""

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor

from core.views.components.LabeledSlider import (
    LabeledSlider,
    TextLabeledSlider,
    _slider_label_colors,
)


@pytest.fixture(scope='session')
def app():
    """Create QApplication for widget tests."""
    return QApplication.instance() or QApplication([])


def _os_light_palette():
    """A palette mimicking a light-mode-OS machine under the dark theme.

    WindowText/Mid are the near-black values the OS supplies for the roles
    qdarktheme leaves unset, while Text/Link carry the theme's real colours.
    """
    palette = QPalette()
    palette.setColor(QPalette.WindowText, QColor("#000000"))
    palette.setColor(QPalette.Mid, QColor("#000000"))
    palette.setColor(QPalette.Text, QColor("#e1e5e9"))       # theme foreground
    palette.setColor(QPalette.Link, QColor("#8ab4f7"))       # theme accent
    return palette


def test_slider_label_colors_use_text_and_link_not_windowtext(app):
    """text_color must come from Text (not the OS-driven WindowText)."""
    widget = TextLabeledSlider(presets=["A", "B", "C"])
    widget.setPalette(_os_light_palette())

    text_color, tick_color, accent_color = _slider_label_colors(widget)

    # The bug was text_color == WindowText (black). It must be the theme
    # foreground (Text) instead.
    assert text_color.name() == "#e1e5e9"
    assert text_color.name() != "#000000"
    # Selected-label highlight uses the theme accent (Link).
    assert accent_color.name() == "#8ab4f7"


def test_slider_tick_color_is_translucent_foreground(app):
    """Ticks reuse the foreground colour at reduced opacity."""
    widget = TextLabeledSlider(presets=["A", "B"])
    widget.setPalette(_os_light_palette())

    text_color, tick_color, _ = _slider_label_colors(widget)

    assert (tick_color.red(), tick_color.green(), tick_color.blue()) == \
        (text_color.red(), text_color.green(), text_color.blue())
    assert tick_color.alpha() == 110


def test_labeled_slider_uses_same_theming(app):
    """The numeric LabeledSlider shares the theme-aware colour logic."""
    widget = LabeledSlider(minimum=1, maximum=5, value=3)
    widget.setPalette(_os_light_palette())

    text_color, _, accent_color = _slider_label_colors(widget)
    assert text_color.name() == "#e1e5e9"
    assert accent_color.name() == "#8ab4f7"


@pytest.mark.parametrize("factory", [
    lambda: TextLabeledSlider(presets=["Very\nConfident", "Balanced", "Permissive"]),
    lambda: LabeledSlider(minimum=1, maximum=20, value=4),
])
def test_slider_paints_without_error(app, factory):
    """paintEvent must run end-to-end with the theme-aware colours."""
    widget = factory()
    widget.setPalette(_os_light_palette())
    widget.resize(420, 90)
    # grab() forces a real paintEvent; a NameError/undefined colour would raise.
    pixmap = widget.grab()
    assert not pixmap.isNull()
