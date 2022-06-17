import functools
from expiringdict import ExpiringDict
from typing import Callable

from NHentai.core.logging import logger

class Cache:
  _CACHE = None

  def __init__(self, cache_key_position: int, cache_key_name: str, max_age_seconds: int=3600, max_size: int=100):
    self._CACHE = ExpiringDict(max_len=max_size, max_age_seconds=max_age_seconds, items=None)
    self.cache_key_position = cache_key_position
    self.cache_key_name = cache_key_name
  
  def cache(self, function: Callable):
    def wrapper(*args, **kwargs):

      key = kwargs.get(self.cache_key_name) if kwargs.get(self.cache_key_name) is not None else args[self.cache_key_position]

      if self._CACHE.get(key) is not None:
        logger.warn(f'Retrieving cached object with key {key}')
        return self._CACHE.get(key)
      else:
        new_execution = function(*args, **kwargs)
        self._CACHE[key] = new_execution
        return new_execution
        
    return wrapper
  
  def async_cache(self, function: Callable):
    @functools.wraps(function)
    async def wrapper(*args, **kwargs):
        key = kwargs.get(self.cache_key_name) if kwargs.get(self.cache_key_name) is not None else args[self.cache_key_position]

        if self._CACHE.get(key) is not None:
            logger.warn(f'Retrieving cached object with key {key}')
            return self._CACHE.get(key)
        else:
            new_execution = await function(*args, **kwargs)
            self._CACHE[key] = new_execution
        return new_execution

    return wrapper