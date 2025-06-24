from typing import Literal, Any
from pathlib import Path
from tkinter import messagebox, TclError
from threading import Event, Thread
import json

from modules import exception_handler
from modules.logger import Logger
from modules.project_data import ProjectData
from modules.filesystem import Directories
from modules.frontend.widgets import Root, Toplevel, Label, GifObject
from modules.frontend.widgets.basic.localized import LocalizedCTkLabel, LocalizedCTkButton
from modules.localization import Localizer
from modules.interfaces.config import ConfigInterface
from modules.deployments import LatestVersion

from . import tasks
from .dataclasses import WindowConfig, WidgetConfig
from .exceptions import InvalidLauncherVersion

from packaging.version import Version, InvalidVersion as pacakaging_invalid_version_error  # type: ignore
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkProgressBar, CTkFont, CTkImage, ScalingTracker, set_default_color_theme, set_appearance_mode  # type: ignore


LAUNCHER_VERSION: Version = Version("1.0.1")


class PreviewLauncher:
    config: dict
    version: Version
    base_directory: Path
    window: Toplevel
    window_config: WindowConfig

    _status_labels: list[LocalizedCTkLabel]
    _file_version_labels: list[LocalizedCTkLabel]
    _channel_labels: list[LocalizedCTkLabel]
    _guid_labels: list[LocalizedCTkLabel]
    _progress_bars: list[CTkProgressBar]

    _LOG_PREFIX: str = "PreviewLauncher"


    def __init__(self, root: Root):
        Logger.info(f"Loading launcher preview...")
        self.root = root
        default_launcher: str = ConfigInterface.get_default_launcher()
        launcher: str = ConfigInterface.get_launcher()

        if launcher != default_launcher:
            Logger.warning(f"Using custom launcher: {launcher}", prefix=self._LOG_PREFIX)

        target: Path = Directories.RESOURCES / "launchers" / launcher
        if not target.is_dir(): target = Directories.LAUNCHERS / launcher
        if not target.is_dir() or not (target / "launcher.json").is_file():
            Logger.error(f'Custom launcher not found: {launcher}, reverting to default launcher', prefix=self._LOG_PREFIX)
            ConfigInterface.set_launcher(None)
            target = Directories.RESOURCES / "launchers" / default_launcher

        with open(target / "launcher.json") as file:
            self.config = json.load(file)

        launcher_version: str = self.config.get("version", None)
        if not launcher_version:
            raise ValueError("Unknown launcher version!")
        try: self.version: Version = Version(launcher_version)
        except (pacakaging_invalid_version_error, TypeError):
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
        self._file_version_labels = []
        self._channel_labels = []
        self._guid_labels = []
        self._progress_bars = []
        self.window_config: WindowConfig = WindowConfig(self.config.get("window", {}), self.base_directory)
        self.stop_event = Event()

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
        window_config = self.window_config
        set_appearance_mode(window_config.appearance_mode)
        if window_config.theme is not None:
            set_default_color_theme(str(window_config.theme))

        self.window = Toplevel(window_config.title, icon=window_config.icon, width=window_config.width, height=window_config.height, centered=True, master=self.root)
        self.window.protocol("WM_DELETE_WINDOW", self.on_cancel)
        if window_config.fg_color is not None:
            self.window.configure(fg_color=window_config.fg_color)
        self.window.resizable(*window_config.resizable)
        if window_config.fullscreen:
            self.window.wm_attributes("-fullscreen", True)
            self.window.state("normal")
        self.window.wm_attributes("-alpha", window_config.alpha)

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

        for bar in self._progress_bars:
            match bar.cget("mode"):
                case "determinate":
                    bar.set(0)
                case "indeterminate":
                    bar.start()

# endregion


# region place widget
    def _place_widget(self, parent, config: WidgetConfig) -> None:
        widget: CTkFrame | CTkLabel | LocalizedCTkLabel | CTkButton | LocalizedCTkButton | CTkProgressBar

        match config.type:
# region - frame
            case "frame":
                kwargs = config.kwargs
                widget = CTkFrame(parent, **kwargs)
                if config.column_configure:
                    for index, kwargs in config.column_configure.items():
                        widget.grid_columnconfigure(index, **kwargs)  # type: ignore
                if config.row_configure:
                    for index, kwargs in config.row_configure.items():
                        widget.grid_rowconfigure(index, **kwargs)  # type: ignore
# endregion

# region - label
            case "label" | "status_label" | "channel_label" | "version_label" | "file_version_label":
                kwargs = config.kwargs
                font_data: dict | None = kwargs.pop("font", None)
                if font_data: kwargs["font"] = CTkFont(**font_data)
                image_data: dict | None = kwargs.pop("image", None)
                if image_data: kwargs["image"] = CTkImage(**image_data)
                gif_data: dict | None = kwargs.pop("gif", None)
                if gif_data: kwargs["gif"] = GifObject(**gif_data)

                match config.type:
                    case "status_label":
                        kwargs.pop("text", None)
                        kwargs.pop("gif", None)
                        widget = LocalizedCTkLabel(
                            parent, key="launcher.progress.initializing",
                            modification=lambda string: Localizer.format(string, {
                                "{roblox.player}": Localizer.Key("roblox.player"),
                                "{roblox.player_alt}": Localizer.Key("roblox.player_alt"),
                                "{roblox.studio}": Localizer.Key("roblox.studio"),
                                "{roblox.studio_alt}": Localizer.Key("roblox.studio_alt"),
                                "{roblox.common}": Localizer.Key("roblox.common"),
                                "{roblox.dynamic}": Localizer.Key("roblox.common")
                            }), **kwargs)
                        self._status_labels.append(widget)

                    case "channel_label":
                        kwargs.pop("text", None)
                        kwargs.pop("gif", None)
                        widget = LocalizedCTkLabel(parent, key=None, modification=None, **kwargs)
                        self._channel_labels.append(widget)

                    case "version_label":
                        kwargs.pop("text", None)
                        kwargs.pop("gif", None)
                        widget = LocalizedCTkLabel(parent, key=None, modification=None, **kwargs)
                        self._guid_labels.append(widget)

                    case "file_version_label":
                        kwargs.pop("text", None)
                        kwargs.pop("gif", None)
                        widget = LocalizedCTkLabel(parent, key=None, modification=None, **kwargs)
                        self._file_version_labels.append(widget)

                    case "label":
                        if config.localized_string is not None:
                            kwargs.pop("gif", None)
                            widget = LocalizedCTkLabel(parent, key=config.localized_string, modification=config.localized_string_modification, **kwargs)
                        else:
                            widget = Label(parent, **kwargs)
# endregion

# region - button
            case "button":
                kwargs = config.kwargs
                kwargs.pop("command", None)
                if config.button_action == "cancel":
                    kwargs["command"] = self.on_cancel
                font_data = kwargs.pop("font", None)
                if font_data: kwargs["font"] = CTkFont(**font_data)
                image_data = kwargs.pop("image", None)
                if image_data: kwargs["image"] = CTkImage(**image_data)

                if config.localized_string is not None:
                    widget = LocalizedCTkButton(parent, key=config.localized_string, modification=config.localized_string_modification, **kwargs)
                else:
                    widget = CTkButton(parent, **kwargs)
# endregion

# region - progress bar
            case "progress_bar":
                kwargs = config.kwargs
                widget = CTkProgressBar(parent, **kwargs)
                self._progress_bars.append(widget)
# endregion

        match config.placement_mode:
            case "grid": widget.grid(**config.placement_mode_kwargs)
            case "pack": widget.pack(**config.placement_mode_kwargs)
            case "place": widget.place(**config.placement_mode_kwargs)

        if config.type == "frame":
            children: list[WidgetConfig] = config.children
            for child in children:
                self._place_widget(widget, child)
# endregion


# region preview
    def preview(self) -> None:
        self.window.deiconify()
        self.window.update()
        self.center_window()
# endregion


# region show
    def show(self) -> None:
        self.update_progress_bars(0.5)
        self.set_deployment_details("version-3c1b78b767674c66", "LIVE", 670)
        self.set_status_label("launcher.progress.preview")
        self.window.update()
        self.window.deiconify()
        self.window.attributes("-topmost", True)  # Sometimes the launcher is hidden behind the menu window
        self.center_window()
        self.window.grab_set()
# endregion


    def center_window(self) -> None:
        window_scaling: float = ScalingTracker.get_window_scaling(self.window)
        width: int = int(self.window_config.width / window_scaling) if self.window_config.width else int(self.window.winfo_width() / window_scaling)
        height: int = int(self.window_config.height / window_scaling) if self.window_config.height else int(self.window.winfo_height() / window_scaling)
        x: int = int((self.window.winfo_screenwidth()-width)/2)
        y: int = int((self.window.winfo_screenheight()-height)/2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")


    def on_cancel(self, *_, **__) -> None:
        self.close_window()


    def close_window(self, *_, **__) -> None:
        self.stop_event.set()
        if self.window.winfo_exists():
            self.window.destroy()


    def set_status_label(self, key: str) -> None:
        for label in self._status_labels:
            label.after(0, lambda: label.configure(key=key))


    def set_deployment_details(self, guid: str, channel: str, file_version: int) -> None:
        if not ConfigInterface.get("deployment_info"): return
        for label in self._channel_labels:
            label.after(0,
                lambda label=label: label.configure(  # type: ignore
                    key="launcher.deployment_info.channel",
                    modification=lambda string: Localizer.format(string, {"{value}": channel})
                )
            )
        for label in self._file_version_labels:
            label.after(0,
                lambda label=label: label.configure(  # type: ignore
                    key="launcher.deployment_info.file_version",
                    modification=lambda string: Localizer.format(string, {"{value}": str(file_version)})
                )
            )
        for label in self._guid_labels:
            label.after(0,
                lambda label=label: label.configure(  # type: ignore
                    key="launcher.deployment_info.guid",
                    modification=lambda string: Localizer.format(string, {"{value}": guid})
                )
            )


    def update_progress_bars(self, value: float) -> None:
        for bar in self._progress_bars:
            try:
                if bar.cget("mode") == "determinate":
                    bar.after(0, bar.set, value)
            except (TclError, AttributeError): pass