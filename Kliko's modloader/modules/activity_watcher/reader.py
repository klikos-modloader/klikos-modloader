from typing import Literal

from modules.logger import Logger


# TODO
class LogReader:
    _LOG_PREFIX: str = "LogReader"

    mode: Literal["Player", "Studio"]


    def __init__(self, mode: Literal["Player", "Studio"]):
        Logger.info("Initializing log reader...", prefix=self._LOG_PREFIX)
        self.mode = mode