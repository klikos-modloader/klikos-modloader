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
ROOT: Path = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
sys.path.insert(0, str((ROOT / "libraries").resolve()))
sys.path.insert(0, str((ROOT / "forked_libraries").resolve()))

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