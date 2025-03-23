import webbrowser
from typing import Literal
from pathlib import Path
from threading import Thread
from packaging.version import parse as parse_version

from modules.logger import Logger
from modules import exception_handler
from modules.localization import Localizer
from modules.core.config_editor import ConfigEditor
from modules.networking import requests, Api, Response
from modules.info import NAME, VERSION, TAGLINE, LATEST
from modules.frontend.widgets.fluent import FluentRootWindow, FluentNavigationFrame, FluentScrollableFrame, FluentLabel, FluentInAppNotification, set_root_instance, clear_root_instance, apply_color_theme

from .sections import ModsSection, MarketplaceSection, GeneratorSection, FastFlagsSection, GlobalBasicSettingsSection, IntegrationsSection, LaunchIntegrationsSection, SettingsSection, AboutSection

import customtkinter as ctk  # type: ignore
from PIL import Image  # type: ignore


class App(FluentRootWindow):
    WIDTH: int = 1100
    MIN_WIDTH: int = 1000
    HEIGHT: int = 600
    MIN_HEIGHT: int = 540
    RESOURCES: Path = Path(__file__).parent / "resources"
    FAVICON: Path = RESOURCES / "favicon.ico"

    active_section: str = None  # type: ignore
    loaded_sections: dict
    sections: dict

    mods_section: ModsSection
    marketplace_section: MarketplaceSection
    generator_section: GeneratorSection
    fastflags_section: FastFlagsSection
    globalbasicsettings_section: GlobalBasicSettingsSection
    integrations_section: IntegrationsSection
    launch_integrations_section: LaunchIntegrationsSection

    settings_section: SettingsSection
    about_section: AboutSection


    def __init__(self):
        appearance: str = ConfigEditor.get_appearance_mode()
        ctk.set_appearance_mode(appearance)
        apply_color_theme()
        super().__init__(NAME, self.FAVICON)
        self.sections = {}
        self.loaded_sections = {}

        try:
            set_root_instance(self)
            self.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
            self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
            self._center_app_window()
            self.report_callback_exception = self._on_error

            # Mods
            self.sections["mods"] = FluentScrollableFrame(self, toplevel=True)
            self.sections["mods"].grid(column=1, row=0, sticky="nsew")
            self.sections["mods"].grid_columnconfigure(0, weight=1)
            self.sections["mods"].grid_rowconfigure(0, weight=1)
            self.mods_section = ModsSection(self, self.sections["mods"], self.RESOURCES)

            # Community Mods
            self.sections["marketplace"] = FluentScrollableFrame(self, toplevel=True)
            self.sections["marketplace"].grid_columnconfigure(0, weight=1)
            self.sections["marketplace"].grid_rowconfigure(0, weight=1)
            self.marketplace_section = MarketplaceSection(self, self.sections["marketplace"], self.RESOURCES)

            # Mod Generator
            self.sections["generator"] = FluentScrollableFrame(self, toplevel=True)
            self.sections["generator"].grid_columnconfigure(0, weight=1)
            self.sections["generator"].grid_rowconfigure(0, weight=1)
            self.generator_section = GeneratorSection(self, self.sections["generator"], self.RESOURCES)

            # FastFlags Manager
            self.sections["fastflags"] = FluentScrollableFrame(self, toplevel=True)
            self.sections["fastflags"].grid_columnconfigure(0, weight=1)
            self.sections["fastflags"].grid_rowconfigure(0, weight=1)
            self.fastflags_section = FastFlagsSection(self, self.sections["fastflags"], self.RESOURCES)

            # GlobalBasicSettings Editor
            self.sections["globalbasicsettings"] = FluentScrollableFrame(self, toplevel=True)
            self.sections["globalbasicsettings"].grid_columnconfigure(0, weight=1)
            self.sections["globalbasicsettings"].grid_rowconfigure(0, weight=1)
            self.globalbasicsettings_section = GlobalBasicSettingsSection(self, self.sections["globalbasicsettings"], self.RESOURCES)

            # Integrations
            self.sections["integrations"] = FluentScrollableFrame(self, toplevel=True)
            self.sections["integrations"].grid_columnconfigure(0, weight=1)
            self.sections["integrations"].grid_rowconfigure(0, weight=1)
            self.integrations_section = IntegrationsSection(self, self.sections["integrations"], self.RESOURCES)

            # Custom Integrations
            self.sections["launch_integrations"] = FluentScrollableFrame(self, toplevel=True)
            self.sections["launch_integrations"].grid_columnconfigure(0, weight=1)
            self.sections["launch_integrations"].grid_rowconfigure(0, weight=1)
            self.launch_integrations_section = LaunchIntegrationsSection(self, self.sections["launch_integrations"], self.RESOURCES)

            # Settings
            self.sections["settings"] = FluentScrollableFrame(self, toplevel=True)
            self.sections["settings"].grid_columnconfigure(0, weight=1)
            self.sections["settings"].grid_rowconfigure(0, weight=1)
            self.settings_section = SettingsSection(self, self.sections["settings"], self.RESOURCES)

            # About Section
            self.sections["about"] = FluentScrollableFrame(self, toplevel=True)
            self.sections["about"].grid_columnconfigure(0, weight=1)
            self.sections["about"].grid_rowconfigure(0, weight=1)
            self.about_section = AboutSection(self, self.sections["about"], self.RESOURCES)


            buttons: tuple = (  # type: ignore
                {"text": Localizer.strings["menu.sidebar"]["navigation"]["mods"], "image": self._get_nav_icon("mods"), "command": lambda: self._change_active_section("mods")},
                {"text": Localizer.strings["menu.sidebar"]["navigation"]["marketplace"], "image": self._get_nav_icon("marketplace"), "command": lambda: self._change_active_section("marketplace")},
                {"text": Localizer.strings["menu.sidebar"]["navigation"]["generator"], "image": self._get_nav_icon("generator"), "command": lambda: self._change_active_section("generator")},
                {"text": Localizer.strings["menu.sidebar"]["navigation"]["fastflags"], "image": self._get_nav_icon("fastflags"), "command": lambda: self._change_active_section("fastflags")},
                {"text": Localizer.strings["menu.sidebar"]["navigation"]["globalbasicsettings"], "image": self._get_nav_icon("globalbasicsettings"), "command": lambda: self._change_active_section("globalbasicsettings")},
                {"text": Localizer.strings["menu.sidebar"]["navigation"]["integrations"], "image": self._get_nav_icon("integrations"), "command": lambda: self._change_active_section("integrations")},
                {"text": Localizer.strings["menu.sidebar"]["navigation"]["launch_integrations"], "image": self._get_nav_icon("launch_integrations"), "command": lambda: self._change_active_section("launch_integrations")}
            )
            footer_buttons: tuple = (  # type: ignore
                {"text": Localizer.strings["menu.sidebar"]["navigation"]["settings"], "image": self._get_nav_icon("settings"), "command": lambda: self._change_active_section("settings")},
                {"text": Localizer.strings["menu.sidebar"]["navigation"]["about"], "image": self._get_nav_icon("about"), "command": lambda: self._change_active_section("about")},
            )

            self.grid_columnconfigure(1, weight=1)
            self.grid_rowconfigure(0, weight=1)

            sidebar = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
            sidebar.grid(column=0, row=0, sticky="nsew")
            sidebar.grid_columnconfigure(0, weight=1)
            sidebar.grid_rowconfigure(1, weight=1)

            header = ctk.CTkFrame(sidebar, fg_color="transparent", height=60, corner_radius=0)
            header.grid(column=0, row=0, padx=16, pady=16, sticky="nsew")

            logo_path = self.RESOURCES / "logo_small.png"
            if logo_path.is_file() and logo_path.suffix == ".png":
                logo_image = Image.open(logo_path)
                logo = ctk.CTkImage(logo_image, size=(60,60))
            else:
                logo = None
            ctk.CTkLabel(header, image=logo, text="", fg_color="transparent").grid(column=0, row=0, sticky="w", padx=(0,12), rowspan=2)
            FluentLabel(header, text=NAME, font_size=20, font_weight="bold").grid(column=1,row=0, sticky="w")
            # FluentLabel(header, text=TAGLINE, font_size=16).grid(column=1,row=1, sticky="w")
            FluentLabel(header, text=Localizer.strings["menu.sidebar"]["version"].replace("{version}", VERSION), font_size=16).grid(column=1,row=1, sticky="w")

            navigation = FluentNavigationFrame(sidebar, buttons=buttons, footer_buttons=footer_buttons)
            navigation.grid(column=0, row=1, sticky="nsew")
            first_button = navigation.buttons[0]
            first_button.set_active()
        
        except Exception:
            clear_root_instance()
            self.destroy()
            raise
        
        else:
            if first_button.is_active() and callable(first_button.command): self.after(10, first_button.command)
            Thread(target=self._check_for_updates, daemon=True).start()
            self.mainloop()
            clear_root_instance()


    def _check_for_updates(self) -> None:
        def show_notification(latest: str) -> None:
            def on_ok() -> None:
                Logger.info("User chose to update!")
                webbrowser.open(LATEST, 2)
            FluentInAppNotification(self, on_click=on_ok, name=NAME, title=Localizer.strings["notifications"]["update.title"].replace("{latest}", latest), message=Localizer.strings["notifications"]["update.message"], icon=ctk.CTkImage(Image.open(self.RESOURCES / "nav" / "light" / f"about.png"), Image.open(self.RESOURCES / "nav" / "dark" / f"about.png"), size=(16,16)))

        try:
            Logger.info("Checking for updates...")
            response : Response = requests.get(Api.GitHub.LATEST_VERSION, attempts=1, timeout=(10,15))
            data: dict = response.json()
            latest: str = data["latest"]
            current_version_object = parse_version(VERSION)
            latest_version_object = parse_version(latest)
        except Exception as e:
            Logger.warning(f"Failed to check for updates! ({type(e).__name__}: {e})")
            return

        if latest_version_object > current_version_object:
            Logger.warning(f"A newer version is available: {latest}")
            self.after(10, show_notification, latest)


    def _change_active_section(self, section: Literal["mods", "marketplace", "generator", "fastflags", "globalbasicsettings", "launch_integrations", "integrations", "settings", "about"]) -> None:
        if section == self.active_section: return

        # Lazy loading
        section_object = getattr(self, f"{section}_section", None)
        if section_object is None: return
        if section not in self.loaded_sections:
            section_object.refresh()
            self.loaded_sections[section] = section_object
        
        if section == "mods": self.mods_section.load()
        elif "mods" in self.loaded_sections: self.loaded_sections["mods"].unload()
        if section == "marketplace": self.marketplace_section.load()
        elif "marketplace" in self.loaded_sections: self.loaded_sections["marketplace"].unload()
        if section == "generator": self.generator_section.load()
        elif "generator" in self.loaded_sections: self.loaded_sections["generator"].unload()
        if section == "fastflags": self.fastflags_section.load()
        elif "fastflags" in self.loaded_sections: self.loaded_sections["fastflags"].unload()

        if section == "about": self.about_section.load()
        elif "about" in self.loaded_sections: self.loaded_sections["about"].unload()

        self.sections[section].grid(column=1, row=0, sticky="nsew")
        self.active_section = section
        for key, frame in self.sections.items():
            if key == section: continue
            frame.grid_forget()


    def _on_error(self, exception_class, exception, traceback) -> None:
        self.destroy()
        clear_root_instance()
        exception_handler.run(exception)
    

    def _on_close(self, *_, **__) -> None:
        self.after(10, self.destroy)


    def _get_nav_icon(self, icon: str) -> ctk.CTkImage | None:
        light_image: Image | None = None
        dark_image: Image | None = None

        light_image_path: Path = self.RESOURCES / "nav" / "light" / f"{icon}.png"
        dark_image_path: Path = self.RESOURCES / "nav" / "dark" / f"{icon}.png"

        if light_image_path.is_file() and light_image_path.suffix == ".png": light_image = Image.open(light_image_path)
        if dark_image_path.is_file() and dark_image_path.suffix == ".png": dark_image = Image.open(dark_image_path)

        if light_image is None and dark_image is None: return None
        return ctk.CTkImage(light_image, dark_image, size=(20,20))


    def _center_app_window(self) -> None:
        self.update_idletasks()
        w: int = self.WIDTH
        h: int = self.HEIGHT
        x: int = self.winfo_screenwidth()//2 - w//2
        y: int = self.winfo_screenheight()//2 - h//2
        self.geometry(f"{w}x{h}+{x}+{y}")