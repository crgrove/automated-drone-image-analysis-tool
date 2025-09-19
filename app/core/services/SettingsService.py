from PySide6 import QtCore


class SettingsService:
    """Service to manage persistent application settings."""

    def __init__(self):
        """
        Initialize the SettingsService with a QSettings instance.
        """
        self.settings = QtCore.QSettings('ADIAT')

    def set_setting(self, name, value):
        """
        Set a specified setting in QSettings.

        Args:
            name (str): The name of the setting.
            value (str): The value to be set for the setting.
        """
        self.settings.setValue(name, value)

    def get_setting(self, name, default_value=''):
        """
        Retrieve the value of a specified setting from QSettings.

        Args:
            name (str): The name of the setting to retrieve.
            default_value (str): The default value to return if the setting does not exist.

        Returns:
            str: The value of the setting, or the default value if the setting does not exist.
        """
        return self.settings.value(name, default_value)
