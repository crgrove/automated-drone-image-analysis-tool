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
        self._loadSettings()
        self._connectSignals()

    def _loadSettings(self):
        """Loads the settings from SettingsService and updates the UI accordingly."""
        self.maxAOIsSpinBox.setValue(self.parent.settings_service.getSetting('MaxAOIs'))
        self.themeComboBox.setCurrentText(self.parent.settings_service.getSetting('Theme'))
        self.AOIRadiusSpinBox.setValue(self.parent.settings_service.getSetting('AOIRadius'))
        self.positionFormatComboBox.setCurrentText(self.parent.settings_service.getSetting('PositionFormat'))

    def _connectSignals(self):
        """Connects UI signals to the appropriate update methods."""
        self.maxAOIsSpinBox.valueChanged.connect(self.updateMaxAOIs)
        self.AOIRadiusSpinBox.valueChanged.connect(self.updateAOIRadius)
        self.themeComboBox.currentTextChanged.connect(self.updateTheme)
        self.positionFormatComboBox.currentTextChanged.connect(self.updatePositionFormat)
        self.temperatureComboBox.currentTextChanged.connect(self.updateTemperatureUnit)

    def updateMaxAOIs(self):
        """Updates the maximum areas of interest setting based on the spinbox value."""
        self.parent.settings_service.setSetting('MaxAOIs', self.maxAOIsSpinBox.value())

    def updateAOIRadius(self):
        """Updates the area of interest radius setting based on the spinbox value."""
        self.parent.settings_service.setSetting('AOIRadius', self.AOIRadiusSpinBox.value())

    def updateTheme(self):
        """Updates the theme setting based on the selected combobox value and applies it."""
        theme = self.themeComboBox.currentText()
        self.parent.settings_service.setSetting('Theme', theme)
        self.parent.updateTheme(theme)

    def updatePositionFormat(self):
        """Updates the position format setting based on the selected combobox value."""
        self.parent.settings_service.setSetting('PositionFormat', self.positionFormatComboBox.currentText())

    def updateTemperatureUnit(self):
        """Updates the temperature unit setting based on the selected combobox value."""
        self.parent.settings_service.setSetting('TemperatureUnit', self.temperatureComboBox.currentText())
