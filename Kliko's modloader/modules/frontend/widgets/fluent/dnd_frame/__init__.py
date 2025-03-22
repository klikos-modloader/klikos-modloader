import re
from pathlib import Path
from typing import Callable, Literal

import customtkinter as ctk  # type: ignore
from tkinterdnd2 import DND_FILES  # type: ignore
from PIL import Image  # type: ignore


class Assets:
    DIRECTORY: Path = Path(__file__).parent / "assets"
    FILE: Path = DIRECTORY / "file.png"
    FOLDER: Path = DIRECTORY / "folder.png"


class Colors:
    class Dark:
        class BackgroundColor:
            hex: str = "#202020"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TopBackgroundColor:
            hex: str = "#2B2B2B"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderColor:
            hex: str = "#1D1D1D"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextColor:
            hex: str = "#FFFFFF"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)

    class Light:
        class BackgroundColor:
            hex: str = "#F3F3F3"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TopBackgroundColor:
            hex: str = "#F9F9F9"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderColor:
            hex: str = "#E5E5E5"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextColor:
            hex: str = "#1B1B1B"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)


class FluentDnDFrame(ctk.CTkFrame):
    command: Callable | None
    _icon_mode: Literal["file", "folder"]
    _icon_image: ctk.CTkImage


    def __init__(self, master, text: str = "", icon: Literal["file", "folder"] = "file", width: int = 200, height: int = 200, command: Callable | None = None, rounded: bool = True, border: bool = True, font_size: int = 16, image_gap: int = 8) -> None:
        super().__init__(master, width=width, height=height, corner_radius=4 if rounded else 0)
        self.command = command
        self._icon_mode = icon

        fg_color = (Colors.Light.TopBackgroundColor.hex, Colors.Dark.TopBackgroundColor.hex) if self._is_toplevel() else (Colors.Light.BackgroundColor.hex, Colors.Dark.BackgroundColor.hex)
        border_color = (Colors.Light.BorderColor.hex, Colors.Dark.BorderColor.hex)
        border_width: int = 0 if not border else 1
        self.configure(fg_color=fg_color, border_color=border_color, border_width=border_width)

        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self._callback)

        self._icon_image = self._get_image(icon, size=(font_size*2,font_size*2))

        text_frame: ctk.CTkFrame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        text_frame.place(relx=0.5, rely=0.5, anchor="center")

        icon_label = ctk.CTkLabel(text_frame, fg_color="transparent", text="", image=self._icon_image)
        icon_label.grid(column=0, row=0)
        text_label = ctk.CTkLabel(text_frame, fg_color="transparent", text=text, text_color=(Colors.Light.TextColor.hex, Colors.Dark.TextColor.hex), font=ctk.CTkFont(family="Segoe UI", size=font_size))
        text_label.grid(column=1, row=0, padx=(image_gap,0))


    def _callback(self, event) -> None:
        if not callable(self.command): return

        matches = re.findall(r'\{([^}]+)\}|([A-Za-z]:/[\S]+)', event.data)
        paths = tuple(Path(path) for match in matches for path in match if path)

        self.command(paths)
    

    def _is_toplevel(self) -> str | tuple[str, str]:
        return self.winfo_parent() == "."
    

    def _get_image(self, mode: Literal["file", "folder"], size: tuple[int, int]) -> ctk.CTkImage:
        light_image: Image.Image
        dark_image: Image.Image

        file: Path = Assets.FILE if mode == "file" else Assets.FOLDER

        with Image.open(file) as icon:
            icon.putdata([(Colors.Light.TextColor.r, Colors.Light.TextColor.g, Colors.Light.TextColor.b, a) for _, _, _, a in icon.getdata()])
            light_image = icon.copy()
            icon.putdata([(Colors.Dark.TextColor.r, Colors.Dark.TextColor.g, Colors.Dark.TextColor.b, a) for _, _, _, a in icon.getdata()])
            dark_image = icon.copy()

        return ctk.CTkImage(light_image, dark_image, size=size)