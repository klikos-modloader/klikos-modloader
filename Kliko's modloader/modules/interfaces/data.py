from pathlib import Path
from typing import Literal

from modules.backend import ConfigEditor
from modules.filesystem import Files


class DataInterface:
    LOG_PREFIX: str = "DataInterface"
    FILEPATH: Path = Files.DATA
    EDITOR: ConfigEditor = ConfigEditor(FILEPATH)


    @classmethod
    def _read(cls) -> dict:
        return cls.EDITOR.read()


    @classmethod
    def get_installed_version(cls, mode: Literal["Player", "Studio"]) -> str:
        try: data: dict = cls._read()
        except FileNotFoundError: return ""

        match mode:
            case "Player": return data.get("player_guid", "")
            case "Studio": return data.get("studio_guid", "")
            case _: raise ValueError(f"Invalid mode: {mode}")


    @classmethod
    def set_installed_version(cls, mode: Literal["Player", "Studio"], value: str) -> None:
        try: data: dict = cls._read()
        except FileNotFoundError: data = {}

        match mode:
            case "Player": data["player_guid"] = value
            case "Studio": data["studio_guid"] = value
            case _: raise ValueError(f"Invalid mode: {mode}")

        cls.EDITOR.write(data)


    @classmethod
    def get_loaded_mods(cls, mode: Literal["Player", "Studio"]) -> list[str]:
        return []
        # try: data: dict = cls._read()
        # except FileNotFoundError: return []

        # match mode:
        #     case "Player": return data.get("player_mods", [])
        #     case "Studio": return data.get("studio_mods", [])
        #     case _: raise ValueError(f"Invalid mode: {mode}")


    @classmethod
    def set_loaded_mods(cls, mode: Literal["Player", "Studio"], value: list[str]) -> None:
        return
        # try: data: dict = cls._read()
        # except FileNotFoundError: data = {}

        # match mode:
        #     case "Player": data["player_mods"] = value
        #     case "Studio": data["studio_mods"] = value
        #     case _: raise ValueError(f"Invalid mode: {mode}")

        # cls.EDITOR.write(data)