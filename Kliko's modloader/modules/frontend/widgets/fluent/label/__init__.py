import webbrowser
from typing import Literal

import winaccent  # type: ignore
import customtkinter as ctk  # type: ignore


class Colors:
    class Dark:
        class HyperlinkColor:
            hex: str = winaccent.accent_light_3
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class HyperlinkHoverColor:
            hex: str = winaccent.accent_light_3
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class HyperlinkActiveColor:
            hex: str = winaccent.accent_light_2
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
    
    class Light:
        class HyperlinkColor:
            hex: str = winaccent.accent_dark_2
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class HyperlinkHoverColor:
            hex: str = winaccent.accent_dark_3
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class HyperlinkActiveColor:
            hex: str = winaccent.accent_dark_1
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)


class FluentLabel(ctk.CTkLabel):
    is_hyperlink: bool = False
    url: str = ""
    hovered: bool = False
    clicked: bool = False
    font: ctk.CTkFont
    font_underlined: ctk.CTkFont

    def __init__(self, master, text: str = "", image: ctk.CTkImage | None = None, width: int = 0, height: int = 28, font_size: int = 13, font_weight: Literal["normal", "bold"] = "normal", slant: Literal["italic", "roman"] = "roman", underline: bool = False, overstrike: bool = False, hyperlink: bool = False, hyperlink_url: str = "", **kwargs) -> None:
        super().__init__(master, text=text, image=image, width=width, height=height, fg_color=kwargs.pop("fg_color", "transparent"), font=ctk.CTkFont(family="Segoe UI", size=font_size, weight=font_weight, slant=slant, underline=underline, overstrike=overstrike), **kwargs)

        self.is_hyperlink = hyperlink
        if self.is_hyperlink:
            self.url = hyperlink_url
            self.font = ctk.CTkFont(family="Segoe UI", size=font_size, weight=font_weight, slant=slant, underline=False, overstrike=overstrike)
            self.font_underlined = ctk.CTkFont(family="Segoe UI", size=font_size, weight=font_weight, slant=slant, underline=True, overstrike=overstrike)
            self.configure(cursor="hand2")
            self._set_hyperlink_color()

            self.bind("<Button-1>", self._on_click)
            self.bind("<ButtonRelease-1>", self._on_unclick)
            self.bind("<Button-2>", self._on_click)
            self.bind("<ButtonRelease-2>", self._on_unclick)
            self.bind("<Enter>", self._on_hover)
            self.bind("<Leave>", self._on_unhover)
        
    
    def _on_hover(self, _) -> None:
        if not self.is_hyperlink: return
        self.hovered = True
        self._set_hyperlink_color()
        
    
    def _on_unhover(self, _) -> None:
        if not self.is_hyperlink: return
        self.hovered = False
        self._set_hyperlink_color()
        
    
    def _on_click(self, _) -> None:
        if not self.is_hyperlink: return
        self.clicked = True
        self._set_hyperlink_color()
        
    
    def _on_unclick(self, _) -> None:
        if not self.is_hyperlink: return
        self.clicked = False
        self._set_hyperlink_color()
        if self.hovered and self.url: webbrowser.open(self.url, 2)
    

    def _set_hyperlink_color(self) -> None:
        if self.clicked: self.configure(text_color=(Colors.Light.HyperlinkActiveColor.hex, Colors.Dark.HyperlinkActiveColor.hex), font=self.font)
        elif self.hovered: self.configure(text_color=(Colors.Light.HyperlinkHoverColor.hex, Colors.Dark.HyperlinkHoverColor.hex), font=self.font)
        else: self.configure(text_color=(Colors.Light.HyperlinkColor.hex, Colors.Dark.HyperlinkColor.hex), font=self.font_underlined)