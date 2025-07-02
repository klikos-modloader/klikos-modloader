from pathlib import Path
from zipfile import ZipFile
from typing import Literal
import os

from py7zr import SevenZipFile # type: ignore


def compress(source: str | Path, destination: str | Path, format: Literal[".zip", ".7z"] = False, ignore_filetype: bool = False) -> None:
    """Destination may be a file or directory"""

    source = Path(source).resolve()
    destination = Path(destination).resolve()

    if not source.exists(): raise FileNotFoundError(f"Source not found: {source}")

    match format:
        case ".zip":
            if not ignore_filetype and destination.suffix != ".zip":
                destination = destination.with_name(f"{destination.name}.zip")
            destination.parent.mkdir(parents=True, exist_ok=True)

            if source.is_file():
                with ZipFile(destination, "w") as archive:
                    archive.write(source, source.name)

            elif source.is_dir():
                with ZipFile(destination, "w") as archive:
                    for dirpath, _, filenames in os.walk(source):
                        dirpath = Path(dirpath).resolve()
                        for filename in filenames:
                            filepath = dirpath / filename
                            arcname = filepath.relative_to(source)
                            archive.write(filepath, arcname)

            else: raise ValueError(f"Source is not a file or directory: {source}")

        case ".7z":
            if not ignore_filetype and destination.suffix != ".7z":
                destination = destination.with_name(f"{destination.name}.7z")
            destination.parent.mkdir(parents=True, exist_ok=True)

            if source.is_file():
                with SevenZipFile(destination, "w") as archive:
                    archive.write(source, source.name)

            elif source.is_dir():
                with SevenZipFile(destination, "w") as archive:
                    for dirpath, _, filenames in os.walk(source):
                        dirpath = Path(dirpath).resolve()
                        for filename in filenames:
                            filepath = dirpath / filename
                            arcname = filepath.relative_to(source)
                            archive.write(filepath, arcname)

            else: raise ValueError(f"Source is not a file or directory: {source}")

        case other: raise ValueError(f"Unsupported format: {other}")