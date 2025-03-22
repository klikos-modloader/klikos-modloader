import urllib.request
from pathlib import Path
from threading import Thread, Event
from typing import Callable, Optional
from urllib.error import URLError, HTTPError
from socket import timeout as _socket_timeout_exception

from .exceptions import DownloadInProgressError, DownloadPermissionError, DownloadSocketTimeoutError, DownloadConnectionError, DownloadHTTPError


class StreamedDownloadHandler:
    downloading: tuple = (False, None, None)
    stop_event: Event

    _on_success: Optional[Callable] = None
    _on_progress: Optional[Callable] = None
    _on_error: Optional[Callable] = None

    def __init__(self, on_progress: Optional[Callable] = None, on_error: Optional[Callable] = None, on_success: Optional[Callable] = None) -> None:
        self._on_success = on_success
        self._on_progress = on_progress
        self._on_error = on_error
        self.stop_event = Event()


    def download_file(self, source: str, target: Path, timeout: int = 10, chunk_size: int = 1024) -> None:
        def worker(source: str, target: Path, chunk_size: int) -> None:
            try:
                if target.is_dir(): target = target / source.split("/")[-1]
                with urllib.request.urlopen(source, timeout=timeout) as response:
                    total_size: int = int(response.headers.get("Content-Length", 0))
                    downloaded: int = 0

                    target.parent.mkdir(parents=True, exist_ok=True)
                    with open(target, "wb") as file:
                        while not self.stop_event.is_set():
                            chunk = response.read(chunk_size)
                            if not chunk: break

                            file.write(chunk)
                            downloaded += len(chunk)

                            if callable(self._on_progress): self._on_progress(downloaded, total_size)

                if self.stop_event.is_set(): target.unlink(missing_ok=True)
                elif callable(self._on_success): self._on_success()

            except PermissionError:
                if callable(self._on_error): self._on_error(DownloadPermissionError(target))

            except _socket_timeout_exception:
                if callable(self._on_error): self._on_error(DownloadSocketTimeoutError(timeout))

            except HTTPError as e:
                if callable(self._on_error): self._on_error(DownloadHTTPError(e.code, e.reason))

            except URLError as e:
                if callable(self._on_error): self._on_error(DownloadConnectionError(str(e)))

            except Exception as e:
                if callable(self._on_error): self._on_error(e)

            finally:
                self.downloading = (False, None, None)
                self.stop_event.clear()

        if self.downloading[0]: raise DownloadInProgressError(self.downloading[1], self.downloading[2])
        self.downloading = (True, source, target)
        Thread(target=worker, args=(source, target, chunk_size), daemon=True).start()


    def stop_download(self) -> None:
        if self.downloading[0]: self.stop_event.set()