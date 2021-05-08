from bs4 import BeautifulSoup
from aiohttp import ClientSession
import requests

class BaseWrapper:
    def __init__(self, base_url: str):
        self.BASE_URL = base_url[:-1] if base_url[-1] == '/' else base_url
        self._SUPORTED_LANG = {'English': 'english', 'Chinese': 'chinese'}
        
    def _get_lang_by_title(self, title: str) -> str:
        """This method runs through the title inputed and search by
        one of supported languages if it doesnt finds the methods returns
        Japanese.
        """

        acceptable_title = title.replace('[', '').replace(']', '')
        partitoned_title = acceptable_title.split(' ')

        lang = 'japanese'

        for part in partitoned_title:
            current_language_key = self._SUPORTED_LANG.get(part)
            lang = current_language_key if current_language_key is not None else lang 
        
        return lang

    def _fetch(self, page_path: str) -> BeautifulSoup:
        page_path = page_path[1:] if page_path[0] == '/' else page_path
        PAGE_REQUEST = requests.get(f'{self.BASE_URL}/{page_path}')
        if (PAGE_REQUEST_STATUS_CODE := PAGE_REQUEST.status_code) == 200:
            return BeautifulSoup(PAGE_REQUEST.content, 'html.parser')
        else:
            raise Exception(f"Was not possible to fetch {self.BASE_URL}/{page_path}\nStatus code: {PAGE_REQUEST_STATUS_CODE}")
    
    async def _async_fetch(self, page_path: str) -> BeautifulSoup:
        page_path = page_path[1:] if page_path[0] == '/' else page_path
        async with ClientSession() as session:
            async with session.get(f'{self.BASE_URL}/{page_path}') as response:
                if (PAGE_REQUEST_STATUS_CODE := response.status) == 200:
                    CONTENT = await response.read()
                    return BeautifulSoup(CONTENT, 'html.parser')
                else:
                    raise Exception(f"Was not possible to fetch {self.BASE_URL}/{page_path}\nStatus code: {PAGE_REQUEST_STATUS_CODE}")
    

if __name__ == '__main__':
    b = BaseWrapper(base_url='https://www.w3schools.com/')
    b.fetch_page('/')