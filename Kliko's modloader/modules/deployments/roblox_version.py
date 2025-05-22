from typing import Literal

from packaging.version import Version  # type: ignore


class RobloxVersion(Version):
    binary_type: Literal["WindowsPlayer", "WindowsStudio64"]
    guid: str
    file_version: Version


    def __init__(self, binary_type: Literal["WindowsPlayer", "WindowsStudio64"], guid: str, file_version: Version | str) -> None:
        self.binary_type = binary_type
        self.guid = guid
        if isinstance(file_version, Version):
            self.file_version = file_version
        else:
            self.file_version = Version(file_version)