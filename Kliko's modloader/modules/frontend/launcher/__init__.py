from typing import Literal

from .custom_launcher import CustomLauncher
from .exceptions import *


def run(mode: Literal["Player", "Studio"]) -> None:
    CustomLauncher(mode).run()