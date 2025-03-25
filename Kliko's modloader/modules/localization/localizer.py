from pathlib import Path
import json


class Localizer:
    METADATA: dict = {
        "default": "en_US",
        "available": {
            "en_US": "English (United States)"
        }
    }

    DIRECTORY: Path = Path(__file__).parent / "strings"
    language: str | None = None
    strings: dict


    @classmethod
    def initialize(cls, language: str = METADATA["default"]) -> None:
        if language not in cls.METADATA["available"]:
            raise ValueError(f"Language '{language}' unavailable! Available lanaguages are: {', '.join(cls.METADATA['available'].keys())}")
        if cls.language == language: return

        cls.language = language

        default_filepath: Path = cls.DIRECTORY / f"{cls.METADATA['default']}.json"
        filepath: Path = cls.DIRECTORY / f"{language}.json"

        cls.strings = cls._load_language(default_filepath)

        if language != cls.METADATA["default"]:
            cls.strings = cls._deep_merge(cls.strings, cls._load_language(filepath))


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