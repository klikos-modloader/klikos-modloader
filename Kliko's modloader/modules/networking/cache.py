"""Responsible for storing and retrieving `requests.Response` object."""

from requests import Response  # type: ignore


class Cache:
    """
    Responsible for storing and retrieving `requests.Response` object."
    
    Methods:
        get(key: str) -> Response:
            Retreive a Response object from the cache.
        set(key: str, value: Response, strict: bool = False) -> None:
            Store a Response object in the cache.
        remove(key: str, strict: bool = False) -> None:
            Remove a Response object from the cache.
        includes(key: str) -> bool:
            Check if a given key is present in the cache.
    """

    _cache: dict[str, Response] = {}


    @classmethod
    def get(cls, key: str) -> Response:
        """
        Retreive a Response object from the cache.

        Parameters:
            key (str): The cache key associated with a Response object.

        Returns:
            Response: The Response object associated with the given cache key.
        
        Raises:
            KeyError: If the given key is not present in the cache.
        """

        if not cls.includes(key):
            raise KeyError(f"Key not present in cache: {key}")
        return cls._cache[key]


    @classmethod
    def set(cls, key: str, value: Response, strict: bool = False) -> None:
        """
        Store a Response object in the cache.

        Parameters:
          key (str): The cache key associated with a Response object.
          value (Response): The Response object to store in the cache.
          strict (bool, optional): Raise an error if the key already exists in the cache. Default is False.
        
        Raises:
          KeyError: If the given key already exists in the cache and strict=True.
        """
        
        if strict and cls.includes(key):
            raise ValueError(f"Key already present in cache: {key}")
        cls._cache[key] = value


    @classmethod
    def remove(cls, key: str, strict: bool = False) -> None:
        """
        Remove a Response object from the cache.

        Parameters:
          key (str): The cache key associated with a Response object.
          strict (bool, optional): Raise an error if the key is not present in the cache. Default is False.
        
        Raises:
          KeyError: If the given key is not present in the cache and strict=True.
        """

        if strict and not cls.includes(key):
            raise KeyError(f"Key not present in cache: {key}")
        cls._cache.pop(key, None)


    @classmethod
    def includes(cls, key: str) -> bool:
        """
        Check if a given key is present in the cache.

        Parameters:
          key (str): The cache key associated with a Response object.

        Returns:
            bool: True if the given key is present in the cache, otherwise False.
        """

        return key in cls._cache