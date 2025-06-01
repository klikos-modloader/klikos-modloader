from pathlib import Path
from typing import Optional, Literal, Any
import json
import os

from modules.backend import ConfigEditor
from modules.filesystem import Files
from modules.logger import Logger

from natsort import natsorted


class CustomIntegration:
    path: Path
    name: str
    args: str
    player: bool
    studio: bool

    def __init__(self, path: Path, args: str = "", player: bool = False, studio: bool = False) -> None:
        self.path = path.resolve()
        self.name = path.name
        self.args = args
        self.player = player
        self.studio = studio


    def launch(self) -> None:
        os.startfile(self.path, arguments=self.args)


    def remove(self) -> None:
        CustomIntegrationManager.remove_from_config(str(self.path))


    def set_args(self, value: str) -> None:
        old_value: str = self.args
        try:
            self.args = value
            CustomIntegrationManager.update_config(self)
        except Exception:
            self.args = old_value
            raise


    def set_status(self, value: int) -> None:
        if value < 0 or value > 3: raise ValueError(f"Bad value: {value}")

        old_player: bool = self.player
        new_player: bool = value == 1 or value == 3
        old_studio: bool = self.studio
        new_studio: bool = value == 2 or value == 3

        try:
            self.player = new_player
            self.studio = new_studio
            CustomIntegrationManager.update_config(self)
        except Exception:
            self.player = old_player
            self.studio = old_studio
            raise


class CustomIntegrationManager:
    LOG_PREFIX: str = "CustomIntegrationManager"
    CONFIG_PATH: Path = Files.CUSTOM_INTEGRATIONS_CONFIG
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
    def get_config(cls, *profiles: str, data: Optional[list[dict]] = None) -> list[CustomIntegration]:
        if not data: data = cls._read()
        data_dict: dict = {item["filepath"]: item for item in data}

        configs: list[CustomIntegration] = []
        for file in profiles:
            config: Optional[dict] = data_dict.get(file)
            if not config:
                continue

            path: Path = Path(file)
            args: str = config.get("launch_args", "")
            player: bool = config.get("enabled", False)
            studio: bool = config.get("enabled_studio", False)
            if not isinstance(args, str): args = ""
            if not isinstance(player, bool): player = False
            if not isinstance(studio, bool): studio = False

            try: configs.append(CustomIntegration(path, args=args, player=player, studio=studio))
            except ValueError: continue

        return configs


    @classmethod
    def get_all(cls, sorted: bool = False) -> list[CustomIntegration]:
        data: list[dict] = cls._read()
        names: list[str] = [item["filepath"] for item in data]
        configs: list[CustomIntegration] = cls.get_config(*names, data=data)

        if sorted: return natsorted(configs, key=lambda mod: mod.name.lower())
        return configs


    @classmethod
    def get_active(cls, mode: Optional[Literal["player", "studio"]] = None, sorted: bool = False) -> list[CustomIntegration]:
        match mode:
            case "player": return [profile for profile in cls.get_all(sorted=sorted) if profile.player]
            case "studio": return [profile for profile in cls.get_all(sorted=sorted) if profile.studio]
            case _: return [profile for profile in cls.get_all(sorted=sorted) if profile.player or profile.studio]


    @classmethod
    def update_config(cls, profile: CustomIntegration) -> None:
        data: list[dict] = cls._read()
        data = [item for item in data if item.get("filepath") != str(profile.path)]
        data.append({"filepath": str(profile.path), "enabled": profile.player, "enabled_studio": profile.studio, "launch_args": profile.args})
        cls._write(data)


    @classmethod
    def remove_from_config(cls, filepath: str) -> None:
        data: list[dict] = cls._read()
        data = [item for item in data if item.get("filepath") != filepath]
        cls._write(data)


    @classmethod
    def launch_active_integrations(cls, mode: Optional[Literal["player", "studio"]] = None, ignore_errors: bool = False) -> None:
        cls.launch_integrations(cls.get_active(mode=mode), ignore_errors=ignore_errors)


    @classmethod
    def launch_integrations(cls, integrations: list[CustomIntegration], ignore_errors: bool = False) -> None:
        Logger.info("Launching Custom Integrations...", prefix=cls.LOG_PREFIX)

        for integration in integrations:
            try: integration.launch()
            except Exception as e:
                Logger.error(f'Failed to launch custom integration: "{integration.name}"! {type(e).__name__}: {e}')
                if not ignore_errors: raise