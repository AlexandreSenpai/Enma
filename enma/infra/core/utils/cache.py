from expiringdict import ExpiringDict
from typing import Callable
from enma.application.core.utils.logger import logger

class Cache:

  def __init__(self, max_age_seconds: int=3600, max_size: int=100):
    self._CACHE = ExpiringDict(max_len=max_size, 
                               max_age_seconds=max_age_seconds, 
                               items=None)
  
  def cache(self, function: Callable):
    def wrapper(*args, **kwargs):
        
        _args = list()

        if len(kwargs.keys()) == 0:
            _args = list(args[1:])
        else:
            _args = list([*list(kwargs.values()), *args[1:]])

        if self._CACHE.get(str(_args)) is not None:
            logger.debug(f'Retrieving cached object with key {str(_args)}')
            return self._CACHE.get(str(_args))
        else:
            new_execution = function(*args, **kwargs)
            self._CACHE[str(_args)] = new_execution
            return new_execution

    return wrapper