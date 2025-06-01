"""
Package responsible for handling HTTP requests and storing API endpoints.

includes:
- Api: A class that stores API endpoints.
- requests: Responsible for handling HTTP requests.
"""

from .api import Api
from . import requests
from .requests import Response, RequestException, ConnectionError, HTTPError
from .cache import Cache