from pathlib import Path
from typing import Optional

from PIL import Image  # type: ignore
from customtkinter import CTkImage  # type: ignore


def get_ctk_image(light: Optional[str | Path | Image.Image] = None, dark: Optional[str | Path | Image.Image] = None, size: int | tuple[int, int] = 32) -> CTkImage:
    if light is not None and not isinstance(light, Image.Image): light = get_image(light)
    if dark is not None and not isinstance(dark, Image.Image): dark = get_image(dark)
    if isinstance(size, int): size = (size, size)
    return CTkImage(light, dark, size)  # type: ignore


def get_image(path: str | Path) -> Image.Image:
    return Image.open(path)