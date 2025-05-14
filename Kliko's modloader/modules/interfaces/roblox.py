from typing import Literal
import subprocess

import psutil  # type: ignore


class RobloxInterface:
    @classmethod
    def is_roblox_running(cls, mode: Literal["Player", "Studio"] | None = None) -> bool:
        match mode:
            case "Player": return cls._process_exists("RobloxPlayerBeta.exe")
            case "Studio": return cls._process_exists("RobloxStudioBeta.exe")
            case _: return cls._process_exists("RobloxPlayerBeta.exe") or cls._process_exists("RobloxStudioBeta.exe")


    @classmethod
    def _process_exists(cls, name: str) -> bool:
        for process in psutil.process_iter():
            try:
                if process.name() == name:
                    return True
            except psutil.NoSuchProcess:
                continue
        return False
    

    @classmethod
    def kill_existing_instances(cls, mode: Literal["Player", "Studio"] | None = None) -> None:
        match mode:
            case "Player": return cls._kill_process("RobloxPlayerBeta.exe")
            case "Studio": return cls._kill_process("RobloxStudioBeta.exe")
            case _: return cls._kill_process("RobloxPlayerBeta.exe") or cls._kill_process("RobloxStudioBeta.exe")


    @classmethod
    def _kill_process(cls, name: str) -> None:
        subprocess.run(["TASKKILL", "/F", "/IM", name], creationflags=subprocess.CREATE_NO_WINDOW, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)