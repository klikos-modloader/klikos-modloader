from pathlib import Path

from ..ctk_root_storage import set_root_instance

import customtkinter as ctk  # type: ignore
from tkinterdnd2 import TkinterDnD  # type: ignore


class Assets:
    DIRECTORY: Path = Path(__file__).parent / "assets"
    DEFAULT_LOGO: Path = DIRECTORY / "logo-default.ico"


class Colors:
    class Dark:
        class BackgroundColor:
            hex: str = "#202020"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)

    class Light:
        class BackgroundColor:
            hex: str = "#F3F3F3"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)


class FluentRootWindow(ctk.CTk, TkinterDnD.DnDWrapper):
    window_title: str
    window_icon: Path


    def __init__(self, title: str = "FluentRootWindow", icon: Path = Assets.DEFAULT_LOGO) -> None:
        super().__init__(fg_color=(Colors.Light.BackgroundColor.hex, Colors.Dark.BackgroundColor.hex))
        set_root_instance(self)

        self.window_title = title
        self.window_icon = icon

        self.title(self.window_title)
        if self.window_icon.is_file() and self.window_icon.suffix == ".ico":
            self.iconbitmap(str(self.window_icon.resolve()))

        self.protocol("WM_DELETE_WINDOW", self._on_close)
    

    def _on_close(self, *_, **__) -> None:
        self.destroy()
