from typing import Literal

from modules.logger import Logger

from pypresence import Presence  # type: ignore


# TODO or REMOVE
class RichPresenceStatus:
    pass


# TODO
class RichPresenceClient:
    APP_ID: str = "1229494846247665775"
    _LOG_PREFIX: str = "RichPresenceClient"

    mode: Literal["Player", "Studio"]
    logo_asset_key: str
    client: Presence


    def __init__(self, mode: Literal["Player", "Studio"]):
        Logger.info("Initializing client...", prefix=self._LOG_PREFIX)
        self.mode = mode
        self.logo_asset_key = "studio" if mode == "Studio" else "roblox"
        self.client = Presence(self.APP_ID)
        Logger.info("Client ready!", prefix=self._LOG_PREFIX)


    def __enter__(self):
        Logger.info("Connecting client...", prefix=self._LOG_PREFIX)
        self.client.connect()
        return self


    def __exit__(self, *_):
        Logger.info("Closing RPC client...", prefix=self._LOG_PREFIX)

        try:
            self.client.clear()
            self.client.close()
        except Exception as e:
            Logger.warning(f"Failed to close RPC client! {type(e).__name__}: {e}", prefix=self._LOG_PREFIX)

        return False