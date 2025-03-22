from pathlib import Path

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


class FluentToplevel(ctk.CTkToplevel):
    root: ctk.CTk


    def __init__(self, root: ctk.CTk, title: str = "FluentToplevel", icon: Path = Assets.DEFAULT_LOGO, minimized: bool = False) -> None:
        super().__init__(root, fg_color=(Colors.Light.BackgroundColor.hex, Colors.Dark.BackgroundColor.hex))
        if minimized: self.withdraw()
        self.root = root
        self.title(title)
        if icon.is_file() and icon.suffix == ".ico":
            self.iconbitmap(icon.resolve())
            self.after(200, self.iconbitmap, icon.resolve())