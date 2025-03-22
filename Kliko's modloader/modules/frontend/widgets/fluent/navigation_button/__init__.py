from pathlib import Path
from typing import Callable

import winaccent  # type: ignore
from PIL import Image  # type: ignore
import customtkinter as ctk  # type: ignore


class Assets:
    DIRECTORY: Path = Path(__file__).parent / "assets"
    BACKGROUND: Path = DIRECTORY / "background.png"
    INDICATOR: Path = DIRECTORY / "indicator.png"


class Colors:
    class Dark:
        class BackgroundColor:
            hex: str = "#202020"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundHoverColor:  # BackgroundActiveColor, BackgroundActiveClickedColor
            hex: str = "#2D2D2D"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundClickedColor:  # BackgroundActiveHoverColor
            hex: str = "#292929"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextColor:  # TextHoverColor, TextActiveColor, TextActiveHoverColor
            hex: str = "#FFFFFF"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextClickedColor:
            hex: str = "#CECECE"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextActiveClickedColor:
            hex: str = "#CFCFCF"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class AccentColor:
            hex: str = winaccent.accent_light_2
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)

    class Light:
        class BackgroundColor:
            hex: str = "#F3F3F3"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundHoverColor:  # BackgroundActiveColor, BackgroundActiveClickedColor
            hex: str = "#EAEAEA"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundClickedColor:  # BackgroundActiveHoverColor
            hex: str = "#EDEDED"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextColor:  # TextHoverColor, TextActiveColor, TextActiveHoverColor
            hex: str = "#1A1A1A"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextClickedColor:
            hex: str = "#5B5B5B"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextActiveClickedColor:
            hex: str = "#5A5A5A"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class AccentColor:
            hex: str = winaccent.accent_dark_1
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)


class FluentNavigationButton(ctk.CTkFrame):
    active: bool = False
    hovered: bool = False
    clicked: bool = False
    command: Callable | None
    _CLASS_NAME: str = "FluentNavigationButton"
    _MIN_WIDTH: int = 36

    _light_image_indicator: Image.Image
    _light_image_default: Image.Image
    _light_image_hover: Image.Image
    _light_image_clicked: Image.Image
    _light_image_active: Image.Image  # _light_image_active_clicked
    _light_image_active_hover: Image.Image

    _dark_image_indicator: Image.Image
    _dark_image_default: Image.Image
    _dark_image_hover: Image.Image
    _dark_image_clicked: Image.Image
    _dark_image_active: Image.Image  # _dark_image_active_clicked
    _dark_image_active_hover: Image.Image

    background_label: ctk.CTkLabel
    foreground_label: ctk.CTkLabel
    icon_label: ctk.CTkLabel | None = None
    image_default: ctk.CTkImage
    image_hover: ctk.CTkImage
    image_clicked: ctk.CTkImage
    image_active: ctk.CTkImage  # image_active_clicked
    image_active_hover: ctk.CTkImage


    def __init__(self, master, text: str = "", icon: ctk.CTkImage | None = None, width: int | None = None, command: Callable | None = None, threaded: bool = False) -> None:
        if width is not None and width < self._MIN_WIDTH:
            raise ValueError(f"{self._CLASS_NAME}: Width may not be less than {self._MIN_WIDTH}")

        super().__init__(master, height=36, fg_color="transparent", cursor="hand2")
        self.command = command
        self.threaded = threaded

        if icon is not None:
            icon.configure(size=(20,20))
            self.icon_label = ctk.CTkLabel(self, image=icon, text="", fg_color="transparent", corner_radius=0, cursor="hand2")
        
        self.foreground_label = ctk.CTkLabel(self, height=16, text=text, corner_radius=0, fg_color="transparent", justify="left", anchor="w", font=ctk.CTkFont(family="Segoe UI"), text_color=(Colors.Light.TextColor.hex, Colors.Dark.TextColor.hex), cursor="hand2")
        self.foreground_label.update_idletasks()

        if width is None:
            width = max(self._MIN_WIDTH, self.foreground_label.winfo_reqwidth() + 24 + 33)
        self._create_image_objects()
        if width > self._MIN_WIDTH:
            self._resize_image_objects(width)
        self._finalize_image_objects(width)

        self.configure(width=width)
        self.background_label = ctk.CTkLabel(self, height=36, width=width, fg_color="transparent", text="")
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        if self.icon_label is not None:
            self.icon_label.place(x=10, y=4)
            self.icon_label.lift()
        self.foreground_label.place(x=45, y=10)
        self.foreground_label.lift()


        self._set_image_object()
        self._set_label_background()
        self._set_text_color()
        
        
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_unclick)
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_unhover)
        self.background_label.bind("<Button-1>", self._on_click)
        self.background_label.bind("<ButtonRelease-1>", self._on_unclick)
        self.background_label.bind("<Enter>", self._on_hover)
        self.background_label.bind("<Leave>", self._on_unhover)
        if self.icon_label is not None:
            self.icon_label.bind("<Button-1>", self._on_click)
            self.icon_label.bind("<ButtonRelease-1>", self._on_unclick)
            self.icon_label.bind("<Enter>", self._on_hover)
            self.icon_label.bind("<Leave>", self._on_unhover)
        self.foreground_label.bind("<Button-1>", self._on_click)
        self.foreground_label.bind("<ButtonRelease-1>", self._on_unclick)
        self.foreground_label.bind("<Enter>", self._on_hover)
        self.foreground_label.bind("<Leave>", self._on_unhover)
    

    def set_command(self, command: Callable | None) -> None:
        self.command = command


    def is_active(self) -> bool:
        return self.active


    def set_active(self) -> None:
        if self.active: return
        self.active = True
        self._set_image_object()
        self._set_label_background()
        self._set_text_color()


    def set_inactive(self) -> None:
        if not self.active: return
        self.active = False
        self._set_image_object()
        self._set_label_background()
        self._set_text_color()
    

    def toggle_active_state(self) -> None:
        self.active = not self.active
        self._set_image_object()
        self._set_label_background()
        self._set_text_color()
    

    def _on_click(self, _) -> None:
        self.clicked = True
        self._set_image_object()
        self._set_label_background()
        self._set_text_color()


    def _on_unclick(self, _) -> None:
        self.clicked = False
        self._set_image_object()
        self._set_label_background()
        self._set_text_color()
        if self.hovered:
            if callable(self.command):
                if self.threaded:
                    self.after(10, self.command)
                else:
                    self.command()


    def _on_hover(self, _) -> None:
        self.hovered = True
        self._set_image_object()
        self._set_label_background()
        self._set_text_color()


    def _on_unhover(self, _) -> None:
        self.hovered = False
        self._set_image_object()
        self._set_label_background()
        self._set_text_color()


    def _set_image_object(self) -> None:
        if self.active and self.clicked: self.background_label.configure(image=self.image_active)
        elif self.active and self.hovered: self.background_label.configure(image=self.image_active_hover)
        elif self.active: self.background_label.configure(image=self.image_active)
        elif not self.active and self.clicked: self.background_label.configure(image=self.image_clicked)
        elif not self.active and self.hovered: self.background_label.configure(image=self.image_hover)
        else: self.background_label.configure(image=self.image_default)


    def _set_label_background(self) -> None:
        if self.active and self.clicked:
            self.foreground_label.configure(fg_color=(Colors.Light.BackgroundHoverColor.hex,Colors.Dark.BackgroundHoverColor.hex))
            if self.icon_label is not None:
                self.icon_label.configure(fg_color=(Colors.Light.BackgroundHoverColor.hex,Colors.Dark.BackgroundHoverColor.hex))
        elif self.active and self.hovered:
            self.foreground_label.configure(fg_color=(Colors.Light.BackgroundClickedColor.hex,Colors.Dark.BackgroundClickedColor.hex))
            if self.icon_label is not None:
                self.icon_label.configure(fg_color=(Colors.Light.BackgroundClickedColor.hex,Colors.Dark.BackgroundClickedColor.hex))
        elif self.active:
            self.foreground_label.configure(fg_color=(Colors.Light.BackgroundHoverColor.hex,Colors.Dark.BackgroundHoverColor.hex))
            if self.icon_label is not None:
                self.icon_label.configure(fg_color=(Colors.Light.BackgroundHoverColor.hex,Colors.Dark.BackgroundHoverColor.hex))
        elif not self.active and self.clicked:
            self.foreground_label.configure(fg_color=(Colors.Light.BackgroundClickedColor.hex,Colors.Dark.BackgroundClickedColor.hex))
            if self.icon_label is not None:
                self.icon_label.configure(fg_color=(Colors.Light.BackgroundClickedColor.hex,Colors.Dark.BackgroundClickedColor.hex))
        elif not self.active and self.hovered:
            self.foreground_label.configure(fg_color=(Colors.Light.BackgroundHoverColor.hex,Colors.Dark.BackgroundHoverColor.hex))
            if self.icon_label is not None:
                self.icon_label.configure(fg_color=(Colors.Light.BackgroundHoverColor.hex,Colors.Dark.BackgroundHoverColor.hex))
        else:
            self.foreground_label.configure(fg_color=(Colors.Light.BackgroundColor.hex,Colors.Dark.BackgroundColor.hex))
            if self.icon_label is not None:
                self.icon_label.configure(fg_color=(Colors.Light.BackgroundColor.hex,Colors.Dark.BackgroundColor.hex))


    def _set_text_color(self) -> None:
        if self.active and self.clicked: self.foreground_label.configure(text_color=(Colors.Light.TextActiveClickedColor.hex, Colors.Dark.TextActiveClickedColor.hex))
        elif self.active and self.hovered: self.foreground_label.configure(text_color=(Colors.Light.TextColor.hex, Colors.Dark.TextColor.hex))
        elif self.active: self.foreground_label.configure(text_color=(Colors.Light.TextColor.hex, Colors.Dark.TextColor.hex))
        elif not self.active and self.clicked: self.foreground_label.configure(text_color=(Colors.Light.TextClickedColor.hex, Colors.Dark.TextClickedColor.hex))
        elif not self.active and self.hovered: self.foreground_label.configure(text_color=(Colors.Light.TextColor.hex, Colors.Dark.TextColor.hex))
        else: self.foreground_label.configure(text_color=(Colors.Light.TextColor.hex, Colors.Dark.TextColor.hex))


    def _create_image_objects(self) -> None:
        with Image.open(Assets.INDICATOR) as indicator:
            indicator.putdata([(Colors.Dark.AccentColor.r, Colors.Dark.AccentColor.g, Colors.Dark.AccentColor.b, a) for _, _, _, a in indicator.getdata()])
            self._dark_image_indicator = indicator.copy()
            indicator.putdata([(Colors.Light.AccentColor.r, Colors.Light.AccentColor.g, Colors.Light.AccentColor.b, a) for _, _, _, a in indicator.getdata()])
            self._light_image_indicator = indicator.copy()

        with Image.open(Assets.BACKGROUND) as background:
            background.putdata([(Colors.Dark.BackgroundColor.r, Colors.Dark.BackgroundColor.g, Colors.Dark.BackgroundColor.b, a) for _, _, _, a in background.getdata()])
            self._dark_image_default = background.copy()
            background.putdata([(Colors.Dark.BackgroundHoverColor.r, Colors.Dark.BackgroundHoverColor.g, Colors.Dark.BackgroundHoverColor.b, a) for _, _, _, a in background.getdata()])
            self._dark_image_hover = background.copy()
            background.putdata([(Colors.Dark.BackgroundClickedColor.r, Colors.Dark.BackgroundClickedColor.g, Colors.Dark.BackgroundClickedColor.b, a) for _, _, _, a in background.getdata()])
            self._dark_image_clicked = background.copy()
            
            background.putdata([(Colors.Light.BackgroundColor.r, Colors.Light.BackgroundColor.g, Colors.Light.BackgroundColor.b, a) for _, _, _, a in background.getdata()])
            self._light_image_default = background.copy()
            background.putdata([(Colors.Light.BackgroundHoverColor.r, Colors.Light.BackgroundHoverColor.g, Colors.Light.BackgroundHoverColor.b, a) for _, _, _, a in background.getdata()])
            self._light_image_hover = background.copy()
            background.putdata([(Colors.Light.BackgroundClickedColor.r, Colors.Light.BackgroundClickedColor.g, Colors.Light.BackgroundClickedColor.b, a) for _, _, _, a in background.getdata()])
            self._light_image_clicked = background.copy()

        self._dark_image_active = Image.alpha_composite(self._dark_image_hover, self._dark_image_indicator)
        self._dark_image_active_hover = Image.alpha_composite(self._dark_image_clicked, self._dark_image_indicator)
        self._light_image_active = Image.alpha_composite(self._light_image_hover, self._light_image_indicator)
        self._light_image_active_hover = Image.alpha_composite(self._light_image_clicked, self._light_image_indicator)


    def _resize_image_objects(self, width: int) -> None:
        def expand_image(old: Image, width: int) -> Image.Image:
            _, height = old.size
            new: Image = Image.new("RGBA", (width, height))
            new.paste(old.crop((0, 0, int(self._MIN_WIDTH/2), 36)), (0, 0))
            new.paste(old.crop((int(self._MIN_WIDTH/2), 0, self._MIN_WIDTH, 36)), (width-int(self._MIN_WIDTH/2), 0))
            new.paste(old.crop((int(self._MIN_WIDTH/2)-1, 0, int(self._MIN_WIDTH/2), 36)).resize((width-self._MIN_WIDTH, 36)), (int(self._MIN_WIDTH/2), 0))
            return new

        self._dark_image_default = expand_image(self._dark_image_default, width)
        self._dark_image_hover = expand_image(self._dark_image_hover, width)
        self._dark_image_clicked = expand_image(self._dark_image_clicked, width)
        self._dark_image_active = expand_image(self._dark_image_active, width)
        self._dark_image_active_hover = expand_image(self._dark_image_active_hover, width)

        self._light_image_default = expand_image(self._light_image_default, width)
        self._light_image_hover = expand_image(self._light_image_hover, width)
        self._light_image_clicked = expand_image(self._light_image_clicked, width)
        self._light_image_active = expand_image(self._light_image_active, width)
        self._light_image_active_hover = expand_image(self._light_image_active_hover, width)
    

    def _finalize_image_objects(self, width: int) -> None:
        self.image_default = ctk.CTkImage(light_image=self._light_image_default, dark_image=self._dark_image_default, size=(width, 36))
        self.image_hover = ctk.CTkImage(light_image=self._light_image_hover, dark_image=self._dark_image_hover, size=(width, 36))
        self.image_clicked = ctk.CTkImage(light_image=self._light_image_clicked, dark_image=self._dark_image_clicked, size=(width, 36))
        self.image_active = ctk.CTkImage(light_image=self._light_image_active, dark_image=self._dark_image_active, size=(width, 36))
        self.image_active_hover = ctk.CTkImage(light_image=self._light_image_active_hover, dark_image=self._dark_image_active_hover, size=(width, 36))