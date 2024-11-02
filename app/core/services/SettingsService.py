from PyQt5 import QtCore


class SettingsService:
    """Service to manage persistent application settings."""

    def __init__(self):
        """
        Initialize the SettingsService with a QSettings instance.
        """
        self.settings = QtCore.QSettings('ADIAT')

    def setSetting(self, name, value):
        """
        Set a specified setting in QSettings.

        Args:
            name (str): The name of the setting.
            value (str): The value to be set for the setting.
        """
        self.settings.setValue(name, value)

    def getSetting(self, name):
        """
        Retrieve the value of a specified setting from QSettings.

        Args:
            name (str): The name of the setting to retrieve.

        Returns:
            str: The value of the setting, or an empty string if the setting does not exist.
        """
        return self.settings.value(name)
