from tkinter import TclError
from typing import Literal, TYPE_CHECKING

from modules.project_data import ProjectData
from ..windows import ModGeneratorPreviewWindow
from modules.frontend.widgets import ScrollableFrame, Frame, Label, Button
from modules.frontend.functions import get_ctk_image
from modules.localization import Localizer
from modules.filesystem import Resources
from modules.mod_generator import ModGenerator

if TYPE_CHECKING: from modules.frontend.widgets import Root

from customtkinter import CTkImage  # type: ignore
from PIL import Image  # type: ignore


class ModGeneratorSection(ScrollableFrame):
    loaded: bool = False
    root: "Root"

    mode: Literal["color", "gradient", "custom"] = "color"
    color_data: tuple[int, int, int] = (255, 255, 255)
    gradient_data: list[tuple[float, tuple[int, int, int]]] = [(0, (255, 255, 255)), (1, (0, 0, 0))]
    gradient_angle: float = 0
    image_data: Image.Image = Image.new(mode="RGBA", size=(64, 64), color="#FFF")

    generating: bool = False

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

        # image: Image.Image = ModGenerator.generate_preview_image("color", (204, 0, 55))
        # ModGeneratorPreviewWindow(self.root, image)

        # image: Image.Image = ModGenerator.generate_preview_image("gradient", [(0, (153, 0, 0)), (1, (255, 0, 110))], angle=-45)
        # ModGeneratorPreviewWindow(self.root, image)

        # from tkinter import filedialog
        # path = filedialog.askopenfilename()
        # if path:
        #     image = ModGenerator.generate_preview_image("custom", Image.open(path))
        #     ModGeneratorPreviewWindow(self.root, image)

        # image = ModGenerator.generate_preview_image("custom", Image.open(Resources.Logo.CHRISTMAS))
        # ModGeneratorPreviewWindow(self.root, image)



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

        Label(header, "menu.mod_generator.header.title", style="title", autowrap=True).grid(column=0, row=0, sticky="ew")
        Label(header, "menu.mod_generator.header.description", style="caption", autowrap=True).grid(column=0, row=1, sticky="ew")


    def _load_content(self, master) -> None:
        wrapper: Frame = Frame(master, transparent=True)
        wrapper.grid_columnconfigure(0, weight=1)
        wrapper.grid_rowconfigure(1, weight=1)
        wrapper.grid(column=0, row=1, sticky="nsew")
# endregion