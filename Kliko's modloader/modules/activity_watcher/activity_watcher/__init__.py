from typing import Optional, Literal, NamedTuple
from dataclasses import dataclass
import traceback
import time
import re

from modules.logger import Logger
from modules.interfaces.roblox import RobloxInterface
from modules.interfaces.config import ConfigInterface
from modules.networking import requests, Response, Api

from .client import RichPresenceClient, DiscordNotFound, PipeClosed, RichPresenceStatus, RichPresenceButton
from .reader import LogReader, LogEntry
from .data import Data
from .bloxstrap_rpc_data import BloxstrapRPC


class Config(NamedTuple):
    bloxstrap_rpc: bool
    activity_joining: bool
    show_user_profile: bool


@dataclass
class GameData:
    timestamp: int | None = None
    server_id: str | None = None
    place_id: str | None = None
    root_place_id: str | None = None
    user_id: str | None = None
    name: str | None = None
    creator: str | None = None
    thumbnail: str | None = None
    bloxstrap_rpc: BloxstrapRPC | None = None


class ActivityWatcher:
    mode: Literal["Player", "Studio"]
    reader: LogReader
    timestamp: int
    config: Config

    _data: GameData
    _last_data: GameData | None = None

    _LOG_PREFIX: str = "ActivityWatcher"
    _COOLDOWN_MS: int = 250
    _CONFIG_UPDATE_INTERVAL_LOOPS: int = 4  # Every _COOLDOWN_MS * _CONFIG_UPDATE_INTERVAL_LOOPS ms


    def run(self, mode: Optional[Literal["Player", "Studio"]] = None) -> None:
        Logger.info("Initializing Activity Watcher...", prefix=self._LOG_PREFIX)
        self._data = GameData()
        if mode is None:
            mode = self._auto_detect_mode()
        self.mode = mode
        Logger.info(f"RPC mode: {mode}", prefix=self._LOG_PREFIX)

        if not RobloxInterface.is_roblox_running(mode):
            self._wait_until_running()

        activity_joining: bool = ConfigInterface.get("activity_joining")
        show_user_in_rpc: bool = ConfigInterface.get("show_user_in_rpc")
        bloxstrap_rpc_sdk: bool = ConfigInterface.get("bloxstrap_rpc_sdk")
        self.config = Config(bloxstrap_rpc=bloxstrap_rpc_sdk, activity_joining=activity_joining, show_user_profile=show_user_in_rpc)

        try:
            self.timestamp = int(time.time())
            cooldown: float = self._COOLDOWN_MS / 1000
            self.reader = LogReader(mode)

            with RichPresenceClient(mode) as client:
                client.set_default_status(self.timestamp)
                loop_counter: int = 0
                while RobloxInterface.is_roblox_running(self.mode):  # mainloop
                    loop_counter += 1
                    forced_update: bool = False
                    if loop_counter % self._CONFIG_UPDATE_INTERVAL_LOOPS == 0:
                        print("TEST")
                        activity_joining = ConfigInterface.get("activity_joining")
                        show_user_in_rpc = ConfigInterface.get("show_user_in_rpc")
                        bloxstrap_rpc_sdk = ConfigInterface.get("bloxstrap_rpc_sdk")
                        new_config: Config = Config(bloxstrap_rpc=bloxstrap_rpc_sdk, activity_joining=activity_joining, show_user_profile=show_user_in_rpc)
                        if new_config != (self.config):
                            print("TEST 2 !!!")
                            self.config = Config(bloxstrap_rpc=bloxstrap_rpc_sdk, activity_joining=activity_joining, show_user_profile=show_user_in_rpc)
                            forced_update = True

                    entries: list[LogEntry] = self.reader.read_new()

                    if not entries:
                        time.sleep(cooldown)
                        continue

                    if self._is_exit_message(entries[-1]):
                        return

                    result: Literal["update", "default"] | None = self._process_entries(entries)
                    if result == "default":
                        client.set_default_status(self.timestamp)

                    elif result == "update" or forced_update:
                        if not forced_update:
                            self._last_data = self._data
                        game_data: GameData = self._last_data
                        start: Optional[int] = game_data.timestamp
                        end: Optional[int] = None
                        state: Optional[str] = f"By {game_data.creator}"
                        details: Optional[str] = f"Editing {game_data.name}..." if self.mode == "Studio" else f"Playing {game_data.name}..."
                        large_image: Optional[str] = game_data.thumbnail
                        large_text: Optional[str] = game_data.name
                        small_image: Optional[str] = client.logo_asset_key
                        small_text: Optional[str] = "Roblox Studio" if self.mode == "Studio" else "Roblox"
                        buttons: Optional[list[RichPresenceButton]] = [RichPresenceButton("View on Roblox", Api.Roblox.Activity.page(game_data.root_place_id))]

                        if self.mode == "Studio" and self.config.activity_joining:
                            buttons.insert(0, RichPresenceButton("Join Server", Api.Roblox.Activity.deeplink(game_data.place_id, game_data.server_id)))

                        if self.config.show_user_profile:
                            response: Response = requests.get(Api.Roblox.Activity.user(game_data.user_id))
                            data: dict = response.json()
                            small_text: str = data.get("displayName", data["name"])

                            response = requests.get(Api.Roblox.Activity.user_thumbnail(game_data.user_id))
                            data = response.json()
                            actual_data: dict = data["data"][0]
                            small_image: str = actual_data["imageUrl"]

                        if self.config.bloxstrap_rpc and game_data.bloxstrap_rpc is not None:
                            # TODO
                            pass

                        status = RichPresenceStatus(
                            start=start, end=end,
                            state=state, details=details,
                            large_image=large_image, large_text=large_text,
                            small_image=small_image, small_text=small_text,
                            buttons=buttons
                        )

                        client.update(status)

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
        return_value: Literal["update", "default"] | None = None

        match self.mode:
            case "Player":
                for entry in entries:
                    if entry.prefix == Data.Player.GameID.prefix and entry.message.startswith(Data.Player.GameID.startswith):
                        split_message: list[str] = entry.message.removeprefix(Data.Player.GameID.startswith).split()
                        server_id: str = split_message[0].strip("'")
                        self._data = GameData(timestamp=int(entry.timestamp), server_id=server_id)

                    elif entry.prefix == Data.Player.Join.prefix and entry.message.startswith(Data.Player.Join.startswith):
                        pattern = r"placeid:(\d+).*?universeid:(\d+).*?userid:(\d+)"
                        match = re.search(pattern, entry.message)
                        if match:
                            self._data.place_id = match.group(1)
                            universe_id = match.group(2)
                            self._data.user_id = match.group(3)

                            response: Response = requests.get(Api.Roblox.Activity.game(universe_id))
                            data: dict = response.json()
                            actual_data: dict = data["data"][0]
                            self._data.root_place_id = actual_data["rootPlaceId"]
                            self._data.name = actual_data["name"]
                            self._data.creator = actual_data["creator"]["name"]

                            response = requests.get(Api.Roblox.Activity.thumbnail(universe_id))
                            data = response.json()
                            actual_data: dict = data["data"][0]
                            self._data.thumbnail = actual_data["imageUrl"]

                            return_value = "update"


                    elif entry.prefix == Data.BloxstrapRPC.prefix and entry.message.startswith(Data.BloxstrapRPC.startswith):
                        print("BloxstrapRPC detected!")
                        print(f"\n\n{entry.message}\n\n")

                        # return_value = "update"


                    elif entry.prefix == Data.Player.Leave.prefix and entry.message == Data.Player.Leave.message:
                        return_value = "default"

            case "Studio":
                for entry in entries:
                    if entry.prefix == Data.Studio.Leave.prefix and entry.message == Data.Studio.Leave.message:
                        return_value = "default"

        return return_value