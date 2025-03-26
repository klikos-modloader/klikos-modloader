from xml.etree import ElementTree as xml
from pathlib import Path
from typing import Literal

from modules.logger import Logger
from modules.localization import Localizer
from modules.core.globalbasicsettings_editor import GlobalBasicSettingsEditor, GlobalBasicSettingsPermissionError
from modules.frontend.widgets.fluent import FluentLabel, FluentFrame, FluentToolTipButton, FluentToggleSwitch, FluentTextBox, messagebox, get_root_instance

import customtkinter as ctk  # type: ignore
from PIL import Image  # type: ignore


class GlobalBasicSettingsSection:
    PADDING_X: int = 16
    PADDING_Y: int = 16
    ENTRY_GAP: int = 12
    ENTRY_PADX: int = 16
    ENTRY_PADY: int = 16
    ENTRY_INNER_GAP_SMALL: int = 4
    ENTRY_INNER_GAP_MEDIUM: int = 8
    ENTRY_INNER_GAP_LARGE: int = 12
    ENTRY_TITLE_FONT_SIZE: int = 14
    ENTRY_TEXT_FONT_SIZE: int = 12
    ENTRY_TEXTBOX_SHORT: int = 108
    ENTRY_TEXTBOX_LONG: int = 188
    COLUMNS: int = 2
    
    WHITELISTED_ELEMENTS: list[str] = ["bool", "token", "string", "int", "float", "Vector2"]

    resources: Path
    file_not_found: ctk.CTkImage

    master: ctk.CTkFrame
    content: ctk.CTkFrame | ctk.CTkScrollableFrame
    tooltip_button: FluentToolTipButton

    active: bool = False
    first_load: bool = True


    def __init__(self, root: ctk.CTk, master: ctk.CTkFrame | ctk.CTkScrollableFrame, resources: Path) -> None:
        self.root = root
        self.master = master
        self.resources = resources
        self.file_not_found = ctk.CTkImage(Image.open(self.resources / "large" / "light" / "file_not_found.png"), Image.open(self.resources / "large" / "dark" / "file_not_found.png"), size=(96, 96))


    def refresh(self) -> None:
        self._clear()
        self._load()


    def load(self) -> None:
        if self.active: return
        self.active = True
        self.tooltip_button.enable()


    def unload(self) -> None:
        self.active = False
        self.tooltip_button.disable()


    def _clear(self) -> None:
        for widget in self.master.winfo_children():
            widget.destroy()


    def _load(self) -> None:
        self.content = ctk.CTkFrame(self.master, fg_color="transparent")
        self.content.grid(column=0, row=0, sticky="nsew", padx=self.PADDING_X, pady=self.PADDING_Y)
        self.content.grid_columnconfigure(0, weight=1)
        self._get_title_frame().grid(column=0, row=0, sticky="nsew")
        self._get_content().grid(column=0, row=1, sticky="nsew", pady=(16,0))


    def _get_title_frame(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.content, fg_color="transparent")

        title_row = ctk.CTkFrame(frame, fg_color="transparent")
        title_row.grid(column=0, row=0, sticky="w")

        FluentLabel(title_row, Localizer.strings["menu.globalbasicsettings"]["title"], font_size=28, font_weight="bold").grid(column=0, row=0, sticky="w")
        self.tooltip_button = FluentToolTipButton(get_root_instance(), master=title_row, wraplength=400, tooltip_title=Localizer.strings["menu.globalbasicsettings"]["tooltip.title"], tooltip_message=Localizer.strings["menu.globalbasicsettings"]["tooltip.message"], tooltip_orientation="down", toplevel=True)
        self.tooltip_button.grid(column=1, row=0, padx=(8,0), sticky="w")

        return frame


    def _get_content(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.content, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)

        try:
            tree: xml.ElementTree = GlobalBasicSettingsEditor.get_tree()
            root = tree.getroot()
            properties = root.find(".//Properties")
        except Exception as e:
            Logger.warning(f"Failed to load data! {type(e).__name__}: {e}", prefix="menu.globalbasicsettings")
            properties = None

        if properties is None:
            frame.grid_columnconfigure(0, weight=1)
            content_frame = FluentFrame(frame)
            content_frame.grid(column=0, row=0, sticky="nsew")
            FluentLabel(content_frame, Localizer.strings["menu.globalbasicsettings"]["failed_to_load"], image=self.file_not_found, font_size=24, font_weight="bold", compound="left", padx=16).place(relx=0.5, rely=0.5, anchor="center")
            return frame

        # Annoying workaround because `uniform="group"` ignores padding
        # Instead of padding, I add an invisible frame between each column
        for i in range(0, (self.COLUMNS*2)-1, 2):
            frame.grid_columnconfigure(i, weight=1, uniform="group")
        for i in range(1, (self.COLUMNS*2)-1, 2):
            ctk.CTkFrame(frame, width=self.ENTRY_GAP, height=1, fg_color="transparent").grid(column=i, row=0, sticky="ns")

        element_counter: int = -1
        for element in properties:
            if "name" not in element.attrib: continue
            if element.tag not in self.WHITELISTED_ELEMENTS: continue

            element_counter += 1
            column: int = self._get_grid_column(element_counter)
            row: int = self._get_grid_row(element_counter)
            element_name: str = element.attrib["name"]

            element_frame = FluentFrame(frame)
            element_frame.grid_columnconfigure(0, weight=1)
            element_frame.grid(column=column, row=row, pady=0 if row == 0 else (self.ENTRY_GAP, 0), sticky="nsew")

            title_frame = ctk.CTkFrame(element_frame, fg_color="transparent")
            title_frame.grid(column=0, row=0, padx=self.ENTRY_PADX, pady=(self.ENTRY_PADY, 0), sticky="w")
            FluentLabel(title_frame, element_name, font_weight="bold", font_size=self.ENTRY_TITLE_FONT_SIZE).grid(column=0, row=0, sticky="w")

            content_frame = ctk.CTkFrame(element_frame, fg_color="transparent")
            content_frame.grid(column=0, row=1, padx=self.ENTRY_PADX, pady=(self.ENTRY_INNER_GAP_SMALL, self.ENTRY_PADY), sticky="w")

            match element.tag:
                case "bool":
                    FluentLabel(content_frame, Localizer.strings["menu.globalbasicsettings"]["element.bool"], font_size=self.ENTRY_TEXT_FONT_SIZE).grid(column=0, row=0, sticky="w")

                    value = (element.text or "").strip().lower() == "true"
                    toggle = FluentToggleSwitch(content_frame, value=value)
                    toggle.command = lambda value, tree=tree, name=element_name, widget=toggle: self._set_boolean_value(tree=tree, name=name, value=value, widget=widget)
                    toggle.grid(column=1, row=0, sticky="w", padx=(self.ENTRY_INNER_GAP_MEDIUM, 0))

                case "int":
                    FluentLabel(content_frame, Localizer.strings["menu.globalbasicsettings"]["element.int"], font_size=self.ENTRY_TEXT_FONT_SIZE).grid(column=0, row=0, sticky="w")
                    value = (element.text or "").strip()
                    textbox = FluentTextBox(content_frame, width=self.ENTRY_TEXTBOX_LONG, validatecommand=(self.root.register(lambda value: value.removeprefix("-").isdigit() or value == "" or value == "-"), '%P'))
                    textbox.set(value)

                    for binding in ("<Return>", "<Control-s>"): textbox.entry.bind(binding, lambda _: self.root.focus())
                    textbox.entry.bind("<FocusOut>", lambda event, tree=tree, name=element_name: self._set_integer_value(tree=tree, name=name, value=event.widget.get(), widget=event.widget))
                    textbox.grid(column=1, row=0, sticky="w", padx=(self.ENTRY_INNER_GAP_MEDIUM, 0))

                case "float":
                    FluentLabel(content_frame, Localizer.strings["menu.globalbasicsettings"]["element.float"], font_size=self.ENTRY_TEXT_FONT_SIZE).grid(column=0, row=0, sticky="w")
                    value = (element.text or "").strip()
                    textbox = FluentTextBox(content_frame, width=self.ENTRY_TEXTBOX_LONG, validatecommand=(self.root.register(lambda value: value.removeprefix("-").replace(".", "", 1).isdigit() or value == "" or value == "-"), '%P'))
                    textbox.set(value)

                    for binding in ("<Return>", "<Control-s>"): textbox.entry.bind(binding, lambda _: self.root.focus())
                    textbox.entry.bind("<FocusOut>", lambda event, tree=tree, name=element_name: self._set_float_value(tree=tree, name=name, value=event.widget.get(), widget=event.widget))
                    textbox.grid(column=1, row=0, sticky="w", padx=(self.ENTRY_INNER_GAP_MEDIUM, 0))

                case "string":
                    FluentLabel(content_frame, Localizer.strings["menu.globalbasicsettings"]["element.string"], font_size=self.ENTRY_TEXT_FONT_SIZE).grid(column=0, row=0, sticky="w")
                    value = (element.text or "").strip()
                    textbox = FluentTextBox(content_frame, width=self.ENTRY_TEXTBOX_LONG)
                    textbox.set(value)

                    for binding in ("<Return>", "<Control-s>"): textbox.entry.bind(binding, lambda _: self.root.focus())
                    textbox.entry.bind("<FocusOut>", lambda event, tree=tree, name=element_name: self._set_string_value(tree=tree, name=name, value=event.widget.get(), widget=event.widget))
                    textbox.grid(column=1, row=0, sticky="w", padx=(self.ENTRY_INNER_GAP_MEDIUM, 0))

                case "token":
                    FluentLabel(content_frame, Localizer.strings["menu.globalbasicsettings"]["element.token"], font_size=self.ENTRY_TEXT_FONT_SIZE).grid(column=0, row=0, sticky="w")
                    value = (element.text or "").strip()
                    textbox = FluentTextBox(content_frame, width=self.ENTRY_TEXTBOX_LONG)
                    textbox.set(value)

                    for binding in ("<Return>", "<Control-s>"): textbox.entry.bind(binding, lambda _: self.root.focus())
                    textbox.entry.bind("<FocusOut>", lambda event, tree=tree, name=element_name: self._set_token_value(tree=tree, name=name, value=event.widget.get(), widget=event.widget))
                    textbox.grid(column=1, row=0, sticky="w", padx=(self.ENTRY_INNER_GAP_MEDIUM, 0))

                case "Vector2":
                    # FluentLabel(content_frame, Localizer.strings["menu.globalbasicsettings"]["element.vector2"]).grid(column=0, row=0, sticky="w", columnspan=4)

                    x_element = element.find("X")
                    x_value = (x_element.text or "").strip() if x_element is not None else ""
                    FluentLabel(content_frame, Localizer.strings["menu.globalbasicsettings"]["element.vector2_x"], font_size=self.ENTRY_TEXT_FONT_SIZE).grid(column=0, row=0, sticky="w")
                    textbox = FluentTextBox(content_frame, width=self.ENTRY_TEXTBOX_SHORT, validatecommand=(self.root.register(lambda value: value.removeprefix("-").replace(".", "", 1).isdigit() or value == "" or value == "-"), '%P'))
                    textbox.set(x_value)

                    for binding in ("<Return>", "<Control-s>"): textbox.entry.bind(binding, lambda _: self.root.focus())
                    textbox.entry.bind("<FocusOut>", lambda event, tree=tree, name=element_name, mode="X": self._set_vector_2_value(tree=tree, name=name, value=event.widget.get(), widget=event.widget, mode=mode))
                    textbox.grid(column=1, row=0, sticky="w", padx=(self.ENTRY_INNER_GAP_MEDIUM, 0))
                    
                    y_element = element.find("X")
                    y_value = (y_element.text or "").strip() if y_element is not None else ""
                    FluentLabel(content_frame, Localizer.strings["menu.globalbasicsettings"]["element.vector2_y"], font_size=self.ENTRY_TEXT_FONT_SIZE).grid(column=3, row=0, padx=(self.ENTRY_INNER_GAP_LARGE, 0), sticky="w")
                    textbox = FluentTextBox(content_frame, width=self.ENTRY_TEXTBOX_SHORT, validatecommand=(self.root.register(lambda value: value.removeprefix("-").replace(".", "", 1).isdigit() or value == "" or value == "-"), '%P'))
                    textbox.set(y_value)

                    for binding in ("<Return>", "<Control-s>"): textbox.entry.bind(binding, lambda _: self.root.focus())
                    textbox.entry.bind("<FocusOut>", lambda event, tree=tree, name=element_name, mode="Y": self._set_vector_2_value(tree=tree, name=name, value=event.widget.get(), widget=event.widget, mode=mode))
                    textbox.grid(column=4, row=0, sticky="w", padx=(self.ENTRY_INNER_GAP_MEDIUM, 0))

        return frame


# region functions
    def _get_grid_column(self, i: int) -> int:
        return (i%self.COLUMNS)*2


    def _get_grid_row(self, i: int) -> int:
        return i//self.COLUMNS


    def _set_string_value(self, tree: xml.ElementTree, name: str, value: str, widget: FluentTextBox) -> None:
        try: GlobalBasicSettingsEditor.update_element(tree, name, value)

        except KeyError:
            widget.set(not value)
            messagebox.show_warning(Localizer.strings["errors"]["globalbasicsettings"]["update_value.title"], Localizer.strings["errors"]["globalbasicsettings"]["update_value.key_error"].replace("{element}", name), blocking=False)
            return

        except GlobalBasicSettingsPermissionError as e:
            widget.set(not value)
            messagebox.show_warning(Localizer.strings["errors"]["globalbasicsettings"]["update_value.title"], Localizer.strings["errors"]["globalbasicsettings"]["update_value.permission_denied"].replace("{path}", e.path), blocking=False)
            return


    def _set_token_value(self, tree: xml.ElementTree, name: str, value: str, widget: FluentTextBox) -> None:
        self._set_string_value(tree=tree, name=name, value=value, widget=widget)


    def _set_integer_value(self, tree: xml.ElementTree, name: str, value: str, widget: FluentTextBox) -> None:
        if not value or value == "-" or value == "-0":
            value = "0"
            widget.set(value)

        try: int(value)
        except ValueError:
            messagebox.show_warning(Localizer.strings["errors"]["globalbasicsettings"]["update_value.title"], Localizer.strings["errors"]["globalbasicsettings"]["update_value.not_an_integer"].replace("{value}", value), blocking=False)
            return
        self._set_string_value(tree=tree, name=name, value=value, widget=widget)


    def _set_float_value(self, tree: xml.ElementTree, name: str, value: str, widget: FluentTextBox) -> None:
        if not value or value == "-" or value == "-0":
            value = "0"
            widget.set(value)

        try: float(value)
        except ValueError:
            messagebox.show_warning(Localizer.strings["errors"]["globalbasicsettings"]["update_value.title"], Localizer.strings["errors"]["globalbasicsettings"]["update_value.not_a_float"].replace("{value}", value), blocking=False)
            return
        self._set_string_value(tree=tree, name=name, value=value, widget=widget)


    def _set_boolean_value(self, tree: xml.ElementTree, name: str, value: bool, widget: FluentToggleSwitch) -> None:
        try: GlobalBasicSettingsEditor.update_element(tree, name, str(value).lower())

        except KeyError:
            widget.set(not value)
            messagebox.show_warning(Localizer.strings["errors"]["globalbasicsettings"]["update_value.title"], Localizer.strings["errors"]["globalbasicsettings"]["update_value.key_error"].replace("{element}", name), blocking=False)
            return

        except GlobalBasicSettingsPermissionError as e:
            widget.set(not value)
            messagebox.show_warning(Localizer.strings["errors"]["globalbasicsettings"]["update_value.title"], Localizer.strings["errors"]["globalbasicsettings"]["update_value.permission_denied"].replace("{path}", e.path), blocking=False)
            return


    def _set_vector_2_value(self, tree: xml.ElementTree, name: str, value: str, widget: FluentTextBox, mode: Literal["X", "Y"] = "X") -> None:
        if not value or value == "-" or value == "-0":
            value = "0"
            widget.set(value)

        try: float(value)
        except ValueError:
            messagebox.show_warning(Localizer.strings["errors"]["globalbasicsettings"]["update_value.title"], Localizer.strings["errors"]["globalbasicsettings"]["update_value.not_a_float"].replace("{value}", value), blocking=False)
            return

        try: GlobalBasicSettingsEditor.update_sub_element(tree, name, mode, value)

        except KeyError:
            widget.set(not value)
            messagebox.show_warning(Localizer.strings["errors"]["globalbasicsettings"]["update_value.title"], Localizer.strings["errors"]["globalbasicsettings"]["update_value.key_error"].replace("{element}", name), blocking=False)
            return

        except GlobalBasicSettingsPermissionError as e:
            widget.set(not value)
            messagebox.show_warning(Localizer.strings["errors"]["globalbasicsettings"]["update_value.title"], Localizer.strings["errors"]["globalbasicsettings"]["update_value.permission_denied"].replace("{path}", e.path), blocking=False)
            return
# endregion