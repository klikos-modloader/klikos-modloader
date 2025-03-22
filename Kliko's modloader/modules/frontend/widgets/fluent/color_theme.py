from pathlib import Path

import customtkinter as ctk


THEME_FILE: Path = Path(__file__).parent / "theme.json"


def apply_color_theme() -> None:
    ctk.set_default_color_theme(str(THEME_FILE.resolve()))