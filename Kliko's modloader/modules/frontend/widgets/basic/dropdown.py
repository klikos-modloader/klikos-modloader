from typing import Optional, Callable

from .localized import LocalizedCTkOptionMenu
from .utils import FontStorage, get_fg_color, modify_hsv_from_hex


class DropDownMenu(LocalizedCTkOptionMenu):
    hovered: bool

    background_color: str | tuple[str, str]
    background_hovered_color: str | tuple[str, str]


    def __init__(self, master, value_keys: list[str], value_modifications: Optional[list[Optional[Callable[[str], str]]]] = None, **kwargs) -> None:
        if "cursor" not in kwargs: kwargs["cursor"] = "hand2"
        if "font" not in kwargs: kwargs["font"] = FontStorage.get(size=14)
        if "dropdown_font" not in kwargs: kwargs["font"] = kwargs["font"]
        if "text_color" not in kwargs: kwargs["text_color"] = ("#1A1A1A", "#FFFFFF")
        if "dropdown_text_color" not in kwargs: kwargs["dropdown_text_color"] = kwargs["text_color"]
        if "corner_radius" not in kwargs: kwargs["corner_radius"] = 4
        if "height" not in kwargs: kwargs["height"] = 32
        if "dropdown_fg_color" not in kwargs: kwargs["dropdown_fg_color"] = ("#F9F9F9", "#2C2C2C")
        if "dropdown_hover_color" not in kwargs: kwargs["dropdown_hover_color"] = ("#F0F0F0", "#383838")
        super().__init__(master, value_keys=value_keys, value_modifications=value_modifications, **kwargs)
        self.hovered = False
        self.pressed = False

        fg_color: tuple[str, str] = get_fg_color(master)
        self.background_color = (modify_hsv_from_hex(fg_color[0], 0, 0, 3), modify_hsv_from_hex(fg_color[1], 0, 0, 5))
        self.background_hovered_color = (modify_hsv_from_hex(fg_color[0], 0, 0, 1), modify_hsv_from_hex(fg_color[1], 0, 0, 7))

        self._update_colors()

        self.bind("<Enter>", self._on_hover_in)
        self.bind("<Leave>", self._on_hover_out)


    def _on_hover_in(self, _) -> None:
        self.hovered = True
        self._update_colors()


    def _on_hover_out(self, _) -> None:
        self.hovered = False
        self._update_colors()


    def _update_colors(self) -> None:
        if self.hovered: self.configure(fg_color=self.background_hovered_color, button_color=self.background_hovered_color, button_hover_color=self.background_hovered_color)
        else: self.configure(fg_color=self.background_color, button_color=self.background_color, button_hover_color=self.background_color)