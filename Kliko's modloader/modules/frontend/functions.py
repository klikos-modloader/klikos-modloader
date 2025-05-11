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



def crop_to_fit(image: Image.Image, target_ratio: float) -> Image.Image:
    w, h = image.size
    ratio = w/h
    if ratio == target_ratio: return image.copy()

    if ratio > target_ratio:
        new_h: int = h
        new_w: int = int(target_ratio * new_h)

    else:
        new_w = w
        new_h = int(new_w / target_ratio)

    resized: Image.Image = Image.new("RGBA", (new_w, new_h))
    paste_x: int = int((new_w - w)/2)
    paste_y: int = int((new_h - h)/2)
    resized.paste(image, (paste_x, paste_y))
    return resized