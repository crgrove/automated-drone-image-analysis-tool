"""
Tests for helpers.ThemeHelper.

Guards that apply_theme() installs the *full* palette (not just qdarktheme's
minimal stylesheet-mode palette), so that WindowText / ButtonText / Mid track
the app theme rather than the OS light/dark setting.
"""

import pytest
import qdarktheme
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette

from helpers.ThemeHelper import apply_theme, normalize_theme


@pytest.fixture(scope='session')
def app():
    """Create QApplication for widget tests."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def restore_theme(app):
    """Snapshot and restore the global palette/stylesheet around a test."""
    saved_palette = QPalette(app.palette())
    saved_stylesheet = app.styleSheet()
    yield
    app.setPalette(saved_palette)
    app.setStyleSheet(saved_stylesheet)


def test_normalize_theme_variants():
    assert normalize_theme("Dark") == "dark"
    assert normalize_theme("dark") == "dark"
    assert normalize_theme("Light") == "light"
    assert normalize_theme("LIGHT") == "light"
    # Unknown / empty defaults to dark.
    assert normalize_theme("") == "dark"
    assert normalize_theme(None) == "dark"
    assert normalize_theme("nonsense") == "dark"


def test_apply_theme_returns_normalized(app, restore_theme):
    assert apply_theme("Dark") == "dark"
    assert apply_theme("Light") == "light"


def test_apply_theme_dark_pins_full_palette(app, restore_theme):
    """After apply_theme('Dark'), the unset-by-default roles match the dark palette."""
    apply_theme("Dark")
    expected = qdarktheme.load_palette("dark")
    actual = app.palette()

    for role in (QPalette.WindowText, QPalette.ButtonText, QPalette.Mid):
        assert actual.color(role).name() == expected.color(role).name()

    # WindowText must be light in the dark theme (this is what the sliders and
    # native widgets rely on); a black value would be the OS-default bug.
    assert actual.color(QPalette.WindowText).lightness() > 127


def test_apply_theme_light_pins_full_palette(app, restore_theme):
    """After apply_theme('Light'), WindowText is dark (theme foreground)."""
    apply_theme("Light")
    expected = qdarktheme.load_palette("light")
    actual = app.palette()

    for role in (QPalette.WindowText, QPalette.ButtonText, QPalette.Mid):
        assert actual.color(role).name() == expected.color(role).name()

    assert actual.color(QPalette.WindowText).lightness() < 127
