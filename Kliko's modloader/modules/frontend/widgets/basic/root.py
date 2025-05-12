from typing import Literal, Optional, Callable
from pathlib import Path

from .root_extensions import Banner, BannerSystem

from customtkinter import CTk, ScalingTracker, set_appearance_mode  # type: ignore
from tkinterdnd2 import TkinterDnD  # type: ignore


class Root(CTk, TkinterDnD.DnDWrapper):
    BannerSystem: Optional["BannerSystem"] = None

    def __init__(self, title: str, icon: str | Path | None = None, appearance_mode: Literal["light", "dark", "system"] = "system", width: Optional[int] = None, height: Optional[int] = None, centered: bool = True, banner_system: bool = False, default_fg_color: bool = False):
        set_appearance_mode(appearance_mode)
        if default_fg_color: CTk.__init__(self)
        else: CTk.__init__(self, fg_color=("#F3F3F3", "#202020"))
        TkinterDnD.DnDWrapper.__init__(self)
        self.TkdndVersion = TkinterDnD._require(self)
        if banner_system: self.BannerSystem = BannerSystem(self)

        self.title(title)
        if icon:
            if isinstance(icon, str): icon = Path(icon)
            if icon.exists() and icon.suffix == ".ico":
                self.iconbitmap(str(icon.resolve()))

        if width is not None and height is not None:
            if centered: self.geometry(f"{width}x{height}+{(self.winfo_screenwidth() - width)//2}+{(self.winfo_screenheight() - height)//2}")
            else: self.geometry(f"{width}x{height}")

        self.bind("<ButtonPress-1>", lambda event: event.widget.focus_set())
        # ScalingTracker.add_window(self._on_scaling_change, self)


    def send_banner(self, title_key: Optional[str] = None, title_modification: Optional[Callable[[str], str]] = None, message_key: Optional[str] = None, message_modification: Optional[Callable[[str], str]] = None, mode: Literal["success", "warning", "error", "attention", "info", "neutral"] = "neutral", icon_visible: bool = True, can_close: bool = True, auto_close_after_ms: int = 0) -> str:
        if self.BannerSystem is None: raise RuntimeError("Root: BannerSystem was not initialized!")
        return self.BannerSystem.send_banner(title_key=title_key, title_modification=title_modification, message_key=message_key, message_modification=message_modification, mode=mode, icon_visible=icon_visible, can_close=can_close, auto_close_after_ms=auto_close_after_ms)


    def close_banner(self, banner_or_id: str | Banner) -> None:
        if self.BannerSystem is None: raise RuntimeError("Root: BannerSystem was not initialized!")
        return self.BannerSystem.close_banner(banner_or_id=banner_or_id)


    # def _on_scaling_change(self, widget_scaling: float, window_scaling: float) -> None:
    #     self.update_idletasks()
    #     width: int = int(self.winfo_width() / window_scaling)
    #     height: int = int(self.winfo_height() / window_scaling)
    #     self.geometry(f"{width}x{height}")