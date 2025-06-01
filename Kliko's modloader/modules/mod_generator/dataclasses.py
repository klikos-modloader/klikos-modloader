from typing import NamedTuple
from dataclasses import dataclass

from PIL import Image  # type: ignore


@dataclass
class GradientColor:
    stop: float
    color: tuple[int, int, int]


@dataclass
class AdditionalFile:
    image: Image.Image
    target: str


@dataclass
class IconBlacklist:
    prefixes: list[str]
    suffixes: list[str]
    keywords: list[str]
    strict: list[str]


class RemoteConfig:
    blacklist: IconBlacklist


    def __init__(self, data: dict) -> None:
        blacklist = data.get("blacklist", {})
        prefixes: list[str] = blacklist.get("prefixes", [])
        suffixes: list[str] = blacklist.get("suffixes", [])
        keywords: list[str] = blacklist.get("keywords", [])
        strict: list[str] = blacklist.get("strict", [])
        self.blacklist = IconBlacklist(prefixes, suffixes, keywords, strict)