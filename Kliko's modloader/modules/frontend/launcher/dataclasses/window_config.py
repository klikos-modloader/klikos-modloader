from typing import Optional, Literal, Any
from pathlib import Path
import re

from modules.project_data import ProjectData
from modules.filesystem import Resources
from modules.interfaces.config import ConfigInterface


class WindowConfig:
    title: str = ProjectData.NAME
    icon: Path = Resources.FAVICON
    width: Optional[int] = None
    height: Optional[int] = None
    fg_color: str | tuple[str, str] = ("#F3F3F3", "#202020")
    appearance_mode: Literal["light", "dark", "system"] = "system"
    resizable: tuple[bool, bool] = (True, True)
    fullscreen: bool = False
    column_configure: Optional[dict[int, dict[str, str | int]]] = None
    row_configure: Optional[dict[int, dict[str, str | int]]] = None

    def __init__(self, data: dict = {}):
        # Window title
        title: Any = data.get("title")
        if isinstance(title, str):
            self.title = title.replace("{app.name}", ProjectData.NAME)

        # Window icon
        icon: Any = data.get("icon")
        if isinstance(icon, str):
            icon = Path(icon)
            if icon.suffix == ".ico" and icon.is_file():
                self.icon = icon

        # Window size
        size: Any = data.get("size")
        if isinstance(size, list) and len(size) == 2:
            width: Any = size[0]
            height: Any = size[1]
            if isinstance(width, int) and width > 0 and  isinstance(height, int) and height > 0:
                self.width = width
                self.height = height

        # Background color
        background_color: Any = data.get("background_color")
        if isinstance(background_color, str):
            if self._is_valid_color(background_color):
                self.fg_color = background_color
        elif isinstance(background_color, list) and len(background_color) == 2:
            light: Any = background_color[0]
            dark: Any = background_color[1]

            if self._is_valid_color(light) and self._is_valid_color(dark):
                self.fg_color = (light, dark)

        # Appearance mode
        appearance_mode: Any = data.get("appearance_mode")
        user_apperance_mode: Literal["light", "dark", "system"] = ConfigInterface.get_appearance_mode()
        if isinstance(appearance_mode, str) and appearance_mode.lower() in {"light", "dark", "system"}:
            self.appearance_mode = appearance_mode.lower()  # type: ignore
        else: self.appearance_mode = user_apperance_mode

        # Resizable
        resizable: Any = data.get("resizable")
        if isinstance(resizable, bool): self.resizable = (resizable, resizable)
        elif isinstance(resizable, list) and len(resizable) == 2:
            resizable_width: Any = resizable[0]
            resizable_height: Any = resizable[1]
            if isinstance(resizable_width, bool) and isinstance(resizable_height, bool): self.resizable = (resizable_width, resizable_height)

        # Fullscreen
        fullscreen: Any = data.get("fullscreen")
        if isinstance(fullscreen, bool): self.fullscreen = fullscreen

        # Column configure
        column_configure: Any = data.get("grid_columnconfigure")
        if isinstance(column_configure, dict) and column_configure:
            self.column_configure = self._parse_gridconfigure_config(column_configure)

        # Row configure
        row_configure: Any = data.get("grid_rowconfigure")
        if isinstance(row_configure, dict) and row_configure:
            self.row_configure = self._parse_gridconfigure_config(row_configure)


    def _parse_gridconfigure_config(self, data: dict) -> dict | None:
        parsed: dict = {}
        for index, config in data.items():
            try: index = int(index)
            except ValueError: continue

            if not isinstance(config, dict) or len(config) == 0:
                continue

            int_keys = {"minsize", "pad", "weight"}
            string_keys = {"uniform"}
            valid_keys = int_keys | string_keys
            kwargs: dict = {}

            for key in valid_keys:
                value: Any = config.get(key)
                if not value: continue

                if key in string_keys:
                    if isinstance(value, str) and value.strip():
                        kwargs[key] = value.strip()

                elif key in int_keys:
                    if isinstance(value, int) and value > 0:
                        kwargs[key] = value

            if kwargs:
                parsed[index] = kwargs

        return parsed or None


    def _is_valid_color(self, color: str) -> bool:
        if isinstance(color, str) and re.fullmatch(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})", color): return True
        return False