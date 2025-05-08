from pathlib import Path
import os


def open(path: str | Path) -> None:
    if isinstance(path, str): path = Path(path)
    path = path.resolve()
    os.startfile(path)