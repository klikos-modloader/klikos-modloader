from typing import Literal
from pathlib import Path
import time

from modules.logger import Logger
from modules.filesystem import Directories


class LogReader:
    DIRECTORY: Path = Directories.ROBLOX / "Logs"
    _LOG_PREFIX: str = "LogReader"

    mode: Literal["Player", "Studio"]


    def __init__(self, mode: Literal["Player", "Studio"]):
        Logger.info("Initializing log reader...", prefix=self._LOG_PREFIX)
        self.mode = mode
        time.sleep(0.5)  # just to make sure the latest log file exists
        self._set_latest_log_file()


    def _set_latest_log_file(self) -> None:
        Logger.info("Finding latest log file...", prefix=self._LOG_PREFIX)
        log_files: list[Path] = list(self.DIRECTORY.glob(f"*_{self.mode}_*.log", case_sensitive=False))
        if not log_files:
            raise FileNotFoundError("No log files found!")
        latest: Path = max(log_files, key=lambda file: file.stat().st_mtime)
        self.log_file: Path = latest
        Logger.info(f"Log found: '{latest.name}'", prefix=self._LOG_PREFIX)


    def read_newlines(self) -> list[str]:
        return []