from tkinter import TclError, messagebox
from threading import Thread
from typing import TYPE_CHECKING

from modules.logger import Logger
from modules.project_data import ProjectData
from modules.frontend.widgets import ScrollableFrame, Frame, Label, Button, InputDialog
from modules.frontend.functions import get_ctk_image
from modules.frontend.menu.dataclasses import Shortcut
from modules.localization import Localizer
from modules.filesystem import Resources
from modules.interfaces.shortcuts import ShortcutsInterface
from modules.networking import requests, Response, Api, RequestException

if TYPE_CHECKING: from modules.frontend.widgets import Root

from PIL import Image  # type: ignore
from customtkinter import CTkImage, ScalingTracker  # type: ignore


class ShortcutsSection(ScrollableFrame):
    loaded: bool = False
    root: "Root"
    shortcuts_wrapper: Frame
    _frames: dict[str, Frame]

    _update_id: str | None = None
    _debounce: int = 100

    placeholder_thumbnail: tuple[Image.Image, Image.Image]
    THUMBNAIL_SIZE: int = 144

    _SECTION_PADX: int | tuple[int, int] = (8, 4)
    _SECTION_PADY: int | tuple[int, int] = 8
    _SECTION_GAP: int = 16
    _ENTRY_GAP: int = 8
    _ENTRY_PADDING: tuple[int, int] = (12, 8)
    _ENTRY_INNER_GAP: int = 4

    _FRAME_WIDTH: int = THUMBNAIL_SIZE + 2 * _ENTRY_PADDING[0]


    def __init__(self, master):
        super().__init__(master, transparent=False, round=True, border=True, layer=1)
        self.root = master
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


    def clear(self) -> None:
        for widget in self.winfo_children():
            try: widget.destroy()
            except TclError: pass
        self.loaded = False


    def refresh(self) -> None:
        self.clear()
        self.show()


    def show(self) -> None:
        self.load()


# region load
    def load(self) -> None:
        if self.loaded: return

        self._frames = {}
        self.placeholder_thumbnail = (Image.open(Resources.Shortcuts.Light.PLACEHOLDER), Image.open(Resources.Shortcuts.Dark.PLACEHOLDER))

        content: Frame = Frame(self, transparent=True)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)
        content.grid(column=0, row=0, sticky="nsew", padx=self._SECTION_PADX, pady=self._SECTION_PADY)

        self._load_header(content)
        self._load_content(content)

        self.loaded = True


    def _load_header(self, master) -> None:
        header: Frame = Frame(master, transparent=True)
        header.grid_columnconfigure(0, weight=1)
        header.grid(column=0, row=0, sticky="nsew", pady=(0,16))

        Label(header, "menu.shortcuts.header.title", style="title", autowrap=True).grid(column=0, row=0, sticky="ew")
        Label(header, "menu.shortcuts.header.description", lambda string: Localizer.format(string, {"{app.name}": ProjectData.NAME}), style="caption", autowrap=True).grid(column=0, row=1, sticky="ew")

        button_wrapper: Frame = Frame(header, transparent=True)
        button_wrapper.grid(column=0, row=2, sticky="w", pady=(8, 0))

        add_image: CTkImage = get_ctk_image(Resources.Common.Light.ADD, Resources.Common.Dark.ADD, size=24)
        Button(button_wrapper, "menu.shortcuts.header.button.add_new", secondary=True, image=add_image, command=self.add_new_shortcut).grid(column=0, row=0)


    def _load_content(self, master) -> None:
        self.shortcuts_wrapper: Frame = Frame(master, transparent=True)
        self.shortcuts_wrapper.bind("<Configure>", self._on_configure)

        self._update_frames()


    def _update_frames(self) -> None:
        shortcut_ids: list[str] = ShortcutsInterface.get_all()
        if not shortcut_ids:
            for shortcut_id, frame in list(self._frames.items()):
                self._frames.pop(shortcut_id)
                frame.destroy()
            if self.shortcuts_wrapper.winfo_ismapped():
                self.shortcuts_wrapper.grid_forget()
            return
        elif not self.shortcuts_wrapper.winfo_ismapped():
            self.shortcuts_wrapper.grid(column=0, row=1, sticky="nsew")


        self.update_idletasks()
        total_width: int = int(self.shortcuts_wrapper.winfo_width() / ScalingTracker.get_widget_scaling(self))
        column_width: int = self._FRAME_WIDTH
        gap: int = self._ENTRY_GAP

        columns: int = max(1, (total_width + gap) // (column_width + gap))
        self.shortcuts_wrapper.grid_columnconfigure(list(range(columns)), minsize=column_width+gap)
        self.shortcuts_wrapper.grid_columnconfigure(0, minsize=column_width)

        for shortcut_id, frame in list(self._frames.items()):
            if shortcut_id not in shortcut_ids:
                self._frames.pop(shortcut_id)
                frame.destroy()

        for i, shortcut_id in enumerate(shortcut_ids):
            column: int = i % columns
            row: int = i // columns

            padx = 0 if column == 0 else (self._ENTRY_GAP, 0)
            pady = 0 if row == 0 else (self._ENTRY_GAP, 0)

            if shortcut_id in self._frames:
                frame = self._frames[shortcut_id]
                if getattr(frame, "column", None) != column or getattr(frame, "row", None) != row:
                    frame.grid(column=column, row=row, sticky="nw", padx=padx, pady=pady)
                    frame._column = column  # type: ignore
                    frame._row = row  # type: ignore

            else:
                frame = Frame(self.shortcuts_wrapper, layer=2)
                frame._column = column  # type: ignore
                frame._row = row  # type: ignore
                frame.grid(column=column, row=row, sticky="nw", padx=padx, pady=pady)
                self._frames[shortcut_id] = frame
                Thread(target=self.load_shortcut_frame_async, args=(frame, shortcut_id), daemon=True).start()


# region frame
    def load_shortcut_frame_async(self, frame: Frame, shortcut_id: str) -> None:
        def load_content_sync(frame: Frame, shortcut: Shortcut, thumbnail: CTkImage) -> None:
            wrapper: Frame = Frame(frame, transparent=True)
            wrapper.grid(column=0, row=0, sticky="nsew", padx=self._ENTRY_PADDING[0], pady=self._ENTRY_PADDING[1])

            Label(wrapper, image=thumbnail, width=self.THUMBNAIL_SIZE, height=self.THUMBNAIL_SIZE).grid(column=0, row=0)
            Label(wrapper, shortcut.name, style="body_strong", autowrap=False, dont_localize=True, wraplength=self.THUMBNAIL_SIZE, width=self.THUMBNAIL_SIZE).grid(column=0, row=1, pady=(self._ENTRY_INNER_GAP, 0))
            Label(wrapper, "menu.shortcuts.content.creator", lambda string: Localizer.format(string, {"{creator}": shortcut.creator}), style="caption", autowrap=False, wraplength=self.THUMBNAIL_SIZE, width=self.THUMBNAIL_SIZE).grid(column=0, row=2)
            play_image = get_ctk_image(Resources.Common.Light.START, Resources.Common.Dark.START, 24)
            Button(wrapper, image=play_image, width=self.THUMBNAIL_SIZE, command=lambda shortcut=shortcut: self.launch_game(shortcut.place_id)).grid(column=0, row=3, pady=(self._ENTRY_INNER_GAP, 0))

            bin_image = get_ctk_image(Resources.Common.Light.BIN, Resources.Common.Dark.BIN, 24)
            Button(wrapper, secondary=True, image=bin_image, width=32, command=lambda shortcut=shortcut: self.remove_shortcut(shortcut.universe_id), corner_radius=0).grid(column=0, row=0, sticky="ne")

        shortcut: Shortcut = Shortcut(shortcut_id, self.placeholder_thumbnail)
        thumbnail: Image.Image | tuple[Image.Image, Image.Image] = shortcut.get_thumbnail()
        thumbnail_ctk = get_ctk_image(thumbnail[0], thumbnail[1], size=self.THUMBNAIL_SIZE) if isinstance(thumbnail, tuple) else get_ctk_image(thumbnail, size=self.THUMBNAIL_SIZE)
        self.after(10, load_content_sync, frame, shortcut, thumbnail_ctk)
# endregion
# endregion


# region functions
    def _on_configure(self, _) -> None:
        if self._update_id is not None: self.after_cancel(self._update_id)
        self._update_id = self.after(self._debounce, self._update_frames)


    def add_new_shortcut(self) -> None:
        dialog: InputDialog = InputDialog(ProjectData.NAME, Resources.FAVICON, "menu.shortcuts.input.new_shortcuts.message", master=self.root)
        place_id: str = dialog.get_input()

        if not place_id:
            return
        place_id = place_id.strip()

        if not place_id.isdigit():
            self.root.send_banner(
                title_key="menu.shortcuts.exception.title.failed_to_add",
                message_key="menu.shortcuts.exception.message.invalid_place_id",
                message_modification=lambda string: Localizer.format(string, {"{place_id}": place_id}),
                mode="warning", auto_close_after_ms=6000
            )
            return

        try:
            response: Response = requests.get(Api.Roblox.Activity.universe_id(place_id))
            data: dict = response.json()
            universe_id: int | None = data["universeId"]
        except (RequestException, RuntimeError):
            self.root.send_banner(
                title_key="menu.shortcuts.exception.title.failed_to_add",
                message_key="menu.shortcuts.exception.message.connection_error",
                mode="error", auto_close_after_ms=6000
            )
            return
        if universe_id is None:
            self.root.send_banner(
                title_key="menu.shortcuts.exception.title.failed_to_add",
                message_key="menu.shortcuts.exception.message.universe_not_found",
                message_modification=lambda string: Localizer.format(string, {"{place_id}": place_id}),
                mode="warning", auto_close_after_ms=6000
            )
            return

        ShortcutsInterface.add(str(universe_id))
        self._update_frames()


    def remove_shortcut(self, universe_id: str) -> None:
        ShortcutsInterface.remove(universe_id)
        self._update_frames()


    def launch_game(self, place_id: str) -> None:
        Logger.info(f"Launching shortcut (placeid={place_id})...")
        try:
            deeplink = rf"roblox://experiences/start?placeId={place_id}"
            # webbrowser.open_new_tab(deeplink)

            # Required to prevent PyInstaller from reusing the same temporary directory
            import os
            import subprocess

            env = os.environ.copy()
            env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
            subprocess.Popen(
                ["cmd", "/c", "start", "", deeplink],
                env=env,
                close_fds=True,
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
            )

        except Exception as e:
            Logger.error(f"Failed to launch shortcut! {type(e).__name__}: {e}")
            self.root.send_banner(
                title_key="menu.shortcuts.exception.title.failed_to_launch",
                message_key="menu.shortcuts.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                mode="error", auto_close_after_ms=6000
            )
# endregion