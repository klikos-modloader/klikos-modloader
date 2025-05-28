from pathlib import Path
from typing import Callable
from copy import deepcopy
import json


class Localizer:
    class Metadata:
        DEFAULT_DIRECTORY: Path = Path(__file__).parent.resolve() / "strings"
        DEFAULT_LANGUAGE: str = "en_US"
        LANGUAGES: dict[str, str] = {
            "en_US": "English (United States)"
        }
        LANGUAGES_REVERSE_DICT: dict[str, str] = {value: key for key, value in LANGUAGES.items()}
    class Key:
        value: str
        def __init__(self, value: str) -> None:
            self.value = value
    Strings: dict[str, str]

    _directories: list[Path]
    _initialized: bool = False
    _callback_dict: dict[str, Callable]
    _callback_id_counter: int = 0
    _available_languages: list[str]


    @classmethod
    def initialize(cls) -> None:
        if cls._initialized: raise RuntimeError("Localizer has already been initialized.")

        cls._directories = [cls.Metadata.DEFAULT_DIRECTORY]
        cls._callback_dict = {}
        cls._initialized = True
        cls._update_available_languages()


    @classmethod
    def add_strings_directory(cls, path: str | Path) -> None:
        if not cls._initialized: raise RuntimeError("Localizer was not initialized.")

        path = Path(path).resolve()
        cls._directories.append(path)
        cls._update_available_languages()


    @classmethod
    def format(cls, string: str, data: dict[str, str | Key]) -> str:
        for key, value in data.items():
            if isinstance(value, cls.Key):
                value = Localizer.Strings.get(value.value, value.value)
            string = string.replace(key, value)
        return string


    @classmethod
    def get_available_languages(cls) -> list[str]:
        return cls._available_languages


    @classmethod
    def _update_available_languages(cls) -> None:
        languages: list[str] = list(cls.Metadata.LANGUAGES_REVERSE_DICT)
        known_languages: set = set(cls.Metadata.LANGUAGES) | set(cls.Metadata.LANGUAGES_REVERSE_DICT)
        if len(cls._directories) > 1:
            for directory in cls._directories[1:]:
                if not directory.is_dir(): continue
                for file in directory.iterdir():
                    if file.is_file() and file.suffix == ".json":
                        name = file.stem
                        if name not in known_languages:
                            languages.append(name)
                            known_languages.add(name)
        cls._available_languages = languages


    @classmethod
    def set_language(cls, language: str) -> None:
        if not cls._initialized: raise RuntimeError("Localizer was not initialized.")

        language = cls.Metadata.LANGUAGES_REVERSE_DICT.get(language, language)
        default_language_filepath: Path = cls.Metadata.DEFAULT_DIRECTORY / f"{cls.Metadata.DEFAULT_LANGUAGE}.json"
        temporary_strings: dict = cls._load_language(default_language_filepath)

        if language == cls.Metadata.DEFAULT_LANGUAGE:
            cls.Strings = deepcopy(temporary_strings)
            cls._on_update()
            return

        for directory in cls._directories:
            filepath: Path = directory / f"{language}.json"
            if filepath.exists():
                temporary_strings = cls._deep_merge(temporary_strings, cls._load_language(filepath))
                cls.Strings = deepcopy(temporary_strings)
                cls._on_update()
                return

        raise ValueError(f"Language '{language}' not available! Available languages are {', '.join(cls.Metadata.LANGUAGES.keys())}")


    @classmethod
    def add_callback(cls, callback: Callable) -> str:
        if not cls._initialized: raise RuntimeError("Localizer was not initialized.")

        cls._callback_id_counter += 1
        id: str = str(cls._callback_id_counter)
        if callable(callback): cls._callback_dict[id] = callback
        return id


    @classmethod
    def remove_callback(cls, id: str) -> None:
        if not cls._initialized: raise RuntimeError("Localizer was not initialized.")
        cls._callback_dict.pop(id, None)


    @classmethod
    def _on_update(cls) -> None:
        for callback in list(cls._callback_dict.values()):
            try: callback()
            except Exception: continue


    @staticmethod
    def _load_language(filepath: Path) -> dict:
        with open(filepath, "r", encoding="utf-8") as file:
            data: dict = json.load(file)
        return data


    @classmethod
    def _deep_merge(cls, dict1: dict, dict2: dict) -> dict:
        for key, value in dict2.items():
            if isinstance(value, dict) and key in dict1 and isinstance(dict1[key], dict):
                dict1[key] = cls._deep_merge(dict1[key], value)
            else: dict1[key] = value
        return dict1