from typing import Literal, Any
from pathlib import Path
from tkinter import messagebox
import json

from modules.logger import Logger
from modules.project_data import ProjectData
from modules.filesystem import Resources, Directories
from modules.frontend.widgets import Root
from modules.frontend.widgets.basic.localized import LocalizedCTkLabel
from modules.frontend.functions import get_ctk_image
from modules.localization import Localizer
from modules.interfaces.config import ConfigInterface

from .dataclasses import WindowConfig, WidgetConfig
from .exceptions import InvalidLauncherVersion

from packaging.version import Version, InvalidVersion as pacakaging_invalid_version_error  # type: ignore
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkFont, CTkImage, set_default_color_theme, set_appearance_mode  # type: ignore


LAUNCHER_VERSION: Version = Version("1.0.0")


class CustomLauncher:
    mode: Literal["Player", "Studio"]
    config: dict
    version: Version
    base_directory: Path
    window: Root

    _status_labels: list[LocalizedCTkLabel]
    _version_labels: list[LocalizedCTkLabel]
    _channel_labels: list[LocalizedCTkLabel]
    _guid_labels: list[LocalizedCTkLabel]

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

        self.base_directory = target
        self._status_labels = []
        self._version_labels = []
        self._channel_labels = []
        self._guid_labels = []
        self.build_launcher_window()


    def check_version_compatibility(self) -> bool:
        if LAUNCHER_VERSION > self.version:
            message: str = Localizer.format(Localizer.Strings["launcher.warning.custom_launcher_version.too_new"], {"{app.name}": ProjectData.NAME})
        elif (LAUNCHER_VERSION.major, LAUNCHER_VERSION.minor) != (self.version.major, self.version.minor):
            message = Localizer.format(Localizer.Strings["launcher.warning.custom_launcher_version.too_old"], {"{app.name}": ProjectData.NAME})
        else: return True

        messagebox.showwarning(title=f"{ProjectData.NAME} ({ProjectData.VERSION})", message=message)
        return False


# region build window
    def build_launcher_window(self) -> None:
        window_config: WindowConfig = WindowConfig(self.config.get("window", {}), self.base_directory)

        set_appearance_mode(window_config.appearance_mode)
        if window_config.theme is not None:
            set_default_color_theme(str(window_config.theme))

        self.window = Root(window_config.title, icon=window_config.icon, appearance_mode=window_config.appearance_mode, width=window_config.width, height=window_config.height, centered=True, banner_system=False)
        self.window.configure(fg_color=window_config.fg_color)
        self.window.resizable(*window_config.resizable)

        if window_config.column_configure:
            for index, kwargs in window_config.column_configure.items():
                self.window.grid_columnconfigure(index, **kwargs)  # type: ignore
        if window_config.row_configure:
            for index, kwargs in window_config.row_configure.items():
                self.window.grid_rowconfigure(index, **kwargs)  # type: ignore

        widgets: Any = self.config.get("widgets", None)
        if not isinstance(widgets, list) or not widgets:
            return

        for item in widgets:
            if not isinstance(item, dict): continue
            widget: WidgetConfig = WidgetConfig(item, self.base_directory)
            self._place_widget(self.window, widget)
# endregion


# region place widget
    def _place_widget(self, parent, config: WidgetConfig) -> None:
        widget: CTkFrame | CTkLabel | LocalizedCTkLabel | CTkButton

        match config.type:
            case "frame":
                kwargs = config.kwargs
                widget = CTkFrame(parent, **kwargs)
                if config.column_configure:
                    for index, kwargs in config.column_configure.items():
                        widget.grid_columnconfigure(index, **kwargs)  # type: ignore
                if config.row_configure:
                    for index, kwargs in config.row_configure.items():
                        widget.grid_rowconfigure(index, **kwargs)  # type: ignore

            case "label":
                kwargs = config.kwargs
                widget = CTkLabel(parent, **kwargs)

            case "button":
                kwargs = config.kwargs
                kwargs.pop("command", None)
                widget = CTkButton(parent, **kwargs)

        match config.placement_mode:
            case "grid": widget.grid(**config.placement_mode_kwargs)
            case "pack": widget.pack(**config.placement_mode_kwargs)
            case "place": widget.place(**config.placement_mode_kwargs)

        if config.type == "frame":
            children: list[WidgetConfig] = config.children
            for child in children:
                self._place_widget(widget, child)
# endregion



# region run
    def run(self) -> None:
        self.window.deiconify()
        self.window.mainloop()
# endregion