from pathlib import Path
import urllib.request
from urllib.error import HTTPError, URLError, ContentTooShortError
import time

from modules.logger import Logger


def download(source: str, destination: Path, attempts: int = 3) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp: Path = destination.with_suffix(".tmp")

    last_exception: Exception | None = None

    for i in range(1, attempts+1):
        try:
            start: float = time.time()
            urllib.request.urlretrieve(source, temp)
            temp.replace(destination)
            duration: float = (time.time() - start) * 1000
            Logger.info(f"DOWNLOAD {source} -> SUCCESS (duration: {duration:.2f}ms)")
            return

        except HTTPError as e:
            last_exception = e
            Logger.warning(f"DOWNLOAD {source} -> {e.code} {e.reason or 'Reason unknown'} (Attempt {i}/{attempts})")

        except ConnectionError as e:
            last_exception = e
            Logger.warning(f"DOWNLOAD {source} -> ConnectionError: {e} (Attempt {i}/{attempts})")

        except URLError as e:
            last_exception = e
            Logger.warning(f"DOWNLOAD {source} -> URLError: {e.reason} (Attempt {i}/{attempts})")

        except ContentTooShortError as e:
            last_exception = e
            Logger.warning(f"DOWNLOAD {source} -> ContentTooShortError: {e.reason} (Attempt {i}/{attempts})")

        except OSError as e:
            last_exception = e
            Logger.warning(f"DOWNLOAD {source} -> OSError {type(e).__name__}: {e} (Attempt {i}/{attempts})")

        except Exception as e:
            last_exception = e
            Logger.warning(f"DOWNLOAD {source} -> Exception {type(e).__name__}: {e} (Attempt {i}/{attempts})")

    Logger.error(f"DOWNLOAD {source} -> Failed after {attempts} attempt{'' if attempts == 1 else 's'}.")
    if last_exception: raise last_exception
    raise RuntimeError(f"DOWNLOAD {source} -> Failed after {attempts} attempt{'' if attempts == 1 else 's'}.")