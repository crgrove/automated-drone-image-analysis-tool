import logging
import pytest
import os
import tempfile
from unittest.mock import patch
from core.services import LoggerService as logger_module
from core.services.LoggerService import (  # Adjust the import according to your project structure
    LoggerService,
    resolve_log_level,
    resolve_log_path,
)


@pytest.fixture
def logger_service():
    # No path patching: under pytest the log resolves to a throwaway temp
    # file, so constructing the real service is safe.
    return LoggerService()


def test_logger_service_initialization_windows():
    with patch.object(logger_module, "_running_under_pytest", return_value=False), \
            patch("platform.system", return_value="Windows"), \
            patch("os.makedirs") as mock_makedirs, \
            patch("logging.getLogger"), \
            patch("logging.FileHandler"), \
            patch("logging.StreamHandler"):
        logger_service = LoggerService()
        expected_dir = os.path.join(os.path.expanduser("~"), 'AppData', 'Roaming', 'ADIAT')
        mock_makedirs.assert_called_once_with(expected_dir, exist_ok=True)
        assert logger_service.logger is not None


# ---------------------------------------------------------------------------
# resolve_log_path: tests must never write into the user's real log file.
# A deliberate test failure landing in adiat_logs.txt has already been
# mistaken for a field error while reading a crew's log.
# ---------------------------------------------------------------------------

def test_log_path_under_pytest_is_a_throwaway_file():
    """We ARE under pytest here, so no patching needed to prove it."""
    path = resolve_log_path()

    assert path.startswith(tempfile.gettempdir())
    assert 'adiat-test-logs' in path
    assert os.path.isdir(os.path.dirname(path))  # created, ready to write


def test_log_path_under_pytest_avoids_the_real_user_log():
    real_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'ADIAT')
    assert os.path.normcase(real_dir) not in os.path.normcase(resolve_log_path())


@pytest.mark.parametrize('system, sys_platform', [('Windows', 'win32'), ('Darwin', 'darwin')])
def test_log_path_outside_pytest_uses_appdata_on_supported_platforms(system, sys_platform):
    with patch.object(logger_module, "_running_under_pytest", return_value=False), \
            patch("platform.system", return_value=system), \
            patch.object(logger_module.sys, "platform", sys_platform), \
            patch("os.makedirs"):
        path = resolve_log_path()

    expected = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'ADIAT', 'adiat_logs.txt')
    assert path == expected


def test_log_path_on_other_platforms_does_not_raise():
    """Regression: neither branch matched, app_path was never assigned, and
    building the log path raised UnboundLocalError during startup."""
    with patch.object(logger_module, "_running_under_pytest", return_value=False), \
            patch("platform.system", return_value="Linux"), \
            patch.object(logger_module.sys, "platform", "linux"), \
            patch("os.makedirs"):
        path = resolve_log_path()

    assert path == os.path.join(os.path.expanduser('~'), '.adiat', 'adiat_logs.txt')


def test_running_under_pytest_detects_the_env_marker():
    with patch.dict(os.environ, {'PYTEST_CURRENT_TEST': 'x'}):
        assert logger_module._running_under_pytest() is True


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
