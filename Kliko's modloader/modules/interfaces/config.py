from pathlib import Path
from typing import Literal, Optional, Any
from copy import deepcopy

from modules.logger import Logger
from modules.backend import ConfigEditor
from modules.filesystem import Files
from modules.localization import Localizer


class ConfigInterface:
    _dev_mode: bool | None = None
    LOG_PREFIX: str = "ConfigInterface"
    FILEPATH: Path = Files.CONFIG
    EDITOR: ConfigEditor = ConfigEditor(FILEPATH)
    DEFAULT_CONFIG: dict = {
        "appearance": "system",
        "language": "en_US",

        "check_for_updates": True,
        "confirm_launch": True,
        "deployment_info": False,
        "force_reinstall": False,
        "disable_mods": False,
        "disable_fastflags": False,
        "menu_size": {
            "w": 1100,
            "h": 600
        },

        "mod_updates": False,
        "multi_instance_launching": False,
        "discord_rpc": False,
        "activity_joining": False,
        "show_user_in_rpc": False,
        "bloxstrap_rpc_sdk": False
    }


    @classmethod
    def _read(cls) -> dict:
        try: return cls.EDITOR.read()
        except Exception as e:
            Logger.error(f"Unable to load config due to {type(e).__name__}: {e}", prefix=cls.LOG_PREFIX)
            cls.restore_default_settings()
            return deepcopy(cls.DEFAULT_CONFIG)


    @classmethod
    def verify_file_integrity(cls) -> None:
        Logger.info("Verifying config...", prefix=cls.LOG_PREFIX)
        if not cls.FILEPATH.exists():
            Logger.warning(f"{cls.FILEPATH.name} not found! Restoring default settings...", prefix=cls.LOG_PREFIX)
            cls.restore_default_settings(silent=True)
            return

        data: dict = cls._read()
        if data == cls.DEFAULT_CONFIG: return

        missing_keys: list[str] = [key for key in cls.DEFAULT_CONFIG if key not in data]
        if missing_keys:
            Logger.warning(f"Restoring missing keys: {', '.join(missing_keys)}", prefix=cls.LOG_PREFIX)
            for key in missing_keys: data[key] = cls.DEFAULT_CONFIG[key]
            cls.EDITOR.write(data)



    @classmethod
    def restore_default_settings(cls, silent: bool = False) -> None:
        if not silent: Logger.info("Restoring default settings...", prefix=cls.LOG_PREFIX)
        if cls.FILEPATH.exists(): cls.FILEPATH.unlink()
        cls.EDITOR.write(cls.DEFAULT_CONFIG)


    @classmethod
    def get_appearance_mode(cls) -> Literal["light", "dark", "system"]:
        data: dict = cls._read()
        appearance_mode: Literal["light", "dark", "system"] = data.get("appearance")  # type: ignore
        if isinstance(appearance_mode, str): appearance_mode = appearance_mode.lower()  # type: ignore
        if appearance_mode not in {"light", "dark", "system"}: appearance_mode = "system"
        return appearance_mode


    @classmethod
    def set_appearance_mode(cls, mode: Literal["light", "dark", "system"]) -> None:
        data: dict = cls._read()
        data["appearance"] = mode
        cls.EDITOR.write(data)


    @classmethod
    def get_language(cls) -> str:
        data: dict = cls._read()
        language: str = data.get("language")  # type: ignore
        if language not in Localizer.Metadata.LANGUAGES and language not in Localizer.get_available_languages(): language = Localizer.Metadata.DEFAULT_LANGUAGE
        return language


    @classmethod
    def set_language(cls, language: str) -> str:
        if language not in Localizer.Metadata.LANGUAGES and language not in Localizer.get_available_languages():
            Logger.error(f"Unsupported language: '{language}'", prefix=cls.LOG_PREFIX)
            raise ValueError(f"Unsupported language: '{language}'. Must be {', '.join(Localizer.Metadata.LANGUAGES)}")

        data: dict = cls._read()
        language: str = data.get("language")  # type: ignore
        return language


    @classmethod
    def get_menu_size(cls) -> tuple[int, int]:
        menu_size: dict = cls.get("menu_size", cls.DEFAULT_CONFIG["menu_size"])

        width: int | Any = menu_size.get("w")
        if not isinstance(width, int): width = cls.DEFAULT_CONFIG["menu_size"]["w"]
        elif width < 1: width = 1

        height: int | Any = menu_size.get("h")
        if not isinstance(height, int): height = cls.DEFAULT_CONFIG["menu_size"]["h"]
        elif height < 1: height = 1

        return width, height


    @classmethod
    def set_menu_size(cls, width: Optional[int] = None, height: Optional[int] = None) -> None:
        if width is None and height is None: return

        menu_size: dict = cls.get("menu_size", cls.DEFAULT_CONFIG["menu_size"])

        if width is None:
            width = menu_size.get("w")
            if not isinstance(width, int): width = cls.DEFAULT_CONFIG["menu_size"]["w"]
            elif width < 1: width = 1

        if height is None:
            height = menu_size.get("h")
            if not isinstance(height, int): height = cls.DEFAULT_CONFIG["menu_size"]["h"]
            elif height < 1: height = 1

        menu_size["w"] = width
        menu_size["h"] = height
        cls.set("menu_size", menu_size)


    @classmethod
    def dev_mode_enabled(cls) -> bool:
        if cls._dev_mode is not None: return cls._dev_mode
        dev_mode: bool = cls.get("developer", False)
        cls._dev_mode = dev_mode
        return dev_mode


    @classmethod
    def get(cls, key: str, default: Optional[Any] = ...) -> Any:
        data: dict = cls._read()
        if default == ...: default = cls.DEFAULT_CONFIG.get(key, ...)
        if key not in data and default == ...:
            Logger.error(f"Setting not found in config file: '{key}'", prefix=cls.LOG_PREFIX)
            raise KeyError(f"Setting not found in config file: '{key}'")
        return data.get(key, default)


    @classmethod
    def set(cls, key: str, value: Any) -> None:
        data: dict = cls._read()
        data[key] = value
        cls.EDITOR.write(data)