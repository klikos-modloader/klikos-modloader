from typing import Literal

from modules.activity_watcher import ActivityWatcher

from .custom_launcher import CustomLauncher
from .preview_launcher import PreviewLauncher
from .exceptions import *


def run(mode: Literal["Player", "Studio"], deeplink: str) -> None:
    launcher: CustomLauncher = CustomLauncher(mode)
    launcher.run(deeplink)

    if launcher.should_run_rpc:
        ActivityWatcher.run(mode)