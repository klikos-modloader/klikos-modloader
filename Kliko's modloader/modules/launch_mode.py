import sys


MODES: dict[str,list[str]] = {
    "menu": ["-m", "--menu"],
    "player": ["-l", "-p", "--launch", "--launcher", "--player"],
    "studio": ["-c", "-s", "--create", "--studio"],
    "rpc": ["-rpc", "--presence"]
}
DEFAULT: str = list(MODES.keys())[0]
REVERSE_MAP: dict[str,str] = {option: mode for mode, options in MODES.items() for option in options}


def get() -> str:
    args: list = sys.argv[1:]

    for item in args:
        mode = REVERSE_MAP.get(item)
        if mode is not None:
            return mode

    return DEFAULT