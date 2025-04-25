"""
Kliko's modloader: Roblox mods made easy
Source: https://github.com/klikos-modloader/klikos-modloader
License: MIT
"""

import sys
import platform
import argparse


parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("-m", "--menu", action="store_true", help="Launches the modloader menu", dest="menu")
group.add_argument("-p", "--player", action="store_true", help="Launches Roblox Player", dest="player")
group.add_argument("-s", "--studio", action="store_true", help="Launches Roblox Studio", dest="studio")
group.add_argument("--presence", action="store_true", help="Launches the Activity Watcher", dest="presence")
parser.add_argument("--presence-mode", choices=["Player", "Studio"], dest="presence_mode")
parser.add_argument("--deeplink", help="Optional deeplink arguments when launching Roblox", dest="deeplink")
args = parser.parse_args()

if not any([args.player, args.studio, args.presence]): args.menu = True
if args.presence_mode and not args.presence: args.presence_mode = None
if args.deeplink and not (args.player or args.studio): args.deeplink = None


FROZEN: bool = getattr(sys, "frozen", False)
if FROZEN:
    try:
        import pyi_splash  # type: ignore
        if pyi_splash.is_alive(): pyi_splash.close()
    except (ImportError, ModuleNotFoundError): pass


from modules.logger import Logger  # Initialize on import
from modules.project_data import ProjectData


def log_debug_info() -> None:
    if not FROZEN: Logger.warning("Running in development mode!")
    Logger.debug(f"{ProjectData.NAME} v{ProjectData.VERSION}")
    Logger.debug(f"Platform: {platform.system()} {platform.release()}")
    Logger.debug(f"Launch arguments: {str(args).removeprefix("Namespace(").removesuffix(")")}")


def main() -> None:
    log_debug_info()


if __name__ == "__main__":
    main()