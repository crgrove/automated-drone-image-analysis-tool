import logging
import pytest
import os
from unittest.mock import patch
from core.services.LoggerService import LoggerService, resolve_log_level  # Adjust the import according to your project structure


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


# ---------------------------------------------------------------------------
# resolve_log_level: baked-in level by build type + env override
# ---------------------------------------------------------------------------

def test_resolve_level_dev_source_is_debug():
    """Running from source (not frozen, no env override) stays verbose."""
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop('ADIAT_LOG_LEVEL', None)
        with patch("sys.frozen", False, create=True):
            assert resolve_log_level() == logging.DEBUG


def test_resolve_level_frozen_prod_is_warning():
    """A packaged (frozen) production build logs warnings + errors only."""
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop('ADIAT_LOG_LEVEL', None)
        with patch("sys.frozen", True, create=True):
            assert resolve_log_level() == logging.WARNING


def test_resolve_level_env_overrides_frozen():
    """ADIAT_LOG_LEVEL wins even on a frozen build (field troubleshooting)."""
    with patch.dict(os.environ, {'ADIAT_LOG_LEVEL': 'debug'}):
        with patch("sys.frozen", True, create=True):
            assert resolve_log_level() == logging.DEBUG


def test_resolve_level_env_case_insensitive_and_aliases():
    with patch.dict(os.environ, {'ADIAT_LOG_LEVEL': ' Warn '}):
        assert resolve_log_level() == logging.WARNING
    with patch.dict(os.environ, {'ADIAT_LOG_LEVEL': 'OFF'}):
        assert resolve_log_level() > logging.CRITICAL


def test_resolve_level_unknown_env_falls_back_to_build_default():
    """A bogus env value is ignored (falls through to the build-type default)."""
    with patch.dict(os.environ, {'ADIAT_LOG_LEVEL': 'bogus'}):
        with patch("sys.frozen", False, create=True):
            assert resolve_log_level() == logging.DEBUG


def test_set_level_applies_named_level():
    LoggerService.set_level('WARNING')
    assert logging.getLogger('core.services.LoggerService').level == logging.WARNING
    # None re-applies the build-type default (source -> DEBUG here).
    with patch("sys.frozen", False, create=True):
        os.environ.pop('ADIAT_LOG_LEVEL', None)
        LoggerService.set_level()
    assert logging.getLogger('core.services.LoggerService').level == logging.DEBUG


def test_set_level_unknown_name_defaults_to_warning():
    LoggerService.set_level('nonsense')
    assert logging.getLogger('core.services.LoggerService').level == logging.WARNING
    LoggerService.set_level('DEBUG')  # restore for other tests


# ---------------------------------------------------------------------------
# PyInstaller runtime hook: packaged builds default to WARNING
# ---------------------------------------------------------------------------

def _runtime_hook_source():
    """Locate and compile runtime_hooks/set_log_level.py from the repo root."""
    from pathlib import Path
    # .../app/tests/core/services/test_logging_service.py -> repo root is 4 up.
    hook = Path(__file__).resolve().parents[4] / 'runtime_hooks' / 'set_log_level.py'
    assert hook.is_file(), f"runtime hook missing at {hook}"
    return compile(hook.read_text(encoding='utf-8'), str(hook), 'exec')


def test_runtime_hook_defaults_to_warning_when_unset():
    """A packaged build with no ADIAT_LOG_LEVEL gets WARNING from the hook."""
    src = _runtime_hook_source()
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop('ADIAT_LOG_LEVEL', None)
        exec(src, {})
        assert os.environ['ADIAT_LOG_LEVEL'] == 'WARNING'


def test_runtime_hook_preserves_operator_override():
    """A field-set ADIAT_LOG_LEVEL survives the hook (setdefault, not assign)."""
    src = _runtime_hook_source()
    with patch.dict(os.environ, {'ADIAT_LOG_LEVEL': 'DEBUG'}):
        exec(src, {})
        assert os.environ['ADIAT_LOG_LEVEL'] == 'DEBUG'
