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
        self.settings = QtCore.QSettings('ADIAT', 'ADIAT')
        self._migrate_old_settings()

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

    def get_bool_setting(self, name, default_value=False):
        """Retrieve a boolean setting from QSettings, handling string conversions.

        QSettings may return boolean values as strings (e.g., "True", "False"),
        so this method properly converts them to actual boolean values.

        Args:
            name: The name of the setting to retrieve.
            default_value: The default boolean value to return if the setting does not
                exist. Defaults to False.

        Returns:
            bool: The boolean value of the setting.
        """
        value = self.get_setting(name, default_value)
        if isinstance(value, bool):
            return value
        if value is None:
            return default_value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "1", "yes", "on"}:
                return True
            if lowered in {"false", "0", "no", "off"}:
                return False
            return default_value
        return bool(value)
    
    def _migrate_old_settings(self):
        """Migrate settings from old single-parameter QSettings format to new format.
        
        This ensures existing user settings are preserved when upgrading to the
        properly formatted QSettings initialization.
        """
        # Check if migration has already been done
        if self.settings.value('settings_migrated', False):
            return
        
        # Try to load from old settings format
        old_settings = QtCore.QSettings('ADIAT')
        
        # Get all keys from old settings
        old_keys = old_settings.allKeys()
        
        if old_keys:
            # Migrate each setting
            for key in old_keys:
                value = old_settings.value(key)
                if value is not None:
                    self.settings.setValue(key, value)
            
            # Mark migration as complete
            self.settings.setValue('settings_migrated', True)
            self.settings.sync()
