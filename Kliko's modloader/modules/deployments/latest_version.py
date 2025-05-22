from typing import Literal

from modules.networking import requests, Response, Api

from .roblox_version import RobloxVersion

from packaging.version import Version  # type: ignore


class LatestVersion(RobloxVersion):
    channel: str

    def __init__(self, binary_type: Literal["WindowsPlayer", "WindowsStudio64"]) -> None:
        self.binary_type = binary_type

        self.channel = self.get_user_channel()
        guid, file_version = self.get_version_info()
        self.guid = guid
        self.file_version = Version(file_version)


    def get_user_channel(self) -> str:
        response: Response = requests.get(Api.Roblox.Deployment.channel(self.binary_type))
        data: dict = response.json()
        return data["channelName"]


    def get_version_info(self) -> tuple[str, str]:
        response: Response = requests.get(Api.Roblox.Deployment.latest(self.binary_type, self.channel))
        data: dict = response.json()
        version: str = data["version"]
        client_version_upload: str = data["clientVersionUpload"]
        return (client_version_upload, version)