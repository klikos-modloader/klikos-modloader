from threading import Thread, Lock
from typing import Callable

import winaccent  # type: ignore


class WinAccentTracker:
    running: bool = False
    _callback_list: list[Callable] = []
    _lock: Lock = Lock()


    @classmethod
    def _start(cls) -> None:
        if not cls.running:
            Thread(target=lambda: winaccent.on_appearance_changed(cls.update_callbacks), daemon=True).start()
            cls.running = True


    @classmethod
    def add_callback(cls, callback: Callable) -> None:
        with cls._lock:
            if callable(callback) and callback not in cls._callback_list: cls._callback_list.append(callback)
        cls._start()


    @classmethod
    def update_callbacks(cls) -> None:
        with cls._lock:
            for callback in cls._callback_list:
                try: callback()
                except Exception: pass