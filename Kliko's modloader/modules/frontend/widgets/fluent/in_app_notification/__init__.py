import platform
from pathlib import Path
from typing import Callable

from ..button import FluentButton

import customtkinter as ctk  # type: ignore
from PIL import Image  # type: ignore


class Colors:
    class Dark:
        class BackgroundColor:
            hex: str = "#1C1C1C"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextTitleColor:
            hex: str = "#FFFFFF"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextColor:
            hex: str = "#CBCBCB"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class IconColor:
            hex: str = "#FFFFFF"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
    
    class Light:
        class BackgroundColor:
            hex: str = "#EEEEEE"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextTitleColor:
            hex: str = "#191919"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextColor:
            hex: str = "#5C5C5CC"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class IconColor:
            hex: str = "#1A1A1A"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)


class Assets:
    DIRECTORY: Path = Path(__file__).parent / "assets"
    CLOSE: Path = DIRECTORY / "close.png"


class FluentInAppNotification(ctk.CTkToplevel):
    OUTER_PADX: int = 16
    OUTER_PADY: int = 16
    INNER_PADX: int = 16
    INNER_PADY: int = 16
    WIDTH: int = 364
    HEIGHT: int = 109
    TITLE_CONTENT_GAP: int = 8
    WRAPLENGTH: int = 400

    visible: bool = False
    hovered: bool = False
    root: ctk.CTk

    _triggered: bool = False
    _on_click: Callable | None
    _on_cancel: Callable | None

    _dark_image: Image.Image
    _light_image: Image.Image

    def __init__(self, master: ctk.CTk, name: str | None = None, title: str | None = None, message: str | None = None, icon: ctk.CTkImage | None = None, on_click: Callable | None = None, on_cancel: Callable | None = None) -> None:
        if not name or not title or not message: raise ValueError("FluentInAppNotification: name, title and message is required!")

        self._create_image_objects()

        super().__init__(master, fg_color=(Colors.Light.BackgroundColor.hex, Colors.Dark.BackgroundColor.hex), cursor="hand2")
        self.withdraw()
        self.overrideredirect(True)
        # self._apply_rounded_corners()

        self.root = master
        self._on_click = on_click
        self._on_cancel = on_cancel

        self.transient(self.root)
        self._apply_rounded_corners()
        self.grid_columnconfigure(0, weight=1)

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid_columnconfigure(2, weight=1)

        if icon is not None: ctk.CTkLabel(top_frame, fg_color="transparent", text="", image=icon).grid(column=0, row=0, sticky="w")
        if name is not None: ctk.CTkLabel(top_frame, fg_color="transparent", text=name, font=ctk.CTkFont(family="Segoe UI", weight="bold", size=12)).grid(column=1, row=0, padx=8 if icon is not None else (0,8), sticky="w")
        FluentButton(top_frame, width=24, height=24, command=self._callback, light_icon=self._light_image, dark_icon=self._dark_image, icon_size=(16,16)).grid(column=2, row=0, sticky="e")

        top_frame.grid(column=0, row=0, sticky="ew", padx=self.INNER_PADX, pady=(self.INNER_PADY, self.TITLE_CONTENT_GAP))

        if title is not None and message is not None:
            bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
            ctk.CTkLabel(bottom_frame, fg_color="transparent", text=title, font=ctk.CTkFont(family="Segoe UI", weight="bold", size=16), wraplength=self.WRAPLENGTH, justify="left").grid(column=0, row=0, sticky="w")
            ctk.CTkLabel(bottom_frame, fg_color="transparent", text=message, font=ctk.CTkFont(family="Segoe UI", size=14), wraplength=self.WRAPLENGTH, justify="left").grid(column=0, row=1, sticky="w")
            bottom_frame.grid(column=0, row=1, sticky="ew", padx=self.INNER_PADX, pady=(0, self.INNER_PADY))

        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_unhover)
        self.bind("<ButtonRelease-1>", self._callback)
        self.update_idletasks()
        self.visible = True
        self.deiconify()
        self.after(10, self._loop)
    

    def _on_hover(self, _) -> None:
        self.hovered = True
    

    def _on_unhover(self, _) -> None:
        self.hovered = False


    def _callback(self, event = None) -> None:
        if not self.hovered: return
        if self._triggered: return
        self._triggered = True
        self.visible = False
        self.withdraw()
        self.destroy()
        if event is None:
            if callable(self._on_cancel): self._on_cancel()
        else:
            if callable(self._on_click): self._on_click()


    def _loop(self) -> None:
        if not self.visible: return
        # self.lift()
        if self.root.focus_get() != self:
            self.lift()
        self._set_geometry()
        self.after(10, self._loop)


    def _set_geometry(self) -> None:
        w: int = max(self.winfo_width(), self.WIDTH)
        h: int = max(self.winfo_height(), self.HEIGHT)
        root_x: int = self.root.winfo_rootx()
        root_y: int = self.root.winfo_rooty()
        root_w: int = self.root.winfo_width()
        root_h: int = self.root.winfo_height()

        x: int = root_x + root_w - w - self.OUTER_PADX
        y: int = root_y + root_h - h - self.OUTER_PADY

        self.geometry(f"{w}x{h}+{x}+{y}")


    def _apply_rounded_corners(self) -> None:  # Generated by ChatGPT
        def is_windows_11() -> bool:
            version = platform.version()
            try:
                release = int(platform.release())
                build = int(version.split(".")[2])
            except (IndexError, ValueError):
                return False
            return release == 11 or (build >= 22000 and release < 12)
        if not is_windows_11(): return

        from ctypes import windll, byref, sizeof, c_int
        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        DWMNCRP_ROUND = 2
        hwnd = windll.user32.GetParent(self.winfo_id())
        preference = c_int(DWMNCRP_ROUND)
        windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, byref(preference), sizeof(preference))


    def _create_image_objects(self) -> None:
        with Image.open(Assets.CLOSE) as icon:
            icon_data = icon.getdata()
            icon.putdata([(Colors.Dark.IconColor.r, Colors.Dark.IconColor.g, Colors.Dark.IconColor.b, a) for _, _, _, a in icon_data])
            self._dark_image = icon.copy()
            icon.putdata([(Colors.Light.IconColor.r, Colors.Light.IconColor.g, Colors.Light.IconColor.b, a) for _, _, _, a in icon_data])
            self._light_image = icon.copy()