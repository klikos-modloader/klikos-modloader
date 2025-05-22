from tkinter import TclError, StringVar
from typing import Literal, Optional, TYPE_CHECKING

from modules.project_data import ProjectData
from ..windows import ModGeneratorPreviewWindow
from modules.frontend.widgets import ScrollableFrame, Frame, Label, Button, DropDownMenu, Entry, CheckBox
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
    mode_variable: StringVar
    _language_change_callback_id: str | None = None

    color_frame: Frame
    gradient_frame: Frame
    custom_frame: Frame
    settings_frame: Frame

    mode: Literal["color", "gradient", "custom"] = "color"
    color_data: tuple[int, int, int] = (255, 255, 255)
    gradient_data: list[tuple[float, tuple[int, int, int]]] = [(0, (255, 255, 255)), (1, (0, 0, 0))]
    gradient_angle: float = 0
    image_data: Image.Image = Image.new(mode="RGBA", size=(64, 64), color="#FFF")

    use_remote_config: bool = True
    create_1x_only: bool = False
    file_version: Optional[int] = None

    generating: bool = False

    _SECTION_PADX: int | tuple[int, int] = (8, 4)
    _SECTION_PADY: int | tuple[int, int] = 8
    _SECTION_GAP: int = 8
    _SETTING_BOX_PADDING: tuple[int, int] = (8, 12)
    _SETTING_GAP: int = 8
    _SETTING_INNER_GAP: int = 8


    def __init__(self, master):
        super().__init__(master, transparent=False, round=True, border=True, layer=1)
        self.root = master
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


    def destroy(self):
        if self._language_change_callback_id is not None:
            Localizer.remove_callback(self._language_change_callback_id)
            self._language_change_callback_id = None
        return super().destroy()


    def clear(self) -> None:
        if self._language_change_callback_id is not None:
            Localizer.remove_callback(self._language_change_callback_id)
            self._language_change_callback_id = None
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

        if self._language_change_callback_id is not None:
            Localizer.remove_callback(self._language_change_callback_id)
            self._language_change_callback_id = None
        self._language_change_callback_id = Localizer.add_callback(self._on_language_change)

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

        # Settings
        settings_frame: Frame = Frame(wrapper, transparent=False, layer=2)
        settings_frame.grid_columnconfigure(0, weight=1)
        settings_frame.grid(column=1, row=0, rowspan=2, sticky="ns", padx=(self._SECTION_GAP, 0))

        settings_wrapper: Frame = Frame(settings_frame, transparent=True)
        settings_wrapper.grid_columnconfigure(0, weight=1)
        settings_wrapper.grid(column=0, row=0, sticky="nsew", padx=self._SETTING_BOX_PADDING[0], pady=self._SETTING_BOX_PADDING[1])
        Label(settings_wrapper, "menu.mod_generator.content.settings.title", style="subtitle", autowrap=False).grid(column=0, row=0, sticky="w")
        setting_counter: int = 0

        setting_counter += 1
        setting: Frame = Frame(settings_wrapper, transparent=True)
        setting.grid_columnconfigure(1, weight=1)
        setting.grid(column=0, row=setting_counter, pady=0 if setting_counter == 0 else (self._SETTING_GAP, 0))
        Label(setting, "menu.mod_generator.content.settings.mode", autowrap=False).grid(column=0, row=0, sticky="w")
        mode_options: list[str] = ["menu.mod_generator.content.settings.mode.color", "menu.mod_generator.content.settings.mode.gradient", "menu.mod_generator.content.settings.mode.custom"]
        mode: str = Localizer.Strings[f"menu.mod_generator.content.settings.mode.{self.mode}"]
        self.mode_variable: StringVar = StringVar(setting, value=mode)
        DropDownMenu(setting, mode_options, variable=self.mode_variable, command=self.set_generator_mode).grid(column=1, row=0, padx=(self._SETTING_INNER_GAP, 0), sticky="ew")

        setting_counter += 1
        setting = Frame(settings_wrapper, transparent=True)
        setting.grid_columnconfigure(1, weight=1)
        setting.grid(column=0, row=setting_counter, pady=0 if setting_counter == 0 else (self._SETTING_GAP, 0))
        Label(setting, "menu.mod_generator.content.settings.1x_only", autowrap=False).grid(column=0, row=0, sticky="w")

        setting_counter += 1
        setting = Frame(settings_wrapper, transparent=True)
        setting.grid_columnconfigure(1, weight=1)
        setting.grid(column=0, row=setting_counter, pady=0 if setting_counter == 0 else (self._SETTING_GAP, 0))
        Label(setting, "menu.mod_generator.content.settings.use_remote_config", autowrap=False).grid(column=0, row=0, sticky="w")

        setting_counter += 1
        setting = Frame(settings_wrapper, transparent=True)
        setting.grid_columnconfigure(1, weight=1)
        setting.grid(column=0, row=setting_counter, pady=0 if setting_counter == 0 else (self._SETTING_GAP, 0))
        Label(setting, "menu.mod_generator.content.settings.version_specific", autowrap=False).grid(column=0, row=0, sticky="w")
# endregion


# region functions
    def _on_language_change(self) -> None:
        if not self.loaded:
            self.after(100, self._on_language_change)
            return

        mode_option_keys: list[str] = ["menu.mod_generator.content.settings.mode.color", "menu.mod_generator.content.settings.mode.gradient", "menu.mod_generator.content.settings.mode.custom"]
        mode: Literal["color", "gradient", "custom"] = self.mode
        mode_value: str = Localizer.Strings[mode_option_keys[0 if mode == "color" else 1 if mode == "gradient" else 2]]
        self.mode_variable.set(mode_value)


    def set_generator_mode(self, value: str) -> None:
        color_value: str = Localizer.Strings["menu.mod_generator.content.settings.mode.color"]
        gradient_value: str = Localizer.Strings["menu.mod_generator.content.settings.mode.gradient"]
        custom_value: str = Localizer.Strings["menu.mod_generator.content.settings.mode.custom"]

        if value not in {color_value, gradient_value, custom_value}:
            self.root.send_banner(
                title_key="menu.mod_generator.exception.title.unknown",
                message_key="menu.mod_generator.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": "ValueError", "{exception.message}": f'Bad value: "{value}". Expected one of "{color_value}", "{gradient_value}", "{custom_value}"'}),
                mode="error", auto_close_after_ms=6000
            )
            return
        normalized_value: Literal["color", "gradient", "custom"] = "color" if value == color_value else "gradient" if value == gradient_value else "custom"
        self.mode = normalized_value
# endregion




    # "menu.mod_generator.content.settings.title": "Settings",
    # "menu.mod_generator.content.settings.mode": "Mode:",
    # "menu.mod_generator.content.settings.mode.color": "Single Color",
    # "menu.mod_generator.content.settings.mode.gradient": "Gradient",
    # "menu.mod_generator.content.settings.mode.custom": "Custom",
    # "menu.mod_generator.content.settings.1x_only": "1x sizes only",
    # "menu.mod_generator.content.settings.use_remote_config": "Ignore icon blacklist",
    # "menu.mod_generator.content.settings.version_specific": "Version:",