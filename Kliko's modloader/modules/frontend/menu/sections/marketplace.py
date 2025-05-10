from tkinter import TclError
from threading import Thread
from typing import Optional, TYPE_CHECKING
from io import BytesIO
from pathlib import Path
import json
import time
import hashlib

from modules.logger import Logger
from modules.project_data import ProjectData
from modules.frontend.widgets import ScrollableFrame, Frame, Label, Button, FlexBox
from modules.frontend.functions import get_ctk_image, apply_rounded_corners
from modules.localization import Localizer
from modules.filesystem import Files, Directories, Resources
from modules import filesystem
from modules.networking import requests, Response, Api

if TYPE_CHECKING: from modules.frontend.widgets import Root

from customtkinter import CTkImage  # type: ignore
from PIL import Image  # ype: ignore


# region CommunityMod
class CommunityMod:
    id: str
    name: str
    download_url: str
    description: Optional[str]
    owner: Optional[str]
    thumbnail_url: Optional[str]

    _thumbnail_placeholder: tuple[Image.Image, Image.Image]
    _THUMBNAIL_CACHE_DURATION: int = 604800  # 7 days


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
            Logger.warning(f"Failed to download thumbnail: '{self.id}'! {type(e).__name__}: {e}", prefix="marketplace")
            return self._thumbnail_placeholder


    def _download_thumbnail(self) -> Image.Image:
        Logger.info(f"Downloading thumbnail: '{self.id}'...", prefix="marketplace")

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


# region MarketplaceSection
class MarketplaceSection(ScrollableFrame):
    loaded: bool = False
    root: "Root"

    placeholder_thumbnail: tuple[Image.Image, Image.Image]

    _SECTION_PADX: int | tuple[int, int] = (8, 4)
    _SECTION_PADY: int | tuple[int, int] = 8
    _ENTRY_GAP: int = 8
    _ENTRY_PADDING: tuple[int , int] = (8, 8)
    _ENTRY_INNER_GAP: int = 8
    _COLUMN_WIDTH: int = 255
    _ENTRY_INNER_WIDTH: int = _COLUMN_WIDTH - 2 * _ENTRY_PADDING[0]
    _ENTRY_THUMBNAIL_ASPECT_RATIO: float = 16/9
    _ENTRY_THUMBNAIL_SIZE: tuple[int, int] = (_ENTRY_INNER_WIDTH, int(_ENTRY_INNER_WIDTH/_ENTRY_THUMBNAIL_ASPECT_RATIO))
    _ROW_HEIGHT: int = _ENTRY_THUMBNAIL_SIZE[1]+2*_ENTRY_PADDING[1]+_ENTRY_INNER_GAP*2+28*2+32  # 28 = label, 32 = button


    def __init__(self, master):
        super().__init__(master, transparent=False, round=True, border=True, layer=1)
        self.root = master
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


    def clear(self) -> None:
        for widget in self.winfo_children():
            try: widget.destroy()
            except TclError: pass
        self.loaded = False


    def refresh(self) -> None:
        self.clear()
        self.show()


    def show(self) -> None:
        self.load()


# region load
    def load(self) -> None:
        if self.loaded: return

        self.placeholder_thumbnail = (Image.open(Resources.Marketplace.Light.PLACEHOLDER), Image.open(Resources.Marketplace.Dark.PLACEHOLDER))

        content: Frame = Frame(self, transparent=True)
        content.grid_columnconfigure(0, weight=1)
        content.grid(column=0, row=0, sticky="nsew", padx=self._SECTION_PADX, pady=self._SECTION_PADY)

        self._load_header(content)
        self._load_content(content)

        self.loaded = True


    def _load_header(self, master) -> None:
        header: Frame = Frame(master, transparent=True)
        header.grid_columnconfigure(0, weight=1)
        header.grid(column=0, row=0, sticky="nsew", pady=(0,16))

        Label(header, "menu.marketplace.header.title", style="title", autowrap=True).grid(column=0, row=0, sticky="ew")
        Label(header, "menu.marketplace.header.description", style="caption", autowrap=True).grid(column=0, row=1, sticky="ew")


    def _load_content(self, master) -> None:
        wrapper: Frame = Frame(master, transparent=True)
        wrapper.grid(column=0, row=1, sticky="nsew")
        Thread(target=self._fetch_community_mods, args=(wrapper,), daemon=True).start()


    def _fetch_community_mods(self, wrapper: Frame) -> None:
        try:
            response: Response = requests.get(Api.GitHub.MARKETPLACE)
            data: list[dict] = response.json()
            mods: list[CommunityMod] = []
            for item in data:
                try: mods.append(CommunityMod(item, self.placeholder_thumbnail))
                except ValueError: pass
            self.after(10, self._create_mod_frames, wrapper, mods)

        except Exception as e:
            self.after(10, self._show_error_screen, wrapper, e)


    def _show_error_screen(self, wrapper: Frame, error: Exception) -> None:
        wrapper.grid_columnconfigure(0, weight=1)

        wifi_off_image: CTkImage = get_ctk_image(Resources.Large.Light.WIFI_OFF, Resources.Large.Dark.WIFI_OFF, size=128)
        Label(wrapper, image=wifi_off_image).grid(column=0, row=0, pady=(16, 0))
        Label(wrapper, "menu.marketplace.content.failed_to_load.title", style="title").grid(column=0, row=1)
        Label(wrapper, "menu.marketplace.content.failed_to_load.message", style="body").grid(column=0, row=2)

        self.root.send_banner(
            title_key="menu.marketplace.exception.title.failed_to_load",
            message_key="menu.marketplace.exception.message.unknown",
            message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(error).__module__}.{type(error).__qualname__}", "{exception.message}": str(error)}),
            mode="error"
        )


    def _create_mod_frames(self, wrapper: Frame, mods: list[CommunityMod]) -> None:
        flexbox: FlexBox = FlexBox(wrapper, self._COLUMN_WIDTH, self._ROW_HEIGHT, self._ENTRY_GAP, transparent=True, layer=1)
        wrapper.grid_columnconfigure(0, weight=1)
        flexbox.grid(column=0, row=0, sticky="nsew")

        download_image: CTkImage = get_ctk_image(Resources.Common.Light.DOWNLOAD, Resources.Common.Dark.DOWNLOAD, size=24)

        for mod in mods:
            frame: Frame = flexbox.add_item()
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_rowconfigure(0, weight=1)
            content: Frame = Frame(frame, transparent=True)
            content.grid(column=0, row=0, sticky="nsew", padx=self._ENTRY_PADDING[0], pady=self._ENTRY_PADDING[1])

            image_label: Label = Label(content, width=self._ENTRY_THUMBNAIL_SIZE[0], height=self._ENTRY_THUMBNAIL_SIZE[1])
            image_label.grid(column=0, row=0, sticky="nsew")

            Label(content, mod.name, style="body_strong", autowrap=False, wraplength=self._ENTRY_INNER_WIDTH).grid(column=0, row=1, sticky="nsew", pady=(self._ENTRY_INNER_GAP, 0))
            Label(content, mod.author, style="caption", autowrap=False, wraplength=self._ENTRY_INNER_WIDTH).grid(column=0, row=2, sticky="nsew")
            Button(content, width=self._ENTRY_INNER_WIDTH, height=32, image=download_image).grid(column=0, row=3, sticky="nsew", pady=(self._ENTRY_INNER_GAP, 0))

            self.after(100, self._load_mod_thumbnail, mod, image_label)
        return


    def _load_mod_thumbnail(self, mod: CommunityMod, image_label: Label) -> None:
        def resize_and_crop(image: Image.Image, size: tuple[int, int]) -> Image.Image:
            if size == image.size: return image.copy()
            w, h = image.size
            ratio = w/h
            new_h = int(size[0]/ratio)
            method = Image.Resampling.LANCZOS if w > size[0] else Image.Resampling.BICUBIC
            resized = image.resize((size[0], new_h), method)
            if new_h > size[1]:
                excess = new_h - size[1]
                margin = int(excess/2)
                resized = resized.crop((0, margin, size[0], size[1]+margin))
            return resized


        thumbnail: Image.Image | tuple[Image.Image, Image.Image] = mod.get_thumbnail()
        thumbnail_size: tuple[int, int] = self._ENTRY_THUMBNAIL_SIZE
        if isinstance(thumbnail, tuple): image: CTkImage = get_ctk_image(resize_and_crop(thumbnail[0], thumbnail_size), resize_and_crop(thumbnail[1], thumbnail_size), size=thumbnail_size)
        else: image = get_ctk_image(resize_and_crop(thumbnail, thumbnail_size), size=thumbnail_size)
        image_label.configure(image=image, width=thumbnail_size[0], height=thumbnail_size[1])
# endregion


# region functions
# endregion
# endregion