import sys
import platform

from modules.logger import Logger


IS_FROZEN = getattr(sys, "frozen", False)
REGISTRY_KEYS: dict[str, list[dict[str, str]]] = {
    "roblox": [
        {
            "path": r"Software\Classes\roblox",
            "value": r"URL: Roblox Protocol"
        },
        {
            "path": r"Software\Classes\roblox",
            "key": r"URL Protocol",
            "value": r""
        },
        {
            "path": r"Software\Classes\roblox\DefaultIcon",
            "value": rf'"{sys.executable}"'
        },
        {
            "path": r"Software\Classes\roblox\shell\open\command",
            "value": rf'"{sys.executable}" -l --deeplink %1'
        },
    ],
    "roblox-player": [
        {
            "path": r"Software\Classes\roblox-player",
            "value": r"URL: Roblox Protocol"
        },
        {
            "path": r"Software\Classes\roblox-player",
            "key": r"URL Protocol",
            "value": r""
        },
        {
            "path": r"Software\Classes\roblox-player\DefaultIcon",
            "value": rf'"{sys.executable}"'
        },
        {
            "path": r"Software\Classes\roblox-player\shell\open\command",
            "value": rf'"{sys.executable}" -l --deeplink %1'
        },
    ],
    "roblox-studio": [
        {
            "path": r"Software\Classes\roblox-studio",
            "value": r"URL: Roblox Protocol"
        },
        {
            "path": r"Software\Classes\roblox-studio",
            "key": r"URL Protocol",
            "value": r""
        },
        {
            "path": r"Software\Classes\roblox-studio\DefaultIcon",
            "value": rf'"{sys.executable}"'
        },
        {
            "path": r"Software\Classes\roblox-studio\shell\open\command",
            "value": rf'"{sys.executable}" -s --deeplink %1'
        },
    ],
    "Roblox.Place": [
        {
            "path": r"Software\Classes\Roblox.Place",
            "value": r"Roblox Place"
        },
        {
            "path": r"Software\Classes\Roblox.Place\DefaultIcon",
            "value": rf'"{sys.executable}"'
        },
        {
            "path": r"Software\Classes\Roblox.Place\shell\Open",
            "value": r"Open"
        },
        {
            "path": r"Software\Classes\Roblox.Place\shell\Open\command",
            "value": rf'"{sys.executable}" -s --deeplink %1'
        }
    ],
    "roblox-studio-auth": [
        {
            "path": r"Software\Classes\roblox-studio-auth",
            "value": r"URL: Roblox Protocol"
        },
        {
            "path": r"Software\Classes\roblox-studio-auth",
            "key": r"URL Protocol",
            "value": r""
        },
        {
            "path": r"Software\Classes\roblox-studio-auth\DefaultIcon",
            "value": rf'"{sys.executable}"'
        },
        {
            "path": r"Software\Classes\roblox-studio-auth\shell\open\command",
            "value": rf'"{sys.executable}" -s --deeplink %1'
        },
    ]
}


def set_registry_keys() -> None:
    if platform.system() != "Windows":
        Logger.warning("Cannot set registry keys! User is not on Windows.")
        return

    if not IS_FROZEN:
        Logger.warning("Cannot set registry keys! Environment not frozen.")
        return

    import winreg

    Logger.info("Setting registry keys...")

    for group, keys in REGISTRY_KEYS.items():
        for item in keys:
            path: str = item["path"]
            key_name: str = item.get("key", "")
            value: str = item["value"]

            try:
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, path) as key:
                    winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, value)

            except Exception as e:
                Logger.warning(f"Failed to set registry key for {path}! {type(e).__name__}: {e}")