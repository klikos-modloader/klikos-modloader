from pathlib import Path


class FastFlagManagerError(Exception):
    pass


class ProfileConfigEditorError(FastFlagManagerError):
    pass


class ProfileConfigPermissionsError(ProfileConfigEditorError):
    path: Path

    def __init__(self, path: Path) -> None:
        super().__init__(f"Write permission denied fpr {path.resolve()}")
        self.path = path


class ProfileError(FastFlagManagerError):
    pass


class ProfileAlreadyExistsError(ProfileError):
    name: str

    def __init__(self, name: str) -> None:
        super().__init__(f"FastFlag profile already exists: {name}")
        self.name = name


class FastFlagManagerPermissionsError(FastFlagManagerError):
    path: Path

    def __init__(self, path: Path) -> None:
        super().__init__(f"Write permission denied fpr {path.resolve()}")
        self.path = path