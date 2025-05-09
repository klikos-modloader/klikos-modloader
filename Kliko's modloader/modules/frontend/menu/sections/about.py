from tkinter import TclError
from typing import TYPE_CHECKING

from modules.project_data import ProjectData
from modules.frontend.widgets import ScrollableFrame, Frame, Label, Button
from modules.frontend.functions import get_ctk_image
from modules.localization import Localizer
from modules.filesystem import Resources

if TYPE_CHECKING: from modules.frontend.widgets import Root

from customtkinter import CTkImage  # type: ignore


class AboutSection(ScrollableFrame):
    loaded: bool = False
    root: "Root"

    _SECTION_PADX: int | tuple[int, int] = (8, 4)
    _SECTION_PADY: int | tuple[int, int] = 8

    _ENTRY_GAP: int = 8
    _ENTRY_PADDING: tuple[int, int] = (16, 16)
    _ENTRY_INNER_GAP: int = 8


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

        Label(header, "menu.about.header.title", style="title", autowrap=True).grid(column=0, row=0, sticky="ew")
        Label(header, "menu.about.header.description", lambda string: Localizer.format(string, {"{app.name}": ProjectData.NAME}), style="caption", autowrap=True).grid(column=0, row=1, sticky="ew")


    def _load_content(self, master) -> None:
        wrapper: Frame = Frame(master, transparent=True)
        wrapper.grid_columnconfigure(0, weight=1)
        wrapper.grid_rowconfigure(1, weight=1)
        wrapper.grid(column=0, row=1, sticky="nsew")
        row_counter: int = -1

        # Banner
        row_counter += 1
        banner_frame: Frame = Frame(wrapper, transparent=True)
        banner_frame.grid(column=0, row=row_counter, sticky="ns", pady=0 if row_counter == 0 else (self._ENTRY_GAP, 0))

        banner_image: CTkImage = get_ctk_image(Resources.BANNER, size=(500, "auto"))
        Label(banner_frame, image=banner_image).grid(column=0, row=0, sticky="s")

        button_wrapper: Frame = Frame(banner_frame, transparent=True)
        button_wrapper.grid(column=0, row=1, sticky="n")

        folder_image: CTkImage = get_ctk_image(Resources.Common.Light.FOLDER, Resources.Common.Dark.FOLDER, size=24)
        Button(button_wrapper, "menu.mods.header.button.open_mods_folder", secondary=True, image=folder_image).grid(column=0, row=0)
        folder_image = get_ctk_image(Resources.Common.Light.FOLDER, Resources.Common.Dark.FOLDER, size=24)
        Button(button_wrapper, "menu.mods.header.button.open_mods_folder", secondary=True, image=folder_image).grid(column=1, row=0, padx=(8, 0))
        folder_image = get_ctk_image(Resources.Common.Light.FOLDER, Resources.Common.Dark.FOLDER, size=24)
        Button(button_wrapper, "menu.mods.header.button.open_mods_folder", secondary=True, image=folder_image).grid(column=2, row=0, padx=(8, 0))
# endregion