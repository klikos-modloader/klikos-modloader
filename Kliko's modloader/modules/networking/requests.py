"""
Responsible for handling HTTP requests.

Methods:
    get(url: str, timeout: int | tuple[int, int] = (5, 10), attempts: int = 3, cache: bool = True) -> Response:
        Makes a HTTP GET request to the specified URL.
"""

import time

from modules.logger import Logger

from .cache import Cache

import requests  # type: ignore
from requests import Response, HTTPError, RequestException, ConnectionError  # type: ignore


def get(url: str, timeout: int | tuple[int, int] = (5, 10), stream: bool = False, attempts: int = 3, cache: bool = True, ignore_cache: bool = False) -> Response:
    """
    Makes a HTTP GET request to the specified URL.

    Parameters:
        url (str):  The URL to which the GET request will be sent.
        timeout (int | tuple[int, int], optional): The timeout for the request. Default is (5, 10).
        attempts (int, optional): The number of attempts for the request. Default is 3.
        cache (bool, optional): Whether the Response should be cached. Default is True.
        ignore_cache (bool, optional): Whether the cached responses should be ignored. Default is False.
    """

    last_exception: Exception | None = None

    for i in range(1, attempts+1):
        try:
            if not ignore_cache and Cache.includes(url):
                return Cache.get(url)

            start: float = time.time()
            response: Response = requests.get(url, timeout=timeout, stream=stream)
            response.raise_for_status()
            duration: float = (time.time() - start) * 1000

            Logger.info(f"GET {url} -> {response.status_code} {response.reason or 'Reason unknown'} (duration: {duration:.2f}ms)")

            if cache:
                Cache.set(url, response)
            return response

        except HTTPError as e:
            response = e.response
            last_exception = e
            Logger.warning(f"GET {url} -> {response.status_code} {response.reason or 'Reason unknown'} (Attempt {i}/{attempts})")

        except ConnectionError as e:
            last_exception = e
            Logger.warning(f"GET {url} -> ConnectionError: {e} (Attempt {i}/{attempts})")

        except RequestException as e:
            last_exception = e
            Logger.warning(f"GET {url} -> RequestException {type(e).__name__}: {e} (Attempt {i}/{attempts})")

    Logger.error(f"GET {url} -> Failed after {attempts} attempt{'' if attempts == 1 else 's'}.")
    if last_exception: raise last_exception
    raise RuntimeError(f"GET {url} -> Failed after {attempts} attempt{'' if attempts == 1 else 's'}.")


# def head(url: str, timeout: int | tuple[int, int] = (5, 10), attempts: int = 3, cache: bool = True, ignore_cache: bool = False) -> Response:
#     """
#     Makes a HTTP HEAD request to the specified URL.

#     Parameters:
#         url (str):  The URL to which the HEAD request will be sent.
#         timeout (int | tuple[int, int], optional): The timeout for the request. Default is (5, 10).
#         attempts (int, optional): The number of attempts for the request. Default is 3.
#         cache (bool, optional): Whether the Response should be cached. Default is True.
#         ignore_cache (bool, optional): Whether the cached responses should be ignored. Default is False.
#     """

#     last_exception: Exception | None = None

#     for i in range(1, attempts+1):
#         try:
#             if not ignore_cache and Cache.includes(url):
#                 return Cache.get(url)

#             start: float = time.time()
#             response: Response = requests.head(url, timeout=timeout)
#             response.raise_for_status()
#             duration: float = (time.time() - start) * 1000

#             Logger.info(f"HEAD {url} -> {response.status_code} {response.reason or 'Reason unknown'} (duration: {duration:.2f}ms)")

#             if cache:
#                 Cache.set(url, response)
#             return response

#         except HTTPError as e:
#             response = e.response
#             last_exception = e
#             Logger.warning(f"HEAD {url} -> {response.status_code} {response.reason or 'Reason unknown'} (Attempt {i}/{attempts})")

#         except ConnectionError as e:
#             last_exception = e
#             Logger.warning(f"HEAD {url} -> ConnectionError: {e} (Attempt {i}/{attempts})")

#         except RequestException as e:
#             last_exception = e
#             Logger.warning(f"HEAD {url} -> RequestException {type(e).__name__}: {e} (Attempt {i}/{attempts})")

#     Logger.error(f"HEAD {url} -> Failed after {attempts} attempt{'' if attempts == 1 else 's'}.")
#     if last_exception: raise last_exception
#     raise RuntimeError(f"HEAD {url} -> Failed after {attempts} attempt{'' if attempts == 1 else 's'}.")