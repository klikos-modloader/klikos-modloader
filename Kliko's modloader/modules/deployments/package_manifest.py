from dataclasses import dataclass

from modules.networking import requests, Response, Api


@dataclass
class Package:
    source: str
    file: str
    md5: str
    size: int
    rawsize: int



class PackageManifest:
    version_guid: str
    manifest_version: str
    packages: list[Package]

    def __init__(self, version_guid: str):
        self.version_guid = version_guid

        response: Response = requests.get(Api.Roblox.Deployment.manifest(self.version_guid))
        text: str = response.text
        lines: list[str] = text.splitlines()
        self.manifest_version = lines[0]
        del lines[0]

        self.packages = [
            Package(source=Api.Roblox.Deployment.download(self.version_guid, lines[i]), file=lines[i], md5=lines[i+1].upper(), size=int(lines[i+2]), rawsize=int(lines[i+3]))
            for i in range(0, len(lines), 4)
        ]