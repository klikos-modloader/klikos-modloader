from typing import Optional, Literal
import traceback
import time

from modules.logger import Logger
from modules.interfaces.roblox import RobloxInterface

from .client import RichPresenceClient, DiscordNotFound, PipeClosed
from .reader import LogReader


class ActivityWatcher:
    mode: Literal["Player", "Studio"]
    reader: LogReader
    timestamp: int

    _LOG_PREFIX: str = "ActivityWatcher"
    _COOLDOWN_MS: int = 250


    def run(self, mode: Optional[Literal["Player", "Studio"]] = None) -> None:
        Logger.info("Initializing Activity Watcher...", prefix=self._LOG_PREFIX)
        if mode is None:
            mode = self._auto_detect_mode()
        self.mode = mode
        Logger.info(f"RPC mode: {mode}", prefix=self._LOG_PREFIX)

        if not RobloxInterface.is_roblox_running(mode):
            self._wait_until_running()

        try:
            self.timestamp = int(time.time())
            cooldown: float = self._COOLDOWN_MS / 1000
            self.reader = LogReader(mode)
            with RichPresenceClient(mode) as client:
                while self._should_run():  # mainloop
                    # TODO
                    time.sleep(cooldown)
                    return

        except DiscordNotFound:
            Logger.warning("Discord not found!", prefix=self._LOG_PREFIX)

        except PipeClosed:
            Logger.warning("Pipe closed!", prefix=self._LOG_PREFIX)

        except Exception as e:  # Fail silently
            Logger.error(f"{type(e).__name__}: {e}", prefix=self._LOG_PREFIX)
            Logger.debug(f"\n\n{"\n".join(traceback.format_exception(e))}")


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


    def _should_run(self) -> bool:
        if not RobloxInterface.is_roblox_running(self.mode):
            return False
        # TODO: Check for last lof entry in log file
        return True