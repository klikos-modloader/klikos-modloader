import sys
from pathlib import Path


class Directory:
    """Dataclass storing the path objects to important directories."""

    ROOT: Path = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent.parent.parent
    LIBRARIES: Path = ROOT / "libraries"
    LOGS: Path = ROOT / "Logs"
    CRASHES: Path = ROOT / "Crashes"
    CONFIG: Path = ROOT / "config"
    MODS: Path = ROOT / "Mods"
    CACHE: Path = ROOT / "cache"
    
    LOCALAPPDATA: Path = Path.home() / "AppData" / "Local"
    ROBLOX: Path = LOCALAPPDATA / "Roblox"