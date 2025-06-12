from pathlib import Path

from modules.backend import ConfigEditor
from modules.filesystem import Files


class ShortcutsInterface:
    LOG_PREFIX: str = "ShortcutInterface"
    FILEPATH: Path = Files.SHORTCUTS_CONFIG
    EDITOR: ConfigEditor = ConfigEditor(FILEPATH, delete_if_empty=True)


    @classmethod
    def _read(cls) -> list[str]:
        try: return cls.EDITOR.read()
        except FileNotFoundError: return []


    @classmethod
    def get_all(cls) -> list[str]:
        """Returns a list of universeIds (NOT placeIds)"""
        return cls._read()


    @classmethod
    def remove(cls, universe_id: str) -> None:
        data: list[str] = cls._read()
        data = [item for item in data if item != universe_id]
        cls.EDITOR.write(data)


    @classmethod
    def add(cls, universe_id: str) -> None:
        data: list[str] = cls._read()
        data = [item for item in data if item != universe_id] + [universe_id]
        cls.EDITOR.write(data)