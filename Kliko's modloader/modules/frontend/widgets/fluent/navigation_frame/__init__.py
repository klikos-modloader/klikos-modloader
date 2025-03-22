from pathlib import Path
from typing import Iterable, Callable, Literal
from functools import partial
from tkinter import Frame

from ..navigation_button import FluentNavigationButton

import customtkinter as ctk  # type: ignore


class Colors:
    class Dark:
        class BackgroundColor:
            hex: str = "#202020"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundSeparatorColor:
            hex: str = "#323232"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ScrollBarColor:
            hex: str = "#9A9A9A"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ScrollBarHoverColor:
            hex: str = "#9F9F9F"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)

    class Light:
        class BackgroundColor:
            hex: str = "#F3F3F3"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundSeparatorColor:
            hex: str = "#E5E5E5"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ScrollBarColor:
            hex: str = "#868686"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ScrollBarHoverColor:
            hex: str = "#8A8A8A"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)


class FluentNavigationFrame(ctk.CTkFrame):
    padding: int = 16
    padding_x: int = 16
    padding_y: int = 10
    button_width: int = 280
    width: int =  + padding_x*2
    button_gap: int = 4

    buttons_frame: ctk.CTkFrame | ctk.CTkScrollableFrame
    separator_frame_1: Frame
    separator_frame_2: Frame
    footer_frame: ctk.CTkFrame

    buttons: tuple[FluentNavigationButton, ...]
    buttons_dict: dict[FluentNavigationButton, Callable | None]

    def __init__(self, master, scrollable: bool = False, buttons: Iterable[dict] | None = None, footer_buttons: Iterable[dict] | None = None) -> None:
        self.buttons_dict = {}

        super().__init__(master, width=self.width, fg_color=(Colors.Light.BackgroundColor.hex, Colors.Dark.BackgroundColor.hex), corner_radius=0)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0, minsize=3)
        self.grid_rowconfigure(2, weight=0, minsize=1)
        self.grid_rowconfigure(3, weight=0, minsize=54)

        # Buttons
        if scrollable:
            new_width: int = self.width - 16  # hard-coded to stay the correct width on my own monitor, but will be different depending on display scaling
            self.buttons_frame = ctk.CTkScrollableFrame(self, width=new_width, fg_color=(Colors.Light.BackgroundColor.hex, Colors.Dark.BackgroundColor.hex), scrollbar_button_color=(Colors.Light.ScrollBarColor.hex, Colors.Dark.ScrollBarColor.hex), scrollbar_button_hover_color=(Colors.Light.ScrollBarHoverColor.hex, Colors.Dark.ScrollBarHoverColor.hex), corner_radius=0)
        else:
            self.buttons_frame = ctk.CTkFrame(self, width=self.width, fg_color=(Colors.Light.BackgroundColor.hex, Colors.Dark.BackgroundColor.hex), corner_radius=0)
        if buttons:
            for i, button in enumerate(buttons):
                text: str = button.get("text", "")
                image: ctk.CTkImage | None = button.get("image")
                command: Callable | None = button.get("command")

                button_object: FluentNavigationButton = FluentNavigationButton(self.buttons_frame, text=text, icon=image, width=self.button_width, threaded=False)
                button_object.command = lambda widget=button_object: self._callback(widget)
                button_object.grid(column=0, row=i, pady=(self.padding_y,0) if i == 0 else (self.button_gap, 0), padx=self.padding_x)

                self.buttons_dict[button_object] = command

        # Separator
        self.separator_frame_1 = Frame(self, width=self.width, height=2, background="red")
        self.separator_frame_2 = Frame(self, width=self.width, height=1, background="green")
        ctk.AppearanceModeTracker.add(self._on_appearance_change)
        self._on_appearance_change("Light" if ctk.AppearanceModeTracker.get_mode() == 0 else "Dark")

        # Footer
        self.footer_frame = ctk.CTkFrame(self, width=self.width, height=54, fg_color=(Colors.Light.BackgroundColor.hex, Colors.Dark.BackgroundColor.hex), corner_radius=0)
        if footer_buttons:
            footer_button_count: int = len(tuple(footer_buttons))-1
            for i, footer_button in enumerate(footer_buttons):
                text = footer_button.get("text", "")
                image = footer_button.get("image")
                command = footer_button.get("command")

                button_object = FluentNavigationButton(self.footer_frame, text=text, icon=image, width=self.button_width, threaded=False)
                button_object.command = lambda widget=button_object: self._callback(widget)
                button_object.grid(column=0, row=i, pady=(self.padding_y, 0) if i == 0 else (self.button_gap, self.padding_y) if i == footer_button_count else (self.button_gap, 0), padx=self.padding_x)
                self.buttons_dict[button_object] = command

        # Placement
        self.buttons_frame.grid(row=0, column=0, sticky="nsew")
        self.separator_frame_1.grid(row=1, column=0, sticky="ew")
        self.separator_frame_2.grid(row=2, column=0, sticky="ew")
        self.footer_frame.grid(row=3, column=0, sticky="ew")

        self.separator_frame_1.configure(height=3)
        self.separator_frame_2.configure(height=1)

        self.buttons = tuple(self.buttons_dict.keys())

    

    def _callback(self, widget: FluentNavigationButton) -> None:
        for button in self.buttons_dict:
            if button == widget: continue
            button.set_inactive()
        widget.set_active()
        command: Callable | None = self.buttons_dict.get(widget)
        if callable(command):
            self.after(10, command)

    
    def _on_appearance_change(self, mode: Literal["Light", "Dark"]) -> None:
        if mode == "Light":
            self.separator_frame_1.configure(background=Colors.Light.BackgroundColor.hex)
            self.separator_frame_2.configure(background=Colors.Light.BackgroundSeparatorColor.hex)
        else:
            self.separator_frame_1.configure(background=Colors.Dark.BackgroundColor.hex)
            self.separator_frame_2.configure(background=Colors.Dark.BackgroundSeparatorColor.hex)