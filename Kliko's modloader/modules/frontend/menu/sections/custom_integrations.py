from tkinter import TclError, messagebox, filedialog, StringVar
from pathlib import Path
from typing import Literal, TYPE_CHECKING

from modules.project_data import ProjectData
from modules.interfaces.custom_integrations_manager import CustomIntegration, CustomIntegrationManager
from modules.frontend.widgets import ScrollableFrame, Frame, Label, Button, Entry, DropDownMenu
from modules.frontend.functions import get_ctk_image
from modules.localization import Localizer
from modules.filesystem import Resources, Directories

if TYPE_CHECKING: from modules.frontend.widgets import Root

from customtkinter import CTkImage  # type: ignore


class CustomIntegrationsSection(ScrollableFrame):
    loaded: bool = False
    root: "Root"
    integrations_list: Frame
    _names: list[str]
    _frames: dict[str, Frame]

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
        self.refresh_list()

        self.loaded = True


    def _load_header(self, master) -> None:
        header: Frame = Frame(master, transparent=True)
        header.grid_columnconfigure(0, weight=1)
        header.grid(column=0, row=0, sticky="nsew", pady=(0,16))

        Label(header, "menu.custom_integrations.header.title", style="title", autowrap=True).grid(column=0, row=0, sticky="ew")
        Label(header, "menu.custom_integrations.header.description", style="caption", autowrap=True).grid(column=0, row=1, sticky="ew")

        button_wrapper: Frame = Frame(header, transparent=True)
        button_wrapper.grid(column=0, row=2, sticky="w", pady=(8, 0))

        image: CTkImage = get_ctk_image(Resources.Common.Light.ADD, Resources.Common.Dark.ADD, size=24)
        Button(button_wrapper, "menu.custom_integrations.header.button.add_new", secondary=True, image=image, command=self.add_new).grid(column=0, row=0)


    def _load_content(self, master) -> None:
        self.integrations_list: Frame = Frame(master, transparent=True)
        self.integrations_list.grid_columnconfigure(0, weight=1)
        self.integrations_list.grid_rowconfigure(1, weight=1)
        self.integrations_list.grid(column=0, row=1, sticky="nsew")


    def refresh_list(self) -> None:
        integrations: list[CustomIntegration] = CustomIntegrationManager.get_all(sorted=True)
        names: list[str] = [integration.name for integration in integrations]
        if names == self._names: return
        self._names = names

        for name, frame in list(self._frames.items()):
            if name not in names:
                self._frames.pop(name)
                frame.destroy()

        for i, integration in enumerate(integrations):
            pady = 0 if i == 0 else (self._ENTRY_GAP, 0)

            if integration.name in self._frames:
                frame = self._frames[integration.name]
                if getattr(frame, "_row", None) != i:
                    frame.grid(column=0, row=i, sticky="nsew", pady=pady)
                    frame._row = i  # type: ignore
            
            else:
                frame = Frame(self.integrations_list, layer=2)
                frame._row = i  # type: ignore
                frame.grid(column=0, row=i, sticky="nsew", pady=pady)
                self._frames[integration.name] = frame
                self.after(10, self._load_integration_frame, frame, integration)


# region frame
    def _load_integration_frame(self, frame: Frame, integration: CustomIntegration) -> None:
        frame.grid_columnconfigure(0, weight=1)

        wrapper: Frame = Frame(frame, transparent=True)
        wrapper.grid_columnconfigure(0, weight=1)
        wrapper.grid(column=0, row=0, sticky="nsew", padx=self._ENTRY_PADDING[0], pady=self._ENTRY_PADDING[1])

        # Name
        Label(wrapper, key=integration.name, style="body_strong", autowrap=True, dont_localize=True).grid(column=0, row=0, sticky="ew")

        # Content
        content: Frame = Frame(wrapper, transparent=True)
        content.grid_columnconfigure(1, weight=1)
        content.grid(column=0, row=1, sticky="ew", pady=(8, 0))

        # Delete integration
        image: CTkImage = get_ctk_image(Resources.Common.Light.BIN, Resources.Common.Dark.BIN, 20)
        Button(content, secondary=True, width=32, height=32, image=image, command=lambda integration=integration: self.delete_integration(integration)).grid(column=0, row=0, sticky="ew")

        # Args
        args_entry: Entry = Entry(
            content, command=lambda event, integration=integration: self.reargs_integration(integration, event),
            on_focus_lost="command", run_command_if_empty=True, reset_if_empty=False, placeholder_key="menu.custom_integrations.content.launch_args.placeholder", width=256
        )
        if integration.args:
            args_entry.set(integration.args)
        args_entry.grid(column=1, row=0, padx=(8, 0), sticky="ew")

        # Status
        status: int = 3 if integration.player and integration.studio else 2 if integration.studio else 1 if integration.player else 0
        dropdown_string_keys: list[str] = [
            "menu.custom_integrations.content.status.dropdown.none",
            "menu.custom_integrations.content.status.dropdown.player",
            "menu.custom_integrations.content.status.dropdown.studio",
            "menu.custom_integrations.content.status.dropdown.both"
        ]
        frame.status_var: StringVar = StringVar(content, value=Localizer.Strings[dropdown_string_keys[status]])  # type: ignore
        DropDownMenu(content, value_keys=dropdown_string_keys, variable=frame.status_var, value_modifications=[  # type: ignore
                None, lambda string: Localizer.format(string, {"{roblox.player}": Localizer.Key("roblox.player"), "{roblox.player_alt}": Localizer.Key("roblox.player_alt")}),
                lambda string: Localizer.format(string, {"{roblox.studio}": Localizer.Key("roblox.studio"), "{roblox.studio_alt}": Localizer.Key("roblox.studio_alt")}), None
            ], command=lambda value, integration=integration: self.change_status(integration, value)
        ).grid(column=2, row=0, sticky="e", padx=(self._ENTRY_INNER_GAP, 0))
# endregion
# endregion


# region functions
    def add_new(self) -> None:
        files: tuple[str, ...] | Literal[''] = filedialog.askopenfilenames(
            initialdir=str(Directories.DOWNLOADS),
            title=Localizer.format(Localizer.Strings["menu.custom_integrations.popup.add.title"], {"{app.name}": ProjectData.NAME})
        )
        if not files: return

        for file in files:
            path: Path = Path(file).resolve()
            if not path.exists():
                self.root.send_banner(
                    title_key="menu.custom_integrations.exception.title.add",
                    title_modification=lambda string: Localizer.format(string, {"{integration.name}": path.name}),
                    message_key="menu.custom_integrations.exception.message.file_not_found",
                    message_modification=lambda string: Localizer.format(string, {"{path}": str(path)}),
                    mode="warning", auto_close_after_ms=6000
                )
                continue

            existing_integrations = {str(integration.path).lower() for integration in CustomIntegrationManager.get_all()}
            if str(path).lower() in existing_integrations:
                self.root.send_banner(
                    title_key="menu.custom_integrations.exception.title.add",
                    title_modification=lambda string: Localizer.format(string, {"{integration.name}": path.name}),
                    message_key="menu.custom_integrations.exception.message.already_exists",
                    mode="warning", auto_close_after_ms=6000
                )
                continue

            try:
                CustomIntegrationManager.update_config(CustomIntegration(path))
            except Exception as e:
                self.root.send_banner(
                    title_key="menu.custom_integrations.exception.title.add",
                    title_modification=lambda string: Localizer.format(string, {"{integration.name}": path.name}),
                    message_key="menu.custom_integrations.exception.message.unknown",
                    message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                    mode="error", auto_close_after_ms=6000
                )
                continue

        self.refresh_list()


    def delete_integration(self, integration: CustomIntegration) -> None:
        if not messagebox.askokcancel(
            Localizer.format(Localizer.Strings["dialog.confirm.title"], {"{app.name}": ProjectData.NAME}),
            Localizer.format(Localizer.Strings["menu.custom_integrations.popup.delete.message"], {"{integration.name}": integration.name})
        ): return
        try: integration.remove()
        except Exception as e:
            self.root.send_banner(
                title_key="menu.custom_integrations.exception.title.remove",
                title_modification=lambda string: Localizer.format(string, {"{integration.name}": integration.name}),
                message_key="menu.custom_integrations.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                mode="error", auto_close_after_ms=6000
            )
        else:
            self.refresh_list()


    def reargs_integration(self, integration: CustomIntegration, event) -> None:
        old_args: str = integration.args
        new_args: str = event.widget.get().strip()

        try:
            event.widget.set(new_args)
            integration.set_args(new_args)

        except Exception as e:
            event.widget.set(old_args)
            self.root.send_banner(
                title_key="menu.custom_integrations.exception.title.update",
                title_modification=lambda string: Localizer.format(string, {"{integration.name}": integration.name}),
                message_key="menu.custom_integrations.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                mode="error", auto_close_after_ms=6000
            )


    def change_status(self, integration: CustomIntegration, value) -> None:
        none_value: str = Localizer.Strings["menu.custom_integrations.content.status.dropdown.none"]
        player_value: str = Localizer.format(Localizer.Strings["menu.custom_integrations.content.status.dropdown.player"], {"{roblox.player}": Localizer.Strings["roblox.player"], "{roblox.player_alt}": Localizer.Strings["roblox.player_alt"]})
        studio_value: str = Localizer.format(Localizer.Strings["menu.custom_integrations.content.status.dropdown.studio"], {"{roblox.studio}": Localizer.Strings["roblox.studio"], "{roblox.studio_alt}": Localizer.Strings["roblox.studio_alt"]})
        both_value: str = Localizer.Strings["menu.custom_integrations.content.status.dropdown.both"]

        if value not in {none_value, player_value, studio_value, both_value}:
            self.root.send_banner(
                title_key="menu.custom_integrations.exception.title.change_status",
                title_modification=lambda string: Localizer.format(string, {"{integration.name}": integration.name}),
                message_key="menu.custom_integrations.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": "ValueError", "{exception.message}": f'Bad value: "{value}". Expected one of "{none_value}", "{player_value}", "{studio_value}", "{both_value}"'}),
                mode="error", auto_close_after_ms=6000
            )
            return
        
        old_status: int = 3 if integration.player and integration.studio else 2 if integration.studio else 1 if integration.player else 0
        new_status: int = 3 if value == both_value else 2 if value == studio_value else 1 if value == player_value else 0
        if old_status == new_status: return
        try: integration.set_status(new_status)

        except Exception as e:
            self.root.send_banner(
                title_key="menu.custom_integrations.exception.title.change_status",
                title_modification=lambda string: Localizer.format(string, {"{integration.name}": integration.name}),
                message_key="menu.custom_integrations.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                mode="error", auto_close_after_ms=6000
            )
# endregion