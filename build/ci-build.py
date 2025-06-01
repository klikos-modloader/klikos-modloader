import sys
import subprocess
from pathlib import Path
import shutil


EXECUTABLE_NAME: str = "Kliko's modloader"
DEPENDENCIES: list[str] = [
    "customtkinter~=5.2.2",
    "tkinterdnd2==0.4.3",
    "winaccent==2.0.1",
    "pyperclip~=1.9.0",
    "pillow~=11.1.0",
    "natsort==8.4.0",
    "packaging==25.0",
    "requests~=2.32.3",
    "py7zr==0.22.0",
    "numpy==2.2.6",
    "pypresence==4.3.0",
    "packaging"
]


class PathObject:
    BUILD: Path = Path(__file__).parent.resolve()
    BIN: Path = BUILD / "bin"
    TEMP: Path = BUILD / "temp"
    SOURCE: Path = BUILD.parent / "Kliko's modloader"
    SPEC_PATH: Path = TEMP / "Kliko's modloader.spec"
    TEMP_SOURCE: Path = TEMP / "source"
    MODULES: Path = TEMP_SOURCE / "modules"
    DEPENDENCIES: Path = TEMP_SOURCE / "libraries"


def get_spec_data(tkdnd_path: Path) -> str:
    return rf"""
# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_submodules

a = Analysis(
    [r"{str(PathObject.TEMP_SOURCE / "main.py")}"],
    pathex=[r"{str(PathObject.DEPENDENCIES)}"],
    binaries=[],
    datas=[
        (r"{str(PathObject.TEMP_SOURCE / "modules")}", 'modules'),
        (r"{str(PathObject.TEMP_SOURCE / "resources")}", 'resources'),
        (r"{str(PathObject.DEPENDENCIES)}", 'libraries'),
        (r"{str(tkdnd_path)}", 'tkdnd')
    ],
    hiddenimports=["tkinter", "customtkinter", "tkinterdnd2"],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
splash = Splash(
    r"{str(PathObject.BUILD / "splash.png")}",
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    text_size=12,
    minify_script=True,
    always_on_top=True,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    splash,
    splash.binaries,
    [],
    name="Kliko's modloader.exe",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[r"{str(PathObject.BUILD / "favicon.ico")}"],
)
"""


def main() -> None:
    print("[INFO] Preparing files...")
    PathObject.BIN.mkdir(parents=True, exist_ok=True)
    PathObject.TEMP.mkdir(parents=True, exist_ok=True)
    shutil.copytree(PathObject.SOURCE, PathObject.TEMP_SOURCE)

    print("[INFO] Installing dependencies...")
    PathObject.DEPENDENCIES.mkdir(parents=True, exist_ok=True)
    command = ["pip", "install", f"--target={str(PathObject.DEPENDENCIES)}", "--upgrade", *DEPENDENCIES]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] pip install failed!")
        sys.exit(e.returncode)

    print("[INFO] Preparing files...")
    sys.path.insert(0, str(PathObject.DEPENDENCIES))
    import tkinterdnd2  # type: ignore
    tkdnd_path: Path = Path(tkinterdnd2.__file__).parent / "tkdnd"
    spec_data: str = get_spec_data(tkdnd_path)
    with open(PathObject.SPEC_PATH, "w", encoding="utf-8") as file:
        file.write(spec_data)

    print("[INFO] Running PyInstaller...")
    PathObject.TEMP.mkdir(parents=True, exist_ok=True)
    command = [
        "pyinstaller", str((PathObject.SPEC_PATH)),
        f'--distpath={str(PathObject.BIN)}',
        f'--workpath={str(PathObject.TEMP)}',
        "--noconfirm"
    ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Pyinstaller failed!")
        sys.exit(e.returncode)

    print("[INFO] Done!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        sys.exit(1)