from pathlib import Path


class ModManagerError(Exception):
    pass


class ModManagerPermissionError(ModManagerError):
    name: str
    path: Path

    def __init__(self, name: str, path: Path) -> None:
        super().__init__(f"Write permission denied for {path.resolve()}")
        self.name = name
        self.path = path


class ModConfigEditorError(ModManagerError):
    pass


class ModConfigPermissionsError(ModConfigEditorError):
    path: Path

    def __init__(self, path: Path) -> None:
        super().__init__(f"Write permission denied fpr {path.resolve()}")
        self.path = path


class ModError(ModManagerError):
    pass


class ModPermissionError(ModError):
    name: str
    path: Path

    def __init__(self, name: str, path: Path) -> None:
        super().__init__(f"Write permission denied for {path.resolve()}")
        self.name = name
        self.path = path


class ModNotFoundError(ModError):
    name: str
    path: Path

    def __init__(self, name: str, path: Path) -> None:
        super().__init__(f"Directory does not exist: {path.resolve()}")
        self.name = name
        self.path = path


class ModAlreadyExistsError(ModError):
    name: str
    path: Path

    def __init__(self, name: str, path: Path) -> None:
        super().__init__(f"Another directory with the same name already exists: {path.resolve()}")
        self.name = name
        self.path = path