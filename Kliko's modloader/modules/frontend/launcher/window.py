from typing import Literal

from modules.project_data import ProjectData
from modules.filesystem import Resources
from modules.frontend.widgets import Root


CURRENT_LAUNCHER_VERSION: str = "1.0.0"


class Window(Root):
    mode: Literal["Player", "Studio"]


    def __init__(self, mode: Literal["Player", "Studio"]):
        self.mode = mode
        super().__init__(ProjectData.NAME, Resources.FAVICON, centered=True, banner_system=False)