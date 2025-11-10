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
        self.settings.sync()  # Ensure setting is persisted immediately

    def get_setting(self, name, default_value=None):
        """
        Retrieve the value of a specified setting from QSettings.

        Args:
            name (str): The name of the setting to retrieve.
            default_value (str): The default value to return if the setting does not exist.

        Returns:
            Any: The value of the setting with its stored type (int/str/bool/tuple/etc.),
                 or the default value if the setting does not exist.
        """
        value = self.settings.value(name, default_value)
        # Return value as-is to preserve original types
        return value if value is not None else default_value
