from typing import Literal

from ..basic import Frame


class ColorPicker(Frame):
    def __init__(self, master) -> None:
        pass


    def redraw_all(self) -> None:
        pass


    def _on_scaling_change(self, widget_scaling: float, window_scaling: float) -> None:
        pass


    def _on_appearance_change(self, appearance: Literal["light", "dark"]) -> None:
        pass