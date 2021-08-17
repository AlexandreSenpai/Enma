from asyncio import get_event_loop
from asyncio import AbstractEventLoop
from urllib.parse import urljoin
from typing import Union

from bs4 import BeautifulSoup
from aiohttp import ClientSession
import requests

class BaseWrapper:

    _BASE_URL = 'https://nhentai.net/'
    _API_URL = 'https://nhentai.net/api/'
    _IMAGE_BASE_URL = 'https://i.nhentai.net/galleries/'
    _TINY_IMAGE_BASE_URL = _IMAGE_BASE_URL.replace('/i.', '/t.')

    _event_loop = get_event_loop()

    def __init__(self, cache_size: int=100):
        self.cache_size: cache_size
    
    @property
    def event_loop(self) -> AbstractEventLoop:
        return self._event_loop

    def _fetch(self, page_path: str, params={}, is_json: bool=False) -> Union[BeautifulSoup, dict]:
        page_path = page_path[1:] if page_path[0] == '/' else page_path
        PAGE_REQUEST = requests.get(urljoin(self._BASE_URL, page_path), params=params)
        if PAGE_REQUEST.status_code == 200:
            return PAGE_REQUEST.json() if is_json else BeautifulSoup(PAGE_REQUEST.content, 'html.parser')
        else:
            return PAGE_REQUEST.json() if is_json else BeautifulSoup("", 'html.parser')
    
    async def _async_fetch(self, page_path: str, params={}, is_json: bool=False) -> Union[BeautifulSoup, dict]:
        page_path = page_path[1:] if page_path[0] == '/' else page_path
        async with ClientSession() as session:
            async with session.get(urljoin(self._BASE_URL, page_path), params=params) as response:
                if response.status == 200:
                    if is_json:
                        CONTENT = await response.json()
                        return CONTENT
                    else:
                        CONTENT = await response.read()
                        return BeautifulSoup(CONTENT, 'html.parser')
                else:
                    return await response.json() if is_json else BeautifulSoup("", 'html.parser')
