from tkinter import TclError, BooleanVar, StringVar
from xml.etree import ElementTree as xml
from typing import Literal, Any, TYPE_CHECKING

from modules.logger import Logger
from modules.project_data import ProjectData
from modules.frontend.widgets import ScrollableFrame, Frame, Label, ToggleSwitch, Entry
from modules.frontend.functions import get_ctk_image
from modules.localization import Localizer
from modules.filesystem import Resources, Files

if TYPE_CHECKING: from modules.frontend.widgets import Root

from customtkinter import CTkImage  # type: ignore


WHITELISTED_TAGS: set[str] = {"bool", "token", "string", "int", "float", "Vector2"}


class XMLError(Exception): pass


class GlobalBasicSettingsSection(ScrollableFrame):
    loaded: bool = False
    file_not_found: bool = False
    root: "Root"

    _SECTION_PADX: int | tuple[int, int] = (8, 4)
    _SECTION_PADY: int | tuple[int, int] = 8

    _COLUMNS: int = 2
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
        self.file_not_found = False
        self.loaded = False


    def refresh(self) -> None:
        self.clear()
        self.show()


    def show(self) -> None:
        if self.loaded and self.file_not_found:
            self.clear()
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

        Label(header, "menu.global_basic_settings.header.title", lambda string: Localizer.format(string, {"{roblox.common}": Localizer.Key("roblox.common"), "{roblox.player}": Localizer.Key("roblox.player"), "{roblox.player_alt}": Localizer.Key("roblox.player_alt"), "{roblox.studio}": Localizer.Key("roblox.studio"), "{roblox.studio_alt}": Localizer.Key("roblox.studio_alt")}), style="title", autowrap=True).grid(column=0, row=0, sticky="ew")
        Label(header, "menu.global_basic_settings.header.description", lambda string: Localizer.format(string, {"{roblox.common}": Localizer.Key("roblox.common")}), style="caption", autowrap=True).grid(column=0, row=1, sticky="ew")


    def _load_content(self, master) -> None:
        wrapper: Frame = Frame(master, transparent=True)
        wrapper.grid(column=0, row=1, sticky="nsew")

        if not Files.GLOBAL_BASIC_SETTINGS.exists():
            wrapper.grid_columnconfigure(0, weight=1)
            wrapper.grid_rowconfigure(1, weight=1)
            image: CTkImage = get_ctk_image(Resources.Large.Light.FILE_NOT_FOUND, Resources.Large.Dark.FILE_NOT_FOUND, 88)
            Label(wrapper, "menu.global_basic_settings.content.file_not_found", lambda string: Localizer.format(string, {"{file.name}": Files.GLOBAL_BASIC_SETTINGS.name}), style="body", image=image, compound="left").place(relx=0.5, rely=0.5, anchor="center")
            self.file_not_found = True
            return

        self.file_not_found = False
        Logger.info(f"Loading {Files.GLOBAL_BASIC_SETTINGS.name}...")

        tree: xml.ElementTree = xml.parse(Files.GLOBAL_BASIC_SETTINGS)
        root: xml.Element | None = tree.getroot()
        if root is None: raise XMLError("Missing root element.")
        properties: xml.Element | None = root.find(".//Properties")
        if properties is None: raise XMLError("Missing <Properties> element.")

        wrapper.grid_columnconfigure(list(range(self._COLUMNS)), weight=1, uniform="group")

        element_counter: int = -1
        for element in properties:
            if element.tag not in WHITELISTED_TAGS or "name" not in element.attrib:
                continue

            element_counter += 1
            self.after(0, self.create_frame, tree, element, element_counter, wrapper)
# endregion


# region frame
    def create_frame(self, tree: xml.ElementTree, element: xml.Element, index: int, master) -> None:
        column: int = index % self._COLUMNS
        row: int = index // self._COLUMNS
        padx: int = 0 if column == 0 else self._ENTRY_GAP
        pady: int = 0 if row == 0 else self._ENTRY_GAP

        frame: Frame = Frame(master, transparent=False, layer=2)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid(column=column, row=row, sticky="nsew", padx=padx, pady=pady)

        content: Frame = Frame(frame, transparent=True)
        content.grid_columnconfigure(0, weight=1)
        content.grid(column=0, row=0, sticky="nsew", padx=self._ENTRY_PADDING[0], pady=self._ENTRY_PADDING[1])

        name: str = element.attrib["name"]
        tag: str = element.tag

        # Name
        display_name: str = f"[{tag.upper()}] {name}"
        Label(content, display_name, style="body_strong", autowrap=True, dont_localize=True).grid(column=0, row=0, sticky="ew")

        # Value
        value_box: Frame = Frame(content, transparent=True, height=32)
        value_box.grid_columnconfigure(1, weight=1)
        value_box.grid(column=0, row=1, sticky="ew", pady=(self._ENTRY_INNER_GAP, 0))


        match tag:
            case "string" | "token":
                string_value: str = (element.text or "")

                string_var: StringVar = StringVar(frame, value=string_value)
                Label(value_box, "menu.global_basic_settings.content.value", style="body", autowrap=False).grid(column=0, row=0, sticky="w")
                Entry(
                    value_box, on_focus_lost="command", run_command_if_empty=False, reset_if_empty=True, command=lambda _, element=element, var=string_var: self.update_string_value(tree, element, var.get()),
                    height=32, textvariable=string_var
                ).grid(column=1, row=0, sticky="ew", padx=(8, 0))


            case "int":
                string_value = (element.text or "")

                string_var = StringVar(frame, value=string_value)
                Label(value_box, "menu.global_basic_settings.content.value", style="body", autowrap=False).grid(column=0, row=0, sticky="w")
                Entry(
                    value_box, on_focus_lost="command", run_command_if_empty=False, reset_if_empty=True, command=lambda _, element=element, var=string_var: self.update_string_value(tree, element, var.get()),
                    height=32, textvariable=string_var, validate="key", validatecommand=(self.root.register(lambda value: value.isdigit() or value == ""), '%P')
                ).grid(column=1, row=0, sticky="ew", padx=(8, 0))


            case "float":
                string_value = (element.text or "")

                string_var = StringVar(frame, value=string_value)
                Label(value_box, "menu.global_basic_settings.content.value", style="body", autowrap=False).grid(column=0, row=0, sticky="w")
                Entry(
                    value_box, on_focus_lost="command", run_command_if_empty=False, reset_if_empty=True, command=lambda _, element=element, var=string_var: self.update_string_value(tree, element, var.get()),
                    height=32, textvariable=string_var, validate="key", validatecommand=(self.root.register(lambda value: value.replace(".", "", 1).isdigit() or value == ""), '%P')
                ).grid(column=1, row=0, sticky="ew", padx=(8, 0))


            case "bool":
                bool_value: bool = (element.text or "false").strip().lower() == "true"

                bool_var: BooleanVar = BooleanVar(frame, value=bool_value)
                Label(value_box, "menu.global_basic_settings.content.value", style="body", autowrap=False).grid(column=0, row=0, sticky="w")
                ToggleSwitch(value_box, variable=bool_var, command=lambda element=element, var=bool_var: self.update_string_value(tree, element, str(var.get()).lower())).grid(column=1, row=0, sticky="w", padx=(8, 0))


            case "Vector2":
                value_box.grid_columnconfigure((1, 3), weight=1)

                x_element: xml.Element | None = element.find("X")
                y_element: xml.Element | None = element.find("Y")
                string_value_x: str = "" if x_element is None else (x_element.text or "")
                string_value_y: str ="" if y_element is None else (y_element.text or "")

                string_var_x = StringVar(frame, value=string_value_x)
                Label(value_box, "menu.global_basic_settings.content.x_value", style="body", autowrap=False).grid(column=0, row=0, sticky="w")
                Entry(
                    value_box, on_focus_lost="command", run_command_if_empty=False, reset_if_empty=True, command=lambda _, element=x_element, var=string_var_x: self.update_string_value(tree, element, var.get()),
                    height=32, textvariable=string_var_x, validate="key", validatecommand=(self.root.register(lambda value: value.replace(".", "", 1).isdigit() or value == ""), '%P')
                ).grid(column=1, row=0, sticky="ew", padx=(8, 0))

                string_var_y = StringVar(frame, value=string_value_y)
                Label(value_box, "menu.global_basic_settings.content.y_value", style="body", autowrap=False).grid(column=2, row=0, sticky="w", padx=(self._ENTRY_INNER_GAP, 0))
                Entry(
                    value_box, on_focus_lost="command", run_command_if_empty=False, reset_if_empty=True, command=lambda _, element=y_element, var=string_var_y: self.update_string_value(tree, element, var.get()),
                    height=32, textvariable=string_var_y, validate="key", validatecommand=(self.root.register(lambda value: value.replace(".", "", 1).isdigit() or value == ""), '%P')
                ).grid(column=3, row=0, sticky="ew", padx=(8, 0))
# endregion


# region functions
    def update_string_value(self, tree: xml.ElementTree, element: xml.Element, value_or_event: str | Any) -> None:
        if isinstance(value_or_event, str): value: str = value_or_event
        else: value = value_or_event.widget.get()
        element.text = value
        tree.write(Files.GLOBAL_BASIC_SETTINGS)
# endregion