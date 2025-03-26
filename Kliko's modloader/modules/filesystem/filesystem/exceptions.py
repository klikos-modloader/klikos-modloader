from pathlib import Path


class FileSystemError(Exception):
    pass


# region FileExtractError
class FileExtractError(FileSystemError):
    pass


class TargetNotADirectoryError(FileExtractError):
    pass


class SourceNotAFileError(FileExtractError):
    path: Path

    def __init__(self, path: Path) -> None:
        super().__init__(f"File not found: {path.resolve()}")
        self.path = path


class UnsupportedFormatError(FileExtractError):
    name: str
    supported_formats: list[str]

    def __init__(self, name: str, supported_formats: list[str]) -> None:
        super().__init__(f"Cannot extract {name} due to unsupported file extension. Supported files are: {', '.join(supported_formats)}")
        self.name = name
        self.supported_formats = supported_formats


class ExtractPermissionError(FileExtractError):
    path: Path

    def __init__(self, path: Path) -> None:
        super().__init__(f"Write permission denied for {path.resolve()}")
        self.path = path
# endregion


# region FileDownloadError
class FileDownloadError(FileSystemError):
    pass


class DownloadInProgressError(FileDownloadError):
    source: str
    target: Path

    def __init__(self, source: str, target: Path) -> None:
        super().__init__(f"Another download is already in progress: {source}")
        self.source = source
        self.target = target


class DownloadPermissionError(FileDownloadError):
    path: Path

    def __init__(self, path: Path) -> None:
        super().__init__(f"Write permission denied for {path.resolve()}")
        self.path = path


class DownloadSocketTimeoutError(FileDownloadError):
    timeout: int

    def __init__(self, timeout: int) -> None:
        super().__init__(f"Failed to establish a connection after {timeout} seconds.")
        self.timeout = timeout


class DownloadConnectionError(FileDownloadError):
    pass


class DownloadHTTPError(FileDownloadError):
    code: int
    reason: str

    def __init__(self, code: int, reason: str) -> None:
        super().__init__(f"HTTP error: {code} {reason}")
        self.code = code
        self.reason = reason
# endregion