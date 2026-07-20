"""
Theme-adaptivity regression test for ReviewerNameDialog.

The title/description labels previously hardcoded dark greys (`#333`/`#666`)
in their stylesheets, so the title was near-invisible on the default dark
theme. They now use theme-aware palette roles; this test proves the rendered
foreground follows the active theme.
"""

import pytest
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import QPalette

from helpers.ThemeHelper import apply_theme
from core.views.images.viewer.dialogs.ReviewerNameDialog import ReviewerNameDialog


@pytest.fixture(scope='session')
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def restore_theme(app):
    saved_palette = QPalette(app.palette())
    saved_stylesheet = app.styleSheet()
    yield
    app.setPalette(saved_palette)
    app.setStyleSheet(saved_stylesheet)


def _palette_styled_label_lightness(dialog):
    """Effective foreground lightness of every label that uses a palette role."""
    out = []
    for lbl in dialog.findChildren(QLabel):
        if "palette(" in lbl.styleSheet():
            lbl.ensurePolished()
            out.append(lbl.palette().color(lbl.foregroundRole()).lightness())
    return out


def test_labels_are_light_on_dark_theme(app, restore_theme):
    apply_theme("Dark")
    dialog = ReviewerNameDialog()
    dialog.ensurePolished()

    lightnesses = _palette_styled_label_lightness(dialog)
    assert lightnesses, "expected palette-styled labels in the dialog"
    # On dark theme the text must be light (the old #333/#666 were dark -> invisible).
    assert all(v > 127 for v in lightnesses), lightnesses


def test_labels_are_dark_on_light_theme(app, restore_theme):
    apply_theme("Light")
    dialog = ReviewerNameDialog()
    dialog.ensurePolished()

    lightnesses = _palette_styled_label_lightness(dialog)
    assert lightnesses
    assert all(v < 127 for v in lightnesses), lightnesses
