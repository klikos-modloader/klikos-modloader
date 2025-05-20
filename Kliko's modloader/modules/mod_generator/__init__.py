from typing import Literal, Optional

from modules.logger import Logger

from .utils import MaskStorage

from PIL import Image  # type: ignore


class ModGenerator:
    _LOG_PREFIX: str = "ModGenerator"


    @classmethod
    def get_mask(cls, mode: Literal["color", "gradient", "custom"], data: tuple[int, int, int] | list[tuple[float, tuple[int, int, int]]] | Image.Image, size: tuple[int, int], angle: Optional[float] = None)  -> Image.Image:
        """Assumes data has already been validated"""

        match mode:
            case "color": return MaskStorage.get_solid_color(data, size, dont_cache=True)  # type: ignore
            case "gradient": return MaskStorage.get_gradient(data, angle or 0, size, dont_cache=True)  # type: ignore
            case "custom": return MaskStorage.get_custom(data, size, dont_cache=True)  # type: ignore


    @classmethod
    def generate_preview_mask(cls, mode: Literal["color", "gradient", "custom"], data: tuple[int, int, int] | list[tuple[float, tuple[int, int, int]]] | Image.Image, size: tuple[int, int], angle: Optional[float] = None)  -> Image.Image:
        cls._validate_data(mode, data)
        return cls.get_mask(mode, data, size, angle)


    # @classmethod
    # def generate_preview_image(cls, mode: Literal["color", "gradient", "custom"], data: tuple[int, int, int] | list[tuple[float, tuple[int, int, int]]] | Image.Image, size: tuple[int, int], angle: Optional[float] = None)  -> Image.Image:
    #     cls._validate_data(mode, data)
    #     mask: Image.Image = cls.get_mask(mode, data, size, angle)
    #     return


    @classmethod
    def _validate_data(cls, mode: Literal["color", "gradient", "custom"], data: tuple[int, int, int] | list[tuple[float, tuple[int, int, int]]] | Image.Image) -> None:
        match mode:
            case "color":
                if (
                    not isinstance(data, (tuple, list))
                    or len(data) != 3
                    or not all(
                        isinstance(item, int)
                        and item >= 0
                        and item <= 255
                        for item in data
                    )
                ): raise ValueError("data must be a list or tuple of 3 int values between 0 and 255")

            case "gradient":
                if (
                    not isinstance(data, (tuple, list))
                    or len(data) < 2
                    or not all(  # type: ignore
                        isinstance(stop_color, (tuple, list))
                        and len(stop_color) == 2
                        and isinstance(stop_color[0], (int, float))
                        and stop_color[0] >= 0 and stop_color[0] <= 1
                        and isinstance(stop_color[1], (tuple, list))
                        and len(stop_color[1]) == 3
                        and all(
                            isinstance(rgb_value, int)
                            and rgb_value >= 0
                            and rgb_value <= 255
                            for rgb_value in stop_color[1]
                        )
                        for stop_color in data
                    )
                ): raise ValueError("data must be a list or tuple of a float value between 0 and 1 and a tuple of 3 int values between 0 and 255")

            case "custom":
                if not isinstance(data, Image.Image):
                    raise ValueError("data must be an Image.Image object")

            case invalid:
                raise ValueError(f"Invalid mode: '{invalid}', must be one of 'color', 'gradient', 'custom'")