import traceback
import sys
import shutil
from tkinter.messagebox import showerror
from pathlib import Path

from modules.logger import Logger
from modules.localization import Localizer
from modules.project_data import ProjectData
from modules.filesystem import Directories, Files


def run(exception: Exception) -> None:
    formatted_traceback: str = "\n".join(traceback.format_exception(exception))

    Logger.critical(f"\n\n{formatted_traceback}")
    try: log_string: str = Localizer.format(Localizer.Strings["fatalerror.log"], {"{discord}": ProjectData.DISCORD})
    except Exception: log_string = f"If you need any help, please join the official support server: {ProjectData.DISCORD}"
    Logger.debug(log_string)

    crash_dir: Path = Directories.CRASHES / Logger.filepath.stem
    crash_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(Logger.filepath, crash_dir)
    try: shutil.copy(Files.CONFIG, crash_dir)
    except FileNotFoundError: pass
    try: shutil.copy(Files.DATA, crash_dir)
    except FileNotFoundError: pass

    if getattr(sys, "frozen", False):
        try:
            import pyi_splash  # type: ignore
            if pyi_splash.is_alive():
                pyi_splash.close()
        except (ModuleNotFoundError, ImportError):
            pass

    exception_type: str = f"{type(exception).__module__}.{type(exception).__qualname__}"
    exception_message: str = str(exception)
    try: user_string: str = Localizer.format(Localizer.Strings["fatalerror.message"], {"{app.name}": ProjectData.NAME, "{exception.type}": exception_type, "{exception.message}": exception_message})
    except Exception: user_string = f"{ProjectData.NAME} crashed due to a fatal error!\n\n{exception_type}: {exception_message}\n\nMore information may be available in the latest log file"
    showerror(title=f"{ProjectData.NAME} ({ProjectData.VERSION})", message=user_string)