from pathlib import Path
from typing import Literal

import winaccent  # type: ignore
from PIL import Image  # type: ignore
import customtkinter as ctk  # type: ignore


class Assets:
    DIRECTORY: Path = Path(__file__).parent / "assets"
    ACCENT: Path = DIRECTORY / "accent.png"
    BACKGROUND: Path = DIRECTORY / "background.png"
    BORDER: Path = DIRECTORY / "border.png"


class Colors:
    class Dark:
        class BackgroundColor:
            hex: str = "#2D2D2D"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundHoverColor:
            hex: str = "#323232"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundActiveColor:
            hex: str = "#1F1F1F"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderColor:
            hex: str = "#303030"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class AccentColor:
            hex: str = "#9A9A9A"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class AccentActiveColor:
            hex: str = winaccent.accent_light_2
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextColor:
            hex: str = "#FFFFFF"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextPlaceHolderColor:
            hex: str = "#CFCFCF"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)

    class Light:
        class BackgroundColor:
            hex: str = "#FBFBFB"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundHoverColor:
            hex: str = "#F6F6F6"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundActiveColor:
            hex: str = "#FFFFFF"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderColor:
            hex: str = "#E5E5E5"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class AccentColor:
            hex: str = "#868686"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class AccentActiveColor:
            hex: str = winaccent.accent_dark_1
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextColor:
            hex: str = "#1B1B1B"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextPlaceHolderColor:
            hex: str = "#5F5F5F"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)

    class TextSelectColor:
        hex: str = winaccent.accent_normal
        r: int = int(hex[1:3], 16)
        g: int = int(hex[3:5], 16)
        b: int = int(hex[5:7], 16)


class FluentTextBox(ctk.CTkFrame):
    label: ctk.CTkLabel
    entry: ctk.CTkEntry
    text_var: ctk.StringVar
    focused: bool = False
    hovered: bool = False
    _CLASS_NAME: str = "FluentTextBox"
    _MIN_WIDTH: int = 32

    _light_image_default: Image
    _light_image_hover: Image
    _light_image_active: Image

    _dark_image_default: Image
    _dark_image_hover: Image
    _dark_image_active: Image

    image_default: ctk.CTkImage
    image_hover: ctk.CTkImage
    image_active: ctk.CTkImage
    
    
    def __init__(self, master, width: int = _MIN_WIDTH, placeholder: str = "", **kwargs) -> None:
        if width < self._MIN_WIDTH:
            raise ValueError(f"{self._CLASS_NAME}: Width may not be less than {self._MIN_WIDTH}")

        super().__init__(master, width=width, height=32, fg_color="transparent", cursor="xterm")

        self.text_var = ctk.StringVar()

        self._create_image_objects()
        if width > self._MIN_WIDTH:
            self._resize_image_objects(width)
        self._finalize_image_objects(width)

        # Label
        self.label = ctk.CTkLabel(self, text="", fg_color="transparent", image=self.image_default, cursor="xterm")
        self.label.place(x=0, y=0, relwidth=1, relheight=1)

        # Entry
        padx=2
        pady=2
        self.entry = ctk.CTkEntry(self, font=ctk.CTkFont(family="Segoe UI"), placeholder_text=placeholder, width=width-(padx*2), height=32-(pady*2), fg_color=(Colors.Light.BackgroundColor.hex, Colors.Dark.BackgroundColor.hex), text_color=(Colors.Light.TextColor.hex, Colors.Dark.TextColor.hex), placeholder_text_color=(Colors.Light.TextPlaceHolderColor.hex, Colors.Dark.TextPlaceHolderColor.hex), corner_radius=0, border_width=0, **kwargs)
        self.entry._entry.configure(selectbackground=Colors.TextSelectColor.hex)
        self.entry.place(x=padx, y=pady)
        
        self.bind("<Button-1>", self._set_focus)
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
        
        self.label.bind("<Button-1>", self._set_focus)
        self.label.bind("<Enter>", self._on_hover)
        self.label.bind("<Leave>", self._on_leave)
        
        self.entry.bind("<FocusIn>", self._on_focus)
        self.entry.bind("<FocusOut>", self._on_unfocus)
        self.entry.bind("<Enter>", self._on_hover)
        self.entry.bind("<Leave>", self._on_leave)
    

    def get(self) -> str:
        return self.entry.get()


    def set(self, string: str) -> None:
        self.delete(0, "end")
        self.insert(0, string)


    def delete(self, first_index: int | Literal["end", "insert"], last_index: int | Literal["end", "insert"] | None = None) -> None:
        self.entry.delete(first_index, last_index)


    def insert(self, index: int | Literal["end", "insert"], string: str) -> None:
        self.entry.insert(index, string)


    def _set_focus(self, _) -> None:
        if self.focused: return
        self.entry.focus_set()


    def _on_hover(self, _) -> None:
        self.hovered = True
        if self.focused: return
        self.label.configure(image=self.image_hover)
        self.entry.configure(fg_color=(Colors.Light.BackgroundHoverColor.hex, Colors.Dark.BackgroundHoverColor.hex))

    def _on_leave(self, _) -> None:
        self.hovered = False
        if self.focused: return
        self.label.configure(image=self.image_default)
        self.entry.configure(fg_color=(Colors.Light.BackgroundColor.hex, Colors.Dark.BackgroundColor.hex))
    
    def _on_focus(self, _) -> None:
        self.label.configure(image=self.image_active)
        self.entry.configure(fg_color=(Colors.Light.BackgroundActiveColor.hex, Colors.Dark.BackgroundActiveColor.hex))
        self.entry.focus_set()
        self.focused = True

    def _on_unfocus(self, _) -> None:
        if self.hovered:
            self.label.configure(image=self.image_hover)
            self.entry.configure(fg_color=(Colors.Light.BackgroundHoverColor.hex, Colors.Dark.BackgroundHoverColor.hex))
        else:
            self.label.configure(image=self.image_default)
            self.entry.configure(fg_color=(Colors.Light.BackgroundColor.hex, Colors.Dark.BackgroundColor.hex))
        self.focused = False


    def _create_image_objects(self) -> None:
        with Image.open(Assets.BACKGROUND) as background:
            background.putdata([(Colors.Dark.BackgroundColor.r, Colors.Dark.BackgroundColor.g, Colors.Dark.BackgroundColor.b, a) for _, _, _, a in background.getdata()])
            self._dark_image_default = background.copy()
            background.putdata([(Colors.Dark.BackgroundHoverColor.r, Colors.Dark.BackgroundHoverColor.g, Colors.Dark.BackgroundHoverColor.b, a) for _, _, _, a in background.getdata()])
            self._dark_image_hover = background.copy()
            background.putdata([(Colors.Dark.BackgroundActiveColor.r, Colors.Dark.BackgroundActiveColor.g, Colors.Dark.BackgroundActiveColor.b, a) for _, _, _, a in background.getdata()])
            self._dark_image_active = background.copy()

            background.putdata([(Colors.Light.BackgroundColor.r, Colors.Light.BackgroundColor.g, Colors.Light.BackgroundColor.b, a) for _, _, _, a in background.getdata()])
            self._light_image_default = background.copy()
            background.putdata([(Colors.Light.BackgroundHoverColor.r, Colors.Light.BackgroundHoverColor.g, Colors.Light.BackgroundHoverColor.b, a) for _, _, _, a in background.getdata()])
            self._light_image_hover = background.copy()
            background.putdata([(Colors.Light.BackgroundActiveColor.r, Colors.Light.BackgroundActiveColor.g, Colors.Light.BackgroundActiveColor.b, a) for _, _, _, a in background.getdata()])
            self._light_image_active = background.copy()

        with Image.open(Assets.BORDER) as border:
            border.putdata([(Colors.Dark.BorderColor.r, Colors.Dark.BorderColor.g, Colors.Dark.BorderColor.b, a) for _, _, _, a in border.getdata()])
            self._dark_image_default = Image.alpha_composite(self._dark_image_default, border)
            self._dark_image_hover = Image.alpha_composite(self._dark_image_hover, border)
            self._dark_image_active = Image.alpha_composite(self._dark_image_active, border)

            border.putdata([(Colors.Light.BorderColor.r, Colors.Light.BorderColor.g, Colors.Light.BorderColor.b, a) for _, _, _, a in border.getdata()])
            self._light_image_default = Image.alpha_composite(self._light_image_default, border)
            self._light_image_hover = Image.alpha_composite(self._light_image_hover, border)
            self._light_image_active = Image.alpha_composite(self._light_image_active, border)

        with Image.open(Assets.ACCENT) as accent:
            accent.putdata([(Colors.Dark.AccentColor.r, Colors.Dark.AccentColor.g, Colors.Dark.AccentColor.b, a) for _, _, _, a in accent.getdata()])
            self._dark_image_default = Image.alpha_composite(self._dark_image_default, accent)
            self._dark_image_hover = Image.alpha_composite(self._dark_image_hover, accent)
            accent.putdata([(Colors.Dark.AccentActiveColor.r, Colors.Dark.AccentActiveColor.g, Colors.Dark.AccentActiveColor.b, a) for _, _, _, a in accent.getdata()])
            self._dark_image_active = Image.alpha_composite(self._dark_image_active, accent)

            accent.putdata([(Colors.Light.AccentColor.r, Colors.Light.AccentColor.g, Colors.Light.AccentColor.b, a) for _, _, _, a in accent.getdata()])
            self._light_image_default = Image.alpha_composite(self._light_image_default, accent)
            self._light_image_hover = Image.alpha_composite(self._light_image_hover, accent)
            accent.putdata([(Colors.Light.AccentActiveColor.r, Colors.Light.AccentActiveColor.g, Colors.Light.AccentActiveColor.b, a) for _, _, _, a in accent.getdata()])
            self._light_image_active = Image.alpha_composite(self._light_image_active, accent)


    def _resize_image_objects(self, width: int) -> None:
        def expand_image(old: Image, width: int) -> Image:
            _, height = old.size
            new: Image = Image.new("RGBA", (width, height))
            new.paste(old.crop((0, 0, int(self._MIN_WIDTH/2), 32)), (0, 0))
            new.paste(old.crop((int(self._MIN_WIDTH/2), 0, self._MIN_WIDTH, 32)), (width-int(self._MIN_WIDTH/2), 0))
            new.paste(old.crop((int(self._MIN_WIDTH/2)-1, 0, int(self._MIN_WIDTH/2), 32)).resize((width-self._MIN_WIDTH, 32)), (int(self._MIN_WIDTH/2), 0))
            return new

        self._dark_image_default = expand_image(self._dark_image_default, width)
        self._dark_image_hover = expand_image(self._dark_image_hover, width)
        self._dark_image_active = expand_image(self._dark_image_active, width)

        self._light_image_default = expand_image(self._light_image_default, width)
        self._light_image_hover = expand_image(self._light_image_hover, width)
        self._light_image_active = expand_image(self._light_image_active, width)
    

    def _finalize_image_objects(self, width: int) -> None:
        self.image_default = ctk.CTkImage(light_image=self._light_image_default, dark_image=self._dark_image_default, size=(width, 32))
        self.image_hover = ctk.CTkImage(light_image=self._light_image_hover, dark_image=self._dark_image_hover, size=(width, 32))
        self.image_active = ctk.CTkImage(light_image=self._light_image_active, dark_image=self._dark_image_active, size=(width, 32))
