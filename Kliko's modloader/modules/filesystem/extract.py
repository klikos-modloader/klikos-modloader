from pathlib import Path
from zipfile import ZipFile

from py7zr import SevenZipFile # type: ignore


def extract(source: str | Path, destination: str | Path, ignore_filetype: bool = False) -> None:
    source = Path(source).resolve()
    destination = Path(destination).resolve()

    if not source.is_file(): raise FileNotFoundError(f"File not found: {source}")
    if destination.is_file(): raise NotADirectoryError(f"Destination exists but is not a directory: {destination}")

    if ignore_filetype:
        destination.mkdir(parents=True, exist_ok=True)
        with ZipFile(source, "r") as archive:
            archive.extractall(destination)
        return

    match source.suffix:
        case ".zip":
            destination.mkdir(parents=True, exist_ok=True)
            with ZipFile(source, "r") as archive:
                archive.extractall(destination)

        case ".7z":
            destination.mkdir(parents=True, exist_ok=True)
            with SevenZipFile(source, "r") as archive:
                archive.extractall(destination)

        case other: raise ValueError(f"Unsupported filetype: {other}")