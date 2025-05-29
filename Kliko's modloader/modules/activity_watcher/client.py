from typing import Literal, Optional
from dataclasses import dataclass

from modules.logger import Logger

from pypresence import Presence, DiscordNotFound, PipeClosed  # type: ignore


@dataclass
class RichPresenceButton:
    label: str
    url: str


class RichPresenceStatus:
    start: Optional[int] = None
    end: Optional[int] = None
    state: Optional[str] = None
    details: Optional[str] = None
    large_image: Optional[str] = None
    large_text: Optional[str] = None
    small_image: Optional[str] = None
    small_text: Optional[str] = None
    buttons: Optional[list[dict]] = None

    def __init__(self,
            start: Optional[int] = None,
            end: Optional[int] = None,
            state: Optional[str] = None,
            details: Optional[str] = None,
            large_image: Optional[str] = None,
            large_text: Optional[str] = None,
            small_image: Optional[str] = None,
            small_text: Optional[str] = None,
            buttons: Optional[list[RichPresenceButton]] = None
            ):
        if start is not None: self.start = start
        if end is not None: self.end = end
        if state is not None: self.state = state or None
        if details is not None: self.details = details or None
        if large_image is not None: self.large_image = large_image or None
        if large_text is not None: self.large_text = large_text or None
        if small_image is not None: self.small_image = small_image or None
        if small_text is not None: self.small_text = small_text or None
        if buttons is not None: self.buttons = [{"label": button.label, "url": button.url} for button in buttons] or None

    def as_dict(self) -> dict:
        return {
            "start": self.start,
            "end": self.end,
            "state": self.state,
            "details": self.details,
            "large_image": self.large_image,
            "large_text": self.large_text,
            "small_image": self.small_image,
            "small_text": self.small_text,
            "buttons": self.buttons
        }


class RichPresenceClient:
    APP_ID: str = "1229494846247665775"
    _LOG_PREFIX: str = "RichPresenceClient"

    mode: Literal["Player", "Studio"]
    logo_asset_key: str
    client: Presence

    _current_status: dict


    def __init__(self, mode: Literal["Player", "Studio"]):
        Logger.info("Initializing client...", prefix=self._LOG_PREFIX)
        self.mode = mode
        self._current_status = {}
        self.logo_asset_key = "studio" if mode == "Studio" else "roblox"
        self.client = Presence(self.APP_ID)
        Logger.info("Client ready!", prefix=self._LOG_PREFIX)


    def update(self, status: RichPresenceStatus) -> None:
        status_dict: dict = status.as_dict()
        if status_dict == self._current_status:
            return
        self.client.update(**status_dict)
        self._current_status = status_dict


    def set_default_status(self, timestamp: int) -> None:
        status = RichPresenceStatus(
            start=timestamp,
            state="Idle",
            details=f"Roblox {self.mode}",
            large_image=self.logo_asset_key,
            large_text=f"Roblox {self.mode}"
        )
        self.update(status)


    def __enter__(self):
        Logger.info("Connecting client...", prefix=self._LOG_PREFIX)
        self.client.connect()
        return self


    def __exit__(self, *_):
        Logger.info("Closing RPC client...", prefix=self._LOG_PREFIX)

        try:
            self.client.clear()
            self.client.update()
            self.client.close()
        except Exception as e:
            Logger.warning(f"Failed to close RPC client! {type(e).__name__}: {e}", prefix=self._LOG_PREFIX)

        return False