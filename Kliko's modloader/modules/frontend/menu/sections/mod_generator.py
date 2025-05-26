from tkinter import TclError, StringVar, BooleanVar, filedialog
from typing import Literal, Optional, TYPE_CHECKING
from pathlib import Path
from threading import Thread
import uuid
import json
import re
from random import randint

from modules.project_data import ProjectData
from ..windows import ModGeneratorPreviewWindow
from modules.frontend.widgets import ScrollableFrame, Frame, Label, Button, DropDownMenu, Entry, CheckBox, ColorPicker, ask_color
from modules.frontend.functions import get_ctk_image, crop_to_fit
from modules.localization import Localizer
from modules.filesystem import Resources, Directories
from modules.mod_generator import ModGenerator, AdditionalFile, GradientColor

if TYPE_CHECKING: from modules.frontend.widgets import Root

from customtkinter import CTkImage  # type: ignore
from PIL import Image  # type: ignore


class ModGeneratorSection(ScrollableFrame):
    loaded: bool = False
    root: "Root"
    mode_variable: StringVar
    _language_change_callback_id: str | None = None
    _gradient_list_frames: dict[str, Frame]
    _gradient_data_dict: dict[str, GradientColor]
    _additional_file_frames: dict[str, Frame]
    _custom_icon_preview_size: int = 218
    _custom_mask_preview_size: int = 260
    _addition_icon_preview_size: int = 24
    _gradient_preview_size: int = 148

    color_frame: Frame
    gradient_frame: Frame
    custom_frame: Frame
    additional_files_list: Frame
    gradient_colors_list: Frame
    custom_icon_preview_label: Label
    custom_mask_preview_label: Label
    gradient_preview_label: Label
    generate_button: Button

    mode: Literal["color", "gradient", "custom"] = "color"
    color_data: tuple[int, int, int] = (255, 0, 0)
    gradient_data: list[GradientColor]
    gradient_angle: float = 0
    image_data: Image.Image = Image.new(mode="RGBA", size=(1, 1))
    custom_roblox_icon: Optional[Image.Image] = None
    additional_files: dict[str, AdditionalFile]

    mod_name: str = "My Custom Mod"
    use_remote_config: bool = True
    create_1x_only: bool = False
    file_version: Optional[int] = None

    generating: bool = False

    _SECTION_PADX: int | tuple[int, int] = (8, 4)
    _SECTION_PADY: int | tuple[int, int] = 8
    _SECTION_GAP: int = 16
    _SECTION_BOX_PADDING: tuple[int, int] = (12, 12)
    _SETTING_GAP: int = 8
    _SETTING_INNER_GAP: int = 8
    _ENTRY_GAP: int = 8
    _ENTRY_INNER_GAP: int = 12
    _ENTRY_BOX_PADDING: tuple[int, int] = (6, 6)


    def __init__(self, master):
        self.mod_name = Localizer.Strings["menu.mod_generator.content.mod_name_default"]
        self._gradient_data_dict = {uuid.uuid4().hex: GradientColor(0, (255, 255, 255)), uuid.uuid4().hex: GradientColor(1, (0, 0, 0))}
        self.gradient_data = list(self._gradient_data_dict.values())
        self.additional_files = {}
        self._additional_file_frames = {}
        self._gradient_list_frames = {}
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

        left_panel: Frame = Frame(wrapper, transparent=True)
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid(column=0, row=0, sticky="nsew")

        right_panel: Frame = Frame(wrapper, transparent=True)
        right_panel.grid(column=1, row=0, sticky="nsew", padx=(self._SECTION_GAP, 0))

        # region -  Settings
        settings_frame: Frame = Frame(right_panel, transparent=False, layer=2)
        settings_frame.grid_columnconfigure(0, weight=1)
        settings_frame.grid(column=0, row=0, sticky="nsew")

        settings_wrapper: Frame = Frame(settings_frame, transparent=True)
        settings_wrapper.grid_columnconfigure(0, weight=1)
        settings_wrapper.grid(column=0, row=0, sticky="nsew", padx=self._SECTION_BOX_PADDING[0], pady=self._SECTION_BOX_PADDING[1])
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
        generate_icon: CTkImage = get_ctk_image(Resources.Common.Light.START, Resources.Common.Dark.START, 24)
        self.generate_button = Button(settings_wrapper, "menu.mod_generator.content.button.generate", secondary=True, image=generate_icon, command=lambda:Thread(target=self.generate_mod, daemon=True).start())
        self.generate_button.grid(column=0, row=setting_row_counter, pady=0 if setting_row_counter == 0 else (self._SETTING_GAP, 0), sticky="ew")

        setting_row_counter += 1
        Label(settings_wrapper, "menu.mod_generator.content.settings.documentation_hyperlink", style="caption", autowrap=False, url=ProjectData.MOD_GENERATOR_DOCUMENTATION).grid(column=0, row=setting_row_counter, pady=0 if setting_row_counter == 0 else (self._SETTING_GAP, 0), sticky="w")
        # endregion

        # Custom Roblox icon
        custom_roblox_icon_frame: Frame = Frame(right_panel, transparent=False, layer=2)
        custom_roblox_icon_frame.grid(column=0, row=1, sticky="nsew", pady=(self._SECTION_GAP, 0))

        custom_icon_wrapper = Frame(custom_roblox_icon_frame, transparent=True)
        custom_icon_wrapper.grid(column=0, row=0, sticky="nsew", padx=self._SECTION_BOX_PADDING[0], pady=self._SECTION_BOX_PADDING[1])

        Label(custom_icon_wrapper, "menu.mod_generator.content.custom_roblox_icon",
            lambda string: Localizer.format(string, {
                "{roblox.common}": Localizer.Key("roblox.common"),
                "{roblox.player}": Localizer.Key("roblox.player"), "{roblox.player_alt}": Localizer.Key("roblox.player_alt"),
                "{roblox.studio}": Localizer.Key("roblox.studio"), "{roblox.studio_alt}": Localizer.Key("roblox.studio_alt")
            }), style="subtitle", autowrap=False, wraplength=200
        ).grid(column=0, row=0, sticky="ew")

        Label(custom_icon_wrapper, "menu.mod_generator.content.custom_roblox_icon.description",
            lambda string: Localizer.format(string, {
                "{roblox.common}": Localizer.Key("roblox.common"),
                "{roblox.player}": Localizer.Key("roblox.player"), "{roblox.player_alt}": Localizer.Key("roblox.player_alt"),
                "{roblox.studio}": Localizer.Key("roblox.studio"), "{roblox.studio_alt}": Localizer.Key("roblox.studio_alt")
            }), style="caption", autowrap=False, wraplength=200
        ).grid(column=0, row=1, sticky="ew")

        button_row = Frame(custom_icon_wrapper, transparent=True)
        button_row.grid(column=0, row=2, sticky="ew", pady=(12, 0))

        bin_image = get_ctk_image(Resources.Common.Light.BIN, Resources.Common.Dark.BIN, 24)
        Button(button_row, "menu.mod_generator.content.button.remove", secondary=True, image=bin_image, command=self._remove_custom_roblox_icon).grid(column=0, row=0)

        bin_image = get_ctk_image(Resources.Common.Light.ADD, Resources.Common.Dark.ADD, 24)
        Button(button_row, "menu.mod_generator.content.button.add", secondary=True, image=bin_image, command=self._choose_custom_roblox_icon).grid(column=1, row=0, padx=(8, 0))

        self.custom_icon_preview_label = Label(custom_icon_wrapper, width=self._custom_icon_preview_size, height=self._custom_icon_preview_size)




        # # region -  General info
        general_info_frame: Frame = Frame(left_panel, transparent=False, layer=2)
        general_info_frame.grid_columnconfigure(0, weight=1)
        general_info_frame.grid(column=0, row=0, sticky="nsew")
    
        general_info_wrapper = Frame(general_info_frame, transparent=True)
        general_info_wrapper.grid_columnconfigure(0, weight=1)
        general_info_wrapper.grid(column=0, row=0, sticky="nsew", padx=self._SECTION_BOX_PADDING[0], pady=self._SECTION_BOX_PADDING[1])

        mod_name_frame = Frame(general_info_wrapper, transparent=True)
        mod_name_frame.grid_columnconfigure(1, weight=1)
        mod_name_frame.grid(column=0, row=0, sticky="ew")
        Label(mod_name_frame, "menu.mod_generator.content.mod_name", style="body_strong", autowrap=False).grid(column=0, row=0, sticky="w")
        mod_name: str = self.mod_name
        mod_name_variable: StringVar = StringVar(mod_name_frame, value=mod_name)
        Entry(
            mod_name_frame, command=lambda event: self.set_mod_name(event.value), on_focus_lost="command", run_command_if_empty=False, reset_if_empty=True, textvariable=mod_name_variable,
            validate="key", validatecommand=(self.register(lambda value: not re.search(r'[\\/:*?"<>|]', value)), "%P")
        ).grid(column=1, row=0, padx=(self._SETTING_INNER_GAP, 0), sticky="ew")
        # # endregion

        # region -  Color mode
        self.color_frame = Frame(general_info_wrapper, transparent=True)
        self.color_frame.grid_columnconfigure(0, weight=1)
        if self.mode == "color":
            self.color_frame.grid(column=0, row=1, sticky="nsew", pady=(self._SECTION_GAP, 0))

        color_picker = ColorPicker(self.color_frame, advanced=False, on_update_callback=self.set_color_data)
        color_picker.set(value_rgb_normalized=self.color_data)
        color_picker.grid(column=0, row=0, sticky="w")
        # endregion

        # region -  Gradient mode
        self.gradient_frame = Frame(general_info_wrapper, transparent=False, layer=2)
        self.gradient_frame.grid_columnconfigure(0, weight=1)
        if self.mode == "gradient":
            self.gradient_frame.grid(column=0, row=1, sticky="nsew", pady=(self._SECTION_GAP, 0))

        button_angle_wrapper = Frame(self.gradient_frame)
        button_angle_wrapper.grid(column=0, row=0, sticky="w")

        add_image: CTkImage = get_ctk_image(Resources.Common.Light.ADD, Resources.Common.Dark.ADD, 24)
        Button(button_angle_wrapper, "menu.mod_generator.content.button.add", secondary=True, image=add_image, command=self._add_gradient_color).grid(column=0, row=0, sticky="w")
        Label(button_angle_wrapper, "menu.mod_generator.content.gradient_angle").grid(column=1, row=0, padx=(12, 0), sticky="w")
        angle_entry: Entry = Entry(
            button_angle_wrapper, command=self.set_gradient_angle,
            on_focus_lost="command", run_command_if_empty=False, reset_if_empty=True, height=32, width=64,
            validate="key", validatecommand=(self.register(lambda value: value.removeprefix("-") == "" or value.removeprefix("-").replace(".", "", 1).isdigit()), "%P")
        )
        angle_entry.set(str(self.gradient_angle))
        angle_entry.grid(column=2, row=0, padx=(8, 0), sticky="w")

        self.gradient_colors_list = Frame(self.gradient_frame, transparent=True)
        self.gradient_colors_list.grid_columnconfigure(0, weight=1)
        self.gradient_colors_list.grid(column=0, row=1, sticky="nsew", pady=(12, 0))

        self.gradient_preview_label = Label(self.gradient_frame)
        self.gradient_preview_label.grid(column=0, row=2, sticky="w", pady=(12, 0))

        self._update_gradient_list()
        # endregion

        # region -  Custom mode
        self.custom_frame = Frame(general_info_wrapper, transparent=False, layer=2)
        self.custom_frame.grid_columnconfigure(0, weight=1)
        if self.mode == "custom":
            self.custom_frame.grid(column=0, row=1, sticky="nsew", pady=(self._SECTION_GAP, 0))

        Button(self.custom_frame, "menu.mod_generator.content.button.add", secondary=True, image=add_image, command=self._choose_custom_mask).grid(column=0, row=0, sticky="w")
        self.custom_mask_preview_label = Label(self.custom_frame, width=self._custom_mask_preview_size, height=self._custom_mask_preview_size)
        # endregion

        # region -  Additional data
        additional_files_frame: Frame = Frame(left_panel, transparent=False, layer=2)
        additional_files_frame.grid_columnconfigure(0, weight=1)
        additional_files_frame.grid(column=0, row=2, sticky="nsew", pady=(self._SECTION_GAP, 0))

        # Additional files
        additional_files_wrapper = Frame(additional_files_frame, transparent=True)
        additional_files_wrapper.grid_columnconfigure(0, weight=1)
        additional_files_wrapper.grid(column=0, row=0, sticky="nsew", padx=self._SECTION_BOX_PADDING[0], pady=self._SECTION_BOX_PADDING[1])

        Label(additional_files_wrapper, "menu.mod_generator.content.additional_files",
            lambda string: Localizer.format(string, {
                "{roblox.common}": Localizer.Key("roblox.common"),
                "{roblox.player}": Localizer.Key("roblox.player"), "{roblox.player_alt}": Localizer.Key("roblox.player_alt"),
                "{roblox.studio}": Localizer.Key("roblox.studio"), "{roblox.studio_alt}": Localizer.Key("roblox.studio_alt")
            }), style="subtitle", autowrap=True
        ).grid(column=0, row=0, sticky="ew")

        button_row = Frame(additional_files_wrapper, transparent=True)
        button_row.grid(column=0, row=1, sticky="ew", pady=(8, 0))

        reset_image: CTkImage = get_ctk_image(Resources.Common.Light.RESET, Resources.Common.Dark.RESET, 24)
        Button(button_row, "menu.mod_generator.content.button.reset", secondary=True, image=reset_image, command=self._reset_additional_files).grid(column=0, row=0, sticky="w")

        bin_image = get_ctk_image(Resources.Common.Light.BIN, Resources.Common.Dark.BIN, 24)
        Button(button_row, "menu.mod_generator.content.button.remove_all", secondary=True, image=bin_image, command=self._remove_all_additional_files).grid(column=1, row=0, sticky="w", padx=(8, 0))

        dnd_frame: Frame = Frame(additional_files_wrapper, height=128, layer=3, dnd_command=self._add_additional_files, cursor="hand2")
        dnd_frame.grid_columnconfigure(0, weight=1)
        dnd_frame.grid_rowconfigure(0, minsize=128)
        dnd_frame.grid(column=0, row=2, sticky="nsew", pady=(8, 0))
        dnd_label: Label = Label(dnd_frame, "menu.mod_generator.content.dnd_target_frame", style="body_strong", justify="center")
        dnd_label.grid(column=0, row=0, sticky="ew")
        dnd_frame.bind("<ButtonPress-1>", self._manual_add_additional_files)
        dnd_label.bind("<ButtonPress-1>", self._manual_add_additional_files)

        self.additional_files_list = Frame(additional_files_wrapper, transparent=True)
        self.additional_files_list.grid_columnconfigure(0, weight=1)
        self._reset_additional_files()
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
            self.color_frame.grid(column=0, row=1, sticky="nsew", pady=(self._SECTION_GAP, 0))

        elif normalized_value == "gradient":
            self.color_frame.grid_forget()
            self.custom_frame.grid_forget()
            self.gradient_frame.grid(column=0, row=1, sticky="nsew", pady=(self._SECTION_GAP, 0))

        else:
            self.color_frame.grid_forget()
            self.gradient_frame.grid_forget()
            self.custom_frame.grid(column=0, row=1, sticky="nsew", pady=(self._SECTION_GAP, 0))


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
# endregion


# region gradient
    def _remove_gradient_color(self, id: str) -> None:
        if len(self.gradient_data) <= 2:
            self.root.send_banner(
                title_key="menu.mod_generator.exception.title.unknown",
                message_key="menu.mod_generator.exception.message.gradient_not_enough_colors",
                mode="warning", auto_close_after_ms=6000
            )
            return
        
        gradient_data: dict[str, GradientColor] = self._gradient_data_dict
        gradient_data.pop(id, None)
        self.gradient_data = sorted(list(gradient_data.values()), key=lambda item: item.stop)
        frame: Frame | None = self._gradient_list_frames.pop(id, None)
        if frame:
            frame.destroy()

        self._update_gradient_list()


    def _add_gradient_color(self) -> None:
        self._gradient_data_dict[uuid.uuid4().hex] = GradientColor(1, (randint(0, 255), randint(0, 255), randint(0, 255)))
        self._update_gradient_list()


    def _update_gradient_preview(self) -> None:
        mode: Literal["gradient"] = "gradient"
        data: list[GradientColor] = self.gradient_data
        preview_size: int = self._gradient_preview_size
        angle: float = self.gradient_angle
        image: CTkImage = get_ctk_image(ModGenerator.generate_preview_mask(mode, data, (preview_size, preview_size), angle), size=preview_size)
        self.gradient_preview_label.configure(image=image)


    def _update_gradient_list(self) -> None:
        self._gradient_list_frames
        self._gradient_data_dict

        gradient_data: dict[str, GradientColor] = dict(sorted(self._gradient_data_dict.items(), key=lambda item: item[1].stop))
        self.gradient_data = list(gradient_data.values())
        gradient_frame_ids: list[str] = list(gradient_data.keys())

        for id, frame in list(self._gradient_list_frames.items()):
            if id not in gradient_frame_ids:
                self._gradient_list_frames.pop(id)
                frame.destroy()

        for i, (id, gradient) in enumerate(gradient_data.items()):
            pady = 0 if i == 0 else (self._ENTRY_GAP, 0)

            frame = self._gradient_list_frames.get(id)  # type: ignore
            if frame is not None:
                if getattr(frame, "_row", None) != i:
                    frame.grid(column=0, row=i, sticky="nsew", pady=pady)
                    frame._row = i  # type: ignore

            else:
                frame = Frame(self.gradient_colors_list, layer=3)
                frame._row = i  # type: ignore
                frame.grid(column=0, row=i, sticky="nsew", pady=pady)
                self._gradient_list_frames[id] = frame
                self.after(10, self._load_gradient_frame, frame, id, gradient)

        self._update_gradient_preview()


    def _load_gradient_frame(self, frame: Frame, id: str, gradient: GradientColor) -> None:
        def pick_gradient_color(frame: Frame, gradient: GradientColor) -> None:
            current_r, current_g, current_b = gradient.color
            current_color_hex: str = f"#{current_r:02x}{current_g:02x}{current_b:02x}"
            color_hex: str = ask_color(self.root, Localizer.format(Localizer.Strings["dialog.color_picker.title"], {"{app.name}": ProjectData.NAME}), Resources.FAVICON, default_color=current_color_hex)
            color_rgb = (int(color_hex[1:3], 16), int(color_hex[3:5], 16), int(color_hex[5:7], 16))
            update_gradient_color(frame, gradient, color_rgb)

        def update_gradient_color(frame: Frame, gradient: GradientColor, color_rgb: tuple[int, int, int]) -> None:
            r, g, b = color_rgb
            hex_color: str = f"#{r:02x}{g:02x}{b:02x}"
            gradient.color = color_rgb
            frame.preview_frame.configure(fg_color=hex_color)  # type: ignore
            self._update_gradient_preview()

        def update_gradient_endpoint(gradient: GradientColor, event) -> None:
            value_string: str = event.value
            try:
                value_float: float = float(value_string)
            except ValueError:
                event.widget.set(str(gradient.stop))
                return
            
            if value_float < 0 or value_float > 1:
                event.widget.set(str(gradient.stop))
                return

            gradient.stop = value_float
            event.widget.set(str(gradient.stop))
            self._update_gradient_list()

        frame.grid_columnconfigure(0, weight=1)

        wrapper: Frame = Frame(frame, transparent=True)
        wrapper.grid_columnconfigure(4, weight=1)
        wrapper.grid(column=0, row=0, sticky="nsew", padx=self._ENTRY_BOX_PADDING[0], pady=self._ENTRY_BOX_PADDING[1])

        bin_image: CTkImage = get_ctk_image(Resources.Common.Light.BIN, Resources.Common.Dark.BIN, 24)
        Button(wrapper, secondary=True, image=bin_image, command=lambda id=id: self._remove_gradient_color(id)).grid(column=0, row=0)

        Label(wrapper, "menu.mod_generator.content.gradient_endpoint").grid(column=1, row=0, padx=(self._ENTRY_INNER_GAP, 0))
        endpoint_entry: Entry = Entry(
            wrapper, command=lambda event, gradient=gradient: update_gradient_endpoint(gradient, event),
            on_focus_lost="command", run_command_if_empty=False, reset_if_empty=True, height=32, width=64,
            validate="key", validatecommand=(self.register(lambda value: value == "" or value.replace(".", "", 1).isdigit()), "%P")
        )
        endpoint_entry.set(str(gradient.stop))
        endpoint_entry.grid(column=2, row=0, padx=(8, 0))

        r, g, b = gradient.color
        hex_color: str = f"#{r:02x}{g:02x}{b:02x}"
        Label(wrapper, "menu.mod_generator.content.gradient_color").grid(column=3, row=0, padx=(self._ENTRY_INNER_GAP, 0))
        frame.preview_frame = Frame(wrapper, layer=4, width=32, height=32, cursor="hand2")  # type: ignore
        frame.preview_frame.configure(fg_color=hex_color)  # type: ignore
        frame.preview_frame.grid(column=4, row=0, sticky="ew", padx=(8, 0))  # type: ignore
        frame.preview_frame.bind("<ButtonPress-1>", lambda _, frame=frame, gradient=gradient: pick_gradient_color(frame, gradient))  # type: ignore


    def set_gradient_angle(self, event) -> None:
        value_string: str = event.value
        try:
            value_float: float = float(value_string)
        except ValueError:
            event.widget.set(str(self.gradient_angle))

        self.gradient_angle = value_float
        event.widget.set(str(self.gradient_angle))
        self._update_gradient_preview()
# endregion


# region custom mask
    def _choose_custom_mask(self) -> None:
        path: str | Literal[''] = filedialog.askopenfilename(
            initialdir=Directories.DOWNLOADS,
            filetypes=(
                (Localizer.Strings["menu.mod_generator.popup.import.filetype.supported"], "*.png"),
            ), title=ProjectData.NAME)
        if not path:
            return

        image: Image.Image = Image.open(path, formats=("PNG",))
        w, h = image.size
        ratio: float = w / h
        if ratio == 1:
            preview_image: Image.Image = image.copy()
        else:  # Fit image
            size: int = max(w, h)
            preview_image = Image.new("RGBA", (size, size))
            paste_x = (size - w) // 2
            paste_y = (size - h) // 2
            preview_image.paste(image, (paste_x, paste_y))
        ctk_image: CTkImage = get_ctk_image(preview_image, size=self._custom_mask_preview_size)
        self.image_data.close()
        self.image_data = image
        self.custom_mask_preview_label.grid(column=0, row=1, pady=(8, 0), sticky="w")
        self.custom_mask_preview_label.configure(image=ctk_image)
# endregion


# region custom roblox icon
    def _remove_custom_roblox_icon(self) -> None:
        self.custom_roblox_icon = None
        self.custom_icon_preview_label.grid_forget()
        self.custom_icon_preview_label.configure(image=None)

    def _choose_custom_roblox_icon(self) -> None:
        path: str | Literal[''] = filedialog.askopenfilename(
            initialdir=Directories.DOWNLOADS,
            filetypes=(
                (Localizer.Strings["menu.mod_generator.popup.import.filetype.supported"], "*.png"),
            ), title=ProjectData.NAME)
        if path:
            self._set_custom_roblox_icon(Path(path))

    def _set_custom_roblox_icon(self, path: Path) -> None:
        if not path.suffix == ".png":
            self.root.send_banner(
                title_key="menu.mod_generator.exception.title.unknown",
                message_key="menu.mod_generator.exception.message.not_a_png",
                message_modification=lambda string: Localizer.format(string, {"{path.name}": path.name}),
                mode="warning", auto_close_after_ms=6000
            )
            return

        self.custom_roblox_icon = Image.open(path)
        self.custom_icon_preview_label.configure(image=get_ctk_image(self.custom_roblox_icon, size=self._custom_icon_preview_size))
        self.custom_icon_preview_label.grid(column=0, row=3, pady=(8, 0))
# endregion


# region additional files
    def _reset_additional_files(self) -> None:
        additional_files: dict[str, AdditionalFile] = {}
        with open(Directories.MOD_GENERATOR_FILES / "index.json") as file:
            data: dict = json.load(file)
        directory: Path = Directories.MOD_GENERATOR_FILES / "images"
        for path in directory.iterdir():
            if not path.exists():
                continue
            if not path.suffix == ".png":
                continue
            target_list: list[str] | None = data.get(path.name)
            if target_list is None:
                continue

            image: Image.Image = Image.open(path, formats=("PNG",))
            target: str = "/".join(target_list)
            additional_files[uuid.uuid4().hex] = AdditionalFile(image, target)
        self.additional_files = additional_files
        self._update_additional_files_list()


    def _remove_all_additional_files(self) -> None:
        self.additional_files = {}
        self._update_additional_files_list()


    def _remove_additional_file(self, id: str) -> None:
        self.additional_files.pop(id, None)
        self._update_additional_files_list()


    def _manual_add_additional_files(self, *_) -> None:
        files: tuple[str, ...] | Literal[''] = filedialog.askopenfilenames(
            initialdir=Directories.DOWNLOADS,
            filetypes=(
                (Localizer.Strings["menu.mod_generator.popup.import.filetype.supported"], "*.png"),
            ), title=ProjectData.NAME)
        if files:
            self._add_additional_files(tuple(Path(path) for path in files))


    def _add_additional_files(self, files_or_directories: tuple[Path, ...]) -> None:
        additional_files: dict = {}
        for file in files_or_directories:
            if file.suffix != ".png":
                self.root.send_banner(
                    title_key="menu.mod_generator.exception.title.unknown",
                    message_key="menu.mod_generator.exception.message.not_a_png",
                    message_modification=lambda string: Localizer.format(string, {"{path.name}": file.name}),
                    mode="warning", auto_close_after_ms=6000
                )
                continue
            
            image: Image.Image = Image.open(file, formats=("PNG",))
            target: str = ""
            additional_files[uuid.uuid4().hex] = AdditionalFile(image, target)
        self.additional_files.update(additional_files)
        self._update_additional_files_list()


    def _update_additional_files_list(self) -> None:
        additional_files: dict[str, AdditionalFile] = self.additional_files

        additional_file_ids: list[str] = list(additional_files.keys())

        for id, frame in list(self._additional_file_frames.items()):
            if id not in additional_file_ids:
                self._additional_file_frames.pop(id)
                frame.destroy()

        list_mapped: bool = self.additional_files_list.winfo_ismapped()
        if not additional_file_ids and list_mapped:
            self.additional_files_list.grid_forget()
            return
        elif not additional_file_ids:
            return
        elif not list_mapped:
            self.additional_files_list.grid(column=0, row=3, sticky="nsew", pady=(8, 0))

        for i, (id, addition_file) in enumerate(additional_files.items()):
            pady = 0 if i == 0 else (self._ENTRY_GAP, 0)

            frame = self._additional_file_frames.get(id)  # type: ignore
            if frame is not None:
                if getattr(frame, "_row", None) != i:
                    frame.grid(column=0, row=i, sticky="nsew", pady=pady)
                    frame._row = i  # type: ignore

            else:
                frame = Frame(self.additional_files_list, layer=3)
                frame._row = i  # type: ignore
                frame.grid(column=0, row=i, sticky="nsew", pady=pady)
                self._additional_file_frames[id] = frame
                self.after(10, self._load_additional_file_frame, frame, id, addition_file)


    def _load_additional_file_frame(self, frame: Frame, id: str, additional_file: AdditionalFile) -> None:
        def update_file_target(file: AdditionalFile, event) -> None:
            file.target = event.value

        frame.grid_columnconfigure(0, weight=1)

        wrapper: Frame = Frame(frame, transparent=True)
        wrapper.grid_columnconfigure(2, weight=1)
        wrapper.grid(column=0, row=0, sticky="nsew", padx=self._ENTRY_BOX_PADDING[0], pady=self._ENTRY_BOX_PADDING[1])

        bin_image: CTkImage = get_ctk_image(Resources.Common.Light.BIN, Resources.Common.Dark.BIN, 24)
        Button(wrapper, secondary=True, image=bin_image, command=lambda id=id: self._remove_additional_file(id)).grid(column=0, row=0)

        icon_image: CTkImage = get_ctk_image(additional_file.image, size=self._addition_icon_preview_size)
        Label(wrapper, image=icon_image).grid(column=1, row=0, padx=(self._ENTRY_INNER_GAP, 0))

        target_entry: Entry = Entry(
            wrapper, command=lambda event, additional_file=additional_file: update_file_target(additional_file, event),
            on_focus_lost="command", run_command_if_empty=True, reset_if_empty=False,
            validate="key", validatecommand=(self.register(lambda value: not re.search(r'[:*?"<>|]', value)), "%P")
        )
        target_entry.set(additional_file.target)
        target_entry.grid(column=2, row=0, sticky="ew", padx=(self._ENTRY_INNER_GAP, 0))
# endregion


# region generate
    def show_preview(self) -> None:
        mode: Literal['color', 'gradient', 'custom'] = self.mode
        angle: float = self.gradient_angle
        data: tuple[int, int, int] | list[GradientColor] | Image.Image = self.color_data if mode == "color" else self.gradient_data if mode == "gradient" else self.image_data
        custom_roblox_icon: Optional[Image.Image] = self.custom_roblox_icon
        image: Image.Image = ModGenerator.generate_preview_image(mode=mode, data=data, angle=angle, custom_roblox_icon=custom_roblox_icon)
        ModGeneratorPreviewWindow(self.root, image)


    def generate_mod(self) -> None:
        if self.generating:
            self.root.send_banner(
                title_key="menu.mod_generator.exception.title.generate",
                message_key="menu.mod_generator.exception.message.generator_busy",
                mode="warning", auto_close_after_ms=6000
            )
            return

        self.generating = True
        self.generate_button.configure(key="menu.mod_generator.content.button.generate_generating")
        mode: Literal['color', 'gradient', 'custom'] = self.mode
        angle: float = self.gradient_angle
        data: tuple[int, int, int] | list[GradientColor] | Image.Image = self.color_data if mode == "color" else self.gradient_data if mode == "gradient" else self.image_data
        custom_roblox_icon: Optional[Image.Image] = self.custom_roblox_icon
        use_remote_config: bool = self.use_remote_config
        create_1x_only: bool = self.create_1x_only
        file_version: Optional[int] = self.file_version
        additional_files: Optional[list[AdditionalFile]] = list(self.additional_files.values()) or None

        if mode == "gradient":
            if len(data) < 2:  # type: ignore
                self.root.send_banner(
                    title_key="menu.mod_generator.exception.title.generate",
                    message_key="menu.mod_generator.exception.message.gradient_not_enough_colors",
                    mode="warning", auto_close_after_ms=6000
                )
                self.generating = False
                self.generate_button.configure(key="menu.mod_generator.content.button.generate")
                return

        mod_name: str = self.mod_name
        if Directories.MODS.exists():
            existing_mods = {path.stem.lower() if path.is_file() else path.name.lower() for path in Directories.MODS.iterdir()}
            if mod_name.lower() in existing_mods:
                self.root.send_banner(
                    title_key="menu.mod_generator.exception.title.generate",
                    message_key="menu.mod_generator.exception.message.mod_exists",
                    mode="warning", auto_close_after_ms=6000
                )
                self.generating = False
                self.generate_button.configure(key="menu.mod_generator.content.button.generate")
                return
        else:
            Directories.MODS.mkdir(parents=True, exist_ok=True)

        try:
            ModGenerator.generate_mod(mode, data, Directories.MODS / mod_name, angle=angle, file_version=file_version, use_remote_config=use_remote_config, create_1x_only=create_1x_only, custom_roblox_icon=custom_roblox_icon, additional_files=additional_files)

        except Exception as e:
            self.root.send_banner(
                title_key="menu.mod_generator.exception.title.generate",
                message_key="menu.mod_generator.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                mode="error", auto_close_after_ms=6000
            )

        else:
            self.root.send_banner(
                title_key="menu.mod_generator.success.title.generate",
                message_key="menu.mod_generator.success.message.generate",
                message_modification=lambda string: Localizer.format(string, {"{mod.name}": mod_name}),
                mode="success", auto_close_after_ms=4000
            )
        self.generating = False
        self.generate_button.configure(key="menu.mod_generator.content.button.generate")
# endregion