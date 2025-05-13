from typing import Optional, Literal, Callable, Any
from pathlib import Path

from modules.project_data import ProjectData
from modules.localization import Localizer

from .parser import Parser



VALID_WIDGET_TYPES: set = {"frame", "label", "button", "progress_bar", "status_label", "channel_label", "version_label", "file_version_label"}
VALID_PLACEMENT_MODES: set = {"grid", "pack", "place"}
VALID_BUTTON_ACTIONS: set = {"cancel"}


class WidgetConfig:
    type: Literal["frame", "label", "button", "progress_bar", "status_label", "channel_label", "version_label", "file_version_label"]
    kwargs: dict
    placement_mode: Literal["grid", "pack", "place"]
    placement_mode_kwargs: dict

    column_configure: Optional[dict[int, dict[str, str | int]]] = None
    row_configure: Optional[dict[int, dict[str, str | int]]] = None
    button_action: Literal["cancel"] | None = None
    localized_string: Optional[str] = None
    localized_string_modification: Optional[Callable[[str], str]] = None

    children: list["WidgetConfig"]

    _theme_base_directory: Path
    _ERROR_PREFIX: str = "WidgetConfig"


    def __init__(self, data: dict, theme_base_directory: Path):
        self.kwargs = {}
        self.placement_mode_kwargs = {}
        self.children = []
        self._theme_base_directory = theme_base_directory

        # Type
        widget_type: Any = data.get("type")
        if not isinstance(widget_type, str) or widget_type.lower() not in VALID_WIDGET_TYPES:
            raise ValueError(f'[{self._ERROR_PREFIX}] Invalid widget type: "{widget_type}"')
        self.type = widget_type.lower()  # type: ignore

        # Placement mode
        placement_mode: Any = data.get("placement_mode")
        if not isinstance(placement_mode, str) or placement_mode.lower() not in VALID_PLACEMENT_MODES:
            raise ValueError(f'[{self._ERROR_PREFIX}] Invalid placement mode: "{placement_mode}"')
        self.placement_mode = placement_mode.lower()  # type: ignore
        
        # Button action
        if self.type == "button":
            action: Any = data.get("action")
            if isinstance(action, str):
                action_lower = action.lower()
                if action_lower not in VALID_BUTTON_ACTIONS:
                    raise ValueError(f'[{self._ERROR_PREFIX}] Invalid button action: "{action}"')
                self.button_action = action_lower  # type: ignore

        # Placement kwargs
        placement_kwargs: Any = data.get("placement_kwargs")
        if isinstance(placement_kwargs, dict) and placement_kwargs:
            self.placement_mode_kwargs = Parser.parse_placement_kwargs(self.placement_mode, placement_kwargs)

        # Grid configure
        if self.type == "frame":
            # Column configure
            column_configure: Any = data.get("grid_columnconfigure")
            if isinstance(column_configure, dict) and column_configure:
                self.column_configure = Parser.parse_gridconfigure_config(column_configure)

            # Row configure
            row_configure: Any = data.get("grid_rowconfigure")
            if isinstance(row_configure, dict) and row_configure:
                self.row_configure = Parser.parse_gridconfigure_config(row_configure)
        
        # Localized widgets
        if self.type in {"button", "label"}:
            localized_string: Any = data.get("localized_string")
            if isinstance(localized_string, str):
                self.localized_string = localized_string

                localized_string_modifications: Any = data.get("localized_string_modifications")
                modifications: dict[str, str | Localizer.Key] = {"{app.name}": ProjectData.NAME, "{app.version}": ProjectData.VERSION}
                if isinstance(localized_string_modifications, dict) and localized_string_modifications:
                    for key, value in localized_string_modifications.items():
                        if not isinstance(key, str) or not isinstance(value, str):
                            continue
                        if not value.startswith("key;"):
                            modifications[key] = value
                        else:
                            value = value.removeprefix("key;")
                            modifications[key] = Localizer.Key(value)
                    
                self.localized_string_modification = lambda string: Localizer.format(string, modifications)
        
        # Kwargs
        kwargs: Any = data.get("kwargs")
        if isinstance(kwargs, dict) and kwargs:
            self.kwargs = Parser.parse_widget_kwargs(self.type, kwargs, self._theme_base_directory)
        if self.type in {"status_label", "client_channel_label", "client_version_label", "file_version_label"}:
            self.kwargs.pop("text", None)

        # Children
        widgets: Any = data.get("widgets")
        if isinstance(widgets, list) and widgets:
            for item in widgets:
                if not isinstance(item, dict): continue
                widget: "WidgetConfig" = WidgetConfig(item, theme_base_directory)
                self.children.append(widget)