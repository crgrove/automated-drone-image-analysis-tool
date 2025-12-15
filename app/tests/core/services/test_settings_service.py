import pytest
from unittest.mock import patch, MagicMock
from PySide6 import QtCore
from PySide6.QtCore import QSettings
from core.services.SettingsService import SettingsService  # Adjust the import according to your project structure


@pytest.fixture
def settings_service():
    return SettingsService()


def test_settings_service_initialization():
    with patch.object(QSettings, '__init__', return_value=None) as mock_qsettings, \
            patch.object(SettingsService, '_migrate_old_settings'):
        service = SettingsService()  # Instantiate the service
        assert service is not None
        mock_qsettings.assert_called_once_with('ADIAT', 'ADIAT')  # Ensure QSettings was initialized with both org and app name


def test_set_setting(settings_service):
    with patch.object(settings_service.settings, 'setValue') as mock_set_value:
        settings_service.set_setting('test_key', 'test_value')
        mock_set_value.assert_called_once_with('test_key', 'test_value')


def test_get_setting(settings_service):
    mock_qsettings = MagicMock()
    mock_qsettings.value.return_value = 'test_value'

    with patch.object(settings_service, 'settings', mock_qsettings):
        value = settings_service.get_setting('test_key')
        # get_setting calls settings.value(name, default_value)
        mock_qsettings.value.assert_called_once_with('test_key', None)
        assert value == 'test_value'


def test_migrate_old_settings():
    """Test that old settings are migrated to new format."""
    # Create mock for old settings
    mock_old_settings = MagicMock()
    mock_old_settings.allKeys.return_value = ['key1', 'key2', 'RecentRGBColors']
    mock_old_settings.value.side_effect = lambda key: {
        'key1': 'value1',
        'key2': 'value2',
        'RecentRGBColors': [{'selected_color': (255, 0, 0)}]
    }.get(key)

    # Create mock for new settings
    mock_new_settings = MagicMock()
    mock_new_settings.value.return_value = False  # settings_migrated not set yet

    def qsettings_side_effect(*args, **kwargs):
        # If called with two args ('ADIAT', 'ADIAT'), return new settings
        if len(args) == 2:
            return mock_new_settings
        # If called with one arg ('ADIAT'), return old settings
        else:
            return mock_old_settings

    with patch('core.services.SettingsService.QtCore.QSettings', side_effect=qsettings_side_effect):
        # Instantiate service to trigger migration
        SettingsService()

        # Verify that migration was attempted
        mock_old_settings.allKeys.assert_called_once()
        # Verify that values were copied
        assert mock_new_settings.setValue.call_count >= 3  # 3 keys + settings_migrated flag


def test_migrate_old_settings_already_migrated():
    """Test that migration is skipped if already done."""
    mock_new_settings = MagicMock()
    mock_new_settings.value.return_value = True  # settings_migrated already set

    mock_old_settings = MagicMock()

    def qsettings_side_effect(*args, **kwargs):
        # If called with two args ('ADIAT', 'ADIAT'), return new settings
        if len(args) == 2:
            return mock_new_settings
        # If called with one arg ('ADIAT'), return old settings
        else:
            return mock_old_settings

    with patch('core.services.SettingsService.QtCore.QSettings', side_effect=qsettings_side_effect):
        # Instantiate service
        SettingsService()

        # Verify allKeys was never called on old settings (migration skipped)
        mock_old_settings.allKeys.assert_not_called()
