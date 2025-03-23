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
        if language not in cls.METADATA["available"]: raise ValueError(f"Language '{language}' unavailable! Available lanaguages are: {', '.join(cls.METADATA['available'].keys())}")
        if cls.language == language: return

        cls.language = language

        default_filepath: Path = cls.DIRECTORY / f"{cls.METADATA['default']}.json"
        filepath: Path = cls.DIRECTORY / f"{language}.json"

        cls.strings = cls._load_language(default_filepath)

        if language != cls.METADATA["default"]:
            cls.strings.update(cls._load_language(filepath))


    @classmethod
    def _load_language(cls, filepath: Path) -> dict:
        with open(filepath, "r", encoding="utf-8") as file:
            data: dict = json.load(file)
        return data