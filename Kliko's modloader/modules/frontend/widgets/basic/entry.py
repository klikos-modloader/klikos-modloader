from typing import Callable, Optional, Literal, NamedTuple
from tkinter import StringVar

from .localized import LocalizedCTkEntry
from .utils import WinAccentTracker, FontStorage

import winaccent  # type: ignore


class Event(NamedTuple):
    widget: "Entry"
    value: str


class Entry(LocalizedCTkEntry):
    focused: bool
    hovered: bool
    command: Optional[Callable]
    reset_on_focus_lost: bool
    command_on_focus_lost: bool
    run_command_if_empty: bool
    reset_if_empty: bool
    last_value: str = ""
    _suppress_next_focus_out: bool = False

    background_color: tuple[str, str] = ("#FBFBFB", "#2D2D2D")
    border_color: tuple[str, str] = ("#E5E5E5", "#303030")

    background_color_hovered: tuple[str, str] = ("#F6F6F6", "#323232")
    border_color_hovered: tuple[str, str] = ("#E5E5E5", "#303030")

    background_color_focused: tuple[str, str] = ("#FFFFFF", "#1F1F1F")
    border_color_focused: tuple[str, str] = (winaccent.accent_dark_1, winaccent.accent_light_2)

    def __init__(self, master, command: Optional[Callable] = None, on_focus_lost: Optional[Literal["command", "reset"]] = None, run_command_if_empty: bool = False, reset_if_empty: bool = False, **kwargs):
        if "font" not in kwargs: kwargs["font"] = FontStorage.get(size=14)
        if "text_color" not in kwargs: kwargs["text_color"] = ("#1A1A1A", "#FFFFFF")
        if "placeholder_text_color" not in kwargs: kwargs["placeholder_text_color"] = ("#5C5C5C", "#CCCCCC")
        if "corner_radius" not in kwargs: kwargs["corner_radius"] = 4
        if "border_width" not in kwargs: kwargs["border_width"] = 1
        if "height" not in kwargs: kwargs["height"] = 32
        textvariable = kwargs.get("textvariable", None)
        if isinstance(textvariable, StringVar):
            self.last_value = textvariable.get()
        super().__init__(master, **kwargs)
        self.focused = False
        self.hovered = False
        self.command = command
        self.reset_on_focus_lost = on_focus_lost == "reset"
        self.command_on_focus_lost = on_focus_lost == "command"
        self.run_command_if_empty = run_command_if_empty
        self.reset_if_empty = reset_if_empty
        WinAccentTracker.add_callback(lambda: self.after(0, self._on_accent_change))
        self._on_accent_change()
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<Enter>", self._on_hover_in)
        self.bind("<Leave>", self._on_hover_out)
        self.bind("<Return>", self._on_confirm)
        self.bind("<Escape>", self._on_escape)


    def set(self, value: str) -> None:
        self.delete("0", "end")
        self.insert("0", value)
        self.last_value = value


    def _on_accent_change(self) -> None:
        self.border_color_focused = (winaccent.accent_dark_1, winaccent.accent_light_2)
        self._entry.configure(selectbackground=winaccent.accent_normal)
        self._update_colors()


    def _on_confirm(self, _) -> None:
        self._suppress_next_focus_out = True
        self.winfo_toplevel().focus_set()
        self._on_focus_out(run_callback=True)


    def _on_escape(self, _) -> None:
        self._suppress_next_focus_out = True
        self.winfo_toplevel().focus_set()
        self.focused = False
        self._update_colors()
        self.set(self.last_value)


    def _on_focus_in(self, _) -> None:
        self.focused = True
        self._update_colors()


    def _on_focus_out(self, *_, run_callback: bool = False) -> None:
        if self._suppress_next_focus_out:
            self._suppress_next_focus_out = False
            return
        self.focused = False
        self._update_colors()
        value: str = self.get()

        if self.reset_if_empty and value == "":
            self.set(self.last_value)

        elif (run_callback or self.command_on_focus_lost):
            self.last_value = value
            if self.command is not None and (self.run_command_if_empty or value != ""):
                event: Event = Event(self, value)
                self.command(event)

        elif self.reset_on_focus_lost and value != "" and value != self.last_value:
            self.set(self.last_value)


    def _on_hover_in(self, _) -> None:
        self.hovered = True
        self._update_colors()


    def _on_hover_out(self, _) -> None:
        self.hovered = False
        self._update_colors()


    def _update_colors(self) -> None:
        if self.focused: self.configure(border_color=self.border_color_focused, fg_color=self.background_color_focused)
        elif self.hovered: self.configure(border_color=self.border_color_hovered, fg_color=self.background_color_hovered)
        else: self.configure(border_color=self.border_color, fg_color=self.background_color)