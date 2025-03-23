from pathlib import Path

from modules.info import NAME
from modules.localization import Localizer
from modules.core.config_editor import ConfigEditor
from modules.frontend.widgets.fluent import FluentLabel, FluentToolTipButton, FluentFrame, FluentDropdownButton, messagebox, get_root_instance

import customtkinter as ctk  # type: ignore
from PIL import Image  # type: ignore


class SettingsSection:
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

        FluentLabel(title_row, Localizer.strings["menu.settings"]["title"], font_size=28, font_weight="bold").grid(column=0, row=0, sticky="w")
        self.tooltip_button = FluentToolTipButton(get_root_instance(), master=title_row, wraplength=400, tooltip_title=Localizer.strings["menu.settings"]["tooltip.title"], tooltip_message=Localizer.strings["menu.settings"]["tooltip.message"], tooltip_orientation="down", toplevel=True)
        self.tooltip_button.grid(column=1, row=0, padx=(8,0), sticky="w")

        return frame


# region Settings
    def _get_content(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.content, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)

        (
            appearance,
            language,
            check_for_updates,
            confirm_launch,
            disable_mods,
            disable_fastflags,
            deployment_info
        )  = ConfigEditor.get_values(
            "appearance",
            "language",
            "check_for_updates",
            "confirm_launch",
            "disable_mods",
            "disable_fastflags",
            "deployment_info"
        )

        row: int = 0

        appearance_language_frame = ctk.CTkFrame(frame, fg_color="transparent")
        appearance_language_frame.grid_columnconfigure((0, 1), weight=1)
        appearance_language_frame.grid(column=0, row=row, sticky="nsew")

        # region Appearance

        appearance_modes: list[str] = [Localizer.strings["menu.settings"]["appearance.light"], Localizer.strings["menu.settings"]["appearance.dark"], Localizer.strings["menu.settings"]["appearance.system"]]
        current_appearance: str = Localizer.strings["menu.settings"][f"appearance.{appearance}"]
        setting_frame = FluentFrame(appearance_language_frame)
        setting_frame.grid_columnconfigure(0, weight=1)
        FluentLabel(setting_frame, Localizer.strings["menu.settings"]["appearance.title"], font_size=self.ENTRY_TITLE_FONT_SIZE, font_weight="bold").grid(column=0, row=0, sticky="w", padx=(self.ENTRY_PADX, 0), pady=self.ENTRY_PADY)
        appearance_dropdown = FluentDropdownButton(get_root_instance(), setting_frame, appearance_modes, current_appearance, command=self._set_appearance_mode)
        appearance_dropdown.grid(column=1, row=0, sticky="e", padx=(self.ENTRY_INNER_GAP, self.ENTRY_PADX), pady=self.ENTRY_PADY)
        setting_frame.grid(column=0, row=0, sticky="nsew")

        # engregion


        # region Language

        available_languages: dict[str, str] = Localizer.METADATA["available"]
        current_language: str = Localizer.METADATA["available"][language]
        setting_frame = FluentFrame(appearance_language_frame)
        setting_frame.grid_columnconfigure(0, weight=1)
        FluentLabel(setting_frame, Localizer.strings["menu.settings"]["language.title"], font_size=self.ENTRY_TITLE_FONT_SIZE, font_weight="bold").grid(column=0, row=0, sticky="w", padx=(self.ENTRY_PADX, 0), pady=self.ENTRY_PADY)
        language_dropdown = FluentDropdownButton(get_root_instance(), setting_frame, available_languages.values(), current_language, command=self._set_language)
        language_dropdown.grid(column=1, row=0, sticky="e", padx=(self.ENTRY_INNER_GAP, self.ENTRY_PADX), pady=self.ENTRY_PADY)
        setting_frame.grid(column=1, row=0, sticky="nsew", padx=(self.ENTRY_GAP, 0))

        # endregion

        appearance_dropdown.update_idletasks()
        language_dropdown.update_idletasks()
        appearance_language_dropdown_width: int = max(appearance_dropdown.winfo_width(), language_dropdown.winfo_width())
        appearance_dropdown.set_width(width=appearance_language_dropdown_width)
        language_dropdown.set_width(width=appearance_language_dropdown_width)

        row += 1

        # region Check for updates
        
        setting_frame = FluentFrame(frame)
        setting_frame.grid_columnconfigure(0, weight=1)
        FluentLabel(setting_frame, Localizer.strings["menu.settings"]["check_for_updates.title"], font_size=self.ENTRY_TITLE_FONT_SIZE, font_weight="bold").grid(column=0, row=0, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(self.ENTRY_PADY, 0))
        FluentLabel(setting_frame, Localizer.strings["menu.settings"]["check_for_updates.description"].replace("{project_name}", NAME), font_size=self.ENTRY_DESCRIPTION_FONT_SIZE).grid(column=0, row=1, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(0, self.ENTRY_PADY))
        setting_frame.grid(column=0, row=row, sticky="nsew", pady=(self.ENTRY_GAP, 0))
        
        # endregion

        row += 1

        # region Check for updates
        
        setting_frame = FluentFrame(frame)
        setting_frame.grid_columnconfigure(0, weight=1)
        FluentLabel(setting_frame, Localizer.strings["menu.settings"]["confirm_launch.title"], font_size=self.ENTRY_TITLE_FONT_SIZE, font_weight="bold").grid(column=0, row=0, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(self.ENTRY_PADY, 0))
        FluentLabel(setting_frame, Localizer.strings["menu.settings"]["confirm_launch.description"], font_size=self.ENTRY_DESCRIPTION_FONT_SIZE).grid(column=0, row=1, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(0, self.ENTRY_PADY))
        setting_frame.grid(column=0, row=row, sticky="nsew", pady=(self.ENTRY_GAP, 0))
        
        # endregion

        row += 1

        # region Force reinstallation
        
        setting_frame = FluentFrame(frame)
        setting_frame.grid_columnconfigure(0, weight=1)
        FluentLabel(setting_frame, Localizer.strings["menu.settings"]["force_reinstall.title"], font_size=self.ENTRY_TITLE_FONT_SIZE, font_weight="bold").grid(column=0, row=0, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(self.ENTRY_PADY, 0))
        FluentLabel(setting_frame, Localizer.strings["menu.settings"]["force_reinstall.description"], font_size=self.ENTRY_DESCRIPTION_FONT_SIZE).grid(column=0, row=1, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(0, self.ENTRY_PADY))
        setting_frame.grid(column=0, row=row, sticky="nsew", pady=(self.ENTRY_GAP, 0))
        
        # endregion

        row += 1

        # region Disable mods
        
        setting_frame = FluentFrame(frame)
        setting_frame.grid_columnconfigure(0, weight=1)
        FluentLabel(setting_frame, Localizer.strings["menu.settings"]["disable_mods.title"], font_size=self.ENTRY_TITLE_FONT_SIZE, font_weight="bold").grid(column=0, row=0, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(self.ENTRY_PADY, 0))
        FluentLabel(setting_frame, Localizer.strings["menu.settings"]["disable_mods.description"], font_size=self.ENTRY_DESCRIPTION_FONT_SIZE).grid(column=0, row=1, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(0, self.ENTRY_PADY))
        setting_frame.grid(column=0, row=row, sticky="nsew", pady=(self.ENTRY_GAP, 0))
        
        # endregion

        row += 1

        # region Disable FastFlags
        
        setting_frame = FluentFrame(frame)
        setting_frame.grid_columnconfigure(0, weight=1)
        FluentLabel(setting_frame, Localizer.strings["menu.settings"]["disable_fastflags.title"], font_size=self.ENTRY_TITLE_FONT_SIZE, font_weight="bold").grid(column=0, row=0, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(self.ENTRY_PADY, 0))
        FluentLabel(setting_frame, Localizer.strings["menu.settings"]["disable_fastflags.description"], font_size=self.ENTRY_DESCRIPTION_FONT_SIZE).grid(column=0, row=1, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(0, self.ENTRY_PADY))
        setting_frame.grid(column=0, row=row, sticky="nsew", pady=(self.ENTRY_GAP, 0))
        
        # endregion

        row += 1

        # region Deployment info
        
        setting_frame = FluentFrame(frame)
        setting_frame.grid_columnconfigure(0, weight=1)
        FluentLabel(setting_frame, Localizer.strings["menu.settings"]["deployment_info.title"], font_size=self.ENTRY_TITLE_FONT_SIZE, font_weight="bold").grid(column=0, row=0, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(self.ENTRY_PADY, 0))
        FluentLabel(setting_frame, Localizer.strings["menu.settings"]["deployment_info.description"], font_size=self.ENTRY_DESCRIPTION_FONT_SIZE).grid(column=0, row=1, sticky="w", padx=(self.ENTRY_PADX, 0), pady=(0, self.ENTRY_PADY))
        setting_frame.grid(column=0, row=row, sticky="nsew", pady=(self.ENTRY_GAP, 0))
        
        # endregion

        return frame
# endregion


# region functions
    def _set_appearance_mode(self, mode: str) -> None:
        appearance_mode: str = "light" if mode == Localizer.strings["menu.settings"]["appearance.light"] else "dark" if mode == Localizer.strings["menu.settings"]["appearance.dark"] else "system"
        ConfigEditor.set_value("appearance", appearance_mode)
        ctk.set_appearance_mode(appearance_mode)


    def _set_language(self, language: str) -> None:
        inverted_languages = {value: key for key, value in Localizer.METADATA["available"].items()}
        language_key: str = inverted_languages[language]
        ConfigEditor.set_value("language", language_key)
# endregion