from pathlib import Path
from threading import Lock
from tempfile import NamedTemporaryFile
import json
from copy import deepcopy

from modules.logger import Logger
from modules.filesystem import File

from .exceptions import ConfigPermissionError, ConfigCorruptError


class ConfigEditor:
    """Responsible for reading and writing to config/config.json"""

    FILEPATH: Path = File.CONFIG
    lock: Lock = Lock()
    DEFAULT_CONFIG: dict = {
        "appearance": "system",
        "language": "en_US",

        "check_for_updates": True,
        "confirm_launch": True,
        "disable_mods": False,
        "disable_fastflags": False,
        "deployment_info": False,

        "mod_updater": False,
        "multi_roblox": False,
        "discord_rpc": False,
        "activity_joining": False,
        "show_user_profile": False,
        "bloxstrap_rpc": False
    }


    @classmethod
    def write_file(cls, data: dict) -> None:
        cls.FILEPATH.parent.mkdir(parents=True, exist_ok=True)
        with cls.lock:
            try:
                with NamedTemporaryFile(mode="w", delete=False, dir=cls.FILEPATH.parent, suffix=".json") as tmp:
                    json.dump(data, tmp, indent=4)
                Path(tmp.name).replace(cls.FILEPATH)

            except PermissionError as e:
                Logger.error(f"Failed to update config due to PermissionError!", prefix="ConfigEditor")
                Path(tmp.name).unlink(missing_ok=True)
                raise ConfigPermissionError(Path(e.filename))

            except OSError as e:
                Logger.error(f"Failed to update config due to OSError: {e}", prefix="ConfigEditor")
                Path(tmp.name).unlink(missing_ok=True)
                raise

            except Exception as e:
                Logger.error(f"Failed to update config due to unexpected {type(e).__name__}: {e}", prefix="ConfigEditor")
                Path(tmp.name).unlink(missing_ok=True)
                raise


    @classmethod
    def read_file(cls) -> dict:
        if not cls.FILEPATH.is_file():
            Logger.warning("File not found! Reverting to default config...", prefix="ConfigEditor")
            data: dict = deepcopy(cls.DEFAULT_CONFIG)
            cls.write_file(data)
            return deepcopy(data)

        try:
            with open(cls.FILEPATH, "r") as file:
                data = json.load(file)
            return data

        except json.JSONDecodeError:
            Logger.error(f"Failed to load config due to JSONDecodeError!", prefix="ConfigEditor")
            raise ConfigCorruptError(cls.FILEPATH)

        except PermissionError:
            Logger.error(f"Failed to load config due to PermissionError!", prefix="ConfigEditor")
            raise ConfigPermissionError(cls.FILEPATH)

        except OSError as e:
            Logger.warning(f"Failed to load config due to OSError: {e}", prefix="ConfigEditor")
            raise
    

    @classmethod
    def get_active_language(cls) -> str:
        data: dict = cls.read_file()
        try:
            return data["language"]
        except KeyError:
            default_data: dict = deepcopy(cls.DEFAULT_CONFIG)
            data["language"] = default_data["language"]
            cls.write_file(data)
            return data["language"]