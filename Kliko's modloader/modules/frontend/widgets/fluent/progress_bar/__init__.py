from typing import Literal

import winaccent  # type: ignore
import customtkinter as ctk  # type: ignore


class Colors:
    class Dark:
        class BarFillColor:
            hex: str = winaccent.accent_light_2
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BarEmptyColor:
            hex: str = "#9A9A9A"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
    class Light:
        class BarFillColor:
            hex: str = winaccent.accent_dark_1
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BarEmptyColor:
            hex: str = "#868686"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)


class FluentProgressBar(ctk.CTkProgressBar):
    def __init__(self, master, length: int | None = None, thickness: int = 3, corner_radius: int = 4, mode: Literal["determinate", "indeterminate"] = "determinate") -> None:
        super().__init__(master, width=length, height=thickness, corner_radius=corner_radius, mode=mode, progress_color=(Colors.Light.BarFillColor.hex, Colors.Dark.BarFillColor.hex), fg_color=(Colors.Light.BarEmptyColor.hex, Colors.Dark.BarEmptyColor.hex))
        self.set(0)