from tkinter import TclError
from customtkinter import ThemeManager  # type: ignore


def get_fg_color(widget) -> tuple[str, str]:
    while widget is not None:
        if hasattr(widget, "cget"):
            color: str | tuple[str, str] | None = None
            try: color = widget.cget("fg_color")
            except (TclError, AttributeError): pass
            if isinstance(color, str) and color != "transparent": color = (color, color)
            if isinstance(color, tuple): return color
        widget = getattr(widget, "master", None)
    fallback = ThemeManager.theme["CTkFrame"]["fg_color"]
    if isinstance(fallback, str): fallback = (fallback, fallback)
    return fallback