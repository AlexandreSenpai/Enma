import os
from expiringdict import ExpiringDict
from typing import Callable, Literal, Union, cast
from enma.application.core.utils.logger import logger

CacheState = Union[Literal["enabled"], Literal['disabled']]
STATE = cast(CacheState, os.getenv("ENMA_CACHING_STATE", 'enabled'))

class Cache:

  def __init__(self, 
               max_age_seconds: int=3600, 
               max_size: int=100, 
               enabled: CacheState = STATE):
    self._CACHE = ExpiringDict(max_len=max_size, 
                               max_age_seconds=max_age_seconds, 
                               items=None)
    self.enabled: bool = enabled == 'enabled'
  
  def cache(self, function: Callable):
    def wrapper(*args, **kwargs):

        _args = list()

        if len(kwargs.keys()) == 0:
            _args = list(args[1:])
        else:
            _args = list([*list(kwargs.values()), *args[1:]])

        if self._CACHE.get(str(_args)) is not None and self.enabled:
            logger.debug(f'Retrieving cached object with key {str(_args)}')
            return self._CACHE.get(str(_args))
        else:
            new_execution = function(*args, **kwargs)
            self._CACHE[str(_args)] = new_execution
            return new_execution

    return wrapper
