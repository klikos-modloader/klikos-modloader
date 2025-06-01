from pathlib import Path
from typing import Optional, Callable, Any
from threading import Thread, Event

from modules.networking import requests


class DownloadStream:
    _on_progress: Optional[Callable[[int, int], Any]]
    _on_success: Optional[Callable]
    _on_cancel: Optional[Callable]
    _on_error: Optional[Callable[[Exception], Any]]
    _downloading: bool = False
    _stop_event: Event

    def __init__(self, on_progress: Optional[Callable[[int, int], Any]] = None, on_success: Optional[Callable] = None, on_error: Optional[Callable[[Exception], Any]] = None, on_cancel: Optional[Callable] = None):
        self._on_progress = on_progress
        self._on_success = on_success
        self._on_cancel = on_cancel
        self._on_error = on_error


    def download_file(self, source: str, destination: str | Path, timeout: int | tuple[int, int] = (5, 10), attempts: int = 3, chunk_size: int = 1024) -> None:
        def worker() -> None:
            target = Path(destination)
            try:
                with requests.get(source, timeout=timeout, attempts=attempts, stream=True, cache=False, ignore_cache=True) as response:
                    try: total_size: int = int(response.headers["Content-Length"])
                    except (ValueError, KeyError): total_size = 0
                    downloaded: int = 0

                    target.parent.mkdir(parents=True, exist_ok=True)
                    with open(target, "wb") as file:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if self._stop_event.is_set(): break
                            if chunk:
                                file.write(chunk)
                                downloaded += len(chunk)
                                if self._on_progress:
                                    self._on_progress(downloaded, total_size)

                    if self._stop_event.is_set():
                        target.unlink(missing_ok=True)
                        if self._on_cancel:
                            self._on_cancel()

                    elif self._on_success:
                        self._on_success()

            except Exception as e:
                if self._on_error: self._on_error(e)

        if self._downloading: raise RuntimeError("DownloadStream busy! Open another stream instead.")
        self._stop_event = Event()
        Thread(target=worker, daemon=True).start()