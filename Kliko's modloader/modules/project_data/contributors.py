from dataclasses import dataclass
from typing import Optional


@dataclass
class Contributor:
    name: str
    url: Optional[str] = None


CONTRIBUTORS: list[Contributor] = []

FEATURE_SUGGESTIONS: list[Contributor] = [
    Contributor("Vortex", r"https://github.com/VolVortex"),
    Contributor("return_request", r"https://github.com/returnrqt"),
    Contributor("kw_roblox"),
    Contributor("NetSoftworks", r"https://github.com/netsoftwork"),
    Contributor("dooM", r"https://github.com/MistressDoom")
]

SPECIAL_THANKS: list[Contributor] = []