import platform
from pathlib import Path
from typing import Literal, Iterable, Callable
from threading import Event
from tkinter import Button as tk_button, TclError

from ..button import FluentButton
from ..ctk_root_storage import get_root_instance

from PIL import Image  # type: ignore
import customtkinter as ctk  # type: ignore


class Colors:
    class Dark:
        class BackgroundColor:
            hex: str = "#2B2B2B"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundFooterColor:
            hex: str = "#202020"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderColor:
            hex: str = "#3B3B3B"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextColor:
            hex: str = "#FFFFFF"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
    
    class Light:
        class BackgroundColor:
            hex: str = "#FFFFFF"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BackgroundFooterColor:
            hex: str = "#F3F3F3"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class BorderColor:
            hex: str = "#3E3E3E"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)
        class TextColor:
            hex: str = "#1B1B1B"
            r: int = int(hex[1:3], 16)
            g: int = int(hex[3:5], 16)
            b: int = int(hex[5:7], 16)


class Assets:
    DIRECTORY: Path = Path(__file__).parent / "assets"
    ERROR: Path = DIRECTORY / "fluent-error.png"
    WARNING: Path = DIRECTORY / "fluent-warning.png"
    QUESTION: Path = DIRECTORY / "fluent-question.png"
    ERROR_ICO: Path = DIRECTORY / "fluent-error.ico"
    WARNING_ICO: Path = DIRECTORY / "fluent-warning.ico"
    QUESTION_ICO: Path = DIRECTORY / "fluent-question.ico"

class FluentMessageBox(ctk.CTkToplevel):
    root: ctk.CTk
    button_frame: ctk.CTkFrame
    uses_temp_root: bool = False
    event: Event
    value: None | bool = None
    
    corner_radius: int = 8
    padding: int = 25
    width: int = 320
    button_gap: int = 8

    _window_start_x: int = 0
    _window_start_y: int = 0


    class Modes:
        ERROR: Literal["error"] = "error"
        WARNING: Literal["warning"] = "warning"
        QUESTION: Literal["question"] = "question"

    def __init__(self, title: str | None = None, message: str | None = None, mode: Literal["error", "warning", "question"] | None = None, additional_buttons: Iterable[dict] = tuple(), _on_ok: Callable | None = None, _on_cancel: Callable | None = None) -> None:
        if not title and not message:
            raise ValueError("FluentMessageBox: A title or a message is required!")
        
        root = get_root_instance()
        if root is None:
            root = ctk.CTk(fg_color=(Colors.Light.BackgroundColor.hex, Colors.Dark.BackgroundColor.hex))
            self.uses_temp_root = True
        self.root = root

        if self.uses_temp_root:
            self.root.title(title)
            self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)

            if mode == "error": self.root.iconbitmap(Assets.ERROR_ICO.resolve())
            elif mode == "warning": self.root.iconbitmap(Assets.WARNING_ICO.resolve())
            elif mode == "question": self.root.iconbitmap(Assets.QUESTION_ICO.resolve())

            self.event = Event()
            self.root.grid_columnconfigure(0, weight=1)
            self.root.grid_rowconfigure(0, weight=1)
            
            self.root.bind("<Button-1>", self._raise_window)
            self.root.bind("<Map>", self._raise_window)

            self.root.resizable(False, False)
            self.root.overrideredirect(True)
            
            self.root.bind("<ButtonPress-1>", self._start_window_movement)
            self.root.bind("<B1-Motion>", self._do_window_movement)

        else:
            super().__init__(self.root, fg_color=(Colors.Light.BackgroundColor.hex, Colors.Dark.BackgroundColor.hex))
            self.title(title)
            self.protocol("WM_DELETE_WINDOW", self._on_cancel)

            if mode == "error": self.iconbitmap(Assets.ERROR_ICO.resolve())
            elif mode == "warning": self.iconbitmap(Assets.WARNING_ICO.resolve())
            elif mode == "question": self.iconbitmap(Assets.QUESTION_ICO.resolve())

            self.event = Event()
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)

            self.resizable(False, False)
            self.overrideredirect(True)
            
            self.bind("<ButtonPress-1>", self._start_window_movement)
            self.bind("<B1-Motion>", self._do_window_movement)

        self._apply_rounded_corners()
        self._restore_taskbar_icon()
        self._set_geometry()


        if self.uses_temp_root: content_frame: ctk.CTkFrame = ctk.CTkFrame(self.root, fg_color="transparent", corner_radius=0)
        else: content_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        content_frame.grid(column=0, row=0, sticky="nsew", padx=self.padding, pady=(self.padding-2, self.padding))
        content_frame.grid_columnconfigure(1, weight=1)

        if mode is not None:
            image: ctk.CTkImage = self._get_image(mode)
            image_label: ctk.CTkLabel = ctk.CTkLabel(content_frame, text="", fg_color="transparent", image=image)
            image_label.grid(column=0, row=0, padx=(0, 12), rowspan=2, sticky="n")

        if title:
            title_label: ctk.CTkLabel = ctk.CTkLabel(content_frame, text=title, fg_color="transparent", wraplength=350, text_color=(Colors.Light.TextColor.hex, Colors.Dark.TextColor.hex), font=ctk.CTkFont(family="Segoe UI", weight="bold", size=20), justify="left", anchor="w")
            title_label.grid(column=1, row=0, sticky="w")
        if message:
            message_label: ctk.CTkLabel = ctk.CTkLabel(content_frame, text=message, fg_color="transparent", wraplength=350, text_color=(Colors.Light.TextColor.hex, Colors.Dark.TextColor.hex), font=ctk.CTkFont(family="Segoe UI"), justify="left", anchor="w")
            message_label.grid(column=1, row=1, sticky="w", pady=(8, 0), columnspan=2)


        if self.uses_temp_root: self.button_frame: ctk.CTkFrame = ctk.CTkFrame(self.root, fg_color=(Colors.Light.BackgroundFooterColor.hex, Colors.Dark.BackgroundFooterColor.hex), corner_radius=0)
        else: self.button_frame: ctk.CTkFrame = ctk.CTkFrame(self, fg_color=(Colors.Light.BackgroundFooterColor.hex, Colors.Dark.BackgroundFooterColor.hex), corner_radius=0)
        self.button_frame.grid(column=0, row=1, sticky="sew")
        self.button_frame.grid_columnconfigure(0, weight=1)

        button_outer_padding: int = int(self.padding/1.5)
        button_gap: int = 8
        i: int = 0
        for entry in additional_buttons:
            text: str = entry.get("text", "")
            width: int | None = entry.get("width")
            command: Callable | None = entry.get("command", None)
            threaded: bool = entry.get("threaded", False)
            disabled: bool = entry.get("disabled", False)

            FluentButton(self.button_frame, text=text, width=width, command=command, threaded=threaded, disabled=disabled).grid(column=i, row=0, sticky="e", padx=(button_outer_padding if i == 0 else button_gap//2, button_gap//2), pady=button_outer_padding)
            i += 1

        if mode == "question":
            button1: FluentButton = FluentButton(self.button_frame, text="Ok", width=78, command=lambda: self._on_ok(_on_ok))
            button1.grid(column=0, row=0, sticky="e", padx=(button_outer_padding if i == 0 else button_gap//2, button_gap//2), pady=button_outer_padding)
            i += 1
            button2: FluentButton = FluentButton(self.button_frame, text="Cancel", width=78, command=lambda: self._on_cancel(_on_cancel))
            button2.grid(column=1, row=0, sticky="e", padx=(button_gap//2, button_outer_padding), pady=button_outer_padding//2)
            i += 1
        else:
            button: FluentButton = FluentButton(self.button_frame, text="Close", width=78, command=self._on_close)
            button.grid(column=1, row=0, sticky="e", padx=(button_outer_padding if i == 0 else button_gap//2, button_outer_padding), pady=button_outer_padding)
            i += 1


        if self.uses_temp_root: self.root.update_idletasks()
        else: self.update_idletasks()
        self._set_geometry()

        if self.uses_temp_root: self.root.mainloop()
        else: self.after(10, self._loop)
    

    def _loop(self) -> None:
        if self.uses_temp_root: return
        if self.root.focus_get() == self.root:
            self.lift()
            self.after(10, self.focus_set)
        self.after(10, self._loop)


    def wait_until_closed(self) -> None | bool:
        while not self.event.is_set():
            continue
        return self.value


    def _raise_window(self, _) -> None:
        if self.uses_temp_root: self.root.lift()
        else: self.lift()
    

    def _on_ok(self, command: Callable | None = None) -> None:
        self.value = True
        self._on_close()
        if callable(command): command()


    def _on_cancel(self, command: Callable | None = None) -> None:
        self.value = False
        self._on_close()
        if callable(command): command()


    def _on_close(self, *_, **__) -> None:
        self.event.set()
        if self.uses_temp_root:
            self.root.destroy()
        else:
            self.grab_release()
            self.withdraw()
            self.destroy()


    def _set_geometry(self) -> None:
        if self.uses_temp_root:
            w: int = max(self.width, self.root.winfo_reqwidth())
            h: int = self.root.winfo_reqheight()
            x: int = self.root.winfo_screenwidth()//2 - w//2
            y: int = self.root.winfo_screenheight()//2 - h//2
            self.root.geometry(f"{w}x{h}+{x}+{y}")
        else:
            w = max(self.width, self.winfo_reqwidth())
            h = self.winfo_reqheight()
            x = self.root.winfo_x() + (self.root.winfo_width()-w)//2
            y = self.root.winfo_y() + (self.root.winfo_height()-h)//2
            self.geometry(f"{w}x{h}+{x}+{y}")


    def _apply_rounded_corners(self) -> None:  # Generated by ChatGPT
        def is_windows_11() -> bool:
            version = platform.version()
            try:
                release = int(platform.release())
                build = int(version.split(".")[2])
            except (IndexError, ValueError):
                return False
            return release == 11 or (build >= 22000 and release < 12)
        if not is_windows_11(): return

        from ctypes import windll, byref, sizeof, c_int
        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        DWMNCRP_ROUND = 2
        if self.uses_temp_root: hwnd = windll.user32.GetParent(self.root.winfo_id())
        else: hwnd = windll.user32.GetParent(self.winfo_id())
        preference = c_int(DWMNCRP_ROUND)
        windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, byref(preference), sizeof(preference))
    

    def _restore_taskbar_icon(self) -> None:  # Generated by ChatGPT
        from ctypes import windll
        GWL_EXSTYLE = -20
        WS_EX_TOOLWINDOW = ~0x00000080
        WS_EX_APPWINDOW = 0x00040000

        SWP_NOSIZE = 0x0001
        SWP_NOMOVE = 0x0002
        SWP_NOZORDER = 0x0004
        SWP_FRAMECHANGED = 0x0020
        SWP_SHOWWINDOW = 0x0040

        if self.uses_temp_root: hwnd = windll.user32.GetParent(self.root.winfo_id())
        else: hwnd = windll.user32.GetParent(self.winfo_id())
        style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style &= WS_EX_TOOLWINDOW
        style |= WS_EX_APPWINDOW
        windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, SWP_NOSIZE | SWP_NOMOVE | SWP_NOZORDER | SWP_FRAMECHANGED | SWP_SHOWWINDOW)


    def _get_image(self, mode: Literal["error", "warning", "question"]) -> ctk.CTkImage:
        image_path: Path = Assets.WARNING
        if mode == "error": image_path = Assets.ERROR
        elif mode == "warning": image_path = Assets.WARNING
        elif mode == "question": image_path = Assets.QUESTION

        image: Image = Image.open(image_path)
        ctk_image: ctk.CTkImage = ctk.CTkImage(light_image=image, size=(48, 48))
        return ctk_image
    

    def _start_window_movement(self, event) -> None:
        if self._should_block_window_movement(event): return
        self._window_start_x = event.x
        self._window_start_y = event.y
    

    def _do_window_movement(self, event) -> None:
        if self._should_block_window_movement(event): return
        if self.uses_temp_root:
            x = self.root.winfo_x() + event.x - self._window_start_x
            y = self.root.winfo_y() + event.y - self._window_start_y
            self.root.geometry(f"+{x}+{y}")
        else:
            x = self.winfo_x() + event.x - self._window_start_x
            y = self.winfo_y() + event.y - self._window_start_y
            self.geometry(f"+{x}+{y}")
    

    def _should_block_window_movement(self, event) -> bool:
        if isinstance(event.widget, tk_button): return True
        if self.root.nametowidget(event.widget.winfo_parent()).winfo_parent() == str(self.button_frame): return True
        return False


def show_error(title: str, message: str, additional_buttons: Iterable[dict] = tuple(), blocking: bool = True) -> None:
    message_box: FluentMessageBox = FluentMessageBox(title=title, message=message, mode="error", additional_buttons=additional_buttons)
    if blocking: message_box.wait_until_closed()


def show_warning(title: str, message: str, additional_buttons: Iterable[dict] = tuple(), blocking: bool = True) -> None:
    message_box: FluentMessageBox = FluentMessageBox(title=title, message=message, mode="warning", additional_buttons=additional_buttons)
    if blocking: message_box.wait_until_closed()


def show_info(title: str, message: str, additional_buttons: Iterable[dict] = tuple(), blocking: bool = True) -> None:
    message_box: FluentMessageBox = FluentMessageBox(title=title, message=message, mode=None, additional_buttons=additional_buttons)
    if blocking: message_box.wait_until_closed()


def ask_ok_cancel(title: str, message: str) -> bool:
    message_box: FluentMessageBox = FluentMessageBox(title=title, message=message, mode="question")
    return message_box.wait_until_closed() or False


def ask_ok_cancel_nonblocking(title: str, message: str, on_ok: Callable | None = None, on_cancel: Callable | None = None) -> None:
    FluentMessageBox(title=title, message=message, mode="question", _on_ok=on_ok, _on_cancel=on_cancel)