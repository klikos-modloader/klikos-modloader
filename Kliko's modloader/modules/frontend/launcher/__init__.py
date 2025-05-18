from typing import Literal

from .custom_launcher import CustomLauncher
from .preview_launcher import PreviewLauncher
from .exceptions import *


def run(mode: Literal["Player", "Studio"], deeplink: str) -> None:
    launcher: CustomLauncher = CustomLauncher(mode)
    launcher.run(deeplink)

    if launcher.should_run_rpc:
        pass
        # TODO