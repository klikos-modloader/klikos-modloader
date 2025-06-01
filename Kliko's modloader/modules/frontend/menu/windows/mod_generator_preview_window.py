from typing import Optional, TYPE_CHECKING

from modules.project_data import ProjectData
from modules.localization import Localizer
from modules.filesystem import Resources
from modules.frontend.widgets import Toplevel, Label
from modules.frontend.functions import get_ctk_image
if TYPE_CHECKING: from modules.frontend.widgets import Root

from PIL import Image  # type: ignore
from customtkinter import CTkImage, ScalingTracker  # type: ignore


class ModGeneratorPreviewWindow(Toplevel):
    root: "Root"
    image: Image.Image
    label: Label


    def __init__(self, master: "Root", image: Image.Image):
        window_title: str = Localizer.format(Localizer.Strings["menu.mod_generator.preview_window.window_title"], {"{app.name}": ProjectData.NAME})
        super().__init__(window_title, icon=Resources.FAVICON, centered=False, hidden=True)
        self.resizable(False, False)
        self.root = master
        self.image = image

        self.label = Label(self, autowrap=False, image=get_ctk_image(self.image, size=self.image.size), dont_localize=True, width=self.image.width, height=self.image.height)
        self.label.grid(column=0, row=0)


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
        width: int = int(self.winfo_reqwidth() / ScalingTracker.get_window_scaling(self))
        height: int = int(self.winfo_reqheight() / ScalingTracker.get_window_scaling(self))
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
        width: int = int(self.winfo_reqwidth() / self_scaling)
        height: int = int(self.winfo_reqheight() / self_scaling)

        self.geometry(f"{width}x{height}+{root_x + int((root_w - width) / 2)}+{root_y + int((root_h - height) / 2)}")


    def _on_scaling_change(self, widget_scaling: float, window_scaling: float) -> None:
        self.update_idletasks()
        width: int = int(self.winfo_reqwidth() / window_scaling)
        height: int = int(self.winfo_reqheight() / window_scaling)
        self.geometry(f"{width}x{height}")