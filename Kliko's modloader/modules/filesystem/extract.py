import os
from zipfile import ZipFile
from pathlib import Path

from .exceptions import SourceNotAFileError, TargetNotADirectoryError, ExtractPermissionError, UnsupportedFormatError

# from py7zr import SevenZipFile


SUPPORTED_FORMATS: list[str] = [".zip"]


def extract(source: Path, destination: Path, ignore_filetype: bool = False) -> None:
    """
    Extracts the provided source archive to the destination directory.

    Parameters:
        source (Path): The source archive.
        destination (Path): The destination directory.
        ignore_filetype (bool, optional): If True, assumes the source is a .zip file, even if the file extension is different. Default: False
    
    Raises:
        UnsupportedFormatError: If the file format is not support and `ignore_filetype` is False.
        SourceNotAFileError: If the source path is not an existing file.
        TargetNotADirectoryError: If the destination exists and is not a directory.
        ExtractPermissionError: If write or access permissions were denied for the target directory.
    """

    if not ignore_filetype and source.suffix not in SUPPORTED_FORMATS:
        raise UnsupportedFormatError(source.name, SUPPORTED_FORMATS)
    if not source.is_file():
        raise SourceNotAFileError(source)
    if destination.is_file():
        raise TargetNotADirectoryError(f"Destination must be a directory! (destination: {destination.name})")

    destination.mkdir(parents=True, exist_ok=True)
    if not os.access(destination, os.W_OK | os.X_OK):
        raise ExtractPermissionError(destination)

    if ignore_filetype:
        with ZipFile(source, "r") as archive:
            archive.extractall(destination)
        return

    match source.suffix:
        case ".zip":
            with ZipFile(source, "r") as archive:
                archive.extractall(destination)

        # case ".7z":
        #     with SevenZipFile(source, "r") as archive:
        #         archive.extractall(destination)

        case _:
            raise UnsupportedFormatError(source.name, SUPPORTED_FORMATS)