from pathlib import Path
from tkinter import StringVar

from modules.info import NAME
from modules.localization import Localizer
from modules.frontend.widgets.fluent import FluentToplevel, FluentLabel, FluentProgressBar

import customtkinter as ctk  # type: ignore


class ModDownloadWindow(FluentToplevel):
    root: ctk.CTk
    progress_bar: ctk.CTkProgressBar

    _width: int
    _height: int
    PADX: int = 32
    PADY: int = 24
    INNER_GAP: int = 12


    def __init__(self, root: ctk.CTk, icon: Path, mod: str) -> None:
        title: str = Localizer.strings["menu.marketplace"]["progress_window_title"].replace("{project_name}", NAME)
        super().__init__(root, title, icon, minimized=True)
        self.root = root

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=self.PADX, pady=self.PADY)

        label = FluentLabel(frame, font_size=16, font_weight="bold", text=Localizer.strings["menu.marketplace"]["progress_window_message"].replace("{mod}", mod))
        label.grid(column=0, row=0, sticky="w")
        self.update_idletasks()
        label_width: int = label.winfo_reqwidth()

        self.progress_bar = FluentProgressBar(frame, length=label_width, thickness=12)
        self.progress_bar.grid(column=0, row=1, sticky="w", pady=(self.INNER_GAP,0))
        self.update_idletasks()
        self._width = frame.winfo_reqwidth() + 2 * self.PADX
        self._height = frame.winfo_reqheight() + 2 * self.PADY

        self.resizable(False, False)
        self._set_geometry()
        self.deiconify()
        self.transient(self.root)


    def _set_geometry(self) -> None:
        w = self._width
        h = self._height
        x = self.root.winfo_x() + (self.root.winfo_width()-w)//2
        y = self.root.winfo_y() + (self.root.winfo_height()-h)//2
        self.geometry(f"{w}x{h}+{x}+{y}")