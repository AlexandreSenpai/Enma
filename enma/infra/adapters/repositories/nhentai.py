from dataclasses import dataclass
from typing import Any, Literal, Optional
from urllib.parse import urlparse, urljoin

import requests

from enma.application.core.handlers.error import NhentaiSourceWithoutConfig
from enma.application.core.interfaces.manga_repository import IMangaRepository
from enma.domain.entities.Manga import Image, Manga, MIME, Title

@dataclass
class CloudFlareConfig:
    user_agent: str
    cf_clearance: str

class NHentai(IMangaRepository):
    
    def __init__(self, 
                 config: CloudFlareConfig | None = None) -> None:

        if config is None:
            raise NhentaiSourceWithoutConfig('Please provide a valid cloudflare cookie and user-agent.')

        self.__config = config
        self.__BASE_URL = 'https://nhentai.net/'
        self.__API_URL = 'https://nhentai.net/api/'
        self.__IMAGE_BASE_URL = 'https://i.nhentai.net/galleries/'
        self.__AVATAR_URL = 'https://i5.nhentai.net/'
        self.__TINY_IMAGE_BASE_URL = self.__IMAGE_BASE_URL.replace('/i.', '/t.')

    def __make_request(self, 
                       url: str,
                       headers: dict[str, Any] | None = None):
        headers = headers if headers is not None else {}
        return requests.get(url=urlparse(url).geturl(), 
                            headers={**headers, 'User-Agent': self.__config.user_agent},
                            cookies={'cf_clearance': self.__config.cf_clearance})
    
    def __make_page_uri(self, 
                        type: Literal['cover'] | Literal['page'] | Literal['thumbnail'],
                        media_id: str,
                        mime: MIME,
                        page_number: Optional[int] = None) -> str:
        if type == 'cover': return urljoin(self.__TINY_IMAGE_BASE_URL, f'{media_id}/cover.{mime.value}')
        if type == 'thumbnail': return urljoin(self.__TINY_IMAGE_BASE_URL, f'{media_id}/thumb.{mime.value}')
        return urljoin(self.__IMAGE_BASE_URL, f'{media_id}/{page_number}.{mime.value}')

    def get(self, identifier: str) -> Manga | None:
        response = self.__make_request(url=f'{self.__API_URL}/gallery/{identifier}')
        
        if response.status_code != 200:
            return
        
        doujin = response.json()

        return Manga(title=Title(english=doujin.get('title').get('english'),
                                 japanese=doujin.get('title').get('japanese'),
                                 other=doujin.get('title').get('pretty')),
                     id=doujin.get('id'),
                     thumbnail=Image(uri=self.__make_page_uri(type='thumbnail',
                                                              mime=MIME[doujin.get("images").get("thumbnail").get("t").upper()],
                                                              media_id=doujin.get('media_id')),
                                     width=doujin.get("images").get("thumbnail").get("w"),
                                     height=doujin.get("images").get("thumbnail").get("h")),
                     cover=Image(uri=self.__make_page_uri(type='cover',
                                                          media_id=doujin.get('media_id'),
                                                          mime=MIME[doujin.get("images").get("thumbnail").get("t").upper()]),
                                 width=doujin.get("images").get("cover").get("w"),
                                 height=doujin.get("images").get("cover").get("h")),
                     pages=[Image(uri=self.__make_page_uri(type='page',
                                                           mime=MIME[doujin.get("images").get("thumbnail").get("t").upper()],
                                                           media_id=doujin.get('media_id'),
                                                           page_number=index+1),
                                  width=page.get('w'),
                                  height=page.get('h')) for index, page in enumerate(doujin.get('images').get('pages'))])

    def search(self, query: str) -> Manga | None:
        raise NotImplementedError('Search Method Was Not Implemented.')