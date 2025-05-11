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


TEST_DATA: list[dict] = [
    {
        "id": "klikos-mod",
        "name": "Kliko's mod",
        "author": "TheKliko",
        "description": "This mod changes the Roblox UI by giving it a red-pink gradient.\n\n- Gradient: #FF006E -> #990000 (45°)\n- Menu icons\n- Avatar editor\n- Skybox\n- Controller, VR and High-Res support",
        "download": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/mods/klikos-mod.zip",
        "thumbnail": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/thumbnails/klikos-mod.png"
    },
    {
        "id": "24k-gradient-gold-theme",
        "name": "24K Gradient Gold Theme",
        "author": "thefrenchguy4",
        "description": "The golden theme for the elite.\n\nWhat does it contain?\n- The theme itself\n - Golden Skybox\n - High quality icons (the same quality as the default ones)\n - Support for VR (I have no clue)\n - Custom Avatar Editor (RX Tower)\n - 2013 Angular cursor (in Misc folder)",
        "download": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/mods/24k-gradient-gold-theme.zip",
        "thumbnail": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/thumbnails/24k-gradient-gold-theme.png"
    },
    {
        "id": "networks-red-theme",
        "name": "Network's Red Theme",
        "author": "netsoftworks",
        "description": "This is basically my previous theme that was discontinuted and now I'm reviving it back with a fresh branding.",
        "download": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/mods/networks-red-theme.zip",
        "thumbnail": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/thumbnails/networks-red-theme.png"
    },
    {
        "id": "blue-star-theme",
        "name": "Blue Star Theme",
        "author": "thefrenchguy4",
        "description": "After multiple requests for a blue theme and seeing most of the blue themes were deprecated, I delivered.\n\nWhat does it contain?\n- The theme itself (obviously)\n- A variant of the emote wheel (in the Miscellaneous folder)",
        "download": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/mods/blue-star-theme.zip",
        "thumbnail": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/thumbnails/blue-star-theme.png"
    },
    {
        "id": "fishstrap-theme",
        "name": "Fishstrap Theme",
        "description": "This mod changes the Roblox UI by giving it a Fishstrap-themed gradient.\n\n- Gradient: #0A293E -> #1B699C\n- Menu icons\n- Controller, VR and High-Res support",
        "author": "TheKliko",
        "download": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/mods/fishstrap-theme.zip",
        "thumbnail": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/thumbnails/fishstrap-theme.png"
    },
    {
        "id": "l337",
        "name": "L337",
        "author": "dooM",
        "description": "Experience Roblox like a true haxx0r! Converts all text into basic leet.",
        "download": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/mods/l337.zip",
        "thumbnail": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/thumbnails/l337.png"
    },
    {
        "id": "content-deleted",
        "name": "Content Deleted",
        "author": "dooM",
        "description": "Are you tired of seeing words? Do you ever picture a perfect future in which free speech is abolished in favor of censorship? Look no further! Introducing cutting-edge technologies specifically created for our Chinese Communist Party.",
        "download": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/mods/content-deleted.zip",
        "thumbnail": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/thumbnails/content-deleted.png"
    },
    {
        "id": "translucency",
        "name": "Translucency",
        "author": "dooM",
        "description": "Make UI elements transparent.",
        "download": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/mods/translucency.zip",
        "thumbnail": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/thumbnails/translucency.png"
    },
    {
        "id": "bloxstrap-theme",
        "name": "Bloxstrap theme",
        "description": "This mod changes the Roblox UI by giving it a Bloxstrap-themed gradient.\n\n- Gradient: #DB59AB -> #3D38C0\n- Menu icons\n- Controller, VR and High-Res support",
        "author": "TheKliko",
        "download": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/mods/bloxstrap-theme.zip",
        "thumbnail": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/thumbnails/bloxstrap-theme.png"
    },
    {
        "id": "bloxstrap-theme-old",
        "name": "Bloxstrap theme (old)",
        "description": "This mod changes the Roblox UI by giving it the old Bloxstrap gradient.\n\n- Gradient: #A011FE -> #5460F9\n- Menu icons\n- Controller and VR support",
        "author": "TheKliko",
        "download": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/mods/bloxstrap-theme-old.zip",
        "thumbnail": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/thumbnails/bloxstrap-theme-old.png"
    },
    {
        "id": "pink-sky",
        "name": "Pink Sky",
        "author": "TheKliko",
        "description": "Adds a pink skybox",
        "download": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/mods/pink-sky.zip",
        "thumbnail": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/thumbnails/pink-sky.png"
    },
    {
        "id": "ubff-theme",
        "name": "UBFF theme",
        "description": "Based on the Useful Bloxstrap FF's community server.\n\n- Gradient: #648BD9 -> #FA94D7\n- Menu icons\n- Controller and VR support",
        "author": "TheKliko",
        "download": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/mods/ubff-theme.zip",
        "thumbnail": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/thumbnails/ubff-theme.png"
    },
    {
        "id": "blue-emote-wheel",
        "name": "Blue Emote Wheel",
        "description": "Adds a blue emote wheel",
        "author": "TheKliko",
        "download": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/mods/blue-emote-wheel.zip",
        "thumbnail": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/thumbnails/blue-emote-wheel.png"
    },
    {
        "id": "old-login-screen",
        "name": "Old login screen (remake)",
        "description": "A remake of the 2017 login screen",
        "author": "TheKliko",
        "download": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/mods/old-login-screen.zip",
        "thumbnail": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/thumbnails/old-login-screen.png"
    },
    {
        "id": "old-death-sound",
        "name": "Old death sound",
        "description": "Brings back the classic 'OOF' death sound",
        "download": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/mods/old-death-sound.zip"
    },
    {
        "id": "wilhelm-scream-death-sound",
        "name": "Wilhelm Scream (death sound)",
        "description": "Adds the iconic 'Wilhelm Scream' death sound",
        "download": "https://github.com/TheKliko/klikos-modloader/raw/refs/heads/marketplace-v2/mods/wilhelm-scream-death-sound.zip"
    }
]


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
            # response: Response = requests.get(Api.GitHub.MARKETPLACE)
            # data: list[dict] = response.json()
            data = TEST_DATA
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
            mode="error", auto_close_after_ms=6000
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

            Thread(target=self._load_mod_thumbnail, args=(mod, image_label), daemon=True).start()
            # self.after(100, self._load_mod_thumbnail, mod, image_label)
        return


    def _load_mod_thumbnail(self, mod: CommunityMod, image_label: Label) -> None:
        thumbnail: Image.Image | tuple[Image.Image, Image.Image] = mod.get_thumbnail()
        thumbnail_size: tuple[int, int] = self._ENTRY_THUMBNAIL_SIZE
        if isinstance(thumbnail, tuple): image: CTkImage = get_ctk_image(crop_to_fit(thumbnail[0], mod.THUMBNAIL_ASPECT_RATIO), crop_to_fit(thumbnail[1], mod.THUMBNAIL_ASPECT_RATIO), size=thumbnail_size)
        else: image = get_ctk_image(crop_to_fit(thumbnail, mod.THUMBNAIL_ASPECT_RATIO), size=thumbnail_size)
        image_label.after(0, lambda: image_label.configure(image=image, width=thumbnail_size[0], height=thumbnail_size[1]))
        # image_label.configure(image=image, width=thumbnail_size[0], height=thumbnail_size[1])
# endregion


# region functions
    def show_mod_window(self, mod: CommunityMod) -> None:
        CommunityModWindow(self.root, mod)
# endregion
# endregion