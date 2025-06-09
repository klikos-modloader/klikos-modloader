from tkinter import TclError
from threading import Thread
from typing import TYPE_CHECKING

from modules.logger import Logger
from modules.project_data import ProjectData
from modules.frontend.widgets import ScrollableFrame, Frame, Label, Button
from modules.frontend.functions import get_ctk_image
from modules.frontend.menu.dataclasses import Shortcut
from modules.localization import Localizer
from modules.filesystem import Resources

if TYPE_CHECKING: from modules.frontend.widgets import Root

from PIL import Image  # type: ignore
from customtkinter import CTkImage  # type: ignore


class ShortcutsSection(ScrollableFrame):
    loaded: bool = False
    root: "Root"

    placeholder_thumbnail: tuple[Image.Image, Image.Image]
    THUMBNAIL_SIZE: int = 144

    _SECTION_PADX: int | tuple[int, int] = (8, 4)
    _SECTION_PADY: int | tuple[int, int] = 8

    _SECTION_GAP: int = 16
    _ENTRY_GAP: int = 8
    _ENTRY_PADDING: tuple[int, int] = (12, 8)
    _ENTRY_INNER_GAP: int = 4


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

        self.placeholder_thumbnail = (Image.open(Resources.Shortcuts.Light.PLACEHOLDER), Image.open(Resources.Shortcuts.Dark.PLACEHOLDER))

        content: Frame = Frame(self, transparent=True)
        content.grid_columnconfigure(0, weight=1)
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
        wrapper: Frame = Frame(master, transparent=True)
        wrapper.grid_columnconfigure(0, weight=1)
        wrapper.grid_rowconfigure(1, weight=1)
        wrapper.grid(column=0, row=1, sticky="nsew")

        frame = Frame(wrapper, layer=2)
        frame.grid(column=0, row=0, sticky="nw")
        Thread(target=self.load_shortcut_frame_async, args=(frame, Shortcut("740581508", self.placeholder_thumbnail)), daemon=True).start()


# region frame
    def load_shortcut_frame_async(self, frame: Frame, shortcut: Shortcut) -> None:
        def load_content_sync(frame: Frame, shortcut: Shortcut, thumbnail: CTkImage) -> None:
            wrapper: Frame = Frame(frame, transparent=True)
            wrapper.grid(column=0, row=0, sticky="nsew", padx=self._ENTRY_PADDING[0], pady=self._ENTRY_PADDING[1])

            Label(wrapper, image=thumbnail, width=self.THUMBNAIL_SIZE, height=self.THUMBNAIL_SIZE).grid(column=0, row=0)
            Label(wrapper, shortcut.name, style="body_strong", autowrap=False, dont_localize=True, wraplength=self.THUMBNAIL_SIZE, width=self.THUMBNAIL_SIZE).grid(column=0, row=1, pady=(self._ENTRY_INNER_GAP, 0))
            Label(wrapper, "menu.shortcuts.content.creator", lambda string: Localizer.format(string, {"{creator}": shortcut.creator}), style="caption", autowrap=False, wraplength=self.THUMBNAIL_SIZE, width=self.THUMBNAIL_SIZE).grid(column=0, row=2)
            play_image = get_ctk_image(Resources.Common.Light.START, Resources.Common.Dark.START, 24)
            Button(wrapper, image=play_image, width=self.THUMBNAIL_SIZE, command=lambda shortcut=shortcut: self.launch_game(shortcut.place_id)).grid(column=0, row=3, pady=(self._ENTRY_INNER_GAP, 0))

        thumbnail: Image.Image | tuple[Image.Image, Image.Image] = shortcut.get_thumbnail()
        thumbnail_ctk = get_ctk_image(thumbnail[0], thumbnail[1], size=self.THUMBNAIL_SIZE) if isinstance(thumbnail, tuple) else get_ctk_image(thumbnail, size=self.THUMBNAIL_SIZE)
        self.after(10, load_content_sync, frame, shortcut, thumbnail_ctk)
# endregion
# endregion


# region functions
    def add_new_shortcut(self) -> None:
        shortcut: Shortcut = Shortcut("740581508", self.placeholder_thumbnail)
        print(shortcut.place_id, shortcut.name, shortcut.creator)
        thumbnail: Image.Image | tuple[Image.Image, Image.Image] = shortcut.get_thumbnail()
        if isinstance(thumbnail, tuple): thumbnail = thumbnail[1]
        thumbnail.show()

        import os
        import time
        time.sleep(5)
        os.system("TASKKILL /F /IM photos.exe")
        # self.launch_game("740581508")


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