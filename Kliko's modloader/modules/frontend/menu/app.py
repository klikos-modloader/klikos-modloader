from typing import Literal

from modules.project_data import ProjectData
from modules.localization import Localizer
from modules.frontend.widgets import Root, Frame, Label, Button
from modules.filesystem import Resources
from modules.interfaces.config import ConfigInterface
from modules.frontend.functions import get_ctk_image

from .sections import ModsSection, MarketplaceSection, ModGeneratorSection, FastFlagsSection, GlobalBasicSettingsSection, IntegrationsSection, CustomIntegrationsSection, SettingsSection, AboutSection

from customtkinter import CTkImage  # type: ignore


class App(Root):
    active_section: str = ""
    loaded_sections: dict = {}
    sidebar: Frame

    mods_section: ModsSection
    marketplace_section: MarketplaceSection
    mod_generator_section: ModGeneratorSection
    fastflags_section: FastFlagsSection
    global_basic_settings_section: GlobalBasicSettingsSection
    integrations_section: IntegrationsSection
    custom_integrations_section: CustomIntegrationsSection
    settings_section: SettingsSection
    about_section: AboutSection

    _NAV_ICON_SIZE: int = 24
    _SIDEBAR_MIN_WIDTH: int = 286


    def __init__(self) -> None:
        appearance: Literal["light", "dark", "system"] = ConfigInterface.get_appearance_mode()
        width, height = ConfigInterface.get_menu_size()
        super().__init__(title="Kliko's modloader", icon=Resources.FAVICON, appearance_mode=appearance, width=width, height=height, centered=True, banner_system=True)
        self.grid_columnconfigure(0, minsize=self._SIDEBAR_MIN_WIDTH)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create sidebar
        self.sidebar: Frame = Frame(self, transparent=True)
        self.configure_sidebar()
        self.sidebar.grid(column=0, row=0, sticky="nsew")

        # Initialize sections
        self.mods_section = ModsSection(self)
        self.marketplace_section = MarketplaceSection(self)
        self.mod_generator_section = ModGeneratorSection(self)
        self.fastflags_section = FastFlagsSection(self)
        self.global_basic_settings_section = GlobalBasicSettingsSection(self)
        self.integrations_section = IntegrationsSection(self)
        self.custom_integrations_section = CustomIntegrationsSection(self)
        self.settings_section = SettingsSection(self)
        self.about_section = AboutSection(self)

        # Default section
        self._set_active_section("mods")



    def _set_active_section(self, section: Literal["mods", "mod_generator", "marketplace", "fastflags", "global_basic_settings", "integrations", "custom_integrations", "settings", "about"]) -> None:
        if self.active_section == section: return

        section_frame = getattr(self, f"{section}_section", None)
        if section_frame is None: return
        section_frame.grid(column=1, row=0, sticky="nsew")
        section_frame.show()

        for key, frame in self.loaded_sections.items():
            if key != section: frame.grid_forget()

        if section_frame not in self.loaded_sections:
            self.loaded_sections[section] = section_frame

        self.active_section = section


    def configure_sidebar(self) -> None:
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(1, weight=1)

        # Header
        header: Frame = Frame(self.sidebar, transparent=True)
        header.grid_columnconfigure(1, weight=1)
        header.grid(column=0, row=0, sticky="nsew", padx=16, pady=16)
        logo: CTkImage = get_ctk_image(Resources.LOGO, size=48)
        Label(header, image=logo, width=48, height=48).grid(column=0, row=0, rowspan=2, sticky="nsew", padx=(0, 12))
        Label(header, key=ProjectData.NAME, style="subtitle").grid(column=1, row=0, sticky="ew")
        Label(header, key="menu.sidebar.version", modification=lambda string: Localizer.format(string, {"{app.version}": ProjectData.VERSION}), style="caption").grid(column=1, row=1, sticky="ew")

        # Main navigation
        navigation: Frame = Frame(self.sidebar, transparent=True)
        navigation.grid_columnconfigure(0, weight=1)
        navigation.grid(column=0, row=1, sticky="nsew", padx=4, pady=4)
        for i, key in enumerate(["mods", "mod_generator", "marketplace", "fastflags", "global_basic_settings", "integrations", "custom_integrations"]): Button(navigation, key=f"menu.sidebar.navigation.{key}", transparent=True, anchor="w", image=self._get_nav_icon(key), command=lambda key=key: self._set_active_section(key)).grid(column=0, row=i, sticky="ew", pady=0 if i == 0 else (4, 0))  # type: ignore

        # Footer navigation
        footer: Frame = Frame(self.sidebar, transparent=True)
        footer.grid_columnconfigure(0, weight=1)
        footer.grid(column=0, row=2, sticky="nsew", padx=4, pady=(4, 8))
        for i, key in enumerate(["settings", "about"]): Button(footer, key=f"menu.sidebar.navigation.{key}", transparent=True, anchor="w", image=self._get_nav_icon(key), command=lambda key=key: self._set_active_section(key)).grid(column=0, row=i, sticky="ew", pady=0 if i == 0 else (4, 0))  # type: ignore


    def _get_nav_icon(self, key: Literal["mods", "mod_generator", "marketplace", "fastflags", "global_basic_settings", "integrations", "custom_integrations", "settings", "about"]) -> CTkImage | None:
        match key:
            case "mods":
                try: return get_ctk_image(Resources.Navigation.Light.MODS, Resources.Navigation.Dark.MODS, self._NAV_ICON_SIZE)
                except Exception: return None
            case "mod_generator":
                try: return get_ctk_image(Resources.Navigation.Light.MOD_GENERATOR, Resources.Navigation.Dark.MOD_GENERATOR, self._NAV_ICON_SIZE)
                except Exception: return None
            case "marketplace":
                try: return get_ctk_image(Resources.Navigation.Light.MARKETPLACE, Resources.Navigation.Dark.MARKETPLACE, self._NAV_ICON_SIZE)
                except Exception: return None
            case "fastflags":
                try: return get_ctk_image(Resources.Navigation.Light.FASTFLAGS, Resources.Navigation.Dark.FASTFLAGS, self._NAV_ICON_SIZE)
                except Exception: return None
            case "global_basic_settings":
                try: return get_ctk_image(Resources.Navigation.Light.GLOBAL_BASIC_SETTINGS, Resources.Navigation.Dark.GLOBAL_BASIC_SETTINGS, self._NAV_ICON_SIZE)
                except Exception: return None
            case "integrations":
                try: return get_ctk_image(Resources.Navigation.Light.INTEGRATIONS, Resources.Navigation.Dark.INTEGRATIONS, self._NAV_ICON_SIZE)
                except Exception: return None
            case "custom_integrations":
                try: return get_ctk_image(Resources.Navigation.Light.CUSTOM_INTEGRATIONS, Resources.Navigation.Dark.CUSTOM_INTEGRATIONS, self._NAV_ICON_SIZE)
                except Exception: return None
            case "settings":
                try: return get_ctk_image(Resources.Navigation.Light.SETTINGS, Resources.Navigation.Dark.SETTINGS, self._NAV_ICON_SIZE)
                except Exception: return None
            case "about":
                try: return get_ctk_image(Resources.Navigation.Light.ABOUT, Resources.Navigation.Dark.ABOUT, self._NAV_ICON_SIZE)
                except Exception: return None
            case _: return None