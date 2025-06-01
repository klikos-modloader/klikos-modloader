from customtkinter import CTkScrollableFrame


class ScrollableFrame(CTkScrollableFrame):
    def __init__(self, master, transparent: bool = False, round: bool = True, border: bool = True, layer: int = 0, **kwargs) -> None:
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


    def _normalize_layer(self, layer: int) -> int:
        if layer > 0: return (layer - 1) % 3 + 1
        elif layer < 0: return (layer % 3) + 1
        return layer