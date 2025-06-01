from pathlib import Path
from typing import Optional, Literal, Any
import json

from modules.backend import ConfigEditor
from modules.filesystem import Files
from modules.logger import Logger

from natsort import natsorted


class FastFlagProfile:
    name: str
    data: dict[str, Any]
    player: bool
    studio: bool

    def __init__(self, name: str, data: dict[str, Any] = {}, player: bool = False, studio: bool = False) -> None:
        self.name = name
        self.data = data
        self.player = player
        self.studio = studio


    def rename(self, value: str) -> None:
        value = value.strip()
        if value.lower() == self.name.lower(): return

        # Check for existing profiles
        existing_profiles = {profile.name.lower() for profile in FastFlagManager.get_all()}
        if value.lower() in existing_profiles:
            raise FileExistsError(f"FastFlag Profile already exists: {value}")

        FastFlagManager.remove_from_config(self.name)
        self.name = value
        FastFlagManager.update_config(self)


    def remove(self) -> None:
        FastFlagManager.remove_from_config(self.name)


    def set_status(self, value: int) -> None:
        if value < 0 or value > 3: raise ValueError(f"Bad value: {value}")

        old_player: bool = self.player
        new_player: bool = value == 1 or value == 3
        old_studio: bool = self.studio
        new_studio: bool = value == 2 or value == 3

        try:
            self.player = new_player
            self.studio = new_studio
            FastFlagManager.update_config(self)
        except Exception:
            self.player = old_player
            self.studio = old_studio
            raise


    def set_data(self, data: dict[str, Any]) -> None:
        old_data: dict = self.data
        try:
            self.data = data
            FastFlagManager.update_config(self)
        except Exception:
            self.data = old_data
            raise


class FastFlagManager:
    LOG_PREFIX: str = "FastFlagManager"
    CONFIG_PATH: Path = Files.FASTFLAG_CONFIG
    ConfigEditor = ConfigEditor(CONFIG_PATH, delete_if_empty=True)


    @classmethod
    def _read(cls) -> list[dict]:
        try: return cls.ConfigEditor.read()
        except FileNotFoundError: return []
        except Exception as e:
            Logger.error(f"Unable to load config due to {type(e).__name__}: {e}", prefix=cls.LOG_PREFIX)
            raise


    @classmethod
    def _write(cls, data: list[dict]) -> None:
        cls.ConfigEditor.write(data)


    @classmethod
    def get_config(cls, *profiles: str, data: Optional[list[dict]] = None) -> list[FastFlagProfile]:
        if not data: data = cls._read()
        data_dict: dict = {item["name"]: item for item in data}

        configs: list[FastFlagProfile] = []
        for name in profiles:
            config: Optional[dict] = data_dict.get(name)
            if not config:
                continue

            fastflags: dict[str, Any] = config.get("data", {})
            player: bool = config.get("enabled", False)
            studio: bool = config.get("enabled_studio", False)
            if not isinstance(fastflags, dict): fastflags = {}
            if not isinstance(player, bool): player = False
            if not isinstance(studio, bool): studio = False

            try:  configs.append(FastFlagProfile(name, data=fastflags, player=player, studio=studio))
            except ValueError: continue

        return configs


    @classmethod
    def get_all(cls, sorted: bool = False) -> list[FastFlagProfile]:
        data: list[dict] = cls._read()
        names: list[str] = [item["name"] for item in data]
        configs: list[FastFlagProfile] = cls.get_config(*names, data=data)

        if sorted: return natsorted(configs, key=lambda mod: mod.name.lower())
        return configs


    @classmethod
    def get_active(cls, mode: Optional[Literal["player", "studio"]] = None, sorted: bool = False) -> list[FastFlagProfile]:
        match mode:
            case "player": return [profile for profile in cls.get_all(sorted=sorted) if profile.player]
            case "studio": return [profile for profile in cls.get_all(sorted=sorted) if profile.studio]
            case _: return [profile for profile in cls.get_all(sorted=sorted) if profile.player or profile.studio]


    @classmethod
    def update_config(cls, profile: FastFlagProfile) -> None:
        data: list[dict] = cls._read()
        data = [item for item in data if item.get("name") != profile.name]
        data.append({"name": profile.name, "enabled": profile.player, "enabled_studio": profile.studio, "data": profile.data})
        cls._write(data)


    @classmethod
    def remove_from_config(cls, name: str) -> None:
        data: list[dict] = cls._read()
        data = [item for item in data if item.get("name") != name]
        cls._write(data)


    @classmethod
    def deploy_active_profiles(cls, target_file: str | Path, mode: Optional[Literal["player", "studio"]] = None, manual_override: dict = {}) -> None:
        cls.deploy_profiles(target_file=target_file, profiles=cls.get_active(mode=mode), manual_override=manual_override)


    @classmethod
    def deploy_profiles(cls, target_file: str | Path, profiles: list[FastFlagProfile], manual_override: dict = {}) -> None:
        target_file = Path(target_file)
        Logger.info(f"Deploying FastFlag Profiles...", prefix=cls.LOG_PREFIX)

        fastflags: dict = {}
        for profile in profiles:
            fastflags.update(profile.data)
        if manual_override:
            fastflags.update(manual_override)
        
        if not fastflags:
            Logger.info("No active profiles found!", prefix=cls.LOG_PREFIX)
            target_file.unlink(missing_ok=True)
            return

        target_file.parent.mkdir(parents=True, exist_ok=True)
        with open(target_file, "w") as file:
            json.dump(fastflags, file, indent=4)