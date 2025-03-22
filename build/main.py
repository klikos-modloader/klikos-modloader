import sys
import shlex
import subprocess
from pathlib import Path
import shutil


EXECUTABLE_NAME: str = "Kliko's modloader"
REQUIRED_PYTHON_VERSION: str = "3.12.4"
LIBRARIES: list[str] = [
    "customtkinter",
    "natsort",
    "packaging",
    "pillow",
    "requests",
    "tkinterdnd2",
    "winaccent"
]


class Directory:
    BUILD: Path = Path(__file__).parent
    BIN: Path = BUILD / "bin"
    TEMP: Path = BUILD / "temp"
    SOURCE: Path = Path(__file__).parent.parent / "Kliko's modloader"
    TEMP_SOURCE: Path = TEMP / "source"
    MODULES: Path = TEMP_SOURCE / "modules"
    CONFIG: Path = TEMP_SOURCE / "config"
    LIBRARIES: Path = TEMP_SOURCE / "libraries"


def main() -> None:
    print("[INFO] Checking Python version...")
    current_python_version: str = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if current_python_version != REQUIRED_PYTHON_VERSION:
        print(f"\n[ERROR] Wrong Python version: {current_python_version} ({REQUIRED_PYTHON_VERSION} required)!")
        return

    print("[INFO] Checking PIP...")
    if not pip_installed():
        print(f"\n[ERROR] PIP not found!")
        print("Please install PIP and try again")
        return

    print("[INFO] Checking PyInstaller...")
    if not pyinstaller_installed():
        print(f"\n[ERROR] PyInstaller not found!")
        print("Please install PyInstaller and try again")
        return

    print("[INFO] Preparing files...")
    if Directory.TEMP.exists(): shutil.rmtree(Directory.TEMP)
    if Directory.BIN.exists(): shutil.rmtree(Directory.BIN)
    Directory.BIN.mkdir(parents=True, exist_ok=True)
    Directory.TEMP.mkdir(parents=True, exist_ok=True)
    shutil.copytree(Directory.SOURCE, Directory.TEMP_SOURCE)

    print("[INFO] Installing libraries...")
    Directory.LIBRARIES.mkdir(parents=True, exist_ok=True)
    command = ["pip", "install", f"--target={str(Directory.LIBRARIES.resolve())}", "--upgrade", *LIBRARIES]
    result = subprocess.run(command)
    if result.returncode != 0:
        print(f"\n[ERROR] Error while installing libraries!")
        return

    print("[INFO] Running PyInstaller...")
    Directory.TEMP.mkdir(parents=True, exist_ok=True)
    command = [
        "pyinstaller", str((Directory.BUILD / "Kliko's modloader.spec").resolve()),
        f'--distpath={str(Directory.BIN.resolve())}',
        f'--workpath={str(Directory.TEMP.resolve())}'
    ]
    result = subprocess.run(command)
    if result.returncode != 0:
        print(f"\n[ERROR] Error while running PyInstaller!")
        return
    
    print("[INFO] Removing temporary files...")
    if Directory.TEMP.exists(): shutil.rmtree(Directory.TEMP)

    print("[INFO] Done!")



def pip_installed() -> bool:
    try:
        subprocess.run(["pip", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError:
        return False


def pyinstaller_installed() -> bool:
    try:
        subprocess.run(["pyinstaller", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError:
        return False


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
    input("Press Enter to exit...")