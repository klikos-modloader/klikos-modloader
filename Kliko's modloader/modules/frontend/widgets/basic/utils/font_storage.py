from typing import Literal, Optional

from customtkinter import CTkFont  # type: ignore


class FontStorage:
    _fonts: dict[str, CTkFont] = {}


    @classmethod
    def get(cls, size: Optional[int] = None, weight: Optional[Literal['normal', 'bold']] = None, slant: Literal['italic', 'roman'] = "roman", underline: bool = False, overstrike: bool = False) -> CTkFont:
        key: str = f"{size}-{weight}-{slant}-{underline}-{overstrike}"
        try: return cls._fonts[key]
        except KeyError:
            font: CTkFont = CTkFont(family="Segoe UI", size=size, weight=weight, slant=slant, underline=underline, overstrike=overstrike)  # type: ignore
            cls._fonts[key] = font
            return font