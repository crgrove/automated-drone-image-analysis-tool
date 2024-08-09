import pytest
import platform
import os
import logging
import sys
from unittest.mock import patch, MagicMock
from app.core.services.LoggerService import LoggerService  # Adjust the import according to your project structure

@pytest.fixture
def logger_service():
    with patch("os.makedirs"), patch("os.path.exists", return_value=False):
        return LoggerService()

def test_logger_service_initialization_windows():
    with patch("platform.system", return_value="Windows"), \
         patch("os.makedirs") as mock_makedirs, \
         patch("os.path.exists", return_value=False), \
         patch("logging.getLogger"), \
         patch("logging.FileHandler"), \
         patch("logging.StreamHandler"):
        logger_service = LoggerService()
        home_path = os.path.expanduser("~")
        app_path = home_path + '/AppData/Roaming/ADIAT/'
        log_path = app_path + 'adiat_logs.txt'
        mock_makedirs.assert_called_once_with(app_path)
        assert logger_service.logger is not None

def test_warning(logger_service):
    with patch.object(logger_service.logger, 'warning') as mock_warning:
        logger_service.warning("This is a warning message")
        mock_warning.assert_called_once_with("This is a warning message")

def test_error(logger_service):
    with patch.object(logger_service.logger, 'error') as mock_error, \
         patch("traceback.format_exc", return_value="Traceback (most recent call last):"):
        logger_service.error("This is an error message")
        mock_error.assert_called_once_with("This is an error message")
