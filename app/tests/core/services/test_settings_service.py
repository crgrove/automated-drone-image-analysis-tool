import pytest
from unittest.mock import patch, MagicMock
from PyQt5 import QtCore
from app.core.services.SettingsService import SettingsService  # Adjust the import according to your project structure


@pytest.fixture
def settings_service():
    return SettingsService()


def test_settings_service_initialization():
    with patch.object(QtCore, 'QSettings') as mock_qsettings:
        mock_qsettings.assert_called_once_with('ADIAT')


def test_set_setting(settings_service):
    with patch.object(settings_service.settings, 'setValue') as mock_set_value:
        settings_service.set_setting('test_key', 'test_value')
        mock_set_value.assert_called_once_with('test_key', 'test_value')


def test_get_setting(settings_service):
    with patch.object(settings_service.settings, 'value', return_value='test_value') as mock_get_value:
        value = settings_service.get_setting('test_key')
        mock_get_value.assert_called_once_with('test_key')
        assert value == 'test_value'
