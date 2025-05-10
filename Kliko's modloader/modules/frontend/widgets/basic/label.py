from typing import Optional, Callable, Literal
import webbrowser

from .localized import LocalizedCTkLabel
from .utils import FontStorage, WinAccentTracker

from customtkinter import CTkFont  # type: ignore
import winaccent  # type: ignore


class Label(LocalizedCTkLabel):
    autowrap: bool
    _update_debounce: int = 100
    _update_id = None

    _url: Optional[str]
    _url_color_default: tuple[str, str]
    _url_color_hovered: tuple[str, str]
    _url_color_pressed: tuple[str, str]
    _url_font_default: CTkFont
    _url_font_hovered: CTkFont
    _url_font_pressed: CTkFont
    _url_hovered: bool = False
    _url_pressed: bool = False


    def __init__(self, master, key: Optional[str] = None, modification: Optional[Callable[[str], str]] = None, weight: Literal['normal', 'bold'] | None = None, slant: Literal['italic', 'roman'] = "roman", underline: bool = False, overstrike: bool = False, style: Optional[Literal["caption", "body", "body_strong", "subtitle", "title", "title_large", "display"]] = None, autowrap: bool = False, url: Optional[str] = None, **kwargs):
        if style is not None: kwargs["font"] = self._get_font_from_style(style, underline=underline, overstrike=overstrike)
        elif "font" not in kwargs: kwargs["font"] = FontStorage.get(14, weight=weight, slant=slant, underline=underline, overstrike=overstrike)
        if "text_color" not in kwargs: kwargs["text_color"] = ("#1A1A1A", "#FFFFFF")
        if "justify" not in kwargs and "anchor" not in kwargs:
            kwargs["justify"] = "left"
            kwargs["anchor"] = "w"
        super().__init__(master, key=key, modification=modification, **kwargs)
        self.autowrap = autowrap
        self.bind("<Configure>", self.update_wraplength)

        self._url = url
        if self._url:
            font: CTkFont = kwargs["font"]
            self._url_font_default = FontStorage.get(font.cget("size"), font.cget("weight"), font.cget("slant"), True, font.cget("overstrike"))
            self._url_font_hovered = FontStorage.get(font.cget("size"), font.cget("weight"), font.cget("slant"), False, font.cget("overstrike"))
            self._url_font_pressed = self._url_font_hovered

            WinAccentTracker.add_callback(lambda: self.after(0, self._on_accent_change))
            self._on_accent_change()

            self.configure(cursor="hand2", font=self._url_font_default)
            self.bind("<Enter>", self._on_url_hover)
            self.bind("<Leave>", self._on_url_unhover)
            self.bind("<ButtonPress-1>", self._on_url_press)
            self.bind("<ButtonRelease-1>", self._on_url_unpress)


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


    def _on_accent_change(self) -> None:
        self._url_color_default = (winaccent.accent_dark_2, winaccent.accent_light_3)
        self._url_color_hovered = (winaccent.accent_dark_3, winaccent.accent_light_3)
        self._url_color_pressed = (winaccent.accent_dark_1, winaccent.accent_light_2)
        self._update_url_background()


    def _on_url_hover(self, _) -> None:
        if self._url_hovered: return
        self._url_hovered = True
        if not self._url_pressed: self._update_url_background()


    def _on_url_unhover(self, _) -> None:
        if not self._url_hovered: return
        self._url_hovered = False
        if not self._url_pressed: self._update_url_background()


    def _on_url_press(self, _) -> None:
        self._url_pressed = True
        self._update_url_background()


    def _on_url_unpress(self, _) -> None:
        self._url_pressed = False
        self._update_url_background()
        if not self._url_hovered: return
        self.focus_set()
        if self._url: webbrowser.open_new_tab(self._url)


    def _update_url_background(self) -> None:
        if self._url_pressed: self.configure(font=self._url_font_pressed, text_color=self._url_color_pressed)
        elif self._url_hovered: self.configure(font=self._url_font_hovered, text_color=self._url_color_hovered)
        else: self.configure(font=self._url_font_default, text_color=self._url_color_default)