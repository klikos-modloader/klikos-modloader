from typing import Optional
from pathlib import Path

from customtkinter import CTkToplevel  # type: ignore


class Toplevel(CTkToplevel):
    def __init__(self, title: str, icon: str | Path | None = None, width: Optional[int] = None, height: Optional[int] = None, centered: bool = True, hidden: bool = False, master = None):
        if master is None: super().__init__(fg_color=("#F3F3F3", "#202020"))
        else: super().__init__(master, fg_color=("#F3F3F3", "#202020"))
        if hidden: self.withdraw()

        self.title(title)
        if icon:
            if isinstance(icon, str): icon = Path(icon)
            if icon.exists() and icon.suffix == ".ico":
                icon_path: str = str(icon.resolve())
                self.iconbitmap(icon_path)
                self.after(200, self.iconbitmap, icon_path)

        if width is not None and height is not None:
            if centered: self.geometry(f"{width}x{height}+{(self.winfo_screenwidth() - width)//2}+{(self.winfo_screenheight() - height)//2}")
            else: self.geometry(f"{width}x{height}")

        self.bind("<ButtonPress-1>", lambda event: event.widget.focus_set())