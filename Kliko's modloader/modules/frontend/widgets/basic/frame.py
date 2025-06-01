from pathlib import Path
from typing import Optional, Callable, Any
import re

from customtkinter import CTkFrame  # type: ignore
from tkinterdnd2 import DND_FILES  # type: ignore


class Frame(CTkFrame):
    dnd_command: Optional[Callable[[tuple[Path, ...]], Any]]


    def __init__(self, master, transparent: bool = False, round: bool = True, border: bool = True, layer: int = 0, dnd_command: Optional[Callable[[tuple[Path, ...]], Any]] = None, **kwargs) -> None:
        layer = self._normalize_layer(layer)
        fg_color: str | tuple[str, str] = "transparent"
        border_color: str | tuple[str, str] | None = None
        if not transparent:
            if layer == 0:
                fg_color = ("#F3F3F3", "#202020")
                border = False
            elif layer == 1:
                fg_color = ("#F9F9F9", "#272727")
                border_color = ("#E5E5E5", "#1D1D1D")
            elif layer == 2:
                fg_color = ("#F3F3F3", "#202020")
                border_color = ("#EAEAEA", "#232323")
            elif layer == 3:
                fg_color = ("#FBFBFB", "#323232")
                border_color = ("#E5E5E5", "#323232")
        else:
            border = False
            round = False
        if "border_color" not in kwargs: kwargs["border_color"] = border_color
        if "border_width" not in kwargs: kwargs["border_width"] = 1 if border else 0
        if "corner_radius" not in kwargs: kwargs["corner_radius"] = 4 if round else 0
        if "fg_color" not in kwargs: kwargs["fg_color"] = fg_color
        super().__init__(master, **kwargs)
        self.bind("<ButtonPress-1>", lambda _: self.focus_set())
        self.dnd_command = dnd_command
        if self.dnd_command:
            self.drop_target_register(DND_FILES)  # type: ignore
            self.dnd_bind("<<Drop>>", self._dnd_callback)  # type: ignore


    def _dnd_callback(self, event) -> None:
        if not callable(self.dnd_command): return
        matches = re.findall(r'\{([^}]+)\}|([A-Za-z]:/[\S]+)', event.data)
        paths = tuple(Path(path) for match in matches for path in match if path)
        self.dnd_command(paths)


    def _normalize_layer(self, layer: int) -> int:
        if layer > 0: return (layer - 1) % 3 + 1
        elif layer < 0: return (layer % 3) + 1
        return layer