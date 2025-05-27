from pathlib import Path
from typing import TYPE_CHECKING
from tkinter import TclError, messagebox
import shutil

from modules.project_data import ProjectData
from modules.localization import Localizer
from modules.logger import Logger
from modules.filesystem import Resources, DownloadStream, Directories
from modules.frontend.widgets import Toplevel, Frame, Label, Button, ProgressBar
from modules.frontend.widgets.basic.utils import FontStorage, WinAccentTracker
if TYPE_CHECKING: from modules.frontend.widgets import Root
from modules.frontend.functions import get_ctk_image, crop_to_fit
from modules.interfaces.fastflag_manager import FastFlagProfile

from PIL import Image  # type: ignore
from customtkinter import CTkImage, CTkTextbox, ScalingTracker  # type: ignore
import winaccent  # type; ignore


class FastFlagEditorWindow(Toplevel):
    root: "Root"
    profile: FastFlagProfile
    WINDOW_WIDTH: int = 256
    PADDING: tuple[int, int] = (16, 16)

    _LOG_PREFIX: str = "FastFlagEditor"


    def __init__(self, master: "Root", profile: FastFlagProfile):
        window_title: str = Localizer.format(Localizer.Strings["menu.fastflags.fastflag_editor.window_title"], {"{app.name}": ProjectData.NAME})
        super().__init__(window_title, icon=Resources.FAVICON, centered=False, hidden=True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(9, weight=1)
        self.resizable(False, False)
        self.root = master
        self.profile = profile

        content: Frame = Frame(self, transparent=True)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)
        content.grid(column=0, row=0, sticky="nsew", padx=self.PADDING[0], pady=self.PADDING[1])

        self.load_content(content)

        # Show window
        self.center_on_root()
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
        self_scaling: float = ScalingTracker.get_window_scaling(self)
        # width: int = int(self.winfo_reqwidth() / self_scaling)
        width: int = int(self.WINDOW_WIDTH / self_scaling)
        height: int = int(self.winfo_reqheight() / self_scaling)
        self.geometry(f"{width}x{height}+{(self.winfo_screenwidth() - width)//2}+{(self.winfo_screenheight() - height)//2}")


    def center_on_root(self) -> None:
        self.root.update_idletasks()
        self.update_idletasks()
        root_scaling: float = ScalingTracker.get_window_scaling(self.root)
        self_scaling: float = ScalingTracker.get_window_scaling(self)

        root_x: int = self.root.winfo_rootx()
        root_y: int = self.root.winfo_rooty()
        root_w: int = int(self.root.winfo_width() / root_scaling)
        root_h: int = int(self.root.winfo_height() / root_scaling)
        # width: int = int(self.winfo_reqwidth() / self_scaling)
        width: int = int(self.WINDOW_WIDTH / self_scaling)
        height: int = int(self.winfo_reqheight() / self_scaling)

        self.geometry(f"{width}x{height}+{root_x + int((root_w - width) / 2)}+{root_y + int((root_h - height) / 2)}")


    def _on_scaling_change(self, widget_scaling: float, window_scaling: float) -> None:
        self.update_idletasks()
        width: int = int(self.winfo_reqwidth() / window_scaling)
        height: int = int(self.winfo_reqheight() / window_scaling)
        self.geometry(f"{width}x{height}")


    def load_content(self, frame: Frame) -> None:
        # Header
        header: Frame = Frame(frame, transparent=True)
        header.grid(column=0, row=0, sticky="nsew")

        Label(header, self.profile.name, style="subtitle", autowrap=True, dont_localize=True).grid(column=0, row=0, sticky="ew")

        button_wrapper: Frame = Frame(header, transparent=True)
        button_wrapper.grid(column=0, row=1, sticky="w", pady=(8, 0))

        image: CTkImage = get_ctk_image(Resources.Common.Light.ADD, Resources.Common.Dark.ADD, size=24)
        Button(button_wrapper, "menu.fastflags.header.button.new_profile", secondary=True, image=image).grid(column=0, row=0)

        # Body
        body: Frame = Frame(frame, layer=1)
        body.grid(column=0, row=1, sticky="nsew", pady=(12, 0))
        return


# region functions
# endregion