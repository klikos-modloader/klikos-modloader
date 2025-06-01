import math

from ..dataclasses import GradientColor

from PIL import Image  # type: ignore
import numpy as np  # type: ignore


class MaskStorage:
    cache: dict[str, Image.Image] = {}

    @classmethod
    def get_solid_color(cls, color: tuple[int, int, int], size: tuple[int, int], dont_cache: bool = False) -> Image.Image:
        cache_key: str = f"{color}-{size}"
        cached_mask: Image.Image | None = cls.cache.get(cache_key)
        if cached_mask is not None:
            return cached_mask
        
        mask: Image.Image = Image.new("RGBA", size, color)
        if not dont_cache:
            cls.cache[cache_key] = mask
        return mask


    @classmethod  # AI-generated
    def get_gradient(cls, colors: list[GradientColor], angle_degrees: float, size: tuple[int, int], dont_cache: bool = False) -> Image.Image:
        cache_key: str = f"{colors}-{angle_degrees}-{size}"
        cached_mask: Image.Image | None = cls.cache.get(cache_key)
        if cached_mask is not None:
            return cached_mask

        width, height = size
        angle: float = math.radians(angle_degrees)

        dx: float = math.cos(angle)
        dy: float = math.sin(angle)

        x = np.linspace(0, 1, width)
        y = np.linspace(0, 1, height)
        xv, yv = np.meshgrid(x, y)
        pos = (xv * dx + yv * dy)
        pos = (pos - pos.min()) / (pos.max() - pos.min())

        img = np.zeros((height, width, 3), dtype=np.uint8)
        sorted_colors: list[GradientColor] = sorted(colors, key=lambda item: item.stop)

        for i in range(len(sorted_colors) - 1):
            color_item0 = sorted_colors[i]
            p0 = color_item0.stop
            c0 = color_item0.color

            color_item1 = sorted_colors[i+1]
            p1 = color_item1.stop
            c1 = color_item1.color

            if p0 == p1:
                continue

            mask = (pos >= p0) & (pos <= p1)
            t = (pos[mask] - p0) / (p1 - p0)

            for ch in range(3):
                img[..., ch][mask] = (np.array(c0[ch]) * (1 - t) + np.array(c1[ch]) * t).astype(np.uint8)

        result: Image.Image = Image.fromarray(img)
        if not dont_cache:
            cls.cache[cache_key] = result
        return result


    @classmethod
    def get_custom(cls, image: Image.Image, size: tuple[int, int], dont_cache: bool = False) -> Image.Image:
        cache_key: str = f"{image}-{size}"
        cached_mask: Image.Image | None = cls.cache.get(cache_key)
        if cached_mask is not None:
            return cached_mask

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        image_width, image_height = image.size
        target_width, target_height = size

        image_ratio: float = image_width / image_height
        target_ratio: float = target_width / target_height

        if image_ratio != target_ratio:
            cropped: Image.Image = cls._crop_to_fit(image, target_ratio)
        else:
            cropped = image

        resized: Image.Image = cropped.resize(size, resample=Image.Resampling.LANCZOS)

        if not dont_cache:
            cls.cache[cache_key] = resized
        return resized


    @classmethod
    def _crop_to_fit(cls, image: Image.Image, target_ratio: float) -> Image.Image:
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