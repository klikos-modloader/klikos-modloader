"""
Kliko's modloader - Roblox mods made easy
License: MIT
Source: https://github.com/TheKliko/klikos-modloader
"""

import sys
from pathlib import Path
import platform

# if not getattr(sys, "frozen", False):
#     print("This program must be converted to an executable (.exe)!")
#     print("Please check out the build folder for more information")
#     input("\nPress Enter to exit...")
#     sys.exit(1)

FROZEN: bool = getattr(sys, "frozen", False)
ROOT: Path = Path(sys.executable).parent if FROZEN else Path(__file__).parent
if not FROZEN: sys.path.insert(0, str((ROOT / "libraries").resolve()))
elif hasattr(sys, "_MEIPASS"): sys.path.insert(0, str((Path(sys._MEIPASS) / "libraries").resolve()))

if FROZEN:
    try:
        import pyi_splash  # type: ignore
        if pyi_splash.is_alive(): pyi_splash.close()
    except (ImportError, ModuleNotFoundError): pass

from modules.logger import Logger  # Initializes the logger
from modules import exception_handler
from modules.info import NAME, VERSION
from modules import launch_mode


def main() -> None:
    Logger.debug(f"{NAME} v{VERSION}")
    Logger.debug(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    Logger.debug(f"Platform: {platform.system()} {platform.release()}")
    Logger.debug(f"Mode: {launch_mode.get()} {sys.argv[1:] or ''}")

    try:
        Logger.info("Initializing localization...")
        from modules.localization import Localizer
        Localizer.initialize()

        from modules.core.config_editor import ConfigEditor
        language: str = ConfigEditor.get_active_language()
        Logger.info(f"Selected language: {language}")
        Localizer.initialize(language)

        match launch_mode.get():
            case "menu":
                from modules.frontend.menu import App
                App()

            case "player":
                print("player")

            case "studio":
                print("studio")

            case "rpc":
                print("rpc")
    
    except Exception as e:
        exception_handler.run(e)
    
    Logger.info("Shutting down...")
    sys.exit(0)


if __name__ == "__main__":
    main()