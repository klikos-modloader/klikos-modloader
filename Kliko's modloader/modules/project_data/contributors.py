from typing import Optional


class Contributor:
    name: str
    url: Optional[str]

    def __init__(self, name: str, url: Optional[str] = None):
        self.name = name
        self.url = url


CONTRIBUTORS: list[Contributor] = []

FEATURE_SUGGESTIONS: list[Contributor] = [
    Contributor("Vortex", r"https://github.com/VolVortex"),
    Contributor("return_request", r"https://github.com/returnrqt"),
    Contributor("kw_roblox")
]

SPECIAL_THANKS: list[Contributor] = []