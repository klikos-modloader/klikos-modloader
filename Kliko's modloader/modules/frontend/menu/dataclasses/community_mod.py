from typing import Optional
from pathlib import Path
from io import BytesIO
import time
import json
import hashlib

from modules.logger import Logger
from modules.filesystem import Files, Directories

from PIL import Image  # type: ignore


# region CommunityMod
class CommunityMod:
    id: str
    name: str
    download_url: str
    description: Optional[str]
    owner: Optional[str]
    thumbnail_url: Optional[str]

    THUMBNAIL_ASPECT_RATIO: float = 16/9

    _thumbnail_placeholder: tuple[Image.Image, Image.Image]
    _THUMBNAIL_CACHE_DURATION: int = 604800  # 7 days
    _LOG_PREFIX: str = "CommunityMod"


    def __init__(self, data: dict, placeholder_thumbnail: tuple[Image.Image, Image.Image]):
        id: str | None = data.get("id")
        name: str | None = data.get("name")
        download_url: str | None = data.get("download")

        if id is None: raise ValueError("Mod ID cannot be None")
        if name is None: raise ValueError("Mod name cannot be None")
        if download_url is None: raise ValueError("Mod download URL cannot be None")

        self.id = id
        self.name = name
        self.download_url = download_url

        self.description = data.get("description")
        self.author = data.get("author")
        self.thumbnail_url = data.get("thumbnail")
        self._thumbnail_placeholder = placeholder_thumbnail


# region thumbnail
    def get_thumbnail(self) -> Image.Image | tuple[Image.Image, Image.Image]:
        if not self.thumbnail_url: return self._thumbnail_placeholder

        target: Path = Directories.MARKETPLACE_CACHE / f"{self.id}.png"
        if not target.exists() or not Files.MARKETPLACE_CACHE_INDEX.exists():
            return self._attempt_thumbnail_download()

        with open(Files.MARKETPLACE_CACHE_INDEX) as file:
            data: dict = json.load(file)
        item: dict | None = data.get(self.id)
        if not item: return self._attempt_thumbnail_download()

        url: str | None = item.get("url")
        md5: str | None = item.get("md5")
        timestamp: int | None = item.get("timestamp")

        if (
            not url or
            not md5 or
            not timestamp or
            url != self.thumbnail_url or
            md5 != self._get_md5(target) or
            timestamp < (time.time() - self._THUMBNAIL_CACHE_DURATION)
        ): return self._attempt_thumbnail_download()

        try: return Image.open(target)
        except Exception: return self._thumbnail_placeholder


    def _attempt_thumbnail_download(self) -> Image.Image | tuple[Image.Image, Image.Image]:
        try: return self._download_thumbnail()
        except Exception as e:
            Logger.warning(f"Failed to download thumbnail: '{self.id}'! {type(e).__name__}: {e}", prefix=self._LOG_PREFIX)
            return self._thumbnail_placeholder


    def _download_thumbnail(self) -> Image.Image:
        Logger.info(f"Downloading thumbnail: '{self.id}'...", prefix=self._LOG_PREFIX)

        response: Response = requests.get(self.thumbnail_url, attempts=1, cache=False)  # type: ignore

        with BytesIO(response.content) as buffer:
            image: Image.Image = Image.open(buffer)
            image.load()
        Directories.MARKETPLACE_CACHE.mkdir(parents=True, exist_ok=True)
        target: Path = Directories.MARKETPLACE_CACHE / f"{self.id}.png"
        image.save(target)
        
        if Files.MARKETPLACE_CACHE_INDEX.exists():
            with open(Files.MARKETPLACE_CACHE_INDEX) as file:
                data: dict = json.load(file)
        else: data = {}

        md5: str = hashlib.md5(response.content).hexdigest().upper()
        timestamp: int = int(time.time())
        data[self.id] = {"url": self.thumbnail_url, "md5": md5, "timestamp": timestamp}

        with open(Files.MARKETPLACE_CACHE_INDEX, "w") as file:
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