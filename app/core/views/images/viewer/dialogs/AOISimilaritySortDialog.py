"""
AOISimilaritySortDialog - Settings for the "Similar & Nearby" AOI sort.

Asks how close together (ground distance) and how alike (similarity %) two
AOIs must be to be grouped. The distance is shown in the viewer's distance
unit and always returned in metres. Accepted values are persisted to
QSettings as the defaults for next time.
"""

from PySide6.QtWidgets import QDialog

from core.services.image.AOISimilarityGroupingService import (
    DEFAULT_MAX_DISTANCE_M, DEFAULT_MIN_SIMILARITY
)
from core.services.SettingsService import SettingsService
from core.views.images.viewer.ui.AOISimilaritySortDialog_ui import Ui_AOISimilaritySortDialog
from helpers.TranslationMixin import TranslationMixin

FEET_PER_METER = 3.28084
MIN_DISTANCE_M = 1.0
MAX_DISTANCE_M = 500.0
MAX_DISTANCE_SETTING = 'SimilaritySortMaxDistanceM'
MIN_SIMILARITY_SETTING = 'SimilaritySortMinSimilarity'


class AOISimilaritySortDialog(TranslationMixin, QDialog, Ui_AOISimilaritySortDialog):
    """Asks how close and how alike AOIs must be to be grouped together."""

    def __init__(self, parent=None, distance_unit='m'):
        """
        Args:
            parent: Parent widget.
            distance_unit (str): 'm' or 'ft'.
        """
        super().__init__(parent)
        self.setupUi(self)
        self._apply_translations()
        self.distance_unit = 'ft' if distance_unit == 'ft' else 'm'
        self.settings_service = SettingsService()

        scale = self._unit_scale()
        self.distanceSpinBox.setRange(round(MIN_DISTANCE_M * scale, 1), round(MAX_DISTANCE_M * scale, 1))
        self.distanceSpinBox.setSuffix(" ft" if self.distance_unit == 'ft' else " m")
        self.distanceSpinBox.setValue(round(self._stored_distance_m() * scale, 1))
        self.similaritySpinBox.setValue(self._stored_min_similarity())

    def accept(self):
        """Remember the chosen values for next time."""
        self.settings_service.set_setting(MAX_DISTANCE_SETTING, self.get_max_distance_m())
        self.settings_service.set_setting(MIN_SIMILARITY_SETTING, self.get_min_similarity())
        super().accept()

    def get_max_distance_m(self):
        """The max distance in metres."""
        return self.distanceSpinBox.value() / self._unit_scale()

    def get_min_similarity(self):
        """The min similarity, 1-100."""
        return self.similaritySpinBox.value()

    def _unit_scale(self):
        return FEET_PER_METER if self.distance_unit == 'ft' else 1.0

    def _stored_distance_m(self):
        try:
            value = float(self.settings_service.get_setting(MAX_DISTANCE_SETTING, DEFAULT_MAX_DISTANCE_M))
        except (TypeError, ValueError):
            return DEFAULT_MAX_DISTANCE_M
        return value if MIN_DISTANCE_M <= value <= MAX_DISTANCE_M else DEFAULT_MAX_DISTANCE_M

    def _stored_min_similarity(self):
        try:
            value = int(self.settings_service.get_setting(MIN_SIMILARITY_SETTING, DEFAULT_MIN_SIMILARITY))
        except (TypeError, ValueError):
            return DEFAULT_MIN_SIMILARITY
        return value if 1 <= value <= 100 else DEFAULT_MIN_SIMILARITY
