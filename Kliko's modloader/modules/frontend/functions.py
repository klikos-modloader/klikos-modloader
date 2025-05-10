from pathlib import Path
from typing import Optional, Literal

from PIL import Image  # type: ignore
from customtkinter import CTkImage  # type: ignore


def get_ctk_image(light: Optional[str | Path | Image.Image] = None, dark: Optional[str | Path | Image.Image] = None, size: int | Literal["auto"] | tuple[int, int] | tuple[int, Literal["auto"]] | tuple[Literal["auto"], int] = 32) -> CTkImage:
    if light is None and dark is None: raise ValueError("get_ctk_image(): light and dark can't both be 'None'")
    elif dark is None: dark = light
    elif light is None: light = dark
    if not isinstance(light, Image.Image): light = get_image(light)  # type: ignore
    if not isinstance(dark, Image.Image): dark = get_image(dark)  # type: ignore
    if size == "auto" or size == ("auto", "auto"): size = light.size
    elif isinstance(size, int): size = (size, size)
    else:
        width, height = light.size
        ratio: float = width / height
        if size[0] == "auto": size = (int(size[1]*ratio), size[1])
        elif size[1] == "auto": size = (size[0], int(size[0]/ratio))
    image: CTkImage = CTkImage(light, dark, size)
    return image  # type: ignore


def get_image(path: str | Path) -> Image.Image:
    return Image.open(path)
