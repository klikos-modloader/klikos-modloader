import os
import sys
import traceback
import shutil
from pathlib import Path

from modules.logger import Logger
from modules.localization.localizer import Localizer
from modules.filesystem import Directory, open
from modules.frontend.widgets.fluent import messagebox


def run(e: Exception) -> None:
    formatted_traceback: str = "\n".join(traceback.format_exception(e))

    Logger.critical(formatted_traceback)

    directory: Path = Directory.CRASHES
    directory.mkdir(parents=True, exist_ok=True)

    shutil.copy(Logger.filepath, directory)

    display_header: str = Localizer.strings["errors"]["global"]["critical.title"]
    display_traceback: str = f"{type(e).__name__}: {e}"
    display_note: str = Localizer.strings["errors"]["global"]["critical.message"]

    display_message: str = f"{display_traceback}\n\n{display_note}"

    messagebox.show_error(title=display_header, message=display_message, additional_buttons=({"text": Localizer.strings["buttons.open_crash_log"], "command": lambda: _open_crash_log(directory, Logger.filename)},))

    _exit()


def _open_crash_log(directory: Path, file: str) -> None:
    os.startfile(directory / file)
    # open(directory)


def _exit() -> None:
    sys.exit(1)
