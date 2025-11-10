import sys
import platform
import os
import logging
import traceback


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
        if platform.system() == 'Windows':
            home_path = os.path.expanduser("~")
            app_path = home_path + '/AppData/Roaming/ADIAT/'
            if not os.path.exists(app_path):
                os.makedirs(app_path)
        elif sys.platform == "darwin":
            home_path = os.path.expanduser("~")
            app_path = home_path + '/AppData/Roaming/ADIAT/'
            if not os.path.exists(app_path):
                os.makedirs(app_path)

        log_path = app_path + 'adiat_logs.txt'
        self.logger = logging.getLogger(__name__)
        stdoutHandler = logging.StreamHandler(stream=sys.stdout)
        fileHandler = logging.FileHandler(log_path)
        stdoutFmt = logging.Formatter(
            "%(name)s: %(asctime)s | %(levelname)s | %(process)d >>> %(message)s"
        )
        stdoutHandler.setFormatter(stdoutFmt)
        fileHandler.setFormatter(stdoutFmt)
        self.logger.addHandler(stdoutHandler)
        self.logger.addHandler(fileHandler)

    def info(self, message):
        """Log an info message.

        Args:
            message: The info message to log.
        """
        print(message)
        self.logger.info(message)

    def debug(self, message):
        """Log a debug message.

        Args:
            message: The debug message to log.
        """
        print(message)
        self.logger.debug(message)

    def warning(self, message):
        """Log a warning message.

        Args:
            message: The warning message to log.
        """
        print(message)
        self.logger.warning(message)

    def error(self, message):
        """Log an error message along with the traceback.

        Args:
            message: The error message to log.
        """
        print(message)
        self.logger.error(message)
