from pathlib import Path

from modules.localization import Localizer
from modules.frontend.widgets.fluent import FluentLabel, FluentToolTipButton, get_root_instance

import customtkinter as ctk  # type: ignore
from PIL import Image  # type: ignore


class GlobalBasicSettingsSection:
    PADDING_X: int = 16
    PADDING_Y: int = 16

    resources: Path

    master: ctk.CTkFrame
    content: ctk.CTkFrame | ctk.CTkScrollableFrame
    tooltip_button: FluentToolTipButton

    active: bool = False
    first_load: bool = True


    def __init__(self, root: ctk.CTk, master: ctk.CTkFrame | ctk.CTkScrollableFrame, resources: Path) -> None:
        self.root = root
        self.master = master
        self.resources = resources


    def refresh(self) -> None:
        self._clear()
        self._load()


    def load(self) -> None:
        if self.active: return
        self.active = True
        self.tooltip_button.enable()


    def unload(self) -> None:
        self.active = False
        self.tooltip_button.disable()

    
    def _clear(self) -> None:
        for widget in self.master.winfo_children():
            widget.destroy()


    def _load(self) -> None:
        self.content = ctk.CTkFrame(self.master, fg_color="transparent")
        self.content.grid(column=0, row=0, sticky="nsew", padx=self.PADDING_X, pady=self.PADDING_Y)
        self.content.grid_columnconfigure(0, weight=1)
        self._get_title_frame().grid(column=0, row=0, sticky="nsew")
        self._get_content().grid(column=0, row=1, sticky="nsew", pady=(16,0))


    def _get_title_frame(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.content, fg_color="transparent")

        title_row = ctk.CTkFrame(frame, fg_color="transparent")
        title_row.grid(column=0, row=0, sticky="w")

        FluentLabel(title_row, Localizer.strings["menu.globalbasicsettings"]["title"], font_size=28, font_weight="bold").grid(column=0, row=0, sticky="w")
        self.tooltip_button = FluentToolTipButton(get_root_instance(), master=title_row, wraplength=400, tooltip_title=Localizer.strings["menu.globalbasicsettings"]["tooltip.title"], tooltip_message=Localizer.strings["menu.globalbasicsettings"]["tooltip.message"], tooltip_orientation="down", toplevel=True)
        self.tooltip_button.grid(column=1, row=0, padx=(8,0), sticky="w")

        return frame

    
    def _get_content(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.content, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)

        return frame


# region functions
# endregion