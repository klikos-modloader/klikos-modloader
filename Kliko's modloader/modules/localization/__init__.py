from pathlib import Path
import json


class Localizer:
    class Metadata:
        DEFAULT_LANGUAGE: str = "en_US"
        LANGUAGES: dict = {
            "en_US": "English (United States)"
        }
    Strings: dict

    _DIRECTORY: Path = Path(__file__).parent.resolve() / "strings"
    _initialized: bool = False


    @classmethod
    def initialize(cls, language: str = Metadata.DEFAULT_LANGUAGE) -> None:
        if cls._initialized: raise RuntimeError("Localizer has already been initialized.")
        if language not in cls.Metadata.LANGUAGES: raise ValueError(f"Language '{language}' not available! Available languages are {', '.join(cls.Metadata.LANGUAGES.keys())}")

        default_language_filepath: Path = cls._DIRECTORY / f"{cls.Metadata.DEFAULT_LANGUAGE}.json"
        cls.Strings = cls._load_language(default_language_filepath)

        if language != cls.Metadata.DEFAULT_LANGUAGE:
            language_filepath: Path = cls._DIRECTORY / f"{language}.json"
            cls.Strings = cls._deep_merge(cls.Strings, cls._load_language(language_filepath))

        cls._initialized = True


    @classmethod
    def _load_language(cls, filepath: Path) -> dict:
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