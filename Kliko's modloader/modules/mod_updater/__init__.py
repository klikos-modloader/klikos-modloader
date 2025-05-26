from typing import Literal, Optional
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import json
import re

from modules.logger import Logger
from modules import filesystem
from modules.deployments import RobloxVersion, LatestVersion, DeployHistory
from modules.networking import requests, Response, Api

from .imagesets import locate_imagesets, locate_imagesetdata, ImageSetData, ImageSet, ImageSetIcon
from .exceptions import *

from PIL import Image, PngImagePlugin  # type: ignore


class ModUpdater:
    _LOG_PREFIX: str = "ModUpdater"


    @classmethod
    def update_mod(cls, mod: Path, latest_version: RobloxVersion) -> None:
        Logger.info(f"Updating mod: '{mod.name}'...", prefix=cls._LOG_PREFIX)

        if not (mod / "info.json").exists():
            raise FileNotFoundError(str(mod / "info.json"))
        with open(mod / "info.json", "r") as file:
            mod_info: dict[str, str | int] = json.load(file)

        deploy_history: DeployHistory = DeployHistory()
        mod_file_version: int | None = mod_info.get("fileVersion")  # type: ignore
        if not isinstance(mod_file_version, int):
            mod_guid: str | None = mod_info.get("clientVersionUpload")  # type: ignore
            if not isinstance(mod_guid, str):
                raise ValueError("Unknown mod verison!")
            else:
                for item in reversed(deploy_history.studio_deployments):
                    if item.guid == mod_guid:
                        mod_version: RobloxVersion = item
                        break
                else: raise ValueError(f"Invalid clientVersionUpload: {mod_guid}")
        else:
            for item in reversed(deploy_history.studio_deployments):
                if item.file_version.minor == mod_file_version:
                    mod_version = item
                    break
            else: raise InvalidVersionError(mod_file_version)

        latest_file_version: int = latest_version.file_version.minor
        if latest_version.binary_type == "WindowsStudio64":
            target_version: RobloxVersion = latest_version
        else:
            for item in reversed(deploy_history.studio_deployments):
                if item.file_version.minor == latest_file_version:
                    target_version = item
                    break
            else: raise InvalidVersionError(latest_file_version)

        if mod_version.file_version == target_version.file_version:
            Logger.info("Mod is not outdated. Cancelling update...", prefix=cls._LOG_PREFIX)
            return

        mod_info.update({
            "clientVersionUpload": target_version.guid,
            "fileVersion": target_version.file_version.minor
        })

        Logger.info("Creating temporary directory...", prefix=cls._LOG_PREFIX)
        with TemporaryDirectory() as tmp:
            temporary_directory: Path = Path(tmp)
            temp_target: Path = temporary_directory / "mod"
            temp_target.mkdir(parents=True, exist_ok=True)
            old_luapackages_path: Path = temporary_directory / "luapackages_old"
            new_luapackages_path: Path = temporary_directory / "luapackages_old"

            Logger.info("Copying mod...", prefix=cls._LOG_PREFIX)
            shutil.copytree(mod, temp_target, dirs_exist_ok=True)

            Logger.info("Writing info.json...", prefix=cls._LOG_PREFIX)
            with open(temp_target / "info.json", "w") as file:
                json.dump(mod_info, file, indent=4)
            
            Logger.info("Downloading ImageSets...", prefix=cls._LOG_PREFIX)
            filesystem.download(Api.Roblox.Deployment.download(mod_version.guid, "extracontent-luapackages.zip"), temporary_directory / "luapackages.zip")
            filesystem.extract(temporary_directory / "luapackages.zip", old_luapackages_path)

            filesystem.download(Api.Roblox.Deployment.download(target_version.guid, "extracontent-luapackages.zip"), temporary_directory / "luapackages.zip")
            filesystem.extract(temporary_directory / "luapackages.zip", new_luapackages_path)

            Logger.info("Locating ImageSets...", prefix=cls._LOG_PREFIX)
            old_imagesetdata_path: Path = locate_imagesetdata(old_luapackages_path)
            old_imagesets_dir: Path = locate_imagesets(old_luapackages_path)
            old_temp_target_imageset_path: Path = temp_target / "ExtraContent" / "Luapackages" / old_imagesets_dir.relative_to(old_luapackages_path)
            shutil.copytree(old_imagesets_dir, old_temp_target_imageset_path, dirs_exist_ok=True)

            new_imagesetdata_path: Path = locate_imagesetdata(new_luapackages_path)
            new_imagesets_dir: Path = locate_imagesets(new_luapackages_path)
            new_temp_target_imageset_path: Path = temp_target / "ExtraContent" / "Luapackages" / new_imagesets_dir.relative_to(new_luapackages_path)
            shutil.copytree(new_imagesets_dir, new_temp_target_imageset_path, dirs_exist_ok=True)

            Logger.info(f"Parsing {new_imagesetdata_path.name}...", prefix=cls._LOG_PREFIX)
            old_image_set_data: ImageSetData = ImageSetData(old_imagesetdata_path, old_temp_target_imageset_path)
            new_image_set_data: ImageSetData = ImageSetData(new_imagesetdata_path, new_temp_target_imageset_path)

            old_icon_dict: dict[str, ImageSetIcon] = {
                icon.name: icon for imageset in old_image_set_data.imagesets for icon in imageset.icons
            }
            new_icon_dict: dict[str, ImageSetIcon] = {
                icon.name: icon for imageset in new_image_set_data.imagesets for icon in imageset.icons
            }

            Logger.info("Detecting modded icons...", prefix=cls._LOG_PREFIX)
            modded_icons: dict[str, Image.Image] = {}
            for imageset in old_image_set_data.imagesets:
                mod_same_imageset_path: Path = old_temp_target_imageset_path / imageset.path.name
                if not mod_same_imageset_path.exists():
                    continue

                with Image.open(imageset.path, formats=("PNG",)) as old_imageset:
                    if old_imageset.mode != "RGBA":
                        old_imageset = old_imageset.convert("RGBA")
                    with Image.open(mod_same_imageset_path, formats=("PNG",)) as mod_imageset:
                        if mod_imageset.mode != "RGBA":
                            mod_imageset = mod_imageset.convert("RGBA")
                        
                        for icon in imageset.icons:
                            old_cropped: Image.Image = old_imageset.crop((icon.x, icon.y, icon.x + icon.w, icon.y + icon.h))
                            mod_cropped: Image.Image = mod_imageset.crop((icon.x, icon.y, icon.x + icon.w, icon.y + icon.h))

                            if not cls._is_same_image(old_cropped, mod_cropped):
                                modded_icons[f"{imageset.name}/{icon.name}"] = mod_cropped

            print(len(modded_icons))


            # TODO
            # detect icon movement
            # detect modded icons
            # generate new imagesets
            # remove unmodded imagesets


    @staticmethod
    def _is_same_image(image1: Image.Image, image2: Image.Image) -> bool:
        return True