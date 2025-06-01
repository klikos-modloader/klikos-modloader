from typing import Literal, Optional, Callable, TYPE_CHECKING

from modules.frontend.functions import get_ctk_image
from modules.filesystem import Resources

if TYPE_CHECKING: from ..root import Root
from ..toplevel import Toplevel
from ..frame import Frame
from ..label import Label
from ..button import Button

from customtkinter import ScalingTracker, CTkImage  # type: ignore


class Banner(Frame):
    id: str
    _row: int = -1
    _MIN_WIDTH: int = 420
    _ICON_SIZE: int = 32
    _PADX: int = 16
    _PADY: int = 16
    _GAP: int = 16
    _TITLE_MESSAGE_GAP: int = 0

    def __init__(self, master: "BannerSystem", id: str, title_key: Optional[str] = None, title_modification: Optional[Callable[[str], str]] = None, message_key: Optional[str] = None, message_modification: Optional[Callable[[str], str]] = None, mode: Literal["success", "warning", "error", "attention", "info", "neutral"] = "neutral", icon_visible: bool = True, can_close: bool = True):
        border_color = self._get_border_color(mode)
        fg_color = self._get_fg_color(mode)
        super().__init__(master, corner_radius=0, border_color=border_color, fg_color=fg_color, border_width=1)
        self.grid_columnconfigure(1, weight=1)

        self.id = id

        if icon_visible:
            image: CTkImage | None = self._get_icon(mode)
            if image is None: icon_visible = False
            else:
                padx: tuple[int, int] = (self._PADX, 0 if can_close or title_key or message_key else self._PADX)
                Label(self, image=image).grid(column=0, row=0, rowspan=2, sticky="n" if title_key and message_key else "", padx=padx, pady=self._PADY)

        if title_key:
            padx = (self._PADX, 0 if can_close else self._PADX) if icon_visible else (self._GAP, 0 if can_close else self._PADX)
            Label(self, key=title_key, modification=title_modification, style="body_strong", autowrap=True).grid(column=1, row=0, sticky="new" if message_key else "ew", padx=padx, pady=(self._PADY, self._TITLE_MESSAGE_GAP) if message_key else self._PADY)
        if message_key:
            padx = (self._PADX, 0 if can_close else self._PADX) if icon_visible else (self._GAP, 0 if can_close else self._PADX)
            Label(self, key=message_key, modification=message_modification, style="body", autowrap=True).grid(column=1, row=1, sticky="new" if title_key else "ew", padx=padx, pady=(0, self._PADY) if title_key else self._PADY)

        if can_close:
            padx = (self._PADX, self._PADX) if icon_visible or title_key or message_key else (self._GAP, self._PADX)
            image = get_ctk_image(Resources.Common.Light.CLOSE, Resources.Common.Dark.CLOSE, size=20)
            Button(self, secondary=True, image=image, width=32, height=32, command=lambda self=self: master.close_banner(self)).grid(column=2, row=0, rowspan=2, sticky="n" if title_key and message_key else "", padx=padx, pady=self._PADY)



    def _get_icon(self, mode: Literal["success", "warning", "error", "attention", "info", "neutral"]) -> CTkImage | None:
        match mode:
            case "success": return get_ctk_image(Resources.Common.Light.SUCCESS, Resources.Common.Dark.SUCCESS, self._ICON_SIZE)
            case "warning": return get_ctk_image(Resources.Common.Light.WARNING, Resources.Common.Dark.WARNING, self._ICON_SIZE)
            case "error": return get_ctk_image(Resources.Common.Light.ERROR, Resources.Common.Dark.ERROR, self._ICON_SIZE)
            case "attention": return get_ctk_image(Resources.Common.Light.ATTENTION, Resources.Common.Dark.ATTENTION, self._ICON_SIZE)
            case "info": return get_ctk_image(Resources.Common.Light.INFO, Resources.Common.Dark.INFO, self._ICON_SIZE)
            case _: return None


    def _get_fg_color(self, mode: Literal["success", "warning", "error", "attention", "info", "neutral"]) -> tuple[str, str]:
        match mode:
            case "success": return ("#DFF6DD", "#1E3A2F")
            case "warning": return ("#FFF3C4", "#3A2E1E")
            case "error": return ("#F9D6D6", "#3F1D1D")
            case "attention": return ("#F0E0FF", "#362A45")
            case "info": return ("#D4E8FF", "#1C3A5E")
            case "neutral": return ("#E5E5E5", "#272727")


    def _get_border_color(self, mode: Literal["success", "warning", "error", "attention", "info", "neutral"]) -> tuple[str, str]:
        match mode:
            case "success": return ("#4ADE80", "#10B981")
            case "warning": return ("#FACC15", "#EAB308")
            case "error": return ("#F87171", "#EF4444")
            case "attention": return ("#C084FC", "#A855F7")
            case "info": return ("#3B82F6", "#3BA0F2")
            case "neutral": return ("#B0B0B0", "#404040")


class BannerSystem(Toplevel):
    _root: "Root"
    _banner_id_counter: int
    _banners: dict[str, Banner]
    _active: bool
    _geometry: str = ""

    _UPDATE_LOOP_INTERVAL: int = 10
    _TRANSPARENT_COLOR: str = "red"
    _MIN_WIDTH: int = Banner._MIN_WIDTH
    _PADX: int = 20
    _PADY: int = 20
    _GAP: int = 16


    def __init__(self, root: "Root"):
        super().__init__(title="BannerSystem", hidden=True, master=root)
        self.overrideredirect(True)
        self.transient(root)

        self.grid_columnconfigure(0, weight=1)
        self.configure(fg_color=self._TRANSPARENT_COLOR)
        self.attributes("-transparentcolor", self._TRANSPARENT_COLOR)
        self.protocol("WM_DELETE_WINDOW", self._on_force_close)

        self.root = root
        self._banner_id_counter = 0
        self._banners = {}
        self._active = False


    def _on_force_close(self):
        command = self.root.protocol("WM_DELETE_WINDOW")
        if callable(command): command()
        elif isinstance(command, str): self.root.eval(command)


    def send_banner(self, title_key: Optional[str] = None, title_modification: Optional[Callable[[str], str]] = None, message_key: Optional[str] = None, message_modification: Optional[Callable[[str], str]] = None, mode: Literal["success", "warning", "error", "attention", "info", "neutral"] = "neutral", icon_visible: bool = True, can_close: bool = True, auto_close_after_ms: int = 0) -> str:
        self._banner_id_counter += 1
        id: str = str(self._banner_id_counter)

        banner: Banner = Banner(self, id, title_key=title_key, title_modification=title_modification, message_key=message_key, message_modification=message_modification, mode=mode, icon_visible=icon_visible, can_close=can_close)
        self._banners[id] = banner

        if not self._active:
            self._active = True
            self.after(0, self._loop)
        
        if auto_close_after_ms > 0: self.after(auto_close_after_ms, self.close_banner, id)

        return id


    def close_banner(self, banner_or_id: str | Banner) -> None:
        if isinstance(banner_or_id, str): id: str = banner_or_id
        else: id = banner_or_id.id
        banner: Banner | None = self._banners.pop(id, None)
        if banner is not None and banner.winfo_exists(): banner.destroy()
        if not self._banners: self._active = False


    def _get_stack_order(self, window) -> int:
        stack_order: str = window.tk.eval(f"wm stackorder {self.root}")
        window_ids: list[str] = stack_order.split()
        index: int = window_ids.index(f"{window}")
        return index


    # HELD TOGETHER BY HOPES AND DREAMS. DO NOT CHANGE UNLESS NECESSARY !!!
    def _loop(self) -> None:
        self.root.update_idletasks()
        root_visible: bool = self.root.winfo_ismapped()
        self_visible: bool = self.winfo_ismapped()

        if not self._active or not self._banners:
            if self_visible: self.withdraw()
            self._active = False
            return

        self.after(self._UPDATE_LOOP_INTERVAL, self._loop)
        if not root_visible:
            if self_visible: self.withdraw()
            return

        window_scaling: float = ScalingTracker.get_window_scaling(self.root)
        window_x: int = self.root.winfo_rootx()
        window_y: int = self.root.winfo_rooty()
        window_w: int = int(self.root.winfo_width() / window_scaling)
        window_h: int = int(self.root.winfo_height() / window_scaling)

        min_width: int = int(self._MIN_WIDTH * window_scaling)

        requested_height: int = window_h - 2 * int(self._PADY * window_scaling)
        if requested_height < 1:
            if self_visible: self.withdraw()
            return

        try: window_stack_order: int = self._get_stack_order(self.root)
        except ValueError:
            if self_visible: self.withdraw()
            return

        if not self_visible:
            self.deiconify()
            self.transient(self.root)
        try:
            if window_stack_order > self._get_stack_order(self): self.lift(aboveThis=self.root)
        except ValueError:
            if self_visible: self.withdraw()
            return

        requested_width_normal: int = window_w - 2 * self._PADX
        requested_width_scaled: int = window_w - 2 * int(self._PADX * window_scaling)
        banner_w_normal: int = max(min_width, requested_width_normal)
        banner_w_scaled: int = max(min_width, requested_width_scaled)
        banner_x: int = window_x + (window_w - banner_w_scaled) // 2
        banner_y: int = window_y + int(self._PADY * window_scaling)

        for i, banner in enumerate(list(self._banners.values())):
            if banner._row != i:
                banner.grid(column=0, row=i, sticky="ew", pady=0 if i == 0 else (self._GAP, 0))
                banner._row = i

        self.update_idletasks()
        banner_h: int = min(int(self.winfo_reqheight() / window_scaling), int(requested_height / window_scaling))
        geometry: str = f"{banner_w_normal}x{banner_h}+{banner_x}+{banner_y}"
        if geometry != self._geometry:
            self.geometry(geometry)
            self._geometry = geometry