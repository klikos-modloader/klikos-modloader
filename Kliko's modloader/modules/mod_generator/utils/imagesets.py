from pathlib import Path
from typing import Literal
from dataclasses import dataclass
import os
import re


IMAGESETDATA_NAME: str = "GetImageSetData.lua"
IMAGESET_NAME: str = "img_set_1x_1.png"


def locate_imagesets(base_dir: Path) -> Path:
    for (root, dirs, files) in os.walk(base_dir):
        if IMAGESET_NAME in files:
            return Path(root).resolve()

    raise FileNotFoundError("Could not find ImageSets")


def locate_imagesetdata(base_dir: Path) -> Path:
    for (root, dirs, files) in os.walk(base_dir):
        if IMAGESETDATA_NAME in files:
            return Path(root, IMAGESETDATA_NAME).resolve()

    raise FileNotFoundError(IMAGESETDATA_NAME)


@dataclass
class ImageSetIcon:
    name: str
    x: int
    y: int
    w: int
    h: int
    imageset: str


@dataclass
class ImageSet:
    name: str
    path: Path
    icons: list[ImageSetIcon]


class ImageSetData:
    imagesets: list[ImageSet]


    def __init__(self, filepath: Path, directory: Path, icon_sizes: Literal[0, 1, 2, 3] = 0):
        with open(filepath) as file:
            content: str = file.read()

        parsed: dict[str, dict[str, dict[str, str | int]]] = self._parse_file_content(content)

        imageset_dict: dict[str, ImageSet] = {}
        for size, icons in parsed.items():
            if icon_sizes != 0 and size != f"{icon_sizes}x":
                continue

            for name, data in icons.items():
                image_set: str = data["image_set"]  # type: ignore
                x: int = data["x"]  # type: ignore
                y: int = data["y"]  # type: ignore
                w: int = data["w"]  # type: ignore
                h: int = data["h"]  # type: ignore
                icon: ImageSetIcon = ImageSetIcon(name, x, y, w, h, image_set)

                imageset_item: ImageSet | None = imageset_dict.get(image_set)
                if imageset_item is None:
                    imageset_item = ImageSet(image_set, directory / f"{image_set}.png", [])
                    imageset_dict[image_set] = imageset_item

                imageset_item.icons.append(icon)

        self.imagesets = list(imageset_dict.values())


    def _parse_file_content(self, content: str) -> dict[str, dict[str, dict[str, str | int]]]:  # AI-Generated
        icon_map: dict[str, dict[str, dict[str, str | int]]] = {}

        image_size_pattern: str = r"function make_assets_(\dx)\(\).*?(\{.*?\}) end"
        icon_data_pattern: str = r"\['([^']+)'\] = \{ ImageRectOffset = Vector2\.new\((\d+), (\d+)\), ImageRectSize = Vector2\.new\((\d+), (\d+)\), ImageSet = '([^']+)' \}"

        image_size_matches: list = re.findall(image_size_pattern, content, re.DOTALL)
        for size, data in image_size_matches:
            if size not in icon_map:
                icon_map[size] = {}

            icon_data_matches: list = re.findall(icon_data_pattern, data)
            for icon in icon_data_matches:
                name, x, y, w, h, image_set = icon
                icon_map[size][name] = {
                    "image_set": image_set,
                    "x": int(x),
                    "y": int(y),
                    "w": int(w),
                    "h": int(h)
                }

        return icon_map