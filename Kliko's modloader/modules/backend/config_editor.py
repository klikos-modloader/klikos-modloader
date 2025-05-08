from typing import Any
from pathlib import Path
import json


class ConfigEditor:
    file: Path
    delete_if_empty: bool


    def __init__(self, file: Path, delete_if_empty: bool = False):
        self.file = file
        self.delete_if_empty = delete_if_empty


    def read(self) -> Any:
        with open(self.file, "r") as file: return json.load(file)


    def write(self, data: dict | list) -> None:
        if not self.file.parent.exists(): self.file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file, "w") as file: json.dump(data, file, indent=4)
        if not data and self.delete_if_empty: self.file.unlink()