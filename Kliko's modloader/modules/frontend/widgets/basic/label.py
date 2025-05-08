from typing import Optional, Callable, Literal

from .utils import FontStorage
from .localized import LocalizedCTkLabel

from customtkinter import CTkFont  # type: ignore


class Label(LocalizedCTkLabel):
    autowrap: bool
    _update_debounce: int = 100
    _update_id = None


    def __init__(self, master, key: Optional[str] = None, modification: Optional[Callable[[str], str]] = None, weight: Literal['normal', 'bold'] | None = None, slant: Literal['italic', 'roman'] = "roman", underline: bool = False, overstrike: bool = False, style: Optional[Literal["caption", "body", "body_strong", "subtitle", "title", "title_large", "display"]] = None, autowrap: bool = False, **kwargs):
        if style is not None: kwargs["font"] = self._get_font_from_style(style, underline=underline, overstrike=overstrike)
        elif "font" not in kwargs: kwargs["font"] = FontStorage.get(14, weight=weight, slant=slant, underline=underline, overstrike=overstrike)
        if "text_color" not in kwargs: kwargs["text_color"] = ("#1A1A1A", "#FFFFFF")
        if "justify" not in kwargs and "anchor" not in kwargs:
            kwargs["justify"] = "left"
            kwargs["anchor"] = "w"
        super().__init__(master, key=key, modification=modification, **kwargs)
        self.autowrap = autowrap
        self.bind("<Configure>", self.update_wraplength)


    def update_wraplength(self, event):
        if not self.autowrap: return
        if self._update_id: self.after_cancel(self._update_id)
        self._update_id = self.after(self._update_debounce, lambda: self.configure(wraplength=event.width))


    def _get_font_from_style(self, style: Literal["caption", "body", "body_strong", "subtitle", "title", "title_large", "display"], underline: bool, overstrike: bool) -> CTkFont:
        match style.lower():
            case "caption":
                font_size: int = 12
                font_weight: Literal["normal", "bold"] = "normal"

            case "body":
                font_size = 14
                font_weight = "normal"

            case "body_strong":
                font_size = 14
                font_weight = "bold"

            case "subtitle":
                font_size = 20
                font_weight = "bold"

            case "title":
                font_size = 28
                font_weight = "bold"

            case "title_large":
                font_size = 40
                font_weight = "bold"

            case "display":
                font_size = 68
                font_weight = "bold"

            case _: raise ValueError(f"Label: Invalid style '{style}'. Must be {', '.join(["caption", "body", "body_strong", "subtitle", "title", "title_large", "display"])}")

        return FontStorage.get(size=font_size, weight=font_weight, underline=underline, overstrike=overstrike)