"""CombinedExportDialog - Choose the outputs of a results-folder combined export.

Opened by the scan dialog's Export Combined Results button: the PDF report,
a KML of the detections, and/or the detections on a CalTopo map. The report
fields are shared with the single-run PDF export (PDFSettingsService), so an
organization or search name typed in either is remembered by both.
"""

from PySide6.QtWidgets import QDialog, QDialogButtonBox

from core.services.SettingsService import SettingsService
from core.services.export.PDFSettingsService import PDFSettingsService
from core.views.images.viewer.ui.CombinedExportDialog_ui import Ui_CombinedExportDialog
from helpers.TranslationMixin import TranslationMixin


class CombinedExportDialog(TranslationMixin, QDialog, Ui_CombinedExportDialog):
    """Outputs and report options for a combined export."""

    def __init__(self, parent=None):
        """
        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        self.setupUi(self)
        self._apply_translations()
        self.pdf_settings_service = PDFSettingsService()
        self.settings_service = SettingsService()

        # Stable values in itemData; only the labels are translated
        self.mapTilesComboBox.addItem(self.tr("Map"), 'map')
        self.mapTilesComboBox.addItem(self.tr("Satellite"), 'satellite')

        self.export_button = self.buttonBox.button(QDialogButtonBox.Ok)
        self.export_button.setText(self.tr("Export"))

        self.load_settings()

        self.pdfCheckBox.toggled.connect(self._update_enabled_state)
        self.kmlCheckBox.toggled.connect(self._update_enabled_state)
        self.caltopoCheckBox.toggled.connect(self._update_enabled_state)
        self._update_enabled_state()

    def accept(self):
        """Remember the choices, then close."""
        self.save_settings()
        super().accept()

    def load_settings(self):
        """Restore the last export's choices."""
        pdf_settings = self.pdf_settings_service.load_settings()
        self.organizationLineEdit.setText(pdf_settings.get('organization', ''))
        self.searchNameLineEdit.setText(pdf_settings.get('search_name', ''))
        self.includeImagesWithoutFlaggedAoisCheckBox.setChecked(
            pdf_settings.get('include_images_without_flagged_aois', False))
        index = self.mapTilesComboBox.findData(pdf_settings.get('map_tile_source', 'map'))
        self.mapTilesComboBox.setCurrentIndex(max(index, 0))

        self.pdfCheckBox.setChecked(
            self.settings_service.get_bool_setting('CombinedExportPdf', True))
        self.kmlCheckBox.setChecked(
            self.settings_service.get_bool_setting('CombinedExportKml', False))
        self.caltopoCheckBox.setChecked(
            self.settings_service.get_bool_setting('CombinedExportCalTopo', False))
        self.caltopoPhotoCheckBox.setChecked(
            self.settings_service.get_bool_setting('CombinedExportCalTopoPhotos', True))

    def save_settings(self):
        """Persist the choices for the next export."""
        self.pdf_settings_service.save_settings(
            self.organizationLineEdit.text(),
            self.searchNameLineEdit.text(),
            self.get_include_images_without_flagged_aois(),
            self.get_map_tile_source())
        self.settings_service.set_setting('CombinedExportPdf', self.should_export_pdf())
        self.settings_service.set_setting('CombinedExportKml', self.should_export_kml())
        self.settings_service.set_setting('CombinedExportCalTopo', self.should_export_caltopo())
        self.settings_service.set_setting(
            'CombinedExportCalTopoPhotos', self.caltopoPhotoCheckBox.isChecked())

    def should_export_pdf(self):
        """True to build the combined PDF report."""
        return self.pdfCheckBox.isChecked()

    def should_export_kml(self):
        """True to write the detections to a KML file."""
        return self.kmlCheckBox.isChecked()

    def should_export_caltopo(self):
        """True to add the detections to a CalTopo map."""
        return self.caltopoCheckBox.isChecked()

    def should_attach_caltopo_photos(self):
        """True to upload each detection's report photo to its marker."""
        return self.should_export_caltopo() and self.caltopoPhotoCheckBox.isChecked()

    def get_organization(self):
        """Organization name for the report cover."""
        return self.organizationLineEdit.text().strip()

    def get_search_name(self):
        """Search name for the report cover."""
        return self.searchNameLineEdit.text().strip()

    def get_include_images_without_flagged_aois(self):
        """The AOI scope shared by every output."""
        return self.includeImagesWithoutFlaggedAoisCheckBox.isChecked()

    def get_map_tile_source(self):
        """'map' or 'satellite' for the report's overview map."""
        return self.mapTilesComboBox.currentData() or 'map'

    def _update_enabled_state(self):
        """Options follow their output; Export needs at least one output."""
        self.pdfOptionsWidget.setEnabled(self.should_export_pdf())
        self.caltopoOptionsWidget.setEnabled(self.should_export_caltopo())
        any_output = self.should_export_pdf() or self.should_export_kml() or self.should_export_caltopo()
        self.export_button.setEnabled(any_output)
