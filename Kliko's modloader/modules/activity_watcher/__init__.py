from typing import Optional, Literal
import time

from modules.logger import Logger
from modules.interfaces.roblox import RobloxInterface

from .client import RichPresenceClient
from .reader import LogReader


class ActivityWatcher:
    mode: Literal["Player", "Studio"]

    _running: bool = False

    _LOG_PREFIX: str = "ActivityWatcher"


    def __init__(self):
        Logger.info("Initializing Activity Watcher...", prefix=self._LOG_PREFIX)
        pass


    def run(self, mode: Optional[Literal["Player", "Studio"]] = None) -> None:
        if mode is None:
            mode = self._auto_detect_mode()
        self.mode = mode
        Logger.info(f"RPC mode: {mode}", prefix=self._LOG_PREFIX)

        client = RichPresenceClient(mode)
        reader = LogReader(mode)

        if not RobloxInterface.is_roblox_running(mode):
            self._wait_until_running()

        raise NotImplementedError("RPC has not yet been implemented!")
        with client:
            # TODO
            pass


    def _auto_detect_mode(self, attempts: int = 3, cooldown_ms: int = 500) -> Literal["Player", "Studio"]:
        Logger.info("Auto-detecting RPC mode...", prefix=self._LOG_PREFIX)
        cooldown: float = cooldown_ms / 1000
        for _ in range(attempts):
            if RobloxInterface.is_roblox_running("Player"):
                return "Player"
            elif RobloxInterface.is_roblox_running("Studio"):
                return "Studio"
            time.sleep(cooldown)

        Logger.error("Failed to detect RPC mode!", prefix=self._LOG_PREFIX)
        raise Exception("Failed to detect RPC mode!")


    def _wait_until_running(self, attempts: int = 60, cooldown_ms: int = 1000) -> None:
        Logger.info("Waiting until Roblox is running...", prefix=self._LOG_PREFIX)

        cooldown: float = cooldown_ms / 1000
        for _ in range(attempts):
            if RobloxInterface.is_roblox_running(self.mode):
                Logger.info("Roblox launch detected!", prefix=self._LOG_PREFIX)
                return
            time.sleep(cooldown)

        Logger.error(f"Failed to detect Roblox launch after {60*cooldown:.1f} seconds!", prefix=self._LOG_PREFIX)
        raise TimeoutError(f"Failed to detect Roblox launch after {60*cooldown:.1f} seconds!")