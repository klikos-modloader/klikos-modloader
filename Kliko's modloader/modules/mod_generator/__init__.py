from typing import Literal, Optional
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event
import shutil
import json
import re

from modules.logger import Logger
from modules import filesystem
from modules.deployments import RobloxVersion, LatestVersion, DeployHistory
from modules.networking import requests, Response, Api

from .utils import MaskStorage, locate_imagesets, locate_imagesetdata, ImageSetData, ImageSet, ImageSetIcon
from .dataclasses import IconBlacklist, RemoteConfig, AdditionalFile, GradientColor
from .exceptions import *

from PIL import Image, PngImagePlugin  # type: ignore


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


    @classmethod
    def generate_mod(cls, mode: Literal["color", "gradient", "custom"], data: tuple[int, int, int] | list[GradientColor] | Image.Image, output_dir: str | Path, angle: Optional[float] = None, file_version: Optional[int] = None, use_remote_config: bool = True, icon_sizes: Literal[0, 1, 2, 3] = 0, custom_roblox_icon: Optional[Image.Image] = None, additional_files: Optional[list[AdditionalFile]] = None, stop_event: Optional[Event] = None) -> bool:
        """Returns True if the mod was generated, False if it was cancelled (stop_event.is_set())"""

        Logger.info(f"Generating mod (mode={mode})...", prefix=cls._LOG_PREFIX)
        cls._validate_data(mode, data)
        angle = angle or 0

        if file_version is None:
            deployment: RobloxVersion = LatestVersion("WindowsStudio64")
        else:
            deploy_history: DeployHistory = DeployHistory()
            for item in reversed(deploy_history.studio_deployments):
                if item.file_version.minor == file_version:
                    deployment = item
                    break
            else: raise InvalidVersionError(file_version)
        mod_info: dict[str, str | int] = {
            "clientVersionUpload": deployment.guid,
            "fileVersion": deployment.file_version.minor,
            "watermark": "Generated with Kliko's modloader"
        }
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("Watermark", "Generated with Kliko's modloader")

        if stop_event is not None and stop_event.is_set():
            Logger.info("Mod generator cancelled!", prefix=cls._LOG_PREFIX)
            return False

        if use_remote_config:
            response: Response = requests.get(Api.GitHub.MOD_GENERATOR_CONFIG)
            remote_config: RemoteConfig = RemoteConfig(response.json())
        else:
            remote_config = RemoteConfig({})

        if stop_event is not None and stop_event.is_set():
            Logger.info("Mod generator cancelled!", prefix=cls._LOG_PREFIX)
            return False

        output_dir = Path(output_dir).resolve()
        if output_dir.exists():
            raise FileExistsError(str(output_dir))

        Logger.info("Creating temporary directory...", prefix=cls._LOG_PREFIX)
        with TemporaryDirectory() as tmp:
            temporary_directory: Path = Path(tmp)
            temp_target: Path = temporary_directory / "mod"
            temp_target.mkdir(parents=True, exist_ok=True)
            luapackages_target: Path = temporary_directory / "luapackages"

            Logger.info("Writing info.json...", prefix=cls._LOG_PREFIX)
            with open(temp_target / "info.json", "w") as file:
                json.dump(mod_info, file, indent=4)

            if stop_event is not None and stop_event.is_set():
                Logger.info("Mod generator cancelled!", prefix=cls._LOG_PREFIX)
                return False
            
            Logger.info("Downloading ImageSets...", prefix=cls._LOG_PREFIX)
            filesystem.download(Api.Roblox.Deployment.download(deployment.guid, "extracontent-luapackages.zip"), temporary_directory / "luapackages.zip")
            filesystem.extract(temporary_directory / "luapackages.zip", luapackages_target)

            if stop_event is not None and stop_event.is_set():
                Logger.info("Mod generator cancelled!", prefix=cls._LOG_PREFIX)
                return False

            Logger.info("Locating ImageSets...", prefix=cls._LOG_PREFIX)
            imagesetdata_path: Path = locate_imagesetdata(luapackages_target)
            imagesets_dir: Path = locate_imagesets(luapackages_target)
            temp_target_imageset_path: Path = temp_target / "ExtraContent" / "Luapackages" / imagesets_dir.relative_to(luapackages_target)
            shutil.copytree(imagesets_dir, temp_target_imageset_path, dirs_exist_ok=True)

            if stop_event is not None and stop_event.is_set():
                Logger.info("Mod generator cancelled!", prefix=cls._LOG_PREFIX)
                return False

            Logger.info("Preparing ImageSets...", prefix=cls._LOG_PREFIX)
            if icon_sizes != 0:
                for path in temp_target_imageset_path.iterdir():
                    if path.suffix != ".png":
                        continue
                    if not path.name.startswith(f"img_set_{icon_sizes}x"):
                        path.unlink()

            if stop_event is not None and stop_event.is_set():
                Logger.info("Mod generator cancelled!", prefix=cls._LOG_PREFIX)
                return False

            Logger.info(f"Parsing {imagesetdata_path.name}...", prefix=cls._LOG_PREFIX)
            image_set_data: ImageSetData = ImageSetData(imagesetdata_path, temp_target_imageset_path, icon_sizes=icon_sizes)

            if stop_event is not None and stop_event.is_set():
                Logger.info("Mod generator cancelled!", prefix=cls._LOG_PREFIX)
                return False

            Logger.info("Generating ImageSets...", prefix=cls._LOG_PREFIX)
            ROBLOX_LOGO_NAME: str = "icons/logo/block"
            for imageset in image_set_data.imagesets:
                with Image.open(imageset.path, formats=("PNG",)) as imageset_image_object:
                    if imageset_image_object.mode != "RGBA":
                        imageset_image_object = imageset_image_object.convert("RGBA")

                    for icon in imageset.icons:
                        if cls._is_icon_blacklisted(icon.name, remote_config.blacklist):
                            continue

                        if custom_roblox_icon is not None and icon.name == ROBLOX_LOGO_NAME:
                            imageset_image_object.paste(custom_roblox_icon.resize((icon.w, icon.h), resample=Image.Resampling.LANCZOS), (icon.x, icon.y))
                        else:
                            cropped: Image.Image = imageset_image_object.crop((icon.x, icon.y, icon.x + icon.w, icon.y + icon.h))
                            cls.apply_mask(cropped, mode=mode, data=data, angle=angle)
                            imageset_image_object.paste(cropped, (icon.x, icon.y))
                    imageset_image_object.save(imageset.path, format="PNG", pnginfo=metadata)

                if stop_event is not None and stop_event.is_set():
                    Logger.info("Mod generator cancelled!", prefix=cls._LOG_PREFIX)
                    return False

            if additional_files:
                Logger.info("Generating additional files...", prefix=cls._LOG_PREFIX)
                additional_file_counter: int = 0
                for additional_file in additional_files:
                    additional_file_counter += 1

                    if additional_file_counter % 20 == 0:
                        if stop_event is not None and stop_event.is_set():
                            Logger.info("Mod generator cancelled!", prefix=cls._LOG_PREFIX)
                            return False


                    target: Path = Path(temp_target, *re.split(r"[\\/]", additional_file.target))

                    if target.suffix != ".png":
                        Logger.warning(f"Skipping file '{target.name}'... (Invalid filetype, must be '.png')")
                        continue

                    match = re.search(r'@(\d+)x$', target.stem)
                    if match:
                        icon_size = int(match.group(1))
                        if icon_size != icon_sizes:
                            Logger.warning(f"Skipping file '{target.name}'... (Only generating @{icon_sizes}x sizes)")
                            continue

                    image_copy: Image.Image = additional_file.image.copy()
                    if image_copy.mode != "RGBA":
                        image_copy = image_copy.convert("RGBA")
                    cls.apply_mask(image_copy, mode, data, angle)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    image_copy.save(target, format="PNG", pnginfo=metadata)

            if stop_event is not None and stop_event.is_set():
                Logger.info("Mod generator cancelled!", prefix=cls._LOG_PREFIX)
                return False

            if output_dir.exists():
                raise FileExistsError(str(output_dir))
            shutil.copytree(temp_target, output_dir, dirs_exist_ok=True)
            Logger.info("Mod generated successfully!", prefix=cls._LOG_PREFIX)
            return True


    @classmethod
    def _is_icon_blacklisted(cls, name: str, blacklist: IconBlacklist) -> bool:
        for prefix in blacklist.prefixes:
            if name.startswith(prefix):
                return True
        for suffix in blacklist.suffixes:
            if name.endswith(suffix):
                return True
        for keyword in blacklist.keywords:
            if keyword in name:
                return True
        for strict in blacklist.strict:
            if name == strict:
                return True
        return False