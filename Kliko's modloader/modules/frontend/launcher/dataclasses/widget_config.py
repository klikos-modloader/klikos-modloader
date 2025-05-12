from typing import Optional, Literal, Any
from pathlib import Path
import re

from modules.filesystem import Directories
from modules.localization import Localizer

VALID_WIDGET_TYPES: set = {"frame", "label", "button"}
VALID_PLACEMENT_MODES: set = {"grid", "pack", "place"}
VALID_BUTTON_ACTIONS: set = {"cancel"}


class WidgetConfig:
    type: Literal["frame", "label", "button"]
    kwargs: dict
    placement_mode: Literal["grid", "pack", "place"]
    placement_mode_kwargs: dict

    column_configure: Optional[dict[int, dict[str, str | int]]] = None
    row_configure: Optional[dict[int, dict[str, str | int]]] = None
    button_action: Literal["cancel"] | None = None

    _theme_base_directory: Path
    _ERROR_PREFIX: str = "WidgetConfig"


    def __init__(self, data: dict, theme_base_directory: Path):
        self.kwargs = {}
        self.placement_mode_kwargs = {}
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
            if not isinstance(action, str) or action.lower() not in VALID_BUTTON_ACTIONS:
                raise ValueError(f'[{self._ERROR_PREFIX}] Invalid button action: "{placement_mode}"')
            self.button_action = action.lower()  # type: ignore

        # Placement kwargs
        placement_kwargs: Any = data.get("placement_kwargs")
        if isinstance(placement_kwargs, dict) and placement_kwargs:
            self.placement_mode_kwargs = self._parse_placement_kwargs(self.placement_mode, placement_kwargs)

        # Grid configure
        if self.type == "frame":
            # Column configure
            column_configure: Any = data.get("grid_columnconfigure")
            if isinstance(column_configure, dict) and column_configure:
                self.column_configure = self._parse_gridconfigure_config(column_configure)

            # Row configure
            row_configure: Any = data.get("grid_rowconfigure")
            if isinstance(row_configure, dict) and row_configure:
                self.row_configure = self._parse_gridconfigure_config(row_configure)
        
        # Kwargs
        kwargs: Any = data.get("kwargs")
        if isinstance(kwargs, dict) and kwargs:
            self.kwargs = self._parse_widget_kwargs(kwargs)


    def _is_valid_color(self, color: str) -> bool:
        if isinstance(color, str) and re.fullmatch(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})", color): return True
        return False


    def _parse_color(self, data: Any) -> str | tuple[str, str] | None:
        if isinstance(data, str):
            if data.lower() == "transparent":
                return "transparent"

            elif self._is_valid_color(data):
                return data

        elif isinstance(data, list) and len(data) == 2:
            light: Any = data[0]
            dark: Any = data[1]

            if self._is_valid_color(light) and self._is_valid_color(dark):
                return (light, dark)

        return None


    def _parse_filepath(self, string: str) -> Path:
        if string.startswith("{RESOURCES}"):
            string = string.replace("{RESOURCES}", str(Directories.RESOURCES.resolve()), 1)
        elif string.startswith("{INTERNAL}"):
            string = string.replace("{INTERNAL}", str(self._theme_base_directory.resolve()), 1)
        return Path(string)


    def _parse_anchor(self, value: str) -> str | None:
        value_lower = value.lower()
        if value_lower == "center":
            return "center"

        value_list = list(value_lower)
        if len(value_list) == len(set(value_list)) and all(char in {"n", "s", "e", "w"} for char in value_list):
            return ''.join(value_list)
        return None


    def _parse_font(self, data: dict) -> dict | None:
        family: Any = data.get("family")
        size: Any = data.get("size")
        weight: Any = data.get("weight")
        slant: Any = data.get("slant")
        underline: Any = data.get("underline")
        overstrike: Any = data.get("overstrike")

        font: dict = {}

        if isinstance(family, str) and family:
            font["family"] = family
        if isinstance(size, int) and size >= 0:
            font["size"] = size
        if isinstance(weight, str) and weight.lower() in {"bold", "normal"}:
            font["weight"] = weight.lower()
        if isinstance(slant, str) and slant.lower() in {"italic", "roman"}:
            font["slant"] = slant.lower()
        if isinstance(underline, bool):
            font["underline"] = underline
        if isinstance(overstrike, bool):
            font["overstrike"] = overstrike

        return font or None


    def _parse_image(self, data: dict) -> dict | None:
        light: Any = data.get("light")
        dark: Any = data.get("dark")
        size = data.get("size")

        image: dict = {}
        has_size: bool = False
        has_path: bool = False

        if isinstance(size, int) and size >= 0:
            size = (size, size)
            image["size"] = size
            has_size = True

        elif isinstance(size, list) and len(size) == 2:
            width: Any = size[0]
            height: Any = size[1]

            if isinstance(width, int) and width >= 0 and  isinstance(height, int) and height >= 0:
                image["size"] = (width, height)
                has_size = True

        if isinstance(light, str) and light:
            light_path: Path = self._parse_filepath(light)
            if light_path.suffix == ".png" and light_path.is_file():
                image["light"] = light_path
                has_path = True

        if isinstance(dark, str) and dark:
            dark_path: Path = self._parse_filepath(dark)
            if dark_path.suffix == ".png" and dark_path.is_file():
                image["dark"] = dark_path
                has_path = True
        
        if has_size and has_path:
            return image
        return None


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


    def _parse_placement_kwargs(self, mode: Literal["grid", "place", "pack"], data: dict) -> dict:
        kwargs: dict = {}

        match mode:
            case "grid":
                int_kwargs = {"row", "column", "rowspan", "columnspan"}
                tuple_or_int_kwargs = {"padx", "pady", "ipadx", "ipady"}
                string_kwargs = {"sticky"}
                valid_kwargs = int_kwargs | tuple_or_int_kwargs | string_kwargs

                for key in valid_kwargs:
                    value: Any = data.get(key)

                    if key in int_kwargs:
                        if isinstance(value, int) and value >= 0:
                            kwargs[key] = value

                    elif key in tuple_or_int_kwargs:
                        if isinstance(value, int) and value >= 0:
                            kwargs[key] = value
                        elif isinstance(value, list) and len(value) == 2:
                            value0: Any = value[0]
                            value1: Any = value[1]
                            if isinstance(value0, int) and value0 >= 0 and isinstance(value1, int) and value1 >= 0:
                                kwargs[key] = (value0, value1)
                    
                    elif key in string_kwargs:
                        if not isinstance(value, str):
                            continue

                        if key == "sticky":
                            sticky: str | None = self._parse_anchor(value)
                            if sticky:
                                kwargs[key] = sticky

            case "place":
                string_kwargs = {"anchor", "side", "fill"}
                boolean_kwargs = {"expand"}
                tuple_or_int_kwargs = {"padx", "pady", "ipadx", "ipady"}
                valid_kwargs = string_kwargs | boolean_kwargs | tuple_or_int_kwargs

                for key in valid_kwargs:
                    value = data.get(key)

                    if key in boolean_kwargs:
                        if isinstance(value, bool):
                            kwargs[key] = value

                    elif key in tuple_or_int_kwargs:
                        if isinstance(value, int) and value >= 0:
                            kwargs[key] = value
                        elif isinstance(value, list) and len(value) == 2:
                            value0 = value[0]
                            value1 = value[1]
                            if isinstance(value0, int) and value0 >= 0 and isinstance(value1, int) and value1 >= 0:
                                kwargs[key] = (value0, value1)

                    elif key in string_kwargs:
                        if not isinstance(value, str):
                            continue

                        if key == "anchor":
                            anchor: str | None = self._parse_anchor(value)
                            if anchor:
                                kwargs[key] = anchor

                        elif key == "fill":
                            value_lower = value.lower()
                            if value_lower in {"none", "x", "y", "both"}:
                                kwargs[key] = value_lower

                        elif key == "side":
                            value_lower = value.lower()
                            if value_lower in {"top", "left", "bottom", "right"}:
                                kwargs[key] = value_lower

            case "pack":
                float_kwargs = {"relx", "rely"}
                int_kwargs = {"width", "height"}
                string_kwargs = {"anchor"}
                valid_kwargs = float_kwargs | int_kwargs | string_kwargs

                for key in valid_kwargs:
                    value = data.get(key)

                    if key in int_kwargs:
                        if isinstance(value, int) and value >= 0:
                            kwargs[key] = value

                    elif key in float_kwargs:
                        if (isinstance(value, int) or isinstance(value, float)) and value >= 0 and value <= 1:
                            kwargs[key] = value

                    elif key in string_kwargs:
                        if not isinstance(value, str):
                            continue

                        if key == "anchor":
                            anchor = self._parse_anchor(value)
                            if anchor:
                                kwargs[key] = anchor
        return kwargs


    def _parse_widget_kwargs(self, data: dict) -> dict:
        kwargs: dict = {}

        match self.type:
            case "frame":
                int_kwargs = {"width", "height", "border_width", "corner_radius"}
                color_kwargs = {"fg_color", "border_color"}
                valid_kwargs = int_kwargs | color_kwargs

                for key in valid_kwargs:
                    value: Any = data.get("key")

                    if key in int_kwargs:
                        if isinstance(value, int) and value >= 0:
                            kwargs[key] = value
                    
                    elif key in color_kwargs:
                        value = data.get("key")
                        color = self._parse_color(value)
                        if color: kwargs[key] = color

            case "label":
                int_kwargs = {"width", "height", "corner_radius", "padx", "pady", "wraplength"}
                string_kwargs = {"text", "compound", "anchor"}
                color_kwargs = {"fg_color", "text_color"}
                font_kwargs = {"font"}
                image_kwargs = {"image"}
                valid_kwargs = int_kwargs | string_kwargs | color_kwargs | font_kwargs | image_kwargs

                for key in valid_kwargs:
                    value = data.get("key")

                    if key in int_kwargs:
                        if isinstance(value, int) and value >= 0:
                            kwargs[key] = value

                    elif key in string_kwargs:
                        if not isinstance(value, str): continue

                        if key == "anchor":
                            anchor: str | None = self._parse_anchor(value)
                            if anchor:
                                kwargs[key] = anchor
                        
                        elif key == "compound":
                            value_lower = value.lower()
                            if value_lower in {"left", "right", "center"}:
                                kwargs[key] = value_lower
                        
                        elif key == "text":
                            kwargs[key] = value

                    elif key in color_kwargs:
                        color = self._parse_color(value)
                        if key == "text_color" and color == "transparent":
                            continue
                        if color:
                            kwargs[key] = color
                    
                    elif key in font_kwargs:
                        if isinstance(value, dict) and value:
                            font: dict | None = self._parse_font(value)
                            if font:
                                kwargs[key] = font

                    elif key in image_kwargs:
                        if isinstance(value, dict) and value:
                            image: dict | None = self._parse_image(value)
                            if image:
                                kwargs[key] = image

            case "button":
                int_kwargs = {"width", "height", "corner_radius", "border_width", "border_spacing"}
                boolean_kwargs = {"round_width_to_even_numbers", "round_height_to_even_numbers", "hover"}
                string_kwargs = {"text", "compound", "anchor", "state"}
                color_kwargs = {"fg_color", "hover_color", "border_color", "text_color"}
                font_kwargs = {"font"}
                image_kwargs = {"image"}
                valid_kwargs = int_kwargs | boolean_kwargs | string_kwargs | color_kwargs | font_kwargs | image_kwargs

                # TODO
        return kwargs