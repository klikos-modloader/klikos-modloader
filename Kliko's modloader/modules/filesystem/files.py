from pathlib import Path

from .directories import Directory


class File:
    """Dataclass storing the path objects to important files."""

    CONFIG: Path = Directory.CONFIG / "config.json"
    MODS_CONFIG: Path = Directory.CONFIG / "mods.json"