from pathlib import Path
from typing import Callable, Literal

# import winaccent  # type: ignore
from PIL import Image  # type: ignore
import customtkinter as ctk  # type: ignore


class Assets:
    DIRECTORY: Path = Path(__file__).parent / "assets"
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
            hex: str = "#272727"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundDisabledColor:
            hex: str = "#2A2A2A"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderColor:
            hex: str = "#303030"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextColor:
            hex: str = "#FFFFFF"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextActiveColor:
            hex: str = "#CECECE"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextDisabledColor:
            hex: str = "#787878"
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
            hex: str = "#F5F5F5"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundDisabledColor:
            hex: str = "#F5F5F5"
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
        class TextActiveColor:
            hex: str = "#5D5D5D"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextDisabledColor:
            hex: str = "#9D9D9D"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)


class ColorsToplevel:
    class Dark:
        class BackgroundColor:
            hex: str = "#343434"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundHoverColor:
            hex: str = "#3A3A3A"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundActiveColor:
            hex: str = "#2E2E2E"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundDisabledColor:
            hex: str = "#2A2A2A"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderColor:
            hex: str = "#373737"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextColor:
            hex: str = "#FFFFFF"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextActiveColor:
            hex: str = "#CFCFCF"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextDisabledColor:
            hex: str = "#787878"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)

    class Light:
        class BackgroundColor:
            hex: str = "#FDFDFD"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundHoverColor:
            hex: str = "#F9F9F9"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundActiveColor:
            hex: str = "#F9F9F9"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundDisabledColor:
            hex: str = "#F5F5F5"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderColor:
            hex: str = "#EAEAEA"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextColor:
            hex: str = "#1B1B1B"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextActiveColor:
            hex: str = "#5E5E5E"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextDisabledColor:
            hex: str = "#9D9D9D"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)


class FluentButton(ctk.CTkLabel):
    active: bool = False
    enabled: bool = False
    hovered: bool = False
    command: Callable | None
    threaded: bool
    
    _toplevel: bool

    _CLASS_NAME: str = "FluentButton"
    _MIN_WIDTH: int = 16
    _MIN_HEIGHT: int = 16
    _ASSET_WIDTH: int = 16
    _ASSET_HEIGHT: int = 16

    _light_image_default: Image.Image
    _light_image_hover: Image.Image
    _light_image_active: Image.Image
    _light_image_disabled: Image.Image

    _dark_image_default: Image.Image
    _dark_image_hover: Image.Image
    _dark_image_active: Image.Image
    _dark_image_disabled: Image.Image

    image_default: ctk.CTkImage
    image_hover: ctk.CTkImage
    image_active: ctk.CTkImage
    image_disabled: ctk.CTkImage
    
    
    def __init__(self, master, text: str = "", width: int | None = None, height: int | None = None, command: Callable | None = None, threaded: bool = False, disabled: bool = False, toplevel: bool = False, light_icon: Image.Image | None = None, dark_icon: Image.Image | None = None, icon_size: tuple[int, int] = (24,24), icon_position: Literal["left", "right", "center"] = "center") -> None:
        if width is not None and width < self._MIN_WIDTH: raise ValueError(f"{self._CLASS_NAME}: Width may not be less than {self._MIN_WIDTH}")
        if height is not None and height < self._MIN_HEIGHT: raise ValueError(f"{self._CLASS_NAME}: Height may not be less than {self._MIN_HEIGHT}")
    
        height = height if height is not None else 32

        super().__init__(master, height=height, fg_color="transparent", text=text, font=ctk.CTkFont(family="Segoe UI"), cursor="hand2")
        self.update_idletasks()
        self.enabled = not disabled
        self.command = command
        self.threaded = threaded
        self._toplevel = toplevel

        if width is None:
            width = max(self._MIN_WIDTH, self.winfo_reqwidth() + 24)
        self._create_image_objects()
        if width > self._MIN_WIDTH:
            self._resize_image_objects_horizontal(width)
        if height > self._MIN_HEIGHT:
            self._resize_image_objects_vertical(height)
        
        if light_icon is None and dark_icon is not None: light_icon = dark_icon
        if dark_icon is None and light_icon is not None: dark_icon = light_icon
        if not (light_icon is None and dark_icon is None): self._add_icon_to_image_objects(light_icon, dark_icon, icon_size, icon_position, width, height)
        
        self._finalize_image_objects(width, height)

        self._set_image_object()
        self._set_text_color()
        
        
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_unclick)
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_unhover)


    def is_enabled(self) -> bool:
        return self.enabled


    def enable(self) -> None:
        self.enabled = True
        self._set_image_object()
        self._set_text_color()
    

    def disable(self) -> None:
        self.enabled = False
        self._set_image_object()
        self._set_text_color()
    

    def _on_click(self, _) -> None:
        if not self.enabled: return
        self.active = True
        self._set_image_object()
        self._set_text_color()


    def _on_unclick(self, _) -> None:
        self.active = False
        self._set_image_object()
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
        self._set_text_color()


    def _on_unhover(self, _) -> None:
        self.hovered = False
        self._set_image_object()
        self._set_text_color()


    def _set_image_object(self) -> None:
        if not self.enabled: self.configure(image=self.image_disabled)
        elif self.active: self.configure(image=self.image_active)
        elif self.hovered: self.configure(image=self.image_hover)
        else: self.configure(image=self.image_default)


    def _set_text_color(self) -> None:
        if not self.enabled: self.configure(text_color=(Colors.Light.TextDisabledColor.hex, Colors.Dark.TextDisabledColor.hex) if not self._toplevel else (ColorsToplevel.Light.TextDisabledColor.hex, ColorsToplevel.Dark.TextDisabledColor.hex))
        elif self.active: self.configure(text_color=(Colors.Light.TextActiveColor.hex, Colors.Dark.TextActiveColor.hex) if not self._toplevel else (ColorsToplevel.Light.TextActiveColor.hex, ColorsToplevel.Dark.TextActiveColor.hex))
        else: self.configure(text_color=(Colors.Light.TextColor.hex, Colors.Dark.TextColor.hex) if not self._toplevel else (ColorsToplevel.Light.TextColor.hex, ColorsToplevel.Dark.TextColor.hex))


    def _create_image_objects(self) -> None:
        with Image.open(Assets.BACKGROUND) as background:
            background_data = background.getdata()
            background.putdata([(Colors.Dark.BackgroundColor.r, Colors.Dark.BackgroundColor.g, Colors.Dark.BackgroundColor.b, a) if not self._toplevel else (ColorsToplevel.Dark.BackgroundColor.r, ColorsToplevel.Dark.BackgroundColor.g, ColorsToplevel.Dark.BackgroundColor.b, a) for _, _, _, a in background_data])
            self._dark_image_default = background.copy()
            background.putdata([(Colors.Dark.BackgroundHoverColor.r, Colors.Dark.BackgroundHoverColor.g, Colors.Dark.BackgroundHoverColor.b, a) if not self._toplevel else (ColorsToplevel.Dark.BackgroundHoverColor.r, ColorsToplevel.Dark.BackgroundHoverColor.g, ColorsToplevel.Dark.BackgroundHoverColor.b, a) for _, _, _, a in background_data])
            self._dark_image_hover = background.copy()
            background.putdata([(Colors.Dark.BackgroundActiveColor.r, Colors.Dark.BackgroundActiveColor.g, Colors.Dark.BackgroundActiveColor.b, a) if not self._toplevel else (ColorsToplevel.Dark.BackgroundActiveColor.r, ColorsToplevel.Dark.BackgroundActiveColor.g, ColorsToplevel.Dark.BackgroundActiveColor.b, a) for _, _, _, a in background_data])
            self._dark_image_active = background.copy()
            background.putdata([(Colors.Dark.BackgroundDisabledColor.r, Colors.Dark.BackgroundDisabledColor.g, Colors.Dark.BackgroundDisabledColor.b, a) if not self._toplevel else (ColorsToplevel.Dark.BackgroundDisabledColor.r, ColorsToplevel.Dark.BackgroundDisabledColor.g, ColorsToplevel.Dark.BackgroundDisabledColor.b, a) for _, _, _, a in background_data])
            self._dark_image_disabled = background.copy()

            background.putdata([(Colors.Light.BackgroundColor.r, Colors.Light.BackgroundColor.g, Colors.Light.BackgroundColor.b, a) if not self._toplevel else (ColorsToplevel.Light.BackgroundColor.r, ColorsToplevel.Light.BackgroundColor.g, ColorsToplevel.Light.BackgroundColor.b, a) for _, _, _, a in background_data])
            self._light_image_default = background.copy()
            background.putdata([(Colors.Light.BackgroundHoverColor.r, Colors.Light.BackgroundHoverColor.g, Colors.Light.BackgroundHoverColor.b, a) if not self._toplevel else (ColorsToplevel.Light.BackgroundHoverColor.r, ColorsToplevel.Light.BackgroundHoverColor.g, ColorsToplevel.Light.BackgroundHoverColor.b, a) for _, _, _, a in background_data])
            self._light_image_hover = background.copy()
            background.putdata([(Colors.Light.BackgroundActiveColor.r, Colors.Light.BackgroundActiveColor.g, Colors.Light.BackgroundActiveColor.b, a) if not self._toplevel else (ColorsToplevel.Light.BackgroundActiveColor.r, ColorsToplevel.Light.BackgroundActiveColor.g, ColorsToplevel.Light.BackgroundActiveColor.b, a) for _, _, _, a in background_data])
            self._light_image_active = background.copy()
            background.putdata([(Colors.Light.BackgroundDisabledColor.r, Colors.Light.BackgroundDisabledColor.g, Colors.Light.BackgroundDisabledColor.b, a) if not self._toplevel else (ColorsToplevel.Light.BackgroundDisabledColor.r, ColorsToplevel.Light.BackgroundDisabledColor.g, ColorsToplevel.Light.BackgroundDisabledColor.b, a) for _, _, _, a in background_data])
            self._light_image_disabled = background.copy()

        with Image.open(Assets.BORDER) as border:
            border_data = border.getdata()
            border.putdata([(Colors.Dark.BorderColor.r, Colors.Dark.BorderColor.g, Colors.Dark.BorderColor.b, a) if not self._toplevel else (ColorsToplevel.Dark.BorderColor.r, ColorsToplevel.Dark.BorderColor.g, ColorsToplevel.Dark.BorderColor.b, a) for _, _, _, a in border_data])
            self._dark_image_default = Image.alpha_composite(self._dark_image_default, border)
            self._dark_image_hover = Image.alpha_composite(self._dark_image_hover, border)
            self._dark_image_active = Image.alpha_composite(self._dark_image_active, border)
            self._dark_image_disabled = Image.alpha_composite(self._dark_image_disabled, border)

            border.putdata([(Colors.Light.BorderColor.r, Colors.Light.BorderColor.g, Colors.Light.BorderColor.b, a) if not self._toplevel else (ColorsToplevel.Light.BorderColor.r, ColorsToplevel.Light.BorderColor.g, ColorsToplevel.Light.BorderColor.b, a) for _, _, _, a in border_data])
            self._light_image_default = Image.alpha_composite(self._light_image_default, border)
            self._light_image_hover = Image.alpha_composite(self._light_image_hover, border)
            self._light_image_active = Image.alpha_composite(self._light_image_active, border)
            self._light_image_disabled = Image.alpha_composite(self._light_image_disabled, border)


    def _resize_image_objects_horizontal(self, width: int) -> None:
        def expand_image(old: Image.Image, width: int) -> Image.Image:
            original_width, height = old.size
            new = Image.new("RGBA", (width, height))

            left_width = int(self._ASSET_WIDTH / 2)
            new.paste(old.crop((0, 0, left_width, height)), (0, 0))

            middle_start = left_width
            middle_end = original_width - left_width
            middle_crop = old.crop((middle_start, 0, middle_end, height))
            middle_resized = middle_crop.resize((width - self._ASSET_WIDTH, height))
            new.paste(middle_resized, (left_width, 0))

            right_x_start = original_width - left_width
            new.paste(old.crop((right_x_start, 0, original_width, height)), (width - left_width, 0))

            return new

        self._dark_image_default = expand_image(self._dark_image_default, width)
        self._dark_image_hover = expand_image(self._dark_image_hover, width)
        self._dark_image_active = expand_image(self._dark_image_active, width)
        self._dark_image_disabled = expand_image(self._dark_image_disabled, width)

        self._light_image_default = expand_image(self._light_image_default, width)
        self._light_image_hover = expand_image(self._light_image_hover, width)
        self._light_image_active = expand_image(self._light_image_active, width)
        self._light_image_disabled = expand_image(self._light_image_disabled, width)


    def _resize_image_objects_vertical(self, height: int) -> None:
        def expand_image(old: Image.Image, height: int) -> Image.Image:
            width, original_height = old.size
            new = Image.new("RGBA", (width, height))

            top_height = int(self._ASSET_HEIGHT / 2)
            new.paste(old.crop((0, 0, width, top_height)), (0, 0))

            middle_start = top_height
            middle_end = original_height - top_height
            middle_crop = old.crop((0, middle_start, width, middle_end))
            middle_resized = middle_crop.resize((width, height - self._ASSET_HEIGHT))
            new.paste(middle_resized, (0, top_height))

            bottom_y_start = original_height - top_height
            new.paste(old.crop((0, bottom_y_start, width, original_height)), (0, height - top_height))

            return new

        self._dark_image_default = expand_image(self._dark_image_default, height)
        self._dark_image_hover = expand_image(self._dark_image_hover, height)
        self._dark_image_active = expand_image(self._dark_image_active, height)
        self._dark_image_disabled = expand_image(self._dark_image_disabled, height)

        self._light_image_default = expand_image(self._light_image_default, height)
        self._light_image_hover = expand_image(self._light_image_hover, height)
        self._light_image_active = expand_image(self._light_image_active, height)
        self._light_image_disabled = expand_image(self._light_image_disabled, height)
    

    def _add_icon_to_image_objects(self, light: Image.Image, dark: Image.Image, size: tuple[int, int], position: Literal["left", "right", "center"], width: int, height: int) -> None:
        def resize_icon(image: Image.Image, size: tuple[int, int]) -> Image.Image:
            current_w, current_h = image.size
            target_w, target_h = size
            if image.size == size: return image
            method = Image.LANCZOS if current_w > target_w or current_h > target_h else Image.BICUBIC
            return image.resize(size, method)

        light_resized = resize_icon(light, size)
        dark_resized = resize_icon(dark, size)

        icon_width, icon_height = size
        icon_x: int = 4 if position == "left" else width - icon_width - 4 if position == "right" else width//2 - icon_width//2
        icon_y: int = height//2 - icon_height//2

        light_fitted = Image.new("RGBA", (width, height))
        light_fitted.paste(light_resized, (icon_x, icon_y))
        dark_fitted = Image.new("RGBA", (width, height))
        dark_fitted.paste(dark_resized, (icon_x, icon_y))

        self._dark_image_default = Image.alpha_composite(self._dark_image_default, dark_fitted)
        self._dark_image_hover = Image.alpha_composite(self._dark_image_hover, dark_fitted)
        self._dark_image_active = Image.alpha_composite(self._dark_image_active, dark_fitted)
        self._dark_image_disabled = Image.alpha_composite(self._dark_image_disabled, dark_fitted)

        self._light_image_default = Image.alpha_composite(self._light_image_default, light_fitted)
        self._light_image_hover = Image.alpha_composite(self._light_image_hover, light_fitted)
        self._light_image_active = Image.alpha_composite(self._light_image_active, light_fitted)
        self._light_image_disabled = Image.alpha_composite(self._light_image_disabled, light_fitted)
    

    def _finalize_image_objects(self, width: int, height: int) -> None:
        self.image_default = ctk.CTkImage(light_image=self._light_image_default, dark_image=self._dark_image_default, size=(width, height))
        self.image_hover = ctk.CTkImage(light_image=self._light_image_hover, dark_image=self._dark_image_hover, size=(width, height))
        self.image_active = ctk.CTkImage(light_image=self._light_image_active, dark_image=self._dark_image_active, size=(width, height))
        self.image_disabled = ctk.CTkImage(light_image=self._light_image_disabled, dark_image=self._dark_image_disabled, size=(width, height))