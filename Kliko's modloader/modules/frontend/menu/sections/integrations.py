from pathlib import Path

from modules.info import NAME
from modules.localization import Localizer
from modules.core.config_editor import ConfigEditor
from modules.frontend.widgets.fluent import FluentLabel, FluentToolTipButton, FluentFrame, FluentToggleSwitch, get_root_instance

import customtkinter as ctk  # type: ignore
from PIL import Image  # type: ignore


class IntegrationsSection:
    PADDING_X: int = 16
    PADDING_Y: int = 16
    ENTRY_GAP: int = 12
    ENTRY_PADX: int = 16
    ENTRY_PADY: int = 16
    ENTRY_INNER_GAP: int = 16
    ENTRY_TITLE_FONT_SIZE: int = 14
    ENTRY_DESCRIPTION_FONT_SIZE: int = 12

    resources: Path

    master: ctk.CTkFrame
    content: ctk.CTkFrame | ctk.CTkScrollableFrame
    tooltip_button: FluentToolTipButton

    active: bool = False
    first_load: bool = True


    def __init__(self, root: ctk.CTk, master: ctk.CTkFrame | ctk.CTkScrollableFrame, resources: Path) -> None:
        self.root = root
        self.master = master
        self.resources = resources


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

        FluentLabel(title_row, Localizer.strings["menu.integrations"]["title"], font_size=28, font_weight="bold").grid(column=0, row=0, sticky="w")
        self.tooltip_button = FluentToolTipButton(get_root_instance(), master=title_row, wraplength=400, tooltip_title=Localizer.strings["menu.integrations"]["tooltip.title"], tooltip_message=Localizer.strings["menu.integrations"]["tooltip.message"], tooltip_orientation="down", toplevel=True)
        self.tooltip_button.grid(column=1, row=0, padx=(8,0), sticky="w")

        return frame


# region Integrations
    def _get_content(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.content, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)

        (
            mod_updater,
            multi_roblox,
            discord_rpc,
            bloxstrap_rpc,
            activity_joining,
            show_user_profile
        )  = ConfigEditor.get_values(
            "mod_updater",
            "multi_roblox",
            "discord_rpc",
            "bloxstrap_rpc",
            "activity_joining",
            "show_user_profile"
        )

        row: int = 0

        # region Mod updates

        setting_frame = FluentFrame(frame)
        setting_frame.grid_columnconfigure(0, weight=1)
        FluentLabel(setting_frame, Localizer.strings["menu.integrations"]["mod_updater.title"], font_size=self.ENTRY_TITLE_FONT_SIZE, font_weight="bold").grid(column=0, row=0, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(self.ENTRY_PADY, 0))
        FluentLabel(setting_frame, Localizer.strings["menu.integrations"]["mod_updater.description"].replace("{project_name}", NAME), font_size=self.ENTRY_DESCRIPTION_FONT_SIZE).grid(column=0, row=1, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(0, self.ENTRY_PADY))
        FluentToggleSwitch(setting_frame, command=lambda value, key="mod_updater": self._update_boolean_value(key, value)).grid(column=1, row=0, rowspan=2, padx=(0, self.ENTRY_PADX*2), pady=self.ENTRY_PADY)
        setting_frame.grid(column=0, row=row, sticky="nsew", pady=(self.ENTRY_GAP, 0))

        # endregion

        row += 1

        # region Multi-Instace Launching
        
        setting_frame = FluentFrame(frame)
        setting_frame.grid_columnconfigure(0, weight=1)
        FluentLabel(setting_frame, Localizer.strings["menu.integrations"]["multi_roblox.title"], font_size=self.ENTRY_TITLE_FONT_SIZE, font_weight="bold").grid(column=0, row=0, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(self.ENTRY_PADY, 0))
        FluentLabel(setting_frame, Localizer.strings["menu.integrations"]["multi_roblox.description"], font_size=self.ENTRY_DESCRIPTION_FONT_SIZE).grid(column=0, row=1, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(0, self.ENTRY_PADY))
        FluentToggleSwitch(setting_frame, command=lambda value, key="multi_roblox": self._update_boolean_value(key, value)).grid(column=1, row=0, rowspan=2, padx=(0, self.ENTRY_PADX*2), pady=self.ENTRY_PADY)
        setting_frame.grid(column=0, row=row, sticky="nsew", pady=(self.ENTRY_GAP, 0))
        
        # endregion

        row += 1

        # region Discord RPC
        
        setting_frame = FluentFrame(frame)
        setting_frame.grid_columnconfigure(0, weight=1)
        FluentLabel(setting_frame, Localizer.strings["menu.integrations"]["discord_rpc.title"], font_size=self.ENTRY_TITLE_FONT_SIZE, font_weight="bold").grid(column=0, row=0, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(self.ENTRY_PADY, 0))
        FluentLabel(setting_frame, Localizer.strings["menu.integrations"]["discord_rpc.description"], font_size=self.ENTRY_DESCRIPTION_FONT_SIZE).grid(column=0, row=1, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(0, self.ENTRY_PADY))
        FluentToggleSwitch(setting_frame, command=lambda value, key="discord_rpc": self._update_boolean_value(key, value)).grid(column=1, row=0, rowspan=2, padx=(0, self.ENTRY_PADX*2), pady=self.ENTRY_PADY)
        setting_frame.grid(column=0, row=row, sticky="nsew", pady=(self.ENTRY_GAP, 0))
        
        # endregion

        row += 1

        # region BloxstrapRPC SDK
        
        setting_frame = FluentFrame(frame)
        setting_frame.grid_columnconfigure(0, weight=1)
        FluentLabel(setting_frame, Localizer.strings["menu.integrations"]["bloxstrap_rpc.title"], font_size=self.ENTRY_TITLE_FONT_SIZE, font_weight="bold").grid(column=0, row=0, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(self.ENTRY_PADY, 0))
        FluentLabel(setting_frame, Localizer.strings["menu.integrations"]["bloxstrap_rpc.description"], font_size=self.ENTRY_DESCRIPTION_FONT_SIZE).grid(column=0, row=1, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(0, self.ENTRY_PADY))
        FluentToggleSwitch(setting_frame, command=lambda value, key="bloxstrap_rpc": self._update_boolean_value(key, value)).grid(column=1, row=0, rowspan=2, padx=(0, self.ENTRY_PADX*2), pady=self.ENTRY_PADY)
        setting_frame.grid(column=0, row=row, sticky="nsew", pady=(self.ENTRY_GAP, 0))
        
        # endregion

        row += 1

        # region Activity Joining
        
        setting_frame = FluentFrame(frame)
        setting_frame.grid_columnconfigure(0, weight=1)
        FluentLabel(setting_frame, Localizer.strings["menu.integrations"]["activity_joining.title"], font_size=self.ENTRY_TITLE_FONT_SIZE, font_weight="bold").grid(column=0, row=0, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(self.ENTRY_PADY, 0))
        FluentLabel(setting_frame, Localizer.strings["menu.integrations"]["activity_joining.description"], font_size=self.ENTRY_DESCRIPTION_FONT_SIZE).grid(column=0, row=1, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(0, self.ENTRY_PADY))
        FluentToggleSwitch(setting_frame, command=lambda value, key="activity_joining": self._update_boolean_value(key, value)).grid(column=1, row=0, rowspan=2, padx=(0, self.ENTRY_PADX*2), pady=self.ENTRY_PADY)
        setting_frame.grid(column=0, row=row, sticky="nsew", pady=(self.ENTRY_GAP, 0))
        
        # endregion

        row += 1

        # region User Profile in RPC
        
        setting_frame = FluentFrame(frame)
        setting_frame.grid_columnconfigure(0, weight=1)
        FluentLabel(setting_frame, Localizer.strings["menu.integrations"]["show_user_profile.title"], font_size=self.ENTRY_TITLE_FONT_SIZE, font_weight="bold").grid(column=0, row=0, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(self.ENTRY_PADY, 0))
        FluentLabel(setting_frame, Localizer.strings["menu.integrations"]["show_user_profile.description"], font_size=self.ENTRY_DESCRIPTION_FONT_SIZE).grid(column=0, row=1, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(0, self.ENTRY_PADY))
        FluentToggleSwitch(setting_frame, command=lambda value, key="show_user_profile": self._update_boolean_value(key, value)).grid(column=1, row=0, rowspan=2, padx=(0, self.ENTRY_PADX*2), pady=self.ENTRY_PADY)
        setting_frame.grid(column=0, row=row, sticky="nsew", pady=(self.ENTRY_GAP, 0))
        
        # endregion

        return frame
# endregion


# region functions
    def _update_boolean_value(self, key: str, value: bool) -> None:
        ConfigEditor.set_value(key, value)
# endregion