import sys
import logging
import uuid
from typing import Optional
from datetime import datetime, timedelta
from pathlib import Path

from modules import launch_mode
from modules.filesystem import Directory


DIRECTORY: Path = Directory.LOGS
MAX_FILE_AGE: int = 7  # Days


class Logger:
    """
    A wrapper around Python's built-in logging library.

    Attributes:
        filename (str): The name of the current log file.
        filepath (path): The path object of the current log file.
    
    Methods:
        initialize() -> None:
            Sets class attributes and initializes the logger.
        cleanup() -> None:
            Remove old log files.
        info(message: object, *, prefix: Optional[str] = None) -> None:
            Logs an INFO level message.
        warning(message: object, *, prefix: Optional[str] = None) -> None:
            Logs a WARNING level message.
        error(message: object, *, prefix: Optional[str] = None) -> None:
            Logs an ERROR level message.
        debug(message: object, *, prefix: Optional[str] = None) -> None:
            Logs a DEBUG level message.
        critical(message: object, *, prefix: Optional[str] = None) -> None:
            Logs a CRITICAL level message.
    """

    timestamp: str
    filename: str
    filepath: Path
    _initialized: bool = False


    @classmethod
    def initialize(cls) -> None:
        """
        Sets class attributes and initializes the logger.

        Raises:
            RuntimeError: If the logger has already been initialized.
        """

        if cls._initialized:
            raise RuntimeError(f"Logger cannot be initialized more than once.")

        DIRECTORY.mkdir(parents=True, exist_ok=True)

        timestamp: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        mode: str = launch_mode.get().upper()
        id: str = uuid.uuid4().hex[:5].upper()

        cls.timestamp = timestamp
        cls.filename = f"{timestamp}_{mode}_{id}.log"
        cls.filepath = DIRECTORY / cls.filename

        logging.basicConfig(
            filename=cls.filepath,
            level=logging.DEBUG,
            format="%(asctime)s.%(msecs)03d | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
            encoding="utf-8"
        )
        logging.getLogger("PIL").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("pyi_splash").setLevel(logging.WARNING)

        cls._initialized = True


    @classmethod
    def cleanup(cls) -> None:
        """Remove old log files."""

        for log in DIRECTORY.iterdir():
            if not log.is_file():
                continue

            age: timedelta = datetime.now() - datetime.fromtimestamp(log.stat().st_mtime)
            if age > timedelta(days=MAX_FILE_AGE):
                try:
                    log.unlink()
                    cls.info(f"Removed old log: {log.name}", prefix="Logger.cleanup()")
                except (PermissionError, OSError) as e:
                    cls.warning(f"Failed to remove old log: {log.name}! {e}", prefix="Logger.cleanup()")


    @classmethod
    def _log(cls, level: int, message: object, prefix: Optional[str] = None) -> None:
        """
        Logs a message with the specified log level.

        Parameters:
            level (int): The logging level (logging.INFO, logging.WARNING, etc.).
            message (object): The message to log.
            prefix (Optional[str]): An optional prefix to add to the log message.

        Raises:
            RuntimeError: If the logger was not yet initialized.
        """

        if not cls._initialized:
            raise RuntimeError(f"Logger has not been initialized")

        msg: object = f"[{prefix}] {message}" if prefix is not None else message
        logging.log(level, msg)


    @classmethod
    def info(cls, message: object, *, prefix: Optional[str] = None) -> None:
        """
        Logs an INFO level message.

        Parameters:
            message (object): The message to log.
            prefix (Optional[str]): An optional prefix to add to the log message.

        Raises:
            RuntimeError: If the logger was not yet initialized.
        """

        cls._log(logging.INFO, message, prefix)


    @classmethod
    def warning(cls, message: object, *, prefix: Optional[str] = None) -> None:
        """
        Logs a WARNING level message.

        Parameters:
            message (object): The message to log.
            prefix (Optional[str]): An optional prefix to add to the log message.

        Raises:
            RuntimeError: If the logger was not yet initialized.
        """
        
        cls._log(logging.WARNING, message, prefix)


    @classmethod
    def error(cls, message: object, *, prefix: Optional[str] = None) -> None:
        """
        Logs an ERROR level message.

        Parameters:
            message (object): The message to log.
            prefix (Optional[str]): An optional prefix to add to the log message.

        Raises:
            RuntimeError: If the logger was not yet initialized.
        """
        
        cls._log(logging.ERROR, message, prefix)


    @classmethod
    def debug(cls, message: object, *, prefix: Optional[str] = None) -> None:
        """
        Logs a DEBUG level message.

        Parameters:
            message (object): The message to log.
            prefix (Optional[str]): An optional prefix to add to the log message.

        Raises:
            RuntimeError: If the logger was not yet initialized.
        """
        
        cls._log(logging.DEBUG, message, prefix)


    @classmethod
    def critical(cls, message: object, *, prefix: Optional[str] = None) -> None:
        """
        Logs a CRITICAL level message.

        Parameters:
            message (object): The message to log.
            prefix (Optional[str]): An optional prefix to add to the log message.

        Raises:
            RuntimeError: If the logger was not yet initialized.
        """
        
        cls._log(logging.CRITICAL, message, prefix)


Logger.initialize()