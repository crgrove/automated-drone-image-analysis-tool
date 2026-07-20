"""
Comprehensive tests for MapExportDialog.

Tests dialog for configuring map export options.
"""

import pytest
from PySide6.QtWidgets import QApplication
from core.views.images.viewer.dialogs.MapExportDialog import MapExportDialog


@pytest.fixture(scope='session')
def app():
    """Create QApplication for widget tests."""
    return QApplication.instance() or QApplication([])


def test_map_export_dialog_initialization(app):
    """Test MapExportDialog initialization."""
    dialog = MapExportDialog()
    assert dialog is not None
    assert dialog.windowTitle() == "Map Export Options"


def test_get_export_type_kml_default(app):
    """Test that KML is selected by default."""
    dialog = MapExportDialog()
    export_type = dialog.get_export_type()
    assert export_type == 'kml'


def test_get_export_type_caltopo(app):
    """Test selecting CalTopo export type."""
    dialog = MapExportDialog()
    dialog.caltopo_radio.setChecked(True)
    export_type = dialog.get_export_type()
    assert export_type == 'caltopo'


def test_should_include_locations_default(app):
    """Test that locations are included by default."""
    dialog = MapExportDialog()
    assert dialog.should_include_locations() is True


def test_should_include_flagged_aois_default(app):
    """Test that flagged AOIs are included by default."""
    dialog = MapExportDialog()
    assert dialog.should_include_flagged_aois() is True


def test_should_include_coverage_default(app):
    """Test that coverage is included by default."""
    dialog = MapExportDialog()
    assert dialog.should_include_coverage() is True


def test_should_include_images_disabled_for_kml(app):
    """Test that images option is disabled for KML."""
    dialog = MapExportDialog()
    dialog.kml_radio.setChecked(True)
    assert dialog.include_images.isEnabled() is False


def test_should_include_images_enabled_for_caltopo(app):
    """Test that images option is enabled for CalTopo."""
    dialog = MapExportDialog()
    dialog.caltopo_radio.setChecked(True)
    assert dialog.include_images.isEnabled() is True


def test_should_include_images_default(app):
    """Test that images are included by default."""
    dialog = MapExportDialog()
    dialog.caltopo_radio.setChecked(True)  # Enable the option
    assert dialog.should_include_images() is True


def test_should_include_pod_default_off(app):
    """POD is heavy compute, so it is opt-in (off by default)."""
    dialog = MapExportDialog()
    assert dialog.should_include_pod() is False


def test_show_pod_on_map_gated_on_include(app):
    """Show-on-map is enabled only when POD is enabled; default on."""
    dialog = MapExportDialog()
    assert dialog.show_pod_on_map.isEnabled() is False
    assert dialog.should_show_pod_on_map() is False
    dialog.include_pod.setChecked(True)
    assert dialog.show_pod_on_map.isEnabled() is True
    assert dialog.show_pod_on_map.isChecked() is True
    assert dialog.should_show_pod_on_map() is True


def test_show_pod_on_map_requires_include(app):
    """show_pod_on_map returns False when POD itself is disabled."""
    dialog = MapExportDialog()
    dialog.show_pod_on_map.setChecked(True)
    dialog.include_pod.setChecked(False)
    assert dialog.should_show_pod_on_map() is False
