from pathlib import Path


class GlobalBasicSettingsError(Exception):
    pass


class GlobalBasicSettingsNotFoundError(GlobalBasicSettingsError):
    path: Path

    def __init__(self, path: Path) -> None:
        super().__init__(f"File not found: {path.resolve()}")
        self.path = path


class GlobalBasicSettingsPermissionError(GlobalBasicSettingsError):
    path: Path

    def __init__(self, path: Path) -> None:
        super().__init__(f"Permission denied: {path.resolve()}")
        self.path = path