from typing import Optional, Callable

from .localized import LocalizedCTkRadioButton
from .utils import WinAccentTracker, FontStorage, modify_hsv_from_hex

import winaccent  # type: ignore


class RadioButton(LocalizedCTkRadioButton):
    hovered: bool
    pressed: bool

    background_color: str | tuple[str, str]
    background_hovered_color: str | tuple[str, str]
    background_pressed_color: str | tuple[str, str]
    border_color: str | tuple[str, str] = ("#858585", "#999999")
    border_hovered_color: str | tuple[str, str] = ("#828282", "#9B9B9B")
    border_pressed_color: str | tuple[str, str]


    def __init__(self, master, key: Optional[str] = None, modification: Optional[Callable[[str], str]] = None, **kwargs) -> None:
        if "cursor" not in kwargs: kwargs["cursor"] = "hand2"
        if "font" not in kwargs: kwargs["font"] = FontStorage.get(size=14)
        if "text_color" not in kwargs: kwargs["text_color"] = ("#1A1A1A", "#FFFFFF")
        if "radiobutton_width" not in kwargs: kwargs["radiobutton_width"] = 20
        if "radiobutton_height" not in kwargs: kwargs["radiobutton_height"] = 20
        if "border_width_unchecked" not in kwargs: kwargs["border_width_unchecked"] = 1
        if "border_width_checked" not in kwargs: kwargs["border_width_checked"] = 4
        if "corner_radius" not in kwargs: kwargs["corner_radius"] = 999
        super().__init__(master, key=key, modification=modification, **kwargs)
        self.hovered = False
        self.pressed = False

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
        self.border_pressed_color = self.background_pressed_color
        self._update_colors()


    def _update_colors(self) -> None:
        if self.pressed: self.configure(fg_color=self.background_pressed_color, hover_color=self.background_pressed_color, border_color=self.border_pressed_color)
        elif self.hovered: self.configure(fg_color=self.background_hovered_color, hover_color=self.background_hovered_color, border_color=self.border_hovered_color)
        else: self.configure(fg_color=self.background_color, hover_color=self.background_color, border_color=self.border_color)