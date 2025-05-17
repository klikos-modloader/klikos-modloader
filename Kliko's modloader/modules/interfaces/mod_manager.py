from pathlib import Path
from typing import Optional, Literal, Any
import shutil

from modules.backend import ConfigEditor
from modules.filesystem import Files, Directories, extract, EmptyFileNameError, ReservedFileNameError, InvalidFileNameError, TrailingDotError
from modules.logger import Logger

from natsort import natsorted


SUPPORTED_FILETPYES: set = {".zip", ".7z"}


class Mod:
    name: str
    path: Path
    archive: bool
    priority: int
    player: bool
    studio: bool

    def __init__(self, path: str | Path, priority: int = 0, player: bool = False, studio: bool = False) -> None:
        self.path = Path(path).resolve()
        self.archive = self.path.is_file()
        if self.archive and self.path.suffix not in SUPPORTED_FILETPYES: raise ValueError("Unsupported filetype!")
        self.name = self.path.stem if self.archive else self.path.name
        self.priority = priority
        self.player = player
        self.studio = studio


    def rename(self, value: str) -> None:
        value = value.strip()
        if value.lower() == self.name.lower(): return

        # Check for common errors
        if not value: raise EmptyFileNameError("Filename cannot be empty or whitespace.")
        if value.endswith("."): raise TrailingDotError("Filename cannot end with '.'")
        if not self.path.exists(): raise FileNotFoundError(str(self.path))
        FORBIDDEN_CHARS = set(r'/\:*?"<>|')
        if any(char in FORBIDDEN_CHARS for char in value): raise InvalidFileNameError(f"Invalid filename: {value}")
        FORBIDDEN_NAMES = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
        if value.upper() in FORBIDDEN_NAMES: raise ReservedFileNameError(f"Reserved filename: {value.upper()}")

        # Check for existing mods
        existing_mods = {path.stem.lower() if path.is_file() else path.name.lower() for path in self.path.parent.iterdir()}
        if value.lower() in existing_mods:
            raise FileExistsError(f"Mod already exists: {value}")
        target: Path = self.path.parent / value
        if self.archive: target = target.with_suffix(self.path.suffix)

        self.path.rename(target)
        ModManager.remove_from_config(self.name)
        self.path = target
        self.name = value
        ModManager.update_config(self)


    def remove(self) -> None:
        if self.path.exists():
            if self.archive: self.path.unlink()
            else: shutil.rmtree(self.path)
        ModManager.remove_from_config(self.name)


    def set_priority(self, value: int) -> None:
        old_value: int = self.priority
        try:
            self.priority = value
            ModManager.update_config(self)
        except Exception:
            self.priority = old_value
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
            ModManager.update_config(self)
        except Exception:
            self.player = old_player
            self.studio = old_studio
            raise


class ModManager:
    LOG_PREFIX: str = "ModManger"
    DIRECTORY: Path = Directories.MODS
    CONFIG_PATH: Path = Files.MOD_CONFIG
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
        data = [item for item in data if not (item.get("enabled", False) == False and item.get("enabled_studio", False) == False and item.get("priority", 0) == 0)]
        cls.ConfigEditor.write(data)


    @classmethod
    def get_config(cls, *mods: tuple[str, Path], data: Optional[list[dict]] = None) -> list[Mod]:
        if not data: data = cls._read()
        data_dict: dict = {item["name"]: item for item in data}

        configs: list[Mod] = []
        for name, path in mods:
            config: Optional[dict] = data_dict.get(name)
            if not config:
                try: configs.append(Mod(path))
                except ValueError: continue
                continue
            priority: int = config.get("priority", 0)
            player: bool = config.get("enabled", False)
            studio: bool = config.get("enabled_studio", False)
            if not isinstance(priority, int): priority = 0
            if not isinstance(player, bool): player = False
            if not isinstance(studio, bool): studio = False

            try:  configs.append(Mod(path, priority=priority, player=player, studio=studio))
            except ValueError: continue

        return configs


    @classmethod
    def get_all(cls, sort: Optional[Literal["name", "priority"]] = None) -> list[Mod]:
        if not cls.DIRECTORY.is_dir(): return []
        mods: list[tuple[str, Path]] = [(path.with_suffix("").name, path) for path in cls.DIRECTORY.iterdir() if path.is_dir() or (path.is_file() and path.suffix in SUPPORTED_FILETPYES)]
        configs: list[Mod] = cls.get_config(*mods)

        match sort:
            case "name": return natsorted(configs, key=lambda mod: mod.name.lower())
            case "priority": return sorted(configs, key=lambda mod: mod.priority)
            case _: return configs


    @classmethod
    def get_active(cls, mode: Optional[Literal["player", "studio"]] = None) -> list[Mod]:
        match mode:
            case "player": return [mod for mod in cls.get_all(sort="priority") if mod.player]
            case "studio": return [mod for mod in cls.get_all(sort="priority") if mod.studio]
            case _: return [mod for mod in cls.get_all(sort="priority") if mod.player or mod.studio]


    @classmethod
    def update_config(cls, mod: Mod) -> None:
        data: list[dict] = cls._read()
        data = [item for item in data if item.get("name") != mod.name]
        data.append({"name": mod.name, "enabled": mod.player, "enabled_studio": mod.studio, "priority": mod.priority})
        cls._write(data)


    @classmethod
    def remove_from_config(cls, name: str) -> None:
        data: list[dict] = cls._read()
        data = [item for item in data if item.get("name") != name]
        cls._write(data)


    @classmethod
    def deploy_active_mods(cls, target_directory: str | Path, mode: Optional[Literal["player", "studio"]] = None) -> None:
        cls.deploy_mods(target_directory=target_directory, mods=cls.get_active(mode=mode))


    @classmethod
    def deploy_mods(cls, target_directory: str | Path, mods: list[Mod]) -> None:
        target_directory = Path(target_directory)

        for mod in mods:
            Logger.info(f"Deploying mod: {mod.name}...", prefix=cls.LOG_PREFIX)
            if not mod.archive: shutil.copytree(mod.path, target_directory)
            else: extract(mod.path, target_directory)