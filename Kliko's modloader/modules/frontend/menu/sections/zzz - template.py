from tkinter import TclError
from typing import TYPE_CHECKING

from modules.frontend.widgets import ScrollableFrame, Frame, Label, Button
from modules.frontend.functions import get_ctk_image
from modules.localization import Localizer
from modules.filesystem import Resources

if TYPE_CHECKING: from modules.frontend.widgets import Root

from customtkinter import CTkImage  # type: ignore


class ModsSection(ScrollableFrame):
    loaded: bool = False
    root: "Root"

    _SECTION_PADX: int | tuple[int, int] = (8, 4)
    _SECTION_PADY: int | tuple[int, int] = 8


    def __init__(self, master):
        super().__init__(master, transparent=False, round=True, border=True, layer=1)
        self.root = master
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


    def clear(self) -> None:
        for widget in self.winfo_children():
            try: widget.destroy()
            except TclError: pass
        self.loaded = False


    def refresh(self) -> None:
        self.clear()
        self.show()


    def show(self) -> None:
        self.load()


# region load
    def load(self) -> None:
        if self.loaded: return

        content: Frame = Frame(self, transparent=True)
        content.grid_columnconfigure(0, weight=1)
        content.grid(column=0, row=0, sticky="nsew", padx=self._SECTION_PADX, pady=self._SECTION_PADY)

        self._load_header(content)
        self._load_content(content)

        self.loaded = True


    def _load_header(self, master) -> None:
        header: Frame = Frame(master, transparent=True)
        header.grid_columnconfigure(0, weight=1)
        header.grid(column=0, row=0, sticky="nsew", pady=(0,16))

        Label(header, "menu.mods.header.title", style="title", autowrap=True).grid(column=0, row=0, sticky="ew")
        Label(header, "menu.mods.header.description", style="caption", autowrap=True).grid(column=0, row=1, sticky="ew")

        button_wrapper: Frame = Frame(header, transparent=True)
        button_wrapper.grid(column=0, row=2, sticky="w", pady=(8, 0))

        folder_image: CTkImage = get_ctk_image(Resources.Common.Light.FOLDER, Resources.Common.Dark.FOLDER, size=24)
        Button(button_wrapper, "menu.mods.header.button.open_mods_folder", secondary=True, image=folder_image).grid(column=0, row=0)


    def _load_content(self, master) -> None:
        wrapper: Frame = Frame(master, transparent=True)
        wrapper.grid_columnconfigure(0, weight=1)
        wrapper.grid_rowconfigure(1, weight=1)
        wrapper.grid(column=0, row=1, sticky="nsew")
# endregion