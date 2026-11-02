"""Tests for CombinedExportDialog (outputs of the results-folder combined export)."""

from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QApplication, QDialogButtonBox

from core.views.images.viewer.dialogs.CombinedExportDialog import CombinedExportDialog

_MODULE = "core.views.images.viewer.dialogs.CombinedExportDialog"


@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])


class _FakeSettings:
    """In-memory stand-in for SettingsService."""

    def __init__(self, values=None):
        self.values = dict(values or {})

    def get_bool_setting(self, name, default_value=False):
        return self.values.get(name, default_value)

    def set_setting(self, name, value):
        self.values[name] = value


@pytest.fixture
def stores():
    """Patch both persistence services; yields (pdf_settings_mock, fake_settings)."""
    settings = _FakeSettings()
    with patch(f"{_MODULE}.PDFSettingsService") as pdf_cls, \
            patch(f"{_MODULE}.SettingsService", return_value=settings):
        pdf_cls.return_value.load_settings.return_value = {
            'organization': 'TEXSAR',
            'search_name': 'Ridge Search',
            'include_images_without_flagged_aois': False,
            'map_tile_source': 'satellite',
        }
        yield pdf_cls.return_value, settings


def test_defaults_to_the_pdf_report_only(app, stores):
    dialog = CombinedExportDialog()

    assert dialog.should_export_pdf()
    assert not dialog.should_export_kml()
    assert not dialog.should_export_caltopo()
    assert dialog.caltopoPhotoCheckBox.isChecked()
    assert dialog.windowTitle() == "Export Combined Results"
    assert dialog.export_button.text() == "Export"


def test_restores_the_report_fields(app, stores):
    dialog = CombinedExportDialog()

    assert dialog.get_organization() == 'TEXSAR'
    assert dialog.get_search_name() == 'Ridge Search'
    assert dialog.get_map_tile_source() == 'satellite'
    assert dialog.get_include_images_without_flagged_aois() is False


def test_restores_the_last_outputs(app, stores):
    _, settings = stores
    settings.values.update({
        'CombinedExportPdf': False, 'CombinedExportKml': True,
        'CombinedExportCalTopo': True, 'CombinedExportCalTopoPhotos': False,
    })
    dialog = CombinedExportDialog()

    assert not dialog.should_export_pdf()
    assert dialog.should_export_kml()
    assert dialog.should_export_caltopo()
    assert not dialog.should_attach_caltopo_photos()


def test_map_tiles_use_stable_values(app, stores):
    dialog = CombinedExportDialog()
    assert [dialog.mapTilesComboBox.itemData(i) for i in range(dialog.mapTilesComboBox.count())] == [
        'map', 'satellite']


def test_options_follow_their_output(app, stores):
    dialog = CombinedExportDialog()

    dialog.pdfCheckBox.setChecked(False)
    assert not dialog.pdfOptionsWidget.isEnabled()
    assert not dialog.caltopoOptionsWidget.isEnabled()

    dialog.caltopoCheckBox.setChecked(True)
    assert dialog.caltopoOptionsWidget.isEnabled()


def test_photos_only_count_when_caltopo_is_chosen(app, stores):
    dialog = CombinedExportDialog()
    dialog.caltopoPhotoCheckBox.setChecked(True)

    dialog.caltopoCheckBox.setChecked(False)
    assert not dialog.should_attach_caltopo_photos()

    dialog.caltopoCheckBox.setChecked(True)
    assert dialog.should_attach_caltopo_photos()


def test_export_needs_at_least_one_output(app, stores):
    dialog = CombinedExportDialog()

    dialog.pdfCheckBox.setChecked(False)
    assert not dialog.export_button.isEnabled()

    dialog.kmlCheckBox.setChecked(True)
    assert dialog.export_button.isEnabled()


def test_accept_saves_the_choices(app, stores):
    pdf_settings, settings = stores
    dialog = CombinedExportDialog()
    dialog.organizationLineEdit.setText("  Teton SAR ")
    dialog.kmlCheckBox.setChecked(True)
    dialog.caltopoCheckBox.setChecked(True)
    dialog.caltopoPhotoCheckBox.setChecked(False)
    dialog.includeImagesWithoutFlaggedAoisCheckBox.setChecked(True)

    dialog.buttonBox.button(QDialogButtonBox.Ok).click()

    pdf_settings.save_settings.assert_called_once_with("  Teton SAR ", 'Ridge Search', True, 'satellite')
    assert dialog.get_organization() == "Teton SAR"
    assert settings.values == {
        'CombinedExportPdf': True, 'CombinedExportKml': True,
        'CombinedExportCalTopo': True, 'CombinedExportCalTopoPhotos': False,
    }


def test_cancel_saves_nothing(app, stores):
    pdf_settings, settings = stores
    dialog = CombinedExportDialog()
    dialog.kmlCheckBox.setChecked(True)

    dialog.buttonBox.button(QDialogButtonBox.Cancel).click()

    pdf_settings.save_settings.assert_not_called()
    assert settings.values == {}
