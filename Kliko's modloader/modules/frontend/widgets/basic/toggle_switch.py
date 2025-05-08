from typing import Optional, Callable

from .localized import LocalizedCTkSwitch
from .utils import WinAccentTracker, FontStorage, modify_hsv_from_hex

import winaccent  # type: ignore


class ToggleSwitch(LocalizedCTkSwitch):
    hovered: bool
    pressed: bool

    progress_color: str | tuple[str, str]
    progress_hovered_color: str | tuple[str, str]
    progress_pressed_color: str | tuple[str, str]


    def __init__(self, master, key: Optional[str] = None, modification: Optional[Callable[[str], str]] = None, **kwargs) -> None:
        if "cursor" not in kwargs: kwargs["cursor"] = "hand2"
        if "font" not in kwargs: kwargs["font"] = FontStorage.get(size=14)
        if "text_color" not in kwargs: kwargs["text_color"] = ("#1A1A1A", "#FFFFFF")
        if "border_width" not in kwargs: kwargs["border_width"] = 1
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
        self.progress_color = (winaccent.accent_normal, winaccent.accent_light_1)
        self.progress_hovered_color = (modify_hsv_from_hex(winaccent.accent_normal, 0, -10, 2), modify_hsv_from_hex(winaccent.accent_light_1, 0, -1, -9))
        self.progress_pressed_color = (modify_hsv_from_hex(winaccent.accent_normal, 0, -20, 4), modify_hsv_from_hex(winaccent.accent_light_1, 0, -2, -17))
        self._update_colors()


    def _update_colors(self) -> None:
        if self.pressed: self.configure(progress_color=self.progress_pressed_color)
        elif self.hovered: self.configure(progress_color=self.progress_hovered_color)
        else: self.configure(progress_color=self.progress_color)