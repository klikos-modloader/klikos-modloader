from tkinter import TclError
from threading import Thread
from typing import TYPE_CHECKING

from modules.logger import Logger
from modules.project_data import ProjectData
from modules.frontend.widgets import ScrollableFrame, Frame, Label, Button, FlexBox
if TYPE_CHECKING: from modules.frontend.widgets import Root
from modules.frontend.functions import get_ctk_image, crop_to_fit
from modules.localization import Localizer
from modules.filesystem import Resources
from modules.networking import requests, Response, Api

from ..dataclasses import CommunityMod
from ..windows import CommunityModWindow


from customtkinter import CTkImage  # type: ignore
from PIL import Image  # ype: ignore


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
    _ENTRY_THUMBNAIL_SIZE: tuple[int, int] = (_ENTRY_INNER_WIDTH, int(_ENTRY_INNER_WIDTH/CommunityMod.THUMBNAIL_ASPECT_RATIO))
    _ROW_HEIGHT: int = _ENTRY_THUMBNAIL_SIZE[1]+2*_ENTRY_PADDING[1]+_ENTRY_INNER_GAP*2+28+32  # 28 = label, 32 = button


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

        button_image: CTkImage = get_ctk_image(Resources.Common.Light.OPEN_EXTERNAL, Resources.Common.Dark.OPEN_EXTERNAL, size=24)

        for mod in mods:
            frame: Frame = flexbox.add_item()
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_rowconfigure(0, weight=1)
            content: Frame = Frame(frame, transparent=True)
            content.grid(column=0, row=0, sticky="nsew", padx=self._ENTRY_PADDING[0], pady=self._ENTRY_PADDING[1])

            image_label: Label = Label(content, width=self._ENTRY_THUMBNAIL_SIZE[0], height=self._ENTRY_THUMBNAIL_SIZE[1])
            image_label.grid(column=0, row=0, sticky="nsew")

            Label(content, mod.name, style="body_strong", autowrap=False, wraplength=self._ENTRY_INNER_WIDTH).grid(column=0, row=1, sticky="nsew", pady=(self._ENTRY_INNER_GAP, 0))
            Button(content, width=self._ENTRY_INNER_WIDTH, height=32, image=button_image, secondary=True, command=lambda mod=mod: self.show_mod_window(mod)).grid(column=0, row=3, sticky="nsew", pady=(self._ENTRY_INNER_GAP, 0))

            self.after(100, self._load_mod_thumbnail, mod, image_label)
        return


    def _load_mod_thumbnail(self, mod: CommunityMod, image_label: Label) -> None:
        thumbnail: Image.Image | tuple[Image.Image, Image.Image] = mod.get_thumbnail()
        thumbnail_size: tuple[int, int] = self._ENTRY_THUMBNAIL_SIZE
        if isinstance(thumbnail, tuple): image: CTkImage = get_ctk_image(crop_to_fit(thumbnail[0], mod.THUMBNAIL_ASPECT_RATIO), crop_to_fit(thumbnail[1], mod.THUMBNAIL_ASPECT_RATIO), size=thumbnail_size)
        else: image = get_ctk_image(crop_to_fit(thumbnail, mod.THUMBNAIL_ASPECT_RATIO), size=thumbnail_size)
        image_label.configure(image=image, width=thumbnail_size[0], height=thumbnail_size[1])
# endregion


# region functions
    def show_mod_window(self, mod: CommunityMod) -> None:
        CommunityModWindow(self.root, mod)
# endregion
# endregion