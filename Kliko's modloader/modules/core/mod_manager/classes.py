import os
import shutil
import json
from typing import Optional, Literal, Iterable
from dataclasses import dataclass
from pathlib import Path

from modules.filesystem import File, Directory

from .exceptions import *


# region ModConfig
@dataclass
class ModConfig:
    """
    A dataclass storing the mod's configuration data.

    Attributes:
        priority (int): The mod's priority (load order).
        player (bool): Whether the mod is enabled for the Roblox Player
        studio (bool): Whether the mod is enabled for Roblox Studio
    """

    priority: int
    player: bool
    studio: bool

DefaultModConfig: ModConfig = ModConfig(priority=0, player=False, studio=False)
# endregion


# region Mod
class Mod:
    """
    A class object representing a mod.

    Attributes:
        name (str): The mod's name.
        path (Path): The mod's directory.
        Config (ModConfig): A dataclass storing the mod's configuration data.
    """

    name: str
    path: Path
    Config: ModConfig


    def __init__(self, path: Path, config: Optional[ModConfig] = None):
        self.name = path.name
        self.path = path
        self.Config = config or ModConfigEditor.get_config(self.name)  # type: ignore


    def delete(self) -> None:
        """Deletes the mod's files and removes its entry from the configuration file."""

        if not self.path.exists():
            raise ModNotFoundError(name=self.name, path=self.path)

        if self.path.is_symlink():
            self.path.unlink()

        # elif self.path.is_file():
        #     if not os.access(self.path.parent, os.W_OK):
        #         raise ModPermissionError(name=self.name, path=self.path)
        #     self.path.unlink()

        elif self.path.is_dir():
            if not os.access(self.path, os.W_OK | os.X_OK) or not os.access(self.path.parent, os.W_OK):
                raise ModPermissionError(name=self.name, path=self.path)

            for path in self.path.rglob("*"):
                if not path.exists():
                    continue

                if path.is_dir() and not os.access(path, os.W_OK | os.X_OK):
                    raise ModPermissionError(name=self.name, path=path)

                elif not os.access(path, os.W_OK):
                    raise ModPermissionError(name=self.name, path=path)

            shutil.rmtree(self.path)

        ModConfigEditor.remove_item(self.name)
# endregion


# region ModConfigEditor
class ModConfigEditor:
    FILEPATH: Path = File.MODS_CONFIG
    MODS_DIRECTORY: Path = Directory.MODS


    @classmethod
    def read_file(cls) -> list[dict[str, str | int | bool]]:
        if not cls.FILEPATH.is_file():
            return []

        with open(cls.FILEPATH, "r") as file:
            data = json.load(file)
        return data


    @classmethod
    def write_file(cls, data: list[dict[str, str | int | bool]]) -> None:
        def filter_default_values(data: list[dict[str, str | int | bool]]) -> list[dict[str, str | int | bool]]:
            return [
                item for item in data
                if not (
                    item.get("priority", DefaultModConfig.priority) == DefaultModConfig.priority
                    and item.get("enabled", DefaultModConfig.player) == DefaultModConfig.player
                    and item.get("enabled_studio", DefaultModConfig.studio) == DefaultModConfig.studio
                )
            ]

        if not cls.FILEPATH.is_file():
            cls.FILEPATH.parent.mkdir(parents=True, exist_ok=True)
            cls.FILEPATH.touch(exist_ok=True)
        
        if not os.access(cls.FILEPATH, os.W_OK):
            raise ModConfigPermissionsError(path=cls.FILEPATH)

        data = sorted(filter_default_values(data), key=lambda item: item.get("name", ""))

        if not data:
            cls.FILEPATH.unlink()
            return

        with open(cls.FILEPATH, "w") as file:
            json.dump(data, file, indent=4)


    @classmethod
    def get_config(cls, *names: str) -> ModConfig | tuple[ModConfig, ...]:
        """Returns the ModConfig for the given mod(s)."""

        configs: list[ModConfig] = []
        data = cls.read_file()
        data_dict = {item["name"]: item for item in data}

        for name in names:
            item = data_dict.get(name)
            if not item:
                configs.append(ModConfig(DefaultModConfig.priority, DefaultModConfig.player, DefaultModConfig.studio))
                continue
            
            priority: int = item.get("priority", DefaultModConfig.priority)  # type: ignore
            player: bool = item.get("enabled", DefaultModConfig.player)  # type: ignore
            studio: bool = item.get("enabled_studio", DefaultModConfig.studio)  # type: ignore

            configs.append(ModConfig(priority=priority, player=player, studio=studio))

        if len(configs) == 1:
            return configs[0]
        return tuple(configs)


    @classmethod
    def update_item(cls, name: str, config: ModConfig) -> None:
        """Updates a mod in the configuration file."""

        data = cls.read_file()
        data = [item for item in data if item.get("name") != name]
        data.append({"name": name, "priority": config.priority, "enabled": config.player, "enabled_studio": config.studio})
        cls.write_file(data)


    @classmethod
    def rename_item(cls, name: str, new: str) -> None:
        """Renames a mod in the configuration file."""

        if name == new:
            return
        
        path: Path = cls.MODS_DIRECTORY / name
        target: Path = cls.MODS_DIRECTORY / new

        if target.exists():
            raise ModAlreadyExistsError(name=name, path=target)
        if not path.exists():
            raise ModNotFoundError(name=name, path=path)
        if not os.access(path.parent, os.W_OK | os.X_OK):
            raise ModConfigPermissionsError(path=path.parent)

        path.rename(target)

        data = cls.read_file()
        data = [item if item.get("name") != name else {"name": new, "priority": item.get("priority", DefaultModConfig.priority), "enabled": item.get("enabled", DefaultModConfig.player), "enabled_studio": item.get("enabled_studio", DefaultModConfig.studio)}  for item in data]
        cls.write_file(data)


    @classmethod
    def remove_item(cls, *names: str) -> None:
        """Removes the specified mod(s) from the configuration file."""

        data = cls.read_file()
        data = [item for item in data if item.get("name") not in names]
        cls.write_file(data)
# endregion


# region ModManager
class ModManager:
    MODS_DIRECTORY: Path = Directory.MODS


    @classmethod
    def get_mods(cls) -> tuple[Mod, ...]:
        """Returns a tuple containing all mods found in the mods directory."""

        if not cls.MODS_DIRECTORY.is_dir(): return tuple()

        return tuple(Mod(path) for path in cls.MODS_DIRECTORY.iterdir() if path.is_dir())


    @classmethod
    def get_active_mods(cls, mode: Literal["Player", "Studio"]) -> tuple[Mod, ...]:
        """Returns a tuple containing all active mods for the given launch mode ('Player' or 'Studio')."""

        match mode:
            case "Player":
                return tuple(mod for mod in cls.get_mods() if mod.Config.player)
            case "Studio":
                return tuple(mod for mod in cls.get_mods() if mod.Config.studio)
            case _:
                raise ValueError(f"Invalid mode: {mode} | Mode must be 'Player' or 'Studio'")


    @classmethod
    def deploy_mods(cls, mods: Iterable[Mod], target: Path) -> None | tuple[Mod, ...]:
        """
        Deploys the provided mods to the specified target directory.

        If all mods were deployed successfully, returns None,
        otherwise returns a tuple containing the failed mods.

        Parameters:
            mods (Iterable[Mod]): The mods that should be deployed to the target directory.
            target (Path): The target directory where the mods will be deployed.

        Raises:
            ValueError: If the target path exists but isn't a directory.
            ModManagerPermissionError: If write or access permissions were denied for the target directory.
        """

        if not mods:
            return None

        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
        elif not target.is_dir():
            raise ValueError(f"Target path must be a directory: {target}")

        if not os.access(target, os.W_OK | os.X_OK):
            raise ModManagerPermissionError(name=target.name, path=target)

        failed_mods: list[Mod] = []

        for mod in mods:
            source: Path = mod.path
            if not source.is_dir():
                failed_mods.append(mod)
                continue

            if not os.access(source, os.R_OK | os.X_OK):
                failed_mods.append(mod)
                continue

            shutil.copytree(source, target, dirs_exist_ok=True)
        
        if failed_mods:
            return tuple(failed_mods)
        return None
# endregion