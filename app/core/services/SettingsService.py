from PySide6 import QtCore


class SettingsService:
    """Service to manage persistent application settings.

    Provides a wrapper around QSettings for storing and retrieving application
    preferences. Settings are persisted across application sessions.

    Attributes:
        settings: QSettings instance for storing application settings.
    """

    def __init__(self):
        """Initialize the SettingsService with a QSettings instance."""
        self.settings = QtCore.QSettings('ADIAT')

    def set_setting(self, name, value):
        """Set a specified setting in QSettings.

        Args:
            name: The name of the setting.
            value: The value to be set for the setting. Can be any type
                supported by QSettings (str, int, bool, etc.).
        """
        self.settings.setValue(name, value)
        self.settings.sync()  # Ensure setting is persisted immediately

    def get_setting(self, name, default_value=None):
        """Retrieve the value of a specified setting from QSettings.

        Args:
            name: The name of the setting to retrieve.
            default_value: The default value to return if the setting does not
                exist. Defaults to None.

        Returns:
            The value of the setting with its stored type (int/str/bool/tuple/etc.),
            or the default value if the setting does not exist.
        """
        value = self.settings.value(name, default_value)
        # Return value as-is to preserve original types
        return value if value is not None else default_value
