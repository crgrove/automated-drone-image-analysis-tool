import sys
import platform
import os
import logging
import tempfile
import traceback


# Name -> logging level, plus an "OFF" sentinel above CRITICAL.
_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'WARN': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
    'OFF': logging.CRITICAL + 10,
    'NONE': logging.CRITICAL + 10,
}


def _running_under_pytest():
    """True while a pytest run is in progress.

    PYTEST_CURRENT_TEST is set per-test; the sys.modules check also covers
    collection and module import, when LoggerService instances are created.
    Factored out so tests can pin it and exercise the real platform paths.
    """
    return 'PYTEST_CURRENT_TEST' in os.environ or 'pytest' in sys.modules


def resolve_log_path():
    """Absolute path of the log file to write.

    Under pytest this is a throwaway file in the temp directory. Tests must
    never write into the user's real adiat_logs.txt: field diagnosis depends
    on that file recording only what the app did, and a deliberate test
    failure ("Post-load zoom request failed: boom") landing there has
    already been mistaken for a field error while reading a crew's log.
    """
    if _running_under_pytest():
        app_path = os.path.join(tempfile.gettempdir(), 'adiat-test-logs')
    else:
        home_path = os.path.expanduser('~')
        if platform.system() == 'Windows' or sys.platform == 'darwin':
            # Deliberately the same location on both: ADIAT keeps its config
            # and caches here too (see helpers/AppConfig).
            app_path = os.path.join(home_path, 'AppData', 'Roaming', 'ADIAT')
        else:
            # Any other platform. Previously app_path was simply never
            # assigned here and building the log path raised
            # UnboundLocalError, taking startup down with it.
            app_path = os.path.join(home_path, '.adiat')

    os.makedirs(app_path, exist_ok=True)
    return os.path.join(app_path, 'adiat_logs.txt')


def resolve_log_level():
    """Resolve the active log level, baked in by build type.

    Precedence:
      1. ``ADIAT_LOG_LEVEL`` env var (DEBUG/INFO/WARNING/ERROR/OFF) — lets an
         operator crank a packaged build back up to troubleshoot in the field.
      2. Packaged ("frozen") production builds -> WARNING: the verbose
         debug/info chatter (POD timing, canopy indexing, EGM96 load, the
         benign "no canopy source" note, ...) stays out of adiat_logs.txt;
         only warnings and errors are recorded.
      3. Running from source (development) -> DEBUG: full verbosity.
    """
    env = os.environ.get('ADIAT_LOG_LEVEL', '').strip().upper()
    if env in _LEVELS:
        return _LEVELS[env]
    if getattr(sys, 'frozen', False):
        return logging.WARNING
    return logging.DEBUG


def resolve_console_log_level():
    """Resolve the console handler's level.

    Separate from the logger's own level so the file log stays verbose
    while the console stays readable. ``ADIAT_CONSOLE_LOG_LEVEL`` wins;
    otherwise the console shows WARNING and above. ``OFF`` silences it.
    """
    env = os.environ.get('ADIAT_CONSOLE_LOG_LEVEL', '').strip().upper()
    if env in _LEVELS:
        return _LEVELS[env]
    return logging.WARNING


def qt_message_handler(mode, context, message):
    """Route one of Qt's own messages into the ADIAT log.

    Some Qt failures are reported only here: "QThread: Destroyed while
    thread is still running" arrives as a fatal message just before Qt
    aborts the process. Qt's default handler writes to stderr, which the
    windowed build does not have, so those crashes left adiat_logs.txt
    with nothing to say.
    """
    from PySide6.QtCore import QtMsgType  # local: keeps Qt out of non-GUI importers

    log = LoggerService()
    if mode == QtMsgType.QtFatalMsg:
        log.error(f"Qt fatal error, the process is about to abort: {message}")
    elif mode == QtMsgType.QtCriticalMsg:
        log.error(f"Qt: {message}")
    elif mode == QtMsgType.QtWarningMsg:
        log.warning(f"Qt: {message}")
    else:
        log.debug(f"Qt: {message}")


def install_qt_message_handler():
    """Send Qt's messages to the ADIAT log instead of stderr."""
    from PySide6.QtCore import qInstallMessageHandler
    qInstallMessageHandler(qt_message_handler)


def fatal_excepthook(exctype, value, tb):
    """The app's sys.excepthook: log the uncaught exception, then exit.

    It used to print the traceback to stderr, which the windowed build does
    not have, so a crash left adiat_logs.txt with nothing to say about it.
    os._exit guarantees a non-zero exit instead of a hung app.
    """
    try:
        text = "".join(traceback.format_exception(exctype, value, tb))
        LoggerService().logger.critical(f"Uncaught exception, ADIAT is exiting:\n{text}")
    except Exception:
        traceback.print_exception(exctype, value, tb)
    os._exit(1)


class LoggerService:
    """Service to write errors and warnings to an application log file.

    Provides centralized logging functionality with both file and console
    handlers. Logs are written to a platform-specific directory.

    Attributes:
        logger: Python logging.Logger instance for logging messages.
    """

    logger = None

    def __init__(self):
        """Initialize the LoggerService, setting up file and console log handlers.

        Creates a log file in a platform-specific directory. If the directory
        does not exist, it is created. Sets up both file and console handlers
        with formatted output.
        """
        log_path = resolve_log_path()
        self.logger = logging.getLogger(__name__)

        # Only add handlers if they haven't been added yet (prevents duplicate logs
        # when multiple LoggerService instances are created)
        if not self.logger.handlers:
            stdoutHandler = logging.StreamHandler(stream=sys.stdout)
            fileHandler = logging.FileHandler(log_path)
            stdoutFmt = logging.Formatter(
                "%(name)s: %(asctime)s | %(levelname)s | %(process)d >>> %(message)s"
            )
            stdoutHandler.setFormatter(stdoutFmt)
            fileHandler.setFormatter(stdoutFmt)
            # The console shows what an operator or developer must notice;
            # the file keeps the full trace for troubleshooting. Without
            # this split a source run prints every DEBUG/INFO diagnostic
            # (terrain indexing, anchor resolution, acquisition skips) over
            # the top of whatever is being worked on, which trains people
            # to ignore the console entirely. ``ADIAT_CONSOLE_LOG_LEVEL``
            # overrides it when the stream itself is what you are watching.
            stdoutHandler.setLevel(resolve_console_log_level())
            self.logger.addHandler(stdoutHandler)
            self.logger.addHandler(fileHandler)
            # Baked in by build type (see resolve_log_level): prod/packaged
            # builds are quiet (warnings + errors); source runs stay verbose.
            self.logger.setLevel(resolve_log_level())

    @classmethod
    def set_level(cls, level=None):
        """Apply a log level to the shared ADIAT logger.

        Args:
            level: a logging int, a name ('WARNING'), or None to use the
                build-type default from resolve_log_level(). Callable at any
                time (e.g. from ``__main__`` at startup) to (re)assert the
                policy regardless of when the first logger was created.
        """
        if level is None:
            level = resolve_log_level()
        elif isinstance(level, str):
            level = _LEVELS.get(level.strip().upper(), logging.WARNING)
        logging.getLogger(__name__).setLevel(level)

    def info(self, message):
        """
        Log an info message.

        Args:
            message: The info message to log.
        """
        self.logger.info(message)

    def debug(self, message):
        """
        Log a debug message.

        Args:
            message: The debug message to log.
        """
        self.logger.debug(message)

    def warning(self, message):
        """
        Log a warning message.

        Args:
            message: The warning message to log.
        """
        self.logger.warning(message)

    def error(self, message):
        """
        Log an error message along with the traceback.

        Args:
            message: The error message to log.
        """
        self.logger.error(message)

        # If we're inside an exception handler, also log the full traceback
        exc_type, exc_value, exc_tb = sys.exc_info()
        if exc_type is not None and exc_tb is not None:
            tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
            self.logger.error(tb_str)
