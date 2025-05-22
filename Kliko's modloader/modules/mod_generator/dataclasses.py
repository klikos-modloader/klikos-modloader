from typing import NamedTuple


class IconBlacklist(NamedTuple):
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