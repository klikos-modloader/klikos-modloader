from tkinter import TclError, messagebox, StringVar
from typing import TYPE_CHECKING

from modules.project_data import ProjectData
from modules.interfaces.fastflag_manager import FastFlagProfile, FastFlagManager
from modules.frontend.widgets import ScrollableFrame, Frame, Label, Button, Entry, InputDialog, DropDownMenu
if TYPE_CHECKING: from modules.frontend.widgets import Root
from modules.frontend.functions import get_ctk_image
from modules.localization import Localizer
from modules.filesystem import Resources

from ..windows import FastFlagEditorWindow

from customtkinter import CTkImage  # type: ignore


class FastFlagsSection(ScrollableFrame):
    loaded: bool = False
    root: "Root"
    profile_list: Frame
    _names: list[str]
    _frames: dict[str, tuple[FastFlagProfile, Frame]]
    _language_change_callback_id: str | None = None

    _SECTION_PADX: int | tuple[int, int] = (8, 4)
    _SECTION_PADY: int | tuple[int, int] = 8
    _ENTRY_GAP: int = 4
    _ENTRY_PADDING: tuple[int , int] = (16, 16)
    _ENTRY_INNER_GAP: int = 16


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
        self.refresh_list()


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

        self.refresh_list()

        self.loaded = True


    def _load_header(self, master) -> None:
        header: Frame = Frame(master, transparent=True)
        header.grid_columnconfigure(0, weight=1)
        header.grid(column=0, row=0, sticky="nsew", pady=(0,16))

        Label(header, "menu.fastflags.header.title", lambda string: Localizer.format(string, {"{roblox.common}": Localizer.Key("roblox.common"), "{roblox.player}": Localizer.Key("roblox.player"), "{roblox.player_alt}": Localizer.Key("roblox.player_alt"), "{roblox.studio}": Localizer.Key("roblox.studio"), "{roblox.studio_alt}": Localizer.Key("roblox.studio_alt")}), style="title", autowrap=True).grid(column=0, row=0, sticky="ew")
        Label(header, "menu.fastflags.header.description", lambda string: Localizer.format(string, {"{roblox.common}": Localizer.Key("roblox.common")}), style="caption", autowrap=True).grid(column=0, row=1, sticky="ew")

        button_wrapper: Frame = Frame(header, transparent=True)
        button_wrapper.grid(column=0, row=2, sticky="w", pady=(8, 0))

        image: CTkImage = get_ctk_image(Resources.Common.Light.ADD, Resources.Common.Dark.ADD, size=24)
        Button(button_wrapper, "menu.fastflags.header.button.new_profile", secondary=True, image=image, command=self.create_profile).grid(column=0, row=0)


    def _load_content(self, master) -> None:
        self.profile_list: Frame = Frame(master, transparent=True)
        self.profile_list.grid_columnconfigure(0, weight=1)
        self.profile_list.grid_rowconfigure(1, weight=1)
        self.profile_list.grid(column=0, row=1, sticky="nsew")


    def refresh_list(self) -> None:
        profiles: list[FastFlagProfile] = FastFlagManager.get_all(sorted=True)
        names: list[str] = [profile.name for profile in profiles]
        if names == self._names: return
        self._names = names

        for name, (_, frame) in list(self._frames.items()):
            if name not in names:
                self._frames.pop(name)
                frame.destroy()

        for i, profile in enumerate(profiles):
            pady = 0 if i == 0 else (self._ENTRY_GAP, 0)

            if profile.name in self._frames:
                _, frame = self._frames[profile.name]
                if getattr(frame, "_row", None) != i:
                    frame.grid(column=0, row=i, sticky="nsew", pady=pady)
                    frame._row = i  # type: ignore
            
            else:
                frame = Frame(self.profile_list, layer=2)
                frame._row = i  # type: ignore
                frame.grid(column=0, row=i, sticky="nsew", pady=pady)
                self._frames[profile.name] = (profile, frame)
                self.after(10, self._load_profile_frame, frame, profile)


# region frame
    def _load_profile_frame(self, frame: Frame, profile: FastFlagProfile) -> None:
        frame.grid_columnconfigure(0, weight=1)

        wrapper: Frame = Frame(frame, transparent=True)
        wrapper.grid_columnconfigure(2, weight=1)
        wrapper.grid(column=0, row=0, sticky="nsew", padx=self._ENTRY_PADDING[0], pady=self._ENTRY_PADDING[1])

        # Delete profile
        image: CTkImage = get_ctk_image(Resources.Common.Light.BIN, Resources.Common.Dark.BIN, 20)
        Button(wrapper, secondary=True, width=32, height=32, image=image, command=lambda profile=profile: self.delete_profile(profile)).grid(column=0, row=0, sticky="ew")

        # Name
        name_entry: Entry = Entry(
            wrapper, command=lambda event, profile=profile: self.rename_profile(profile, event),
            on_focus_lost="command", reset_if_empty=True, width=256
        )
        name_entry.set(profile.name)
        name_entry.grid(column=1, row=0, padx=(8, 0), sticky="w")

        # Configure
        image = get_ctk_image(Resources.Common.Light.CONFIGURE, Resources.Common.Dark.CONFIGURE, 20)
        Button(wrapper, "menu.fastflags.content.configure", secondary=True, height=32, image=image, command=lambda profile=profile: self.configure_profile(profile)).grid(column=2, row=0, padx=(self._ENTRY_INNER_GAP, 0))

        # Status
        status: int = 3 if profile.player and profile.studio else 2 if profile.studio else 1 if profile.player else 0
        dropdown_string_keys: list[str] = [
            "menu.fastflags.content.status.dropdown.none",
            "menu.fastflags.content.status.dropdown.player",
            "menu.fastflags.content.status.dropdown.studio",
            "menu.fastflags.content.status.dropdown.both"
        ]
        frame.status_var: StringVar = StringVar(wrapper, value=Localizer.format(Localizer.Strings[dropdown_string_keys[status]], {  # type: ignore
            "{roblox.player}": Localizer.Key("roblox.player"), "{roblox.player_alt}": Localizer.Key("roblox.player_alt"),
            "{roblox.studio}": Localizer.Key("roblox.studio"), "{roblox.studio_alt}": Localizer.Key("roblox.studio_alt"),
        }))
        DropDownMenu(wrapper, value_keys=dropdown_string_keys, variable=frame.status_var, value_modifications=[  # type: ignore
                None, lambda string: Localizer.format(string, {"{roblox.player}": Localizer.Key("roblox.player"), "{roblox.player_alt}": Localizer.Key("roblox.player_alt")}),
                lambda string: Localizer.format(string, {"{roblox.studio}": Localizer.Key("roblox.studio"), "{roblox.studio_alt}": Localizer.Key("roblox.studio_alt")}), None
            ], command=lambda value, profile=profile: self.change_status(profile, value)
        ).grid(column=3, row=0, sticky="e", padx=(self._ENTRY_INNER_GAP, 0))
# endregion
# endregion


# region functions
    def _on_language_change(self) -> None:
        if not self.loaded:
            self.after(100, self._on_language_change)
            return

        for profile, frame in list(self._frames.values()):
            status: int = 3 if profile.player and profile.studio else 2 if profile.studio else 1 if profile.player else 0
            status_dropdown_string_keys: list[str] = [
                "menu.fastflags.content.status.dropdown.none",
                "menu.fastflags.content.status.dropdown.player",
                "menu.fastflags.content.status.dropdown.studio",
                "menu.fastflags.content.status.dropdown.both"
            ]
            status_var: StringVar | None = getattr(frame, "status_var", None)
            if isinstance(status_var, StringVar): status_var.set(Localizer.format(Localizer.Strings[status_dropdown_string_keys[status]], {
                "{roblox.player}": Localizer.Key("roblox.player"), "{roblox.player_alt}": Localizer.Key("roblox.player_alt"),
                "{roblox.studio}": Localizer.Key("roblox.studio"), "{roblox.studio_alt}": Localizer.Key("roblox.studio_alt")
            }))  # type: ignore


    def create_profile(self) -> None:
        response: str | None = InputDialog(ProjectData.NAME, Resources.FAVICON, "menu.fastflags.input.new_profile.message", master=self.root).get_input()
        if not response: return

        response = response.strip()
        existing_profiles = {profile.name.lower() for profile in FastFlagManager.get_all()}
        if response.lower() in existing_profiles:
            self.root.send_banner(
                title_key="menu.fastflags.exception.title.create",
                title_modification=lambda string: Localizer.format(string, {"{profile.name}": response}),
                message_key="menu.fastflags.exception.message.profile_exists",
                mode="warning", auto_close_after_ms=6000
            )
            return

        try:
            FastFlagManager.update_config(FastFlagProfile(response))
        except Exception as e:
            self.root.send_banner(
                title_key="menu.fastflags.exception.title.create",
                title_modification=lambda string: Localizer.format(string, {"{profile.name}": response}),
                message_key="menu.fastflags.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                mode="error", auto_close_after_ms=6000
            )
        else:
            self.refresh_list()


    def delete_profile(self, profile: FastFlagProfile) -> None:
        if not messagebox.askokcancel(
            Localizer.format(Localizer.Strings["dialog.confirm.title"], {"{app.name}": ProjectData.NAME}),
            Localizer.format(Localizer.Strings["menu.fastflags.popup.delete.message"], {"{profile.name}": profile.name})
        ): return
        try: profile.remove()
        except Exception as e:
            self.root.send_banner(
                title_key="menu.fastflags.exception.title.remove",
                title_modification=lambda string: Localizer.format(string, {"{profile.name}": profile.name}),
                message_key="menu.fastflags.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                mode="error", auto_close_after_ms=6000
            )
        else:
            self.refresh_list()


    def rename_profile(self, profile: FastFlagProfile, event) -> None:
        old_name: str = profile.name
        new_name: str = event.widget.get().strip()

        try:
            event.widget.set(new_name)
            profile.rename(new_name)
            self._frames[new_name] = self._frames.pop(old_name)

        except FileExistsError:
            event.widget.set(old_name)
            self.root.send_banner(
                title_key="menu.fastflags.exception.title.rename",
                title_modification=lambda string: Localizer.format(string, {"{profile.name}": old_name}),
                message_key="menu.fastflags.exception.message.profile_exists",
                mode="warning", auto_close_after_ms=6000
            )

        except Exception as e:
            event.widget.set(old_name)
            self.root.send_banner(
                title_key="menu.fastflags.exception.title.rename",
                title_modification=lambda string: Localizer.format(string, {"{profile.name}": old_name}),
                message_key="menu.fastflags.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                mode="error", auto_close_after_ms=6000
            )
        
        else:
            self.refresh_list()


    def change_status(self, profile: FastFlagProfile, value) -> None:
        none_value: str = Localizer.Strings["menu.fastflags.content.status.dropdown.none"]
        player_value: str = Localizer.format(Localizer.Strings["menu.fastflags.content.status.dropdown.player"], {"{roblox.player}": Localizer.Strings["roblox.player"], "{roblox.player_alt}": Localizer.Strings["roblox.player_alt"]})
        studio_value: str = Localizer.format(Localizer.Strings["menu.fastflags.content.status.dropdown.studio"], {"{roblox.studio}": Localizer.Strings["roblox.studio"], "{roblox.studio_alt}": Localizer.Strings["roblox.studio_alt"]})
        both_value: str = Localizer.Strings["menu.fastflags.content.status.dropdown.both"]

        if value not in {none_value, player_value, studio_value, both_value}:
            self.root.send_banner(
                title_key="menu.fastflags.exception.title.change_status",
                title_modification=lambda string: Localizer.format(string, {"{profile.name}": profile.name}),
                message_key="menu.fastflags.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": "ValueError", "{exception.message}": f'Bad value: "{value}". Expected one of "{none_value}", "{player_value}", "{studio_value}", "{both_value}"'}),
                mode="error", auto_close_after_ms=6000
            )
            return
        
        old_status: int = 3 if profile.player and profile.studio else 2 if profile.studio else 1 if profile.player else 0
        new_status: int = 3 if value == both_value else 2 if value == studio_value else 1 if value == player_value else 0
        if old_status == new_status: return
        try: profile.set_status(new_status)

        except Exception as e:
            self.root.send_banner(
                title_key="menu.fastflags.exception.title.change_status",
                title_modification=lambda string: Localizer.format(string, {"{profile.name}": profile.name}),
                message_key="menu.fastflags.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                mode="error", auto_close_after_ms=6000
            )
# endregion


# region configure profile
    def configure_profile(self, profile: FastFlagProfile) -> None:
        FastFlagEditorWindow(self.root, profile)
# endregion