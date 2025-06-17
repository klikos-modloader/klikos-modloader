from typing import TYPE_CHECKING
from tkinter import BooleanVar
from pathlib import Path
import re

from modules.project_data import ProjectData
from modules.localization import Localizer
from modules.logger import Logger
from modules.filesystem import Resources, Directories
from modules.frontend.widgets import Toplevel, ScrollableFrame, Frame, CheckBox, Label, Button
from modules.frontend.menu.dataclasses import Shortcut
if TYPE_CHECKING: from modules.frontend.widgets import Root

from PIL import Image  # type: ignore
from customtkinter import ScalingTracker  # type: ignore


class ShortcutToDesktopWindow(Toplevel):
    root: "Root"
    desktop: Path
    _selected: set[Shortcut]

    LIST_ENTRY_GAP: int = 4
    LIST_BUTTON_GAP: int = 16
    WINDOW_PADDING: tuple[int, int] = (20, 20)
    LIST_FRAME_SIZE: tuple[int, int] = (256, 256)

    _LOG_PREFIX: str = "ShortcutToDesktopWindow"


    def __init__(self, master: "Root", shortcuts: list[Shortcut], desktop_path: Path):
        window_title: str = Localizer.format(Localizer.Strings["menu.shortcuts.shortcut_to_desktop_window.window_title"], {"{app.name}": ProjectData.NAME})
        super().__init__(window_title, icon=Resources.FAVICON, centered=False, hidden=True)
        self.grid_columnconfigure(0, weight=1, minsize=self.LIST_FRAME_SIZE[0] + self.WINDOW_PADDING[0] + 16 + 28)  # 🖕
        self.grid_rowconfigure(0, weight=1, minsize=self.LIST_FRAME_SIZE[1])
        self.resizable(False, False)
        self.root = master
        self.desktop = desktop_path
        self._selected = set()

        list_frame: ScrollableFrame = ScrollableFrame(self, transparent=True)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid(column=0, row=0, sticky="nsew", padx=(self.WINDOW_PADDING[0], 0), pady=(self.WINDOW_PADDING[1], 0))

        for i, shortcut in enumerate(shortcuts):
            frame: Frame = Frame(list_frame, transparent=True)
            frame.grid_columnconfigure(1, weight=1, minsize=self.LIST_FRAME_SIZE[0])
            frame.grid(column=0, row=i, sticky="nsew", pady=0 if i == 0 else self.LIST_ENTRY_GAP, padx=(0, self.WINDOW_PADDING[0]))

            var: BooleanVar = BooleanVar(frame, value=False)
            CheckBox(frame, width=0, variable=var, command=lambda var=var, shortcut=shortcut: self.toggle_shortcut(shortcut, var.get())).grid(column=0, row=0, sticky="n")
            Label(frame, shortcut.name, style="body", autowrap=False, dont_localize=True, width=self.LIST_FRAME_SIZE[0], wraplength=self.LIST_FRAME_SIZE[0]).grid(column=1, row=0, sticky="new")

        button_wrapper: Frame = Frame(self, transparent=True)
        button_wrapper.grid_columnconfigure((0, 1), weight=1, uniform="group")
        button_wrapper.grid(column=0, row=1, sticky="nsew", pady=(self.LIST_BUTTON_GAP, self.WINDOW_PADDING[1]), padx=self.WINDOW_PADDING[0])

        Button(button_wrapper, "button.ok", command=self.on_ok).grid(column=0, row=0, sticky="ew")
        Button(button_wrapper, "button.cancel", secondary=True, command=self.on_cancel).grid(column=1, row=0, padx=(8, 0), sticky="ew")

        # Show window
        self.center_on_root()
        self.deiconify()
        self.focus()
        self.lift(aboveThis=self.root)
        self.after_idle(self.lift, self.root)
        self.after_idle(self.focus)
        self.after(200, self.lift, self.root)
        self.after(200, self.focus)
        ScalingTracker.add_window(self._on_scaling_change, self)


    def center_window(self) -> None:
        self.update_idletasks()
        width: int = int(self.winfo_reqwidth() / ScalingTracker.get_window_scaling(self))
        height: int = int(self.winfo_reqheight() / ScalingTracker.get_window_scaling(self))
        self.geometry(f"{width}x{height}+{(self.winfo_screenwidth() - width)//2}+{(self.winfo_screenheight() - height)//2}")


    def center_on_root(self) -> None:
        self.root.update_idletasks()
        self.update_idletasks()
        root_scaling: float = ScalingTracker.get_window_scaling(self.root)
        self_scaling: float = ScalingTracker.get_window_scaling(self)

        root_x: int = self.root.winfo_rootx()
        root_y: int = self.root.winfo_rooty()
        root_w: int = int(self.root.winfo_width() / root_scaling)
        root_h: int = int(self.root.winfo_height() / root_scaling)
        width: int = int(self.winfo_reqwidth() / self_scaling)
        height: int = int(self.winfo_reqheight() / self_scaling)

        self.geometry(f"{width}x{height}+{root_x + int((root_w - width) / 2)}+{root_y + int((root_h - height) / 2)}")


    def _on_scaling_change(self, widget_scaling: float, window_scaling: float) -> None:
        self.update_idletasks()
        width: int = int(self.winfo_reqwidth() / window_scaling)
        height: int = int(self.winfo_reqheight() / window_scaling)
        self.geometry(f"{width}x{height}")


# region functions
    def on_ok(self, *_) -> None:
        selected: set[Shortcut] = self._selected
        for shortcut in selected:
            Logger.info(f"Creating shortcut... (id={shortcut.place_id})", prefix=self._LOG_PREFIX)

            deeplink = rf"roblox://experiences/start?placeId={shortcut.place_id}"
            safe_name: str = re.sub(r'[\\/*?:"<>|]', "", shortcut.name)
            target: Path = self.desktop / f"{safe_name}.url"

            try:
                has_icon: bool = True
                icon_target: Path = Directories.SHORTCUTS_DESKTOP_ICON_CACHE.resolve() / f"{shortcut.place_id}.ico"
                if not icon_target.exists():
                    thumbnail: Image.Image | tuple[Image.Image, Image.Image] = shortcut.get_thumbnail()
                    if isinstance(thumbnail, tuple):  # Don't set thumbnail if placeholder
                        has_icon = False
                    else:
                        icon_target.parent.mkdir(parents=True, exist_ok=True)
                        thumbnail.save(icon_target, sizes=[(16, 16), (20, 20), (24, 24), (30, 30), (32, 32), (36, 36), (40, 40), (48, 48), (60, 60), (64, 64), (72, 72), (80, 80), (96, 96), (256, 256)])

                content_string: str = f"""[InternetShortcut]
    URL={deeplink}"""
                if has_icon: content_string += f"""
    IconFile={str(icon_target)}
    IconIndex=0"""

                with open(target, "w") as file:
                    file.write(content_string)

            except Exception as e:
                Logger.error(f"Failed to create shortcut! {type(e).__name__}: {e}", prefix=self._LOG_PREFIX)
                self.root.send_banner(
                    title_key="menu.shortcuts.exception.title.failed_to_add",
                    message_key="menu.shortcuts.exception.message.unknown",
                    message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                    mode="error", auto_close_after_ms=6000
                )

        self.destroy()


    def on_cancel(self, *_) -> None:
        self.destroy()


    def toggle_shortcut(self, shortcut: Shortcut, value: bool) -> None:
        if value:
            self._selected.add(shortcut)
        else:
            try: self._selected.remove(shortcut)
            except KeyError:  pass
# endregion