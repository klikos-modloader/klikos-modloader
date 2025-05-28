from pathlib import Path
from typing import Literal, TYPE_CHECKING
from tkinter import messagebox, filedialog
import json

from modules.project_data import ProjectData
from modules.localization import Localizer
from modules.filesystem import Resources, Directories
from modules.frontend.widgets import Toplevel, Frame, Label, Button, Textbox
if TYPE_CHECKING: from modules.frontend.widgets import Root
from modules.frontend.functions import get_ctk_image
from modules.interfaces.fastflag_manager import FastFlagProfile

import pyperclip  # type: ignore
from customtkinter import CTkImage, ScalingTracker  # type: ignore


class FastFlagEditorWindow(Toplevel):
    root: "Root"
    profile: FastFlagProfile
    profile_name_label: Label
    data_textbox: Textbox

    _localizer_callback_id: str | None = None
    _profile_name: str

    PADDING: tuple[int, int] = (16, 16)
    TEXTBOX_HEIGHT: int = 256
    WINDOW_MIN_WIDTH: int = 512

    _LOG_PREFIX: str = "FastFlagEditor"
    _BACKGROUND_TASK_INTERVAL: int = 1000  # ms


    def __init__(self, master: "Root", profile: FastFlagProfile):
        window_title: str = Localizer.format(Localizer.Strings["menu.fastflags.fastflag_editor.window_title"], {"{app.name}": ProjectData.NAME})
        super().__init__(window_title, icon=Resources.FAVICON, centered=False, hidden=True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(9, weight=1)
        self.resizable(False, False)
        self.root = master
        self.profile = profile
        self._profile_name = self.profile.name

        content: Frame = Frame(self, transparent=True)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)
        content.grid(column=0, row=0, sticky="nsew", padx=self.PADDING[0], pady=self.PADDING[1])
        self.load_content(content)

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
        self._localizer_callback_id = Localizer.add_callback(self._on_language_change)
        self.after(self._BACKGROUND_TASK_INTERVAL, self._run_background_tasks)


    def destroy(self):
        if self._localizer_callback_id is not None: Localizer.remove_callback(self._localizer_callback_id)
        return super().destroy()


    def center_window(self) -> None:
        self.update_idletasks()
        self_scaling: float = ScalingTracker.get_window_scaling(self)
        # width: int = int(self.winfo_reqwidth() / self_scaling)
        width: int = max(int(self.winfo_reqwidth() / self_scaling), int(self.WINDOW_MIN_WIDTH / self_scaling))
        height: int = int(self.winfo_reqheight() / self_scaling)
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
        # width: int = int(self.winfo_reqwidth() / self_scaling)
        width: int = max(int(self.winfo_reqwidth() / self_scaling), int(self.WINDOW_MIN_WIDTH / self_scaling))
        height: int = int(self.winfo_reqheight() / self_scaling)

        self.geometry(f"{width}x{height}+{root_x + int((root_w - width) / 2)}+{root_y + int((root_h - height) / 2)}")


    def _on_scaling_change(self, widget_scaling: float, window_scaling: float) -> None:
        self.update_idletasks()
        # width: int = int(self.winfo_reqwidth() / window_scaling)
        width: int = max(int(self.winfo_reqwidth() / window_scaling), int(self.WINDOW_MIN_WIDTH / window_scaling))
        height: int = int(self.winfo_reqheight() / window_scaling)
        self.geometry(f"{width}x{height}")


    def _on_language_change(self) -> None:
        self.update_idletasks()
        self_scaling: float = ScalingTracker.get_window_scaling(self)
        # width: int = int(self.winfo_reqwidth() / self_scaling)
        width: int = max(int(self.winfo_reqwidth() / self_scaling), int(self.WINDOW_MIN_WIDTH / self_scaling))
        height: int = int(self.winfo_reqheight() / self_scaling)
        self.geometry(f"{width}x{height}")


    def load_content(self, frame: Frame) -> None:
        # Header
        header: Frame = Frame(frame, transparent=True)
        header.grid_columnconfigure(0, weight=1)
        header.grid(column=0, row=0, sticky="nsew")

        self.profile_name_label = Label(header, self.profile.name, style="subtitle", autowrap=True, dont_localize=True)
        self.profile_name_label.grid(column=0, row=0, sticky="ew")

        button_wrapper: Frame = Frame(header, transparent=True)
        button_wrapper.grid(column=0, row=1, sticky="w", pady=(8, 0))

        import_image: CTkImage = get_ctk_image(Resources.Common.Light.DOWNLOAD, Resources.Common.Dark.DOWNLOAD, size=24)
        export_image: CTkImage = get_ctk_image(Resources.Common.Light.UPLOAD, Resources.Common.Dark.UPLOAD, size=24)
        copy_image: CTkImage = get_ctk_image(Resources.Common.Light.COPY, Resources.Common.Dark.COPY, size=24)
        Button(button_wrapper, "menu.fastflags.fastflag_editor.button.import", secondary=True, image=import_image, command=self._import_data).grid(column=0, row=0)
        Button(button_wrapper, "menu.fastflags.fastflag_editor.button.export", secondary=True, image=export_image, command=self._export_data).grid(column=1, row=0, padx=(8, 0))
        Button(button_wrapper, "menu.fastflags.fastflag_editor.button.copy_to_clipboard", secondary=True, image=copy_image, command=self._copy_data).grid(column=2, row=0, padx=(8, 0))

        # Body
        body: Frame = Frame(frame, transparent=True)
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=1)
        body.grid(column=0, row=1, sticky="nsew", pady=(12, 0))

        self.data_textbox = Textbox(body, command=self._save_data, on_focus_lost="command", run_command_if_empty=False, reset_if_empty=True, height=self.TEXTBOX_HEIGHT)
        data_string: str = json.dumps(self.profile.data, indent=4)
        self.data_textbox.set(data_string)
        self.data_textbox.grid(column=0, row=0, sticky="ew")


# region functions
    def _run_background_tasks(self) -> None:
        if not self.winfo_exists():
            return
        
        profile_name: str = self.profile.name
        if self._profile_name != profile_name:
            self._profile_name = profile_name
            self.profile_name_label.configure(key=profile_name)
        self.after(self._BACKGROUND_TASK_INTERVAL, self._run_background_tasks)


    def _save_data(self, event) -> None:
        textbox_string = event.value
        try:
            textbox_data: dict = json.loads(textbox_string)
            self.profile.set_data(textbox_data)

        except Exception as e:
            messagebox.showwarning(
                title=f"{ProjectData.NAME} ({ProjectData.VERSION})",
                message=Localizer.format(
                    Localizer.Strings["menu.fastflags.fastflag_editor.exception.message.save"],
                    {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}
                )
            )
            self.focus()
            self.lift(aboveThis=self.root)


    def _import_data(self) -> None:
        filepath: str | Literal[''] = filedialog.askopenfilename(
            initialdir=str(Directories.DOWNLOADS),
            filetypes=(
                (Localizer.Strings["menu.fastflags.fastflag_editor.popup.import.filetype.supported"], "*.txt;*.json"),
            ), title=Localizer.format(Localizer.Strings["menu.fastflags.fastflag_editor.popup.import.title"], {"{app.name}": ProjectData.NAME})
        )
        if not filepath:
            return
        path: Path = Path(filepath)

        try:
            with open(path) as file:
                data: dict = json.load(file)
            self.profile.set_data(data)
            data_string: str = json.dumps(data, indent=4)
            self.data_textbox.set(data_string)

        except Exception as e:
            messagebox.showwarning(
                title=f"{ProjectData.NAME} ({ProjectData.VERSION})",
                message=Localizer.format(
                    Localizer.Strings["menu.fastflags.fastflag_editor.exception.message.save"],
                    {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}
                )
            )
            self.focus()
            self.lift(aboveThis=self.root)


    def _export_data(self) -> None:
        filepath: str | Literal[''] = filedialog.asksaveasfilename(
            initialdir=str(Directories.DOWNLOADS),
            initialfile="ClientAppSettings.json",
            filetypes=(
                (Localizer.Strings["menu.fastflags.fastflag_editor.popup.export.filetype.supported"], "*.txt;*.json"),
            ), title=Localizer.format(Localizer.Strings["menu.fastflags.fastflag_editor.popup.export.title"], {"{app.name}": ProjectData.NAME})
        )
        if not filepath:
            return
        path: Path = Path(filepath)

        try:
            data: dict = self.profile.data
            with open(path, "w") as file:
                json.dump(data, file, indent=4)

        except Exception as e:
            messagebox.showwarning(
                title=f"{ProjectData.NAME} ({ProjectData.VERSION})",
                message=Localizer.format(
                    Localizer.Strings["menu.fastflags.fastflag_editor.exception.message.save"],
                    {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}
                )
            )
            self.focus()
            self.lift(aboveThis=self.root)


    def _copy_data(self) -> None:
        data: dict = self.profile.data
        data_string: str = json.dumps(data, indent=4)
        pyperclip.copy(data_string)
# endregion