"""
This module provides an adapter for the nhentai repository.
It contains functions and classes to interact with the nhentai API and retrieve manga data.
"""
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal, Optional, Union, cast
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag

from enma.application.core.handlers.error import (ExceedRetryCount,
                                                  NhentaiSourceWithoutConfig)
from enma.application.core.interfaces.manga_repository import IMangaRepository
from enma.application.core.utils.logger import logger
from enma.domain.entities.author_page import AuthorPage
from enma.domain.entities.manga import (MIME, Chapter, Genre, Author, Image, Manga, SymbolicLink,
                                        Title)
from enma.domain.entities.search_result import Pagination, SearchResult, Thumb
from enma.infra.core.interfaces.nhentai_response import NHentaiImage, NHentaiResponse


@dataclass
class CloudFlareConfig:
    user_agent: str
    cf_clearance: str

class __StrEnum(str, Enum):...

class Sort(__StrEnum):
    TODAY = 'popular-today'
    WEEK = 'popular-week'
    ALL_TIME = 'popular'
    RECENT = None

class NHentai(IMangaRepository):
    """
    Repository class for interacting with the nhentai API.
    Provides methods to fetch manga details, search for manga, etc.
    """
    def __init__(self,
                 config: Optional[CloudFlareConfig] = None) -> None:
        self.__config = config
        self.__BASE_URL = 'https://nhentai.net'
        self.__API_URL = 'https://nhentai.net/api/'
        self.__IMAGE_BASE_URL = 'https://i.nhentai.net/galleries/'
        self.__AVATAR_URL = 'https://i5.nhentai.net/'
        self.__TINY_IMAGE_BASE_URL = self.__IMAGE_BASE_URL.replace('/i.', '/t.')

    def __make_request(self,
                       url: str,
                       headers: Union[dict[str, Any], None] = None,
                       params: Optional[dict[str, Union[str, int]]] = None):

        if self.__config is None:
            raise NhentaiSourceWithoutConfig('Please provide a valid cloudflare cookie and user-agent.')

        headers = headers if headers is not None else {}
        params = params if params is not None else {}

        logger.debug(f'Fetching {url} with headers {headers} and params {params} the current config cf_clearance: {self.__config.cf_clearance}')

        response = requests.get(url=urlparse(url).geturl(),
                                headers={**headers, 'User-Agent': self.__config.user_agent},
                                params={**params},
                                cookies={'cf_clearance': self.__config.cf_clearance})
        
        logger.debug(f'Fetched {url} with response status code {response.status_code} and text {response.text}')

        return response

    def set_config(self, config: CloudFlareConfig) -> None:
        self.__config = config

    def __handle_request_error(self, msg: str) -> None:
        logger.error(msg)
        return None
    
    def __make_page_uri(self,
                        type: Union[Literal['cover'], Literal['page'], Literal['thumbnail']],
                        media_id: str,
                        mime: MIME,
                        page_number: Optional[int] = None) -> str:
        
        url = ''

        if type == 'cover': 
            url = urljoin(self.__TINY_IMAGE_BASE_URL, f'{media_id}/cover.{mime.value}')
        elif type == 'thumbnail': 
            url = urljoin(self.__TINY_IMAGE_BASE_URL, f'{media_id}/thumb.{mime.value}')
        else:
            url = urljoin(self.__IMAGE_BASE_URL, f'{media_id}/{page_number}.{mime.value}')
        
        logger.debug(f'Built page uri for type {type} as {url}')

        return url
    
    def fetch_chapter_by_symbolic_link(self, 
                                       link: SymbolicLink) -> Chapter:
        response = self.__make_request(url=link.link)

        if response.status_code != 200:
            self.__handle_request_error(msg=f'Could not fetch {link.link} because nhentai\'s request ends up with {response.status_code} status code.')
            return Chapter()
        
        doujin: NHentaiResponse = response.json()

        if doujin.get('media_id') is None or doujin.get('images') is None:
            return Chapter()

        return self.__create_chapter(url=link.link, 
                                     with_symbolic_links=False, 
                                     media_id=doujin.get('media_id'), 
                                     pages=doujin.get('images').get('pages'))

    def __create_chapter(self,
                         url: str,
                         media_id: str, 
                         pages: list[NHentaiImage],
                         with_symbolic_links: bool = False) -> Chapter:
        
        if with_symbolic_links:
            return Chapter(link=SymbolicLink(link=url))
        else:
            chapter = Chapter()
            for index, page in enumerate(pages):
                mime = MIME[page.get('t').upper()]
                chapter.add_page(Image(uri=self.__make_page_uri(type='page',
                                                                mime=mime,
                                                                media_id=media_id,
                                                                page_number=index+1),
                                name=f'{index}.{mime.value}',
                                mime=mime,
                                width=page.get('w'),
                                height=page.get('h')))
            return chapter
    
    def get(self, 
            identifier: str,
            with_symbolic_links: bool = False) -> Union[Manga, None]:

        url = f'{self.__API_URL}/gallery/{identifier}'
        response = self.__make_request(url=url)

        if response.status_code != 200:
            return self.__handle_request_error(msg=f'Could not fetch {identifier} because nhentai\'s request ends up with {response.status_code} status code.')

        doujin: NHentaiResponse = response.json()
        media_id = doujin.get('media_id')

        chapter = self.__create_chapter(url=url,
                                        with_symbolic_links=with_symbolic_links,
                                        media_id=media_id, 
                                        pages=doujin.get('images').get('pages'))

        language = [tag.get('name') for tag in doujin.get('tags') if tag.get('type') == 'language']
        authors = [Author(id=tag.get('id'),
                          name=tag.get('name')) for tag in doujin.get('tags') if tag.get('type') == 'artist']
        genres = [Genre(id=genre.get('id'),
                        name=genre.get('name')) for genre in doujin.get('tags') if genre.get('type') == 'tag']
        
        thumbnail_mime = MIME[doujin.get("images").get("thumbnail").get("t").upper()]
        thumbnail = Image(uri=self.__make_page_uri(type='thumbnail',
                                                   mime=thumbnail_mime,
                                                   media_id=media_id),
                          mime=thumbnail_mime,
                          width=doujin.get("images").get("thumbnail").get("w"),
                          height=doujin.get("images").get("thumbnail").get("h"))
        
        cover_mime = MIME[doujin.get("images").get("cover").get("t").upper()]
        cover = Image(uri=self.__make_page_uri(type='cover',
                                               media_id=media_id,
                                               mime=cover_mime),
                      mime=cover_mime,
                      width=doujin.get("images").get("cover").get("w"),
                      height=doujin.get("images").get("cover").get("h"))

        manga = Manga(title=Title(english=doujin.get('title').get('english'),
                                  japanese=doujin.get('title').get('japanese'),
                                  other=doujin.get('title').get('pretty')),
                      id=doujin.get('id'),
                      created_at=datetime.fromtimestamp(doujin.get('upload_date'), tz=timezone.utc),
                      updated_at=datetime.fromtimestamp(doujin.get('upload_date'), tz=timezone.utc),
                      language=language[0] if len(language) > 0 else None,
                      authors=authors,
                      genres=genres,
                      thumbnail=thumbnail,
                      cover=cover,
                      chapters=[chapter])

        return manga

    def search(self,
               query: str,
               page: int,
               sort: Sort = Sort.RECENT) -> SearchResult:
        
        logger.debug(f'Searching into Nhentai with args query={query};page={page};sort={sort}')

        request_response = self.__make_request(url=urljoin(self.__BASE_URL, 'search'),
                                               params={'q': query,
                                                       'sort': sort if isinstance(sort, str) else sort.value,
                                                       'page': page})
        
        search_result = SearchResult(query=query,
                                     total_pages=0,
                                     page=page,
                                     total_results=0,
                                     results=[])
        
        if request_response.status_code != 200:
            self.__handle_request_error(f'Could not search by {query} because nhentai\'s request ends up with {request_response.status_code} status code.')
            return search_result

        soup = BeautifulSoup(request_response.text, 'html.parser')

        search_results_container = soup.find('div', {'class': 'container'})
        logger.debug(f'Found successfully search result container using .class.container.')
        pagination_container = soup.find('section', {'class': 'pagination'})
        logger.debug(f'Found successfully pagination container using .class.pagination.')

        last_page_a_tag = pagination_container.find('a', {'class': 'last'}) if pagination_container else None # type: ignore
        logger.debug(f'Found last pagination container using .calss.last.')
        total_pages = int(last_page_a_tag['href'].split('=')[-1]) if last_page_a_tag else 1 # type: ignore
        logger.debug(f'Found last page number successfully splitting last pagination number href.')

        if not search_results_container:
            return search_result

        search_results = search_results_container.find_all('div', {'class': 'gallery'}) # type: ignore
        logger.debug(f'Found search results container using .class.gallery')
        
        if not search_results:
            return search_result
        
        a_tags_with_doujin_id = [gallery.find('a', {'class': 'cover'}) for gallery in search_results]

        thumbs = []

        for a_tag in a_tags_with_doujin_id:
            if a_tag is None: continue

            doujin_id = a_tag['href'].split('/')[-2]

            if doujin_id == '': continue

            result_cover = a_tag.find('img', {'class': 'lazyload'})
            cover_uri = None
            width = None
            height = None

            if result_cover is not None:
                cover_uri = result_cover['data-src']
                width = result_cover['width']
                height = result_cover['height']

            result_caption = a_tag.find('div', {'class': 'caption'})

            caption = None
            if result_caption is not None:
                caption = result_caption.text

            thumbs.append(Thumb(id=doujin_id,
                                cover=Image(uri=cover_uri or '',
                                            mime=MIME.J,
                                            width=int(width or 0),
                                            height=int(height or 0)),
                                title=caption or ''))

        search_result.total_pages = total_pages
        search_result.total_results = 25 * total_pages if pagination_container else len(thumbs)
        search_result.results = thumbs

        return search_result

    def paginate(self, page: int) -> Pagination:
        response = self.__make_request(url=urljoin(self.__API_URL, f'galleries/all'),
                                       params={'page': page})

        if response.status_code != 200:
            self.__handle_request_error(f'Could not paginate to page {page} because nhentai\'s request ends up with {response.status_code} status code.')
            return Pagination(page=page)

        data = response.json()

        PAGES = data.get('num_pages', 0)
        PER_PAGE = data.get('per_page', 0)
        TOTAL_RESULTS = int(PAGES) * int(PER_PAGE)

        return Pagination(page=int(page),
                          total_results=TOTAL_RESULTS,
                          total_pages=PAGES,
                          results=[Thumb(id=result.get('id'),
                                         title=result.get('title').get('english'),
                                         cover=Image(uri=self.__make_page_uri(type='cover',
                                                                              media_id=result.get('media_id'),
                                                                              mime=MIME[result.get('images').get('cover').get('t').upper()]),
                                                     mime=MIME[result.get("images").get("thumbnail").get("t").upper()],
                                                     width=result.get('images').get('cover').get('w'),
                                                     height=result.get('images').get('cover').get('h'))) for result in data.get('result')])

    def random(self, retry=0) -> Manga:
        response = self.__make_request(url=urljoin(self.__BASE_URL, 'random'))

        if response.status_code != 200:
            self.__handle_request_error(f'Could not fetch a random manga because nhentai\'s request ends up with {response.status_code} status code.')

        soup = BeautifulSoup(response.text, 'html.parser')

        id = cast(Tag, soup.find('h3', id='gallery_id')).text.replace('#', '')
        logger.debug(f'Got successfully random manga id {id} from "gallery_id.h3" tag.')
        logger.debug(f'Using get method to Fetch manga with identifier: {id}')
        doujin = self.get(identifier=id)
        logger.debug(f'Got successfully random manga with id {id}.')

        if doujin is None:
            if retry >= 4:
                raise ExceedRetryCount('Could not fetch a random doujin after 4 retries.')
            
            logger.warning('Could not fetch random manga. Retrying.')
            return self.random(retry=retry+1)

        return doujin
    
    def author_page(self,
                    author: str,
                    page: int) -> AuthorPage:
        request_response = self.__make_request(url=urljoin(self.__BASE_URL, f'artist/{author}'),
                                               params={'page': page})
        
        result = AuthorPage(author=author,
                            total_pages=0,
                            page=page,
                            total_results=0,
                            results=[])
        
        if request_response.status_code != 200:
            logger.error('Could not fetch author page properly')
            return result    
   
        soup = BeautifulSoup(request_response.text, 'html.parser')

        search_results_container = soup.find('div', {'class': 'container'})
        pagination_container = soup.find('section', {'class': 'pagination'})

        last_page_a_tag = pagination_container.find('a',
                                                    {'class': 'last'}) if pagination_container else None  # type: ignore
        total_pages = int(last_page_a_tag['href'].split('=')[-1]) if last_page_a_tag else 1  # type: ignore

        if not search_results_container:
            return result

        search_results = search_results_container.find_all('div', {'class': 'gallery'})  # type: ignore

        if not search_results:
            return result

        a_tags_with_doujin_id = [gallery.find('a', {'class': 'cover'}) for gallery in search_results]

        thumbs = []

        for a_tag in a_tags_with_doujin_id:
            if a_tag is None: continue

            doujin_id = a_tag['href'].split('/')[-2]

            if doujin_id == '': continue

            result_cover = a_tag.find('img', {'class': 'lazyload'})
            cover_uri = None
            width = None
            height = None

            if result_cover is not None:
                cover_uri = result_cover['data-src']
                width = result_cover['width']
                height = result_cover['height']

            result_caption = a_tag.find('div', {'class': 'caption'})

            caption = None
            if result_caption is not None:
                caption = result_caption.text

            thumbs.append(Thumb(id=doujin_id,
                                cover=Image(uri=cover_uri or '',
                                            mime=MIME.J,
                                            width=int(width or 0),
                                            height=int(height or 0)),
                                title=caption or ''))
        
        result.author = author
        result.total_pages = total_pages
        result.page = page
        result.total_results = 25 * total_pages if pagination_container else len(thumbs)
        result.results = thumbs
        
        return result