from pathlib import Path
from typing import Optional, Literal

from PIL import Image, ImageDraw  # type: ignore
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

def apply_rounded_corners(image: Image.Image, radius: int = 4) -> Image.Image:
        diameter: int = radius * 2
        image = image.convert("RGBA")

        mask: Image.Image = Image.new("L", (diameter, diameter))
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, diameter, diameter), fill=255)
        # with Image.open(Assets.RoundedRectangle.Radius4px.BACKGROUND) as mask:
        #      mask = mask.split()[-1]
        mask_w, mask_h = mask.size
        corner_w, corner_h = mask_w//2, mask_h//2

        top_left = mask.crop((0, 0, corner_w, corner_h))
        top_right = mask.crop((corner_w, 0, mask_w, corner_h))
        bottom_left = mask.crop((0, corner_h, corner_w, mask_h))
        bottom_right = mask.crop((corner_w, corner_h, mask_w, mask_h))

        image_w, image_h = image.size
        final_mask = Image.new("L", (image_w, image_h), 255)
        final_mask.paste(top_left, (0, 0))
        final_mask.paste(top_right, (image_w - corner_w, 0))
        final_mask.paste(bottom_left, (0, image_h - corner_h))
        final_mask.paste(bottom_right, (image_w - corner_w, image_h - corner_h))

        rounded = Image.new("RGBA", (image_w, image_h))
        rounded.paste(image, (0, 0), final_mask)
        return rounded