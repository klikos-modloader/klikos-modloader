import re
import shutil
from typing import Literal
from pathlib import Path

from modules.localization import Localizer
from modules.info import NAME
from modules.frontend.widgets.fluent import FluentFrame, FluentLabel, FluentTextBox, FluentButton, FluentCheckBox, FluentToolTipButton, FluentDnDFrame, get_root_instance, messagebox
from modules.core.mod_manager import ModManager, ModConfigEditor, Mod, ModConfigPermissionsError, ModNotFoundError, ModAlreadyExistsError, ModPermissionError
from modules.filesystem import Directory, SourceNotAFileError, ExtractPermissionError
from modules import filesystem

from natsort import natsorted  # type: ignore
import customtkinter as ctk  # type: ignore
from PIL import Image  # type: ignore


class ModsSection:
    PADDING_X: int = 16
    PADDING_Y: int = 16
    ENTRY_GAP: int = 8
    ENTRY_PADX: int = 12
    ENTRY_PADY: int = 16
    ENTRY_INNER_GAP: int = 8

    resources: Path
    bin_light: Image
    bin_dark: Image

    master: ctk.CTkFrame
    content: ctk.CTkFrame | ctk.CTkScrollableFrame
    mod_list_frame: ctk.CTkFrame
    tooltip_button: FluentToolTipButton

    active: bool = False
    _pause_background_tasks: bool = False
    _mod_names: list[str]

    _frame_cache: dict[str, FluentFrame]


    def __init__(self, root: ctk.CTk, master: ctk.CTkFrame | ctk.CTkScrollableFrame, resources: Path) -> None:
        self.root = root
        self.master = master
        self.resources = resources
        self.bin_light = Image.open(self.resources / "common" / "light" / "bin.png")
        self.bin_dark = Image.open(self.resources / "common" / "dark" / "bin.png")


    def refresh(self) -> None:
        self._clear()
        self._load()
        self._mod_names = []


    def load(self) -> None:
        if self.active: return
        self.active = True
        self.tooltip_button.enable()
        self.master.after(10, self._run_background_tasks)


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

        FluentLabel(title_row, Localizer.strings["menu.mods"]["title"], font_size=28, font_weight="bold").grid(column=0, row=0, sticky="w")
        self.tooltip_button = FluentToolTipButton(get_root_instance(), master=title_row, wraplength=400, tooltip_title=Localizer.strings["menu.mods"]["tooltip.title"], tooltip_message=Localizer.strings["menu.mods"]["tooltip.message"].replace("{project_name}", NAME), tooltip_orientation="down", toplevel=True)
        self.tooltip_button.grid(column=1, row=0, padx=(8,0), sticky="w")

        button_row = ctk.CTkFrame(frame, fg_color="transparent")
        button_row.grid(column=0, row=1, sticky="w", pady=(8,0))

        FluentButton(button_row, Localizer.strings["buttons.open_mods_folder"], command=self._open_mods_folder, toplevel=True).grid(column=0, row=0)

        return frame

    
    def _get_content(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.content, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)

        dnd_frame = FluentDnDFrame(frame, Localizer.strings["menu.mods"]["dnd_frame"], height=128, command=self._import_mods)
        dnd_frame.grid(column=0, row=0, sticky="ew")

        self.mod_list_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.mod_list_frame.grid_columnconfigure(0, weight=1)
        self.mod_list_frame.grid(column=0, row=1, sticky="ew", pady=(self.ENTRY_GAP,0))

        return frame


# region background tasks
    def _run_background_tasks(self) -> None:
        if not self.active: return

        mods = ModManager.get_mods()
        sorted_mods: list[Mod] = natsorted(mods, key=lambda mod: mod.name)
        mod_names: list[str] = [mod.name for mod in sorted_mods]

        if mod_names == self._mod_names:
            self.master.after(10, self._run_background_tasks)
            return

        # for widget in self.mod_list_frame.winfo_children():
        #     widget.destroy()

        existing_frames = {widget.reference: widget for widget in self.mod_list_frame.winfo_children() if hasattr(widget, "reference")}

        for i, mod in enumerate(sorted_mods):
            if mod.name in existing_frames:
                frame = existing_frames[mod.name]
                if frame.grid_info()["row"] != i: frame.grid(column=0, row=i, sticky="nsew", pady=0 if i == 0 else (self.ENTRY_GAP, 0))
                continue

            frame = FluentFrame(self.mod_list_frame)
            frame.grid_columnconfigure((2, 3), weight=1)
            frame.grid(column=0, row=i, sticky="nsew", pady=0 if i == 0 else (self.ENTRY_GAP, 0))

            # Delete
            FluentButton(frame, width=32, height=32, command=lambda mod_object=mod: self._delete_mod(mod_object), light_icon=self.bin_light, dark_icon=self.bin_dark, icon_size=(20, 20)).grid(column=0, row=0, padx=(self.ENTRY_PADX, 0), pady=self.ENTRY_PADY, sticky="w")

            # Name
            name_textbox: FluentTextBox = FluentTextBox(frame, width=256, validate="key", validatecommand=(self.root.register(lambda value: not re.search(r'[\\/:*?"<>|]', value)), "%P"))
            name_textbox.insert("end", mod.name)
            for binding in ("<Return>", "<Control-s>"): name_textbox.entry.bind(binding, lambda _: self.root.focus())
            name_textbox.entry.bind("<FocusOut>", lambda event, mod_object=mod: self._rename_mod(event, mod_object))
            name_textbox.grid(column=1, row=0, padx=(self.ENTRY_INNER_GAP, 0), pady=self.ENTRY_PADY, sticky="w")

            # Load order
            load_order_frame = ctk.CTkFrame(frame, fg_color="transparent")

            FluentLabel(load_order_frame, Localizer.strings["menu.mods"]["load_order"]).grid(column=0, row=0)

            load_order_textbox: FluentTextBox = FluentTextBox(load_order_frame, validate="key", validatecommand=(self.root.register(lambda value: value.removeprefix("-").isdigit() or value.removeprefix("-") == ""), "%P"))
            load_order_textbox.insert("end", str(mod.Config.priority))
            for binding in ("<Return>", "<Control-s>"): load_order_textbox.entry.bind(binding, lambda _: self.root.focus())
            load_order_textbox.entry.bind("<FocusOut>", lambda event, mod_object=mod: self._change_load_order(event, mod_object))
            load_order_textbox.grid(column=1, row=0, padx=(8, 0))

            load_order_frame.grid(column=2, row=0, padx=self.ENTRY_INNER_GAP, pady=self.ENTRY_PADY)
            
            FluentCheckBox(frame, Localizer.strings["menu.mods"]["status.player"], lambda value, mod_object=mod: self._set_mod_state(value, mod_object, "player"), "right", mod.Config.player).grid(column=3, row=0)
            FluentCheckBox(frame, Localizer.strings["menu.mods"]["status.studio"], lambda value, mod_object=mod: self._set_mod_state(value, mod_object, "studio"), "right", mod.Config.studio).grid(column=4, row=0, padx=(self.ENTRY_INNER_GAP,self.ENTRY_PADX))

            frame.reference = mod.name

        for entry in list(existing_frames.keys()):
            if entry not in mod_names:
                existing_frames[entry].destroy()

        self._mod_names = mod_names
        self.master.after(10, self._run_background_tasks)
# endregion


# region functions
    def _open_mods_folder(self) -> None:
        Directory.MODS.mkdir(parents=True, exist_ok=True)
        filesystem.open(Directory.MODS)


    def _delete_mod(self, mod: Mod) -> None:
        def on_ok() -> None:
            try:
                mod.delete()
            except ModNotFoundError as e:
                messagebox.show_error(Localizer.strings["errors"]["mods"]["delete.title"], Localizer.strings["errors"]["mods"]["delete.not_found"].replace("{mod}", e.name), blocking=False)
            except (ModConfigPermissionsError, ModPermissionError) as e:
                messagebox.show_error(Localizer.strings["errors"]["mods"]["delete.title"], Localizer.strings["errors"]["mods"]["delete.permission_denied"].replace("{path}", e.path), blocking=False)
        messagebox.ask_ok_cancel_nonblocking(Localizer.strings["popups"]["mods"]["confirm_delete.title"].replace("{mod}", mod.name), Localizer.strings["popups"]["mods"]["confirm_delete.message"], on_ok)


    def _rename_mod(self, event, mod: Mod) -> None:
        old: str = mod.name
        new: str = event.widget.get()

        if old == new: return
        if not new or new == "-":
            event.widget.delete(0, "end")
            event.widget.insert(0, old)
            return

        try:
            ModConfigEditor.rename_item(old, new)
            mod.name = new
            mod.path = Directory.MODS / new
        except ModNotFoundError as e:
            messagebox.show_error(Localizer.strings["errors"]["mods"]["rename.title"], Localizer.strings["errors"]["mods"]["rename.not_found"].replace("{mod}", e.name), blocking=False)
        except ModAlreadyExistsError as e:
            messagebox.show_error(Localizer.strings["errors"]["mods"]["rename.title"], Localizer.strings["errors"]["mods"]["rename.already_exists"], blocking=False)
        except ModConfigPermissionsError as e:
            messagebox.show_error(Localizer.strings["errors"]["mods"]["rename.title"], Localizer.strings["errors"]["mods"]["rename.permission_denied"].replace("{path}", str(e.path.resolve())), blocking=False)


    def _change_load_order(self, event, mod: Mod) -> None:
        old: int = mod.Config.priority
        new: str = event.widget.get()

        try:
            new_int: int = int(new)
        except ValueError:
            event.widget.delete(0, "end")
            event.widget.insert(0, str(old))

        if old == new_int: return

        try:
            mod.Config.priority = new_int
            ModConfigEditor.update_item(mod.name, mod.Config)
        except ModConfigPermissionsError as e:
            messagebox.show_error(Localizer.strings["errors"]["mods"]["config.title"], Localizer.strings["errors"]["mods"]["config.permission_denied"].replace("{path}", str(e.path.resolve())), blocking=False)
    

    def _set_mod_state(self, new: bool, mod: Mod, mode: Literal["player", "studio"]) -> None:
        old: bool = mod.Config.studio if mode == "studio" else mod.Config.player
        if old == new: return

        match mode:
            case "player": mod.Config.player = new
            case "studio": mod.Config.studio = new
            case unknown: raise ValueError(f"Invalid mode: {unknown} (must be 'player' or 'studio')")

        try:
            ModConfigEditor.update_item(mod.name, mod.Config)
        except ModConfigPermissionsError as e:
            messagebox.show_error(Localizer.strings["errors"]["mods"]["config.title"], Localizer.strings["errors"]["mods"]["config.permission_denied"].replace("{path}", str(e.path.resolve())), blocking=False)


# region import mods
    def _import_mods(self, files_or_directories: tuple[Path]) -> None:
        if not files_or_directories: return
        if not any(path.exists() for path in files_or_directories): return

        unsupported_files: list[str] = []

        for path in files_or_directories:
            if path.is_dir():
                name: str = path.name

                target: Path = Directory.MODS / name
                n: int = 1
                while target.exists():
                    target = Directory.MODS / f"{name} ({n})"
                    n += 1

                target.mkdir(parents=True, exist_ok=True)
                shutil.copytree(path, target, dirs_exist_ok=True)

            elif path.is_file():
                match path.suffix:
                    case ".zip":
                        try:
                            name = path.with_suffix("").name

                            target = Directory.MODS / name
                            n = 1
                            while target.exists():
                                target = Directory.MODS / f"{name} ({n})"
                                n += 1

                            filesystem.extract(path, target)

                        except SourceNotAFileError as e:
                            messagebox.show_error(Localizer.strings["errors"]["mods"]["import.title"], Localizer.strings["errors"]["mods"]["import.not_found"].replace("{path}", e.path), blocking=False)
                            return

                        except ExtractPermissionError as e:
                            messagebox.show_error(Localizer.strings["errors"]["mods"]["import.title"], Localizer.strings["errors"]["mods"]["import.permission_denied"].replace("{path}", e.path), blocking=False)
                            return

                    case ".ttf":
                        name = f"Custom Font ({path.with_suffix("").name})"

                        target = Directory.MODS / name
                        n = 1
                        while target.exists():
                            target = Directory.MODS / f"{name} ({n})"
                            n += 1

                        target.mkdir(parents=True, exist_ok=True)
                        font_target: Path = target / "content" / "fonts" / "CustomFont.tff"
                        font_target.parent.mkdir(parents=True, exist_ok=True)

                        shutil.copy(path, font_target)

                    case ".otf":
                        name = f"Custom Font ({path.with_suffix("").name})"

                        target = Directory.MODS / name
                        n = 1
                        while target.exists():
                            target = Directory.MODS / f"{name} ({n})"
                            n += 1

                        target.mkdir(parents=True, exist_ok=True)
                        font_target = target / "content" / "fonts" / "CustomFont.otf"
                        font_target.parent.mkdir(parents=True, exist_ok=True)

                        shutil.copy(path, font_target)

                    case _:
                        unsupported_files.append(path.name)

        if unsupported_files: messagebox.show_error(Localizer.strings["errors"]["mods"]["import.title"], Localizer.strings["errors"]["mods"]["import.unsupported_format"].replace("{failed_imports}", ", ".join(unsupported_files)).replace("{supported_formats}", ".zip, .ttf, .otf"), blocking=False)
# endregion
# endregion