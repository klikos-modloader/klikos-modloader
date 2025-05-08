from tkinter import TclError, filedialog, messagebox, StringVar
from pathlib import Path
import re
import shutil
from typing import Literal, Callable, TYPE_CHECKING

from modules.project_data import ProjectData
from modules.frontend.widgets import ScrollableFrame, Frame, Label, Button, Entry, DropDownMenu
from modules.frontend.functions import get_ctk_image
from modules.interfaces.mod_manager import Mod, ModManager
from modules.localization import Localizer
from modules.filesystem import Resources, Directories, EmptyFileNameError, InvalidFileNameError, ReservedFileNameError, TrailingDotError
from modules import filesystem

if TYPE_CHECKING: from modules.frontend.widgets import Root

from customtkinter import CTkImage  # type: ignore


class ModsSection(ScrollableFrame):
    loaded: bool = False
    root: "Root"

    _names: list[str]
    _frames: dict[str, tuple[Mod, Frame]]
    _mod_list: Frame
    _language_change_callback_id: str | None = None

    _SECTION_PADX: int | tuple[int, int] = (8, 4)
    _SECTION_PADY: int | tuple[int, int] = 8
    _BACKGROUND_TASK_INTERVAL: int = 50
    _ENTRY_GAP: int = 4
    _ENTRY_PADDING: tuple[int , int] = (16, 16)
    _ENTRY_INNER_GAP: int = 16


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
        self._run_when_mapped(self._run_background_tasks)


    def _run_when_mapped(self, callback: Callable):
        if not self.winfo_ismapped():
            self.after(self._BACKGROUND_TASK_INTERVAL, self._run_when_mapped, callback)
        else:
            callback()


# region load
    def load(self) -> None:
        if self.loaded: return

        self._names = []
        self._frames = {}

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

        Label(header, "menu.mods.header.title", style="title", autowrap=True).grid(column=0, row=0, sticky="ew")
        Label(header, "menu.mods.header.description", style="caption", autowrap=True).grid(column=0, row=1, sticky="ew")

        button_wrapper: Frame = Frame(header, transparent=True)
        button_wrapper.grid(column=0, row=2, sticky="w", pady=(8, 0))

        folder_image: CTkImage = get_ctk_image(Resources.Common.Light.FOLDER, Resources.Common.Dark.FOLDER, size=24)
        Button(button_wrapper, "menu.mods.header.button.open_mods_folder", secondary=True, image=folder_image, command=self.open_mods_folder).grid(column=0, row=0)


    def _load_content(self, master) -> None:
        wrapper: Frame = Frame(master, transparent=True)
        wrapper.grid_columnconfigure(0, weight=1)
        wrapper.grid_rowconfigure(1, weight=1)
        wrapper.grid(column=0, row=1, sticky="nsew")

        dnd_frame: Frame = Frame(wrapper, height=128, layer=2, dnd_command=self.import_mods, cursor="hand2")
        dnd_frame.grid_columnconfigure(0, weight=1)
        dnd_frame.grid_rowconfigure(0, minsize=128)
        dnd_frame.grid(column=0, row=0, sticky="nsew")
        dnd_label: Label = Label(dnd_frame, "menu.mods.content.dnd_target_frame", style="body_strong", justify="center")
        dnd_label.grid(column=0, row=0, sticky="ew")
        dnd_frame.bind("<ButtonPress-1>", self.show_import_dialog)
        dnd_label.bind("<ButtonPress-1>", self.show_import_dialog)

        self._mod_list = Frame(wrapper, transparent=True)
        self._mod_list.grid_columnconfigure(0, weight=1)
        self._mod_list.grid(column=0, row=1, sticky="nsew", pady=(self._ENTRY_GAP, 0))
# endregion


# region background tasks
    def _run_background_tasks(self) -> None:
        if not self.loaded: return
        self.update_idletasks()
        if not self.winfo_ismapped(): return
        self.after(self._BACKGROUND_TASK_INTERVAL, self._run_background_tasks)

        mods: list[Mod] = ModManager.get_all(sort="name")
        names: list[str] = [mod.name for mod in mods]
        if names == self._names: return
        self._names = names

        for name, (mod, frame) in list(self._frames.items()):
            if mod.name not in names:
                self._frames.pop(name)
                frame.destroy()

        list_mapped: bool = self._mod_list.winfo_ismapped()
        if not names and list_mapped:
            self._mod_list.grid_forget()
            return
        elif not list_mapped: self._mod_list.grid(column=0, row=1, sticky="nsew", pady=(self._ENTRY_GAP, 0))


        for i, mod in enumerate(mods):
            pady = 0 if i == 0 else (self._ENTRY_GAP, 0)

            if mod.name in self._frames:
                mod, frame = self._frames[mod.name]
                if getattr(frame, "_row", None) != i:
                    frame.grid(column=0, row=i, sticky="nsew", pady=pady)
                    frame._row = i  # type: ignore
            
            else:
                frame = Frame(self._mod_list, layer=2)
                frame._row = i  # type: ignore
                frame.grid(column=0, row=i, sticky="nsew", pady=pady)
                self._frames[mod.name] = (mod, frame)
                self.after(10, self._load_mod_frame, frame, mod)
                # self._load_mod_frame(frame, mod)
# endregion


# region mod frame
    def _load_mod_frame(self, frame: Frame, mod: Mod) -> None:
        frame.grid_columnconfigure(0, weight=1)

        wrapper: Frame = Frame(frame, transparent=True)
        wrapper.grid_columnconfigure((1,2), weight=1)
        wrapper.grid(column=0, row=0, sticky="nsew", padx=self._ENTRY_PADDING[0], pady=self._ENTRY_PADDING[1])

        # Delete mod
        image: CTkImage = get_ctk_image(Resources.Common.Light.BIN, Resources.Common.Dark.BIN, 20)
        Button(wrapper, secondary=True, width=32, height=32, image=image, command=lambda mod=mod: self.delete_mod(mod)).grid(column=0, row=0, sticky="ew")

        # Name
        name_entry: Entry = Entry(wrapper, command=lambda event, mod=mod: self.rename_mod(mod, event), on_focus_lost="command", reset_if_empty=True, validate="key", validatecommand=(self.register(lambda value: not re.search(r'[\\/:*?"<>|]', value)), "%P"), width=256)
        name_entry.set(mod.name)
        name_entry.grid(column=1, row=0, padx=(8, 0), sticky="w")

        # Load order
        load_order_frame: Frame = Frame(wrapper, transparent=True)
        load_order_frame.grid(column=2, row=0, padx=(self._ENTRY_INNER_GAP, 0), sticky="w")

        load_order_label: Label = Label(load_order_frame, "menu.mods.content.load_order")
        load_order_label.grid(column=0, row=0, sticky="w", padx=(0, 8))

        load_order_entry: Entry = Entry(load_order_frame, command=lambda event, mod=mod: self.change_load_order(mod, event), on_focus_lost="command", reset_if_empty=True, validate="key", validatecommand=(self.register(lambda value: value.removeprefix("-").isdigit() or value.removeprefix("-") == ""), "%P"), width=32, height=32)
        load_order_entry.set(str(mod.priority))
        load_order_entry.grid(column=1, row=0, sticky="w")

        # Status
        status: int = 3 if mod.player and mod.studio else 2 if mod.studio else 1 if mod.player else 0
        dropdown_string_keys: list[str] = [
            "menu.mods.content.status.dropdown.none",
            "menu.mods.content.status.dropdown.player",
            "menu.mods.content.status.dropdown.studio",
            "menu.mods.content.status.dropdown.both"
        ]
        frame.status_var: StringVar = StringVar(wrapper, value=Localizer.Strings[dropdown_string_keys[status]])  # type: ignore
        DropDownMenu(wrapper, value_keys=dropdown_string_keys, variable=frame.status_var, value_modifications=[  # type: ignore
                None, lambda string: Localizer.format(string, {"{roblox.player}": Localizer.Key("roblox.player"), "{roblox.player_alt}": Localizer.Key("roblox.player_alt")}),
                lambda string: Localizer.format(string, {"{roblox.studio}": Localizer.Key("roblox.studio"), "{roblox.studio_alt}": Localizer.Key("roblox.studio_alt")}), None
            ], command=lambda value, mod=mod: self.change_status(mod, value)
        ).grid(column=3, row=0, sticky="e", padx=(self._ENTRY_INNER_GAP, 0))
# endregion


# region Functions
    def _on_language_change(self) -> None:
        if not self.loaded:
            self.after(100, self._on_language_change)
            return

        for mod, frame in list(self._frames.values()):
            status: int = 3 if mod.player and mod.studio else 2 if mod.studio else 1 if mod.player else 0
            status_dropdown_string_keys: list[str] = [
                "menu.mods.content.status.dropdown.none",
                "menu.mods.content.status.dropdown.player",
                "menu.mods.content.status.dropdown.studio",
                "menu.mods.content.status.dropdown.both"
            ]
            status_var: StringVar | None = getattr(frame, "status_var", None)
            if isinstance(status_var, StringVar): status_var.set(Localizer.format(Localizer.Strings[status_dropdown_string_keys[status]], {
                "{roblox.player}": Localizer.Key("roblox.player"), "{roblox.player_alt}": Localizer.Key("roblox.player_alt"),
                "{roblox.studio}": Localizer.Key("roblox.studio"), "{roblox.studio_alt}": Localizer.Key("roblox.studio_alt")
            }))  # type: ignore


    def open_mods_folder(self) -> None:
        if not Directories.MODS.exists(): Directories.MODS.mkdir(parents=True, exist_ok=True)
        filesystem.open(Directories.MODS)


# region import mods
    def show_import_dialog(self, *_) -> None:
        files: tuple[str, ...] | Literal[''] = filedialog.askopenfilenames(
            initialdir=str(Directories.DOWNLOADS),
            filetypes=(
                (Localizer.Strings["menu.mods.popup.import.filetype.supported"], "*.zip;*.7z;*.ttf;*.otf"),
                (Localizer.Strings["menu.mods.popup.import.filetype.zip"], "*.zip"),
                (Localizer.Strings["menu.mods.popup.import.filetype.7z"], "*.7z"),
                (Localizer.Strings["menu.mods.popup.import.filetype.ttf"], "*.ttf"),
                (Localizer.Strings["menu.mods.popup.import.filetype.otf"], "*.otf")
            ), title=Localizer.format(Localizer.Strings["menu.mods.popup.import.title"], {"{app.name}": ProjectData.NAME})
        )
        if not files: return
        self.import_mods(tuple(Path(path) for path in files))


    def import_mods(self, files_or_directories: tuple[Path, ...]) -> None:
        Directories.MODS.mkdir(parents=True, exist_ok=True)
        for path in files_or_directories:
            path = path.resolve()

            if not path.exists():
                self.root.send_banner(
                    title_key="menu.mods.exception.title.import",
                    title_modification=lambda string: Localizer.format(string, {"{mod.name}": path.stem}),
                    message_key="menu.mods.exception.message.file_not_found",
                    message_modification=lambda string: Localizer.format(string, {"{path}": str(path)}),
                    mode="warning"
                )
                continue

            is_file: bool = path.is_file()
            is_font: bool = is_file and path.suffix in {".ttf", ".otf"}
            target_name: str
            if is_font: target_name = path.name
            else:
                try:
                    mod: Mod = Mod(path)
                    target_name = mod.name
                except ValueError:
                    self.root.send_banner(
                        title_key="menu.mods.exception.title.import",
                        title_modification=lambda string: Localizer.format(string, {"{mod.name}": path.stem}),
                        message_key="menu.mods.exception.message.unsupported_filetype",
                        message_modification=lambda string: Localizer.format(string, {"{filetype}": path.suffix}),
                        mode="warning"
                    )
                    continue

            existing_mods = {path.stem.lower() if path.is_file() else path.name.lower() for path in Directories.MODS.iterdir()}
            if target_name in existing_mods:
                self.root.send_banner(
                    title_key="menu.mods.exception.title.import",
                    title_modification=lambda string: Localizer.format(string, {"{mod.name}": target_name}),
                    message_key="menu.mods.exception.message.mod_exists",
                    mode="warning"
                )
                continue

            try:
                if is_font: self._import_font_mod(path)
                elif mod.archive: filesystem.extract(path, Directories.MODS / mod.name)
                else: shutil.copytree(path, Directories.MODS / mod.name)

            except Exception as e:
                self.root.send_banner(
                    title_key="menu.mods.exception.title.import",
                    title_modification=lambda string: Localizer.format(string, {"{mod.name}": target_name}),
                    message_key="menu.mods.exception.message.unknown",
                    message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                    mode="error"
                )
                continue


    def _import_font_mod(self, path: Path) -> None:
        if path.suffix not in {".ttf", ".otf"}: raise ValueError(f'Unsupported file format: "{path.suffix}". Must be ".ttf", ".otf"')
        mod_path: Path = Directories.MODS / path.name
        target_path: Path = (mod_path / "content" / "fonts" / path.name).with_name("CustomFont").with_suffix(path.suffix)
        shutil.copy(path, target_path)
# endregion


# region delete mod
    def delete_mod(self, mod: Mod) -> None:
        if not messagebox.askokcancel(
            Localizer.format(Localizer.Strings["dialog.confirm.title"], {"{app.name}": ProjectData.NAME}),
            Localizer.format(Localizer.Strings["menu.mods.popup.delete.message"], {"{mod.name}": mod.name})
        ): return
        try: mod.remove()
        except Exception as e:
            self.root.send_banner(
                title_key="menu.mods.exception.title.remove",
                title_modification=lambda string: Localizer.format(string, {"{mod.name}": mod.name}),
                message_key="menu.mods.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                mode="error"
            )
# endregion


# region rename mod
    def rename_mod(self, mod: Mod, event) -> None:
        old_name: str = mod.name
        old_path: Path = mod.path
        new_name: str = event.widget.get().strip()

        try:
            event.widget.set(new_name)
            mod.rename(new_name)
            self._frames[new_name] = self._frames.pop(old_name)

        except EmptyFileNameError:
            event.widget.set(old_name)
            self.root.send_banner(
                title_key="menu.mods.exception.title.rename",
                title_modification=lambda string: Localizer.format(string, {"{mod.name}": old_name}),
                message_key="menu.mods.exception.message.empty_filename",
                mode="warning"
            )

        except FileNotFoundError:  # TODO
            event.widget.set(old_name)
            self.root.send_banner(
                title_key="menu.mods.exception.title.rename",
                title_modification=lambda string: Localizer.format(string, {"{mod.name}": old_name}),
                message_key="menu.mods.exception.file_not_found",
                message_modification=lambda string: Localizer.format(string, {"{path}": str(old_path)}),
                mode="warning"
            )

        except FileExistsError:  # TODO
            event.widget.set(old_name)
            self.root.send_banner(
                title_key="menu.mods.exception.title.rename",
                title_modification=lambda string: Localizer.format(string, {"{mod.name}": old_name}),
                message_key="menu.mods.exception.message.mod_exists",
                mode="warning"
            )

        except ReservedFileNameError:
            event.widget.set(old_name)
            self.root.send_banner(
                title_key="menu.mods.exception.title.rename",
                title_modification=lambda string: Localizer.format(string, {"{mod.name}": old_name}),
                message_key="menu.mods.exception.message.reserved_filename",
                message_modification=lambda string: Localizer.format(string, {"{value}": new_name.upper()}),
                mode="warning"
            )

        except TrailingDotError:
            event.widget.set(old_name)
            self.root.send_banner(
                title_key="menu.mods.exception.title.rename",
                title_modification=lambda string: Localizer.format(string, {"{mod.name}": old_name}),
                message_key="menu.mods.exception.message.trailing_dot_filename",
                mode="warning"
            )

        except InvalidFileNameError:
            event.widget.set(old_name)
            self.root.send_banner(
                title_key="menu.mods.exception.title.rename",
                title_modification=lambda string: Localizer.format(string, {"{mod.name}": old_name}),
                message_key="menu.mods.exception.message.invalid_filename",
                message_modification=lambda string: Localizer.format(string, {"{value}": new_name.upper()}),
                mode="warning"
            )

        except Exception as e:
            event.widget.set(old_name)
            self.root.send_banner(
                title_key="menu.mods.exception.title.rename",
                title_modification=lambda string: Localizer.format(string, {"{mod.name}": old_name}),
                message_key="menu.mods.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                mode="error"
            )
# endregion


# region change load order
    def change_load_order(self, mod: Mod, event) -> None:
        old_value: int = mod.priority
        new_value_string: str = event.widget.get().strip()
        if not new_value_string.removeprefix("-"):
            event.widget.set(str(old_value))
            return
        
        try: new_value: int = int(new_value_string)
        except ValueError as e:
            event.widget.set(old_value)
            self.root.send_banner(
                title_key="menu.mods.exception.title.change_priority",
                title_modification=lambda string: Localizer.format(string, {"{mod.name}": mod.name}),
                message_key="menu.mods.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": "ValueError", "{exception.message}": str(e)}),
                mode="error"
            )

        if old_value == new_value: return
        try: mod.set_priority(new_value)

        except Exception as e:
            event.widget.set(old_value)
            self.root.send_banner(
                title_key="menu.mods.exception.title.change_priority",
                title_modification=lambda string: Localizer.format(string, {"{mod.name}": mod.name}),
                message_key="menu.mods.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                mode="error"
            )
# endregion


# region change status
    def change_status(self, mod: Mod, value: str) -> None:
        none_value: str = Localizer.Strings["menu.mods.content.status.dropdown.none"]
        player_value: str = Localizer.format(Localizer.Strings["menu.mods.content.status.dropdown.player"], {"{roblox.player}": Localizer.Strings["roblox.player"], "{roblox.player_alt}": Localizer.Strings["roblox.player_alt"]})
        studio_value: str = Localizer.format(Localizer.Strings["menu.mods.content.status.dropdown.studio"], {"{roblox.studio}": Localizer.Strings["roblox.studio"], "{roblox.studio_alt}": Localizer.Strings["roblox.studio_alt"]})
        both_value: str = Localizer.Strings["menu.mods.content.status.dropdown.both"]

        if value not in {none_value, player_value, studio_value, both_value}:
            self.root.send_banner(
                title_key="menu.mods.exception.title.change_priority",
                title_modification=lambda string: Localizer.format(string, {"{mod.name}": mod.name}),
                message_key="menu.mods.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": "ValueError", "{exception.message}": f'Bad value: "{value}". Expected one of "{none_value}", "{player_value}", "{studio_value}", "{both_value}"'}),
                mode="error"
            )
            return
        
        old_status: int = 3 if mod.player and mod.studio else 2 if mod.studio else 1 if mod.player else 0
        new_status: int = 3 if value == both_value else 2 if value == studio_value else 1 if value == player_value else 0
        if old_status == new_status: return
        try: mod.set_status(new_status)

        except Exception as e:
            self.root.send_banner(
                title_key="menu.mods.exception.title.change_priority",
                title_modification=lambda string: Localizer.format(string, {"{mod.name}": mod.name}),
                message_key="menu.mods.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                mode="error"
            )
# endregion
# endregion
