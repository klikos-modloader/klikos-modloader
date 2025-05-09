from tkinter import TclError, BooleanVar
from typing import Optional, Callable, TYPE_CHECKING

from modules.frontend.widgets import ScrollableFrame, Frame, Label, ToggleSwitch
from modules.localization import Localizer
from modules.interfaces.config import ConfigInterface

if TYPE_CHECKING: from modules.frontend.widgets import Root


class IntegrationsSection(ScrollableFrame):
    loaded: bool = False
    root: "Root"

    _SECTION_PADX: int | tuple[int, int] = (8, 4)
    _SECTION_PADY: int | tuple[int, int] = 8

    _ENTRY_GAP: int = 8
    _ENTRY_PADDING: tuple[int, int] = (16, 16)
    _ENTRY_INNER_GAP: int = 8


    def __init__(self, master):
        super().__init__(master, transparent=False, round=True, border=True, layer=1)
        self.root = master
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


    def destroy(self):
        return super().destroy()


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

        Label(header, "menu.integrations.header.title", style="title", autowrap=True).grid(column=0, row=0, sticky="ew")
        Label(header, "menu.integrations.header.description", style="caption", autowrap=True).grid(column=0, row=1, sticky="ew")


    def _load_content(self, master) -> None:
        wrapper: Frame = Frame(master, transparent=True)
        wrapper.grid_columnconfigure(0, weight=1)
        wrapper.grid_rowconfigure(1, weight=1)
        wrapper.grid(column=0, row=1, sticky="nsew")
        row_counter: int = -1


        # Mod updates
        row_counter += 1
        frame = Frame(wrapper, layer=2)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid(column=0, row=row_counter, sticky="nsew", pady=0 if row_counter == 0 else (self._ENTRY_GAP, 0))
        Label(frame, "menu.integrations.content.mod_updates.title", style="body_strong", autowrap=True).grid(column=0, row=0, sticky="sew", pady=(self._ENTRY_PADDING[1], 0), padx=(self._ENTRY_PADDING[0], 0))
        Label(frame, "menu.integrations.content.mod_updates.description", style="caption", autowrap=True).grid(column=0, row=1, sticky="new", pady=(0, self._ENTRY_PADDING[1]), padx=(self._ENTRY_PADDING[0], 0))
        value: bool = ConfigInterface.get("mod_updates")
        switch_var: BooleanVar = BooleanVar(value=value)
        ToggleSwitch(frame, variable=switch_var, command=lambda var=switch_var: self._update_boolean_setting("mod_updates", var.get(), "menu.integrations.content.mod_updates.title")).grid(column=1, row=0, rowspan=2, sticky="e", pady=self._ENTRY_PADDING[1], padx=(self._ENTRY_INNER_GAP, self._ENTRY_PADDING[0]))


        # Multi-Instance Launching
        row_counter += 1
        frame = Frame(wrapper, layer=2)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid(column=0, row=row_counter, sticky="nsew", pady=0 if row_counter == 0 else (self._ENTRY_GAP, 0))
        Label(frame, "menu.integrations.content.multi_instance_launching.title", style="body_strong", autowrap=True).grid(column=0, row=0, sticky="sew", pady=(self._ENTRY_PADDING[1], 0), padx=(self._ENTRY_PADDING[0], 0))
        Label(frame, "menu.integrations.content.multi_instance_launching.description", lambda string: Localizer.format(string, {"{roblox.common}": Localizer.Key("roblox.common")}), style="caption", autowrap=True).grid(column=0, row=1, sticky="new", pady=(0, self._ENTRY_PADDING[1]), padx=(self._ENTRY_PADDING[0], 0))
        value = ConfigInterface.get("multi_instance_launching")
        switch_var = BooleanVar(value=value)
        ToggleSwitch(frame, variable=switch_var, command=lambda var=switch_var: self._update_boolean_setting("multi_instance_launching", var.get(), "menu.integrations.content.multi_instance_launching.title")).grid(column=1, row=0, rowspan=2, sticky="e", pady=self._ENTRY_PADDING[1], padx=(self._ENTRY_INNER_GAP, self._ENTRY_PADDING[0]))


        # Discord RPC
        row_counter += 1
        frame = Frame(wrapper, layer=2)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid(column=0, row=row_counter, sticky="nsew", pady=0 if row_counter == 0 else (self._ENTRY_GAP, 0))
        Label(frame, "menu.integrations.content.discord_rpc.title", style="body_strong", autowrap=True).grid(column=0, row=0, sticky="sew", pady=(self._ENTRY_PADDING[1], 0), padx=(self._ENTRY_PADDING[0], 0))
        Label(frame, "menu.integrations.content.discord_rpc.description", style="caption", autowrap=True).grid(column=0, row=1, sticky="new", pady=(0, self._ENTRY_PADDING[1]), padx=(self._ENTRY_PADDING[0], 0))
        value = ConfigInterface.get("discord_rpc")
        switch_var = BooleanVar(value=value)
        ToggleSwitch(frame, variable=switch_var, command=lambda var=switch_var: self._update_boolean_setting("discord_rpc", var.get(), "menu.integrations.content.discord_rpc.title")).grid(column=1, row=0, rowspan=2, sticky="e", pady=self._ENTRY_PADDING[1], padx=(self._ENTRY_INNER_GAP, self._ENTRY_PADDING[0]))


        # Bloxstrap RPC
        row_counter += 1
        frame = Frame(wrapper, layer=2)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid(column=0, row=row_counter, sticky="nsew", pady=0 if row_counter == 0 else (self._ENTRY_GAP, 0))
        Label(frame, "menu.integrations.content.activity_joining.title", style="body_strong", autowrap=True).grid(column=0, row=0, sticky="sew", pady=(self._ENTRY_PADDING[1], 0), padx=(self._ENTRY_PADDING[0], 0))
        Label(frame, "menu.integrations.content.activity_joining.description", style="caption", autowrap=True).grid(column=0, row=1, sticky="new", pady=(0, self._ENTRY_PADDING[1]), padx=(self._ENTRY_PADDING[0], 0))
        value = ConfigInterface.get("activity_joining")
        switch_var = BooleanVar(value=value)
        ToggleSwitch(frame, variable=switch_var, command=lambda var=switch_var: self._update_boolean_setting("activity_joining", var.get(), "menu.integrations.content.activity_joining.title")).grid(column=1, row=0, rowspan=2, sticky="e", pady=self._ENTRY_PADDING[1], padx=(self._ENTRY_INNER_GAP, self._ENTRY_PADDING[0]))


        # Activity joining
        row_counter += 1
        frame = Frame(wrapper, layer=2)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid(column=0, row=row_counter, sticky="nsew", pady=0 if row_counter == 0 else (self._ENTRY_GAP, 0))
        Label(frame, "menu.integrations.content.show_user_in_rpc.title", style="body_strong", autowrap=True).grid(column=0, row=0, sticky="sew", pady=(self._ENTRY_PADDING[1], 0), padx=(self._ENTRY_PADDING[0], 0))
        Label(frame, "menu.integrations.content.show_user_in_rpc.description", style="caption", autowrap=True).grid(column=0, row=1, sticky="new", pady=(0, self._ENTRY_PADDING[1]), padx=(self._ENTRY_PADDING[0], 0))
        value = ConfigInterface.get("show_user_in_rpc")
        switch_var = BooleanVar(value=value)
        ToggleSwitch(frame, variable=switch_var, command=lambda var=switch_var: self._update_boolean_setting("show_user_in_rpc", var.get(), "menu.integrations.content.show_user_in_rpc.title")).grid(column=1, row=0, rowspan=2, sticky="e", pady=self._ENTRY_PADDING[1], padx=(self._ENTRY_INNER_GAP, self._ENTRY_PADDING[0]))


        # Profile in RPC
        row_counter += 1
        frame = Frame(wrapper, layer=2)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid(column=0, row=row_counter, sticky="nsew", pady=0 if row_counter == 0 else (self._ENTRY_GAP, 0))
        Label(frame, "menu.integrations.content.bloxstrap_rpc_sdk.title", style="body_strong", autowrap=True).grid(column=0, row=0, sticky="sew", pady=(self._ENTRY_PADDING[1], 0), padx=(self._ENTRY_PADDING[0], 0))
        Label(frame, "menu.integrations.content.bloxstrap_rpc_sdk.description", style="caption", autowrap=True).grid(column=0, row=1, sticky="new", pady=(0, self._ENTRY_PADDING[1]), padx=(self._ENTRY_PADDING[0], 0))
        value = ConfigInterface.get("bloxstrap_rpc_sdk")
        switch_var = BooleanVar(value=value)
        ToggleSwitch(frame, variable=switch_var, command=lambda var=switch_var: self._update_boolean_setting("bloxstrap_rpc_sdk", var.get(), "menu.integrations.content.bloxstrap_rpc_sdk.title")).grid(column=1, row=0, rowspan=2, sticky="e", pady=self._ENTRY_PADDING[1], padx=(self._ENTRY_INNER_GAP, self._ENTRY_PADDING[0]))
# endregion


# region functions
    def _update_boolean_setting(self, key: str, value: bool, localizer_name_key: Optional[str] = None, localizer_name_modification: Optional[Callable[[str], str]] = None) -> None:
        if not localizer_name_key: name: str = key
        else:
            name = Localizer.Strings[localizer_name_key]
            if callable(localizer_name_modification): name = localizer_name_modification(name)

        try: ConfigInterface.set(key, value)

        except Exception as e:
            self.root.send_banner(
                title_key="menu.integrations.exception.title",
                title_modification=lambda string: Localizer.format(string, {"{setting.name}": name}),
                message_key="menu.integrations.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                mode="error"
            )
# endregion