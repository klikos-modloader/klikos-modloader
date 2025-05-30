from typing import Optional, Literal
from pathlib import Path
from datetime import datetime, timezone
import time
import re

from modules.logger import Logger
from modules.filesystem import Directories


class LogEntry:
    full: str
    timestamp: float
    level: Optional[str] = None
    metadata: str
    prefix: Optional[str] = None
    message: str

    def __init__(self, data: str) -> None:
        self.full = data.strip()
        split_data: list[str] = data.split()

        self.metadata = split_data[0]
        split_metadata = self.metadata.split(",")
        self.timestamp = datetime.strptime(split_metadata[0], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc).timestamp()
        level: str = split_metadata[-1]
        if not level.isdigit():
            self.level = level

        prefix: str = split_data[1]
        if prefix.startswith("[") and prefix.endswith("]"):
            self.prefix = prefix
            self.message = self.full.replace(self.metadata, "", 1).replace(self.prefix, "", 1).strip()
        else:
            self.message = self.full.replace(self.metadata, "", 1).strip()



class LogReader:
    DIRECTORY: Path = Directories.ROBLOX / "Logs"
    _LOG_PREFIX: str = "LogReader"

    mode: Literal["Player", "Studio"]
    log_file: Path
    _position: int = 0


    def __init__(self, mode: Literal["Player", "Studio"]):
        Logger.info("Initializing log reader...", prefix=self._LOG_PREFIX)
        self.mode = mode
        self._readlines = []
        self._set_latest_log_file()


    def _set_latest_log_file(self) -> None:
        Logger.info("Finding latest log file...", prefix=self._LOG_PREFIX)
        time.sleep(3)  # just to make sure the latest log file exists
        log_files: list[Path] = list(self.DIRECTORY.glob(f"*_{self.mode}_*.log", case_sensitive=False))
        if not log_files:
            raise FileNotFoundError("No log files found!")
        latest: Path = max(log_files, key=lambda file: file.stat().st_mtime)
        self.log_file: Path = latest
        Logger.info(f"Log found: '{latest.name}'", prefix=self._LOG_PREFIX)


    def read_new(self) -> list[LogEntry]:
        with open(self.log_file) as file:
            file.seek(self._position)
            new: str = file.read()
            self._position = file.tell()

        pattern: str = r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z.*?)(?=^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z|$)'
        matches = re.findall(pattern, new, re.DOTALL | re.MULTILINE)

        entries: list[LogEntry] = []
        for entry in matches:
            try: entries.append(LogEntry(entry))
            except Exception: pass
        return entries