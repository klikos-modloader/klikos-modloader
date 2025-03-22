from pathlib import Path
import subprocess


def open(path: str | Path) -> None:
    path = Path(path)

    if path.is_file():
        path = path.parent
    
    subprocess.Popen(f"explorer \"{path}\"")