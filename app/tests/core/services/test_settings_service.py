import pytest
from unittest.mock import patch, MagicMock
from PySide6 import QtCore
from PySide6.QtCore import QSettings
from core.services.SettingsService import SettingsService  # Adjust the import according to your project structure


@pytest.fixture
def settings_service():
    return SettingsService()


def test_settings_service_initialization():
    with patch.object(QSettings, '__init__', return_value=None) as mock_qsettings:
        service = SettingsService()  # Instantiate the service
        assert service is not None
        mock_qsettings.assert_called_once_with('ADIAT')  # Ensure QSettings was initialized


def test_set_setting(settings_service):
    with patch.object(settings_service.settings, 'setValue') as mock_set_value:
        settings_service.set_setting('test_key', 'test_value')
        mock_set_value.assert_called_once_with('test_key', 'test_value')


def test_get_setting(settings_service):
    mock_qsettings = MagicMock()
    mock_qsettings.value.return_value = 'test_value'

    with patch.object(settings_service, 'settings', mock_qsettings):
        value = settings_service.get_setting('test_key')
        mock_qsettings.value.assert_called_once_with('test_key')
        assert value == 'test_value'
