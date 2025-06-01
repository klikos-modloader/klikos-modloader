from .utils import WinAccentTracker

from customtkinter import CTkProgressBar
import winaccent  # type: ignore


class ProgressBar(CTkProgressBar):
    progress_bar_fg_color: tuple[str, str]
    progress_bar_bg_color: tuple[str, str]


    def __init__(self, master, **kwargs) -> None:
        if "width" not in kwargs: kwargs["width"] = 132
        if "height" not in kwargs: kwargs["height"] = 4
        if "corner_radius" not in kwargs: kwargs["corner_radius"] = 999
        if "border_width" not in kwargs: kwargs["border_width"] = 0
        if "fg_color" not in kwargs: kwargs["fg_color"] = ("#868686", "#9A9A9A")
        super().__init__(master, **kwargs)
        self.progress_bar_bg_color = kwargs["fg_color"]

        WinAccentTracker.add_callback(lambda: self.after(0, self._on_accent_change))
        self._on_accent_change()
        self.set(0)


    def _on_accent_change(self) -> None:
        self.progress_bar_fg_color = (winaccent.accent_dark_1, winaccent.accent_light_2)
        self._update_colors()


    def _update_colors(self) -> None:
        self.configure(progress_color=self.progress_bar_fg_color, fg_color=self.progress_bar_bg_color)