from xml.etree import ElementTree as xml
from pathlib import Path
from threading import Lock
from typing import Any

from modules.filesystem import File

from .exceptions import GlobalBasicSettingsPermissionError, GlobalBasicSettingsNotFoundError


class GlobalBasicSettingsEditor:
    """Responsible for reading and writing to GlobalBasicSettings_13.xml"""

    FILEPATH: Path = File.GLOBALBASICSETTINGS
    lock: Lock = Lock()


    @classmethod
    def get_tree(cls) -> xml.ElementTree:
        if not cls.FILEPATH.is_file(): raise GlobalBasicSettingsNotFoundError(cls.FILEPATH)

        try: return xml.parse(cls.FILEPATH)
        except PermissionError: raise GlobalBasicSettingsPermissionError(cls.FILEPATH)


    @classmethod
    def update_element(cls, tree: xml.ElementTree, name: str, value: Any) -> None:
        element: xml.Element | None = tree.find(f".//*[@name='{name}']")
        if element is None: raise KeyError(f"Element not found: {name}")

        element.text = value
        try: tree.write(cls.FILEPATH)
        except FileNotFoundError: raise GlobalBasicSettingsNotFoundError(cls.FILEPATH)
        except PermissionError: raise GlobalBasicSettingsPermissionError(cls.FILEPATH)


    @classmethod
    def update_sub_element(cls, tree: xml.ElementTree, name: str, subname: str, value: Any) -> None:
        element: xml.Element | None = tree.find(f".//*[@name='{name}']")
        if element is None: raise KeyError(f"Element not found: {name}")

        sub_element = element.find(subname)
        if sub_element is None: raise KeyError(f"Element not found: {name}.{subname}")

        sub_element.text = value
        try: tree.write(cls.FILEPATH)
        except FileNotFoundError: raise GlobalBasicSettingsNotFoundError(cls.FILEPATH)
        except PermissionError: raise GlobalBasicSettingsPermissionError(cls.FILEPATH)