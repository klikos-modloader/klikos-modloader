from pathlib import Path
from typing import Optional, TYPE_CHECKING
from tkinter import TclError

from modules.project_data import ProjectData
from modules.localization import Localizer
from modules.filesystem import Resources
from modules.frontend.widgets import Toplevel, Frame, Label, Button, ProgressBar
from modules.frontend.widgets.basic.utils import FontStorage, WinAccentTracker
if TYPE_CHECKING: from modules.frontend.widgets import Root
from modules.frontend.functions import get_ctk_image, crop_to_fit

from ..dataclasses import CommunityMod

from PIL import Image  # type: ignore
from customtkinter import CTkImage, CTkTextbox, ScalingTracker  # type: ignore
import winaccent  # type; ignore


class CommunityModWindow(Toplevel):
    root: "Root"
    mod: CommunityMod
    THUMBNAIL_SIZE: tuple[int, int] = (480, 270)
    INFO_PANEL_WIDTH: int = 300
    INFO_PANEL_HEIGHT: int = THUMBNAIL_SIZE[1]
    PADDING: tuple[int, int] = (16, 16)
    INNER_GAP: int = 16
    DOWNLOAD_BUTTON_ICON_SIZE: int = 32
    DOWNLOAD_BUTTON_HEIGHT: int = 48
    PROGRESS_BAR_HEIGHT: int = 8

    _progress_bar: ProgressBar
    _downloading: bool = False


    def __init__(self, master: "Root", mod: CommunityMod):
        window_title: str = Localizer.format(Localizer.Strings["menu.marketplace.mod_window.window_title"], {"{app.name}": ProjectData.NAME})
        super().__init__(window_title, icon=Resources.FAVICON, centered=False, hidden=True)
        self.root = master
        self.mod = mod

        content: Frame = Frame(self, transparent=True, width=(self.THUMBNAIL_SIZE[0] + self.INNER_GAP + self.INFO_PANEL_WIDTH), height=self.INFO_PANEL_HEIGHT)
        content.grid_rowconfigure(2, weight=1)
        content.grid(column=0, row=0, sticky="new", padx=self.PADDING[0], pady=self.PADDING[1])

        thumbnail: Image.Image | tuple[Image.Image, Image.Image] = mod.get_thumbnail()
        if isinstance(thumbnail, tuple): image: CTkImage = get_ctk_image(crop_to_fit(thumbnail[0], mod.THUMBNAIL_ASPECT_RATIO), crop_to_fit(thumbnail[1], mod.THUMBNAIL_ASPECT_RATIO), size=self.THUMBNAIL_SIZE)
        else: image = get_ctk_image(crop_to_fit(thumbnail, mod.THUMBNAIL_ASPECT_RATIO), size=self.THUMBNAIL_SIZE)
        Label(content, image=image, width=self.THUMBNAIL_SIZE[0], height=self.THUMBNAIL_SIZE[1]).grid(column=0, row=0, sticky="new", rowspan=4)


        # Name & author
        name_label: Label = Label(content, mod.name, style="title", autowrap=False, wraplength=self.INFO_PANEL_WIDTH, width=self.INFO_PANEL_WIDTH)
        name_label.grid(column=1, row=0, padx=(self.INNER_GAP, 0), sticky="ns")
        if mod.author:
            author_label: Label = Label(content, "menu.marketplace.mod_window.mod_author", lambda string: Localizer.format(string, {"{mod.author}": mod.author}), style="body", autowrap=False, wraplength=self.INFO_PANEL_WIDTH, width=self.INFO_PANEL_WIDTH)  # type: ignore
            author_label.grid(column=1, row=1, padx=(self.INNER_GAP, 0), sticky="ns")
        else: 
            author_label = Label(content, "menu.marketplace.mod_window.mod_author_unknown", style="body", autowrap=False, wraplength=self.INFO_PANEL_WIDTH, width=self.INFO_PANEL_WIDTH)
            author_label.grid(column=1, row=1, padx=(self.INNER_GAP, 0), sticky="ns")


        # Description
        name_label.update_idletasks()
        author_label.update_idletasks()
        description_frame_height: int = self.THUMBNAIL_SIZE[1] - (self.INNER_GAP*2 + self.DOWNLOAD_BUTTON_HEIGHT + self.PROGRESS_BAR_HEIGHT + name_label.winfo_height() + author_label.winfo_height())
        description_frame: Frame = Frame(content, transparent=True, width=self.INFO_PANEL_WIDTH, height=description_frame_height)
        description_frame.grid_rowconfigure(0, weight=1)
        description_frame.grid(column=1, row=2, padx=(self.INNER_GAP-8, 0), sticky="ns")
        if mod.description:
            description_frame.grid_rowconfigure(0, weight=1)
            description_box: CTkTextbox = CTkTextbox(description_frame, text_color=("#1A1A1A", "#FFFFFF"), font=FontStorage.get(12), cursor="", width=self.INFO_PANEL_WIDTH, height=description_frame_height, corner_radius=0, fg_color="transparent", border_width=0, wrap="word")  # type: ignore
            description_box.grid(column=0, row=0, sticky="ns")
            description_box.insert("0.0", mod.description)
            description_box.configure(state="disabled")

            WinAccentTracker.add_callback(lambda: self._on_accent_change(description_box))
            self._on_accent_change(description_box)


        # Progress bar & download button
        progress_download_frame: Frame = Frame(content, width=self.INFO_PANEL_WIDTH, height=self.PROGRESS_BAR_HEIGHT + self.INNER_GAP + self.DOWNLOAD_BUTTON_HEIGHT)
        progress_download_frame.grid(column=1, row=3, padx=(self.INNER_GAP, 0), sticky="s")

        self.progress_bar = ProgressBar(progress_download_frame, width=self.INFO_PANEL_HEIGHT, height=self.PROGRESS_BAR_HEIGHT, mode="determinate")

        download_image: CTkImage = get_ctk_image(Resources.Common.Light.DOWNLOAD, Resources.Common.Dark.DOWNLOAD, size=self.DOWNLOAD_BUTTON_ICON_SIZE)
        Button(progress_download_frame, image=download_image, width=self.INFO_PANEL_WIDTH, height=self.DOWNLOAD_BUTTON_HEIGHT, command=self.download).grid(column=0, row=1, pady=(self.INNER_GAP, 0))


        # Show window
        self.center_window()
        self.deiconify()
        self.focus()
        self.lift(aboveThis=self.root)
        self.after_idle(self.lift, self.root)
        self.after_idle(self.focus)
        self.after(200, self.lift, self.root)
        self.after(200, self.focus)
        ScalingTracker.add_window(self._on_scaling_change, self)


    def center_window(self) -> None:
        self.update_idletasks()
        width: int = int(self.winfo_reqwidth() / ScalingTracker.get_window_scaling(self))
        height: int = int(self.winfo_reqheight() / ScalingTracker.get_window_scaling(self))
        self.geometry(f"{width}x{height}+{(self.winfo_screenwidth() - width)//2}+{(self.winfo_screenheight() - height)//2}")


    def _on_scaling_change(self, widget_scaling: float, window_scaling: float) -> None:
        self.update_idletasks()
        width: int = int(self.winfo_reqwidth() / window_scaling)
        height: int = int(self.winfo_reqheight() / window_scaling)
        self.geometry(f"{width}x{height}")


    def _on_accent_change(self, description_box: CTkTextbox) -> None:
        try: description_box._textbox.configure(selectbackground=winaccent.accent_normal)
        except TclError: pass



# region functions
    def show_progress_bar(self) -> None:
        try: self.progress_bar.grid(column=0, row=0)
        except TclError: pass


    def hide_progress_bar(self) -> None:
        try: self.progress_bar.grid_forget()
        except TclError: pass


    def download(self) -> None:
        if self._downloading: return
        self._downloading = True
        self.progress_bar.set(0)
        self.show_progress_bar()

        self.hide_progress_bar()
        self._downloading = False
# endregion