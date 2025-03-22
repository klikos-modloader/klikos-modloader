import platform
from pathlib import Path
from typing import Literal

import winaccent  # type: ignore
import customtkinter as ctk  # type: ignore
from PIL import Image  # type: ignore


class Colors:
    class Dark:
        class BackgroundColor:
            hex: str = "#2C2C2C"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderColor:
            hex: str = "#1C1C1C"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextColor:
            hex: str = "#FFFFFF"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class IconColor:
            hex: str = winaccent.accent_light_3
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ButtonBackgroundColor:
            hex: str = "#2D2D2D"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ButtonBackgroundHoverColor:
            hex: str = "#323232"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ButtonBackgroundActiveColor:
            hex: str = "#272727"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ButtonBackgroundDisabledColor:
            hex: str = "#2A2A2A"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ButtonBorderColor:
            hex: str = "#303030"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ButtonToplevelBackgroundColor:
            hex: str = "#272727"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ButtonToplevelBackgroundHoverColor:
            hex: str = "#343434"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ButtonToplevelBackgroundActiveColor:
            hex: str = "#303030"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ButtonToplevelBackgroundDisabledColor:
            hex: str = "#2A2A2A"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)

    class Light:
        class BackgroundColor:
            hex: str = "#F9F9F9"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderColor:
            hex: str = "#DDDDDD"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextColor:
            hex: str = "#1A1A1A"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class IconColor:
            hex: str = winaccent.accent_dark_2
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ButtonBackgroundColor:
            hex: str = "#FBFBFB"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ButtonBackgroundHoverColor:
            hex: str = "#F6F6F6"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ButtonBackgroundActiveColor:
            hex: str = "#F5F5F5"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ButtonBackgroundDisabledColor:
            hex: str = "#F5F5F5"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ButtonBorderColor:
            hex: str = "#E5E5E5"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ButtonToplevelBackgroundColor:
            hex: str = "#F9F9F9"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ButtonToplevelBackgroundHoverColor:
            hex: str = "#F0F0F0"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ButtonToplevelBackgroundActiveColor:
            hex: str = "#F3F3F3"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ButtonToplevelBackgroundDisabledColor:
            hex: str = "#F5F5F5"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)


class Assets:
    DIRECTORY: Path = Path(__file__).parent / "assets"
    BACKGROUND: Path = DIRECTORY / "background.png"
    BORDER: Path = DIRECTORY / "border.png"
    ICON: Path = DIRECTORY / "icon.png"


class FluentToolTip(ctk.CTkToplevel):
    orientation: Literal["up", "down", "left", "right"]
    visible: bool = False
    gap: int
    button: "FluentToolTipButton"
    root: ctk.CTk
    _padx: int = 10
    _pady: int = 10


    def __init__(self, master: ctk.CTk, button: "FluentToolTipButton", title: str = "", message: str = "", orientation: Literal["up", "down", "left", "right"] = "up", gap: int = 12, wraplength: int = 0) -> None:
        super().__init__(master, fg_color=(Colors.Light.BackgroundColor.hex, Colors.Dark.BackgroundColor.hex))
        self.withdraw()
        self.overrideredirect(True)
        self.orientation = orientation
        self.gap = gap
        self.button = button
        self.root = master

        if title:
            title_label: ctk.CTkLabel = ctk.CTkLabel(self, text=title, fg_color="transparent", wraplength=wraplength, text_color=(Colors.Light.TextColor.hex, Colors.Dark.TextColor.hex), font=ctk.CTkFont(family="Segoe UI", weight="bold", size=16), justify="left", anchor="w")
            title_label.grid(column=0, row=0, sticky="w", padx=self._padx, pady=self._pady if not message else (self._pady, 0))
        if message:
            message_label: ctk.CTkLabel = ctk.CTkLabel(self, text=message, fg_color="transparent", wraplength=wraplength, text_color=(Colors.Light.TextColor.hex, Colors.Dark.TextColor.hex), font=ctk.CTkFont(family="Segoe UI", size=12), justify="left", anchor="w")
            message_label.grid(column=0, row=1, sticky="w", padx=self._padx, pady=self._pady if not title else (8, self._pady))
        
        self.after(10, self._apply_rounded_corners)


    def show(self) -> None:
        if self.visible: return
        self._set_geometry()
        self.deiconify()
        self.visible = True
        self.after(10, self._loop)


    def hide(self) -> None:
        if not self.visible: return
        self.withdraw()
        self.visible = False


    def _loop(self) -> None:
        if not self.visible: return
        if not self.button.winfo_exists():
            self.hide()
            self.after(10, self.destroy)
            return
        self.lift()
        self._set_geometry()
        self.after(10, self._loop)

    
    def _set_geometry(self) -> None:
        w: int = self.winfo_reqwidth()
        h: int = self.winfo_reqheight()
        button_x: int = self.button.winfo_rootx()
        button_y: int = self.button.winfo_rooty()
        button_w: int = self.button.winfo_width()
        button_h: int = self.button.winfo_height()

        if self.orientation == "up":
            x: int = button_x + (button_w - w) // 2
            y: int = button_y - h - self.gap
        elif self.orientation == "down":
            x = button_x + (button_w - w) // 2
            y = button_y + button_h + self.gap
        elif self.orientation == "left":
            x = button_x - w - self.gap
            y = button_y + (button_h - h) // 2
        elif self.orientation == "right":
            x = button_x + button_w + self.gap
            y = button_y + (button_h - h) // 2

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


class FluentToolTipButton(ctk.CTkLabel):
    button_clicked: bool = False
    button_hovered: bool = False
    button_toggled: bool = False
    button_enabled: bool = False
    tooltip: FluentToolTip

    _toplevel: bool = False

    _dark_image_default: Image.Image
    _dark_image_hover: Image.Image
    _dark_image_active: Image.Image
    _dark_image_disabled: Image.Image
    
    _light_image_default: Image.Image
    _light_image_hover: Image.Image
    _light_image_active: Image.Image
    _light_image_disabled: Image.Image

    image_default: ctk.CTkImage
    image_hover: ctk.CTkImage
    image_active: ctk.CTkImage
    image_disabled: ctk.CTkImage

    def __init__(self, root, master, tooltip_title: str = "", tooltip_message: str = "", tooltip_orientation: Literal["up", "down", "left", "right"] = "up", tooltip_gap: int = 12, wraplength: int = 0, disabled: bool = False, toplevel: bool = False) -> None:
        if not tooltip_title and not tooltip_message: raise RuntimeError("FluentToolTipButton: Title or message must exist!")

        self._toplevel = toplevel
        self._create_image_objects()
        self._finalize_image_objects()
        self.button_enabled = not disabled

        super().__init__(master, width=22, height=22, image=None, compound="center", text="", fg_color="transparent", cursor="hand2")
        self._set_image_object()
        self.tooltip = FluentToolTip(root, self, tooltip_title, tooltip_message, tooltip_orientation, tooltip_gap, wraplength=wraplength)

        self.bind("<Enter>", self._on_button_hover)
        self.bind("<Leave>", self._on_button_unhover)
        self.bind("<Button-1>", self._on_button_click)
        self.bind("<ButtonRelease-1>", self._on_button_unclick)
    

    def enable(self) -> None:
        self.button_enabled = True
        self._set_image_object()
        if self.button_toggled or self.button_clicked or self.button_hovered: self.tooltip.show()
    

    def disable(self) -> None:
        self.button_enabled = True
        self._set_image_object()
        self.button_toggled = False
        self.tooltip.hide()


    def _on_button_hover(self, _) -> None:
        self.button_hovered = True
        self._set_image_object()
        if self.button_enabled: self.tooltip.show()


    def _on_button_unhover(self, _) -> None:
        self.button_hovered = False
        self._set_image_object()
        if not self.button_clicked and not self.button_toggled: self.tooltip.hide()


    def _on_button_click(self, _) -> None:
        self.button_clicked = True
        self._set_image_object()
        # self.button_toggled = not self.button_toggled
        if self.button_enabled: self.tooltip.show()


    def _on_button_unclick(self, _) -> None:
        self.button_clicked = False
        self._set_image_object()
        if not self.button_toggled and not self.button_hovered: self.tooltip.hide()


    def _set_image_object(self) -> None:
        if not self.button_enabled:
            self.configure(image=self.image_disabled)
        elif self.button_clicked:
            self.configure(image=self.image_active)
        elif self.button_hovered:
            self.configure(image=self.image_hover)
        else:
            self.configure(image=self.image_default)


    def _create_image_objects(self) -> None:
        with Image.open(Assets.BACKGROUND) as background:
            background.putdata([(Colors.Dark.ButtonBackgroundColor.r, Colors.Dark.ButtonBackgroundColor.g, Colors.Dark.ButtonBackgroundColor.b, a) if not self._toplevel else (Colors.Dark.ButtonToplevelBackgroundColor.r, Colors.Dark.ButtonToplevelBackgroundColor.g, Colors.Dark.ButtonToplevelBackgroundColor.b, a) for _, _, _, a in background.getdata()])
            self._dark_image_default = background.copy()
            background.putdata([(Colors.Dark.ButtonBackgroundHoverColor.r, Colors.Dark.ButtonBackgroundHoverColor.g, Colors.Dark.ButtonBackgroundHoverColor.b, a) if not self._toplevel else (Colors.Dark.ButtonToplevelBackgroundHoverColor.r, Colors.Dark.ButtonToplevelBackgroundHoverColor.g, Colors.Dark.ButtonToplevelBackgroundHoverColor.b, a) for _, _, _, a in background.getdata()])
            self._dark_image_hover = background.copy()
            background.putdata([(Colors.Dark.ButtonBackgroundActiveColor.r, Colors.Dark.ButtonBackgroundActiveColor.g, Colors.Dark.ButtonBackgroundActiveColor.b, a) if not self._toplevel else (Colors.Dark.ButtonToplevelBackgroundActiveColor.r, Colors.Dark.ButtonToplevelBackgroundActiveColor.g, Colors.Dark.ButtonToplevelBackgroundActiveColor.b, a) for _, _, _, a in background.getdata()])
            self._dark_image_active = background.copy()
            background.putdata([(Colors.Dark.ButtonBackgroundDisabledColor.r, Colors.Dark.ButtonBackgroundDisabledColor.g, Colors.Dark.ButtonBackgroundDisabledColor.b, a) if not self._toplevel else (Colors.Dark.ButtonToplevelBackgroundDisabledColor.r, Colors.Dark.ButtonToplevelBackgroundDisabledColor.g, Colors.Dark.ButtonToplevelBackgroundDisabledColor.b, a) for _, _, _, a in background.getdata()])
            self._dark_image_disabled = background.copy()

            background.putdata([(Colors.Light.ButtonBackgroundColor.r, Colors.Light.ButtonBackgroundColor.g, Colors.Light.ButtonBackgroundColor.b, a) if not self._toplevel else (Colors.Light.ButtonToplevelBackgroundColor.r, Colors.Light.ButtonToplevelBackgroundColor.g, Colors.Light.ButtonToplevelBackgroundColor.b, a) for _, _, _, a in background.getdata()])
            self._light_image_default = background.copy()
            background.putdata([(Colors.Light.ButtonBackgroundHoverColor.r, Colors.Light.ButtonBackgroundHoverColor.g, Colors.Light.ButtonBackgroundHoverColor.b, a) if not self._toplevel else (Colors.Light.ButtonToplevelBackgroundHoverColor.r, Colors.Light.ButtonToplevelBackgroundHoverColor.g, Colors.Light.ButtonToplevelBackgroundHoverColor.b, a) for _, _, _, a in background.getdata()])
            self._light_image_hover = background.copy()
            background.putdata([(Colors.Light.ButtonBackgroundActiveColor.r, Colors.Light.ButtonBackgroundActiveColor.g, Colors.Light.ButtonBackgroundActiveColor.b, a) if not self._toplevel else (Colors.Light.ButtonToplevelBackgroundActiveColor.r, Colors.Light.ButtonToplevelBackgroundActiveColor.g, Colors.Light.ButtonToplevelBackgroundActiveColor.b, a) for _, _, _, a in background.getdata()])
            self._light_image_active = background.copy()
            background.putdata([(Colors.Light.ButtonBackgroundDisabledColor.r, Colors.Light.ButtonBackgroundDisabledColor.g, Colors.Light.ButtonBackgroundDisabledColor.b, a) if not self._toplevel else (Colors.Light.ButtonToplevelBackgroundDisabledColor.r, Colors.Light.ButtonToplevelBackgroundDisabledColor.g, Colors.Light.ButtonToplevelBackgroundDisabledColor.b, a) for _, _, _, a in background.getdata()])
            self._light_image_disabled = background.copy()

        if not self._toplevel:
            with Image.open(Assets.BORDER) as border:
                border.putdata([(Colors.Dark.ButtonBorderColor.r, Colors.Dark.ButtonBorderColor.g, Colors.Dark.ButtonBorderColor.b, a) for _, _, _, a in border.getdata()])
                self._dark_image_default = Image.alpha_composite(self._dark_image_default, border)
                self._dark_image_hover = Image.alpha_composite(self._dark_image_hover, border)
                self._dark_image_active = Image.alpha_composite(self._dark_image_active, border)
                self._dark_image_disabled = Image.alpha_composite(self._dark_image_disabled, border)

                border.putdata([(Colors.Light.ButtonBorderColor.r, Colors.Light.ButtonBorderColor.g, Colors.Light.ButtonBorderColor.b, a) for _, _, _, a in border.getdata()])
                self._light_image_default = Image.alpha_composite(self._light_image_default, border)
                self._light_image_hover = Image.alpha_composite(self._light_image_hover, border)
                self._light_image_active = Image.alpha_composite(self._light_image_active, border)
                self._light_image_disabled = Image.alpha_composite(self._light_image_disabled, border)

        with Image.open(Assets.ICON) as icon:
            icon.putdata([(Colors.Dark.IconColor.r, Colors.Dark.IconColor.g, Colors.Dark.IconColor.b, a) for _, _, _, a in icon.getdata()])
            self._dark_image_default = Image.alpha_composite(self._dark_image_default, icon)
            self._dark_image_hover = Image.alpha_composite(self._dark_image_hover, icon)
            self._dark_image_active = Image.alpha_composite(self._dark_image_active, icon)
            self._dark_image_disabled = Image.alpha_composite(self._dark_image_disabled, icon)
            
            icon.putdata([(Colors.Light.IconColor.r, Colors.Light.IconColor.g, Colors.Light.IconColor.b, a) for _, _, _, a in icon.getdata()])
            self._light_image_default = Image.alpha_composite(self._light_image_default, icon)
            self._light_image_hover = Image.alpha_composite(self._light_image_hover, icon)
            self._light_image_active = Image.alpha_composite(self._light_image_active, icon)
            self._light_image_disabled = Image.alpha_composite(self._light_image_disabled, icon)


    def _finalize_image_objects(self) -> None:
        self.image_default = ctk.CTkImage(light_image=self._light_image_default, dark_image=self._dark_image_default, size=(22, 22))
        self.image_hover = ctk.CTkImage(light_image=self._light_image_hover, dark_image=self._dark_image_hover, size=(22, 22))
        self.image_active = ctk.CTkImage(light_image=self._light_image_active, dark_image=self._dark_image_active, size=(22, 22))
        self.image_disabled = ctk.CTkImage(light_image=self._light_image_disabled, dark_image=self._dark_image_disabled, size=(22, 22))