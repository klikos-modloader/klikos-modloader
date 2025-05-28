from typing import Optional, Literal
import time

from modules.logger import Logger
from modules.interfaces.roblox import RobloxInterface


class ActivityWatcher:
    _running: bool = False

    _LOG_PREFIX: str = "ActivityWatcher"


    @classmethod
    def run(cls, mode: Optional[Literal["Player", "Studio"]] = None) -> None:
        Logger.info("Running RPC mode...", prefix=cls._LOG_PREFIX)
        if mode is None:
            mode = cls._auto_detect_mode()
            if mode is None:
                raise Exception("Failed to detect RPC mode!")
        raise NotImplementedError("RPC has not yet been implemented!")


    @classmethod
    def _auto_detect_mode(cls, attempts: int = 3, cooldown_ms: int = 500) -> Literal["Player", "Studio"] | None:
        cooldown: float = cooldown_ms / 1000

        for _ in range(attempts):
            if RobloxInterface.is_roblox_running("Player"):
                return "Player"
            elif RobloxInterface.is_roblox_running("Studio"):
                return "Studio"
            time.sleep(cooldown)
        return None