from PyQt5.QtCore import QSettings
from app.core.services.SettingsService import SettingsService
import os

SETTINGS_DRONE_FILE_VERSION = "drone_sensor_file_version"

settings = QSettings("MyCompany", "MyApp")

def get_pickle_file(app_version):
    settings_service = SettingsService()
    settings_service.get_setting('drone_sensor_file_version')
    last_app_version = settings_service.get_setting('app_version')
    user_pickle = settings.value(SETTINGS_KEY_PICKLE, None)
    # Check if the app version has changed
    if last_app_version != APP_VERSION:
        # App was updated: reset to bundled pickle and update version
        settings.setValue(SETTINGS_KEY_PICKLE, bundled_pickle)
        settings.setValue(SETTINGS_KEY_VERSION, APP_VERSION)
        return bundled_pickle
    # Not updated: use previous selection (user or bundled)
    if user_pickle and os.path.exists(user_pickle):
        return user_pickle
    else:
        return bundled_pickle

def user_imported_pickle(pickle_path):
    # User selects a new pickle file (overrides for current app version)
    settings.setValue(SETTINGS_KEY_PICKLE, pickle_path)

# Example usage:
pickle_path = get_pickle_file()
print("Using pickle file:", pickle_path)
