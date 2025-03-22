import customtkinter as ctk  # type: ignore


class Colors:
    class Dark:
        class BackgroundColor:
            hex: str = "#202020"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TopBackgroundColor:
            hex: str = "#272727"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderColor:
            hex: str = "#1D1D1D"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ScrollbarColor:
            hex: str = "#9D9D9D"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ScrollbarHoverColor:
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
        class TopBackgroundColor:
            hex: str = "#F9F9F9"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderColor:
            hex: str = "#E5E5E5"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ScrollbarColor:
            hex: str = "#868686"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class ScrollbarHoverColor:
            hex: str = "#8A8A8A"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)


class FluentScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, width: int = 200, height: int = 200, rounded: bool = True, border: bool = True, toplevel: bool = False) -> None:
        super().__init__(master, width=width, height=height, corner_radius=4 if rounded else 0, scrollbar_button_color=(Colors.Light.ScrollbarColor.hex, Colors.Dark.ScrollbarColor.hex), scrollbar_button_hover_color=(Colors.Light.ScrollbarHoverColor.hex, Colors.Dark.ScrollbarHoverColor.hex))
        fg_color = (Colors.Light.TopBackgroundColor.hex, Colors.Dark.TopBackgroundColor.hex) if (toplevel or self._is_toplevel()) else (Colors.Light.BackgroundColor.hex, Colors.Dark.BackgroundColor.hex)
        border_color = (Colors.Light.BorderColor.hex, Colors.Dark.BorderColor.hex)
        border_width: int = 0 if not border else 1
        self.configure(fg_color=fg_color, border_color=border_color, border_width=border_width)
    

    def _is_toplevel(self) -> str | tuple[str, str]:
        return self.winfo_parent() == ".!ctkframe.!canvas"