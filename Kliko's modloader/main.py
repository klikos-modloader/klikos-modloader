"""
Kliko's modloader: Roblox mods made easy
Source: https://github.com/klikos-modloader/klikos-modloader
License: MIT
"""

import sys
import platform
import argparse
from pathlib import Path


parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("-m", "--menu", action="store_true", help="Launches the modloader menu", dest="menu")
group.add_argument("-p", "--player", action="store_true", help="Launches Roblox Player", dest="player")
group.add_argument("-s", "--studio", action="store_true", help="Launches Roblox Studio", dest="studio")
group.add_argument("--presence", action="store_true", help="Launches the Activity Watcher", dest="presence")
parser.add_argument("--presence-mode", choices=["Player", "Studio"], dest="presence_mode")
parser.add_argument("--deeplink", help="Optional deeplink arguments when launching Roblox", dest="deeplink")
args = parser.parse_args()

# if not any([args.player, args.studio, args.presence]): args.menu = True  # Default launch mode
if not any([args.player, args.studio, args.presence]): args.player = True  # TODO: Remove this!
if args.presence_mode and not args.presence: args.presence_mode = None
if args.deeplink and not (args.player or args.studio): args.deeplink = None


FROZEN: bool = getattr(sys, "frozen", False)
if FROZEN:
    try:
        import pyi_splash  # type: ignore
        if pyi_splash.is_alive(): pyi_splash.close()
    except (ImportError, ModuleNotFoundError): pass

ROOT: Path = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT / "libraries"))


try:
    from modules.logger import Logger
    from modules.project_data import ProjectData
    from modules.localization import Localizer
    from modules.interfaces.config import ConfigInterface
    from modules.filesystem import Directories
    from modules.backend.registry_editor import set_registry_keys
    from modules import exception_handler
except (ImportError, ModuleNotFoundError) as e:
    print(f"[CRITICAL] Missing requires libraries!\n{type(e).__name__}: {e}")
    input("\nPress enter to exit")
    sys.exit(1)


def log_debug_info() -> None:
    if not FROZEN: Logger.warning("Environment not frozen!")
    if ConfigInterface.dev_mode_enabled(): Logger.debug("Running in developer mode...")
    Logger.debug(f"{ProjectData.NAME} v{ProjectData.VERSION}")
    Logger.debug(f"Platform: {platform.system()} {platform.release()}")
    Logger.debug(f"Launch mode: {'menu' if args.menu else 'player' if args.player else 'studio' if args.studio else 'presence' if args.presence else 'undefined'}")


def initialize_localization() -> None:
    Logger.info("Initializing localization...")
    language: str = ConfigInterface.get_language()
    Localizer.initialize()

    if ConfigInterface.dev_mode_enabled():
        Localizer.add_strings_directory(Directories.DEV_TRANSLATIONS)

    try: Localizer.set_language(language)
    except ValueError:
        Logger.error(f"Unsupported language: '{language}', reverting to default language")
        Localizer.set_language(Localizer.Metadata.DEFAULT_LANGUAGE)


def main() -> None:
    Logger.initialize()
    ConfigInterface.verify_file_integrity()
    log_debug_info()
    initialize_localization()

    try:
        if FROZEN:
            set_registry_keys()

        if args.menu:
            from modules.frontend import menu
            menu.run()

        elif args.player:
            from modules.frontend import launcher
            launcher.run("Player", args.deeplink)

        elif args.studio:
            from modules.frontend import launcher
            launcher.run("Studio", args.deeplink)

        elif args.presence:
            pass

    except Exception as e: exception_handler.run(e)
    Logger.info("Shutting down...")


if __name__ == "__main__":
    main()