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
    _MIMES = {'j': 'jpg',
              'p': 'png',
              'g': 'gif'}
    _event_loop = get_event_loop()
    
    @property
    def event_loop(self) -> AbstractEventLoop:
        return self._event_loop

    @staticmethod
    def _get_lang_by_title(title: str) -> str:
        """This method runs through the title inputed and search by
        one of supported languages if it doesnt finds the methods returns
        Japanese.
        """

        SUPORTED_LANG = {'English': 'english', 'Chinese': 'chinese'}

        acceptable_title = title.replace('[', '').replace(']', '')
        partitoned_title = acceptable_title.split(' ')

        lang = 'japanese'

        for part in partitoned_title:
            current_language_key = SUPORTED_LANG.get(part)
            lang = current_language_key if current_language_key is not None else lang 
        
        return lang

    def _fetch(self, page_path: str, is_json: bool=False) -> Union[BeautifulSoup, dict]:
        page_path = page_path[1:] if page_path[0] == '/' else page_path
        PAGE_REQUEST = requests.get(urljoin(self._BASE_URL, page_path))
        if PAGE_REQUEST.status_code == 200:
            return PAGE_REQUEST.json() if is_json else BeautifulSoup(PAGE_REQUEST.content, 'html.parser')
        else:
            return PAGE_REQUEST.json() if is_json else BeautifulSoup("", 'html.parser')
    
    async def _async_fetch(self, page_path: str, is_json: bool=False) -> Union[BeautifulSoup, dict]:
        page_path = page_path[1:] if page_path[0] == '/' else page_path
        async with ClientSession() as session:
            async with session.get(urljoin(self._BASE_URL, page_path)) as response:
                if response.status == 200:
                    if is_json:
                        CONTENT = await response.json()
                        return CONTENT
                    else:
                        CONTENT = await response.read()
                        return BeautifulSoup(CONTENT, 'html.parser')
                else:
                    return await response.json() if is_json else BeautifulSoup("", 'html.parser')
