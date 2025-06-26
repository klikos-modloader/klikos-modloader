from typing import Optional, Callable, Literal, NamedTuple
import webbrowser

from .localized import LocalizedCTkLabel
from .utils import FontStorage, WinAccentTracker

from customtkinter import CTkFont, CTkImage  # type: ignore
from PIL import Image  # type: ignore
import winaccent  # type: ignore


class Label(LocalizedCTkLabel):
    autowrap: bool
    _update_debounce: int = 100
    _update_id = None

    _gif: Optional["GifObject"]

    _url: Optional[str]
    _url_color_default: tuple[str, str]
    _url_color_hovered: tuple[str, str]
    _url_color_pressed: tuple[str, str]
    _url_font_default: CTkFont
    _url_font_hovered: CTkFont
    _url_font_pressed: CTkFont
    _url_hovered: bool = False
    _url_pressed: bool = False


    def __init__(self, master, key: Optional[str] = None, modification: Optional[Callable[[str], str]] = None, weight: Literal['normal', 'bold'] | None = None, slant: Literal['italic', 'roman'] = "roman", underline: bool = False, overstrike: bool = False, style: Optional[Literal["caption", "body", "body_strong", "subtitle", "title", "title_large", "display"]] = None, autowrap: bool = False, url: Optional[str] = None, gif: Optional["GifObject"] = None, **kwargs):
        if style is not None: kwargs["font"] = self._get_font_from_style(style, underline=underline, overstrike=overstrike)
        elif "font" not in kwargs: kwargs["font"] = FontStorage.get(14, weight=weight, slant=slant, underline=underline, overstrike=overstrike)
        if "text_color" not in kwargs: kwargs["text_color"] = ("#1A1A1A", "#FFFFFF")
        if "justify" not in kwargs and "anchor" not in kwargs:
            kwargs["justify"] = "left"
            kwargs["anchor"] = "w"
        if gif is None: gif = kwargs.pop("gif", None)
        self._gif = gif
        if self._gif is not None:
            kwargs.pop("image", None)

        kwargs.pop("gif", None)
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

        if self._gif is not None:
            gif_player = GifPlayer(self, self._gif)
            self.after(200, gif_player.start())


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


# region GifPlayer
class GifObject(NamedTuple):
    size: tuple[int, int]
    gif: Image.Image


class FrameDisposal:
    UNSPECIFIED: Literal[0] = 0
    DO_NOT_DISPOSE: Literal[1] = 1
    RESTORE_TO_BACKGROUND: Literal[2] = 2
    RESTORE_TO_PREVIOUS: Literal[3] = 3
    DEFAULT = DO_NOT_DISPOSE


class GifPlayer:
    label: Label
    gif: Image.Image
    loop: int
    size: tuple[int, int]
    background_color: tuple[int, int, int, int]
    _remaining: int

    _previous: Image.Image | None
    _last_saved: Image.Image | None

    _LOOP_FALLBACK: int = 0
    _DURATION_FALLBACK: int = 100

    def __init__(self, label: Label, gif: GifObject) -> None:
        self.label = label
        self.gif = gif.gif
        self.size = gif.size
        self.loop = self.gif.info.get("loop", self._LOOP_FALLBACK)
        if not isinstance(self.loop, int): self.loop = self._LOOP_FALLBACK
        background_index = self.gif.info.get("background", None)
        palette = self.gif.getpalette()
        if background_index is not None and palette:
            r = palette[background_index * 3]
            g = palette[background_index * 3 + 1]
            b = palette[background_index * 3 + 2]
            self.background_color = (r, g, b, 255)
        else:
            self.background_color = (0, 0, 0, 0)


    def start(self) -> None:
        self._previous = None
        self._last_saved = None
        self._remaining = self.loop
        self.next(0)


    def next(self, index: int) -> None:
        try:
            self.gif.seek(index)
        except EOFError:
            if self._remaining == 1:
                return
            elif self._remaining > 1:
                self._remaining -= 1
            self.label.after(0, self.start)
            return

        duration = self.gif.info.get("duration", self._DURATION_FALLBACK)
        if not isinstance(duration, int): duration = self._DURATION_FALLBACK
        disposal = self.get_frame_disposal()

        new_frame: Image.Image = self.gif.copy()
        mask: Image.Image = new_frame.convert("RGBA").split()[3]
        x: int = self.gif.info.get("x", 0)
        y: int = self.gif.info.get("y", 0)

        match disposal:
            case FrameDisposal.DO_NOT_DISPOSE:
                if self._previous is not None:
                    frame = self._previous.copy()
                else:
                    frame = Image.new("RGBA", self.size, (0, 0, 0, 0))
                frame.paste(new_frame, (x, y), mask)
                self._last_saved = frame.copy()

            case FrameDisposal.RESTORE_TO_BACKGROUND:
                if self._previous is not None:
                    frame = self._previous.copy()
                else:
                    frame = Image.new("RGBA", self.size, (0, 0, 0, 0))
                background: Image.Image = Image.new("RGBA", (new_frame.width, new_frame.height), self.background_color)
                frame.paste(background, (x, y))
                frame.paste(new_frame, (x, y), mask)

            case FrameDisposal.RESTORE_TO_PREVIOUS:
                if self._last_saved is not None:
                    frame = self._last_saved.copy()
                else:
                    frame = Image.new("RGBA", self.size, (0, 0, 0, 0))
                frame.paste(new_frame, (x, y), mask)

        self.label.configure(image=CTkImage(frame, size=self.size))
        self.label.after(duration, self.next, index+1)


    def get_frame_disposal(self) -> Literal[1, 2, 3]:
        disposal = getattr(self.gif, "disposal_method", None)
        if disposal is None:
            disposal = self.gif.info.get("disposal", FrameDisposal.UNSPECIFIED)
        if disposal not in {FrameDisposal.UNSPECIFIED, FrameDisposal.DO_NOT_DISPOSE, FrameDisposal.RESTORE_TO_BACKGROUND, FrameDisposal.RESTORE_TO_PREVIOUS}:
            disposal = FrameDisposal.UNSPECIFIED
        if disposal == FrameDisposal.UNSPECIFIED:
            disposal = FrameDisposal.DEFAULT
        return disposal
# endregion