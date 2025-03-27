import os
import json
from typing import Literal, Iterable
from pathlib import Path

from modules.filesystem import File

from .exceptions import *


# region Profile
class Profile:
    """
    A class object representing a fastflag profile.

    Attributes:
        name (str): The fastflag profile's name.
        Config (ProfileConfig): A dataclass storing the fastflag profile's configuration data.
    """

    name: str
    data: dict
    player: bool
    studio: bool


    def __init__(self, data: dict):
        name: str | None = data.get("name")
        if name is None:
            raise ValueError(f"Failed to load FastFlag profile! Name required:\n{json.dumps(data, indent=4)}")

        fastflags: dict = data.get("data")  # type: ignore
        player: bool = data.get("enabled")  # type: ignore
        studio: bool = data.get("enabled_studio")  # type: ignore

        if not isinstance(fastflags, dict): fastflags = {}
        if not isinstance(player, bool): player = False
        if not isinstance(studio, bool): studio = False

        self.name = name
        self.data = fastflags
        self.player = player
        self.studio = studio
# endregion


# region ProfileConfigEditor
class ProfileConfigEditor:
    FILEPATH: Path = File.FASTFLAGS_CONFIG


    @classmethod
    def read_file(cls) -> list[dict[str, str | dict | bool | None]]:
        if not cls.FILEPATH.is_file(): return []

        with open(cls.FILEPATH, "r") as file:
            data = json.load(file)
        return [
            item for item in data
            if isinstance(item.get("name"), str)
        ]


    @classmethod
    def write_file(cls, data: list[dict]) -> None:
        if not cls.FILEPATH.is_file():
            cls.FILEPATH.parent.mkdir(parents=True, exist_ok=True)
            cls.FILEPATH.touch(exist_ok=True)

        if not os.access(cls.FILEPATH, os.W_OK):
            raise ProfileConfigPermissionsError(path=cls.FILEPATH)

        if not data:
            cls.FILEPATH.unlink()
            return

        data = sorted(data, key=lambda item: item.get("name", ""))

        with open(cls.FILEPATH, "w") as file:
            json.dump(data, file, indent=4)


    @classmethod
    def update_item(cls, name: str, profile: Profile) -> None:
        """Updates a FastFlag profile in the configuration file."""

        data = cls.read_file()
        data = [item for item in data if item.get("name") != name]
        data.append({"name": profile.name, "enabled": profile.player, "enabled_studio": profile.studio, "data": profile.data})
        cls.write_file(data)
    

    @classmethod
    def add_item(cls, name: str) -> None:
        data = cls.read_file()
        if name in [item.get("name") for item in data]:
            raise ProfileAlreadyExistsError(name)

        profile = Profile({"name": name})
        data.append({"name": profile.name, "enabled": profile.player, "enabled_studio": profile.studio, "data": profile.data})
        cls.write_file(data)


    @classmethod
    def remove_item(cls, name: str) -> None:
        """Removes a FastFlag profile from the configuration file."""

        data = cls.read_file()
        data = [item for item in data if item.get("name") != name]
        cls.write_file(data)
# endregion


# region FastFlagManager
class FastFlagManager:
    @staticmethod
    def get_profiles() -> tuple[Profile, ...]:
        """Returns a tuple containing all FastFlag profiles found in the config file directory."""
        
        data: list[dict] = ProfileConfigEditor.read_file()
        return tuple(Profile(item) for item in data)


    @classmethod
    def get_active_profiles(cls, mode: Literal["Player", "Studio"]) -> tuple[Profile, ...]:
        """Returns a tuple containing all active FastFlag profiles for the given launch mode ('Player' or 'Studio')."""

        match mode:
            case "Player": return tuple(profile for profile in cls.get_profiles() if profile.player)
            case "Studio": return tuple(profile for profile in cls.get_profiles() if profile.studio)
            case _: raise ValueError(f"Invalid mode: {mode} | Mode must be 'Player' or 'Studio'")


    @classmethod
    def deploy_profiles(cls, profiles: Iterable[Profile], target: Path, data_override: dict | None = None) -> None:
        """Deploys the provided FastFlag profiles to the specified target file."""

        if not profiles and not data_override: return
        if not target.exists(): target.parent.mkdir()
        elif target.is_dir(): target = target / "ClientAppSettings.json"

        if not os.access(target.parent, os.W_OK | os.X_OK):
            raise FastFlagManagerPermissionsError(path=target)

        final_data: dict = {}
        for profile in profiles:final_data.update(profile.data)
        if data_override:final_data.update(data_override)

        with open(target, "w") as file:
            json.dump(final_data, file, indent=4)
# endregion