import logging
import os

class Logger:
    """
    Class for handling log messages.
    """

    def __init__(self, logFilePath="./logs/app.log"):
        """
        Initializes the logger and ensures the log directory exists.

        Args:
            logFilePath (str, optional): The file path where logs will be saved. Defaults to "./logs/app.log".
        """
        # Ensure the log directory exists
        os.makedirs(os.path.dirname(logFilePath), exist_ok=True)

        # Logging configuration
        logging.basicConfig(
            filename=logFilePath,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            encoding="utf-8",
        )
        self.logger = logging.getLogger()

    def logInfo(self, message):
        """
        Logs an informational message.

        Args:
            message (str): The message to log.
        """
        self.logger.info(message)

    def logError(self, message):
        """
        Logs an error message.

        Args:
            message (str): The error message to log.
        """
        self.logger.error(message)

    def logCritical(self, message):
        """
        Logs a critical error message.

        Args:
            message (str): The critical message to log.
        """
        self.logger.critical(message)
