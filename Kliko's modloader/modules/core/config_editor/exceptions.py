from pathlib import Path


class ConfigError(Exception):
    pass


class ConfigPermissionError(ConfigError):
    path: Path

    def __init__(self, path: Path) -> None:
        super().__init__(f"Permission denied: {path.resolve()}")
        self.path = path


class ConfigCorruptError(ConfigError):
    path: Path

    def __init__(self, path: Path) -> None:
        super().__init__(f"Config file corrupted (Invalid JSON): {path.resolve()}")
        self.path = path