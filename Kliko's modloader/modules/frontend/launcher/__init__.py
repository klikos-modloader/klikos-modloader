from typing import Literal

from .window import Window


def run(mode: Literal["Player", "Studio"]) -> None:
    Window(mode).mainloop()