from dataclasses import dataclass
from typing import Optional


@dataclass
class Contributor:
    name: str
    url: Optional[str] = None


CONTRIBUTORS: list[Contributor] = sorted([], key=lambda item: item.name.casefold())

FEATURE_SUGGESTIONS: list[Contributor] = sorted([
    Contributor("Vortex", r"https://github.com/VolVortex"),
    Contributor("return_request", r"https://github.com/returnrqt"),
    Contributor("kw_roblox"),
    Contributor("NetSoftworks", r"https://github.com/netsoftwork"),
    Contributor("dooM", r"https://github.com/MistressDoom"),
    Contributor("toast"),
    Contributor("xale", r"https://github.com/fakexale")
], key=lambda item: item.name.casefold())

SPECIAL_THANKS: list[Contributor] = sorted([], key=lambda item: item.name.casefold())