from typing import Callable

import customtkinter as ctk  # type: ignore


class Colors:
    class Dark:
        class BackgroundColor:
            hex: str = "#2D2D2D"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundHoverColor:
            hex: str = "#323232"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundActiveColor:
            hex: str = "#272727"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundDisabledColor:
            hex: str = "#2A2A2A"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderColor:
            hex: str = "#303030"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)

    class Light:
        class BackgroundColor:
            hex: str = "#FBFBFB"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundHoverColor:
            hex: str = "#F6F6F6"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundActiveColor:
            hex: str = "#F5F5F5"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundDisabledColor:
            hex: str = "#F5F5F5"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderColor:
            hex: str = "#E5E5E5"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)


class ColorsToplevel:
    class Dark:
        class BackgroundColor:
            hex: str = "#343434"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundHoverColor:
            hex: str = "#3A3A3A"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundActiveColor:
            hex: str = "#2E2E2E"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundDisabledColor:
            hex: str = "#2A2A2A"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderColor:
            hex: str = "#373737"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)

    class Light:
        class BackgroundColor:
            hex: str = "#FDFDFD"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundHoverColor:
            hex: str = "#F9F9F9"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundActiveColor:
            hex: str = "#F9F9F9"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundDisabledColor:
            hex: str = "#F5F5F5"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderColor:
            hex: str = "#EAEAEA"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)


class FluentButtonFrame(ctk.CTkFrame):
    active: bool = False
    enabled: bool = False
    hovered: bool = False
    command: Callable | None
    threaded: bool
    
    _toplevel: bool
    def __init__(self, master, width: int = 200, height: int = 200, rounded: bool = True, border: bool = True, command: Callable | None = None, threaded: bool = False, disabled: bool = False, toplevel: bool = False, corner_radius: int = 4) -> None:
        border_color = (ColorsToplevel.Light.BorderColor.hex, ColorsToplevel.Dark.BorderColor.hex) if toplevel else (Colors.Light.BorderColor.hex, Colors.Dark.BorderColor.hex)
        super().__init__(master, cursor="hand2", width=width, height=height, corner_radius=corner_radius if rounded else 0, border_width = 0 if not border else 1, border_color=border_color)
        self.enabled = not disabled
        self.command = command
        self.threaded = threaded
        self._toplevel = toplevel
        self._set_fg_color()
        
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_unclick)
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_unhover)

        # self.after(10, self.bind_all_children)
    

    def bind_all_children(self) -> None:
        def bind_widget_children(widget) -> None:
            for widget in widget.winfo_children():
                widget.bind("<Button-1>", self._on_click)
                widget.bind("<ButtonRelease-1>", self._on_unclick)
                widget.bind("<Enter>", self._on_hover)
                widget.bind("<Leave>", self._on_unhover)
                if isinstance(widget, ctk.CTkFrame):
                    self.after(10, bind_widget_children, widget)

        for widget in self.winfo_children():
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<ButtonRelease-1>", self._on_unclick)
            widget.bind("<Enter>", self._on_hover)
            widget.bind("<Leave>", self._on_unhover)
            if isinstance(widget, ctk.CTkFrame):
                self.after(10, bind_widget_children, widget)
    

    def _is_toplevel(self) -> str | tuple[str, str]:
        return self.winfo_parent() == "."


    def is_enabled(self) -> bool:
        return self.enabled


    def enable(self) -> None:
        self.enabled = True
        self._set_fg_color()
    

    def disable(self) -> None:
        self.enabled = False
        self._set_fg_color()
    

    def _on_click(self, _) -> None:
        if not self.enabled: return
        self.active = True
        self._set_fg_color()


    def _on_unclick(self, event) -> None:
        def is_child_of_self(widget, max_recursion_depth: int = 100) -> bool:
            if widget == self: return True
            i: int = 0
            while True:
                widget = widget.master
                if not widget: return False
                if widget == self: return True
                i += 1
                if i > max_recursion_depth:
                    return False

        self.active = False
        self._set_fg_color()

        hovered_widget = self.winfo_containing(event.x_root, event.y_root)
        if hovered_widget and is_child_of_self(hovered_widget):
            if callable(self.command):
                if self.threaded:
                    self.after(10, self.command)
                else:
                    self.command()


    def _on_hover(self, _) -> None:
        self.hovered = True
        self._set_fg_color()


    def _on_unhover(self, _) -> None:
        self.hovered = False
        self._set_fg_color()
    

    def _set_fg_color(self) -> None:
        if not self.enabled: self.configure(fg_color=(ColorsToplevel.Light.BackgroundDisabledColor.hex, ColorsToplevel.Dark.BackgroundDisabledColor.hex) if self._toplevel else (Colors.Light.BackgroundDisabledColor.hex, Colors.Dark.BackgroundDisabledColor.hex))
        elif self.active: self.configure(fg_color=(ColorsToplevel.Light.BackgroundActiveColor.hex, ColorsToplevel.Dark.BackgroundActiveColor.hex) if self._toplevel else (Colors.Light.BackgroundActiveColor.hex, Colors.Dark.BackgroundActiveColor.hex))
        elif self.hovered: self.configure(fg_color=(ColorsToplevel.Light.BackgroundHoverColor.hex, ColorsToplevel.Dark.BackgroundHoverColor.hex) if self._toplevel else (Colors.Light.BackgroundHoverColor.hex, Colors.Dark.BackgroundHoverColor.hex))
        else: self.configure(fg_color=(ColorsToplevel.Light.BackgroundColor.hex, ColorsToplevel.Dark.BackgroundColor.hex) if self._toplevel else (Colors.Light.BackgroundColor.hex, Colors.Dark.BackgroundColor.hex))
