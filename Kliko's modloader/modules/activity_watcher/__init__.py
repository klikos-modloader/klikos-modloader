from typing import Optional, Literal
from dataclasses import dataclass
import traceback
import time

from modules.logger import Logger
from modules.interfaces.roblox import RobloxInterface

from .client import RichPresenceClient, DiscordNotFound, PipeClosed, RichPresenceStatus, RichPresenceButton
from .reader import LogReader, LogEntry
from .data import Data


@dataclass
class GameData:
    game_id: str | None = None
    place_id: str | None = None
    name: str | None = None
    creator: str | None = None
    is_private: bool = None
    is_reserved: bool = None


class ActivityWatcher:
    mode: Literal["Player", "Studio"]
    reader: LogReader
    timestamp: int

    _data: GameData
    _status: RichPresenceStatus

    _LOG_PREFIX: str = "ActivityWatcher"
    _COOLDOWN_MS: int = 250


    def run(self, mode: Optional[Literal["Player", "Studio"]] = None) -> None:
        Logger.info("Initializing Activity Watcher...", prefix=self._LOG_PREFIX)
        self._data = GameData()
        self._status = RichPresenceStatus()
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
                client.set_default_status(self.timestamp)
                while RobloxInterface.is_roblox_running(self.mode):  # mainloop
                    entries: list[LogEntry] = self.reader.read_new()

                    if not entries:
                        time.sleep(cooldown)
                        continue

                    if self._is_exit_message(entries[-1]):
                        return

                    result: Literal["update", "default"] | None = self._process_entries(entries)
                    if result == "update":
                        client.update(self._status)
                    elif result == "default":
                        client.update(self._status)

                    time.sleep(cooldown)

        except DiscordNotFound:
            Logger.warning("Discord not found!", prefix=self._LOG_PREFIX)

        except PipeClosed:
            Logger.warning("Pipe closed!", prefix=self._LOG_PREFIX)

        except Exception as e:  # Fail silently
            Logger.error(f"{type(e).__name__}: {e}", prefix=self._LOG_PREFIX)
            Logger.debug(f"\n\n{"\n".join(traceback.format_exception(e))}")

        else:
            Logger.info("Exiting Activity Watcher!", prefix=self._LOG_PREFIX)


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


    def _is_exit_message(self, entry: LogEntry) -> bool:
        match self.mode:
            case "Player": return entry.prefix == Data.Player.Exit.prefix and entry.message == Data.Player.Exit.message
            case "Studio": return entry.prefix == Data.Studio.Exit.prefix and entry.message == Data.Studio.Exit.message


    def _process_entries(self, entries: list[LogEntry]) -> Literal["update", "default"] | None:
        match self.mode:
            case "Player":
                for entry in entries:
                    if entry.prefix == Data.Player.Leave.prefix and entry.message == Data.Player.Leave.message:
                        return "default"

            case "Studio":
                for entry in entries:
                    if entry.prefix == Data.Studio.Leave.prefix and entry.message == Data.Studio.Leave.message:
                        return "default"

        return None