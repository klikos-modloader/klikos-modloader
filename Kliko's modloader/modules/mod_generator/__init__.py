from typing import Literal, Optional
from pathlib import Path
from tempfile import TemporaryDirectory
import json

from modules.logger import Logger
from modules.deployments import RobloxVersion, LatestVersion, DeployHistory
from modules.networking import requests, Response, Api

from .utils import MaskStorage
from .dataclasses import IconBlacklist, RemoteConfig, AdditionalFile, GradientColor
from .exceptions import *

from PIL import Image  # type: ignore


PREVIEW_DATA_DIR: Path = Path(__file__).parent / "preview_data"


class ModGenerator:
    _LOG_PREFIX: str = "ModGenerator"


    @classmethod
    def get_mask(cls, mode: Literal["color", "gradient", "custom"], data: tuple[int, int, int] | list[GradientColor] | Image.Image, size: tuple[int, int], angle: Optional[float] = None, dont_cache: bool = False)  -> Image.Image:
        """Assumes data has been validated"""

        match mode:
            case "color": return MaskStorage.get_solid_color(data, size, dont_cache=dont_cache)  # type: ignore
            case "gradient": return MaskStorage.get_gradient(data, angle or 0, size, dont_cache=dont_cache)  # type: ignore
            case "custom": return MaskStorage.get_custom(data, size, dont_cache=dont_cache)  # type: ignore


    @classmethod
    def generate_preview_mask(cls, mode: Literal["color", "gradient", "custom"], data: tuple[int, int, int] | list[GradientColor] | Image.Image, size: tuple[int, int], angle: Optional[float] = None)  -> Image.Image:
        cls._validate_data(mode, data)
        return cls.get_mask(mode, data, size, angle, dont_cache=True)


    @classmethod
    def generate_preview_image(cls, mode: Literal["color", "gradient", "custom"], data: tuple[int, int, int] | list[GradientColor] | Image.Image, angle: Optional[float] = None, custom_roblox_icon: Optional[Image.Image] = None)  -> Image.Image:
        cls._validate_data(mode, data)

        index: Path = PREVIEW_DATA_DIR / "index.json"
        with open(index) as file:
            icon_data: list[str] = json.load(file)

        image: Image.Image = Image.open(PREVIEW_DATA_DIR / "image.png", formats=["PNG"])
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        for item in icon_data:
            icon_name, icon_position, icon_size = item.split()
            icon_position = icon_position.split("x")  # type: ignore
            icon_size = icon_size.split("x")  # type: ignore
            icon_x: int = int(icon_position[0])
            icon_y: int = int(icon_position[1])
            icon_w: int = int(icon_size[0])
            icon_h: int = int(icon_size[1])

            if custom_roblox_icon is not None and icon_name == "roblox":
                custom_icon_resized: Image.Image = custom_roblox_icon.resize((icon_w, icon_h), resample=Image.Resampling.LANCZOS)
                image.paste(custom_icon_resized, (icon_x, icon_y))
            else:
                icon: Image.Image = image.crop((icon_x, icon_y, icon_x + icon_w, icon_y + icon_h))
                cls.apply_mask(icon, mode, data, angle)
                image.paste(icon, (icon_x, icon_y))
        MaskStorage.cache.clear()

        return image


    @classmethod
    def _validate_data(cls, mode: Literal["color", "gradient", "custom"], data: tuple[int, int, int] | list[GradientColor] | Image.Image) -> None:
        match mode:
            case "color":
                if (
                    not isinstance(data, (tuple, list))
                    or len(data) != 3
                    or not all(
                        isinstance(item, int)
                        and item >= 0
                        and item <= 255
                        for item in data
                    )
                ): raise ValueError("data must be a list or tuple of 3 int values between 0 and 255")

            case "gradient":
                if (
                    not isinstance(data, (tuple, list))
                    or len(data) < 2
                    or not all(  # type: ignore
                        isinstance(gradient_color, GradientColor)
                        and isinstance(gradient_color.stop, (int, float))
                        and gradient_color.stop >= 0 and gradient_color.stop <= 1
                        and isinstance(gradient_color.color, (tuple, list))
                        and len(gradient_color.color) == 3
                        and all(
                            isinstance(rgb_value, int)
                            and rgb_value >= 0
                            and rgb_value <= 255
                            for rgb_value in gradient_color.color
                        )
                        for gradient_color in data
                    )
                ): raise ValueError("data must be a GradientColor with a float stop value between 0 and tuple tuple color value of 3 int values between 0 and 255")

            case "custom":
                if not isinstance(data, Image.Image):
                    raise ValueError("data must be an Image.Image object")

            case invalid:
                raise ValueError(f"Invalid mode: '{invalid}', must be one of 'color', 'gradient', 'custom'")


    @classmethod
    def generate_mod(cls, mode: Literal["color", "gradient", "custom"], data: tuple[int, int, int] | list[GradientColor] | Image.Image, output_dir: str | Path, angle: Optional[float] = None, file_version: Optional[int] = None, use_remote_config: bool = True, create_1x_only: bool = False) -> None:
        Logger.info(f"Generating mod (mode={mode})...", prefix=cls._LOG_PREFIX)
        cls._validate_data(mode, data)
        angle = angle or 0

        if file_version is None:
            target_version: RobloxVersion = LatestVersion("WindowsStudio64")
        else:
            deploy_history: DeployHistory = DeployHistory()
            for deployment in reversed(deploy_history.studio_deployments):
                if deployment.file_version.minor == file_version:
                    target_version = deployment
                    break
            else: raise InvalidVersionError(file_version)

        if use_remote_config:
            response: Response = requests.get(Api.GitHub.MOD_GENERATOR_CONFIG)
            remote_config: RemoteConfig = RemoteConfig(response.json())
        else:
            remote_config = RemoteConfig({})

        output_dir = Path(output_dir).resolve()
        if output_dir.exists():
            raise FileExistsError(str(output_dir))

        with TemporaryDirectory() as tmp:
            temporary_directory: Path = Path(tmp)



            if output_dir.exists():
                raise FileExistsError(str(output_dir))


    @classmethod
    def apply_mask(cls, image: Image.Image, mode: Literal["color", "gradient", "custom"], data: tuple[int, int, int] | list[GradientColor] | Image.Image, angle: Optional[float] = None):
        """Modifies the image in place. Assumes data has been validated"""

        size = image.size
        w, h = size
        mask: Image.Image = cls.get_mask(mode, data, (w, h), angle)
        if mode == "custom":
            mask = Image.alpha_composite(image, mask)
            mask.putalpha(image.getchannel("A"))
            image.paste(mask)
        else:
            mask.putalpha(image.getchannel("A"))
            image.paste(mask)
