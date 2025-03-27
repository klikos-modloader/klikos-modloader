from pathlib import Path

from ..toplevel import FluentToplevel
from ..button import FluentButton
from ..textbox import FluentTextBox
from ..label import FluentLabel
from ..frame import FluentFrame

import customtkinter as ctk  # type: ignore


class Assets:
    DIRECTORY: Path = Path(__file__).parent / "assets"
    DEFAULT_LOGO: Path = DIRECTORY / "logo-default.ico"


class FluentInputDialog(FluentToplevel):
    padding: int = 25
    width: int = 280

    _user_input: str | None = None
    _running: bool
    _text: str
    _ok_text: str
    _cancel_text: str
    _entry: FluentTextBox

    button_frame: FluentFrame

    _window_start_x: int = 0
    _window_start_y: int = 0


    def __init__(self, root: ctk.CTk, title: str = "FluentInputDialog", icon: Path = Assets.DEFAULT_LOGO, text: str = "FluentInputDialog", ok_text: str = "OK", cancel_text: str = "Cancel") -> None:

        super().__init__(root, title=title, icon=icon)
        self.configure(fg_color=("#F9F9F9", "#272727"))

        self._user_input = None
        self._running = False
        self._text = text
        self._ok_text = ok_text
        self._cancel_text = cancel_text

        self.lift()
        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.after(10, self._create_widgets)
        self.resizable(False, False)
        self.grab_set()

        self._set_geometry()


    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        content_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        content_frame.grid(column=0, row=0, sticky="nsew", padx=self.padding, pady=(self.padding-2, self.padding))
        content_frame.grid_columnconfigure(1, weight=1)

        FluentLabel(content_frame, self._text, wraplength=230, justify="left", font_size=16).grid(column=0, row=0, sticky="w")
        self._entry = FluentTextBox(content_frame, width=230)
        self._entry.grid(column=0, row=1, sticky="w", pady=(self.padding//2, 0))

        self.button_frame = FluentFrame(self, rounded=False, border=False)
        self.button_frame.grid(column=0, row=1, sticky="sew")
        self.button_frame.grid_columnconfigure(0, weight=1)

        button_outer_padding = int(self.padding/1.5)
        button_gap = 8

        FluentButton(self.button_frame, text=self._ok_text, width=78, command=self._ok_event).grid(column=0, row=0, sticky="e", padx=(button_outer_padding, button_gap//2), pady=button_outer_padding)
        FluentButton(self.button_frame, text=self._cancel_text, width=78, command=self._cancel_event).grid(column=1, row=0, sticky="e", padx=(button_gap//2, button_outer_padding), pady=button_outer_padding)

        self.after(100, self._entry.entry.focus)
        self._entry.entry.bind("<Return>", self._ok_event)


    def _ok_event(self,*_, **__):
        self._user_input = self._entry.get()
        self.grab_release()
        self.destroy()


    def _on_closing(self):
        self.grab_release()
        self.destroy()


    def _cancel_event(self):
        self.grab_release()
        self.destroy()


    def get_input(self):
        self.master.wait_window(self)
        return self._user_input


    def _set_geometry(self) -> None:
        self.update_idletasks()
        w = max(self.width, self.winfo_reqwidth())
        h = self.winfo_reqheight()
        x = self.root.winfo_x() + (self.root.winfo_width()-w)//2
        y = self.root.winfo_y() + (self.root.winfo_height()-h)//2
        self.geometry(f"{w}x{h}+{x}+{y}")