from typing import Optional
from pathlib import Path
import sys
import os


FROZEN: bool = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def _get_downloads_directory() -> Path:
    home: Path = Path.home()
    fallback: Path = home / "Downloads" if (home / "Downloads").exists() else home
    if os.name != "nt": return fallback

    try:
        # https://stackoverflow.com/a/35851955
        import ctypes
        from ctypes import windll, wintypes
        from uuid import UUID

        # ctypes GUID copied from MSDN sample code
        class GUID(ctypes.Structure):
            _fields_ = [
                ("Data1", wintypes.DWORD),
                ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD),
                ("Data4", wintypes.BYTE * 8)
            ] 

            def __init__(self, uuidstr):
                uuid = UUID(uuidstr)
                ctypes.Structure.__init__(self)
                self.Data1, self.Data2, self.Data3, \
                    self.Data4[0], self.Data4[1], rest = uuid.fields
                for i in range(2, 8):
                    self.Data4[i] = rest>>(8-i-1)*8 & 0xff

        SHGetKnownFolderPath = windll.shell32.SHGetKnownFolderPath
        SHGetKnownFolderPath.argtypes = [
            ctypes.POINTER(GUID), wintypes.DWORD,
            wintypes.HANDLE, ctypes.POINTER(ctypes.c_wchar_p)
        ]

        def _get_known_folder_path(uuidstr):
            pathptr = ctypes.c_wchar_p()
            guid = GUID(uuidstr)
            if SHGetKnownFolderPath(ctypes.byref(guid), 0, 0, ctypes.byref(pathptr)):
                raise ctypes.WinError()
            return pathptr.value

        FOLDERID_Download = '{374DE290-123F-4565-9164-39C4925E467B}'

        return Path(_get_known_folder_path(FOLDERID_Download))

    except Exception: return fallback


class Directories:
    ROOT: Path = (Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent.parent.parent).resolve()
    CRASHES: Path = ROOT / "Crashes"
    CONFIG: Path = ROOT / "config"
    MODS: Path = ROOT / "Mods"
    VERSIONS: Path = ROOT / "Versions"
    LAUNCHERS: Path = ROOT / "Launchers"
    CACHE: Path = ROOT / "cache"
    VERSIONS_CACHE: Path = CACHE / "downloads"
    MARKETPLACE_CACHE: Path = CACHE / "marketplace"
    MEIPASS: Optional[Path] = Path(sys._MEIPASS) if FROZEN else None  # type: ignore
    RESOURCES: Path = (MEIPASS if FROZEN else ROOT) / "resources"  # type: ignore

    DOWNLOADS: Path = _get_downloads_directory().resolve()
    ROBLOX: Path = Path.home() / "AppData" / "Local" / "Roblox"

    DEV: Path = ROOT / "dev"
    DEV_TRANSLATIONS: Path = DEV / "localization"


class Files:
    CONFIG: Path = Directories.CONFIG / "config.json"
    DATA: Path = Directories.CONFIG / "data.json"
    MOD_CONFIG: Path = Directories.CONFIG / "mods.json"
    FASTFLAG_CONFIG: Path = Directories.CONFIG / "fastflags.json"
    CUSTOM_INTEGRATIONS_CONFIG: Path = Directories.CONFIG / "launch_integrations.json"
    MARKETPLACE_CACHE_INDEX: Path = Directories.MARKETPLACE_CACHE / "index.json"
    GLOBAL_BASIC_SETTINGS: Path = Directories.ROBLOX / "GlobalBasicSettings_13.xml"


class Resources:
    FAVICON: Path = Directories.RESOURCES / "favicon.ico"
    BANNER: Path = Directories.RESOURCES / "banner.png"

    class Logo:
        DEFAULT: Path = Directories.RESOURCES / "logo" / "default.png"
        STUDIO: Path = Directories.RESOURCES / "logo" / "studio.png"
        CHRISTMAS: Path = Directories.RESOURCES / "logo" / "christmas.png"
        VALENTINE: Path = Directories.RESOURCES / "logo" / "valentine.png"
        TOAST: Path = Directories.RESOURCES / "logo" / "toast.png"

    class Common:
        class Light:
            BIN: Path = Directories.RESOURCES / "common" / "light" / "bin.png"
            SUCCESS: Path = Directories.RESOURCES / "common" / "light" / "success.png"
            WARNING: Path = Directories.RESOURCES / "common" / "light" / "warning.png"
            ERROR: Path = Directories.RESOURCES / "common" / "light" / "error.png"
            ATTENTION: Path = Directories.RESOURCES / "common" / "light" / "attention.png"
            INFO: Path = Directories.RESOURCES / "common" / "light" / "info.png"
            CLOSE: Path = Directories.RESOURCES / "common" / "light" / "close.png"
            FOLDER: Path = Directories.RESOURCES / "common" / "light" / "folder.png"
            ARROW_RIGHT: Path = Directories.RESOURCES / "common" / "light" / "arrow_right.png"
            DOWNLOAD: Path = Directories.RESOURCES / "common" / "light" / "download.png"
            OPEN_EXTERNAL: Path = Directories.RESOURCES / "common" / "light" / "open_external.png"
            EYE: Path = Directories.RESOURCES / "common" / "light" / "eye.png"
            CONFIGURE: Path = Directories.RESOURCES / "common" / "light" / "configure.png"
            ADD: Path = Directories.RESOURCES / "common" / "light" / "add.png"
        class Dark:
            BIN: Path = Directories.RESOURCES / "common" / "dark" / "bin.png"
            SUCCESS: Path = Directories.RESOURCES / "common" / "dark" / "success.png"
            WARNING: Path = Directories.RESOURCES / "common" / "dark" / "warning.png"
            ERROR: Path = Directories.RESOURCES / "common" / "dark" / "error.png"
            ATTENTION: Path = Directories.RESOURCES / "common" / "dark" / "attention.png"
            INFO: Path = Directories.RESOURCES / "common" / "dark" / "info.png"
            CLOSE: Path = Directories.RESOURCES / "common" / "dark" / "close.png"
            FOLDER: Path = Directories.RESOURCES / "common" / "dark" / "folder.png"
            ARROW_RIGHT: Path = Directories.RESOURCES / "common" / "dark" / "arrow_right.png"
            DOWNLOAD: Path = Directories.RESOURCES / "common" / "dark" / "download.png"
            OPEN_EXTERNAL: Path = Directories.RESOURCES / "common" / "dark" / "open_external.png"
            EYE: Path = Directories.RESOURCES / "common" / "dark" / "eye.png"
            CONFIGURE: Path = Directories.RESOURCES / "common" / "dark" / "configure.png"
            ADD: Path = Directories.RESOURCES / "common" / "dark" / "add.png"

    class Navigation:
        class Light:
            MODS: Path = Directories.RESOURCES / "nav" / "light" / "mods.png"
            MOD_GENERATOR: Path = Directories.RESOURCES / "nav" / "light" / "mod_generator.png"
            MARKETPLACE: Path = Directories.RESOURCES / "nav" / "light" / "marketplace.png"
            FASTFLAGS: Path = Directories.RESOURCES / "nav" / "light" / "fastflags.png"
            GLOBAL_BASIC_SETTINGS: Path = Directories.RESOURCES / "nav" / "light" / "global_basic_settings.png"
            INTEGRATIONS: Path = Directories.RESOURCES / "nav" / "light" / "integrations.png"
            CUSTOM_INTEGRATIONS: Path = Directories.RESOURCES / "nav" / "light" / "custom_integrations.png"
            SETTINGS: Path = Directories.RESOURCES / "nav" / "light" / "settings.png"
            ABOUT: Path = Directories.RESOURCES / "nav" / "light" / "about.png"
        class Dark:
            MODS: Path = Directories.RESOURCES / "nav" / "dark" / "mods.png"
            MOD_GENERATOR: Path = Directories.RESOURCES / "nav" / "dark" / "mod_generator.png"
            MARKETPLACE: Path = Directories.RESOURCES / "nav" / "dark" / "marketplace.png"
            FASTFLAGS: Path = Directories.RESOURCES / "nav" / "dark" / "fastflags.png"
            GLOBAL_BASIC_SETTINGS: Path = Directories.RESOURCES / "nav" / "dark" / "global_basic_settings.png"
            INTEGRATIONS: Path = Directories.RESOURCES / "nav" / "dark" / "integrations.png"
            CUSTOM_INTEGRATIONS: Path = Directories.RESOURCES / "nav" / "dark" / "custom_integrations.png"
            SETTINGS: Path = Directories.RESOURCES / "nav" / "dark" / "settings.png"
            ABOUT: Path = Directories.RESOURCES / "nav" / "dark" / "about.png"

    class Large:
        class Light:
            WIFI_OFF: Path = Directories.RESOURCES / "large" / "light" / "wifi_off.png"
            FILE_NOT_FOUND: Path = Directories.RESOURCES / "large" / "light" / "file_not_found.png"
        class Dark:
            WIFI_OFF: Path = Directories.RESOURCES / "large" / "dark" / "wifi_off.png"
            FILE_NOT_FOUND: Path = Directories.RESOURCES / "large" / "dark" / "file_not_found.png"

    class Marketplace:
        MASK: Path = Directories.RESOURCES / "marketplace" / "mask.png"
        class Light:
            PLACEHOLDER: Path = Directories.RESOURCES / "marketplace" / "light" / "placeholder.png"
        class Dark:
            PLACEHOLDER: Path = Directories.RESOURCES / "marketplace" / "dark" / "placeholder.png"

    class Brands:
        class Light:
            GITHUB: Path = Directories.RESOURCES / "brands" / "light" / "github.png"
            DISCORD: Path = Directories.RESOURCES / "brands" / "light" / "discord.png"
        class Dark:
            GITHUB: Path = Directories.RESOURCES / "brands" / "dark" / "github.png"
            DISCORD: Path = Directories.RESOURCES / "brands" / "dark" / "discord.png"
        class Normal:
            GITHUB: Path = Directories.RESOURCES / "brands" / "normal" / "github.png"
            DISCORD: Path = Directories.RESOURCES / "brands" / "normal" / "discord.png"