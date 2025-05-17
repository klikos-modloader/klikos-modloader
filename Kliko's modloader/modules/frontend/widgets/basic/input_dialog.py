# Original: https://github.com/TomSchimansky/CustomTkinter/blob/master/customtkinter/windows/ctk_input_dialog.py
# 
# MIT License
# 
# Copyright (c) 2023 Tom Schimansky
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from typing import Union, Optional, Callable
from pathlib import Path

from .label import Label
from .entry import Entry
from .button import Button
from .toplevel import Toplevel

from customtkinter import ScalingTracker  # type: ignore


class InputDialog(Toplevel):
    """
    Dialog with extra window, message, entry widget, cancel and ok button.
    For detailed information check out the documentation.
    """

    def __init__(
            self,
            title: str,
            icon: Optional[str | Path] = None,
            message_key: Optional[str] = None,
            message_modification: Optional[Callable[[str], str]] = None,
            master = None
        ):

        super().__init__(title=title, icon=icon, master=master)

        self._message_key: Optional[str] = message_key
        self._message_modification: Optional[Callable[[str], str]] = message_modification
        self._user_input: Union[str, None] = None
        self._running: bool = False
        self.root = master

        self.lift()  # lift window on top
        self.attributes("-topmost", True)  # stay on top
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.after(10, self._create_widgets)  # create widgets with slight delay, to avoid white flickering of background
        self.resizable(False, False)

        self.grab_set()  # make other windows not clickable

    def _create_widgets(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        self._label = Label(
            self,
            self._message_key,
            self._message_modification,
            width=300,
            wraplength=300
        )
        self._label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self._entry = Entry(
            self,
            width=230
        )
        self._entry.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")

        self._ok_button = Button(
            self,
            "button.ok",
            command=self._ok_event
        )
        self._ok_button.grid(row=2, column=0, columnspan=1, padx=(20, 10), pady=(0, 20), sticky="ew")

        self._cancel_button = Button(
            self,
            "button.cancel",
            secondary=True,
            command=self._cancel_event
        )
        self._cancel_button.grid(row=2, column=1, columnspan=1, padx=(10, 20), pady=(0, 20), sticky="ew")

        self.after(150, lambda: self._entry.focus())  # set focus to entry with slight delay, otherwise it won't work
        self._entry.bind("<Return>", self._ok_event)

        self.update_idletasks()
        if not self.root:
            scaling = ScalingTracker.get_window_scaling(self)
            width = int(self.winfo_reqwidth() / scaling)
            height = int(self.winfo_reqheight() / scaling)
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            self.geometry(f"{width}x{height}+{(screen_width - width)//2}+{(screen_height - height)//2}")

        else:
            root_scaling = ScalingTracker.get_window_scaling(self.root)
            self_scaling = ScalingTracker.get_window_scaling(self)
            root_x = self.root.winfo_rootx()
            root_y = self.root.winfo_rooty()
            root_w = int(self.root.winfo_width() / root_scaling)
            root_h = int(self.root.winfo_height() / root_scaling)
            width = int(self.winfo_reqwidth() / self_scaling)
            height = int(self.winfo_reqheight() / self_scaling)
            self.geometry(f"{width}x{height}+{root_x + int((root_w - width) / 2)}+{root_y + int((root_h - height) / 2)}")

    def _ok_event(self, event=None):
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