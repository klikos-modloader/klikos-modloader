from pathlib import Path
from typing import Optional
import sys
import logging
import uuid
from datetime import datetime, timedelta


DIRECTORY: Path = (Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent.parent).resolve() / "Logs"
MAX_FILE_AGE: int = 7  # Days


class Logger:
    timestamp: str
    filename: str
    filepath: Path
    _initialized: bool = False

    @classmethod
    def initialize(cls) -> None:
        if cls._initialized: raise RuntimeError("Logger has already been initialized.")
        DIRECTORY.mkdir(parents=True, exist_ok=True)

        cls.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        cls.filename = f"{cls.timestamp}_{uuid.uuid4().hex[:5].upper()}.log"
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
        cls.info("Clearning old logs...", prefix="Logger.cleanup()")
        for log in DIRECTORY.iterdir():
            if not log.is_file(): continue

            age: timedelta = datetime.now() - datetime.fromtimestamp(log.stat().st_mtime)
            if age > timedelta(days=MAX_FILE_AGE):
                try:
                    log.unlink()
                    cls.info(f"Removed log file: {log.name}", prefix="Logger.cleanup()")
                except (PermissionError, OSError) as e:
                    cls.warning(f"Unable to remove log file: {log.name}!", prefix="Logger.cleanup()")


    @classmethod
    def write(cls, level: int, message: object, prefix: Optional[str] = None) -> None:
        if not cls._initialized: cls.initialize()
        msg: object = f"[{prefix}] {message}" if prefix is not None else message
        logging.log(level, msg)


    @classmethod
    def info(cls, message: object, *, prefix: Optional[str] = None) -> None: cls.write(logging.INFO, message, prefix)

    @classmethod
    def warning(cls, message: object, *, prefix: Optional[str] = None) -> None: cls.write(logging.WARNING, message, prefix)

    @classmethod
    def error(cls, message: object, *, prefix: Optional[str] = None) -> None: cls.write(logging.ERROR, message, prefix)

    @classmethod
    def debug(cls, message: object, *, prefix: Optional[str] = None) -> None: cls.write(logging.DEBUG, message, prefix)

    @classmethod
    def critical(cls, message: object, *, prefix: Optional[str] = None) -> None: cls.write(logging.CRITICAL, message, prefix)