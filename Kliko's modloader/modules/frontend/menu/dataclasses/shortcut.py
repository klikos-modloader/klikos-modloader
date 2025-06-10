from typing import Optional
from pathlib import Path
from io import BytesIO
import time
import json
import hashlib

from modules.logger import Logger
from modules.filesystem import Files, Directories
from modules.networking import requests, Response, Api

from PIL import Image  # type: ignore


# region Shortcut
class Shortcut:
    name: str
    creator: str
    universe_id: str
    place_id: str
    thumbnail_url: str

    THUMBNAIL_ASPECT_RATIO: float = 1

    _thumbnail_placeholder: tuple[Image.Image, Image.Image]
    _THUMBNAIL_CACHE_DURATION: int = 2678400  # 31 days
    _LOG_PREFIX: str = "Shortcut"


    def __init__(self, universe_id: str | int, placeholder_thumbnail: tuple[Image.Image, Image.Image]):
        if isinstance(universe_id, int): universe_id = str(universe_id)
        self.universe_id = universe_id
        self._thumbnail_placeholder = placeholder_thumbnail
        self.set_game_info()


# region game info
    def set_game_info(self) -> None:
        response = requests.get(Api.Roblox.Activity.game(self.universe_id))
        data = response.json()
        actual_data = data["data"][0]
        self.name = actual_data["name"]
        self.creator = actual_data["creator"]["name"]
        self.place_id = actual_data["rootPlaceId"]

        response = requests.get(Api.Roblox.Activity.thumbnail(self.universe_id))
        data = response.json()
        actual_data = data["data"][0]
        self.thumbnail_url = actual_data["imageUrl"]
# endregion


# region thumbnail
    def get_thumbnail(self) -> Image.Image | tuple[Image.Image, Image.Image]:
        if not self.thumbnail_url: return self._thumbnail_placeholder

        target: Path = Directories.SHORTCUTS_CACHE / f"{self.place_id}.png"
        if not target.exists() or not Files.SHORTCUTS_CACHE_INDEX.exists():
            return self._attempt_thumbnail_download()

        with open(Files.SHORTCUTS_CACHE_INDEX) as file:
            data: dict = json.load(file)
        item: dict | None = data.get(self.place_id)
        if not item:
            return self._attempt_thumbnail_download()

        url: str | None = item.get("url")
        md5: str | None = item.get("md5")
        timestamp: int | None = item.get("timestamp")

        if (
            not url
            or not md5
            or not timestamp
            or url != self.thumbnail_url
            or md5 != self._get_md5(target)
            or (time.time() - timestamp) > self._THUMBNAIL_CACHE_DURATION
        ):
            return self._attempt_thumbnail_download()

        try: return Image.open(target)
        except Exception: return self._thumbnail_placeholder


    def _attempt_thumbnail_download(self) -> Image.Image | tuple[Image.Image, Image.Image]:
        try: return self._download_thumbnail()
        except Exception as e:
            Logger.warning(f"Failed to download thumbnail: '{self.place_id}'! {type(e).__name__}: {e}", prefix=self._LOG_PREFIX)
            return self._thumbnail_placeholder


    def _download_thumbnail(self) -> Image.Image:
        Logger.info(f"Downloading thumbnail: '{self.place_id}'...", prefix=self._LOG_PREFIX)

        response: Response = requests.get(self.thumbnail_url, attempts=1, cache=False)  # type: ignore

        with BytesIO(response.content) as buffer:
            image: Image.Image = Image.open(buffer)
            image.load()
        Directories.SHORTCUTS_CACHE.mkdir(parents=True, exist_ok=True)
        target: Path = Directories.SHORTCUTS_CACHE / f"{self.place_id}.png"
        image.save(target)
        
        if Files.SHORTCUTS_CACHE_INDEX.exists():
            with open(Files.SHORTCUTS_CACHE_INDEX) as file:
                data: dict = json.load(file)
        else: data = {}

        md5: str = self._get_md5(target)
        timestamp: int = int(time.time())
        data[self.place_id] = {"url": self.thumbnail_url, "md5": md5, "timestamp": timestamp}

        with open(Files.SHORTCUTS_CACHE_INDEX, "w") as file:
            json.dump(data, file, indent=4)

        return image


    def _get_md5(self, path: Path) -> str:
            hasher = hashlib.md5()
            with open(path, "rb") as file:
                for chunk in iter(lambda: file.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest().upper()
# endregion
# endregion