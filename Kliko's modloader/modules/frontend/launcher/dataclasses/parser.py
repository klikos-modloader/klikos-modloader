from typing import Literal, Any
from pathlib import Path
import re

from modules.filesystem import Directories

from PIL import Image  # type: ignore
import winaccent  # type: ignore


class Parser:
# region filepath
    @classmethod
    def parse_filepath(cls, string: str, base_directory: Path) -> Path:
        if string.startswith("{RESOURCES}"):
            string = string.replace("{RESOURCES}", str(base_directory.resolve()), 1)
        elif string.startswith("{INTERNAL}"):
            string = string.replace("{INTERNAL}", str(Directories.RESOURCES.resolve()), 1)
        return Path(string).resolve()
# endregion


# region color
    @classmethod
    def _is_valid_color(cls, color: str) -> bool:
        if re.fullmatch(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})", color): return True
        return False


    @classmethod
    def parse_color(cls, data: Any) -> str | tuple[str, str] | None:
        if isinstance(data, str):
            data_lower = data.lower()
            if data_lower == "transparent":
                return "transparent"

            elif cls._is_valid_color(data):
                return data

            elif data_lower == "{accent_normal}":
                return winaccent.accent_normal

            elif data_lower == "{accent_light_1}":
                return winaccent.accent_light_1

            elif data_lower == "{accent_light_2}":
                return winaccent.accent_light_2

            elif data_lower == "{accent_light_3}":
                return winaccent.accent_light_3

            elif data_lower == "{accent_dark_1}":
                return winaccent.accent_dark_1

            elif data_lower == "{accent_dark_2}":
                return winaccent.accent_dark_2

            elif data_lower == "{accent_dark_3}":
                return winaccent.accent_dark_3

        elif isinstance(data, list) and len(data) == 2:
            light: Any = data[0]
            dark: Any = data[1]

            if isinstance(light, str) and isinstance(dark, str):
                light_lower = light.lower()
                dark_lower = dark.lower()

                light_valid: bool = False
                dark_valid: bool = False

                if cls._is_valid_color(light):
                    light_valid = True

                elif light_lower == "{accent_normal}":
                    light = winaccent.accent_normal
                    light_valid = True

                elif light_lower == "{accent_light_1}":
                    light = winaccent.accent_light_1
                    light_valid = True

                elif light_lower == "{accent_light_2}":
                    light = winaccent.accent_light_2
                    light_valid = True

                elif light_lower == "{accent_light_3}":
                    light = winaccent.accent_light_3
                    light_valid = True

                elif light_lower == "{accent_dark_1}":
                    light = winaccent.accent_dark_1
                    light_valid = True

                elif light_lower == "{accent_dark_2}":
                    light = winaccent.accent_dark_2
                    light_valid = True

                elif light_lower == "{accent_dark_3}":
                    light = winaccent.accent_dark_3
                    light_valid = True
                

                if cls._is_valid_color(dark):
                    dark_valid = True

                elif dark_lower == "{accent_normal}":
                    dark = winaccent.accent_normal
                    dark_valid = True

                elif dark_lower == "{accent_light_1}":
                    dark = winaccent.accent_light_1
                    dark_valid = True

                elif dark_lower == "{accent_light_2}":
                    dark = winaccent.accent_light_2
                    dark_valid = True

                elif dark_lower == "{accent_light_3}":
                    dark = winaccent.accent_light_3
                    dark_valid = True

                elif dark_lower == "{accent_dark_1}":
                    dark = winaccent.accent_dark_1
                    dark_valid = True

                elif dark_lower == "{accent_dark_2}":
                    dark = winaccent.accent_dark_2
                    dark_valid = True

                elif dark_lower == "{accent_dark_3}":
                    dark = winaccent.accent_dark_3
                    dark_valid = True

                if light_valid and dark_valid:
                    return (light, dark)

        return None
# endregion


# region grid configure
    @classmethod
    def parse_gridconfigure_config(cls, data: dict) -> dict | None:
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
# endregion


# region placement kwargs
    @classmethod
    def parse_placement_kwargs(cls, mode: Literal["grid", "place", "pack"], data: dict) -> dict:
        kwargs: dict = {}

        match mode:
    # region - grid
            case "grid":
                int_kwargs = {"row", "column", "rowspan", "columnspan", "ipadx", "ipady"}
                tuple_or_int_kwargs = {"padx", "pady"}
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
                            sticky: str | None = cls._parse_sticky(value)
                            if sticky:
                                kwargs[key] = sticky
    # endregion

    # region - place
            case "place":
                string_kwargs = {"anchor", "side", "fill"}
                boolean_kwargs = {"expand"}
                int_kwargs = {"ipadx", "ipady"}
                tuple_or_int_kwargs = {"padx", "pady"}
                float_kwargs = {"relx", "rely", "relwidth", "relheight"}
                valid_kwargs = string_kwargs | int_kwargs | float_kwargs | boolean_kwargs | tuple_or_int_kwargs

                for key in valid_kwargs:
                    value = data.get(key)

                    if key in int_kwargs:
                        if isinstance(value, int) and value >= 0:
                            kwargs[key] = value

                    elif key in float_kwargs:
                        if (isinstance(value, int) or isinstance(value, float)) and value >= 0 and value <= 1:
                            kwargs[key] = value

                    elif key in boolean_kwargs:
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
                            anchor: str | None = cls._parse_anchor(value)
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
    # endregion

    # region - pack
            case "pack":
                int_kwargs = {"width", "height"}
                string_kwargs = {"anchor"}
                valid_kwargs = int_kwargs | string_kwargs

                for key in valid_kwargs:
                    value = data.get(key)

                    if key in int_kwargs:
                        if isinstance(value, int) and value >= 0:
                            kwargs[key] = value

                    elif key in string_kwargs:
                        if not isinstance(value, str):
                            continue

                        if key == "anchor":
                            anchor = cls._parse_anchor(value)
                            if anchor:
                                kwargs[key] = anchor
    # endregion
        return kwargs
# endregion


# region anchor
    @classmethod
    def _parse_anchor(cls, value: str) -> str | None:
        value_lower = value.lower()
        if value_lower == "center":
            return "center"

        value_list = list(value_lower)
        if len(value_list) == len(set(value_list)) and all(char in {"n", "s", "e", "w"} for char in value_list):
            return ''.join(value_list)
        return None
# endregion


# region sticky
    @classmethod
    def _parse_sticky(cls, value: str) -> str | None:
        value_lower = value.lower()
        value_list = list(value_lower)
        if len(value_list) == len(set(value_list)) and all(char in {"n", "s", "e", "w"} for char in value_list):
            return ''.join(value_list)
        return None
# endregion


# region font
    @classmethod
    def _parse_font(cls, data: dict) -> dict | None:
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
# endregion


# region image
    @classmethod
    def _parse_image(cls, data: dict, base_directory: Path) -> dict | None:
        light: Any = data.get("light")
        dark: Any = data.get("dark")
        size = data.get("size")

        image: dict = {}
        has_size: bool = False
        has_image: bool = False

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
            light_path: Path = cls.parse_filepath(light, base_directory)
            if light_path.suffix == ".png" and light_path.is_file():
                image["light_image"] = Image.open(light_path)
                has_image = True

        if isinstance(dark, str) and dark:
            dark_path: Path = cls.parse_filepath(dark, base_directory)
            if dark_path.suffix == ".png" and dark_path.is_file():
                image["dark_image"] = Image.open(dark_path)
                has_image = True

        if has_size and has_image:
            return image
        return None
# endregion


# region widget kwargs
    @classmethod
    def parse_widget_kwargs(cls, type: Literal["frame", "progress_bar", "label", "button", "status_label", "channel_label", "version_label", "file_version_label"], data: dict, base_directory: Path) -> dict:
        kwargs: dict = {}

        match type:
    # region - frame
            case "frame":
                int_kwargs = {"width", "height", "border_width", "corner_radius"}
                color_kwargs = {"fg_color", "border_color"}
                valid_kwargs = int_kwargs | color_kwargs

                for key in valid_kwargs:
                    value: Any = data.get(key)

                    if key in int_kwargs:
                        if isinstance(value, int) and value >= 0:
                            kwargs[key] = value

                    elif key in color_kwargs:
                        color = cls.parse_color(value)
                        if color: kwargs[key] = color
    # endregion

    # region - progress bar
            case "progress_bar":
                int_kwargs = {"width", "height", "border_width", "corner_radius"}
                color_kwargs = {"fg_color", "progress_color", "border_color"}
                string_kwargs = {"mode", "orientation"}
                float_kwargs = {"determinate_speed", "indeterminate_speed"}
                valid_kwargs = int_kwargs | color_kwargs | string_kwargs | float_kwargs

                for key in valid_kwargs:
                    value = data.get(key)

                    if key in int_kwargs:
                        if isinstance(value, int) and value >= 0:
                            kwargs[key] = value

                    elif key in float_kwargs:
                        if (isinstance(value, int) or isinstance(value, float)) and value >= 0 and value <= 1:
                            kwargs[key] = value

                    elif key in color_kwargs:
                        color = cls.parse_color(value)
                        if color: kwargs[key] = color
                    
                    elif key in string_kwargs:
                        if not isinstance(value, str):
                            continue
                        value_lower = value.lower()

                        if key == "orientation":
                            if value_lower in {"horizontal", "vertical"}:
                                kwargs[key] = value_lower

                        elif key == "mode":
                            if value_lower in {"determinate", "indeterminate"}:
                                kwargs[key] = value_lower
    # endregion

    # region - label
            case "label" | "status_label" | "channel_label" | "version_label" | "file_version_label":
                int_kwargs = {"width", "height", "corner_radius", "padx", "pady", "wraplength"}
                string_kwargs = {"text", "compound", "anchor", "justify"}
                color_kwargs = {"fg_color", "text_color"}
                font_kwargs = {"font"}
                image_kwargs = {"image"}
                valid_kwargs = int_kwargs | string_kwargs | color_kwargs | font_kwargs | image_kwargs

                for key in valid_kwargs:
                    value = data.get(key)

                    if key in int_kwargs:
                        if isinstance(value, int) and value >= 0:
                            kwargs[key] = value

                    elif key in string_kwargs:
                        if not isinstance(value, str):
                            continue

                        if key == "anchor":
                            anchor: str | None = cls._parse_anchor(value)
                            if anchor:
                                kwargs[key] = anchor

                        elif key == "compound":
                            value_lower = value.lower()
                            if value_lower in {"left", "right", "center"}:
                                kwargs[key] = value_lower
                        
                        elif key == "justify":
                            value_lower = value.lower()
                            if value_lower in {"left", "right", "center"}:
                                kwargs[key] = value_lower

                        elif key == "text":
                            kwargs[key] = value

                    elif key in color_kwargs:
                        color = cls.parse_color(value)
                        if key == "text_color" and color == "transparent":
                            continue
                        if color:
                            kwargs[key] = color
                    
                    elif key in font_kwargs:
                        if isinstance(value, dict) and value:
                            font: dict | None = cls._parse_font(value)
                            if font:
                                kwargs[key] = font

                    elif key in image_kwargs:
                        if isinstance(value, dict) and value:
                            image: dict | None = cls._parse_image(value, base_directory)
                            if image:
                                kwargs[key] = image

                kwargs["text"] = kwargs.get("text", "")
    # endregion

    # region - button
            case "button":
                int_kwargs = {"width", "height", "corner_radius", "border_width", "border_spacing"}
                boolean_kwargs = {"round_width_to_even_numbers", "round_height_to_even_numbers", "hover"}
                color_kwargs = {"fg_color", "hover_color", "border_color", "text_color"}
                string_kwargs = {"text", "compound", "anchor", "cursor"}
                font_kwargs = {"font"}
                image_kwargs = {"image"}
                valid_kwargs = int_kwargs | boolean_kwargs | color_kwargs | string_kwargs | font_kwargs | image_kwargs

                for key in valid_kwargs:
                    value = data.get(key)

                    if key in int_kwargs:
                        if isinstance(value, int) and value >= 0:
                            kwargs[key] = value

                    elif key in boolean_kwargs:
                        if isinstance(value, bool):
                            kwargs[key] = value

                    elif key in color_kwargs:
                        color = cls.parse_color(value)
                        if key in {"text_color", "text_color"} and color == "transparent":
                            continue
                        if color:
                            kwargs[key] = color

                    elif key in string_kwargs:
                        if not isinstance(value, str):
                            continue

                        if key == "anchor":
                            anchor = cls._parse_anchor(value)
                            if anchor:
                                kwargs[key] = anchor
                        
                        elif key == "compound":
                            value_lower = value.lower()
                            if value_lower in {"left", "right", "center"}:
                                kwargs[key] = value_lower

                        elif key == "text":
                            kwargs[key] = value

                    elif key in font_kwargs:
                        if isinstance(value, dict) and value:
                            font = cls._parse_font(value)
                            if font:
                                kwargs[key] = font

                    elif key in image_kwargs:
                        if isinstance(value, dict) and value:
                            image = cls._parse_image(value, base_directory)
                            if image:
                                kwargs[key] = image

                kwargs["cursor"] = kwargs.get("cursor", "hand2")
    # endregion
        return kwargs
# endregion
