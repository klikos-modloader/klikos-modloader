from typing import Optional, Callable

from .localized import LocalizedCTkButton
from .utils import WinAccentTracker, FontStorage, get_fg_color, modify_hsv_from_hex

import winaccent  # type: ignore


class Button(LocalizedCTkButton):
    secondary: bool
    transparent: bool
    hovered: bool
    pressed: bool

    background_color: str | tuple[str, str]
    background_hovered_color: str | tuple[str, str]
    background_pressed_color: str | tuple[str, str]
    text_color: str | tuple[str, str] = ("#FFFFFF", "#1A1A1A")
    text_hovered_color: str | tuple[str, str] = ("#FFFFFF", "#1A1A1A")
    text_pressed_color: str | tuple[str, str] = ("#FFFFFF", "#1A1A1A")
    border_color: str | tuple[str, str]
    border_hovered_color: str | tuple[str, str]
    border_pressed_color: str | tuple[str, str]
    border_width: int = 0

    background_color_secondary: str | tuple[str, str]
    background_hovered_color_secondary: str | tuple[str, str]
    background_pressed_color_secondary: str | tuple[str, str]
    text_color_secondary: str | tuple[str, str] = ("#1A1A1A", "#FFFFFF")
    text_hovered_color_secondary: str | tuple[str, str] = ("#1A1A1A", "#FFFFFF")
    text_pressed_color_secondary: str | tuple[str, str] = ("#1A1A1A", "#FFFFFF")
    border_color_secondary: str | tuple[str, str]
    border_hovered_color_secondary: str | tuple[str, str]
    border_pressed_color_secondary: str | tuple[str, str]
    border_width_secondary: int = 1

    background_color_transparent: str | tuple[str, str]
    background_hovered_color_transparent: str | tuple[str, str]
    background_pressed_color_transparent: str | tuple[str, str]
    text_color_transparent: str | tuple[str, str] = text_color_secondary
    text_hovered_color_transparent: str | tuple[str, str] = text_hovered_color_secondary
    text_pressed_color_transparent: str | tuple[str, str] = text_pressed_color_secondary
    border_color_transparent: str | tuple[str, str]
    border_hovered_color_transparent: str | tuple[str, str]
    border_pressed_color_transparent: str | tuple[str, str]
    border_width_transparent: int = 0


    def __init__(self, master, key: Optional[str] = None, modification: Optional[Callable[[str], str]] = None, secondary: bool = False, transparent: bool = False, **kwargs) -> None:
        if "cursor" not in kwargs: kwargs["cursor"] = "hand2"
        if "font" not in kwargs: kwargs["font"] = FontStorage.get(size=14)
        if "text_color" not in kwargs: kwargs["text_color"] = ("#1A1A1A", "#FFFFFF")
        if "corner_radius" not in kwargs: kwargs["corner_radius"] = 4
        if "height" not in kwargs: kwargs["height"] = 32
        if "width" not in kwargs: kwargs["width"] = 0
        super().__init__(master, key=key, modification=modification, **kwargs)
        self.secondary = secondary
        self.transparent = transparent
        self.hovered = False
        self.pressed = False

        fg_color: tuple[str, str] = get_fg_color(master)
        self.background_color_secondary = (modify_hsv_from_hex(fg_color[0], 0, 0, 3), modify_hsv_from_hex(fg_color[1], 0, 0, 5))
        self.background_hovered_color_secondary = (modify_hsv_from_hex(fg_color[0], 0, 0, 1), modify_hsv_from_hex(fg_color[1], 0, 0, 7))
        self.background_pressed_color_secondary = (modify_hsv_from_hex(fg_color[0], 0, 0, 1), modify_hsv_from_hex(fg_color[1], 0, 0, 2))
        self.border_color_secondary = (modify_hsv_from_hex(fg_color[0], 0, 0, -5), modify_hsv_from_hex(fg_color[1], 0, 0, 6))
        self.border_hovered_color_secondary = self.border_color_secondary
        self.border_pressed_color_secondary = self.border_color_secondary

        self.background_color_transparent = fg_color
        self.background_hovered_color_transparent = (modify_hsv_from_hex(fg_color[0], 0, 0, -3), modify_hsv_from_hex(fg_color[1], 0, 0, 5))
        self.background_pressed_color_transparent = (modify_hsv_from_hex(fg_color[0], 0, 0, -2), modify_hsv_from_hex(fg_color[1], 0, 0, 3))
        self.border_color_transparent = fg_color
        self.border_hovered_color_transparent = self.background_hovered_color_transparent
        self.border_pressed_color_transparent = self.background_pressed_color_transparent

        WinAccentTracker.add_callback(lambda: self.after(0, self._on_accent_change))
        self._on_accent_change()

        self.bind("<Enter>", self._on_hover_in)
        self.bind("<Leave>", self._on_hover_out)
        self.bind("<ButtonPress-1>", self._on_press_in)
        self.bind("<ButtonRelease-1>", self._on_press_out)


    def _on_hover_in(self, _) -> None:
        self.hovered = True
        self._update_colors()


    def _on_hover_out(self, _) -> None:
        self.hovered = False
        self._update_colors()


    def _on_press_in(self, _) -> None:
        self.pressed = True
        self._update_colors()


    def _on_press_out(self, _) -> None:
        self.pressed = False
        self._update_colors()


    def _on_accent_change(self) -> None:
        self.background_color = (winaccent.accent_dark_1, winaccent.accent_light_2)
        self.background_hovered_color = (modify_hsv_from_hex(winaccent.accent_dark_1, 0, -10, 2), modify_hsv_from_hex(winaccent.accent_light_2, 0, -1, -9))
        self.background_pressed_color = (modify_hsv_from_hex(winaccent.accent_dark_1, 0, -20, 4), modify_hsv_from_hex(winaccent.accent_light_2, 0, -2, -17))
        self.border_color = (modify_hsv_from_hex(winaccent.accent_dark_1, 0, -8, 2), modify_hsv_from_hex(winaccent.accent_light_2, 0, -4, 0))
        self.border_hovered_color = (modify_hsv_from_hex(winaccent.accent_dark_1, 0, -18, 3), modify_hsv_from_hex(winaccent.accent_light_2, 0, -5, -8))
        self.border_pressed_color = self.background_pressed_color
        self._update_colors()


    def _update_colors(self) -> None:
        if self.pressed:
            if self.secondary: self.configure(fg_color=self.background_pressed_color_secondary, hover_color=self.background_hovered_color_secondary, text_color=self.text_pressed_color_secondary, border_color=self.border_pressed_color_secondary, border_width=self.border_width_secondary)
            elif self.transparent: self.configure(fg_color=self.background_pressed_color_transparent, hover_color=self.background_hovered_color_transparent, text_color=self.text_pressed_color_transparent, border_color=self.border_pressed_color_transparent, border_width=self.border_width_transparent)
            else: self.configure(fg_color=self.background_pressed_color, hover_color=self.background_pressed_color, text_color=self.text_pressed_color, border_color=self.border_pressed_color, border_width=self.border_width)

        elif self.hovered:
            if self.secondary: self.configure(fg_color=self.background_hovered_color_secondary, hover_color=self.background_hovered_color_secondary, text_color=self.text_hovered_color_secondary, border_color=self.border_hovered_color_secondary, border_width=self.border_width_secondary)
            elif self.transparent: self.configure(fg_color=self.background_hovered_color_transparent, hover_color=self.background_hovered_color_transparent, text_color=self.text_hovered_color_transparent, border_color=self.border_hovered_color_transparent, border_width=self.border_width_transparent)
            else: self.configure(fg_color=self.background_hovered_color, hover_color=self.background_hovered_color, text_color=self.text_hovered_color, border_color=self.border_hovered_color, border_width=self.border_width)

        else:
            if self.secondary: self.configure(fg_color=self.background_color_secondary, text_color=self.text_color_secondary, border_color=self.border_color_secondary, border_width=self.border_width_secondary)
            elif self.transparent: self.configure(fg_color=self.background_color_transparent, text_color=self.text_color_transparent, border_color=self.border_color_transparent, border_width=self.border_width_transparent)
            else: self.configure(fg_color=self.background_color, hover_color=self.background_color, text_color=self.text_color, border_color=self.border_color, border_width=self.border_width)