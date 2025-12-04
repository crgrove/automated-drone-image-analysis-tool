"""
Comprehensive tests for CalTopoMethodDialog.

Tests dialog for selecting CalTopo export method.
"""

import pytest
from PySide6.QtWidgets import QApplication
from core.views.images.viewer.dialogs.CalTopoMethodDialog import CalTopoMethodDialog


@pytest.fixture(scope='session')
def app():
    """Create QApplication for widget tests."""
    return QApplication.instance() or QApplication([])


def test_caltopo_method_dialog_initialization(app):
    """Test CalTopoMethodDialog initialization."""
    dialog = CalTopoMethodDialog()
    assert dialog is not None
    assert dialog.windowTitle() == "CalTopo Export Method"


def test_get_selected_method_api_default(app):
    """Test that API method is selected by default."""
    dialog = CalTopoMethodDialog()
    method = dialog.get_selected_method()
    assert method == 'api'


def test_get_selected_method_browser(app):
    """Test selecting browser method."""
    dialog = CalTopoMethodDialog()
    dialog.browser_radio.setChecked(True)
    method = dialog.get_selected_method()
    assert method == 'browser'


def test_get_selected_method_api(app):
    """Test selecting API method."""
    dialog = CalTopoMethodDialog()
    dialog.api_radio.setChecked(True)
    method = dialog.get_selected_method()
    assert method == 'api'


def test_dialog_modal(app):
    """Test that dialog is modal."""
    dialog = CalTopoMethodDialog()
    assert dialog.isModal() is True
