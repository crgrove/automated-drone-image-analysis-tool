from PyQt5.QtWidgets import QDialog
from core.views.components.Preferences_ui import Ui_Preferences
from core.services.SettingsService import SettingsService


class Preferences(QDialog, Ui_Preferences):
    """Controller for the Preferences dialog box.

    This class manages user preferences for the application, including settings such as
    maximum areas of interest, theme, area of interest radius, position format, and temperature unit.
    """

    def __init__(self, parent):
        """Initializes the Preferences dialog.

        Args:
            parent (MainWindow): The parent window for the dialog.
        """
        super().__init__()
        self.parent = parent
        self.setupUi(self)
        self._load_settings()
        self._connect_signals()

    def _load_settings(self):
        """Loads the settings from SettingsService and updates the UI accordingly."""
        self.maxAOIsSpinBox.setValue(self.parent.settings_service.get_setting('MaxAOIs'))
        self.themeComboBox.setCurrentText(self.parent.settings_service.get_setting('Theme'))
        self.AOIRadiusSpinBox.setValue(self.parent.settings_service.get_setting('AOIRadius'))
        self.positionFormatComboBox.setCurrentText(self.parent.settings_service.get_setting('PositionFormat'))

    def _connect_signals(self):
        """Connects UI signals to the appropriate update methods."""
        self.maxAOIsSpinBox.valueChanged.connect(self._update_max_aois)
        self.AOIRadiusSpinBox.valueChanged.connect(self._update_aoi_radius)
        self.themeComboBox.currentTextChanged.connect(self._update_theme)
        self.positionFormatComboBox.currentTextChanged.connect(self._update_position_format)
        self.temperatureComboBox.currentTextChanged.connect(self._update_temperature_unit)

    def _update_max_aois(self):
        """Updates the maximum areas of interest setting based on the spinbox value."""
        self.parent.settings_service.set_setting('MaxAOIs', self.maxAOIsSpinBox.value())

    def _update_aoi_radius(self):
        """Updates the area of interest radius setting based on the spinbox value."""
        self.parent.settings_service.set_setting('AOIRadius', self.AOIRadiusSpinBox.value())

    def _update_theme(self):
        """Updates the theme setting based on the selected combobox value and applies it."""
        theme = self.themeComboBox.currentText()
        self.parent.settings_service.set_setting('Theme', theme)
        self.parent.update_theme(theme)

    def _update_position_format(self):
        """Updates the position format setting based on the selected combobox value."""
        self.parent.settings_service.set_setting('PositionFormat', self.positionFormatComboBox.currentText())

    def _update_temperature_unit(self):
        """Updates the temperature unit setting based on the selected combobox value."""
        self.parent.settings_service.set_setting('TemperatureUnit', self.temperatureComboBox.currentText())
