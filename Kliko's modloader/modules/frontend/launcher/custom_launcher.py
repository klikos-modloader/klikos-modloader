from typing import Literal
from pathlib import Path
from tkinter import messagebox
import json

from modules.logger import Logger
from modules.project_data import ProjectData
from modules.filesystem import Resources, Directories
from modules.frontend.widgets import Root
from modules.localization import Localizer
from modules.interfaces.config import ConfigInterface

from .dataclasses import WindowConfig
from .exceptions import InvalidLauncherVersion

from packaging.version import Version, InvalidVersion as pacakaging_invalid_version_error  # type: ignore


LAUNCHER_VERSION: Version = Version("1.0.0")


class CustomLauncher:
    mode: Literal["Player", "Studio"]
    config: dict
    version: Version
    window: Root

    _LOG_PREFIX: str = "CustomLauncher"


    def __init__(self, mode: Literal["Player", "Studio"]):
        self.mode = mode
        default_launcher: str = ConfigInterface.get_default_launcher()
        launcher: str = ConfigInterface.get_launcher()

        if launcher != default_launcher:
            Logger.warning(f"Using custom launcher: {launcher}", prefix=self._LOG_PREFIX)

        target: Path = Directories.RESOURCES / "launchers" / launcher
        if not target.is_dir(): target = Directories.LAUNCHERS / launcher
        if not target.is_dir() or not not (target / "launcher.json").is_file():
            Logger.error(f'Custom launcher not found: {launcher}, reverting to default launcher', prefix=self._LOG_PREFIX)
            ConfigInterface.set_launcher(None)
            target = Directories.RESOURCES / "launchers" / default_launcher

        with open(target / "launcher.json") as file:
            self.config = json.load(file)

        launcher_version: str = self.config.get("version", None)
        try: self.version: Version = Version(launcher_version)
        except pacakaging_invalid_version_error:
            raise InvalidLauncherVersion(f'Invalid launcher version: "{launcher_version}"')
        if len(self.version.base_version.split(".")) != 3:
            raise InvalidLauncherVersion(f'Invalid launcher version: "{launcher_version}"')
        
        
        if not self.check_version_compatibility():
            target = Directories.RESOURCES / "launchers" / default_launcher
            with open(target / "launcher.json") as file:
                self.config = json.load(file)
            self.version = LAUNCHER_VERSION

        self.build_launcher_window()


    def check_version_compatibility(self) -> bool:
        if LAUNCHER_VERSION > self.version:
            message: str = Localizer.format(Localizer.Strings["launcher.warning.custom_launcher_version.too_new"], {"{app.name}": ProjectData.NAME})
        elif (LAUNCHER_VERSION.major, LAUNCHER_VERSION.minor) != (self.version.major, self.version.minor):
            message = Localizer.format(Localizer.Strings["launcher.warning.custom_launcher_version.too_old"], {"{app.name}": ProjectData.NAME})
        else: return True

        messagebox.showwarning(title=f"{ProjectData.NAME} ({ProjectData.VERSION})", message=message)
        return False



    def build_launcher_window(self) -> None:
        window_config: WindowConfig = WindowConfig(self.config.get("window", {}))

        self.window = Root(window_config.title, icon=window_config.icon, appearance_mode=window_config.appearance_mode, width=window_config.width, height=window_config.height, centered=True, banner_system=False)
        self.window.resizable(*window_config.resizable)
        if window_config.column_configure:
            for index, kwargs in window_config.column_configure.items():
                self.window.grid_columnconfigure(index, **kwargs)  # type: ignore
        if window_config.row_configure:
            for index, kwargs in window_config.row_configure.items():
                self.window.grid_columnconfigure(index, **kwargs)  # type: ignore


    def run(self) -> None:
        self.window.deiconify()
        self.window.mainloop()