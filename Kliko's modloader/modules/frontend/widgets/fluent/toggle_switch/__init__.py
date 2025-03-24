import colorsys
from pathlib import Path
from typing import Callable, Literal

import winaccent  # type: ignore
from PIL import Image  # type: ignore
import customtkinter as ctk  # type: ignore


class Assets:
    DIRECTORY: Path = Path(__file__).parent / "assets"
    BACKGROUND: Path = DIRECTORY / "background.png"
    BORDER: Path = DIRECTORY / "border.png"
    DOT_DEFAULT: Path = DIRECTORY / "dot_default.png"
    DOT_HOVER: Path = DIRECTORY / "dot_hover.png"
    DOT_CLICKED: Path = DIRECTORY / "dot_clicked.png"
    DOT_ACTIVE_DEFAULT: Path = DIRECTORY / "dot_active_default.png"
    DOT_ACTIVE_HOVER: Path = DIRECTORY / "dot_active_hover.png"
    DOT_ACTIVE_CLICKED: Path = DIRECTORY / "dot_active_clicked.png"


def get_ActiveHoverColor(hex: str, darkmode: bool = False, border: bool = False) -> str:
    r, g, b = int(hex[1:3], 16), int(hex[3:5], 16), int(hex[5:7], 16)
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

    if darkmode and not border:
        s = max(0.0, s - 1 / 100)
        v = max(0.0, v - 9 / 100)
    elif not darkmode and not border:
        s = max(0.0, s - 10 / 100)
        v = min(1.0, v + 2 / 100)
    elif darkmode and border:
        h = (h * 360 + 1) % 360 / 360
        s = max(0.0, s - 1 / 100)
        v = max(0.0, v - 5 / 100)
    elif not darkmode and border:
        s = max(0.0, s - 6 / 100)

    r, g, b = colorsys.hsv_to_rgb(h, s, v)  # type: ignore
    hex = f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}"
    return hex


def get_ActiveClickedColor(hex: str, darkmode: bool = False, border: bool = False) -> str:
    r, g, b = int(hex[1:3], 16), int(hex[3:5], 16), int(hex[5:7], 16)
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

    if darkmode and not border:
        s = max(0.0, s - 2 / 100)
        v = max(0.0, v - 17 / 100)
    elif not darkmode and not border:
        s = max(0.0, s - 10 / 100)
        v = min(1.0, v + 2 / 100)
    elif darkmode and border:
        h = (h * 360 + 1) % 360 / 360
        s = max(0.0, s - 1 / 100)
        v = max(0.0, v - 10 / 100)
    elif not darkmode and border:
        s = max(0.0, s - 2 / 100)

    r, g, b = colorsys.hsv_to_rgb(h, s, v)  # type: ignore
    hex = f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}"
    return hex


class Colors:
    class Dark:
        class BackgroundColor:
            hex: str = "#1D1D1D"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundHoverColor:
            hex: str = "#2A2A2A"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundClickedColor:
            hex: str = "#303030"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundActiveColor:
            hex: str = winaccent.accent_light_2
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundActiveHoverColor:
            hex: str = get_ActiveHoverColor(winaccent.accent_light_2, darkmode=True)
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundActiveClickedColor:
            hex: str = get_ActiveClickedColor(winaccent.accent_light_2, darkmode=True)
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderColor:
            hex: str = "#999999"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderHoverColor:
            hex: str = "#9C9C9C"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderClickedColor:
            hex: str = "#9d9d9d"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderActiveColor:
            hex: str = winaccent.accent_light_2
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderActiveHoverColor:
            hex: str = get_ActiveHoverColor(winaccent.accent_light_2, darkmode=True)
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderActiveClickedColor:
            hex: str = get_ActiveClickedColor(winaccent.accent_light_2, darkmode=True, border=True)
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class DotColor:
            hex: str = "#CCCCCC"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class DotHoverColor:
            hex: str = "#CFCFCF"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class DotClickedColor:
            hex: str = "#D0D0D0"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class DotActiveColor:
            hex: str = "#000000"
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
            hex: str = "#EDEDED"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundHoverColor:
            hex: str = "#E5E5E5"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundClickedColor:
            hex: str = "#DCDCDC"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundActiveColor:
            hex: str = winaccent.accent_dark_1
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundActiveHoverColor:
            hex: str = get_ActiveHoverColor(winaccent.accent_dark_1)
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundActiveClickedColor:
            hex: str = get_ActiveClickedColor(winaccent.accent_dark_1)
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderColor:
            hex: str = "#858585"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderHoverColor:
            hex: str = "#828282"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderClickedColor:
            hex: str = "#808080"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderActiveColor:
            hex: str = winaccent.accent_dark_1
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderActiveHoverColor:
            hex: str = get_ActiveHoverColor(winaccent.accent_dark_1)
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderActiveClickedColor:
            hex: str = get_ActiveClickedColor(winaccent.accent_dark_1, border=True)
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class DotColor:
            hex: str = "#5A5A5A"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class DotHoverColor:
            hex: str = "#575757"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class DotClickedColor:
            hex: str = "#545454"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class DotActiveColor:
            hex: str = "#FFFFFF"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextColor:
            hex: str = "#1B1B1B"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)


class FluentToggleSwitch(ctk.CTkLabel):
    value: bool = False
    hovered: bool = False
    clicked: bool = False
    command: Callable | None

    _light_image_default: Image.Image
    _light_image_hover: Image.Image
    _light_image_clicked: Image.Image
    _light_image_active: Image.Image
    _light_image_active_hover: Image.Image
    _light_image_active_clicked: Image.Image

    _dark_image_default: Image.Image
    _dark_image_hover: Image.Image
    _dark_image_clicked: Image.Image
    _dark_image_active: Image.Image
    _dark_image_active_hover: Image.Image
    _dark_image_active_clicked: Image.Image

    image_default: ctk.CTkImage
    image_hover: ctk.CTkImage
    image_clicked: ctk.CTkImage
    image_active: ctk.CTkImage
    image_active_hover: ctk.CTkImage
    image_active_clicked: ctk.CTkImage


    def __init__(self, master, text: str = "", command: Callable | None = None, compound: Literal["left", "right"] = "left", value: bool = False) -> None:
        self.command = command
        self.value = value

        self._create_image_objects()
        self._finalize_image_objects()

        super().__init__(master, height=20, fg_color="transparent", text=text, font=ctk.CTkFont(family="Segoe UI"), text_color=(Colors.Light.TextColor.hex, Colors.Dark.TextColor.hex), cursor="hand2", compound=compound, padx=8)
        self._set_image_object()
        
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_unclick)
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
    

    def get(self) -> bool:
        return self.state


    def set(self, value: bool) -> None:
        self.value = value


    def _toggle_value(self) -> None:
        self.value = not self.value
        self._set_image_object()
        if callable(self.command):
            self.command(self.value)


    def _on_hover(self, _) -> None:
        self.hovered = True
        self._set_image_object()

    def _on_leave(self, _) -> None:
        self.hovered = False
        self._set_image_object()


    def _on_click(self, _) -> None:
        self.clicked = True
        self._set_image_object()

    def _on_unclick(self, _) -> None:
        self.clicked = False
        self._set_image_object()
        if self.hovered: self._toggle_value()


    def _set_image_object(self) -> None:
        if self.clicked and self.value: self.configure(image=self.image_active_clicked)
        elif self.clicked: self.configure(image=self.image_clicked)
        elif self.hovered and self.value: self.configure(image=self.image_active_hover)
        elif self.hovered: self.configure(image=self.image_hover)
        elif self.value: self.configure(image=self.image_active)
        else: self.configure(image=self.image_default)


    def _create_image_objects(self) -> None:
        with Image.open(Assets.BACKGROUND) as background:
            background_data = background.getdata()
            background.putdata([(Colors.Dark.BackgroundColor.r, Colors.Dark.BackgroundColor.g, Colors.Dark.BackgroundColor.b, a) for _, _, _, a in background_data])
            self._dark_image_default = background.copy()
            background.putdata([(Colors.Dark.BackgroundHoverColor.r, Colors.Dark.BackgroundHoverColor.g, Colors.Dark.BackgroundHoverColor.b, a) for _, _, _, a in background_data])
            self._dark_image_hover = background.copy()
            background.putdata([(Colors.Dark.BackgroundClickedColor.r, Colors.Dark.BackgroundClickedColor.g, Colors.Dark.BackgroundClickedColor.b, a) for _, _, _, a in background_data])
            self._dark_image_clicked = background.copy()
            background.putdata([(Colors.Dark.BackgroundActiveColor.r, Colors.Dark.BackgroundActiveColor.g, Colors.Dark.BackgroundActiveColor.b, a) for _, _, _, a in background_data])
            self._dark_image_active = background.copy()
            background.putdata([(Colors.Dark.BackgroundActiveHoverColor.r, Colors.Dark.BackgroundActiveHoverColor.g, Colors.Dark.BackgroundActiveHoverColor.b, a) for _, _, _, a in background_data])
            self._dark_image_active_hover = background.copy()
            background.putdata([(Colors.Dark.BackgroundActiveClickedColor.r, Colors.Dark.BackgroundActiveClickedColor.g, Colors.Dark.BackgroundActiveClickedColor.b, a) for _, _, _, a in background_data])
            self._dark_image_active_clicked = background.copy()

            background.putdata([(Colors.Light.BackgroundColor.r, Colors.Light.BackgroundColor.g, Colors.Light.BackgroundColor.b, a) for _, _, _, a in background_data])
            self._light_image_default = background.copy()
            background.putdata([(Colors.Light.BackgroundHoverColor.r, Colors.Light.BackgroundHoverColor.g, Colors.Light.BackgroundHoverColor.b, a) for _, _, _, a in background_data])
            self._light_image_hover = background.copy()
            background.putdata([(Colors.Light.BackgroundClickedColor.r, Colors.Light.BackgroundClickedColor.g, Colors.Light.BackgroundClickedColor.b, a) for _, _, _, a in background_data])
            self._light_image_clicked = background.copy()
            background.putdata([(Colors.Light.BackgroundActiveColor.r, Colors.Light.BackgroundActiveColor.g, Colors.Light.BackgroundActiveColor.b, a) for _, _, _, a in background_data])
            self._light_image_active = background.copy()
            background.putdata([(Colors.Light.BackgroundActiveHoverColor.r, Colors.Light.BackgroundActiveHoverColor.g, Colors.Light.BackgroundActiveHoverColor.b, a) for _, _, _, a in background_data])
            self._light_image_active_hover = background.copy()
            background.putdata([(Colors.Light.BackgroundActiveClickedColor.r, Colors.Light.BackgroundActiveClickedColor.g, Colors.Light.BackgroundActiveClickedColor.b, a) for _, _, _, a in background_data])
            self._light_image_active_clicked = background.copy()

        with Image.open(Assets.BORDER) as border:
            border_data = border.getdata()
            border.putdata([(Colors.Dark.BorderColor.r, Colors.Dark.BorderColor.g, Colors.Dark.BorderColor.b, a) for _, _, _, a in border_data])
            self._dark_image_default = Image.alpha_composite(self._dark_image_default, border)
            border.putdata([(Colors.Dark.BorderHoverColor.r, Colors.Dark.BorderHoverColor.g, Colors.Dark.BorderHoverColor.b, a) for _, _, _, a in border_data])
            self._dark_image_hover = Image.alpha_composite(self._dark_image_hover, border)
            border.putdata([(Colors.Dark.BorderClickedColor.r, Colors.Dark.BorderClickedColor.g, Colors.Dark.BorderClickedColor.b, a) for _, _, _, a in border_data])
            self._dark_image_clicked = Image.alpha_composite(self._dark_image_clicked, border)
            border.putdata([(Colors.Dark.BorderActiveColor.r, Colors.Dark.BorderActiveColor.g, Colors.Dark.BorderActiveColor.b, a) for _, _, _, a in border_data])
            self._dark_image_active = Image.alpha_composite(self._dark_image_active, border)
            border.putdata([(Colors.Dark.BorderActiveHoverColor.r, Colors.Dark.BorderActiveHoverColor.g, Colors.Dark.BorderActiveHoverColor.b, a) for _, _, _, a in border_data])
            self._dark_image_active_hover = Image.alpha_composite(self._dark_image_active_hover, border)
            border.putdata([(Colors.Dark.BorderActiveClickedColor.r, Colors.Dark.BorderActiveClickedColor.g, Colors.Dark.BorderActiveClickedColor.b, a) for _, _, _, a in border_data])
            self._dark_image_active_clicked = Image.alpha_composite(self._dark_image_active_clicked, border)

            border.putdata([(Colors.Light.BorderColor.r, Colors.Light.BorderColor.g, Colors.Light.BorderColor.b, a) for _, _, _, a in border_data])
            self._light_image_default = Image.alpha_composite(self._light_image_default, border)
            border.putdata([(Colors.Light.BorderHoverColor.r, Colors.Light.BorderHoverColor.g, Colors.Light.BorderHoverColor.b, a) for _, _, _, a in border_data])
            self._light_image_hover = Image.alpha_composite(self._light_image_hover, border)
            border.putdata([(Colors.Light.BorderClickedColor.r, Colors.Light.BorderClickedColor.g, Colors.Light.BorderClickedColor.b, a) for _, _, _, a in border_data])
            self._light_image_clicked = Image.alpha_composite(self._light_image_clicked, border)
            border.putdata([(Colors.Light.BorderActiveColor.r, Colors.Light.BorderActiveColor.g, Colors.Light.BorderActiveColor.b, a) for _, _, _, a in border_data])
            self._light_image_active = Image.alpha_composite(self._light_image_active, border)
            border.putdata([(Colors.Light.BorderActiveHoverColor.r, Colors.Light.BorderActiveHoverColor.g, Colors.Light.BorderActiveHoverColor.b, a) for _, _, _, a in border_data])
            self._light_image_active_hover = Image.alpha_composite(self._light_image_active_hover, border)
            border.putdata([(Colors.Light.BorderActiveClickedColor.r, Colors.Light.BorderActiveClickedColor.g, Colors.Light.BorderActiveClickedColor.b, a) for _, _, _, a in border_data])
            self._light_image_active_clicked = Image.alpha_composite(self._light_image_active_clicked, border)

        with Image.open(Assets.DOT_DEFAULT) as dot_default:
            dot_default_data = dot_default.getdata()
            dot_default.putdata([(Colors.Dark.DotColor.r, Colors.Dark.DotColor.g, Colors.Dark.DotColor.b, a) for _, _, _, a in dot_default_data])
            self._dark_image_default = Image.alpha_composite(self._dark_image_default, dot_default)
            dot_default.putdata([(Colors.Light.DotColor.r, Colors.Light.DotColor.g, Colors.Light.DotColor.b, a) for _, _, _, a in dot_default_data])
            self._light_image_default = Image.alpha_composite(self._light_image_default, dot_default)

        with Image.open(Assets.DOT_HOVER) as dot_hover:
            dot_hover_data = dot_hover.getdata()
            dot_hover.putdata([(Colors.Dark.DotHoverColor.r, Colors.Dark.DotHoverColor.g, Colors.Dark.DotHoverColor.b, a) for _, _, _, a in dot_hover_data])
            self._dark_image_hover = Image.alpha_composite(self._dark_image_hover, dot_hover)
            dot_hover.putdata([(Colors.Light.DotHoverColor.r, Colors.Light.DotHoverColor.g, Colors.Light.DotHoverColor.b, a) for _, _, _, a in dot_hover_data])
            self._light_image_hover = Image.alpha_composite(self._light_image_hover, dot_hover)

        with Image.open(Assets.DOT_CLICKED) as dot_clicked:
            dot_clicked_data = dot_clicked.getdata()
            dot_clicked.putdata([(Colors.Dark.DotClickedColor.r, Colors.Dark.DotClickedColor.g, Colors.Dark.DotClickedColor.b, a) for _, _, _, a in dot_clicked_data])
            self._dark_image_clicked = Image.alpha_composite(self._dark_image_clicked, dot_clicked)
            dot_clicked.putdata([(Colors.Light.DotClickedColor.r, Colors.Light.DotClickedColor.g, Colors.Light.DotClickedColor.b, a) for _, _, _, a in dot_clicked_data])
            self._light_image_clicked = Image.alpha_composite(self._light_image_clicked, dot_clicked)

        with Image.open(Assets.DOT_ACTIVE_DEFAULT) as dot_active_default:
            dot_active_default_data = dot_active_default.getdata()
            dot_active_default.putdata([(Colors.Dark.DotActiveColor.r, Colors.Dark.DotActiveColor.g, Colors.Dark.DotActiveColor.b, a) for _, _, _, a in dot_active_default_data])
            self._dark_image_active = Image.alpha_composite(self._dark_image_active, dot_active_default)
            dot_active_default.putdata([(Colors.Light.DotActiveColor.r, Colors.Light.DotActiveColor.g, Colors.Light.DotActiveColor.b, a) for _, _, _, a in dot_active_default_data])
            self._light_image_active = Image.alpha_composite(self._light_image_active, dot_active_default)

        with Image.open(Assets.DOT_ACTIVE_HOVER) as dot_active_hover:
            dot_active_hover_data = dot_active_hover.getdata()
            dot_active_hover.putdata([(Colors.Dark.DotActiveColor.r, Colors.Dark.DotActiveColor.g, Colors.Dark.DotActiveColor.b, a) for _, _, _, a in dot_active_hover_data])
            self._dark_image_active_hover = Image.alpha_composite(self._dark_image_active_hover, dot_active_hover)
            dot_active_hover.putdata([(Colors.Light.DotActiveColor.r, Colors.Light.DotActiveColor.g, Colors.Light.DotActiveColor.b, a) for _, _, _, a in dot_active_hover_data])
            self._light_image_active_hover = Image.alpha_composite(self._light_image_active_hover, dot_active_hover)

        with Image.open(Assets.DOT_ACTIVE_CLICKED) as dot_active_clicked:
            dot_active_clicked_data = dot_active_clicked.getdata()
            dot_active_clicked.putdata([(Colors.Dark.DotActiveColor.r, Colors.Dark.DotActiveColor.g, Colors.Dark.DotActiveColor.b, a) for _, _, _, a in dot_active_clicked_data])
            self._dark_image_active_clicked = Image.alpha_composite(self._dark_image_active_clicked, dot_active_clicked)
            dot_active_clicked.putdata([(Colors.Light.DotActiveColor.r, Colors.Light.DotActiveColor.g, Colors.Light.DotActiveColor.b, a) for _, _, _, a in dot_active_clicked_data])
            self._light_image_active_clicked = Image.alpha_composite(self._light_image_active_clicked, dot_active_clicked)


    def _finalize_image_objects(self) -> None:
        self.image_default = ctk.CTkImage(light_image=self._light_image_default, dark_image=self._dark_image_default, size=(40, 20))
        self.image_hover = ctk.CTkImage(light_image=self._light_image_hover, dark_image=self._dark_image_hover, size=(40, 20))
        self.image_clicked = ctk.CTkImage(light_image=self._light_image_clicked, dark_image=self._dark_image_clicked, size=(40, 20))
        self.image_active = ctk.CTkImage(light_image=self._light_image_active, dark_image=self._dark_image_active, size=(40, 20))
        self.image_active_hover = ctk.CTkImage(light_image=self._light_image_active_hover, dark_image=self._dark_image_active_hover, size=(40, 20))
        self.image_active_clicked = ctk.CTkImage(light_image=self._light_image_active_clicked, dark_image=self._dark_image_active_clicked, size=(40, 20))