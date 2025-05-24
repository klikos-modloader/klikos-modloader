from tkinter import TclError, StringVar, BooleanVar
from typing import Literal, Optional, TYPE_CHECKING
import re

from modules.project_data import ProjectData
from ..windows import ModGeneratorPreviewWindow
from modules.frontend.widgets import ScrollableFrame, Frame, Label, Button, DropDownMenu, Entry, CheckBox, ColorPicker, ask_color
from modules.frontend.functions import get_ctk_image
from modules.localization import Localizer
from modules.filesystem import Resources, Directories
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

    mode: Literal["color", "gradient", "custom"] = "color"
    color_data: tuple[int, int, int] = (255, 0, 0)
    gradient_data: list[tuple[float, tuple[int, int, int]]] = [(0, (255, 255, 255)), (1, (0, 0, 0))]
    gradient_angle: float = 0
    image_data: Image.Image = Image.new(mode="RGBA", size=(1, 1))

    mod_name: str = "My Custom Mod"
    use_remote_config: bool = True
    create_1x_only: bool = False
    file_version: Optional[int] = None

    generating: bool = False

    _SECTION_PADX: int | tuple[int, int] = (8, 4)
    _SECTION_PADY: int | tuple[int, int] = 8
    _SECTION_GAP: int = 8
    _SETTING_BOX_PADDING: tuple[int, int] = (12, 12)
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
        wrapper.grid(column=0, row=1, sticky="nsew")

        # region -  Settings
        settings_frame: Frame = Frame(wrapper, transparent=False, layer=2)
        settings_frame.grid_columnconfigure(0, weight=1)
        settings_frame.grid(column=1, row=0, rowspan=3, sticky="n", padx=(self._SECTION_GAP, 0))

        settings_wrapper: Frame = Frame(settings_frame, transparent=True)
        settings_wrapper.grid_columnconfigure(0, weight=1)
        settings_wrapper.grid(column=0, row=0, sticky="nsew", padx=self._SETTING_BOX_PADDING[0], pady=self._SETTING_BOX_PADDING[1])
        Label(settings_wrapper, "menu.mod_generator.content.settings.title", style="subtitle", autowrap=False).grid(column=0, row=0, sticky="w")
        setting_row_counter: int = 0

        setting_row_counter += 1
        setting = Frame(settings_wrapper, transparent=True)
        setting.grid_columnconfigure(1, weight=1)
        setting.grid(column=0, row=setting_row_counter, pady=0 if setting_row_counter == 0 else (self._SETTING_GAP, 0), sticky="ew")
        Label(setting, "menu.mod_generator.content.settings.mode", autowrap=False).grid(column=0, row=0, sticky="w")
        mode_options: list[str] = ["menu.mod_generator.content.settings.mode.color", "menu.mod_generator.content.settings.mode.gradient", "menu.mod_generator.content.settings.mode.custom"]
        mode: str = Localizer.Strings[f"menu.mod_generator.content.settings.mode.{self.mode}"]
        self.mode_variable: StringVar = StringVar(setting, value=mode)
        DropDownMenu(setting, mode_options, variable=self.mode_variable, command=self.set_generator_mode).grid(column=1, row=0, padx=(self._SETTING_INNER_GAP, 0), sticky="ew")

        setting_row_counter += 1
        setting = Frame(settings_wrapper, transparent=True)
        setting.grid_columnconfigure(1, weight=1)
        setting.grid(column=0, row=setting_row_counter, pady=0 if setting_row_counter == 0 else (self._SETTING_GAP, 0), sticky="ew")
        Label(setting, "menu.mod_generator.content.settings.1x_only", autowrap=False).grid(column=0, row=0, sticky="w")
        value = self.create_1x_only
        variable = BooleanVar(setting, value=value)
        CheckBox(setting, width=0, command=lambda variable=variable: self.set_1x_only(variable.get()), variable=variable).grid(column=1, row=0, padx=(self._SETTING_INNER_GAP, 0), sticky="e")

        setting_row_counter += 1
        setting = Frame(settings_wrapper, transparent=True)
        setting.grid_columnconfigure(1, weight=1)
        setting.grid(column=0, row=setting_row_counter, pady=0 if setting_row_counter == 0 else (self._SETTING_GAP, 0), sticky="ew")
        Label(setting, "menu.mod_generator.content.settings.use_remote_config", autowrap=False).grid(column=0, row=0, sticky="w")
        value = self.use_remote_config
        variable = BooleanVar(setting, value=value)
        CheckBox(setting, width=0, command=lambda variable=variable: self.set_remote_config(variable.get()), variable=variable).grid(column=1, row=0, padx=(self._SETTING_INNER_GAP, 0), sticky="e")

        setting_row_counter += 1
        setting = Frame(settings_wrapper, transparent=True)
        setting.grid_columnconfigure(1, weight=1)
        setting.grid(column=0, row=setting_row_counter, pady=0 if setting_row_counter == 0 else (self._SETTING_GAP, 0), sticky="ew")
        Label(setting, "menu.mod_generator.content.settings.version_specific", autowrap=False).grid(column=0, row=0, sticky="w")
        file_version: str = "" if self.file_version is None else str(self.file_version)
        file_version_variable: StringVar = StringVar(setting, value=file_version)
        Entry(
            setting, command=lambda event: self.set_file_version(event.value), on_focus_lost="command", run_command_if_empty=True, reset_if_empty=False, textvariable=file_version_variable,
            validate="key", validatecommand=(self.register(lambda value: value == "" or value.isdigit()), "%P")
        ).grid(column=1, row=0, padx=(self._SETTING_INNER_GAP, 0), sticky="ew")

        setting_row_counter += 1
        setting = Frame(settings_wrapper, transparent=True)
        setting.grid_columnconfigure(0, weight=1)
        setting.grid(column=0, row=setting_row_counter, pady=0 if setting_row_counter == 0 else (self._SETTING_GAP, 0), sticky="ew")
        eye_image: CTkImage = get_ctk_image(Resources.Common.Light.EYE, Resources.Common.Dark.EYE, 24)
        Button(setting, "menu.mod_generator.content.settings.preview", secondary=True, image=eye_image, command=self.show_preview).grid(column=0, row=0, sticky="ew")

        setting_row_counter += 1
        Label(settings_wrapper, "menu.mod_generator.content.settings.documentation_hyperlink", style="caption", autowrap=False, url=ProjectData.MOD_GENERATOR_DOCUMENTATION).grid(column=0, row=setting_row_counter, pady=0 if setting_row_counter == 0 else (self._SETTING_GAP, 0), sticky="w")
        # endregion

        # region -  General info
        mod_info_frame: Frame = Frame(wrapper, transparent=True)
        mod_info_frame.grid_columnconfigure(0, weight=1)
        mod_info_frame.grid(column=0, row=0, sticky="nsew")

        mod_name_frame = Frame(mod_info_frame, transparent=True)
        mod_name_frame.grid_columnconfigure(1, weight=1)
        mod_name_frame.grid(column=0, row=0, pady=0, sticky="ew")
        Label(mod_name_frame, "menu.mod_generator.content.settings.mod_name", style="body_strong", autowrap=False).grid(column=0, row=0, sticky="w")
        mod_name: str = self.mod_name
        mod_name_variable: StringVar = StringVar(mod_name_frame, value=mod_name)
        Entry(
            mod_name_frame, command=lambda event: self.set_mod_name(event.value), on_focus_lost="command", run_command_if_empty=False, reset_if_empty=True, textvariable=mod_name_variable,
            validate="key", validatecommand=(self.register(lambda value: not re.search(r'[\\/:*?"<>|]', value)), "%P")
        ).grid(column=1, row=0, padx=(self._SETTING_INNER_GAP, 0), sticky="ew")
        # endregion

        # region -  Color mode
        self.color_frame = Frame(wrapper, transparent=True)
        self.color_frame.grid_columnconfigure(0, weight=1)
        if self.mode == "color":
            self.color_frame.grid(column=0, row=1, sticky="nsew", pady=(12, 0))

        color_picker = ColorPicker(self.color_frame, on_update_callback=self.set_color_data)
        color_picker.set(value_rgb_normalized=self.color_data)
        color_picker.grid(column=0, row=0)
        # 
        # endregion

        # region -  Gradient mode
        self.gradient_frame = Frame(wrapper, transparent=True)
        if self.mode == "gradient":
            self.gradient_frame.grid(column=0, row=1, sticky="nsew", pady=(12, 0))
        # endregion

        # region -  Custom mode
        self.custom_frame = Frame(wrapper, transparent=True)
        if self.mode == "custom":
            self.custom_frame.grid(column=0, row=1, sticky="nsew", pady=(12, 0))
        # endregion

        # region -  Additional data
        general_data_frame: Frame = Frame(wrapper, transparent=True)
        general_data_frame.grid_columnconfigure(1, weight=1)
        general_data_frame.grid(column=0, row=2, sticky="nsew")

        # Custom Roblox icon
        custom_roblox_icon_frame = Frame(general_data_frame, transparent=True)
        custom_roblox_icon_frame.grid(column=0, row=0, sticky="nsew")

        # Additional files
        additional_files_frame = Frame(general_data_frame, transparent=True)
        additional_files_frame.grid(column=0, row=1, sticky="nsew")

        # Mod name

        # Start button
        # endregion
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

        if normalized_value == "color":
            self.gradient_frame.grid_forget()
            self.custom_frame.grid_forget()
            self.color_frame.grid(column=0, row=1, sticky="nsew", pady=(12, 0))

        elif normalized_value == "gradient":
            self.color_frame.grid_forget()
            self.custom_frame.grid_forget()
            self.gradient_frame.grid(column=0, row=1, sticky="nsew", pady=(12, 0))

        else:
            self.color_frame.grid_forget()
            self.gradient_frame.grid_forget()
            self.custom_frame.grid(column=0, row=1, sticky="nsew", pady=(12, 0))


    def set_file_version(self, value: str) -> None:
        if not value:
            self.file_version = None
            return

        value_int: int = int(value)
        self.file_version = value_int


    def set_remote_config(self, value: bool) -> None:
        self.use_remote_config = value


    def set_1x_only(self, value: bool) -> None:
        self.create_1x_only = value


    def set_mod_name(self, value: str) -> None:
        self.mod_name = value

    
    def set_color_data(self, value_hex: str) -> None:
        hex_without_prefix: str = value_hex.removeprefix("#")
        r, g, b = int(hex_without_prefix[0:2], 16), int(hex_without_prefix[2:4], 16), int(hex_without_prefix[4:6], 16)
        self.color_data = (r, g, b)


    def show_preview(self) -> None:
        mode: Literal['color', 'gradient', 'custom'] = self.mode
        angle: float = self.gradient_angle
        data: tuple[int, int, int] | list[tuple[float, tuple[int, int, int]]] | Image.Image = self.color_data if mode == "color" else self.gradient_data if mode == "gradient" else self.image_data
        image: Image.Image = ModGenerator.generate_preview_image(mode=mode, data=data, angle=angle)
        ModGeneratorPreviewWindow(self.root, image)


    def generate_mod(self) -> None:
        if self.generating:
            self.root.send_banner(
                title_key="menu.mods.exception.title.generate",
                message_key="menu.mod_generator.exception.message.generator_busy",
                mode="warning", auto_close_after_ms=6000
            )
            return

        self.generating = True
        mode: Literal['color', 'gradient', 'custom'] = self.mode
        angle: float = self.gradient_angle
        data: tuple[int, int, int] | list[tuple[float, tuple[int, int, int]]] | Image.Image = self.color_data if mode == "color" else self.gradient_data if mode == "gradient" else self.image_data
        mod_name: str = self.mod_name
        
        existing_mods = {path.stem.lower() if path.is_file() else path.name.lower() for path in Directories.MODS.iterdir()}
        if mod_name in existing_mods:
            self.root.send_banner(
                title_key="menu.mods.exception.title.generate",
                message_key="menu.mods.exception.message.mod_exists",
                mode="warning", auto_close_after_ms=6000
            )
            self.generating = False
            return
# endregion