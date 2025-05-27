from typing import Literal, Callable, NamedTuple, Any
from pathlib import Path
from threading import Event
from tkinter import messagebox
import time
import subprocess
import ctypes
import shutil
import hashlib

from modules.logger import Logger
from modules.project_data import ProjectData
from modules.localization import Localizer
from modules.interfaces.config import ConfigInterface
from modules.interfaces.data import DataInterface
from modules.interfaces.mod_manager import Mod, ModManager
from modules.interfaces.fastflag_manager import FastFlagProfile, FastFlagManager
from modules.interfaces.custom_integrations_manager import CustomIntegrationManager
from modules.interfaces.roblox import RobloxInterface
from modules.deployments import LatestVersion, Package, PackageManifest
from modules.networking import requests, Response, Api
from modules.filesystem import Directories
from modules.mod_updater import ModUpdater
from modules import filesystem


LOG_PREFIX: str = "LauncherTasks"
DEPLOYMENT_DETAILS_END_PROGRESS: float = 0.06
DOWNLOAD_END_PROGRESS: float = 0.65
MOD_UPDATER_START_PROGRESS: float = DOWNLOAD_END_PROGRESS
MOD_UPDATER_END_PROGRESS: float = 0.85
MOD_DEPLOY_END_PROGRESS: float = 0.90
FASTFLAG_DEPLOY_END_PROGRESS: float = 0.92
CUSTOM_INTEGRATIONS_END_PROGRESS: float = 0.95
LAUNCH_END_PROGRESS: float = 1

APPSETTINGS: str = """<?xml version="1.0" encoding="UTF-8"?>
<Settings>
	<ContentFolder>content</ContentFolder>
	<BaseUrl>http://www.roblox.com</BaseUrl>
</Settings>"""

class Config(NamedTuple):
    confirm_launch: bool
    force_reinstall: bool
    disable_mods: bool
    disable_fastflags: bool
    static_version_folder: bool
    use_roblox_version_folder: bool
    mod_updates: bool
    multi_instance_launching: bool
    discord_rpc: bool
    installed_version: str
    loaded_mods: list[str]


class Functions(NamedTuple):
    on_success: Callable
    on_cancel: Callable
    on_error: Callable[[Exception], Any]
    set_status_label: Callable[[str], Any]
    set_deployment_details: Callable[[LatestVersion], Any]
    update_progress_bars: Callable[[float], Any]


# region run
def run(mode: Literal["Player", "Studio"], deeplink: str, stop_event: Event, on_success: Callable, on_cancel: Callable, on_error: Callable[[Exception], Any], set_status_label: Callable[[str], Any], set_deployment_details: Callable[[LatestVersion], Any], update_progress_bars: Callable[[float], Any]) -> None:
    try:
        Logger.info("Running launcher tasks...", prefix=LOG_PREFIX)
        functions = Functions(on_success, on_cancel, on_error, set_status_label, set_deployment_details, update_progress_bars)


        # Settings & Data
        Logger.info("Getting config...", prefix=LOG_PREFIX)
        confirm_launch: bool = ConfigInterface.get("confirm_launch")
        force_reinstall: bool = ConfigInterface.get("force_reinstall")
        disable_mods: bool = ConfigInterface.get("disable_mods")
        disable_fastflags: bool = ConfigInterface.get("disable_fastflags")
        static_version_folder: bool = ConfigInterface.get("static_version_folder")
        use_roblox_version_folder: bool = ConfigInterface.get("use_roblox_version_folder")

        mod_updates: bool = ConfigInterface.get("mod_updates")
        multi_instance_launching: bool = ConfigInterface.get("multi_instance_launching")
        discord_rpc: bool = ConfigInterface.get("discord_rpc")

        installed_version: str = DataInterface.get_installed_version(mode)
        loaded_mods: list[str] = DataInterface.get_loaded_mods(mode)
        config: Config = Config(confirm_launch, force_reinstall, disable_mods, disable_fastflags, static_version_folder, use_roblox_version_folder, mod_updates, multi_instance_launching, discord_rpc, installed_version, loaded_mods)


        if config.disable_mods:
            mods: list[Mod] = []
        else:
            mods = ModManager.get_active(mode.lower())  # type: ignore
        mod_names: list[str] = [mod.name for mod in mods]


        # Deployment details
        Logger.info("Getting deployment details...", prefix=LOG_PREFIX)
        functions.set_status_label("launcher.progress.get_client_info")
        match mode:
            case "Player": binary_type: Literal["WindowsPlayer", "WindowsStudio64"] = "WindowsPlayer"
            case "Studio": binary_type = "WindowsStudio64"
            case _: raise ValueError(f'Invalid launch mode: "{mode}"!')
        latest_version: LatestVersion = LatestVersion(binary_type)
        functions.set_deployment_details(latest_version)
        functions.update_progress_bars(DEPLOYMENT_DETAILS_END_PROGRESS)
        if stop_event.is_set():
            return


        # Updates
        Logger.info("Checking for updates...", prefix=LOG_PREFIX)
        functions.set_status_label("launcher.progress.check_for_update")
        if should_update(mode, latest_version, config):
            Logger.info("Updating Roblox...", prefix=LOG_PREFIX)
            functions.set_status_label("launcher.progress.client_update")
            update_roblox(mode, config, functions, stop_event, latest_version)
            DataInterface.set_loaded_mods(mode, [])
        functions.update_progress_bars(DOWNLOAD_END_PROGRESS)
        if stop_event.is_set():
            return


        # Mutliple Instances
        skip_modloader: bool = False  # Don't load mods during multi-instance launching
        if RobloxInterface.is_roblox_running(mode):
            if config.multi_instance_launching:
                create_singleton_mutexes()
                skip_modloader = True

            else:
                if not messagebox.askokcancel(
                    title=Localizer.format(Localizer.Strings["dialog.confirm.title"], {"{app.name}": ProjectData.NAME}),
                    message=Localizer.format(Localizer.Strings["launcher.popup.permission_to_kill.on_update"], {
                        "{roblox.dynamic}": Localizer.Key("roblox.player") if mode == "Player" else Localizer.Key("roblox.studio"),
                        "{roblox.common}": Localizer.Key("roblox.common"),
                        "{roblox.player}": Localizer.Key("roblox.player"),
                        "{roblox.player_alt}": Localizer.Key("roblox.player_alt"),
                        "{roblox.studio}": Localizer.Key("roblox.studio"),
                        "{roblox.studio_alt}": Localizer.Key("roblox.studio_alt")
                })): return functions.on_cancel()
                RobloxInterface.kill_existing_instances(mode)

        elif config.multi_instance_launching:
            create_singleton_mutexes()
        if stop_event.is_set():
            return


        # Mods
        version_folder: Path = get_version_dir(mode, latest_version, config)
        if not skip_modloader or not config.disable_mods:
            if config.mod_updates:
                functions.set_status_label("launcher.progress.check_mod_update")
                Logger.info("Checking for mod updates...", prefix=LOG_PREFIX)

                outdated_mods: list[Mod] = []
                for mod in mods:
                    if mod.archive:  # mod udpater is not compatible with archived mods
                        continue

                    if ModUpdater.check_for_updates(mod.path, latest_version):
                        outdated_mods.append(mod)

                if outdated_mods:
                    functions.update_progress_bars(MOD_UPDATER_START_PROGRESS)
                    functions.set_status_label("launcher.progress.mod_update")
                    Logger.info(f"Updating mods...", prefix=LOG_PREFIX)

                    failed_mod_updates: list[str] = []
                    outdated_mod_count: int = len(outdated_mods)
                    for i, mod in enumerate(outdated_mods, start=1):
                        try:
                            ModUpdater.update_mod(mod.path, latest_version)
                        except Exception as e:
                            Logger.error(f"Mod update failed: '{mod.name}'. {type(e).__name__}: {e}",prefix=LOG_PREFIX)
                            failed_mod_updates.append(mod.name)
                        progress: float = MOD_UPDATER_START_PROGRESS + ((MOD_UPDATER_END_PROGRESS - MOD_UPDATER_START_PROGRESS) / outdated_mod_count) * i
                        functions.update_progress_bars(progress)

                    if failed_mod_updates:
                        messagebox.showwarning(ProjectData.NAME, Localizer.format(Localizer.Strings["launcher.warning.failed_mod_updates"], {"{failed_mods}": ", ".join(f"'{mod}'" for mod in failed_mod_updates)}))
            functions.update_progress_bars(MOD_UPDATER_END_PROGRESS)

            Logger.info("Deploying mods...", prefix=LOG_PREFIX)
            functions.set_status_label("launcher.progress.deploying_mods")
            ModManager.deploy_mods(version_folder, mods)  # type: ignore
            DataInterface.set_loaded_mods(mode=mode, value=mod_names)
        functions.update_progress_bars(MOD_DEPLOY_END_PROGRESS)
        if stop_event.is_set():
            return


        # FastFlags
        Logger.info("Deploying FastFlags...")
        if config.disable_fastflags: fastflag_profiles: list[FastFlagProfile] = []
        else: fastflag_profiles = FastFlagManager.get_active(mode=mode.lower(), sorted=True)  # type: ignore
        if not config.discord_rpc: manual_override: dict = {}
        else: manual_override = {"FLogNetwork": "7"}

        clientsettings_file: Path = version_folder / "ClientSettings" / "ClientAppSettings.json"
        FastFlagManager.deploy_profiles(clientsettings_file, fastflag_profiles, manual_override)
        functions.update_progress_bars(FASTFLAG_DEPLOY_END_PROGRESS)
        if stop_event.is_set():
            return


        # Custom integrations
        CustomIntegrationManager.launch_active_integrations(mode=mode.lower(), ignore_errors=True)  # type: ignore
        functions.update_progress_bars(CUSTOM_INTEGRATIONS_END_PROGRESS)


        # Launch Roblox
        Logger.info("Launching Roblox...")
        functions.set_status_label("launcher.progress.launch_client")
        functions.update_progress_bars(LAUNCH_END_PROGRESS)
        target: Path = version_folder / f"Roblox{mode}Beta.exe"
        timestamp: int = int(time.time() * 1000)
        args: str = ""
        if deeplink:
            args = "+".join([
                item if not item.startswith("launchtime:") else f"launchtime:{timestamp}"
                for item in deeplink.split("+")
            ])
            args = f"\"{str(target)}\" {args}"
        else:
            args =  f"\"{str(target)}\""
        subprocess.Popen(args)

        time.sleep(1)


    except Exception as e:
        return functions.on_error(e)

    else:
        return functions.on_success(config.discord_rpc)
# endregion


# region update
def should_update(mode: Literal["Player", "Studio"], latest_version: LatestVersion, config: Config) -> bool:
    if config.force_reinstall:
        Logger.info("Forced Roblox reinstallation!")
        return True
    elif not get_version_dir(mode, latest_version, config).is_dir():
        return True
    elif config.installed_version != latest_version.guid:
        return True
    return False


def update_roblox(mode: Literal["Player", "Studio"], config: Config, functions: Functions, stop_event: Event, latest_version: LatestVersion) -> None:
    package_manifest = PackageManifest(latest_version.guid)
    install_target: Path = Directories.VERSIONS / (mode if config.static_version_folder else latest_version.guid)

    # Get filemap
    response: Response = requests.get(Api.GitHub.FILEMAP)
    data: dict = response.json()
    pacakage_map: dict[str, Path] = {key: Path(install_target, *value) for key, value in data["common"].items()}
    pacakage_map.update({key: Path(install_target, *value) for key, value in data[mode.lower()].items()})

    # Kill existing instances
    if RobloxInterface.is_roblox_running(mode):
        if not messagebox.askokcancel(
            title=Localizer.format(Localizer.Strings["dialog.confirm.title"], {"{app.name}": ProjectData.NAME}),
            message=Localizer.format(Localizer.Strings["launcher.popup.permission_to_kill.on_update"], {
                "{roblox.dynamic}": Localizer.Key("roblox.player") if mode == "Player" else Localizer.Key("roblox.studio"),
                "{roblox.common}": Localizer.Key("roblox.common"),
                "{roblox.player}": Localizer.Key("roblox.player"),
                "{roblox.player_alt}": Localizer.Key("roblox.player_alt"),
                "{roblox.studio}": Localizer.Key("roblox.studio"),
                "{roblox.studio_alt}": Localizer.Key("roblox.studio_alt")
        })): return functions.on_cancel()
        RobloxInterface.kill_existing_instances(mode)

    # Clear unknown versions
    Logger.info("Cleaning versions folder...", prefix=LOG_PREFIX)
    if Directories.VERSIONS.exists():
        for path in Directories.VERSIONS.iterdir():
            if path.is_file():
                try: path.unlink()
                except PermissionError: continue
            elif path.is_dir():
                # Don't remove studio if running in player mode, don't remove player if running in studio mode
                if config.static_version_folder:
                    if path.name != ("Studio" if mode == "Player" else "Player"):
                        shutil.rmtree(path)
                elif not (path / ("RobloxStudioBeta.exe" if mode == "Player" else "RobloxPlayerBeta.exe")).exists():
                    shutil.rmtree(path)
    if stop_event.is_set():
        return

    # Clear downloads cache (don't remove files for the current version)
    Logger.info("Cleaning downloads cache...", prefix=LOG_PREFIX)
    cache_dir: Path = (Directories.VERSIONS_CACHE / mode)
    hashes: set[str] = {package.md5 for package in package_manifest.packages}
    cached_packages: list[str] = []
    if cache_dir.exists():
        for path in cache_dir.iterdir():
            if path.is_file():
                if path.name not in hashes:
                    path.unlink(missing_ok=True)
                elif get_md5(path) not in hashes:
                    path.unlink(missing_ok=True)
                else:
                    cached_packages.append(path.name)
            elif path.is_dir(): shutil.rmtree(path, ignore_errors=True)
    if stop_event.is_set():
        return

    # Download missing files
    Logger.info("Downloading Roblox...")
    download_start_progress: float = DEPLOYMENT_DETAILS_END_PROGRESS
    download_end_progress: float = DOWNLOAD_END_PROGRESS
    functions.update_progress_bars(download_start_progress)
    missing_packages: list[Package] = [package for package in package_manifest.packages if package.md5 not in cached_packages]
    total: int = len(missing_packages)
    for i, package in enumerate(missing_packages):
        destination: Path = cache_dir / package.md5
        filesystem.download(package.source, destination)
        current_progress: float = download_start_progress + i * ((download_end_progress - download_start_progress) / total)
        functions.update_progress_bars(current_progress)
        if stop_event.is_set():
            return

    # Extract files to version folder
    Logger.info("Installing Roblox...")
    version_folder: Path = get_version_dir(mode, latest_version, config)
    version_folder.mkdir(parents=True, exist_ok=True)
    for package in package_manifest.packages:
        source: Path = Directories.VERSIONS_CACHE / mode / package.md5
        destination = pacakage_map[package.file]
        if package.file.endswith(".zip"):
            filesystem.extract(source, destination, ignore_filetype=True)
        else:
            shutil.copy(source, destination)

    Logger.info("Writing AppSettings.xml")
    with open(version_folder / "AppSettings.xml", "w") as file:
        file.write(APPSETTINGS)

    DataInterface.set_installed_version(mode, latest_version.guid)
# endregion


# region other
def get_version_dir(mode: Literal["Player", "Studio"], latest_version: LatestVersion, config: Config) -> Path:
    if config.use_roblox_version_folder:
        if config.static_version_folder:
            return (Directories.ROBLOX / "Versions" / mode).resolve()
        return (Directories.ROBLOX / "Versions" / latest_version.guid).resolve()
    else:
        if config.static_version_folder:
            return (Directories.VERSIONS / mode).resolve()
        return (Directories.VERSIONS / latest_version.guid).resolve()


def get_md5(path: Path) -> str:
        hasher = hashlib.md5()
        with open(path, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest().upper()


def create_singleton_mutexes() -> None:
    kernel32 = ctypes.windll.kernel32
    mutexes: list[str] = ["ROBLOX_singletonMutex", "ROBLOX_singletonEvent"]

    for mutex_name in mutexes:
        Logger.info(f"Creating mutex: {mutex_name}", prefix=LOG_PREFIX)
        mutex = kernel32.CreateMutexW(None, False, mutex_name)

        if mutex == 0:
            Logger.warning(f"Failed to create mutex: {mutex_name}. {ctypes.WinError()}", prefix=LOG_PREFIX)
        elif kernel32.GetLastError() == 193:
            Logger.warning(f"Mutex already exists: {mutex_name}", prefix=LOG_PREFIX)
# endregion