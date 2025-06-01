from modules.networking import requests, Response, Api

from .roblox_version import RobloxVersion


class DeployHistory:
    """Deployments are ordered oldest to newest"""
    deployments: tuple[RobloxVersion, ...]


    def __init__(self) -> None:
        response: Response = requests.get(Api.Roblox.Deployment.HISTORY)
        text: str = response.text

        deployments: list[RobloxVersion] = []
        valid_binary_types: set[str] = {"WindowsPlayer", "WindowsStudio64"}
        for line in text.splitlines():
            try:
                split_line: list[str] = line.split()
                file_version: str = split_line[-2]
                if not file_version.replace(".", "").isdigit():
                    continue
                binary_type: str = split_line[1]
                if binary_type == "Studio64": binary_type = "WindowsStudio64"
                if binary_type not in valid_binary_types:
                    continue
                guid: str = split_line[2]
                deployments.append(RobloxVersion(binary_type, guid, file_version))  # type: ignore
            except Exception: pass

        self.deployments = tuple(deployments)


    @property
    def player_deployments(self) -> tuple[RobloxVersion, ...]:
        return tuple(deployment for deployment in self.deployments if deployment.binary_type == "WindowsPlayer")


    @property
    def studio_deployments(self) -> tuple[RobloxVersion, ...]:
        return tuple(deployment for deployment in self.deployments if deployment.binary_type == "WindowsStudio64")